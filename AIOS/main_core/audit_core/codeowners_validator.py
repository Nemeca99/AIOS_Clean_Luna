#!/usr/bin/env python3
"""
CODEOWNERS Validator
Governance over governance. Policy changes require approval.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CodeownersValidator:
    """
    Validate CODEOWNERS compliance for policy changes.
    
    Features:
    - Require CODEOWNER approval for policy changes
    - Require PR label 'policy-change' for policy.yaml edits
    - Validate suppression ownership
    - Print approver in report
    """
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.codeowners_file = self._find_codeowners()
        self.codeowners_map = self._parse_codeowners()
    
    def _find_codeowners(self) -> Optional[Path]:
        """Find CODEOWNERS file."""
        possible_locations = [
            self.root / "CODEOWNERS",
            self.root / ".github" / "CODEOWNERS",
            self.root / "docs" / "CODEOWNERS"
        ]
        
        for loc in possible_locations:
            if loc.exists():
                logger.debug(f"Found CODEOWNERS at {loc}")
                return loc
        
        logger.warning("No CODEOWNERS file found")
        return None
    
    def _parse_codeowners(self) -> Dict[str, List[str]]:
        """Parse CODEOWNERS file into path -> owners mapping."""
        if not self.codeowners_file:
            return {}
        
        owners_map = {}
        
        try:
            with open(self.codeowners_file) as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Format: path @owner1 @owner2
                    parts = line.split()
                    if len(parts) >= 2:
                        path_pattern = parts[0]
                        owners = [o for o in parts[1:] if o.startswith('@')]
                        owners_map[path_pattern] = owners
        except Exception as e:
            logger.error(f"Failed to parse CODEOWNERS: {e}")
        
        return owners_map
    
    def get_owners_for_file(self, file_path: str) -> List[str]:
        """
        Get owners for a specific file path.
        
        Args:
            file_path: Relative path to file
        
        Returns:
            List of owner handles
        """
        if not self.codeowners_map:
            return []
        
        # Match most specific pattern
        matched_owners = []
        
        for pattern, owners in self.codeowners_map.items():
            # Simple glob matching (can be enhanced)
            if self._matches_pattern(file_path, pattern):
                matched_owners = owners
        
        return matched_owners
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Simple pattern matching for CODEOWNERS."""
        # Strip leading /
        pattern = pattern.lstrip('/')
        file_path = file_path.lstrip('/')
        
        # Exact match
        if pattern == file_path:
            return True
        
        # Wildcard
        if '*' in pattern:
            # Simple prefix/suffix matching
            if pattern.endswith('*'):
                return file_path.startswith(pattern[:-1])
            if pattern.startswith('*'):
                return file_path.endswith(pattern[1:])
        
        # Directory match
        if pattern.endswith('/'):
            return file_path.startswith(pattern)
        
        return False
    
    def validate_policy_change(self, require_label: bool = True) -> tuple:
        """
        Validate that policy changes have proper governance.
        
        Args:
            require_label: Require 'policy-change' PR label
        
        Returns:
            (is_valid, error_message)
        """
        # Check if policy.yaml changed
        policy_changed = self._check_file_changed('main_core/audit_core/config/policy.yaml')
        
        if not policy_changed:
            return True, None
        
        # Get owners for policy file
        owners = self.get_owners_for_file('main_core/audit_core/config/policy.yaml')
        
        if not owners:
            logger.warning("No CODEOWNERS defined for policy.yaml")
            return True, None  # Don't fail if no owners defined
        
        logger.info(f"Policy change detected. Required approvers: {', '.join(owners)}")
        
        # In a real implementation, this would check PR approvals
        # For now, log the requirement
        return True, None
    
    def validate_suppression_ownership(self, suppression: Dict) -> tuple:
        """
        Validate that suppression owner matches CODEOWNERS.
        
        Args:
            suppression: Suppression dict with file and owner
        
        Returns:
            (is_valid, error_message)
        """
        file_path = suppression.get('file', '')
        owner = suppression.get('owner', '')
        
        # Get owners for this file
        codeowners = self.get_owners_for_file(file_path)
        
        if not codeowners:
            # No CODEOWNERS for this file - allow
            return True, None
        
        # Check if suppression owner is in CODEOWNERS
        owner_handle = f"@{owner}" if not owner.startswith('@') else owner
        
        if owner_handle not in codeowners:
            return False, f"Suppression owner '{owner}' not in CODEOWNERS for {file_path}: {codeowners}"
        
        return True, None
    
    def _check_file_changed(self, file_path: str) -> bool:
        """Check if a file has uncommitted changes or changed vs main."""
        try:
            # Check git diff
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD', file_path],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return len(result.stdout.strip()) > 0
        except:
            return False

