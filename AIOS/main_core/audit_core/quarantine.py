#!/usr/bin/env python3
"""
Quarantine Manager
Handle flaky checks gracefully with auto-expiry.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QuarantineManager:
    """
    Manage quarantined checks with expiry enforcement.
    
    Quarantined checks:
    - Still run and report
    - Don't fail CI
    - Must have owner, reason, expiry
    - Auto-fail when expired
    """
    
    def __init__(self, quarantine_file: Path = None):
        if quarantine_file is None:
            quarantine_file = Path(__file__).parent / "config" / "quarantine.json"
        
        self.quarantine_file = quarantine_file
        self.quarantine = self._load_quarantine()
    
    def _load_quarantine(self) -> Dict:
        """Load quarantine configuration."""
        if not self.quarantine_file.exists():
            return {'version': '1.0.0', 'quarantined_checks': []}
        
        try:
            with open(self.quarantine_file) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load quarantine: {e}")
            return {'version': '1.0.0', 'quarantined_checks': []}
    
    def is_quarantined(self, check_id: str) -> bool:
        """Check if a check is quarantined."""
        for entry in self.quarantine['quarantined_checks']:
            if entry.get('check_id') == check_id:
                # Check if still valid (not expired)
                if self._is_entry_valid(entry):
                    return True
        return False
    
    def validate_all_entries(self) -> tuple:
        """
        Validate all quarantine entries.
        
        Returns:
            (all_valid, issues)
        """
        issues = []
        
        for entry in self.quarantine['quarantined_checks']:
            is_valid, error_msg = self._validate_entry(entry)
            if not is_valid:
                issues.append({
                    'check_id': entry.get('check_id'),
                    'error': error_msg
                })
        
        return len(issues) == 0, issues
    
    def _validate_entry(self, entry: Dict) -> tuple:
        """
        Validate a single quarantine entry.
        
        Returns:
            (is_valid, error_message)
        """
        # Required fields
        if not entry.get('check_id'):
            return False, "Missing 'check_id' field"
        
        if not entry.get('owner'):
            return False, f"Quarantine {entry.get('check_id')} requires 'owner' field"
        
        if not entry.get('reason'):
            return False, f"Quarantine {entry.get('check_id')} requires 'reason' field"
        
        if not entry.get('expires_on'):
            return False, f"Quarantine {entry.get('check_id')} requires 'expires_on' field"
        
        # Check expiry
        try:
            expires = datetime.fromisoformat(entry['expires_on'])
            now = datetime.now()
            
            if expires < now:
                return False, f"Quarantine {entry.get('check_id')} expired on {entry['expires_on']}"
            
            # Check max duration (30 days from policy)
            created = entry.get('created', now.isoformat())
            created_dt = datetime.fromisoformat(created)
            max_duration = timedelta(days=30)
            
            if expires - created_dt > max_duration:
                return False, f"Quarantine duration exceeds 30 days"
            
        except ValueError:
            return False, f"Invalid expiry date format: {entry.get('expires_on')}"
        
        return True, None
    
    def _is_entry_valid(self, entry: Dict) -> bool:
        """Check if entry is valid (not expired)."""
        is_valid, _ = self._validate_entry(entry)
        return is_valid
    
    def get_expiring_soon(self, days: int = 7) -> List[Dict]:
        """Get quarantines expiring within N days."""
        expiring = []
        now = datetime.now()
        threshold = now + timedelta(days=days)
        
        for entry in self.quarantine['quarantined_checks']:
            expires_str = entry.get('expires_on')
            if expires_str:
                try:
                    expires = datetime.fromisoformat(expires_str)
                    if now < expires <= threshold:
                        expiring.append(entry)
                except ValueError:
                    pass
        
        return expiring
    
    def get_all_quarantined_checks(self) -> List[str]:
        """Get list of all quarantined check IDs."""
        return [
            entry['check_id'] 
            for entry in self.quarantine['quarantined_checks']
            if self._is_entry_valid(entry)
        ]

