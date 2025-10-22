"""
User Data Deletion API
Hard-delete user records by hashed conversation ID (GDPR compliance)
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import hashlib


def hash_conv_id_for_deletion(conv_id: str) -> str:
    """Hash conversation ID same way as provenance logger"""
    if conv_id.startswith('hashed_'):
        return conv_id
    return f"hashed_{hashlib.sha256(f'aios_conv:{conv_id}'.encode()).hexdigest()[:16]}"


class DataDeletionService:
    """
    Handles user data deletion requests
    """
    
    def __init__(self, 
                 provenance_file: str = 'data_core/analytics/hypotheses.ndjson',
                 deletion_log: str = 'data_core/analytics/deletion_audit.ndjson'):
        self.provenance_file = Path(provenance_file)
        self.deletion_log = Path(deletion_log)
        self.deletion_log.parent.mkdir(parents=True, exist_ok=True)
    
    def find_user_data(self, conv_id: str) -> Dict[str, Any]:
        """
        Find all data associated with a conversation ID
        
        Args:
            conv_id: Conversation ID (will be hashed if not already)
        
        Returns:
            Summary of found data
        """
        # Hash the conv_id
        hashed_id = hash_conv_id_for_deletion(conv_id)
        
        if not self.provenance_file.exists():
            return {'error': 'Provenance file not found', 'conv_id': hashed_id, 'found': 0}
        
        found_events = []
        
        with open(self.provenance_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    event = json.loads(line)
                    if event.get('conv_id') == hashed_id:
                        found_events.append({
                            'line_num': line_num,
                            'event_type': event.get('event_type', 'unknown'),
                            'msg_id': event.get('msg_id'),
                            'ts': event.get('ts')
                        })
                except Exception as e:
                    continue
        
        return {
            'conv_id': hashed_id,
            'found': len(found_events),
            'events': found_events
        }
    
    def delete_user_data(self, conv_id: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Delete all data for a conversation ID
        
        Args:
            conv_id: Conversation ID to delete
            dry_run: If True, only report what would be deleted
        
        Returns:
            Deletion summary
        """
        # Hash the conv_id
        hashed_id = hash_conv_id_for_deletion(conv_id)
        
        if not self.provenance_file.exists():
            return {'error': 'Provenance file not found'}
        
        # Read all events
        kept_events = []
        deleted_events = []
        
        with open(self.provenance_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    event = json.loads(line)
                    
                    if event.get('conv_id') == hashed_id:
                        deleted_events.append(event)
                    else:
                        kept_events.append(event)
                except Exception as e:
                    # Keep malformed lines
                    kept_events.append({'_raw': line.strip()})
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'conv_id': hashed_id,
            'total_events_before': len(kept_events) + len(deleted_events),
            'deleted_count': len(deleted_events),
            'kept_count': len(kept_events),
            'dry_run': dry_run
        }
        
        # Execute deletion if not dry run
        if not dry_run and deleted_events:
            # Backup original
            backup_file = self.provenance_file.with_suffix(f'.pre_deletion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
            import shutil
            shutil.copy2(self.provenance_file, backup_file)
            summary['backup_file'] = str(backup_file)
            
            # Write kept events only
            with open(self.provenance_file, 'w', encoding='utf-8') as f:
                for event in kept_events:
                    if '_raw' in event:
                        f.write(event['_raw'] + '\n')
                    else:
                        f.write(json.dumps(event, ensure_ascii=False) + '\n')
            
            # Log deletion to audit
            self._log_deletion_audit(hashed_id, deleted_events)
        
        return summary
    
    def _log_deletion_audit(self, conv_id: str, deleted_events: List[Dict[str, Any]]):
        """Log deletion to audit trail"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'hard_delete',
            'conv_id': conv_id,
            'deleted_count': len(deleted_events),
            'event_types': list(set(e.get('event_type', 'unknown') for e in deleted_events)),
            'time_range': {
                'first': min(e.get('ts', '') for e in deleted_events if 'ts' in e),
                'last': max(e.get('ts', '') for e in deleted_events if 'ts' in e)
            }
        }
        
        with open(self.deletion_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='User Data Deletion Service')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Find user data')
    find_parser.add_argument('--conv-id', required=True, help='Conversation ID')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete user data')
    delete_parser.add_argument('--conv-id', required=True, help='Conversation ID')
    delete_parser.add_argument('--execute', action='store_true', help='Execute deletion (default: dry-run)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    service = DataDeletionService()
    
    if args.command == 'find':
        result = service.find_user_data(args.conv_id)
        
        print("="*70)
        print("USER DATA SEARCH")
        print("="*70)
        print(f"Conversation ID: {result['conv_id']}")
        print(f"Events found: {result['found']}")
        
        if result.get('events'):
            print("\nEvents:")
            for e in result['events'][:10]:
                print(f"  Line {e['line_num']}: {e['event_type']} msg_{e['msg_id']} at {e['ts']}")
            
            if len(result['events']) > 10:
                print(f"  ... and {len(result['events']) - 10} more")
        
        print("="*70)
    
    elif args.command == 'delete':
        result = service.delete_user_data(args.conv_id, dry_run=not args.execute)
        
        print("="*70)
        print("USER DATA DELETION")
        print("="*70)
        print(f"Conversation ID: {result['conv_id']}")
        print(f"Events before: {result['total_events_before']}")
        print(f"Would delete: {result['deleted_count']}")
        print(f"Would keep: {result['kept_count']}")
        
        if result['dry_run']:
            print("\nDRY RUN - No changes made")
            print("Run with --execute to perform deletion")
        else:
            print(f"\n✓ Deleted {result['deleted_count']} events")
            print(f"  Backup: {result.get('backup_file', 'N/A')}")
            print(f"  Audit: data_core/analytics/deletion_audit.ndjson")
        
        print("="*70)


if __name__ == "__main__":
    main()

