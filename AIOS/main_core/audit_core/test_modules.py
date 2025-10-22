#!/usr/bin/env python3
"""
Test all V3 modules to ensure they actually work.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_all_modules():
    """Test that all V3 modules work."""
    print("\n" + "=" * 60)
    print("TESTING V3 MODULES")
    print("=" * 60)
    
    tests_passed = []
    tests_failed = []
    
    # Test 1: Policy Loader
    try:
        from main_core.audit_core.policy_loader import PolicyLoader, AllowlistManager
        p = PolicyLoader()
        gates = p.get_production_gates()
        print(f"✅ PolicyLoader: {gates.get('minimum_average_score')}")
        tests_passed.append("PolicyLoader")
    except Exception as e:
        print(f"❌ PolicyLoader: {e}")
        tests_failed.append("PolicyLoader")
    
    # Test 2: SBOM Scanner
    try:
        from main_core.audit_core.sbom_scanner import SBOMScanner
        from main_core.audit_core.policy_loader import PolicyLoader
        p = PolicyLoader()
        s = SBOMScanner(Path.cwd(), p.policy)
        sbom = s.generate_sbom()
        print(f"✅ SBOMScanner: {sbom.get('package_count', 0)} packages")
        tests_passed.append("SBOMScanner")
    except Exception as e:
        print(f"❌ SBOMScanner: {e}")
        tests_failed.append("SBOMScanner")
    
    # Test 3: Hermetic Runner
    try:
        from main_core.audit_core.hermetic import HermeticRunner
        h = HermeticRunner()
        h.setup_hermetic_environment()
        versions = h.collect_tool_versions()
        print(f"✅ HermeticRunner: Python {versions.get('python')}")
        tests_passed.append("HermeticRunner")
    except Exception as e:
        print(f"❌ HermeticRunner: {e}")
        tests_failed.append("HermeticRunner")
    
    # Test 4: SARIF Generator
    try:
        from main_core.audit_core.sarif_generator import SARIFGenerator
        s = SARIFGenerator(Path.cwd())
        sarif = s.generate_sarif([])
        print(f"✅ SARIFGenerator: version {sarif.get('version')}")
        tests_passed.append("SARIFGenerator")
    except Exception as e:
        print(f"❌ SARIFGenerator: {e}")
        tests_failed.append("SARIFGenerator")
    
    # Test 5: Secret Baseline
    try:
        from main_core.audit_core.secret_baseline import SecretBaselineManager
        s = SecretBaselineManager()
        stats = s.get_baseline_stats()
        print(f"✅ SecretBaseline: {stats['total_baseline_secrets']} baseline secrets")
        tests_passed.append("SecretBaseline")
    except Exception as e:
        print(f"❌ SecretBaseline: {e}")
        tests_failed.append("SecretBaseline")
    
    # Test 6: Performance Tracker
    try:
        from main_core.audit_core.perf_tracker import PerformanceTracker
        p = PerformanceTracker(Path("reports/audit_trends.jsonl"))
        print(f"✅ PerformanceTracker: {len(p.trends)} trend entries")
        tests_passed.append("PerformanceTracker")
    except Exception as e:
        print(f"❌ PerformanceTracker: {e}")
        tests_failed.append("PerformanceTracker")
    
    # Test 7: Reproducer
    try:
        from main_core.audit_core.reproducer import ReproducerBundler
        r = ReproducerBundler(Path.cwd())
        print(f"✅ ReproducerBundler: ready")
        tests_passed.append("ReproducerBundler")
    except Exception as e:
        print(f"❌ ReproducerBundler: {e}")
        tests_failed.append("ReproducerBundler")
    
    # Test 8: Quarantine
    try:
        from main_core.audit_core.quarantine import QuarantineManager
        q = QuarantineManager()
        valid, issues = q.validate_all_entries()
        print(f"✅ QuarantineManager: {len(q.quarantine.get('quarantined_checks', []))} quarantined")
        tests_passed.append("QuarantineManager")
    except Exception as e:
        print(f"❌ QuarantineManager: {e}")
        tests_failed.append("QuarantineManager")
    
    # Test 9: Differential
    try:
        from main_core.audit_core.differential import DifferentialAuditor
        d = DifferentialAuditor(Path.cwd())
        print(f"✅ DifferentialAuditor: {len(d.cache.get('file_hashes', {}))} cached hashes")
        tests_passed.append("DifferentialAuditor")
    except Exception as e:
        print(f"❌ DifferentialAuditor: {e}")
        tests_failed.append("DifferentialAuditor")
    
    # Test 10: Dashboard Generator
    try:
        from main_core.audit_core.dashboard_generator import DashboardGenerator
        d = DashboardGenerator(Path("reports/audit_trends.jsonl"))
        print(f"✅ DashboardGenerator: {len(d.trends)} trend entries")
        tests_passed.append("DashboardGenerator")
    except Exception as e:
        print(f"❌ DashboardGenerator: {e}")
        tests_failed.append("DashboardGenerator")
    
    # Test 11: Plugin ABI
    try:
        from main_core.audit_core.plugin_abi import PluginABIValidator
        v = PluginABIValidator()
        print(f"✅ PluginABIValidator: ABI v{v.current_version}")
        tests_passed.append("PluginABIValidator")
    except Exception as e:
        print(f"❌ PluginABIValidator: {e}")
        tests_failed.append("PluginABIValidator")
    
    # Test 12: CODEOWNERS
    try:
        from main_core.audit_core.codeowners_validator import CodeownersValidator
        c = CodeownersValidator(Path.cwd())
        print(f"✅ CodeownersValidator: {len(c.codeowners_map)} patterns")
        tests_passed.append("CodeownersValidator")
    except Exception as e:
        print(f"❌ CodeownersValidator: {e}")
        tests_failed.append("CodeownersValidator")
    
    # Test 13: Multi-Repo
    try:
        from main_core.audit_core.multi_repo import MultiRepoAuditor
        m = MultiRepoAuditor()
        valid, errors = m.validate_manifest()
        print(f"✅ MultiRepoAuditor: {len(m.get_projects())} projects")
        tests_passed.append("MultiRepoAuditor")
    except Exception as e:
        print(f"❌ MultiRepoAuditor: {e}")
        tests_failed.append("MultiRepoAuditor")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {len(tests_passed)}/{len(tests_passed) + len(tests_failed)} passed")
    
    if tests_failed:
        print(f"\nFailed tests:")
        for test in tests_failed:
            print(f"  - {test}")
        return 1
    
    print("\n✅ All modules functional")
    return 0


if __name__ == "__main__":
    sys.exit(test_all_modules())

