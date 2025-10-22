#!/usr/bin/env python3
"""
Performance Regression Tracker
Blocks merges on >30% p95 slowdowns vs last green commit.
"""

import json
import logging
import statistics
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Track performance metrics and detect regressions.
    
    Features:
    - p50/p95 import time tracking
    - Regression detection (>30% slowdown)
    - Historical trend analysis
    - Fail-on-regression enforcement
    """
    
    def __init__(self, trends_file: Path):
        self.trends_file = trends_file
        self.trends = self._load_trends()
    
    def _load_trends(self) -> List[Dict]:
        """Load historical trends from JSONL."""
        trends = []
        
        if not self.trends_file.exists():
            return trends
        
        try:
            with open(self.trends_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        trends.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Failed to load trends: {e}")
        
        return trends
    
    def record_performance(self, core_name: str, metrics: Dict, commit_hash: str):
        """
        Record performance metrics for a core.
        
        Args:
            core_name: Name of core
            metrics: Dict with 'import_time_ms', 'audit_time_ms', etc.
            commit_hash: Git commit hash
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'commit_hash': commit_hash,
            'core_name': core_name,
            'import_time_ms': metrics.get('import_time_ms', 0),
            'audit_time_ms': metrics.get('audit_time_ms', 0),
            'score': metrics.get('score', 0),
            'status': metrics.get('status', 'UNKNOWN')
        }
        
        # Append to trends file
        try:
            with open(self.trends_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to record performance: {e}")
    
    def get_historical_metrics(self, core_name: str, lookback: int = 10) -> List[Dict]:
        """
        Get historical metrics for a core.
        
        Args:
            core_name: Name of core
            lookback: Number of recent entries to return
        
        Returns:
            List of metric dicts
        """
        core_trends = [
            t for t in self.trends
            if t.get('core_name') == core_name
        ]
        
        # Return most recent N
        return core_trends[-lookback:] if core_trends else []
    
    def detect_regression(self, 
                         core_name: str, 
                         current_metrics: Dict,
                         threshold_pct: float = 30.0) -> Optional[Dict]:
        """
        Detect performance regression.
        
        Args:
            core_name: Name of core
            current_metrics: Current performance metrics
            threshold_pct: Regression threshold (default 30%)
        
        Returns:
            Regression details if detected, None otherwise
        """
        history = self.get_historical_metrics(core_name, lookback=10)
        
        if len(history) < 3:
            logger.debug(f"Insufficient history for {core_name} ({len(history)} entries)")
            return None
        
        # Calculate baseline (p95 of last green commits)
        green_imports = [
            h['import_time_ms'] for h in history
            if h.get('status') == 'OK' and h.get('import_time_ms', 0) > 0
        ]
        
        if not green_imports:
            logger.debug(f"No green baseline for {core_name}")
            return None
        
        # Calculate p50 and p95 of baseline
        baseline_p50 = statistics.median(green_imports)
        baseline_p95 = statistics.quantiles(green_imports, n=20)[18] if len(green_imports) > 5 else max(green_imports)
        
        # Get current import time
        current_import = current_metrics.get('import_time_ms', 0)
        
        if current_import == 0:
            return None
        
        # Calculate regression percentage
        p95_regression_pct = ((current_import - baseline_p95) / baseline_p95) * 100
        p50_regression_pct = ((current_import - baseline_p50) / baseline_p50) * 100
        
        # Check threshold
        if p95_regression_pct > threshold_pct:
            return {
                'core_name': core_name,
                'metric': 'import_time_ms',
                'current': current_import,
                'baseline_p50': round(baseline_p50, 1),
                'baseline_p95': round(baseline_p95, 1),
                'regression_pct': round(p95_regression_pct, 1),
                'threshold_pct': threshold_pct,
                'severity': 'CRITICAL' if p95_regression_pct > 50 else 'WARNING'
            }
        
        return None
    
    def check_budget(self, core_name: str, metrics: Dict, slos: Dict) -> Optional[Dict]:
        """
        Check if metrics meet SLO budgets.
        
        Args:
            core_name: Name of core
            metrics: Current metrics
            slos: SLO configuration from policy
        
        Returns:
            Violation details if budget exceeded, None otherwise
        """
        import_time_slo = slos.get('import_time', {})
        p95_threshold = import_time_slo.get('p95_threshold_ms', 5000)
        critical_threshold = import_time_slo.get('critical_threshold_ms', 10000)
        
        current_import = metrics.get('import_time_ms', 0)
        
        if current_import > critical_threshold:
            return {
                'core_name': core_name,
                'metric': 'import_time_ms',
                'current': current_import,
                'threshold': critical_threshold,
                'severity': 'CRITICAL',
                'message': f'Import time {current_import}ms exceeds critical threshold {critical_threshold}ms'
            }
        elif current_import > p95_threshold:
            return {
                'core_name': core_name,
                'metric': 'import_time_ms',
                'current': current_import,
                'threshold': p95_threshold,
                'severity': 'WARNING',
                'message': f'Import time {current_import}ms exceeds p95 threshold {p95_threshold}ms'
            }
        
        return None
    
    def generate_perf_summary(self, all_metrics: List[Dict]) -> Dict:
        """
        Generate performance summary across all cores.
        
        Args:
            all_metrics: List of metric dicts for all cores
        
        Returns:
            Summary dict
        """
        total_import_time = sum(m.get('import_time_ms', 0) for m in all_metrics)
        total_audit_time = sum(m.get('audit_time_ms', 0) for m in all_metrics)
        
        import_times = [m['import_time_ms'] for m in all_metrics if m.get('import_time_ms', 0) > 0]
        
        if import_times:
            p50_import = statistics.median(import_times)
            p95_import = statistics.quantiles(import_times, n=20)[18] if len(import_times) > 5 else max(import_times)
        else:
            p50_import = 0
            p95_import = 0
        
        return {
            'total_cores': len(all_metrics),
            'total_import_time_ms': round(total_import_time, 1),
            'total_audit_time_ms': round(total_audit_time, 1),
            'p50_import_time_ms': round(p50_import, 1),
            'p95_import_time_ms': round(p95_import, 1),
            'slowest_core': max(all_metrics, key=lambda m: m.get('import_time_ms', 0))['core_name'] if all_metrics else None
        }

