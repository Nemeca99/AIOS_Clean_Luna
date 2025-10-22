#!/usr/bin/env python3
"""
Audit System V2 - Industrial Strength
Config-driven, parallel, modular architecture
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main_core.audit_core.auditor import Auditor
from main_core.audit_core.reporter import AuditReporter
from main_core.audit_core.git_integration import GitIntegration
from main_core.audit_core.meta_audit import MetaAudit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Psychological hygiene warning
COMPLACENCY_WARNING = """
⚠️  SCORES REPRESENT CURRENT COMPLIANCE, NOT FUTURE IMMUNITY.
   Quality requires continuous vigilance. High scores today don't guarantee safety tomorrow.
   Keep the audit hungry. Keep it mean. Never assume "mission accomplished" is permanent.
"""


class AuditSystemV2:
    """
    Industrial-strength audit system.
    
    Features:
    - Parallel execution
    - Config-driven scoring
    - Modular checks
    - Auto-saved reports
    - Proper logging
    - CI-friendly exit codes
    """
    
    def __init__(self, root_dir: Path = None, enable_warnings: bool = True):
        self.root = root_dir or Path.cwd()
        self.auditor = Auditor(self.root)
        self.reporter = AuditReporter(self.root / "reports")
        self.git_integration = GitIntegration(self.root)
        self.meta_audit = MetaAudit(self.root / "main_core" / "audit_core")
        self.enable_warnings = enable_warnings
        logger.info("Audit System V2 initialized")
    
    def run_full_audit(self, parallel: bool = True, save_report: bool = True, run_meta_audit: bool = True) -> tuple:
        """
        Run complete system audit with git tracking and meta-audit.
        
        Returns:
            (report_dict, exit_code)
        """
        # Run meta-audit first (audit the auditor)
        if run_meta_audit:
            meta_passed, meta_issues = self.meta_audit.run_meta_audit()
            if not meta_passed:
                logger.warning("Meta-audit detected issues in audit system itself!")
                for issue in meta_issues:
                    logger.warning(f"  - {issue}")
        
        logger.info("Starting full system audit...")
        
        # Run audit (parallel by default)
        results = self.auditor.audit_all_cores(parallel=parallel, max_workers=4)
        
        # Generate report
        report = self.reporter.generate_report(results)
        
        # Enrich with git metadata
        report = self.git_integration.enrich_report(report)
        
        # Save to file
        if save_report:
            report_path = self.reporter.save_report(report)
            logger.info(f"Report saved to {report_path}")
            
            # Save trend data
            self.git_integration.save_trend_data(report)
        
        # Print summary
        self.reporter.print_summary(report, verbose=False)
        
        # Print complacency warning if score is high
        if self.enable_warnings and report['summary']['average_score'] > 90:
            print(COMPLACENCY_WARNING)
        
        # Calculate score delta from last commit
        score_delta = self.git_integration.get_score_delta_from_last_commit(
            report['summary']['average_score']
        )
        if score_delta is not None:
            delta_emoji = "📈" if score_delta > 0 else "📉" if score_delta < 0 else "➡️"
            print(f"\n{delta_emoji} Score delta from last commit: {score_delta:+.1f}")
        
        # Determine exit code
        exit_code = 0 if report['summary']['production_ready'] else 1
        
        return report, exit_code
    
    def run_single_core_audit(self, core_name: str) -> tuple:
        """
        Audit a single core.
        
        Returns:
            (core_result, exit_code)
        """
        # Normalize core name
        if not core_name.endswith('_core'):
            core_name = f"{core_name}_core"
        
        logger.info(f"Auditing {core_name}...")
        
        # Run audit
        result = self.auditor.audit_core(core_name)
        
        # Print detail
        self.reporter.print_core_detail(result)
        
        # Exit code based on status
        exit_code = 0 if result.status == 'OK' else 1
        
        return result, exit_code
    
    def check_production_readiness(self, save_report: bool = True) -> tuple:
        """
        Check production readiness.
        
        Returns:
            (report, exit_code)
        """
        # Run full audit
        results = self.auditor.audit_all_cores(parallel=True)
        report = self.reporter.generate_report(results)
        
        # Save report
        if save_report:
            self.reporter.save_report(report)
        
        # Print readiness assessment
        exit_code = self.reporter.print_production_readiness(report)
        
        return report, exit_code
    
    def get_priority_fixes(self, max_items: int = 20, save_report: bool = False) -> tuple:
        """
        Get prioritized fix list.
        
        Returns:
            (report, exit_code)
        """
        # Run audit
        results = self.auditor.audit_all_cores(parallel=True)
        report = self.reporter.generate_report(results)
        
        # Print fixes
        self.reporter.print_priority_fixes(report, max_items=max_items)
        
        # Exit code
        exit_code = 0 if report['summary']['production_ready'] else 1
        
        return report, exit_code


def handle_command(args: List[str]) -> bool:
    """
    Handle audit commands (V2 implementation).
    
    Returns:
        True if command was handled
    """
    if '--audit' not in args:
        return False
    
    # Initialize audit system
    audit = AuditSystemV2()
    exit_code = 0
    
    try:
        # Check for specific core audit
        if '--core' in args:
            try:
                core_idx = args.index('--core') + 1
                core_name = args[core_idx]
                _, exit_code = audit.run_single_core_audit(core_name)
            except IndexError:
                logger.error("--core requires a core name")
                exit_code = 1
        
        # Check for priority fixes
        elif '--fixes' in args:
            _, exit_code = audit.get_priority_fixes()
        
        # Check for production readiness
        elif '--production-ready' in args:
            _, exit_code = audit.check_production_readiness()
        
        # Default: full audit
        else:
            _, exit_code = audit.run_full_audit()
        
    except Exception as e:
        logger.error(f"Audit failed: {e}", exc_info=True)
        exit_code = 1
    
    # Exit with appropriate code for CI
    if '--ci' in args:
        sys.exit(exit_code)
    
    return True


def main():
    """Standalone execution."""
    audit = AuditSystemV2()
    report, exit_code = audit.run_full_audit()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

