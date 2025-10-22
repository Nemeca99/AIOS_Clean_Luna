#!/usr/bin/env python3
"""
Base Check Class
All audit checks inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CheckResult:
    """Result from a single check."""
    check_name: str
    severity: str  # 'critical', 'performance', 'safety', 'maintenance'
    passed: bool
    issues: List[str]
    details: Dict[str, Any]


class BaseCheck(ABC):
    """Base class for all audit checks."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def run(self, core_path: Path, core_name: str) -> CheckResult:
        """
        Run the check on a core.
        
        Args:
            core_path: Path to the core directory
            core_name: Name of the core
            
        Returns:
            CheckResult with findings
        """
        pass
    
    def is_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded from checking."""
        excluded_dirs = self.config.get('exclusions', {}).get('directories', [])
        excluded_patterns = self.config.get('exclusions', {}).get('file_patterns', [])
        
        # Check if in excluded directory
        for excluded in excluded_dirs:
            if excluded in str(file_path):
                return True
        
        # Check if matches excluded pattern
        import re
        for pattern in excluded_patterns:
            if re.match(pattern.replace('*', '.*'), file_path.name):
                return True
        
        return False

