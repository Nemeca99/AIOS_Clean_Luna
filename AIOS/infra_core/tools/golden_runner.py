"""
Golden Test Runner
Replays golden prompts and validates: win rate, response quality, latency, token-efficiency
CI gate: fail on regression
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Luna system via main AIOS
try:
    from main import AIOSClean
    AIOS_AVAILABLE = True
except ImportError:
    AIOS_AVAILABLE = False
    print("⚠️ AIOS system not available")

# Import provenance
try:
    from utils_core.provenance import ProvenanceLogger, log_response_event
    PROVENANCE_AVAILABLE = True
except ImportError:
    PROVENANCE_AVAILABLE = False

class GoldenRunner:
    """
    Golden test runner for regression detection
    """
    
    def __init__(self, output_dir: str = "data_core/goldens"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize AIOS and Luna
        if AIOS_AVAILABLE:
            self.aios = AIOSClean()
            # Use _get_system to lazy load luna
            self.luna = self.aios._get_system('luna')
        else:
            self.aios = None
            self.luna = None
        
        # Initialize provenance logger
        if PROVENANCE_AVAILABLE:
            self.prov_logger = ProvenanceLogger('data_core/analytics/golden_tests.ndjson')
        else:
            self.prov_logger = None
    
    def record_baseline(self, golden_set: str, output_file: str):
        """
        Record baseline results for golden set
        
        Args:
            golden_set: Path to JSON file with golden prompts
            output_file: Path to save baseline results
        """
        print(f"📝 Recording baseline from: {golden_set}")
        
        # Load golden set
        with open(golden_set, 'r') as f:
            goldens = json.load(f)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'golden_set': golden_set,
            'total_tests': len(goldens),
            'tests': []
        }
        
        # Run each golden test
        for i, golden in enumerate(goldens):
            print(f"\n🧪 Test {i+1}/{len(goldens)}: {golden['id']}")
            
            test_result = self._run_golden_test(golden)
            results['tests'].append(test_result)
            
            # Print summary
            if 'error' in test_result:
                print(f"   ❌ Error: {test_result['error']}")
            else:
                print(f"   ✅ Completed in {test_result['latency_ms']:.0f}ms")
                print(f"   Source: {test_result['source']}")
                print(f"   Response: {test_result['response'][:50]}...")
        
        # Calculate summary stats
        results['summary'] = self._calculate_summary(results['tests'])
        
        # Save baseline
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Baseline recorded to: {output_file}")
        print(f"\n📊 Summary:")
        print(f"   Total tests: {results['summary']['total']}")
        
        # Only print detailed stats if we have valid tests
        if results['summary']['total'] > 0:
            print(f"   Avg latency: {results['summary']['avg_latency_ms']:.0f}ms")
            print(f"   Main model: {results['summary']['main_model_count']} ({results['summary']['main_model_percent']:.1f}%)")
            print(f"   Embedder: {results['summary']['embedder_count']} ({results['summary']['embedder_percent']:.1f}%)")
        else:
            print(f"   ❌ All tests failed - check LM Studio is running with models loaded")
            print(f"   Errors: {results['summary']['errors']}")
        
        return results
    
    def compare_to_baseline(self, golden_set: str, baseline_file: str, threshold: float = 0.1):
        """
        Compare current performance to baseline
        
        Args:
            golden_set: Path to JSON file with golden prompts
            baseline_file: Path to baseline results
            threshold: Regression threshold (0.1 = 10%)
        
        Returns:
            Dictionary with comparison results
        """
        print(f"📊 Comparing to baseline: {baseline_file}")
        
        # Load baseline
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)
        
        # Run current tests
        current = self.record_baseline(golden_set, self.output_dir / 'current_results.json')
        
        # Compare
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'baseline_timestamp': baseline['timestamp'],
            'regression_threshold': threshold,
            'regressions_detected': [],
            'improvements_detected': [],
            'status': 'PASS'
        }
        
        # Check if current tests produced valid results
        if current['summary']['total'] == 0:
            print("\n❌ CI FAIL: All current tests failed - cannot compare to baseline")
            comparison['status'] = 'FAIL'
            comparison['regressions_detected'].append({
                'metric': 'test_execution',
                'error': f"All {current['summary']['errors']} tests failed - check LM Studio is running"
            })
            self._print_comparison(comparison)
            return comparison
        
        # Compare latency
        baseline_latency = baseline['summary']['avg_latency_ms']
        current_latency = current['summary']['avg_latency_ms']
        latency_change = (current_latency - baseline_latency) / baseline_latency
        
        if latency_change > threshold:
            comparison['regressions_detected'].append({
                'metric': 'avg_latency_ms',
                'baseline': baseline_latency,
                'current': current_latency,
                'change_percent': latency_change * 100,
                'threshold_percent': threshold * 100
            })
            comparison['status'] = 'FAIL'
        elif latency_change < -threshold:
            comparison['improvements_detected'].append({
                'metric': 'avg_latency_ms',
                'baseline': baseline_latency,
                'current': current_latency,
                'improvement_percent': abs(latency_change) * 100
            })
        
        # Compare routing split
        baseline_main_pct = baseline['summary']['main_model_percent']
        current_main_pct = current['summary']['main_model_percent']
        routing_change = abs(current_main_pct - baseline_main_pct)
        
        if routing_change > (threshold * 100):  # 10 percentage points
            comparison['regressions_detected'].append({
                'metric': 'main_model_routing_percent',
                'baseline': baseline_main_pct,
                'current': current_main_pct,
                'change': routing_change,
                'threshold': threshold * 100
            })
            comparison['status'] = 'FAIL'
        
        # Add metrics for SLO monitoring
        # Extract latencies from current test results
        current_latencies = [t['latency_ms'] for t in current['tests'] if 'error' not in t and 'latency_ms' in t]
        sorted_latencies = sorted(current_latencies) if current_latencies else []
        
        comparison['metrics'] = {
            'pass_rate': 1.0 if comparison['status'] == 'PASS' else 0.0,
            'p50_ms': sorted_latencies[len(sorted_latencies)//2] if sorted_latencies else 0.0,
            'p95_ms': sorted_latencies[int(len(sorted_latencies)*0.95)] if sorted_latencies else 0.0,
            'mean_ms': current_latency if current['summary']['total'] > 0 else 0.0
        }
        
        # Print results
        self._print_comparison(comparison)
        
        # Save comparison (timestamped)
        comparison_file = self.output_dir / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        return comparison
    
    def _run_golden_test(self, golden: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single golden test"""
        if not self.luna:
            return {
                'id': golden['id'],
                'question': golden['question'],
                'error': 'Luna system not available'
            }
        
        # Time the response
        start_time = time.perf_counter()
        
        try:
            print(f"   DEBUG: Calling python_impl.process_question with question: {type(golden['question'])}, trait: {type(golden.get('trait', 'general'))}")
            response, metadata = self.luna.python_impl.process_question(
                golden['question'],
                golden.get('trait', 'general')
            )
            print(f"   DEBUG: Got response: {type(response)}, metadata: {type(metadata)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                'id': golden['id'],
                'question': golden['question'],
                'error': str(e)
            }
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        # Build result
        result = {
            'id': golden['id'],
            'question': golden['question'],
            'trait': golden.get('trait', 'balanced'),
            'response': response,
            'latency_ms': latency_ms,
            'source': metadata.get('source', 'unknown'),
            'tier': metadata.get('tier', 'unknown'),
            'response_type': metadata.get('response_type', 'unknown'),
            'response_length': len(response),
            'timestamp': datetime.now().isoformat()
        }
        
        # Log to provenance if available
        if self.prov_logger:
            log_response_event(
                self.prov_logger,
                conv_id=f"golden_{golden['id']}",
                msg_id=1,
                question=golden['question'],
                trait=golden.get('trait', 'balanced'),
                response=response,
                meta={'source': metadata.get('source'), 'tier': metadata.get('tier'), 'response_type': metadata.get('response_type')},
                carma={'fragments_found': 0},  # Goldens don't use CARMA
                math_weights={'latency_ms': latency_ms}
            )
        
        return result
    
    def _calculate_summary(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        valid_tests = [t for t in tests if 'error' not in t]
        
        if not valid_tests:
            return {'total': 0, 'errors': len(tests)}
        
        latencies = [t['latency_ms'] for t in valid_tests]
        sources = [t['source'] for t in valid_tests]
        
        main_model_count = sum(1 for s in sources if s == 'main_model')
        embedder_count = sum(1 for s in sources if s == 'embedder')
        
        return {
            'total': len(valid_tests),
            'errors': len(tests) - len(valid_tests),
            'avg_latency_ms': sum(latencies) / len(latencies),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'main_model_count': main_model_count,
            'embedder_count': embedder_count,
            'main_model_percent': (main_model_count / len(valid_tests)) * 100 if valid_tests else 0,
            'embedder_percent': (embedder_count / len(valid_tests)) * 100 if valid_tests else 0
        }
    
    def _print_comparison(self, comparison: Dict[str, Any]):
        """Print comparison results"""
        print("\n" + "="*70)
        print("GOLDEN TEST COMPARISON REPORT")
        print("="*70)
        
        print(f"\nStatus: {comparison['status']}")
        print(f"Regression Threshold: {comparison['regression_threshold'] * 100}%")
        
        if comparison['regressions_detected']:
            print(f"\n❌ REGRESSIONS DETECTED ({len(comparison['regressions_detected'])}):")
            for reg in comparison['regressions_detected']:
                print(f"   - {reg['metric']}:")
                # Handle error regressions (no baseline/current values)
                if 'error' in reg:
                    print(f"     Error: {reg['error']}")
                else:
                    print(f"     Baseline: {reg['baseline']:.2f}")
                    print(f"     Current:  {reg['current']:.2f}")
                    print(f"     Change:   {reg.get('change_percent', reg.get('change', 0)):.1f}%")
        else:
            print("\n✅ NO REGRESSIONS DETECTED")
        
        if comparison['improvements_detected']:
            print(f"\n📈 IMPROVEMENTS DETECTED ({len(comparison['improvements_detected'])}):")
            for imp in comparison['improvements_detected']:
                print(f"   - {imp['metric']}:")
                print(f"     Baseline: {imp['baseline']:.2f}")
                print(f"     Current:  {imp['current']:.2f}")
                print(f"     Improvement: {imp['improvement_percent']:.1f}%")
        
        print("="*70 + "\n")

def main():
    """Main CLI"""
    parser = argparse.ArgumentParser(description='Golden Test Runner')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record baseline')
    record_parser.add_argument('--set', required=True, help='Golden set JSON file')
    record_parser.add_argument('--out', required=True, help='Output file for results')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare to baseline')
    compare_parser.add_argument('--set', required=True, help='Golden set JSON file')
    compare_parser.add_argument('--baseline', required=True, help='Baseline results file')
    compare_parser.add_argument('--threshold', type=float, default=0.1, help='Regression threshold (default: 0.1 = 10%)')
    compare_parser.add_argument('--out', help='Output file for comparison results (default: data_core/goldens/last_report.json)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create runner
    runner = GoldenRunner()
    
    if args.command == 'record':
        runner.record_baseline(args.set, args.out)
    
    elif args.command == 'compare':
        comparison = runner.compare_to_baseline(args.set, args.baseline, args.threshold)
        
        # Save to specified output file if provided
        if args.out:
            output_path = Path(args.out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(comparison, f, indent=2)
            print(f"\n📝 Comparison saved to: {args.out}")
        
        # Exit with error code if regressions detected
        if comparison['status'] == 'FAIL':
            print("❌ CI FAIL: Regressions detected")
            sys.exit(1)
        else:
            print("✅ CI PASS: No regressions detected")
            sys.exit(0)

if __name__ == "__main__":
    main()

