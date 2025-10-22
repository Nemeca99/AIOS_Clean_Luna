"""
NDJSON Schema Migrator
Handles version upgrades for provenance logs
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class SchemaMigrator:
    """Migrates NDJSON provenance logs between schema versions"""
    
    # Schema version history
    VERSIONS = {
        "0.9": "Pre-versioned schema (no schema_version field)",
        "1.0": "Added schema_version and event_type fields"
    }
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
    
    def detect_version(self) -> str:
        """Detect schema version from log file"""
        if not self.log_file.exists():
            return "1.0"  # New file, use current version
        
        # Read first event to check version
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        return event.get('schema_version', '0.9')
                    except Exception as e:
                        return '0.9'
        
        return '0.9'  # Empty file or parse error
    
    def needs_migration(self, target_version: str = "1.0") -> bool:
        """Check if migration is needed"""
        current = self.detect_version()
        return current != target_version
    
    def migrate(self, target_version: str = "1.0", backup: bool = True):
        """
        Migrate log file to target schema version
        
        Args:
            target_version: Target schema version
            backup: Create backup before migration
        """
        current_version = self.detect_version()
        
        if current_version == target_version:
            print(f"Already at version {target_version}, no migration needed")
            return
        
        print(f"Migrating from {current_version} -> {target_version}")
        
        # Backup if requested
        if backup:
            backup_file = self.log_file.with_suffix(f'.{current_version}.bak')
            print(f"Creating backup: {backup_file}")
            if self.log_file.exists():
                import shutil
                shutil.copy2(self.log_file, backup_file)
        
        # Read all events
        events = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except Exception as e:
                            print(f"Warning: Skipping malformed line")
        
        # Apply migrations
        if current_version == "0.9" and target_version == "1.0":
            events = self._migrate_0_9_to_1_0(events)
        
        # Write migrated events
        temp_file = self.log_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            for event in events:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        
        # Replace original
        temp_file.replace(self.log_file)
        
        print(f"Migration complete: {len(events)} events migrated")
    
    def _migrate_0_9_to_1_0(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Migrate from 0.9 to 1.0 schema"""
        migrated = []
        for event in events:
            # Add schema version
            event['schema_version'] = '1.0'
            
            # Infer event type from fields
            if 'hypo_id' in event:
                event['event_type'] = 'hypothesis_test'
            elif 'question' in event and 'response' in event:
                event['event_type'] = 'response'
            elif 'batch_id' in event or 'results' in event:
                event['event_type'] = 'hypothesis_batch'
            else:
                event['event_type'] = 'unknown'
            
            migrated.append(event)
        
        return migrated


def migrate_provenance_logs(log_dir: str = 'data_core/analytics'):
    """Migrate all NDJSON files in analytics directory"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"Directory not found: {log_dir}")
        return
    
    ndjson_files = list(log_path.glob('*.ndjson'))
    
    if not ndjson_files:
        print(f"No NDJSON files found in {log_dir}")
        return
    
    print(f"Found {len(ndjson_files)} NDJSON files")
    
    for ndjson_file in ndjson_files:
        print(f"\nProcessing: {ndjson_file.name}")
        migrator = SchemaMigrator(str(ndjson_file))
        
        if migrator.needs_migration():
            migrator.migrate(backup=True)
        else:
            print(f"  Already at latest version")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Migrate specific file
        migrator = SchemaMigrator(sys.argv[1])
        migrator.migrate()
    else:
        # Migrate all files in analytics
        migrate_provenance_logs()

