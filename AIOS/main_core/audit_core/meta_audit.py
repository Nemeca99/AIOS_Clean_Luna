#!/usr/bin/env python3
"""
Meta-Audit: Audit the Auditor
Verifies scoring logic hasn't drifted, configuration is valid, and math is correct
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class MetaAudit:
    """
    Audits the audit system itself.
    Catches entropy, config drift, and scoring math errors.
    """
    
    def __init__(self, audit_core_path: Path):
        self.audit_path = audit_core_path
        self.config_path = audit_core_path / "config"
    
    def run_meta_audit(self) -> Tuple[bool, List[str]]:
        """
        Run complete meta-audit.
        
        Returns:
            (passed, issues)
        """
        issues = []
        
        logger.info("Running meta-audit on audit system...")
        
        # Test 1: Configuration integrity
        config_issues = self._verify_config_integrity()
        issues.extend(config_issues)
        
        # Test 2: Scoring math consistency
        math_issues = self._verify_scoring_math()
        issues.extend(math_issues)
        
        # Test 3: Check plugin integrity
        plugin_issues = self._verify_check_plugins()
        issues.extend(plugin_issues)
        
        # Test 4: Mock data scoring
        mock_issues = self._test_mock_scoring()
        issues.extend(mock_issues)
        
        passed = len(issues) == 0
        
        if passed:
            logger.info("Meta-audit PASSED - Audit system is healthy")
        else:
            logger.warning(f"Meta-audit found {len(issues)} issues")
        
        return passed, issues
    
    def _verify_config_integrity(self) -> List[str]:
        """Verify configuration files are valid and complete."""
        issues = []
        
        # Check scoring_weights.json
        scoring_file = self.config_path / "scoring_weights.json"
        if not scoring_file.exists():
            issues.append("CRITICAL: scoring_weights.json missing")
        else:
            try:
                with open(scoring_file) as f:
                    config = json.load(f)
                
                # Verify required sections
                required = ['penalties', 'bonuses', 'thresholds', 'caps']
                for section in required:
                    if section not in config:
                        issues.append(f"scoring_weights.json missing '{section}' section")
                
                # Verify penalty values are negative
                penalties = config.get('penalties', {})
                for key, value in penalties.items():
                    if value > 0:
                        issues.append(f"Penalty '{key}' should be negative, got {value}")
                
                # Verify bonuses are positive
                bonuses = config.get('bonuses', {})
                for key, value in bonuses.items():
                    if isinstance(value, (int, float)) and value < 0:
                        issues.append(f"Bonus '{key}' should be positive, got {value}")
                        
            except json.JSONDecodeError:
                issues.append("CRITICAL: scoring_weights.json is invalid JSON")
        
        # Check check_patterns.json
        patterns_file = self.config_path / "check_patterns.json"
        if not patterns_file.exists():
            issues.append("CRITICAL: check_patterns.json missing")
        else:
            try:
                with open(patterns_file) as f:
                    config = json.load(f)
                
                # Verify has patterns
                if 'grep_patterns' not in config:
                    issues.append("check_patterns.json missing 'grep_patterns'")
                        
            except json.JSONDecodeError:
                issues.append("CRITICAL: check_patterns.json is invalid JSON")
        
        return issues
    
    def _verify_scoring_math(self) -> List[str]:
        """Verify scoring math is consistent."""
        issues = []
        
        try:
            scoring_file = self.config_path / "scoring_weights.json"
            with open(scoring_file) as f:
                config = json.load(f)
            
            penalties = config.get('penalties', {})
            caps = config.get('caps', {})
            
            # Verify math: Individual penalties should be reasonable
            # Check that no single critical issue takes more than 30 points
            if abs(penalties.get('critical_issue', -25)) > 30:
                issues.append(f"Critical penalty too high: {penalties.get('critical_issue')}")
            
            # Check caps exist and are reasonable
            if 'max_total_penalty' in caps:
                max_total = caps.get('max_total_penalty', 80)
                if max_total > 100:
                    issues.append(f"Max total penalty ({max_total}) exceeds 100 points")
            
            # Verify thresholds make sense
            thresholds = config.get('thresholds', {})
            prod_ready = thresholds.get('production_ready_score', 85)
            warning = thresholds.get('warning_threshold', 70)
            
            if prod_ready <= warning:
                issues.append(f"Threshold logic: production_ready ({prod_ready}) must be > warning ({warning})")
            
        except Exception as e:
            issues.append(f"Scoring math verification failed: {e}")
        
        return issues
    
    def _verify_check_plugins(self) -> List[str]:
        """Verify check plugins are valid."""
        issues = []
        
        checks_dir = self.audit_path / "checks"
        if not checks_dir.exists():
            issues.append("CRITICAL: checks/ directory missing")
            return issues
        
        # Verify base_check.py exists
        if not (checks_dir / "base_check.py").exists():
            issues.append("CRITICAL: checks/base_check.py missing")
        
        # Try importing checks
        try:
            import sys
            sys.path.insert(0, str(self.audit_path.parent.parent))
            from main_core.audit_core.checks import BaseCheck, ImportCheck, PatternCheck
        except ImportError as e:
            issues.append(f"Check import failed: {e}")
        
        return issues
    
    def _test_mock_scoring(self) -> List[str]:
        """Test scoring on mock data to verify math."""
        issues = []
        
        # Mock test cases
        test_cases = [
            {
                'name': 'perfect_core',
                'critical': [],
                'perf': [],
                'safety': [],
                'missing': [],
                'positive': ['has_logging', 'has_type_hints', 'has_docstrings'],
                'import_time': 0.5,
                'expected_min': 95,  # Should score very high
            },
            {
                'name': 'critical_core',
                'critical': ['import_failure', 'crash_on_init'],
                'perf': [],
                'safety': [],
                'missing': [],
                'positive': [],
                'import_time': 1.0,
                'expected_max': 60,  # Should score low (2 critical issues)
            },
            {
                'name': 'average_core',
                'critical': [],
                'perf': ['slow_function'],
                'safety': ['10x print_instead_of_log'],
                'missing': [],
                'positive': ['has_logging'],
                'import_time': 5.0,
                'expected_min': 70,
                'expected_max': 95,
            }
        ]
        
        # Load scoring config
        try:
            scoring_file = self.config_path / "scoring_weights.json"
            with open(scoring_file) as f:
                config = json.load(f)
            
            for test in test_cases:
                score = self._calculate_mock_score(test, config)
                
                # Verify expectations
                if 'expected_min' in test and score < test['expected_min']:
                    issues.append(f"Mock test '{test['name']}': score {score} < expected min {test['expected_min']}")
                if 'expected_max' in test and score > test['expected_max']:
                    issues.append(f"Mock test '{test['name']}': score {score} > expected max {test['expected_max']}")
                
        except Exception as e:
            issues.append(f"Mock scoring test failed: {e}")
        
        return issues
    
    def _calculate_mock_score(self, test_data: Dict, config: Dict) -> int:
        """Calculate score for mock test data."""
        base = 100
        
        # Apply penalties
        penalties = config.get('penalties', {})
        base += penalties.get('critical_issue', -30) * len(test_data['critical'])
        base += penalties.get('performance_issue', -10) * len(test_data['perf'])
        base += penalties.get('real_safety_issue', -8) * len(test_data['safety'])
        base += penalties.get('missing_feature', -6) * len(test_data['missing'])
        
        # Apply bonuses
        bonuses = config.get('bonuses', {})
        if len(test_data['positive']) >= 3:
            base += min(6, len(test_data['positive']))
        
        if test_data['import_time'] < 1.0:
            base += bonuses.get('fast_import_1ms', 3)
        
        if len(test_data['safety']) == 0:
            base += bonuses.get('zero_real_safety_issues', 4)
        
        if len(test_data['critical']) == 0 and len(test_data['missing']) == 0:
            base += bonuses.get('zero_critical_and_missing', 2)
        
        return max(0, min(100, base))


def run_meta_audit_standalone():
    """Standalone meta-audit execution."""
    from pathlib import Path
    
    audit_path = Path(__file__).parent
    meta = MetaAudit(audit_path)
    
    passed, issues = meta.run_meta_audit()
    
    print("\n" + "=" * 60)
    print("META-AUDIT: AUDIT THE AUDITOR")
    print("=" * 60)
    
    if passed:
        print("\n✅ Meta-audit PASSED")
        print("   Audit system is healthy and trustworthy")
    else:
        print(f"\n❌ Meta-audit FAILED ({len(issues)} issues)")
        print("\nIssues found:")
        for issue in issues:
            print(f"   - {issue}")
    
    print("\n" + "=" * 60)
    
    return 0 if passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_meta_audit_standalone())

