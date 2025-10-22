#!/usr/bin/env python3
"""
Auditor - Core business logic for running audit checks and scoring.
V3: Enhanced with policy enforcement, secrets scanning, and per-core quality bars.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from main_core.audit_core.checks import (
    ImportCheck,
    PatternCheck,
    CoreSpecificCheck,
    SecretsCheck
)
from main_core.audit_core.policy_loader import PolicyLoader, AllowlistManager

logger = logging.getLogger(__name__)


class Auditor:
    """
    Orchestrates audit checks across cores.
    
    V3 Features:
    - Policy-driven enforcement
    - Per-core quality bars
    - Secrets scanning
    - Allowlist management
    """
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.config = self._load_config()
        
        # Load V3 policy and allowlist
        self.policy = PolicyLoader()
        self.allowlist = AllowlistManager()
        
        # Validate allowlist on init
        valid, issues = self.allowlist.validate_all_suppressions()
        if not valid:
            logger.warning(f"Allowlist validation issues: {issues}")
        
        # Initialize checks (V3 includes secrets scanning)
        self.checks = [
            ImportCheck(self.config),
            PatternCheck(self.config),
            CoreSpecificCheck(self.config),
            SecretsCheck(self.policy.policy)  # NEW: Secrets scanning
        ]
        
        logger.info(f"Auditor V3 initialized with {len(self.checks)} check types")
    
    def _load_config(self) -> Dict:
        """Load configuration from files."""
        config_path = Path(__file__).parent / "config" / "scoring_weights.json"
        patterns_path = Path(__file__).parent / "config" / "check_patterns.json"
        
        config = {}
        
        # Load scoring weights
        try:
            with open(config_path) as f:
                config.update(json.load(f))
        except Exception as e:
            logger.warning(f"Failed to load scoring config: {e}")
        
        # Load check patterns
        try:
            with open(patterns_path) as f:
                patterns = json.load(f)
                config['grep_patterns'] = patterns.get('grep_patterns', [])
        except Exception as e:
            logger.warning(f"Failed to load patterns config: {e}")
        
        return config
    
    def discover_cores(self) -> List[str]:
        """Discover all *_core directories."""
        cores = []
        for path in self.root.iterdir():
            if path.is_dir() and path.name.endswith('_core'):
                cores.append(path.name)
        
        return sorted(cores)
    
    def audit_core(self, core_name: str) -> Dict:
        """Audit a single core with V3 policy enforcement."""
        core_path = self.root / core_name
        
        if not core_path.exists():
            return {
                'core_name': core_name,
                'status': 'CRITICAL',
                'error': 'Core directory not found',
                'score': 0,
                'meets_policy': False
            }
        
        # Run all checks
        results = {}
        for check in self.checks:
            check_name = check.__class__.__name__
            try:
                results[check_name] = check.run(core_path)
            except Exception as e:
                logger.error(f"Check {check_name} failed for {core_name}: {e}")
                results[check_name] = {'error': str(e)}
        
        # Calculate score
        score = self.calculate_score(core_name, results)
        
        # V3: Check against per-core policy
        core_policy = self.policy.get_core_policy(core_name)
        meets_policy = self._check_core_policy(core_name, score, results, core_policy)
        
        return {
            'core_name': core_name,
            'results': results,
            'score': score,
            'status': self._determine_status(results, score),
            'meets_policy': meets_policy,  # NEW: V3 per-core policy check
            'policy': core_policy  # NEW: Include policy for reference
        }
    
    def _check_core_policy(self, core_name: str, score: float, results: Dict, policy: Dict) -> bool:
        """
        V3: Check if core meets its policy requirements.
        
        Returns:
            True if meets policy, False otherwise
        """
        min_score = policy.get('minimum_score', 80)
        max_critical = policy.get('max_critical', 0)
        max_performance = policy.get('max_performance', 2)
        max_safety = policy.get('max_safety', 10)
        
        # Count issues
        critical_count = 0
        perf_count = 0
        safety_count = 0
        
        for check_name, result in results.items():
            if isinstance(result, dict):
                critical_count += len(result.get('critical', []))
                perf_count += len(result.get('perf', []))
                safety_count += len(result.get('safety', []))
        
        # Check thresholds
        if score < min_score:
            logger.debug(f"{core_name}: Score {score} < minimum {min_score}")
            return False
        
        if critical_count > max_critical:
            logger.debug(f"{core_name}: Critical count {critical_count} > max {max_critical}")
            return False
        
        if perf_count > max_performance:
            logger.debug(f"{core_name}: Perf count {perf_count} > max {max_performance}")
            return False
        
        if safety_count > max_safety:
            logger.debug(f"{core_name}: Safety count {safety_count} > max {max_safety}")
            return False
        
        return True
    
    def audit_all_cores(self, parallel: bool = True, max_workers: int = 4) -> List[Dict]:
        """Audit all discovered cores."""
        cores = self.discover_cores()
        logger.info(f"Auditing {len(cores)} cores{'in parallel' if parallel else ''}")
        
        if not parallel:
            return [self.audit_core(core) for core in cores]
        
        # Parallel execution
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_core = {executor.submit(self.audit_core, core): core for core in cores}
            
            for future in as_completed(future_to_core):
                core = future_to_core[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to audit {core}: {e}")
                    results.append({
                        'core_name': core,
                        'status': 'CRITICAL',
                        'error': str(e),
                        'score': 0,
                        'meets_policy': False
                    })
        
        return results
    
    def calculate_score(self, core_name: str, results: Dict) -> int:
        """Calculate score for core based on check results."""
        base = 100
        
        # Extract issues from results
        critical = []
        perf = []
        safety = []
        missing = []
        positive = []
        
        for check_name, result in results.items():
            if isinstance(result, dict):
                critical.extend(result.get('critical', []))
                perf.extend(result.get('perf', []))
                safety.extend(result.get('safety', []))
                missing.extend(result.get('missing', []))
                positive.extend(result.get('positive', []))
        
        # Apply penalties from policy
        scoring = self.policy.get_scoring_config()
        penalties = scoring.get('penalties', {})
        bonuses = scoring.get('bonuses', {})
        
        base += penalties.get('critical_issue', -25) * len(critical)
        base += penalties.get('performance_issue', -8) * len(perf)
        base += penalties.get('real_safety_issue', -6) * len(safety)
        base += penalties.get('missing_feature', -5) * len(missing)
        
        # Apply bonuses
        if len(critical) == 0 and len(missing) == 0:
            base += bonuses.get('zero_critical_and_missing', 2)
        
        if len(safety) == 0:
            base += bonuses.get('zero_real_safety_issues', 4)
        
        if len(positive) >= 3:
            base += min(6, len(positive))
        
        # Get import time bonus if available
        import_result = results.get('ImportCheck', {})
        if import_result.get('import_ok'):
            import_time_ms = import_result.get('import_time_ms', 0)
            if import_time_ms < 100:
                base += bonuses.get('fast_import_100ms', 2)
            elif import_time_ms < 1000:
                base += bonuses.get('fast_import_1s', 1)
        
        return max(0, min(100, base))
    
    def _determine_status(self, results: Dict, score: int) -> str:
        """Determine status based on results and score."""
        # Check for critical issues
        for check_name, result in results.items():
            if isinstance(result, dict):
                if len(result.get('critical', [])) > 0:
                    return 'CRITICAL'
        
        # Check score thresholds
        if score < 70:
            return 'WARNING'
        
        return 'OK'
