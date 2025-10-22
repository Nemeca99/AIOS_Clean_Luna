#!/usr/bin/env python3
"""
Core-Specific Check
Runs checks tailored to specific cores (loaded from config)
"""

from pathlib import Path
from typing import Dict, List

from .base_check import BaseCheck, CheckResult


class CoreSpecificCheck(BaseCheck):
    """Run core-specific checks from configuration."""
    
    def run(self, core_path: Path, core_name: str) -> CheckResult:
        """Run core-specific checks."""
        core_checks = self.config.get('core_specific_checks', {}).get(core_name, {})
        
        issues = []
        positive_findings = []
        details = {}
        
        for check_name, check_config in core_checks.items():
            file_rel = check_config.get('file', '')
            check_expr = check_config.get('check', '')
            severity = check_config.get('severity', 'safety')
            is_positive = check_config.get('positive', False)
            description = check_config.get('description', check_name)
            
            # Find the file
            file_path = core_path / file_rel
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Evaluate the check (simple eval of boolean expression)
                # Note: Using eval here is controlled - only on trusted config
                result = eval(check_expr, {'content': content})
                
                if is_positive:
                    # Positive check - good if true
                    if result:
                        positive_findings.append(description)
                else:
                    # Negative check - bad if true
                    if result:
                        issues.append(description)
                
                details[check_name] = {
                    'file': str(file_rel),
                    'passed': result if is_positive else not result
                }
                
            except Exception as e:
                details[check_name] = {'error': str(e)}
        
        return CheckResult(
            check_name='CoreSpecificCheck',
            severity='mixed',
            passed=len(issues) == 0,
            issues=issues,
            details={'issues': issues, 'positive': positive_findings, 'checks': details}
        )

