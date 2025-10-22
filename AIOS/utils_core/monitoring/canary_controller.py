"""
Canary Rollout Controller
Gradually increases treatment bucket percentage based on SLO compliance
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CanaryController:
    """
    Controls gradual rollout of adaptive routing treatment bucket
    Auto-advances on SLO compliance, rolls back on violations
    """
    
    def __init__(self, state_file: str = 'data_core/analytics/canary_state.json'):
        self.state_file = Path(state_file)
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load canary state from disk"""
        if not self.state_file.exists():
            return {
                'current_pct': 10,  # Start with 10% treatment
                'target_pct': 100,
                'step_pct': 10,
                'consecutive_passes': 0,
                'consecutive_failures': 0,
                'last_advance': None,
                'last_rollback': None,
                'history': []
            }
        
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def _save_state(self):
        """Save canary state to disk"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_slos(self, last_report_file: str = 'data_core/goldens/last_report.json') -> Dict[str, Any]:
        """
        Check SLOs from last golden test report
        
        Returns dict with SLO status
        """
        report_path = Path(last_report_file)
        if not report_path.exists():
            return {'pass': False, 'reason': 'No report file'}
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        metrics = report.get('metrics', {})
        pass_rate = metrics.get('pass_rate', 0.0)
        p95_ms = metrics.get('p95_ms', 999999.0)
        
        # Canary SLO thresholds (stricter than production)
        slo_pass_rate = 0.98  # 98% for canary
        slo_p95_ms = 20000.0  # 20s
        
        slo_check = {
            'pass_rate_ok': pass_rate >= slo_pass_rate,
            'latency_ok': p95_ms <= slo_p95_ms,
            'pass': (pass_rate >= slo_pass_rate) and (p95_ms <= slo_p95_ms),
            'metrics': metrics,
            'thresholds': {
                'pass_rate': slo_pass_rate,
                'p95_ms': slo_p95_ms
            }
        }
        
        if not slo_check['pass']:
            reasons = []
            if not slo_check['pass_rate_ok']:
                reasons.append(f"pass_rate {pass_rate:.1%} < {slo_pass_rate:.0%}")
            if not slo_check['latency_ok']:
                reasons.append(f"p95 {p95_ms:.0f}ms > {slo_p95_ms:.0f}ms")
            slo_check['reason'] = '; '.join(reasons)
        else:
            slo_check['reason'] = 'All SLOs passing'
        
        return slo_check
    
    def advance_canary(self, slo_check: Dict[str, Any]) -> Dict[str, str]:
        """
        Advance or rollback canary based on SLO check
        
        Strategy:
        - 3 consecutive passes → advance by step_pct
        - 2 consecutive failures → rollback by step_pct
        - Reset counter on mixed results
        """
        if slo_check['pass']:
            self.state['consecutive_passes'] += 1
            self.state['consecutive_failures'] = 0
            
            # Advance after 3 consecutive passes
            if self.state['consecutive_passes'] >= 3:
                if self.state['current_pct'] < self.state['target_pct']:
                    old_pct = self.state['current_pct']
                    self.state['current_pct'] = min(
                        self.state['current_pct'] + self.state['step_pct'],
                        self.state['target_pct']
                    )
                    self.state['last_advance'] = datetime.now().isoformat()
                    self.state['consecutive_passes'] = 0  # Reset after advance
                    
                    # Record history
                    self.state['history'].append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'advance',
                        'from_pct': old_pct,
                        'to_pct': self.state['current_pct'],
                        'reason': f"3 consecutive SLO passes"
                    })
                    
                    self._save_state()
                    
                    return {
                        'action': 'advanced',
                        'from': old_pct,
                        'to': self.state['current_pct'],
                        'reason': '3 consecutive SLO passes'
                    }
                else:
                    return {
                        'action': 'at_target',
                        'current': self.state['current_pct'],
                        'reason': 'Already at 100%'
                    }
            else:
                return {
                    'action': 'waiting',
                    'passes': self.state['consecutive_passes'],
                    'needed': 3,
                    'reason': f"{self.state['consecutive_passes']}/3 passes"
                }
        
        else:
            # SLO failure
            self.state['consecutive_failures'] += 1
            self.state['consecutive_passes'] = 0
            
            # Rollback after 2 consecutive failures
            if self.state['consecutive_failures'] >= 2:
                if self.state['current_pct'] > 10:  # Don't go below 10%
                    old_pct = self.state['current_pct']
                    self.state['current_pct'] = max(
                        self.state['current_pct'] - self.state['step_pct'],
                        10
                    )
                    self.state['last_rollback'] = datetime.now().isoformat()
                    self.state['consecutive_failures'] = 0  # Reset after rollback
                    
                    # Record history
                    self.state['history'].append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'rollback',
                        'from_pct': old_pct,
                        'to_pct': self.state['current_pct'],
                        'reason': f"2 consecutive SLO failures: {slo_check['reason']}"
                    })
                    
                    self._save_state()
                    
                    return {
                        'action': 'rolled_back',
                        'from': old_pct,
                        'to': self.state['current_pct'],
                        'reason': f"2 consecutive SLO failures: {slo_check['reason']}"
                    }
                else:
                    return {
                        'action': 'at_minimum',
                        'current': self.state['current_pct'],
                        'reason': 'Already at minimum 10%'
                    }
            else:
                return {
                    'action': 'warning',
                    'failures': self.state['consecutive_failures'],
                    'critical_threshold': 2,
                    'reason': f"{self.state['consecutive_failures']}/2 failures - {slo_check['reason']}"
                }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current canary status"""
        return {
            'current_pct': self.state['current_pct'],
            'target_pct': self.state['target_pct'],
            'consecutive_passes': self.state['consecutive_passes'],
            'consecutive_failures': self.state['consecutive_failures'],
            'last_advance': self.state['last_advance'],
            'last_rollback': self.state['last_rollback'],
            'history_length': len(self.state['history'])
        }
    
    def reset_canary(self, start_pct: int = 10):
        """Reset canary to starting percentage"""
        self.state = {
            'current_pct': start_pct,
            'target_pct': 100,
            'step_pct': 10,
            'consecutive_passes': 0,
            'consecutive_failures': 0,
            'last_advance': None,
            'last_rollback': None,
            'history': self.state.get('history', [])  # Preserve history
        }
        self._save_state()


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Canary Rollout Controller')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check SLOs and advance/rollback canary')
    check_parser.add_argument('--report', default='data_core/goldens/last_report.json',
                             help='Last golden test report file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show canary status')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset canary to start')
    reset_parser.add_argument('--start-pct', type=int, default=10,
                             help='Starting percentage (default: 10)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    controller = CanaryController()
    
    if args.command == 'check':
        print("="*70)
        print("CANARY ROLLOUT CHECK")
        print("="*70)
        
        # Check SLOs
        slo_check = controller.check_slos(args.report)
        print(f"\nSLO Status: {'PASS' if slo_check['pass'] else 'FAIL'}")
        print(f"  Pass rate: {slo_check['metrics'].get('pass_rate', 0):.0%} (threshold: {slo_check['thresholds']['pass_rate']:.0%})")
        print(f"  P95 latency: {slo_check['metrics'].get('p95_ms', 0):.0f}ms (threshold: {slo_check['thresholds']['p95_ms']:.0f}ms)")
        print(f"  Reason: {slo_check['reason']}")
        
        # Advance/rollback
        print("\nCanary decision:")
        result = controller.advance_canary(slo_check)
        print(f"  Action: {result['action']}")
        print(f"  Reason: {result['reason']}")
        
        if result['action'] in ['advanced', 'rolled_back']:
            print(f"  Changed: {result['from']}% -> {result['to']}%")
        
        # Show current status
        status = controller.get_status()
        print(f"\nCurrent treatment bucket: {status['current_pct']}%")
        print(f"Consecutive passes: {status['consecutive_passes']}")
        print(f"Consecutive failures: {status['consecutive_failures']}")
        print("="*70)
    
    elif args.command == 'status':
        status = controller.get_status()
        
        print("="*70)
        print("CANARY STATUS")
        print("="*70)
        print(f"Treatment bucket: {status['current_pct']}%")
        print(f"Target: {status['target_pct']}%")
        print(f"Consecutive passes: {status['consecutive_passes']}")
        print(f"Consecutive failures: {status['consecutive_failures']}")
        print(f"Last advance: {status['last_advance'] or 'Never'}")
        print(f"Last rollback: {status['last_rollback'] or 'Never'}")
        print(f"History events: {status['history_length']}")
        print("="*70)
    
    elif args.command == 'reset':
        controller.reset_canary(start_pct=args.start_pct)
        print(f"Canary reset to {args.start_pct}%")


if __name__ == "__main__":
    main()

