#!/usr/bin/env python3
"""
Golden Test Promoter
Automatically promotes failed/interesting cases to golden test set
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils_core.provenance import ProvenanceLogger, SCHEMA_VERSION


class GoldenPromoter:
    """
    Promotes conversation cases to golden test set based on criteria
    """
    
    def __init__(self, 
                 provenance_file: str = 'data_core/analytics/hypotheses.ndjson',
                 golden_set_file: str = 'data_core/goldens/sample_set.json'):
        self.provenance_file = Path(provenance_file)
        self.golden_set_file = Path(golden_set_file)
    
    def analyze_candidates(self, min_latency_ms: float = 20000.0, max_complexity: float = 0.8) -> List[Dict[str, Any]]:
        """
        Find candidate cases for promotion
        
        Criteria:
        - High latency (edge case testing)
        - High complexity (stress testing)
        - Routing edge cases (boundary testing)
        - Errors/failures (regression prevention)
        """
        candidates = []
        
        if not self.provenance_file.exists():
            print(f"Provenance file not found: {self.provenance_file}")
            return candidates
        
        # Read provenance events
        with open(self.provenance_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    event = json.loads(line)
                    
                    # Only process response events
                    if event.get('event_type') != 'response':
                        continue
                    
                    # Extract metadata
                    math_weights = event.get('math_weights', {})
                    complexity = math_weights.get('question_complexity', 0.0)
                    weight = math_weights.get('calculated_weight', 0.5)
                    
                    # Check criteria
                    reason = None
                    
                    # High complexity
                    if complexity >= max_complexity:
                        reason = f"high_complexity_{complexity:.2f}"
                    
                    # Edge case routing (very close to boundary)
                    boundary = math_weights.get('adaptive', {}).get('boundary', 0.5)
                    if abs(weight - boundary) < 0.01:
                        reason = f"routing_edge_case_{weight:.3f}_vs_{boundary:.3f}"
                    
                    # Source mismatch (should be main but got embedder, or vice versa)
                    source = event.get('meta', {}).get('source')
                    expected_source = 'main_model' if weight > boundary else 'embedder'
                    if source and source != expected_source:
                        reason = f"routing_mismatch_{source}_expected_{expected_source}"
                    
                    if reason:
                        candidates.append({
                            'question': event['question'],
                            'trait': event['trait'],
                            'conv_id': event['conv_id'],
                            'msg_id': event['msg_id'],
                            'reason': reason,
                            'complexity': complexity,
                            'weight': weight,
                            'source': source,
                            'timestamp': event['ts']
                        })
                
                except Exception as e:
                    print(f"Warning: Skipping malformed event: {e}")
                    continue
        
        return candidates
    
    def promote_candidates(self, candidates: List[Dict[str, Any]], max_promote: int = 5) -> int:
        """
        Promote candidates to golden set
        
        Args:
            candidates: List of candidate events
            max_promote: Maximum number to promote
        
        Returns:
            Number of cases promoted
        """
        if not candidates:
            print("No candidates to promote")
            return 0
        
        # Load existing golden set
        existing_goldens = []
        if self.golden_set_file.exists():
            with open(self.golden_set_file, 'r') as f:
                existing_goldens = json.load(f)
        
        # Get existing questions to avoid duplicates
        existing_questions = {g['question'].lower().strip() for g in existing_goldens}
        
        # Sort candidates by priority (high complexity first, then routing edge cases)
        sorted_candidates = sorted(
            candidates,
            key=lambda c: (
                -c['complexity'],  # High complexity first
                abs(c['weight'] - 0.5)  # Then edge cases
            )
        )
        
        promoted = 0
        for candidate in sorted_candidates[:max_promote]:
            # Skip duplicates
            if candidate['question'].lower().strip() in existing_questions:
                continue
            
            # Create golden test entry
            golden_id = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{promoted+1}"
            golden_entry = {
                'id': golden_id,
                'question': candidate['question'],
                'trait': candidate['trait'],
                'labels': [candidate['reason']],
                'promoted_from': {
                    'conv_id': candidate['conv_id'],
                    'msg_id': candidate['msg_id'],
                    'timestamp': candidate['timestamp']
                },
                'metadata': {
                    'complexity': candidate['complexity'],
                    'weight': candidate['weight'],
                    'source': candidate['source']
                }
            }
            
            existing_goldens.append(golden_entry)
            existing_questions.add(candidate['question'].lower().strip())
            promoted += 1
        
        # Save updated golden set
        if promoted > 0:
            self.golden_set_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing
            if self.golden_set_file.exists():
                backup_file = self.golden_set_file.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
                import shutil
                shutil.copy2(self.golden_set_file, backup_file)
            
            # Write updated set
            with open(self.golden_set_file, 'w') as f:
                json.dump(existing_goldens, f, indent=2)
        
        return promoted
    
    def auto_promote(self, max_promote: int = 5) -> Dict[str, Any]:
        """
        Run automatic promotion of candidates
        
        Returns summary of promotion
        """
        print("="*70)
        print("GOLDEN TEST AUTO-PROMOTION")
        print("="*70)
        
        # Analyze candidates
        print("\nAnalyzing candidates from provenance log...")
        candidates = self.analyze_candidates()
        print(f"Found {len(candidates)} candidates")
        
        if candidates:
            print("\nTop candidates:")
            for i, c in enumerate(candidates[:10], 1):
                print(f"  {i}. {c['question'][:50]}...")
                print(f"     Reason: {c['reason']}, Complexity: {c['complexity']:.2f}")
        
        # Promote
        print(f"\nPromoting up to {max_promote} cases...")
        promoted_count = self.promote_candidates(candidates, max_promote)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_candidates': len(candidates),
            'promoted': promoted_count,
            'golden_set_file': str(self.golden_set_file)
        }
        
        print(f"\n✓ Promoted {promoted_count} cases to golden set")
        print(f"  Golden set: {self.golden_set_file}")
        print("="*70)
        
        return summary


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Golden Test Promoter')
    parser.add_argument('--provenance', default='data_core/analytics/hypotheses.ndjson',
                       help='Provenance NDJSON file')
    parser.add_argument('--golden-set', default='data_core/goldens/sample_set.json',
                       help='Golden set JSON file')
    parser.add_argument('--max-promote', type=int, default=5,
                       help='Maximum cases to promote (default: 5)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Analyze only, do not promote')
    
    args = parser.parse_args()
    
    promoter = GoldenPromoter(args.provenance, args.golden_set)
    
    if args.dry_run:
        candidates = promoter.analyze_candidates()
        print(f"\nDRY RUN: Found {len(candidates)} candidates")
        for i, c in enumerate(candidates[:args.max_promote], 1):
            print(f"\n  {i}. {c['question']}")
            print(f"     Reason: {c['reason']}")
            print(f"     Complexity: {c['complexity']:.2f}, Weight: {c['weight']:.3f}")
    else:
        promoter.auto_promote(max_promote=args.max_promote)


if __name__ == "__main__":
    main()

