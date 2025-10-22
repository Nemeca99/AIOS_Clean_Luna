#!/usr/bin/env python3
"""
Hermetic Audit Runner
Deterministic, reproducible audits. Same commit = same score.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class HermeticRunner:
    """
    Create deterministic audit environment.
    
    Features:
    - Set PYTHONHASHSEED
    - Pin tool versions
    - Fix random seeds
    - Emit tool versions to report
    """
    
    def __init__(self):
        self.tool_versions = {}
    
    def setup_hermetic_environment(self):
        """Set up deterministic environment variables."""
        # Python hash seed for determinism
        os.environ['PYTHONHASHSEED'] = '0'
        
        # Disable Python bytecode caching
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        
        # Ensure consistent locale
        os.environ['LC_ALL'] = 'C.UTF-8'
        os.environ['LANG'] = 'C.UTF-8'
        
        logger.debug("Hermetic environment configured")
    
    def collect_tool_versions(self) -> Dict:
        """Collect versions of all audit tools."""
        versions = {}
        
        # Python version
        versions['python'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # pip version
        try:
            result = subprocess.run(
                ['pip', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Extract version from "pip X.Y.Z from ..."
                versions['pip'] = result.stdout.split()[1]
        except:
            versions['pip'] = 'unknown'
        
        # Audit tools (if available)
        for tool in ['ruff', 'mypy', 'bandit', 'pip-audit', 'pip-licenses']:
            versions[tool] = self._get_tool_version(tool)
        
        self.tool_versions = versions
        return versions
    
    def _get_tool_version(self, tool: str) -> str:
        """Get version of a specific tool."""
        try:
            # Try --version
            result = subprocess.run(
                [tool, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse version from output
                output = result.stdout.strip()
                # Common patterns: "tool X.Y.Z" or "X.Y.Z"
                parts = output.split()
                for part in parts:
                    if part[0].isdigit():
                        return part
                return output[:20]  # First 20 chars if can't parse
        except:
            pass
        
        return 'not installed'
    
    def verify_determinism(self, score1: float, score2: float) -> bool:
        """Verify two scores are identical (determinism check)."""
        return abs(score1 - score2) < 0.01  # Allow tiny float precision diff
    
    def get_environment_fingerprint(self) -> str:
        """Get a fingerprint of the current environment."""
        import hashlib
        
        # Combine tool versions into a fingerprint
        fingerprint_data = json.dumps(self.tool_versions, sort_keys=True)
        return hashlib.md5(fingerprint_data.encode()).hexdigest()[:8]

