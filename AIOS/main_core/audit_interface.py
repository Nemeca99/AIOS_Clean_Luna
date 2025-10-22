#!/usr/bin/env python3
"""
AIOS Audit Core - Integration wrapper for audit system
Provides AIOS-style interface to the audit runner
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try V2 (industrial strength), fallback to V1
try:
    from main_core.audit_core.audit_v2 import AuditSystemV2, handle_command as handle_command_v2
    AUDIT_V2_AVAILABLE = True
except ImportError as e:
    AUDIT_V2_AVAILABLE = False
    logging.warning(f"Audit V2 not available: {e}, using V1")

# V1 imports (fallback)
from main_core.audit_core.audit_runner import (
    discover_cores,
    audit_core,
    generate_report,
    CoreScore
)


class AuditCore:
    """
    AIOS Audit Core System
    
    Provides automated health checks and production readiness scoring
    for all AIOS core systems.
    """
    
    def __init__(self):
        """Initialize audit core."""
        self.last_report: Optional[Dict] = None
        print("🔍 AIOS Audit Core Initialized")
    
    def audit_all_cores(self, verbose: bool = True) -> Dict:
        """
        Audit all discovered cores and generate comprehensive report.
        
        Args:
            verbose: Print progress during audit
            
        Returns:
            Audit report dictionary
        """
        if verbose:
            print("\n🔍 Starting System-Wide Audit...")
        
        cores = discover_cores()
        if verbose:
            print(f"   Discovered {len(cores)} cores: {', '.join(cores)}")
        
        core_scores = []
        for core in cores:
            if verbose:
                print(f"   Auditing {core}...", end=" ")
            
            try:
                cs = audit_core(core)
                core_scores.append(cs)
                
                if verbose:
                    status_emoji = "✅" if cs.status == "OK" else "⚠️" if cs.status == "WARNING" else "❌"
                    print(f"{status_emoji} {cs.score}/100")
            except Exception as e:
                if verbose:
                    print(f"❌ FAILED: {e}")
                cs = CoreScore(
                    name=core,
                    status="CRITICAL",
                    critical=[f"Audit crashed: {str(e)[:200]}"],
                    perf=[],
                    safety=[],
                    missing=[],
                    ok=[]
                )
                core_scores.append(cs)
        
        report = generate_report(core_scores)
        self.last_report = report
        
        if verbose:
            self._print_summary(report)
        
        return report
    
    def audit_single_core(self, core_name: str, verbose: bool = True) -> CoreScore:
        """
        Audit a single core system.
        
        Args:
            core_name: Name of core to audit (e.g., 'carma_core')
            verbose: Print audit details
            
        Returns:
            CoreScore for the audited core
        """
        if verbose:
            print(f"\n🔍 Auditing {core_name}...")
        
        cs = audit_core(core_name)
        
        if verbose:
            self._print_core_details(cs)
        
        return cs
    
    def get_priority_fixes(self, max_items: int = 10) -> List[Dict]:
        """
        Get prioritized list of issues to fix.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of prioritized fix items
        """
        if not self.last_report:
            self.audit_all_cores(verbose=False)
        
        fixes = []
        
        for core_data in self.last_report['cores']:
            core_name = core_data['name']
            
            # Critical breaks (highest priority)
            for issue in core_data['critical']:
                fixes.append({
                    'priority': 1,
                    'severity': 'CRITICAL',
                    'core': core_name,
                    'issue': issue,
                    'impact': 'System crash or failure'
                })
            
            # Performance issues
            for issue in core_data['perf']:
                fixes.append({
                    'priority': 2,
                    'severity': 'PERFORMANCE',
                    'core': core_name,
                    'issue': issue,
                    'impact': 'Slow response times'
                })
            
            # Safety gaps
            for issue in core_data['safety']:
                fixes.append({
                    'priority': 3,
                    'severity': 'SAFETY',
                    'core': core_name,
                    'issue': issue,
                    'impact': 'Production reliability risk'
                })
        
        # Sort by priority
        fixes.sort(key=lambda x: x['priority'])
        
        return fixes[:max_items]
    
    def check_production_readiness(self) -> Dict:
        """
        Check if system is ready for production deployment.
        
        Returns:
            Production readiness assessment
        """
        if not self.last_report:
            self.audit_all_cores(verbose=False)
        
        summary = self.last_report['summary']
        
        # Production criteria
        avg_score = summary['average_score']
        critical_count = summary['status_breakdown']['critical']
        critical_breaks = summary['issue_counts']['critical_breaks']
        
        is_ready = (
            avg_score >= 85 and
            critical_count == 0 and
            critical_breaks == 0
        )
        
        blockers = []
        if avg_score < 85:
            blockers.append(f"Average score {avg_score}/100 < 85")
        if critical_count > 0:
            blockers.append(f"{critical_count} core(s) in CRITICAL state")
        if critical_breaks > 0:
            blockers.append(f"{critical_breaks} critical break(s) found")
        
        return {
            'ready': is_ready,
            'score': avg_score,
            'blockers': blockers,
            'recommendation': 'DEPLOY' if is_ready else 'FIX BLOCKERS FIRST'
        }
    
    def _print_summary(self, report: Dict):
        """Print audit summary."""
        summary = report['summary']
        
        print("\n" + "=" * 60)
        print("📊 AUDIT SUMMARY")
        print("=" * 60)
        print(f"Average Score: {summary['average_score']}/100")
        print(f"Production Ready: {'✅ YES' if summary['production_ready'] else '❌ NO'}")
        print(f"\nStatus: {summary['status_breakdown']['ok']} OK, "
              f"{summary['status_breakdown']['warning']} WARNING, "
              f"{summary['status_breakdown']['critical']} CRITICAL")
        print(f"\nIssues: {summary['issue_counts']['critical_breaks']} critical, "
              f"{summary['issue_counts']['performance_issues']} performance, "
              f"{summary['issue_counts']['safety_gaps']} safety")
        
        if summary['critical_cores']:
            print(f"\n❌ CRITICAL CORES: {', '.join(summary['critical_cores'])}")
    
    def _print_core_details(self, cs: CoreScore):
        """Print detailed core audit results."""
        status_emoji = "✅" if cs.status == "OK" else "⚠️" if cs.status == "WARNING" else "❌"
        
        print(f"\n{status_emoji} {cs.name}: {cs.score}/100 ({cs.status})")
        print(f"   Import Time: {cs.import_time_ms:.1f}ms")
        
        if cs.critical:
            print(f"\n   ❌ CRITICAL ({len(cs.critical)}):")
            for issue in cs.critical[:5]:
                print(f"      - {issue}")
        
        if cs.perf:
            print(f"\n   ⚡ PERFORMANCE ({len(cs.perf)}):")
            for issue in cs.perf[:5]:
                print(f"      - {issue}")
        
        if cs.safety:
            print(f"\n   🔒 SAFETY ({len(cs.safety)}):")
            for issue in cs.safety[:5]:
                print(f"      - {issue}")
        
        if cs.ok:
            print(f"\n   ✓ WORKING ({len(cs.ok)}):")
            for item in cs.ok[:3]:
                print(f"      - {item}")


def handle_command(args: List[str]) -> bool:
    """
    Handle audit commands from main.py
    
    Args:
        args: Command line arguments
        
    Returns:
        True if command was handled
    """
    if '--audit' not in args:
        return False
    
    # Use V2 if available (parallel, config-driven, industrial strength)
    if AUDIT_V2_AVAILABLE:
        return handle_command_v2(args)
    
    # Fallback to V1
    audit = AuditCore()
    
    # Check for specific core audit
    if '--core' in args:
        try:
            core_idx = args.index('--core') + 1
            core_name = args[core_idx]
            if not core_name.endswith('_core'):
                core_name = f"{core_name}_core"
            
            audit.audit_single_core(core_name)
        except IndexError:
            print("❌ Error: --core requires a core name")
            return True
    
    # Check for priority fixes
    elif '--fixes' in args:
        report = audit.audit_all_cores(verbose=False)
        fixes = audit.get_priority_fixes(max_items=20)
        
        print("\n" + "=" * 60)
        print("🔧 PRIORITY FIXES")
        print("=" * 60)
        
        for i, fix in enumerate(fixes, 1):
            print(f"\n{i}. [{fix['severity']}] {fix['core']}")
            print(f"   {fix['issue']}")
            print(f"   Impact: {fix['impact']}")
    
    # Check for production readiness
    elif '--production-ready' in args:
        report = audit.audit_all_cores(verbose=False)
        readiness = audit.check_production_readiness()
        
        print("\n" + "=" * 60)
        print("🚀 PRODUCTION READINESS CHECK")
        print("=" * 60)
        print(f"Status: {readiness['recommendation']}")
        print(f"Score: {readiness['score']}/100")
        
        if readiness['blockers']:
            print(f"\n❌ BLOCKERS:")
            for blocker in readiness['blockers']:
                print(f"   - {blocker}")
        else:
            print("\n✅ System is production ready!")
    
    # Default: full audit
    else:
        audit.audit_all_cores(verbose=True)
    
    return True


def main():
    """Test the audit core."""
    import sys
    
    audit = AuditCore()
    
    if len(sys.argv) > 1:
        # Handle command line args
        handle_command(sys.argv)
    else:
        # Run full audit
        report = audit.audit_all_cores()
        
        # Show priority fixes
        print("\n" + "=" * 60)
        print("🔧 TOP PRIORITY FIXES")
        print("=" * 60)
        fixes = audit.get_priority_fixes(max_items=5)
        for i, fix in enumerate(fixes, 1):
            print(f"\n{i}. [{fix['severity']}] {fix['core']}")
            print(f"   {fix['issue']}")


if __name__ == "__main__":
    main()

