#!/usr/bin/env python3
"""
Pattern Check
Scans code for anti-patterns using regex
"""

import re
from pathlib import Path
from collections import defaultdict

from .base_check import BaseCheck, CheckResult


class PatternCheck(BaseCheck):
    """Check for code anti-patterns using regex."""
    
    def run(self, core_path: Path, core_name: str) -> CheckResult:
        """Scan for code patterns."""
        patterns = self.config.get('grep_patterns', {})
        issues = []
        details = defaultdict(list)
        
        # Scan all Python files
        for py_file in core_path.rglob("*.py"):
            if self.is_excluded(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                for pattern_name, pattern_config in patterns.items():
                    pattern = pattern_config.get('pattern', '')
                    severity = pattern_config.get('severity', 'safety')
                    
                    # Search for pattern
                    matches = len(re.findall(pattern, content, re.MULTILINE))
                    if matches > 0:
                        relative_path = py_file.relative_to(core_path.parent)
                        details[pattern_name].append({
                            'file': str(relative_path),
                            'count': matches
                        })
            except Exception:
                continue
        
        # Summarize findings
        for pattern_name, files in details.items():
            total_count = sum(f['count'] for f in files)
            if total_count > 0:
                issues.append(f"{total_count}x {pattern_name}")
        
        return CheckResult(
            check_name='PatternCheck',
            severity='safety',
            passed=len(issues) == 0,
            issues=issues,
            details=dict(details)
        )

