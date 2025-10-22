#!/usr/bin/env python3
"""
Reporter - Output Formatting and Persistence
Handles console output, JSON reports, CSV exports
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dataclasses import asdict

logger = logging.getLogger(__name__)


class AuditReporter:
    """Handles all audit output and persistence."""
    
    def __init__(self, reports_dir: Path = None):
        self.reports_dir = reports_dir or Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, audit_results: List) -> Dict:
        """Generate comprehensive report from audit results."""
        if not audit_results:
            return {
                'summary': {'error': 'No audit results'},
                'cores': []
            }
        
        # Calculate summary statistics
        total_cores = len(audit_results)
        avg_score = sum(r.score for r in audit_results) / total_cores
        
        status_counts = {
            'critical': len([r for r in audit_results if r.status == 'CRITICAL']),
            'warning': len([r for r in audit_results if r.status == 'WARNING']),
            'ok': len([r for r in audit_results if r.status == 'OK'])
        }
        
        issue_counts = {
            'critical': sum(len(r.critical_issues) for r in audit_results),
            'performance': sum(len(r.performance_issues) for r in audit_results),
            'safety': sum(len(r.safety_issues) for r in audit_results),
            'missing': sum(len(r.missing_features) for r in audit_results)
        }
        
        critical_cores = [r.core_name for r in audit_results if r.status == 'CRITICAL']
        warning_cores = [r.core_name for r in audit_results if r.status == 'WARNING']
        
        return {
            'summary': {
                'generated_at': datetime.now().isoformat(),
                'total_cores': total_cores,
                'average_score': round(avg_score, 1),
                'status_breakdown': status_counts,
                'issue_counts': issue_counts,
                'critical_cores': critical_cores,
                'warning_cores': warning_cores,
                'production_ready': avg_score >= 85 and len(critical_cores) == 0
            },
            'cores': [self._serialize_core_result(r) for r in audit_results]
        }
    
    def _serialize_core_result(self, result) -> Dict:
        """Serialize core result to dict."""
        return {
            'name': result.core_name,
            'score': result.score,
            'status': result.status,
            'critical': result.critical_issues,
            'performance': result.performance_issues,
            'safety': result.safety_issues,
            'missing': result.missing_features,
            'positive': result.positive_findings,
            'import_time_ms': result.import_time_ms
        }
    
    def save_report(self, report: Dict, filename: str = None) -> Path:
        """Save report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_{timestamp}.json"
        
        report_path = self.reports_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_path}")
        return report_path
    
    def print_summary(self, report: Dict, verbose: bool = False):
        """Print console summary."""
        summary = report['summary']
        
        print("\n" + "=" * 60)
        print("AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Cores: {summary['total_cores']}")
        print(f"Average Score: {summary['average_score']}/100")
        print(f"Production Ready: {'YES' if summary['production_ready'] else 'NO'}")
        
        print(f"\nStatus Breakdown:")
        print(f"  CRITICAL: {summary['status_breakdown']['critical']}")
        print(f"  WARNING:  {summary['status_breakdown']['warning']}")
        print(f"  OK:       {summary['status_breakdown']['ok']}")
        
        print(f"\nIssue Counts:")
        print(f"  Critical: {summary['issue_counts']['critical']}")
        print(f"  Performance: {summary['issue_counts']['performance']}")
        print(f"  Safety: {summary['issue_counts']['safety']}")
        print(f"  Missing: {summary['issue_counts']['missing']}")
        
        if summary['critical_cores']:
            print(f"\nCRITICAL CORES: {', '.join(summary['critical_cores'])}")
        
        if verbose:
            print("\n" + "=" * 60)
            print("PER-CORE SCORES")
            print("=" * 60)
            for core_data in sorted(report['cores'], key=lambda x: x['score']):
                status_emoji = self._get_status_emoji(core_data['status'])
                print(f"{status_emoji} {core_data['name']}: {core_data['score']}/100")
    
    def print_core_detail(self, core_result) -> None:
        """Print detailed core audit results."""
        status_emoji = self._get_status_emoji(core_result.status)
        
        print(f"\n{status_emoji} {core_result.core_name}: {core_result.score}/100 ({core_result.status})")
        print(f"   Import Time: {core_result.import_time_ms:.1f}ms")
        
        if core_result.critical_issues:
            print(f"\n   CRITICAL ({len(core_result.critical_issues)}):")
            for issue in core_result.critical_issues[:5]:
                print(f"      - {issue}")
        
        if core_result.performance_issues:
            print(f"\n   PERFORMANCE ({len(core_result.performance_issues)}):")
            for issue in core_result.performance_issues[:5]:
                print(f"      - {issue}")
        
        if core_result.safety_issues:
            print(f"\n   SAFETY ({len(core_result.safety_issues)}):")
            for issue in core_result.safety_issues[:5]:
                print(f"      - {issue}")
        
        if core_result.positive_findings:
            print(f"\n   WORKING ({len(core_result.positive_findings)}):")
            for finding in core_result.positive_findings[:5]:
                print(f"      - {finding}")
    
    def print_production_readiness(self, report: Dict) -> int:
        """
        Print production readiness assessment.
        
        Returns exit code: 0 if ready, 1 if not
        """
        summary = report['summary']
        
        print("\n" + "=" * 60)
        print("PRODUCTION READINESS CHECK")
        print("=" * 60)
        print(f"Status: {'DEPLOY' if summary['production_ready'] else 'FIX BLOCKERS FIRST'}")
        print(f"Score: {summary['average_score']}/100")
        
        if not summary['production_ready']:
            print(f"\nBLOCKERS:")
            if summary['average_score'] < 85:
                print(f"   - Average score {summary['average_score']}/100 < 85")
            if summary['status_breakdown']['critical'] > 0:
                print(f"   - {summary['status_breakdown']['critical']} core(s) in CRITICAL state")
            if summary['issue_counts']['critical'] > 0:
                print(f"   - {summary['issue_counts']['critical']} critical break(s) found")
            return 1
        else:
            print(f"\nSystem is production ready!")
            return 0
    
    def print_priority_fixes(self, report: Dict, max_items: int = 20):
        """Print prioritized fix list."""
        fixes = []
        
        for core_data in report['cores']:
            core_name = core_data['name']
            
            # Critical (priority 1)
            for issue in core_data['critical']:
                fixes.append({
                    'priority': 1,
                    'severity': 'CRITICAL',
                    'core': core_name,
                    'issue': issue
                })
            
            # Performance (priority 2)
            for issue in core_data['performance']:
                fixes.append({
                    'priority': 2,
                    'severity': 'PERFORMANCE',
                    'core': core_name,
                    'issue': issue
                })
            
            # Safety (priority 3)
            for issue in core_data['safety']:
                # Only include real safety issues
                if not any(x in issue for x in ['print-instead', 'uninitialized-var', 'random-no-seed']):
                    fixes.append({
                        'priority': 3,
                        'severity': 'SAFETY',
                        'core': core_name,
                        'issue': issue
                    })
        
        # Sort by priority
        fixes.sort(key=lambda x: x['priority'])
        
        print("\n" + "=" * 60)
        print("PRIORITY FIXES")
        print("=" * 60)
        
        for i, fix in enumerate(fixes[:max_items], 1):
            print(f"\n{i}. [{fix['severity']}] {fix['core']}")
            print(f"   {fix['issue']}")
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        return {
            'CRITICAL': '❌',
            'WARNING': '⚠️',
            'OK': '✅'
        }.get(status, '❓')

