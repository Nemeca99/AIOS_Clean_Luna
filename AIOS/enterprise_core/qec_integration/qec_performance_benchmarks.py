"""
QEC Performance Benchmarks
Bench suite for move-gen TPS, eval TPS, game/sec with regression detection
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Tuple, Optional
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse
import logging
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

logger = logging.getLogger(__name__)

class QECPerformanceBenchmark:
    """
    Performance benchmarking for QEC operations
    """
    
    def __init__(self, output_dir: str = "results/benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Benchmark results
        self.benchmark_results = {}
        self.regression_thresholds = {
            'move_gen_tps': 0.1,  # 10% regression threshold
            'eval_tps': 0.1,
            'game_per_sec': 0.1,
            'memory_usage': 0.2,  # 20% memory regression threshold
            'cpu_usage': 0.15     # 15% CPU regression threshold
        }
        
    def benchmark_move_generation(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Benchmark move generation performance"""
        logger.info("Benchmarking move generation...")
        
        times = []
        move_counts = []
        
        for i in range(num_tests):
            start_time = time.perf_counter()
            
            # Simulate move generation (replace with actual QEC move generation)
            moves = self._simulate_move_generation()
            
            end_time = time.perf_counter()
            
            elapsed = end_time - start_time
            times.append(elapsed)
            move_counts.append(len(moves))
        
        # Calculate TPS (moves per second)
        tps_values = [count / time for count, time in zip(move_counts, times)]
        
        results = {
            'benchmark_type': 'move_generation',
            'num_tests': num_tests,
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times),
            'avg_moves': np.mean(move_counts),
            'avg_tps': np.mean(tps_values),
            'std_tps': np.std(tps_values),
            'min_tps': np.min(tps_values),
            'max_tps': np.max(tps_values),
            'raw_times': times,
            'raw_tps': tps_values
        }
        
        self.benchmark_results['move_generation'] = results
        logger.info(f"Move generation: {results['avg_tps']:.2f} TPS (avg)")
        return results
    
    def benchmark_evaluation(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Benchmark evaluation performance"""
        logger.info("Benchmarking evaluation...")
        
        times = []
        eval_counts = []
        
        for i in range(num_tests):
            start_time = time.perf_counter()
            
            # Simulate evaluation (replace with actual QEC evaluation)
            eval_score = self._simulate_evaluation()
            
            end_time = time.perf_counter()
            
            elapsed = end_time - start_time
            times.append(elapsed)
            eval_counts.append(1)  # One evaluation per test
        
        # Calculate TPS (evaluations per second)
        tps_values = [count / time for count, time in zip(eval_counts, times)]
        
        results = {
            'benchmark_type': 'evaluation',
            'num_tests': num_tests,
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times),
            'avg_tps': np.mean(tps_values),
            'std_tps': np.std(tps_values),
            'min_tps': np.min(tps_values),
            'max_tps': np.max(tps_values),
            'raw_times': times,
            'raw_tps': tps_values
        }
        
        self.benchmark_results['evaluation'] = results
        logger.info(f"Evaluation: {results['avg_tps']:.2f} TPS (avg)")
        return results
    
    def benchmark_full_game(self, num_games: int = 100) -> Dict[str, Any]:
        """Benchmark full game performance"""
        logger.info("Benchmarking full game performance...")
        
        game_times = []
        game_plies = []
        memory_usage = []
        cpu_usage = []
        
        for i in range(num_games):
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            start_cpu = psutil.Process().cpu_percent()
            
            # Simulate full game (replace with actual QEC game)
            plies = self._simulate_full_game()
            
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.Process().cpu_percent()
            
            elapsed = end_time - start_time
            game_times.append(elapsed)
            game_plies.append(plies)
            memory_usage.append(end_memory - start_memory)
            cpu_usage.append(end_cpu - start_cpu)
        
        # Calculate games per second
        games_per_sec = [1 / time for time in game_times]
        
        results = {
            'benchmark_type': 'full_game',
            'num_games': num_games,
            'avg_game_time': np.mean(game_times),
            'std_game_time': np.std(game_times),
            'min_game_time': np.min(game_times),
            'max_game_time': np.max(game_times),
            'avg_plies': np.mean(game_plies),
            'avg_games_per_sec': np.mean(games_per_sec),
            'std_games_per_sec': np.std(games_per_sec),
            'avg_memory_usage': np.mean(memory_usage),
            'max_memory_usage': np.max(memory_usage),
            'avg_cpu_usage': np.mean(cpu_usage),
            'max_cpu_usage': np.max(cpu_usage),
            'raw_times': game_times,
            'raw_games_per_sec': games_per_sec,
            'raw_memory': memory_usage,
            'raw_cpu': cpu_usage
        }
        
        self.benchmark_results['full_game'] = results
        logger.info(f"Full game: {results['avg_games_per_sec']:.2f} games/sec (avg)")
        return results
    
    def benchmark_parallel_performance(self, num_workers: int = 4, num_tasks: int = 100) -> Dict[str, Any]:
        """Benchmark parallel performance"""
        logger.info(f"Benchmarking parallel performance with {num_workers} workers...")
        
        # Thread-based parallel execution
        thread_times = []
        thread_results = []
        
        def thread_task():
            return self._simulate_parallel_task()
        
        for i in range(5):  # Run 5 iterations
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(thread_task) for _ in range(num_tasks)]
                results = [future.result() for future in futures]
            
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            thread_times.append(elapsed)
            thread_results.append(results)
        
        # Process-based parallel execution
        process_times = []
        process_results = []
        
        for i in range(5):  # Run 5 iterations
            start_time = time.perf_counter()
            
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(self._simulate_parallel_task) for _ in range(num_tasks)]
                results = [future.result() for future in futures]
            
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            process_times.append(elapsed)
            process_results.append(results)
        
        results = {
            'benchmark_type': 'parallel_performance',
            'num_workers': num_workers,
            'num_tasks': num_tasks,
            'thread_avg_time': np.mean(thread_times),
            'thread_std_time': np.std(thread_times),
            'process_avg_time': np.mean(process_times),
            'process_std_time': np.std(process_times),
            'thread_speedup': num_tasks / np.mean(thread_times),
            'process_speedup': num_tasks / np.mean(process_times),
            'raw_thread_times': thread_times,
            'raw_process_times': process_times
        }
        
        self.benchmark_results['parallel'] = results
        logger.info(f"Parallel performance: {results['thread_speedup']:.2f}x speedup (threads), {results['process_speedup']:.2f}x speedup (processes)")
        return results
    
    def _simulate_move_generation(self) -> List[str]:
        """Simulate move generation (replace with actual QEC implementation)"""
        # Simulate variable move generation time
        num_moves = np.random.randint(10, 50)
        time.sleep(np.random.uniform(0.001, 0.01))  # 1-10ms
        return [f"move_{i}" for i in range(num_moves)]
    
    def _simulate_evaluation(self) -> float:
        """Simulate evaluation (replace with actual QEC implementation)"""
        # Simulate variable evaluation time
        time.sleep(np.random.uniform(0.0001, 0.001))  # 0.1-1ms
        return np.random.normal(0, 100)  # Random evaluation score
    
    def _simulate_full_game(self) -> int:
        """Simulate full game (replace with actual QEC implementation)"""
        # Simulate variable game length
        plies = np.random.randint(50, 200)
        time.sleep(np.random.uniform(0.1, 1.0))  # 100ms-1s
        return plies
    
    def _simulate_parallel_task(self) -> Dict[str, Any]:
        """Simulate parallel task (replace with actual QEC implementation)"""
        # Simulate variable task time
        time.sleep(np.random.uniform(0.01, 0.1))  # 10-100ms
        return {
            'task_id': np.random.randint(0, 1000),
            'result': np.random.random(),
            'timestamp': time.time()
        }
    
    def detect_regressions(self, baseline_file: str = None) -> Dict[str, Any]:
        """Detect performance regressions"""
        logger.info("Detecting performance regressions...")
        
        regressions = {}
        
        if baseline_file and Path(baseline_file).exists():
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)
        else:
            # Use default baseline values
            baseline = {
                'move_generation': {'avg_tps': 1000.0},
                'evaluation': {'avg_tps': 5000.0},
                'full_game': {'avg_games_per_sec': 10.0},
                'parallel': {'thread_speedup': 2.0, 'process_speedup': 3.0}
            }
        
        # Check each benchmark for regressions
        for benchmark_name, current_results in self.benchmark_results.items():
            if benchmark_name in baseline:
                baseline_results = baseline[benchmark_name]
                benchmark_regressions = []
                
                # Check TPS regressions
                if 'avg_tps' in current_results and 'avg_tps' in baseline_results:
                    current_tps = current_results['avg_tps']
                    baseline_tps = baseline_results['avg_tps']
                    regression = (baseline_tps - current_tps) / baseline_tps
                    
                    if regression > self.regression_thresholds.get('move_gen_tps', 0.1):
                        benchmark_regressions.append({
                            'metric': 'avg_tps',
                            'current': current_tps,
                            'baseline': baseline_tps,
                            'regression': regression,
                            'threshold': self.regression_thresholds.get('move_gen_tps', 0.1)
                        })
                
                # Check games per second regressions
                if 'avg_games_per_sec' in current_results and 'avg_games_per_sec' in baseline_results:
                    current_gps = current_results['avg_games_per_sec']
                    baseline_gps = baseline_results['avg_games_per_sec']
                    regression = (baseline_gps - current_gps) / baseline_gps
                    
                    if regression > self.regression_thresholds.get('game_per_sec', 0.1):
                        benchmark_regressions.append({
                            'metric': 'avg_games_per_sec',
                            'current': current_gps,
                            'baseline': baseline_gps,
                            'regression': regression,
                            'threshold': self.regression_thresholds.get('game_per_sec', 0.1)
                        })
                
                # Check speedup regressions
                if 'thread_speedup' in current_results and 'thread_speedup' in baseline_results:
                    current_speedup = current_results['thread_speedup']
                    baseline_speedup = baseline_results['thread_speedup']
                    regression = (baseline_speedup - current_speedup) / baseline_speedup
                    
                    if regression > self.regression_thresholds.get('game_per_sec', 0.1):
                        benchmark_regressions.append({
                            'metric': 'thread_speedup',
                            'current': current_speedup,
                            'baseline': baseline_speedup,
                            'regression': regression,
                            'threshold': self.regression_thresholds.get('game_per_sec', 0.1)
                        })
                
                if benchmark_regressions:
                    regressions[benchmark_name] = benchmark_regressions
        
        # Overall regression status
        total_regressions = sum(len(regressions[benchmark]) for benchmark in regressions)
        regression_status = 'FAIL' if total_regressions > 0 else 'PASS'
        
        results = {
            'regression_status': regression_status,
            'total_regressions': total_regressions,
            'regressions': regressions,
            'thresholds': self.regression_thresholds
        }
        
        logger.info(f"Regression detection: {regression_status} ({total_regressions} regressions found)")
        return results
    
    def generate_benchmark_plots(self):
        """Generate benchmark visualization plots"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('QEC Performance Benchmarks', fontsize=16, fontweight='bold')
        
        # Plot 1: Move Generation TPS
        if 'move_generation' in self.benchmark_results:
            move_results = self.benchmark_results['move_generation']
            axes[0, 0].hist(move_results['raw_tps'], bins=20, alpha=0.7, edgecolor='black')
            axes[0, 0].axvline(move_results['avg_tps'], color='red', linestyle='--', label=f"Avg: {move_results['avg_tps']:.1f}")
            axes[0, 0].set_xlabel('TPS (Moves/Second)')
            axes[0, 0].set_ylabel('Frequency')
            axes[0, 0].set_title('Move Generation Performance')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Evaluation TPS
        if 'evaluation' in self.benchmark_results:
            eval_results = self.benchmark_results['evaluation']
            axes[0, 1].hist(eval_results['raw_tps'], bins=20, alpha=0.7, edgecolor='black')
            axes[0, 1].axvline(eval_results['avg_tps'], color='red', linestyle='--', label=f"Avg: {eval_results['avg_tps']:.1f}")
            axes[0, 1].set_xlabel('TPS (Evaluations/Second)')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].set_title('Evaluation Performance')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Full Game Performance
        if 'full_game' in self.benchmark_results:
            game_results = self.benchmark_results['full_game']
            axes[0, 2].hist(game_results['raw_games_per_sec'], bins=20, alpha=0.7, edgecolor='black')
            axes[0, 2].axvline(game_results['avg_games_per_sec'], color='red', linestyle='--', label=f"Avg: {game_results['avg_games_per_sec']:.2f}")
            axes[0, 2].set_xlabel('Games/Second')
            axes[0, 2].set_ylabel('Frequency')
            axes[0, 2].set_title('Full Game Performance')
            axes[0, 2].legend()
            axes[0, 2].grid(True, alpha=0.3)
        
        # Plot 4: Parallel Performance Comparison
        if 'parallel' in self.benchmark_results:
            parallel_results = self.benchmark_results['parallel']
            categories = ['Thread', 'Process']
            speedups = [parallel_results['thread_speedup'], parallel_results['process_speedup']]
            
            bars = axes[1, 0].bar(categories, speedups, alpha=0.7)
            axes[1, 0].set_ylabel('Speedup Factor')
            axes[1, 0].set_title('Parallel Performance')
            axes[1, 0].grid(True, alpha=0.3)
            
            # Add value labels
            for bar, speedup in zip(bars, speedups):
                axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                               f'{speedup:.1f}x', ha='center', va='bottom')
        
        # Plot 5: Memory Usage
        if 'full_game' in self.benchmark_results:
            game_results = self.benchmark_results['full_game']
            axes[1, 1].hist(game_results['raw_memory'], bins=20, alpha=0.7, edgecolor='black')
            axes[1, 1].axvline(game_results['avg_memory_usage'], color='red', linestyle='--', label=f"Avg: {game_results['avg_memory_usage']:.1f}MB")
            axes[1, 1].set_xlabel('Memory Usage (MB)')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].set_title('Memory Usage per Game')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        # Plot 6: Performance Summary
        benchmark_names = list(self.benchmark_results.keys())
        performance_scores = []
        
        for name in benchmark_names:
            results = self.benchmark_results[name]
            if 'avg_tps' in results:
                performance_scores.append(results['avg_tps'])
            elif 'avg_games_per_sec' in results:
                performance_scores.append(results['avg_games_per_sec'] * 100)  # Scale for comparison
            else:
                performance_scores.append(0)
        
        bars = axes[1, 2].bar(benchmark_names, performance_scores, alpha=0.7)
        axes[1, 2].set_ylabel('Performance Score')
        axes[1, 2].set_title('Performance Summary')
        axes[1, 2].tick_params(axis='x', rotation=45)
        axes[1, 2].grid(True, alpha=0.3)
        
        # Add value labels
        for bar, score in zip(bars, performance_scores):
            axes[1, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{score:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'benchmark_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Benchmark plots generated")
    
    def run_all_benchmarks(self, num_tests: int = 1000, num_games: int = 100) -> Dict[str, Any]:
        """Run all performance benchmarks"""
        logger.info("Running all performance benchmarks...")
        
        # Run individual benchmarks
        self.benchmark_move_generation(num_tests)
        self.benchmark_evaluation(num_tests)
        self.benchmark_full_game(num_games)
        self.benchmark_parallel_performance()
        
        # Detect regressions
        regression_results = self.detect_regressions()
        
        # Generate plots
        self.generate_benchmark_plots()
        
        # Compile summary
        summary = {
            'benchmark_results': self.benchmark_results,
            'regression_analysis': regression_results,
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
                'python_version': sys.version
            }
        }
        
        # Save results
        self._save_benchmark_results(summary)
        
        logger.info("All benchmarks complete!")
        return summary
    
    def _save_benchmark_results(self, results: Dict[str, Any]):
        """Save benchmark results"""
        results_file = self.output_dir / "benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Benchmark results saved to {results_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='QEC Performance Benchmarks')
    parser.add_argument('--output-dir', default='results/benchmarks', help='Output directory')
    parser.add_argument('--num-tests', type=int, default=1000, help='Number of tests for move gen and eval')
    parser.add_argument('--num-games', type=int, default=100, help='Number of games for full game benchmark')
    parser.add_argument('--baseline-file', help='Baseline file for regression detection')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run benchmarks
    benchmark = QECPerformanceBenchmark(output_dir=args.output_dir)
    results = benchmark.run_all_benchmarks(args.num_tests, args.num_games)
    
    # Print summary
    print(f"\nBenchmark Summary:")
    print(f"  Move Generation: {results['benchmark_results']['move_generation']['avg_tps']:.1f} TPS")
    print(f"  Evaluation: {results['benchmark_results']['evaluation']['avg_tps']:.1f} TPS")
    print(f"  Full Game: {results['benchmark_results']['full_game']['avg_games_per_sec']:.2f} games/sec")
    print(f"  Regression Status: {results['regression_analysis']['regression_status']}")
    
    logger.info("Performance benchmarks complete!")

if __name__ == "__main__":
    main()
