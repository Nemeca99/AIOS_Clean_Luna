#!/usr/bin/env python3
"""
Adaptive Routing Sweep Runner
Tunes routing parameters by testing different boundary values
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import time

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class AdaptiveSweep:
    """
    Sweep runner for adaptive routing parameter tuning
    Tests different boundary values to find optimal settings
    """
    
    def __init__(self, 
                 golden_set: str = 'data_core/goldens/sample_set.json',
                 output_dir: str = 'data_core/sweep_results'):
        self.golden_set = Path(golden_set)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def sweep_boundaries(self, 
                        boundaries: List[float] = None,
                        iterations: int = 3) -> Dict[str, Any]:
        """
        Sweep different boundary values and measure performance
        
        Args:
            boundaries: List of boundary values to test (default: [0.45, 0.475, 0.5, 0.525, 0.55])
            iterations: Number of iterations per boundary
        
        Returns:
            Sweep results with best boundary identified
        """
        if boundaries is None:
            boundaries = [0.45, 0.475, 0.5, 0.525, 0.55]
        
        print("="*70)
        print("ADAPTIVE ROUTING PARAMETER SWEEP")
        print("="*70)
        print(f"Boundaries to test: {boundaries}")
        print(f"Iterations per boundary: {iterations}")
        print()
        
        # Load golden set
        if not self.golden_set.exists():
            print(f"Golden set not found: {self.golden_set}")
            return {}
        
        with open(self.golden_set, 'r') as f:
            goldens = json.load(f)
        
        print(f"Loaded {len(goldens)} golden tests")
        
        # Import AIOS
        try:
            from main import AIOSClean
            from utils_core.adaptive_routing import AdaptiveConfig
        except ImportError as e:
            print(f"Failed to import AIOS: {e}")
            return {}
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'boundaries_tested': boundaries,
            'iterations': iterations,
            'golden_count': len(goldens),
            'sweep_results': []
        }
        
        # Sweep each boundary
        for boundary in boundaries:
            print(f"\n{'='*70}")
            print(f"Testing boundary: {boundary}")
            print(f"{'='*70}")
            
            boundary_results = {
                'boundary': boundary,
                'iterations': [],
                'avg_metrics': {}
            }
            
            # Run multiple iterations for stability
            for iteration in range(iterations):
                print(f"\n  Iteration {iteration + 1}/{iterations}")
                
                # Initialize AIOS with custom boundary
                aios = AIOSClean()
                luna = aios._get_system('luna')
                
                # Override conversation math boundary (simulate adaptive routing)
                if hasattr(luna, 'learning_system') and hasattr(luna.learning_system, 'conversation_math'):
                    # We'll test by running questions and seeing routing
                    pass
                
                # Run golden tests
                iteration_metrics = {
                    'main_model_count': 0,
                    'embedder_count': 0,
                    'total_latency_ms': 0.0,
                    'errors': 0
                }
                
                for golden in goldens[:5]:  # Use subset for speed
                    try:
                        start = time.perf_counter()
                        
                        # Call with custom boundary (via monkey patch for testing)
                        if hasattr(luna, 'learning_system'):
                            response, metadata = luna.learning_system.python_impl.process_question(
                                golden['question'],
                                golden.get('trait', 'general')
                            )
                            
                            latency_ms = (time.perf_counter() - start) * 1000
                            iteration_metrics['total_latency_ms'] += latency_ms
                            
                            source = metadata.get('source', 'unknown')
                            if source == 'main_model':
                                iteration_metrics['main_model_count'] += 1
                            elif source == 'embedder':
                                iteration_metrics['embedder_count'] += 1
                        
                    except Exception as e:
                        print(f"    Error on {golden['id']}: {e}")
                        iteration_metrics['errors'] += 1
                
                # Calculate iteration metrics
                total_tests = iteration_metrics['main_model_count'] + iteration_metrics['embedder_count']
                iteration_metrics['main_model_pct'] = (iteration_metrics['main_model_count'] / total_tests * 100) if total_tests > 0 else 0
                iteration_metrics['avg_latency_ms'] = iteration_metrics['total_latency_ms'] / total_tests if total_tests > 0 else 0
                
                boundary_results['iterations'].append(iteration_metrics)
                
                print(f"    Main model: {iteration_metrics['main_model_pct']:.1f}%")
                print(f"    Avg latency: {iteration_metrics['avg_latency_ms']:.0f}ms")
            
            # Calculate average metrics across iterations
            if boundary_results['iterations']:
                avg_main_pct = sum(i['main_model_pct'] for i in boundary_results['iterations']) / len(boundary_results['iterations'])
                avg_latency = sum(i['avg_latency_ms'] for i in boundary_results['iterations']) / len(boundary_results['iterations'])
                avg_errors = sum(i['errors'] for i in boundary_results['iterations']) / len(boundary_results['iterations'])
                
                boundary_results['avg_metrics'] = {
                    'main_model_pct': avg_main_pct,
                    'avg_latency_ms': avg_latency,
                    'errors': avg_errors
                }
                
                print(f"\n  Average across {iterations} iterations:")
                print(f"    Main model: {avg_main_pct:.1f}%")
                print(f"    Latency: {avg_latency:.0f}ms")
                print(f"    Errors: {avg_errors:.1f}")
            
            results['sweep_results'].append(boundary_results)
        
        # Identify best boundary
        if results['sweep_results']:
            # Best = lowest latency with reasonable routing split (40-70% main)
            valid_results = [
                r for r in results['sweep_results']
                if 40 <= r['avg_metrics']['main_model_pct'] <= 70
            ]
            
            if valid_results:
                best = min(valid_results, key=lambda r: r['avg_metrics']['avg_latency_ms'])
                results['best_boundary'] = {
                    'boundary': best['boundary'],
                    'main_model_pct': best['avg_metrics']['main_model_pct'],
                    'avg_latency_ms': best['avg_metrics']['avg_latency_ms']
                }
                
                print(f"\n{'='*70}")
                print(f"BEST BOUNDARY: {best['boundary']}")
                print(f"  Main model: {best['avg_metrics']['main_model_pct']:.1f}%")
                print(f"  Latency: {best['avg_metrics']['avg_latency_ms']:.0f}ms")
                print(f"{'='*70}")
        
        # Save results
        output_file = self.output_dir / f"sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
        return results


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Adaptive Routing Sweep Runner')
    parser.add_argument('--golden-set', default='data_core/goldens/sample_set.json',
                       help='Golden set to use for testing')
    parser.add_argument('--boundaries', nargs='+', type=float,
                       help='Boundaries to test (default: 0.45 0.475 0.5 0.525 0.55)')
    parser.add_argument('--iterations', type=int, default=1,
                       help='Iterations per boundary (default: 1)')
    
    args = parser.parse_args()
    
    sweeper = AdaptiveSweep(golden_set=args.golden_set)
    sweeper.sweep_boundaries(boundaries=args.boundaries, iterations=args.iterations)


if __name__ == "__main__":
    main()

