#!/usr/bin/env python3
"""
Policy Loader - Load and validate audit policy configuration.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PolicyLoader:
    """
    Load and validate audit policy from policy.yaml.
    Single source of truth for all gates, thresholds, and enforcement rules.
    """
    
    def __init__(self, policy_path: Path = None):
        if policy_path is None:
            policy_path = Path(__file__).parent / "config" / "policy.yaml"
        
        self.policy_path = policy_path
        self.policy = self._load_policy()
    
    def _load_policy(self) -> Dict:
        """Load policy from YAML file."""
        try:
            with open(self.policy_path) as f:
                policy = yaml.safe_load(f)
            
            logger.info(f"Loaded policy v{policy.get('version', 'unknown')}")
            return policy
        except Exception as e:
            logger.error(f"Failed to load policy: {e}")
            # Return minimal default policy
            return self._default_policy()
    
    def _default_policy(self) -> Dict:
        """Minimal default policy if file load fails."""
        return {
            'version': '3.0.0',
            'production_gates': {
                'minimum_average_score': 85,
                'minimum_per_core_score': 80,
                'allow_critical_issues': False,
                'max_regression_delta': 3
            }
        }
    
    def get_production_gates(self) -> Dict:
        """Get production readiness gates."""
        return self.policy.get('production_gates', {})
    
    def get_core_policy(self, core_name: str) -> Dict:
        """Get policy for specific core."""
        core_policies = self.policy.get('core_policies', {})
        strict_cores = core_policies.get('strict_cores', [])
        
        if core_name in strict_cores:
            return core_policies.get('strict', core_policies.get('default', {}))
        else:
            return core_policies.get('default', {})
    
    def get_performance_slos(self) -> Dict:
        """Get performance SLO thresholds."""
        return self.policy.get('performance_slos', {})
    
    def get_secrets_config(self) -> Dict:
        """Get secrets scanning configuration."""
        return self.policy.get('secrets_scanning', {})
    
    def get_static_analysis_config(self) -> Dict:
        """Get static analysis configuration."""
        return self.policy.get('static_analysis', {})
    
    def get_scoring_config(self) -> Dict:
        """Get scoring configuration."""
        return self.policy.get('scoring', {})
    
    def is_differential_enabled(self) -> bool:
        """Check if differential auditing is enabled."""
        return self.policy.get('differential', {}).get('enabled', False)
    
    def validate_suppression(self, suppression: Dict) -> tuple:
        """
        Validate a suppression entry.
        
        Returns:
            (is_valid, error_message)
        """
        suppression_policy = self.policy.get('suppressions', {})
        
        # Check required fields
        if suppression_policy.get('require_owner', True):
            if not suppression.get('owner'):
                return False, "Suppression requires 'owner' field"
        
        if suppression_policy.get('require_reason', True):
            if not suppression.get('reason'):
                return False, "Suppression requires 'reason' field"
        
        if suppression_policy.get('require_expiry', True):
            if not suppression.get('expires_on'):
                return False, "Suppression requires 'expires_on' field"
            
            # Check expiry date
            try:
                expires = datetime.fromisoformat(suppression['expires_on'])
                now = datetime.now()
                
                # Check if expired
                if expires < now:
                    if suppression_policy.get('fail_on_expired', True):
                        return False, f"Suppression expired on {suppression['expires_on']}"
                
                # Check max expiry
                max_days = suppression_policy.get('max_expiry_days', 90)
                max_future = now + timedelta(days=max_days)
                if expires > max_future:
                    return False, f"Expiry date exceeds max {max_days} days"
                
            except ValueError:
                return False, f"Invalid expiry date format: {suppression['expires_on']}"
        
        return True, None


class AllowlistManager:
    """
    Manage suppression allowlist with expiry tracking.
    """
    
    def __init__(self, allowlist_path: Path = None):
        if allowlist_path is None:
            allowlist_path = Path(__file__).parent / "config" / "allowlist.json"
        
        self.allowlist_path = allowlist_path
        self.allowlist = self._load_allowlist()
        self.policy = PolicyLoader()
    
    def _load_allowlist(self) -> Dict:
        """Load allowlist from JSON file."""
        try:
            with open(self.allowlist_path) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load allowlist: {e}")
            return {'version': '1.0.0', 'suppressions': [], 'quarantined_checks': []}
    
    def is_suppressed(self, pattern_id: str, file_path: str, line: int = None) -> bool:
        """Check if a specific issue is suppressed."""
        for suppression in self.allowlist.get('suppressions', []):
            if suppression.get('pattern_id') == pattern_id:
                if suppression.get('file') in str(file_path):
                    if line is None or suppression.get('line') == line:
                        # Check if still valid
                        is_valid, _ = self.policy.validate_suppression(suppression)
                        return is_valid
        
        return False
    
    def validate_all_suppressions(self) -> tuple:
        """
        Validate all suppressions in allowlist.
        
        Returns:
            (all_valid, issues)
        """
        issues = []
        
        for suppression in self.allowlist.get('suppressions', []):
            is_valid, error_msg = self.policy.validate_suppression(suppression)
            if not is_valid:
                issues.append({
                    'suppression_id': suppression.get('id'),
                    'error': error_msg
                })
        
        return len(issues) == 0, issues
    
    def get_expiring_suppressions(self, days: int = 14) -> List[Dict]:
        """Get suppressions expiring within N days."""
        expiring = []
        now = datetime.now()
        threshold = now + timedelta(days=days)
        
        for suppression in self.allowlist.get('suppressions', []):
            expires_str = suppression.get('expires_on')
            if expires_str:
                try:
                    expires = datetime.fromisoformat(expires_str)
                    if now < expires <= threshold:
                        expiring.append(suppression)
                except ValueError:
                    pass
        
        return expiring

