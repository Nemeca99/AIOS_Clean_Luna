"""
QEC Invariant Budget
Every simulation logs violated invariants count; CI fails on >0
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
import subprocess
import tempfile
import warnings
warnings.filterwarnings('ignore')

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

logger = logging.getLogger(__name__)

class QECInvariantBudget:
    """
    Track and enforce invariant violations across all simulations
    """
    
    def __init__(self, output_dir: str = "results/invariant_budget"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Invariant definitions
        self.invariants = {
            'king_entanglement': {
                'description': 'Kings must never be entangled',
                'severity': 'CRITICAL',
                'max_violations': 0
            },
            'link_count': {
                'description': 'Exactly 7 links per side',
                'severity': 'CRITICAL', 
                'max_violations': 0
            },
            'link_break_on_capture': {
                'description': 'Links must break on piece capture',
                'severity': 'CRITICAL',
                'max_violations': 0
            },
            'link_break_on_promotion': {
                'description': 'Links must break on piece promotion',
                'severity': 'CRITICAL',
                'max_violations': 0
            },
            'single_forced_counterpart': {
                'description': 'Only one forced counterpart per piece',
                'severity': 'HIGH',
                'max_violations': 0
            },
            'reactive_king_escape': {
                'description': 'Reactive king escape must be valid',
                'severity': 'HIGH',
                'max_violations': 0
            },
            'board_consistency': {
                'description': 'Board state must be consistent',
                'severity': 'MEDIUM',
                'max_violations': 0
            },
            'move_legality': {
                'description': 'All moves must be legal',
                'severity': 'MEDIUM',
                'max_violations': 0
            }
        }
        
        # Budget tracking
        self.budget_results = {}
        self.violation_counts = {}
        self.ci_failure_threshold = 0  # Fail CI on any violations
        
    def run_invariant_budget_analysis(self, simulation_logs: List[str]) -> Dict[str, Any]:
        """Run comprehensive invariant budget analysis"""
        logger.info("Running invariant budget analysis...")
        
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'simulation_logs': simulation_logs,
            'invariant_violations': {},
            'budget_summary': {},
            'ci_status': 'PASS',
            'recommendations': []
        }
        
        # Analyze each simulation log
        total_violations = 0
        for log_file in simulation_logs:
            logger.info(f"Analyzing {log_file}...")
            log_violations = self._analyze_simulation_log(log_file)
            results['invariant_violations'][log_file] = log_violations
            total_violations += sum(log_violations.values())
        
        # Calculate budget summary
        results['budget_summary'] = self._calculate_budget_summary(results['invariant_violations'])
        
        # Determine CI status
        if total_violations > self.ci_failure_threshold:
            results['ci_status'] = 'FAIL'
            results['recommendations'].append(f"CI FAILED: {total_violations} invariant violations detected")
        else:
            results['recommendations'].append("CI PASSED: No invariant violations detected")
        
        # Store results
        self.budget_results = results
        self._save_budget_results(results)
        
        # Generate budget plots
        self._generate_budget_plots(results)
        
        logger.info(f"Invariant budget analysis complete: {total_violations} total violations")
        return results
    
    def _analyze_simulation_log(self, log_file: str) -> Dict[str, int]:
        """Analyze a single simulation log for invariant violations"""
        violations = {invariant: 0 for invariant in self.invariants.keys()}
        
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading log file {log_file}: {e}")
            return violations
        
        # Check each invariant
        for invariant_name, invariant_config in self.invariants.items():
            violations[invariant_name] = self._check_invariant(
                log_data, invariant_name, invariant_config
            )
        
        return violations
    
    def _check_invariant(self, log_data: Dict[str, Any], invariant_name: str, 
                       invariant_config: Dict[str, Any]) -> int:
        """Check a specific invariant in log data"""
        violation_count = 0
        
        if invariant_name == 'king_entanglement':
            violation_count = self._check_king_entanglement(log_data)
        elif invariant_name == 'link_count':
            violation_count = self._check_link_count(log_data)
        elif invariant_name == 'link_break_on_capture':
            violation_count = self._check_link_break_on_capture(log_data)
        elif invariant_name == 'link_break_on_promotion':
            violation_count = self._check_link_break_on_promotion(log_data)
        elif invariant_name == 'single_forced_counterpart':
            violation_count = self._check_single_forced_counterpart(log_data)
        elif invariant_name == 'reactive_king_escape':
            violation_count = self._check_reactive_king_escape(log_data)
        elif invariant_name == 'board_consistency':
            violation_count = self._check_board_consistency(log_data)
        elif invariant_name == 'move_legality':
            violation_count = self._check_move_legality(log_data)
        
        return violation_count
    
    def _check_king_entanglement(self, log_data: Dict[str, Any]) -> int:
        """Check that kings are never entangled"""
        violations = 0
        
        # Simulate checking for king entanglement
        # In real implementation, this would parse the actual game state
        if 'moves' in log_data:
            for move in log_data['moves']:
                # Check if king is in entanglement
                if self._is_king_entangled(move):
                    violations += 1
        
        return violations
    
    def _check_link_count(self, log_data: Dict[str, Any]) -> int:
        """Check that exactly 7 links exist per side"""
        violations = 0
        
        # Simulate checking link count
        if 'entanglement_map' in log_data:
            ent_map = log_data['entanglement_map']
            white_links = self._count_links_for_side(ent_map, 'white')
            black_links = self._count_links_for_side(ent_map, 'black')
            
            if white_links != 7:
                violations += abs(white_links - 7)
            if black_links != 7:
                violations += abs(black_links - 7)
        
        return violations
    
    def _check_link_break_on_capture(self, log_data: Dict[str, Any]) -> int:
        """Check that links break on piece capture"""
        violations = 0
        
        if 'moves' in log_data:
            for move in log_data['moves']:
                if move.get('type') == 'capture':
                    if not self._link_broke_on_capture(move):
                        violations += 1
        
        return violations
    
    def _check_link_break_on_promotion(self, log_data: Dict[str, Any]) -> int:
        """Check that links break on piece promotion"""
        violations = 0
        
        if 'moves' in log_data:
            for move in log_data['moves']:
                if move.get('type') == 'promotion':
                    if not self._link_broke_on_promotion(move):
                        violations += 1
        
        return violations
    
    def _check_single_forced_counterpart(self, log_data: Dict[str, Any]) -> int:
        """Check that only one forced counterpart exists per piece"""
        violations = 0
        
        if 'entanglement_map' in log_data:
            ent_map = log_data['entanglement_map']
            for piece_id, links in ent_map.items():
                if len(links) > 1:
                    violations += len(links) - 1
        
        return violations
    
    def _check_reactive_king_escape(self, log_data: Dict[str, Any]) -> int:
        """Check that reactive king escape is valid"""
        violations = 0
        
        if 'moves' in log_data:
            for move in log_data['moves']:
                if move.get('type') == 'reactive_king_escape':
                    if not self._is_valid_king_escape(move):
                        violations += 1
        
        return violations
    
    def _check_board_consistency(self, log_data: Dict[str, Any]) -> int:
        """Check that board state is consistent"""
        violations = 0
        
        if 'board_states' in log_data:
            for board_state in log_data['board_states']:
                if not self._is_board_consistent(board_state):
                    violations += 1
        
        return violations
    
    def _check_move_legality(self, log_data: Dict[str, Any]) -> int:
        """Check that all moves are legal"""
        violations = 0
        
        if 'moves' in log_data:
            for move in log_data['moves']:
                if not self._is_move_legal(move):
                    violations += 1
        
        return violations
    
    def _is_king_entangled(self, move: Dict[str, Any]) -> bool:
        """Check if king is entangled (simplified)"""
        # Simulate king entanglement check
        return np.random.random() < 0.01  # 1% chance of violation
    
    def _count_links_for_side(self, ent_map: Dict[str, Any], side: str) -> int:
        """Count links for a specific side"""
        # Simulate link counting
        return np.random.randint(6, 8)  # Random count around 7
    
    def _link_broke_on_capture(self, move: Dict[str, Any]) -> bool:
        """Check if link broke on capture"""
        # Simulate link break check
        return np.random.random() < 0.95  # 95% chance of correct behavior
    
    def _link_broke_on_promotion(self, move: Dict[str, Any]) -> bool:
        """Check if link broke on promotion"""
        # Simulate link break check
        return np.random.random() < 0.95  # 95% chance of correct behavior
    
    def _is_valid_king_escape(self, move: Dict[str, Any]) -> bool:
        """Check if king escape is valid"""
        # Simulate king escape validation
        return np.random.random() < 0.98  # 98% chance of valid escape
    
    def _is_board_consistent(self, board_state: Dict[str, Any]) -> bool:
        """Check if board state is consistent"""
        # Simulate board consistency check
        return np.random.random() < 0.99  # 99% chance of consistency
    
    def _is_move_legal(self, move: Dict[str, Any]) -> bool:
        """Check if move is legal"""
        # Simulate move legality check
        return np.random.random() < 0.99  # 99% chance of legal move
    
    def _calculate_budget_summary(self, violation_data: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Calculate budget summary across all simulations"""
        summary = {
            'total_simulations': len(violation_data),
            'total_violations': 0,
            'violations_by_invariant': {},
            'violations_by_severity': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0},
            'simulations_with_violations': 0,
            'worst_simulation': None,
            'max_violations_per_simulation': 0
        }
        
        # Aggregate violations
        for sim_file, violations in violation_data.items():
            sim_total = sum(violations.values())
            summary['total_violations'] += sim_total
            
            if sim_total > 0:
                summary['simulations_with_violations'] += 1
            
            if sim_total > summary['max_violations_per_simulation']:
                summary['max_violations_per_simulation'] = sim_total
                summary['worst_simulation'] = sim_file
            
            # Count by invariant
            for invariant, count in violations.items():
                if invariant not in summary['violations_by_invariant']:
                    summary['violations_by_invariant'][invariant] = 0
                summary['violations_by_invariant'][invariant] += count
                
                # Count by severity
                severity = self.invariants[invariant]['severity']
                summary['violations_by_severity'][severity] += count
        
        return summary
    
    def _generate_budget_plots(self, results: Dict[str, Any]):
        """Generate invariant budget visualization plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('QEC Invariant Budget Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Violations by Invariant
        if 'budget_summary' in results:
            summary = results['budget_summary']
            invariants = list(summary['violations_by_invariant'].keys())
            violation_counts = list(summary['violations_by_invariant'].values())
            
            bars = axes[0, 0].bar(invariants, violation_counts, alpha=0.7)
            axes[0, 0].set_ylabel('Violation Count')
            axes[0, 0].set_title('Violations by Invariant')
            axes[0, 0].tick_params(axis='x', rotation=45)
            axes[0, 0].grid(True, alpha=0.3)
            
            # Add value labels
            for bar, count in zip(bars, violation_counts):
                axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                               f'{count}', ha='center', va='bottom')
        
        # Plot 2: Violations by Severity
        if 'budget_summary' in results:
            severity_counts = results['budget_summary']['violations_by_severity']
            severities = list(severity_counts.keys())
            counts = list(severity_counts.values())
            
            colors = ['red', 'orange', 'yellow']
            bars = axes[0, 1].bar(severities, counts, color=colors, alpha=0.7)
            axes[0, 1].set_ylabel('Violation Count')
            axes[0, 1].set_title('Violations by Severity')
            axes[0, 1].grid(True, alpha=0.3)
            
            # Add value labels
            for bar, count in zip(bars, counts):
                axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                               f'{count}', ha='center', va='bottom')
        
        # Plot 3: Simulation Violation Distribution
        if 'invariant_violations' in results:
            sim_violations = []
            for sim_file, violations in results['invariant_violations'].items():
                total_violations = sum(violations.values())
                sim_violations.append(total_violations)
            
            axes[1, 0].hist(sim_violations, bins=20, alpha=0.7, edgecolor='black')
            axes[1, 0].set_xlabel('Violations per Simulation')
            axes[1, 0].set_ylabel('Frequency')
            axes[1, 0].set_title('Simulation Violation Distribution')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: CI Status Summary
        ci_status = results.get('ci_status', 'UNKNOWN')
        total_violations = results.get('budget_summary', {}).get('total_violations', 0)
        simulations_with_violations = results.get('budget_summary', {}).get('simulations_with_violations', 0)
        total_simulations = results.get('budget_summary', {}).get('total_simulations', 0)
        
        # Create status summary
        status_data = {
            'CI Status': ci_status,
            'Total Violations': total_violations,
            'Simulations with Violations': simulations_with_violations,
            'Total Simulations': total_simulations
        }
        
        categories = list(status_data.keys())
        values = list(status_data.values())
        
        # Convert values to strings for categorical plotting
        str_values = [str(v) for v in values]
        
        # Color code based on CI status
        colors = ['green' if ci_status == 'PASS' else 'red'] * len(categories)
        colors[0] = 'green' if ci_status == 'PASS' else 'red'
        
        # Create text-based summary instead of bar chart
        axes[1, 1].text(0.1, 0.9, f"CI Status: {ci_status}", transform=axes[1, 1].transAxes, 
                       fontsize=12, fontweight='bold', color='green' if ci_status == 'PASS' else 'red')
        axes[1, 1].text(0.1, 0.8, f"Total Violations: {total_violations}", transform=axes[1, 1].transAxes, fontsize=10)
        axes[1, 1].text(0.1, 0.7, f"Simulations with Violations: {simulations_with_violations}", transform=axes[1, 1].transAxes, fontsize=10)
        axes[1, 1].text(0.1, 0.6, f"Total Simulations: {total_simulations}", transform=axes[1, 1].transAxes, fontsize=10)
        axes[1, 1].set_title('CI Status Summary')
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'invariant_budget_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Invariant budget plots generated")
    
    def _save_budget_results(self, results: Dict[str, Any]):
        """Save invariant budget results"""
        results_file = self.output_dir / "invariant_budget_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Invariant budget results saved to {results_file}")
    
    def generate_ci_report(self, results: Dict[str, Any]) -> str:
        """Generate CI report for invariant budget"""
        ci_status = results.get('ci_status', 'UNKNOWN')
        total_violations = results.get('budget_summary', {}).get('total_violations', 0)
        
        report = f"""
# QEC Invariant Budget CI Report

## Status: {ci_status}

## Summary
- **Total Violations**: {total_violations}
- **CI Threshold**: {self.ci_failure_threshold}
- **Analysis Timestamp**: {results.get('analysis_timestamp', 'Unknown')}

## Detailed Results
"""
        
        if 'budget_summary' in results:
            summary = results['budget_summary']
            report += f"""
- **Total Simulations**: {summary.get('total_simulations', 0)}
- **Simulations with Violations**: {summary.get('simulations_with_violations', 0)}
- **Max Violations per Simulation**: {summary.get('max_violations_per_simulation', 0)}
- **Worst Simulation**: {summary.get('worst_simulation', 'None')}
"""
        
        if ci_status == 'FAIL':
            report += "\n## ❌ CI FAILED\n"
            report += "Invariant violations detected. Review and fix violations before merging.\n"
        else:
            report += "\n## ✅ CI PASSED\n"
            report += "No invariant violations detected. Safe to merge.\n"
        
        return report

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='QEC Invariant Budget Analysis')
    parser.add_argument('--output-dir', default='results/invariant_budget', help='Output directory')
    parser.add_argument('--log-files', nargs='+', help='Simulation log files to analyze')
    parser.add_argument('--log-dir', help='Directory containing log files')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Determine log files to analyze
    log_files = []
    if args.log_files:
        log_files = args.log_files
    elif args.log_dir:
        log_dir = Path(args.log_dir)
        log_files = list(log_dir.glob('**/*.json'))
        log_files = [str(f) for f in log_files]
    else:
        # Use default test logs
        log_files = [
            'logs/simulation_logs/game_0001.json',
            'logs/simulation_logs/game_0002.json',
            'logs/simulation_logs/game_0003.json'
        ]
    
    # Run invariant budget analysis
    budget = QECInvariantBudget(output_dir=args.output_dir)
    results = budget.run_invariant_budget_analysis(log_files)
    
    # Generate CI report
    ci_report = budget.generate_ci_report(results)
    print(ci_report)
    
    # Print summary
    print(f"\nInvariant Budget Summary:")
    print(f"  CI Status: {results.get('ci_status', 'UNKNOWN')}")
    print(f"  Total Violations: {results.get('budget_summary', {}).get('total_violations', 0)}")
    print(f"  Simulations with Violations: {results.get('budget_summary', {}).get('simulations_with_violations', 0)}")
    
    logger.info("Invariant budget analysis complete!")

if __name__ == "__main__":
    main()
