#!/usr/bin/env python3
"""
Import Check
Tests if core can be imported and measures timing
"""

import time
import importlib
from pathlib import Path
from typing import Dict

from .base_check import BaseCheck, CheckResult


class ImportCheck(BaseCheck):
    """Check if core imports successfully and measure timing."""
    
    def run(self, core_path: Path, core_name: str) -> CheckResult:
        """Test import timing and success."""
        t0 = time.perf_counter()
        issues = []
        details = {}
        
        try:
            importlib.invalidate_caches()
            module = importlib.import_module(core_name)
            import_time_ms = (time.perf_counter() - t0) * 1000
            
            details['import_time_ms'] = import_time_ms
            details['module_loaded'] = True
            
            # Check for slow imports
            slow_threshold = self.config.get('thresholds', {}).get('slow_import_ms', 200)
            if import_time_ms > slow_threshold:
                issues.append(f"Slow import ({import_time_ms:.1f}ms > {slow_threshold}ms)")
            
            passed = True
            
        except Exception as e:
            import_time_ms = (time.perf_counter() - t0) * 1000
            details['import_time_ms'] = import_time_ms
            details['module_loaded'] = False
            details['error'] = str(e)
            issues.append(f"Import failed: {str(e)[:200]}")
            passed = False
        
        return CheckResult(
            check_name='ImportCheck',
            severity='critical' if not passed else 'performance',
            passed=passed,
            issues=issues,
            details=details
        )

