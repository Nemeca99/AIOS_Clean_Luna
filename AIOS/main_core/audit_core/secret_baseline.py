#!/usr/bin/env python3
"""
Secret Baseline Manager
Only alert on NEW secrets. Reduce entropy spam.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class SecretBaselineManager:
    """
    Manage baseline of accepted secrets.
    Only alert on net new findings.
    
    Features:
    - Redacted baseline storage
    - Net new detection
    - Precision/recall tracking
    - Auto-tune entropy threshold
    """
    
    def __init__(self, baseline_file: Path = None):
        if baseline_file is None:
            baseline_file = Path("reports") / ".secret_baseline.json"
        
        self.baseline_file = baseline_file
        self.baseline = self._load_baseline()
    
    def _load_baseline(self) -> Dict:
        """Load baseline from disk."""
        if not self.baseline_file.exists():
            return {
                'version': '1.0.0',
                'secrets': {},
                'stats': {
                    'total_baseline': 0,
                    'false_positives_reported': 0,
                    'true_positives_reported': 0
                }
            }
        
        try:
            with open(self.baseline_file) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load secret baseline: {e}")
            return {'version': '1.0.0', 'secrets': {}}
    
    def _save_baseline(self):
        """Save baseline to disk."""
        try:
            self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.baseline_file, 'w') as f:
                json.dump(self.baseline, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save secret baseline: {e}")
    
    def _hash_secret(self, file_path: str, line: int, secret_type: str) -> str:
        """Create a hash fingerprint of a secret location."""
        fingerprint = f"{file_path}:{line}:{secret_type}"
        return hashlib.md5(fingerprint.encode()).hexdigest()
    
    def is_known_secret(self, file_path: str, line: int, secret_type: str) -> bool:
        """Check if a secret is in the baseline."""
        secret_hash = self._hash_secret(file_path, line, secret_type)
        return secret_hash in self.baseline.get('secrets', {})
    
    def add_to_baseline(self, 
                       file_path: str,
                       line: int,
                       secret_type: str,
                       redacted_preview: str):
        """Add a secret to the baseline (redacted)."""
        secret_hash = self._hash_secret(file_path, line, secret_type)
        
        self.baseline.setdefault('secrets', {})[secret_hash] = {
            'file': file_path,
            'line': line,
            'type': secret_type,
            'preview': redacted_preview,
            'added_date': self._get_timestamp()
        }
        
        self.baseline.setdefault('stats', {})['total_baseline'] = len(self.baseline['secrets'])
        self._save_baseline()
    
    def filter_new_secrets(self, all_secrets: List[Dict]) -> List[Dict]:
        """
        Filter secrets to only new ones (not in baseline).
        
        Args:
            all_secrets: List of secret dicts with file, line, type
        
        Returns:
            List of only new secrets
        """
        new_secrets = []
        
        for secret in all_secrets:
            file_path = secret.get('file', '')
            line = secret.get('line', 0)
            secret_type = secret.get('type', '')
            
            if not self.is_known_secret(file_path, line, secret_type):
                new_secrets.append(secret)
        
        return new_secrets
    
    def update_baseline_with_approved(self, secrets_to_approve: List[Dict]):
        """
        Update baseline with approved (legacy) secrets.
        
        Args:
            secrets_to_approve: List of secrets to add to baseline
        """
        for secret in secrets_to_approve:
            self.add_to_baseline(
                file_path=secret.get('file', ''),
                line=secret.get('line', 0),
                secret_type=secret.get('type', ''),
                redacted_preview=secret.get('preview', '***')
            )
        
        logger.info(f"Added {len(secrets_to_approve)} secrets to baseline")
    
    def get_baseline_stats(self) -> Dict:
        """Get statistics about the baseline."""
        return {
            'total_baseline_secrets': len(self.baseline.get('secrets', {})),
            'oldest_secret': self._get_oldest_secret_date(),
            'baseline_file': str(self.baseline_file)
        }
    
    def _get_oldest_secret_date(self) -> str:
        """Get date of oldest secret in baseline."""
        secrets = self.baseline.get('secrets', {})
        if not secrets:
            return "N/A"
        
        dates = [s.get('added_date', '') for s in secrets.values() if s.get('added_date')]
        return min(dates) if dates else "N/A"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def calculate_precision_recall(self, 
                                   new_findings: int,
                                   confirmed_leaks: int) -> Dict:
        """
        Calculate precision/recall for entropy tuning.
        
        Args:
            new_findings: Number of new secrets flagged
            confirmed_leaks: Number that were actual leaks
        
        Returns:
            Dict with precision/recall metrics
        """
        if new_findings == 0:
            return {'precision': 1.0, 'recall': 0.0}
        
        precision = confirmed_leaks / new_findings if new_findings > 0 else 0
        
        stats = self.baseline.setdefault('stats', {})
        stats['true_positives_reported'] = stats.get('true_positives_reported', 0) + confirmed_leaks
        stats['false_positives_reported'] = stats.get('false_positives_reported', 0) + (new_findings - confirmed_leaks)
        
        total_tp = stats['true_positives_reported']
        total_fp = stats['false_positives_reported']
        
        overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        
        return {
            'current_precision': precision,
            'overall_precision': overall_precision,
            'true_positives': total_tp,
            'false_positives': total_fp
        }

