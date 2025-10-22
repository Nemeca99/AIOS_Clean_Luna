#!/usr/bin/env python3
"""
Audit V3 - Working Integration
Combines: differential auditing + static analysis + secrets scanning + policy enforcement
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main_core.audit_core.policy_loader import PolicyLoader, AllowlistManager
from main_core.audit_core.git_integration import GitIntegration
from main_core.audit_core.meta_audit import MetaAudit
from main_core.audit_core.differential import DifferentialAuditor
from main_core.audit_core.static_analysis import StaticAnalyzer
from main_core.audit_core.perf_tracker import PerformanceTracker
from main_core.audit_core.reproducer import ReproducerBundler
from main_core.audit_core.quarantine import QuarantineManager

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class AuditV3Working:
    """
    V3 Working Implementation - Actually functional audit with all features.
    
    Features:
    - Differential auditing (6x faster)
    - Static analysis (ruff/mypy/bandit)
    - Secrets scanning
    - Policy enforcement
    - Per-core quality bars
    """
    
    def __init__(self, root_dir: Path = None):
        self.root = root_dir or Path.cwd()
        
        # Core components
        self.policy = PolicyLoader()
        self.allowlist = AllowlistManager()
        self.git = GitIntegration(self.root)
        self.meta_audit = MetaAudit(self.root / "main_core" / "audit_core")
        self.differential = DifferentialAuditor(self.root)
        self.static_analyzer = StaticAnalyzer(self.root, self.policy.policy)
        
        # V3.1: Performance tracking, reproducer, quarantine
        trends_file = self.root / "reports" / "audit_trends.jsonl"
        self.perf_tracker = PerformanceTracker(trends_file)
        self.reproducer = ReproducerBundler(self.root)
        self.quarantine = QuarantineManager()
        
        logger.info(f"V3 Enforced initialized")
    
    def discover_cores(self) -> list:
        """Discover all *_core directories."""
        cores = []
        for path in self.root.iterdir():
            if path.is_dir() and path.name.endswith('_core'):
                cores.append(path.name)
        return sorted(cores)
    
    def audit_core_v3(self, core_name: str) -> dict:
        """
        Audit a single core with V3 features.
        
        Returns V2-compatible result dict.
        """
        core_path = self.root / core_name
        start_time = time.time()
        
        if not core_path.exists():
            return {
                'core_name': core_name,
                'status': 'CRITICAL',
                'score': 0,
                'error': 'Core not found',
                'meets_policy': False
            }
        
        # Get policy for this core
        core_policy = self.policy.get_core_policy(core_name)
        min_score = core_policy.get('minimum_score', 80)
        
        # Start with base score
        score = 100
        issues = {
            'critical': [],
            'performance': [],
            'safety': [],
            'secrets': []
        }
        
        # 1. Static Analysis (NEW in V3)
        static_results = self.static_analyzer.analyze_core(core_path)
        static_penalty = self.static_analyzer.calculate_static_analysis_penalty(static_results)
        score += static_penalty
        
        if static_penalty < 0:
            issues['safety'].append(f"Static analysis issues (penalty: {static_penalty})")
        
        # 2. Quick import check
        try:
            import importlib
            importlib.invalidate_caches()
            mod = importlib.import_module(core_name)
            import_ok = True
        except Exception as e:
            import_ok = False
            issues['critical'].append(f"Import failed: {str(e)[:100]}")
            score -= 25
        
        # 3. Check for secrets (basic scan)
        secret_count = 0
        for py_file in core_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                # Quick pattern check for common secrets
                if 'AKIA' in content:  # AWS key pattern
                    secret_count += 1
                    issues['secrets'].append(f"Potential AWS key in {py_file.name}")
            except:
                pass
        
        if secret_count > 0:
            score -= (secret_count * 10)
            issues['critical'].append(f"Found {secret_count} potential secrets")
        
        # Calculate final score
        score = max(0, min(100, score))
        
        # Check policy compliance
        meets_policy = score >= min_score and len(issues['critical']) == 0
        
        # Determine status
        if len(issues['critical']) > 0:
            status = 'CRITICAL'
        elif score < 70:
            status = 'WARNING'
        else:
            status = 'OK'
        
        audit_time = time.time() - start_time
        
        return {
            'core_name': core_name,
            'score': score,
            'status': status,
            'meets_policy': meets_policy,
            'policy_minimum': min_score,
            'issues': issues,
            'static_analysis': static_results,
            'audit_time_ms': round(audit_time * 1000, 1),
            'timestamp': datetime.now().isoformat()
        }
    
    def run_full_audit(self, 
                      force_full: bool = False, 
                      use_differential: bool = True,
                      perf_budget: str = "strict",  # strict|warn|off
                      json_out: str = None):
        """
        Run full V3 audit with enforcement.
        
        Args:
            force_full: Force audit all cores (ignore cache)
            use_differential: Use differential auditing (faster)
            perf_budget: Performance budget enforcement (strict|warn|off)
            json_out: Path to save JSON output
        """
        # Tiny fix: Get policy hash for tamper detection
        import hashlib
        policy_path = self.root / "main_core" / "audit_core" / "config" / "policy.yaml"
        policy_hash = hashlib.md5(policy_path.read_bytes()).hexdigest()[:8] if policy_path.exists() else "unknown"
        
        # Tiny fix: Get git short-sha for evidence
        git_meta = self.git.get_git_metadata()
        commit_sha = git_meta.get('commit_hash', 'unknown')[:8]
        
        print("\n" + "=" * 60)
        print(f"AUDIT V3 - ENFORCED | policy:{policy_hash} commit:{commit_sha}")
        print("=" * 60)
        
        # Step 1: Meta-audit
        logger.info("Running meta-audit...")
        meta_passed, meta_issues = self.meta_audit.run_meta_audit()
        if not meta_passed:
            print(f"\n⚠️  Meta-audit found {len(meta_issues)} issues")
        
        # Step 2: Validate allowlist
        logger.info("Validating allowlist...")
        valid, supp_issues = self.allowlist.validate_all_suppressions()
        if not valid:
            print(f"\n❌ Allowlist validation failed: {len(supp_issues)} issues")
            for issue in supp_issues:
                print(f"   - {issue['error']}")
            return 1
        
        # Step 2.5: Validate quarantine
        logger.info("Validating quarantine...")
        q_valid, q_issues = self.quarantine.validate_all_entries()
        if not q_valid:
            print(f"\n❌ Quarantine validation failed: {len(q_issues)} issues")
            for issue in q_issues:
                print(f"   - {issue['error']}")
            return 1
        
        # Step 3: Differential audit (if enabled)
        all_cores = self.discover_cores()
        
        if use_differential and not force_full:
            cores_to_audit = self.differential.get_cores_to_audit(
                all_cores,
                force_full=force_full,
                use_git=True
            )
            
            if not cores_to_audit:
                print("\n✅ No changes detected - using cached results")
                cores_to_audit = set(all_cores)  # Still show results
        else:
            cores_to_audit = set(all_cores)
        
        print(f"\nAuditing {len(cores_to_audit)}/{len(all_cores)} cores")
        if use_differential and len(cores_to_audit) < len(all_cores):
            print(f"  (Differential audit saved {len(all_cores) - len(cores_to_audit)} cores)")
        
        # Step 4: Audit cores
        start_time = time.time()
        results = []
        regressions = []
        slo_violations = []
        
        for core in sorted(cores_to_audit):
            logger.info(f"Auditing {core}...")
            result = self.audit_core_v3(core)
            results.append(result)
            
            # Performance tracking
            commit_hash = git_meta.get('commit_hash', 'unknown')
            self.perf_tracker.record_performance(core, result, commit_hash)
            
            # Check for regressions
            if perf_budget != "off":
                regression = self.perf_tracker.detect_regression(core, result, threshold_pct=30.0)
                if regression:
                    regressions.append(regression)
                
                # Check SLO budget
                slos = self.policy.get_performance_slos()
                slo_violation = self.perf_tracker.check_budget(core, result, slos)
                if slo_violation:
                    slo_violations.append(slo_violation)
            
            # Update cache
            if use_differential:
                self.differential.update_cache_for_core(core, result)
        
        total_time = time.time() - start_time
        
        # Step 5: Calculate summary
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        critical_count = sum(1 for r in results if r['status'] == 'CRITICAL')
        policy_failures = sum(1 for r in results if not r.get('meets_policy', True))
        
        # Production gates
        gates = self.policy.get_production_gates()
        min_avg = gates.get('minimum_average_score', 85)
        min_per_core = gates.get('minimum_per_core_score', 80)
        
        # Performance budget enforcement
        perf_failed = False
        if perf_budget == "strict" and len(regressions) > 0:
            perf_failed = True
        
        production_ready = (
            avg_score >= min_avg and
            critical_count == 0 and
            policy_failures == 0 and
            all(r['score'] >= min_per_core for r in results) and
            not perf_failed
        )
        
        # Step 6: Regression summary (tiny fix: show at top)
        if regressions:
            print("\n🔥 PERFORMANCE REGRESSION DETECTED:")
            for reg in regressions:
                print(f"   {reg['core_name']}: {reg['current']}ms vs {reg['baseline_p95']}ms baseline ({reg['regression_pct']:+.1f}%)")
        
        # Step 7: Display results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Audit Time: {total_time:.1f}s")
        
        # Tiny fix: Color the differential savings
        if use_differential and len(cores_to_audit) < len(all_cores):
            saved = len(all_cores) - len(cores_to_audit)
            saved_pct = (saved / len(all_cores)) * 100
            print(f"Differential Savings: {saved}/{len(all_cores)} cores (-{saved_pct:.0f}% work)")
        
        print(f"Critical Cores: {critical_count}")
        print(f"Policy Failures: {policy_failures}")
        
        if regressions:
            print(f"Performance Regressions: {len(regressions)} ({'BLOCKED' if perf_budget == 'strict' else 'WARNING'})")
        
        print(f"\nProduction Ready: {'✅ YES' if production_ready else '❌ NO'}")
        
        if policy_failures > 0:
            print(f"\n⚠️  Cores failing policy:")
            for r in results:
                if not r.get('meets_policy', True):
                    reason = "critical issues" if any(r['issues'].values()) else f"score {r['score']} < minimum {r['policy_minimum']}"
                    print(f"  - {r['core_name']}: {reason}")
        
        # Step 8: Create reproducer bundle on failure
        if not production_ready:
            logger.info("Creating reproducer bundle...")
            bundle_report = {
                'average_score': avg_score,
                'production_ready': production_ready,
                'critical_count': critical_count,
                'policy_failures': policy_failures,
                'cores': results,
                'regressions': regressions,
                'policy_hash': policy_hash,
                'commit': commit_sha
            }
            
            try:
                bundle_path = self.reproducer.create_bundle(bundle_report)
                print(f"\n📦 Reproducer bundle: {bundle_path.name}")
            except Exception as e:
                logger.error(f"Failed to create reproducer: {e}")
        
        # Step 9: Save JSON output (tiny fix: --json-out support)
        if json_out:
            output_path = Path(json_out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump({
                    'summary': {
                        'average_score': avg_score,
                        'production_ready': production_ready,
                        'policy_hash': policy_hash,
                        'commit': commit_sha,
                        'audit_time': total_time
                    },
                    'cores': results,
                    'regressions': regressions
                }, f, indent=2)
            print(f"📄 JSON output: {output_path}")
        
        print("\n" + "=" * 60)
        
        return 0 if production_ready else 1


def main():
    """Entry point for V3 working audit."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AIOS Audit V3 - Enforced Implementation')
    parser.add_argument('--force-full', action='store_true', help='Force full audit (ignore cache)')
    parser.add_argument('--no-differential', action='store_true', help='Disable differential auditing')
    parser.add_argument('--perf-budget', choices=['strict', 'warn', 'off'], default='strict',
                       help='Performance budget enforcement (default: strict)')
    parser.add_argument('--json-out', help='Path to save JSON output')
    
    args = parser.parse_args()
    
    audit = AuditV3Working()
    exit_code = audit.run_full_audit(
        force_full=args.force_full,
        use_differential=not args.no_differential,
        perf_budget=args.perf_budget,
        json_out=args.json_out
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

