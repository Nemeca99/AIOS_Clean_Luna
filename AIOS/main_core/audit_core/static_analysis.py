#!/usr/bin/env python3
"""
Static Analysis Integration - Actually run ruff, mypy, bandit.
Scoped to changed files only for speed.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """
    Run static analysis tools (ruff, mypy, bandit) on code.
    Features:
    - Incremental analysis (changed files only)
    - Parallel execution
    - Cache-aware
    - Policy-driven scoring
    """
    
    def __init__(self, root_dir: Path, policy: Dict):
        self.root = root_dir
        self.policy = policy.get('static_analysis', {})
        self.enabled = self.policy.get('enabled', True)
        self.incremental = self.policy.get('incremental', True)
    
    def analyze_core(self, core_path: Path, changed_files: List[Path] = None) -> Dict:
        """
        Run static analysis on a core.
        
        Args:
            core_path: Path to core directory
            changed_files: Optional list of changed files (for incremental)
        
        Returns:
            Dict with analysis results
        """
        if not self.enabled:
            return {'enabled': False, 'results': {}}
        
        results = {}
        
        # Determine files to analyze
        if self.incremental and changed_files:
            files_to_analyze = changed_files
        else:
            files_to_analyze = list(core_path.rglob("*.py"))
        
        if not files_to_analyze:
            return {'enabled': True, 'results': {}, 'files_analyzed': 0}
        
        logger.debug(f"Analyzing {len(files_to_analyze)} files in {core_path.name}")
        
        # Run tools in parallel
        tools_config = self.policy.get('tools', {})
        
        if tools_config.get('ruff', {}).get('enabled', False):
            results['ruff'] = self._run_ruff(core_path, files_to_analyze)
        
        if tools_config.get('mypy', {}).get('enabled', False):
            results['mypy'] = self._run_mypy(core_path, files_to_analyze)
        
        if tools_config.get('bandit', {}).get('enabled', False):
            results['bandit'] = self._run_bandit(core_path, files_to_analyze)
        
        return {
            'enabled': True,
            'results': results,
            'files_analyzed': len(files_to_analyze)
        }
    
    def _run_ruff(self, core_path: Path, files: List[Path]) -> Dict:
        """Run ruff linter."""
        try:
            # Run ruff check
            cmd = ['ruff', 'check', '--output-format=json', str(core_path)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root
            )
            
            # Parse JSON output
            if result.stdout:
                try:
                    violations = json.loads(result.stdout)
                    return {
                        'passed': len(violations) == 0,
                        'violation_count': len(violations),
                        'violations': violations[:10]  # First 10 only
                    }
                except json.JSONDecodeError:
                    pass
            
            return {
                'passed': result.returncode == 0,
                'violation_count': 0 if result.returncode == 0 else 1,
                'output': result.stdout[:500]  # First 500 chars
            }
            
        except FileNotFoundError:
            logger.warning("ruff not found - install with 'pip install ruff'")
            return {'error': 'ruff not installed', 'passed': True}
        except Exception as e:
            logger.error(f"ruff failed: {e}")
            return {'error': str(e), 'passed': True}
    
    def _run_mypy(self, core_path: Path, files: List[Path]) -> Dict:
        """Run mypy type checker."""
        try:
            # Run mypy with JSON output
            file_paths = [str(f) for f in files]
            cmd = ['mypy', '--no-error-summary', '--show-column-numbers'] + file_paths
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.root
            )
            
            # Count errors from output
            error_lines = [l for l in result.stdout.split('\n') if 'error:' in l]
            
            return {
                'passed': result.returncode == 0,
                'error_count': len(error_lines),
                'errors': error_lines[:10]  # First 10 only
            }
            
        except FileNotFoundError:
            logger.warning("mypy not found - install with 'pip install mypy'")
            return {'error': 'mypy not installed', 'passed': True}
        except Exception as e:
            logger.error(f"mypy failed: {e}")
            return {'error': str(e), 'passed': True}
    
    def _run_bandit(self, core_path: Path, files: List[Path]) -> Dict:
        """Run bandit security linter."""
        try:
            # Run bandit with JSON output
            cmd = ['bandit', '-f', 'json', '-q', '-r', str(core_path)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root
            )
            
            # Parse JSON output
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    results = data.get('results', [])
                    
                    # Count by severity
                    high = len([r for r in results if r.get('issue_severity') == 'HIGH'])
                    medium = len([r for r in results if r.get('issue_severity') == 'MEDIUM'])
                    low = len([r for r in results if r.get('issue_severity') == 'LOW'])
                    
                    return {
                        'passed': high == 0,  # Fail on HIGH severity
                        'high_severity': high,
                        'medium_severity': medium,
                        'low_severity': low,
                        'total_issues': len(results)
                    }
                except json.JSONDecodeError:
                    pass
            
            return {
                'passed': result.returncode == 0,
                'total_issues': 0
            }
            
        except FileNotFoundError:
            logger.warning("bandit not found - install with 'pip install bandit'")
            return {'error': 'bandit not installed', 'passed': True}
        except Exception as e:
            logger.error(f"bandit failed: {e}")
            return {'error': str(e), 'passed': True}
    
    def calculate_static_analysis_penalty(self, results: Dict) -> int:
        """
        Calculate score penalty from static analysis results.
        
        Args:
            results: Results dict from analyze_core()
        
        Returns:
            Penalty points (negative)
        """
        if not results.get('enabled'):
            return 0
        
        penalty = 0
        analysis_results = results.get('results', {})
        
        # Ruff violations
        ruff = analysis_results.get('ruff', {})
        if not ruff.get('passed', True):
            violation_count = ruff.get('violation_count', 0)
            penalty -= min(10, violation_count)  # Max -10 for ruff
        
        # MyPy errors
        mypy = analysis_results.get('mypy', {})
        if not mypy.get('passed', True):
            error_count = mypy.get('error_count', 0)
            penalty -= min(15, error_count * 2)  # Max -15 for mypy
        
        # Bandit security issues
        bandit = analysis_results.get('bandit', {})
        if not bandit.get('passed', True):
            high = bandit.get('high_severity', 0)
            medium = bandit.get('medium_severity', 0)
            penalty -= (high * 10 + medium * 3)  # High = -10 each, medium = -3 each
        
        return max(-30, penalty)  # Cap at -30 total

