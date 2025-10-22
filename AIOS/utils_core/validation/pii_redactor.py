"""
PII Redaction System
Detects and redacts personally identifiable information from logs
"""

import re
import hashlib
from typing import Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path
import json


class PIIRedactor:
    """
    Redacts PII from text and logs redactions for audit
    """
    
    # Redaction patterns
    PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        'url': re.compile(r'https?://[^\s]+'),
        'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        # Add more patterns as needed
    }
    
    def __init__(self, audit_log: str = 'data_core/analytics/redaction_audit.ndjson'):
        self.audit_log = Path(audit_log)
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
    
    def hash_identifier(self, text: str, salt: str = "aios_privacy") -> str:
        """Create deterministic hash of identifier for consistency"""
        combined = f"{salt}:{text}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def redact_text(self, text: str, preserve_structure: bool = True) -> Tuple[str, List[Dict[str, str]]]:
        """
        Redact PII from text
        
        Args:
            text: Input text to redact
            preserve_structure: If True, replace with [REDACTED_TYPE] instead of hash
        
        Returns:
            Tuple of (redacted_text, redaction_list)
        """
        redacted = text
        redactions = []
        
        for pii_type, pattern in self.PATTERNS.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                original = match.group(0)
                
                if preserve_structure:
                    replacement = f"[REDACTED_{pii_type.upper()}]"
                else:
                    replacement = f"[{self.hash_identifier(original)}]"
                
                redacted = redacted.replace(original, replacement, 1)  # Replace one at a time
                
                redactions.append({
                    'type': pii_type,
                    'position': match.start(),
                    'length': len(original),
                    'hash': self.hash_identifier(original)
                })
        
        return redacted, redactions
    
    def redact_event(self, event: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
        """
        Redact PII from provenance event
        
        Redacts:
        - Question text
        - Response text
        - Conversation ID (hashed for consistency)
        
        Preserves:
        - Metrics, metadata, math weights
        """
        redacted_event = event.copy()
        all_redactions = []
        
        # Redact question
        if 'question' in event:
            redacted_question, q_redactions = self.redact_text(event['question'])
            redacted_event['question'] = redacted_question
            all_redactions.extend([{**r, 'field': 'question'} for r in q_redactions])
        
        # Redact response
        if 'response' in event:
            redacted_response, r_redactions = self.redact_text(event['response'])
            redacted_event['response'] = redacted_response
            all_redactions.extend([{**r, 'field': 'response'} for r in r_redactions])
        
        # Hash conversation ID (preserve for grouping)
        if 'conv_id' in event and not event['conv_id'].startswith('hashed_'):
            original_conv_id = event['conv_id']
            redacted_event['conv_id'] = f"hashed_{self.hash_identifier(original_conv_id)}"
            all_redactions.append({
                'type': 'conv_id',
                'field': 'conv_id',
                'hash': redacted_event['conv_id']
            })
        
        return redacted_event, all_redactions
    
    def log_redaction(self, redactions: List[Dict[str, str]], event_id: str):
        """Log redaction to audit trail"""
        if not redactions:
            return
        
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_id': event_id,
            'redaction_count': len(redactions),
            'redactions': redactions
        }
        
        # Append to audit log
        with open(self.audit_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
    
    def scan_log_file(self, log_file: str) -> Dict[str, Any]:
        """
        Scan NDJSON log file for PII
        
        Returns:
            Summary of PII found
        """
        log_path = Path(log_file)
        
        if not log_path.exists():
            return {'error': 'Log file not found'}
        
        summary = {
            'file': str(log_path),
            'total_events': 0,
            'events_with_pii': 0,
            'pii_by_type': {},
            'sample_redactions': []
        }
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                summary['total_events'] += 1
                
                try:
                    event = json.loads(line)
                    
                    # Check question and response for PII
                    has_pii = False
                    for field in ['question', 'response']:
                        if field in event:
                            _, redactions = self.redact_text(event[field])
                            
                            if redactions:
                                has_pii = True
                                for redaction in redactions:
                                    pii_type = redaction['type']
                                    summary['pii_by_type'][pii_type] = summary['pii_by_type'].get(pii_type, 0) + 1
                                    
                                    # Save first few examples
                                    if len(summary['sample_redactions']) < 5:
                                        summary['sample_redactions'].append({
                                            'event_id': event.get('conv_id', 'unknown'),
                                            'field': field,
                                            'type': pii_type,
                                            'position': redaction['position']
                                        })
                    
                    if has_pii:
                        summary['events_with_pii'] += 1
                
                except Exception as e:
                    continue
        
        return summary


def redact_provenance_file(input_file: str, 
                          output_file: str,
                          audit: bool = True) -> Dict[str, Any]:
    """
    Create redacted copy of provenance file
    
    Args:
        input_file: Source NDJSON file
        output_file: Destination redacted file
        audit: Log redactions to audit trail
    
    Returns:
        Redaction summary
    """
    redactor = PIIRedactor()
    
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        return {'error': 'Input file not found'}
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'input_file': str(input_path),
        'output_file': str(output_path),
        'total_events': 0,
        'events_redacted': 0,
        'total_redactions': 0
    }
    
    with open(input_path, 'r', encoding='utf-8') as f_in:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                if not line.strip():
                    continue
                
                summary['total_events'] += 1
                
                try:
                    event = json.loads(line)
                    event_id = f"{event.get('conv_id', 'unknown')}_{event.get('msg_id', 0)}"
                    
                    # Redact event
                    redacted_event, redactions = redactor.redact_event(event)
                    
                    if redactions:
                        summary['events_redacted'] += 1
                        summary['total_redactions'] += len(redactions)
                        
                        # Log to audit
                        if audit:
                            redactor.log_redaction(redactions, event_id)
                    
                    # Write redacted event
                    f_out.write(json.dumps(redacted_event, ensure_ascii=False) + '\n')
                
                except Exception as e:
                    # Write original line if redaction fails
                    f_out.write(line)
    
    return summary


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PII Redaction Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan log for PII')
    scan_parser.add_argument('--file', required=True, help='NDJSON file to scan')
    
    # Redact command
    redact_parser = subparsers.add_parser('redact', help='Create redacted copy')
    redact_parser.add_argument('--input', required=True, help='Input NDJSON file')
    redact_parser.add_argument('--output', required=True, help='Output redacted file')
    redact_parser.add_argument('--no-audit', action='store_true', help='Skip audit logging')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'scan':
        redactor = PIIRedactor()
        summary = redactor.scan_log_file(args.file)
        
        print("="*70)
        print("PII SCAN REPORT")
        print("="*70)
        print(f"File: {summary.get('file', 'Unknown')}")
        print(f"Total events: {summary.get('total_events', 0)}")
        print(f"Events with PII: {summary.get('events_with_pii', 0)}")
        
        if summary.get('pii_by_type'):
            print("\nPII detected:")
            for pii_type, count in summary['pii_by_type'].items():
                print(f"  {pii_type}: {count}")
        else:
            print("\n✓ No PII detected")
        
        print("="*70)
    
    elif args.command == 'redact':
        summary = redact_provenance_file(
            args.input,
            args.output,
            audit=not args.no_audit
        )
        
        print("="*70)
        print("PII REDACTION COMPLETE")
        print("="*70)
        print(f"Input: {summary['input_file']}")
        print(f"Output: {summary['output_file']}")
        print(f"Total events: {summary['total_events']}")
        print(f"Events redacted: {summary['events_redacted']}")
        print(f"Total redactions: {summary['total_redactions']}")
        
        if summary['events_redacted'] > 0:
            print(f"\n⚠ {summary['events_redacted']} events contained PII")
            if not args.no_audit:
                print("  Audit log: data_core/analytics/redaction_audit.ndjson")
        else:
            print("\n✓ No PII found")
        
        print("="*70)


if __name__ == "__main__":
    main()

