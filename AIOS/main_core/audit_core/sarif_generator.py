#!/usr/bin/env python3
"""
SARIF Generator
Convert audit results to SARIF format for PR annotations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SARIFGenerator:
    """
    Generate SARIF (Static Analysis Results Interchange Format) output.
    
    Used for:
    - GitHub PR annotations
    - IDE integration
    - Standard tooling compatibility
    """
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
    
    def generate_sarif(self, 
                       audit_results: List[Dict],
                       static_analysis: Dict = None) -> Dict:
        """
        Generate SARIF 2.1.0 format output.
        
        Args:
            audit_results: List of core audit results
            static_analysis: Optional static analysis results
        
        Returns:
            SARIF dict
        """
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": []
        }
        
        # Create run for audit results
        audit_run = self._create_audit_run(audit_results)
        sarif['runs'].append(audit_run)
        
        # Add static analysis if available
        if static_analysis:
            static_run = self._create_static_analysis_run(static_analysis)
            if static_run:
                sarif['runs'].append(static_run)
        
        return sarif
    
    def _create_audit_run(self, audit_results: List[Dict]) -> Dict:
        """Create SARIF run from audit results."""
        results = []
        
        for core_result in audit_results:
            core_name = core_result.get('core_name')
            issues = core_result.get('issues', {})
            
            # Critical issues
            for issue in issues.get('critical', []):
                results.append(self._create_result(
                    rule_id='critical-issue',
                    level='error',
                    message=issue,
                    file_path=f"{core_name}/__init__.py"
                ))
            
            # Safety issues
            for issue in issues.get('safety', []):
                results.append(self._create_result(
                    rule_id='safety-issue',
                    level='warning',
                    message=issue,
                    file_path=f"{core_name}/__init__.py"
                ))
            
            # Secrets
            for secret in issues.get('secrets', []):
                results.append(self._create_result(
                    rule_id='secret-detected',
                    level='error',
                    message=secret,
                    file_path=f"{core_name}/__init__.py"
                ))
        
        return {
            "tool": {
                "driver": {
                    "name": "AIOS Audit V3",
                    "version": "3.0.0",
                    "informationUri": "https://github.com/your-org/aios",
                    "rules": self._get_audit_rules()
                }
            },
            "results": results
        }
    
    def _create_static_analysis_run(self, static_analysis: Dict) -> Dict:
        """Create SARIF run from static analysis tools."""
        results = []
        
        # Ruff violations
        ruff = static_analysis.get('ruff', {})
        if ruff.get('violations'):
            for violation in ruff['violations']:
                results.append(self._create_result(
                    rule_id=violation.get('code', 'ruff'),
                    level='warning',
                    message=violation.get('message', 'Ruff violation'),
                    file_path=violation.get('filename', 'unknown'),
                    line=violation.get('location', {}).get('row', 1)
                ))
        
        # MyPy errors
        mypy = static_analysis.get('mypy', {})
        if mypy.get('errors'):
            for error in mypy['errors']:
                # Parse mypy error format: "file:line: error: message"
                parts = error.split(':', 3)
                if len(parts) >= 4:
                    file_path = parts[0]
                    line = int(parts[1]) if parts[1].isdigit() else 1
                    message = parts[3].strip()
                    
                    results.append(self._create_result(
                        rule_id='mypy-type-error',
                        level='warning',
                        message=message,
                        file_path=file_path,
                        line=line
                    ))
        
        # Bandit security issues
        bandit = static_analysis.get('bandit', {})
        if bandit.get('high_severity', 0) > 0:
            results.append(self._create_result(
                rule_id='bandit-security',
                level='error',
                message=f"{bandit['high_severity']} high-severity security issues found",
                file_path='.'
            ))
        
        if not results:
            return None
        
        return {
            "tool": {
                "driver": {
                    "name": "AIOS Static Analysis",
                    "version": "3.0.0",
                    "rules": self._get_static_analysis_rules()
                }
            },
            "results": results
        }
    
    def _create_result(self, 
                      rule_id: str,
                      level: str,
                      message: str,
                      file_path: str,
                      line: int = 1) -> Dict:
        """Create a SARIF result object."""
        return {
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": message
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": file_path
                    },
                    "region": {
                        "startLine": line
                    }
                }
            }]
        }
    
    def _get_audit_rules(self) -> List[Dict]:
        """Get SARIF rules for audit checks."""
        return [
            {
                "id": "critical-issue",
                "name": "CriticalIssue",
                "shortDescription": {"text": "Critical audit issue"},
                "helpUri": "https://docs.aios/audit/critical"
            },
            {
                "id": "safety-issue",
                "name": "SafetyIssue",
                "shortDescription": {"text": "Code safety issue"},
                "helpUri": "https://docs.aios/audit/safety"
            },
            {
                "id": "secret-detected",
                "name": "SecretDetected",
                "shortDescription": {"text": "Potential secret in code"},
                "helpUri": "https://docs.aios/audit/secrets"
            }
        ]
    
    def _get_static_analysis_rules(self) -> List[Dict]:
        """Get SARIF rules for static analysis."""
        return [
            {
                "id": "ruff",
                "name": "RuffViolation",
                "shortDescription": {"text": "Ruff linter violation"}
            },
            {
                "id": "mypy-type-error",
                "name": "TypeMismatch",
                "shortDescription": {"text": "Type checking error"}
            },
            {
                "id": "bandit-security",
                "name": "SecurityIssue",
                "shortDescription": {"text": "Security vulnerability"}
            }
        ]
    
    def save_sarif(self, sarif: Dict, output_path: Path):
        """Save SARIF to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(sarif, f, indent=2)
        
        logger.info(f"SARIF output saved to {output_path}")

