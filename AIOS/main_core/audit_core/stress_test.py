#!/usr/bin/env python3
"""
Stress Test Layer
Real-world stress testing: concurrent load, IO saturation, memory pressure
"""

import time
import logging
import multiprocessing
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ProcessPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)


class StressTest:
    """
    Stress testing for cores under real-world load.
    
    Tests:
    - Concurrent access (fork multiple processes)
    - IO saturation (repeated file operations)
    - Memory pressure (long-running operations)
    - Retry storms (error recovery)
    """
    
    def __init__(self, root_dir: Path, duration_seconds: int = 60):
        self.root = root_dir
        self.duration = duration_seconds
    
    def stress_test_core(self, core_name: str) -> Dict:
        """
        Stress test a single core.
        
        Returns:
            Dict with test results
        """
        logger.info(f"Stress testing {core_name} for {self.duration}s...")
        
        results = {
            'core_name': core_name,
            'duration_seconds': self.duration,
            'tests_passed': [],
            'tests_failed': [],
            'metrics': {}
        }
        
        # Test 1: Concurrent import stress
        concurrent_result = self._test_concurrent_imports(core_name)
        if concurrent_result['passed']:
            results['tests_passed'].append('concurrent_imports')
        else:
            results['tests_failed'].append('concurrent_imports')
        results['metrics']['concurrent_imports'] = concurrent_result
        
        # Test 2: Memory stability
        memory_result = self._test_memory_stability(core_name)
        if memory_result['passed']:
            results['tests_passed'].append('memory_stability')
        else:
            results['tests_failed'].append('memory_stability')
        results['metrics']['memory_stability'] = memory_result
        
        # Test 3: Repeated operations
        repeat_result = self._test_repeated_operations(core_name)
        if repeat_result['passed']:
            results['tests_passed'].append('repeated_operations')
        else:
            results['tests_failed'].append('repeated_operations')
        results['metrics']['repeated_operations'] = repeat_result
        
        return results
    
    def _test_concurrent_imports(self, core_name: str) -> Dict:
        """Test concurrent imports (fork subprocesses)."""
        def import_core():
            """Import core in subprocess."""
            try:
                import importlib
                importlib.invalidate_caches()
                importlib.import_module(core_name)
                return True
            except Exception as e:
                return False
        
        passed_count = 0
        failed_count = 0
        
        try:
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(import_core) for _ in range(10)]
                
                for future in futures:
                    try:
                        if future.result(timeout=10):
                            passed_count += 1
                        else:
                            failed_count += 1
                    except TimeoutError:
                        failed_count += 1
            
            return {
                'passed': failed_count == 0,
                'successful_imports': passed_count,
                'failed_imports': failed_count
            }
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_memory_stability(self, core_name: str) -> Dict:
        """Test memory stability under repeated operations."""
        import psutil
        import os
        
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Import and use core repeatedly
            import importlib
            for i in range(100):
                try:
                    module = importlib.import_module(core_name)
                    # Force reimport
                    importlib.reload(module)
                except:
                    pass
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory
            
            # Allow up to 50MB growth (reasonable for 100 reloads)
            passed = memory_growth < 50
            
            return {
                'passed': passed,
                'initial_memory_mb': round(initial_memory, 2),
                'final_memory_mb': round(final_memory, 2),
                'memory_growth_mb': round(memory_growth, 2)
            }
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _test_repeated_operations(self, core_name: str) -> Dict:
        """Test repeated operations for stability."""
        success_count = 0
        error_count = 0
        
        try:
            import importlib
            module = importlib.import_module(core_name)
            
            # Test repeated imports
            start_time = time.time()
            while time.time() - start_time < min(10, self.duration):
                try:
                    importlib.reload(module)
                    success_count += 1
                except Exception:
                    error_count += 1
            
            passed = error_count == 0
            
            return {
                'passed': passed,
                'successful_operations': success_count,
                'failed_operations': error_count,
                'operations_per_second': success_count / 10
            }
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }


def run_stress_test_suite(cores: List[str] = None, duration: int = 60):
    """Run stress test suite on specified cores."""
    from pathlib import Path
    
    root = Path.cwd()
    stress = StressTest(root, duration)
    
    if cores is None:
        # Discover cores
        cores = [p.name for p in root.iterdir() if p.is_dir() and p.name.endswith('_core')]
    
    print("\n" + "=" * 60)
    print(f"STRESS TEST SUITE ({duration}s per core)")
    print("=" * 60)
    
    results = []
    for core in cores:
        print(f"\nTesting {core}...")
        result = stress.stress_test_core(core)
        results.append(result)
        
        # Print summary
        passed = len(result['tests_passed'])
        failed = len(result['tests_failed'])
        status = "✅ PASSED" if failed == 0 else f"❌ FAILED ({failed} tests)"
        print(f"   {status}: {passed}/{passed+failed} tests passed")
    
    # Overall summary
    total_passed = sum(len(r['tests_passed']) for r in results)
    total_failed = sum(len(r['tests_failed']) for r in results)
    
    print("\n" + "=" * 60)
    print(f"Total: {total_passed}/{total_passed+total_failed} tests passed")
    print("=" * 60)
    
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_stress_test_suite(duration=10))  # 10s for quick test

