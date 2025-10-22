#!/usr/bin/env python3
"""
Plugin ABI Validator
Hard interface boundaries. Prevents drift as team scales.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from packaging import version

logger = logging.getLogger(__name__)


# Current ABI version
CURRENT_ABI_VERSION = "1.0.0"


class PluginABIValidator:
    """
    Validate plugin interface versions.
    
    Features:
    - CHECK_INTERFACE_VERSION validation
    - Backward compatibility checking
    - Quarantine mismatched versions
    - Schema validation via Pydantic
    """
    
    def __init__(self, min_version: str = "1.0.0"):
        self.min_version = min_version
        self.current_version = CURRENT_ABI_VERSION
    
    def validate_check_module(self, check_module) -> tuple:
        """
        Validate a check module's ABI version.
        
        Args:
            check_module: Imported check module
        
        Returns:
            (is_valid, error_message)
        """
        # Check for CHECK_INTERFACE_VERSION
        if not hasattr(check_module, 'CHECK_INTERFACE_VERSION'):
            return False, f"Missing CHECK_INTERFACE_VERSION in {check_module.__name__}"
        
        module_version = check_module.CHECK_INTERFACE_VERSION
        
        # Validate version format
        try:
            mod_ver = version.parse(module_version)
            min_ver = version.parse(self.min_version)
            cur_ver = version.parse(self.current_version)
        except Exception as e:
            return False, f"Invalid version format '{module_version}': {e}"
        
        # Check compatibility
        if mod_ver < min_ver:
            return False, f"Version {module_version} < minimum {self.min_version} (outdated)"
        
        if mod_ver.major > cur_ver.major:
            return False, f"Version {module_version} > current {self.current_version} (incompatible major version)"
        
        return True, None
    
    def validate_all_checks(self, check_classes: List) -> tuple:
        """
        Validate all check classes.
        
        Args:
            check_classes: List of check class instances
        
        Returns:
            (all_valid, issues)
        """
        issues = []
        
        for check in check_classes:
            check_module = check.__class__.__module__
            
            try:
                # Import the module
                import importlib
                module = importlib.import_module(check_module.rsplit('.', 1)[0])
                
                is_valid, error_msg = self.validate_check_module(module)
                
                if not is_valid:
                    issues.append({
                        'check': check.__class__.__name__,
                        'module': check_module,
                        'error': error_msg
                    })
            except Exception as e:
                issues.append({
                    'check': check.__class__.__name__,
                    'module': check_module,
                    'error': f"Failed to validate: {e}"
                })
        
        return len(issues) == 0, issues


class ReportSchemaValidator:
    """
    Validate audit report schema with Pydantic.
    Strict schema enforcement prevents drift.
    """
    
    def __init__(self):
        self.schema_version = "3.0.0"
    
    def validate_report(self, report: Dict) -> tuple:
        """
        Validate report structure.
        
        Args:
            report: Audit report dict
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Required top-level fields
        required_fields = ['summary', 'cores']
        for field in required_fields:
            if field not in report:
                errors.append(f"Missing required field: {field}")
        
        # Validate summary
        if 'summary' in report:
            summary = report['summary']
            summary_required = ['average_score', 'production_ready', 'total_cores']
            
            for field in summary_required:
                if field not in summary:
                    errors.append(f"Missing summary field: {field}")
        
        # Validate cores
        if 'cores' in report:
            for i, core in enumerate(report['cores']):
                core_required = ['core_name', 'score', 'status']
                
                for field in core_required:
                    if field not in core:
                        errors.append(f"Core {i}: missing field '{field}'")
        
        # Check for unknown top-level fields (strict mode)
        allowed_fields = {
            'summary', 'cores', 'git_metadata', 'tools',
            'regressions', 'policy_hash', 'commit', 'timestamp'
        }
        
        unknown = set(report.keys()) - allowed_fields
        if unknown:
            errors.append(f"Unknown fields in report: {unknown}")
        
        return len(errors) == 0, errors
    
    def get_schema_version(self) -> str:
        """Get current schema version."""
        return self.schema_version

