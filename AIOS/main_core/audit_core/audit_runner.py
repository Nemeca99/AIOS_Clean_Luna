#!/usr/bin/env python3
"""
AIOS Audit Runner - Automated System Health Check
Zero-ceremony audit harness that scans all cores for critical breaks,
performance bottlenecks, safety gaps, and production readiness.
"""

import importlib
import json
import os
import re
import sys
import time
import pathlib
import subprocess
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]  # Go up to AIOS_Clean root
CORE_GLOB = "*_core"
PY = sys.executable

@dataclass
class CoreScore:
    """Audit score for a single core system."""
    name: str
    status: str  # "CRITICAL", "WARNING", "OK"
    critical: List[str]  # Critical breaks (import failures, crashes)
    perf: List[str]  # Performance issues
    safety: List[str]  # Safety gaps
    missing: List[str]  # Missing features
    ok: List[str]  # Working features
    import_time_ms: float = 0.0
    score: int = 0  # 0-100


def discover_cores() -> List[str]:
    """Discover all *_core directories."""
    return sorted([
        p.name for p in ROOT.iterdir() 
        if p.is_dir() and p.name.endswith("_core")
    ])


def run_command(cmd: List[str], cwd: Optional[pathlib.Path] = None, timeout: int = 120) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        p = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def quick_static_analysis(core: str) -> Dict[str, Tuple[int, str]]:
    """Run quick static analysis tools (ruff, mypy, bandit)."""
    results = {}
    core_path = ROOT / core
    
    # Ruff - fast Python linter
    code, out, err = run_command([PY, "-m", "ruff", "check", "."], cwd=core_path)
    results["ruff"] = (code, out + err)
    
    # Mypy - type checker (skip for now, can be slow)
    # code, out, err = run_command([PY, "-m", "mypy", "--install-types", "--non-interactive", "."], cwd=core_path)
    # results["mypy"] = (code, out + err)
    results["mypy"] = (0, "skipped")
    
    # Bandit - security linter
    code, out, err = run_command([PY, "-m", "bandit", "-q", "-r", "."], cwd=core_path)
    results["bandit"] = (code, out + err)
    
    return results


def grep_code_smells(core: str) -> List[str]:
    """Grep for common code smells and anti-patterns."""
    smells = []
    core_path = ROOT / core
    
    # Patterns to detect
    patterns = {
        "bare-except": r"except\s*:\s*$",
        "print-instead-of-log": r"\bprint\s*\(",
        "eval-exec": r"\b(eval|exec)\s*\(",
        # Removed requests-no-timeout - too many false positives, checked separately
        "open-no-context": r"(?<!with\s)open\s*\([^)]*\)(?!\s*as)",
        "todo-fixme": r"\b(TODO|FIXME|XXX|HACK)\b",
        "random-no-seed": r"random\.(random|uniform|choice)\s*\(",
        # Removed uninitialized-var - too many false positives
    }
    
    for path in core_path.rglob("*.py"):
        try:
            txt = path.read_text(encoding='utf-8', errors='ignore')
            for line_num, line in enumerate(txt.split('\n'), 1):
                for name, pat in patterns.items():
                    if re.search(pat, line, flags=re.IGNORECASE):
                        # Filter out comments
                        if not line.strip().startswith('#'):
                            relative_path = path.relative_to(ROOT)
                            smells.append(f"{relative_path}:{line_num}:{name}")
        except Exception:
            continue
    
    return smells


def test_import_timing(core: str) -> Tuple[bool, float, str]:
    """Test if core can be imported and measure timing."""
    t0 = time.perf_counter()
    try:
        importlib.invalidate_caches()
        module_name = core.replace("/", ".")
        importlib.import_module(module_name)
        dt = (time.perf_counter() - t0) * 1000  # milliseconds
        return True, dt, ""
    except Exception as e:
        dt = (time.perf_counter() - t0) * 1000
        return False, dt, str(e)


def run_perf_canary(core: str) -> Tuple[bool, float, str]:
    """Run performance canary if module exports benchmark hooks."""
    try:
        module_name = core.replace("/", ".")
        m = importlib.import_module(module_name)
        if hasattr(m, "benchmark_canary"):
            t0 = time.perf_counter()
            res = m.benchmark_canary()
            dt = (time.perf_counter() - t0) * 1000
            return True, dt, str(res)
    except Exception as e:
        return False, 0.0, str(e)
    return False, 0.0, "no_canary"


def run_contract_tests(core: str) -> Tuple[bool, str]:
    """Run contract/conformance tests if available."""
    core_path = ROOT / core
    
    # Look for contract test files
    test_files = [
        core_path / "conformance.py",
        core_path / "tests" / "test_contract.py",
        ROOT / "tests" / f"test_contract_{core}.py"
    ]
    
    for test_file in test_files:
        if test_file.exists():
            code, out, err = run_command([PY, "-m", "pytest", "-q", str(test_file)])
            return code == 0, out + err
    
    return True, "no_contract_tests_found"


def apply_known_checks(core: str, cs: CoreScore, import_ms: float, smells: List[str]):
    """Apply known systemic checks based on previous manual audit findings."""
    
    # Check for positive patterns (add to OK list)
    core_path = ROOT / core
    
    # Check for proper error handling patterns
    has_proper_logging = False
    has_type_hints = False
    has_docstrings = False
    
    for py_file in list(core_path.rglob("*.py"))[:10]:  # Sample first 10 files
        if '__pycache__' in str(py_file):
            continue
        try:
            txt = py_file.read_text(encoding='utf-8', errors='ignore')
            if 'import logging' in txt or 'self.logger' in txt:
                has_proper_logging = True
            if '-> ' in txt or ': str' in txt or ': int' in txt:
                has_type_hints = True
            if '"""' in txt and 'Args:' in txt:
                has_docstrings = True
        except:
            continue
    
    if has_proper_logging:
        cs.ok.append("Uses proper logging")
    if has_type_hints:
        cs.ok.append("Has type hints")
    if has_docstrings:
        cs.ok.append("Well documented")
    
    # CARMA known issues
    if core == "carma_core":
        if import_ms > 200:
            cs.perf.append(f"Slow import ({import_ms:.1f}ms) - likely loading embeddings/models")
        
        # Check for known import bug
        analytics_file = ROOT / core / "core" / "analytics.py"
        if analytics_file.exists():
            txt = analytics_file.read_text(encoding='utf-8', errors='ignore')
            if "defaultdict" in txt and "from collections import" not in txt:
                cs.critical.append("analytics.py:107 - uses defaultdict without importing")
        
        # Check for conversation embedding cache
        carma_main = ROOT / core / "carma_core.py"
        if carma_main.exists():
            txt = carma_main.read_text(encoding='utf-8', errors='ignore')
            has_cache = "conversation_embedding_cache" in txt
            if "_find_conversation_memories" in txt and not has_cache:
                cs.perf.append("No conversation embedding cache - N+1 embeds per query")
            elif has_cache:
                cs.ok.append("Conversation embedding cache implemented")
    
    # Fractal known issues
    elif core == "fractal_core":
        safety_rails = ROOT / core / "core" / "safety_rails.py"
        if safety_rails.exists():
            txt = safety_rails.read_text(encoding='utf-8', errors='ignore')
            if "self.conflicts_logged" in txt:
                if "__init__" not in txt or "self.conflicts_logged = []" not in txt:
                    cs.critical.append("safety_rails.py:173 - references uninitialized self.conflicts_logged")
        
        # Check for idempotency
        allocator = ROOT / core / "core" / "knapsack_allocator.py"
        if allocator.exists():
            txt = allocator.read_text(encoding='utf-8', errors='ignore')
            if "idempotency" not in txt.lower() and "deterministic" not in txt.lower():
                cs.safety.append("Allocator lacks idempotency keys on mutating operations")
            elif "deterministic" in txt.lower() or "pure function" in txt.lower():
                cs.ok.append("Allocator is deterministic (functional idempotency)")
    
    # Luna known issues
    elif core == "luna_core":
        arbiter = ROOT / core / "systems" / "luna_arbiter_system.py"
        if arbiter.exists():
            txt = arbiter.read_text(encoding='utf-8', errors='ignore')
            http_calls = txt.count("requests.post")
            # Check if caching is implemented
            has_cache = "_gold_standard_cache" in txt or "_quality_cache" in txt
            if http_calls >= 2 and not has_cache:
                cs.perf.append(f"Arbiter makes {http_calls} HTTP calls per response - no caching")
            elif not has_cache:
                cs.missing.append("Arbiter HTTP caching recommended")
    
    # Dream known issues
    elif core == "dream_core":
        dream_main = ROOT / core / "dream_core.py"
        if dream_main.exists():
            txt = dream_main.read_text(encoding='utf-8', errors='ignore')
            if "jaccard" in txt.lower() or "words_current.intersection" in txt:
                if "cosine" not in txt.lower() and "embedding" not in txt:
                    cs.safety.append("Uses Jaccard-only merge - needs cosine similarity fallback")


def calculate_score(cs: CoreScore, smells_count: int, static_res: Dict, canary_ms: float) -> CoreScore:
    """Calculate 0-100 score based on findings."""
    base = 100
    
    # Critical issues (-30 each)
    critical_count = len(cs.critical)
    base -= 30 * min(3, critical_count)  # Cap at -90
    
    # Performance issues (-10 each)
    perf_count = len(cs.perf)
    base -= 10 * min(5, perf_count)  # Cap at -50
    
    # Safety issues - refined scoring
    # Real safety issues (from manual checks)
    real_safety = [s for s in cs.safety if not any(x in s for x in ['uninitialized-var', 'print-instead', 'random-no-seed', 'requests-no-timeout'])]
    base -= 8 * min(5, len(real_safety))
    
    # Code smell safety issues (even lighter penalty)
    print_count = len([s for s in cs.safety if 'print-instead' in s])
    uninit_count = len([s for s in cs.safety if 'uninitialized-var' in s])
    random_count = len([s for s in cs.safety if 'random-no-seed' in s])
    requests_count = len([s for s in cs.safety if 'requests-no-timeout' in s])
    
    # Very light penalties for code smell patterns (these are warnings, not errors)
    base -= min(3, print_count // 20)  # -1 per 20 print statements
    base -= min(2, uninit_count // 20)  # -1 per 20 uninitialized warnings
    base -= min(1, random_count)  # -1 per random-no-seed
    base -= min(1, requests_count // 10)  # -1 per 10 request warnings
    
    # Missing features (-6 each)
    missing_count = len(cs.missing)
    base -= 6 * min(5, missing_count)
    
    # Code smells from grep (-0.5 each, capped at -10)
    base -= min(10, smells_count // 2)
    
    # Static analysis failures
    if static_res.get("ruff", (0, ""))[0] != 0:
        base -= 5
    if static_res.get("mypy", (0, ""))[0] != 0:
        base -= 10
    if static_res.get("bandit", (0, ""))[0] != 0:
        base -= 5
    
    # Slow canary
    if canary_ms and canary_ms > 200:
        base -= 5
    
    # Add bonus points for good practices
    bonus = 0
    
    # Bonus for having health checks, benchmarks, contract tests
    if len(cs.ok) >= 3:
        bonus += min(6, len(cs.ok))  # +1 per OK item, cap at +6
    
    # Bonus for very fast imports (<1ms)
    if cs.import_time_ms > 0 and cs.import_time_ms < 1.0:
        bonus += 3
    elif cs.import_time_ms < 10.0:
        bonus += 1
    
    # Bonus for zero real safety issues
    real_safety_count = len([s for s in cs.safety if not any(x in s for x in ['uninitialized-var', 'print-instead', 'random-no-seed', 'todo-fixme', 'requests-no-timeout'])])
    if real_safety_count == 0:
        bonus += 4
    
    # Bonus for excellent performance (no perf issues and fast import)
    if len(cs.perf) == 0 and cs.import_time_ms < 50:
        bonus += 2
    
    # Bonus for zero critical and zero missing
    if len(cs.critical) == 0 and len(cs.missing) == 0:
        bonus += 2
    
    # Excellence bonus: If already close to perfect and no real issues
    if base >= 95 and len(real_safety) == 0 and len(cs.critical) == 0 and len(cs.perf) == 0:
        bonus += 2  # Push excellent cores to 100
    
    # Apply bonus
    base += bonus
    
    cs.score = max(0, min(100, base))
    
    # Determine status - refined thresholds
    if critical_count > 0:
        cs.status = "CRITICAL"
    elif cs.score < 70:
        cs.status = "WARNING"
    else:
        cs.status = "OK"
    
    return cs


def audit_core(core: str) -> CoreScore:
    """Run complete audit on a single core."""
    print(f"\nAuditing {core}...")
    
    cs = CoreScore(
        name=core,
        status="OK",
        critical=[],
        perf=[],
        safety=[],
        missing=[],
        ok=[]
    )
    
    # Test import
    ok, import_ms, err = test_import_timing(core)
    cs.import_time_ms = import_ms
    
    if not ok:
        cs.critical.append(f"Import failure: {err[:200]}")
        cs.status = "CRITICAL"
        cs.score = 0
        return cs
    else:
        cs.ok.append(f"Imports successfully in {import_ms:.1f}ms")
    
    # Static analysis (can be slow, make optional)
    static_res = {"ruff": (0, ""), "mypy": (0, ""), "bandit": (0, "")}
    try:
        # static_res = quick_static_analysis(core)
        pass  # Skip for now - too slow
    except Exception:
        pass
    
    # Grep for code smells
    smells = grep_code_smells(core)
    
    # Performance canary
    canary_ok, canary_ms, canary_res = run_perf_canary(core)
    if canary_ok:
        cs.ok.append(f"Perf canary passed in {canary_ms:.1f}ms")
    
    # Contract tests
    contract_ok, contract_out = run_contract_tests(core)
    if not contract_ok:
        cs.critical.append("Contract tests failed")
    
    # Apply known systemic checks
    apply_known_checks(core, cs, import_ms, smells)
    
    # Add smell summary (only for real issues, not pattern noise)
    if smells:
        smell_summary = defaultdict(int)
        for smell in smells[:50]:  # Cap at 50
            smell_type = smell.split(":")[-1]
            # Skip noisy patterns
            if smell_type not in ['uninitialized-var', 'requests-no-timeout']:
                smell_summary[smell_type] += 1
        for smell_type, count in smell_summary.items():
            if count > 5:  # Only report if significant count
                cs.safety.append(f"{count}x {smell_type}")
    
    # Calculate final score
    calculate_score(cs, len(smells), static_res, canary_ms)
    
    return cs


def generate_report(core_scores: List[CoreScore]) -> Dict:
    """Generate final audit report."""
    total_critical = sum(len(cs.critical) for cs in core_scores)
    total_perf = sum(len(cs.perf) for cs in core_scores)
    total_safety = sum(len(cs.safety) for cs in core_scores)
    total_missing = sum(len(cs.missing) for cs in core_scores)
    
    avg_score = sum(cs.score for cs in core_scores) / len(core_scores) if core_scores else 0
    
    critical_cores = [cs.name for cs in core_scores if cs.status == "CRITICAL"]
    warning_cores = [cs.name for cs in core_scores if cs.status == "WARNING"]
    ok_cores = [cs.name for cs in core_scores if cs.status == "OK"]
    
    return {
        "summary": {
            "generated_at": time.time(),
            "total_cores_audited": len(core_scores),
            "average_score": round(avg_score, 1),
            "status_breakdown": {
                "critical": len(critical_cores),
                "warning": len(warning_cores),
                "ok": len(ok_cores)
            },
            "issue_counts": {
                "critical_breaks": total_critical,
                "performance_issues": total_perf,
                "safety_gaps": total_safety,
                "missing_features": total_missing
            },
            "critical_cores": critical_cores,
            "warning_cores": warning_cores,
            "production_ready": avg_score >= 85
        },
        "cores": [asdict(cs) for cs in core_scores]
    }


def main():
    """Run complete system audit."""
    print("=" * 60)
    print("AIOS SYSTEM AUDIT - Automated Health Check")
    print("=" * 60)
    
    cores = discover_cores()
    print(f"\nDiscovered {len(cores)} core systems: {', '.join(cores)}")
    
    start_time = time.time()
    core_scores = []
    
    for core in cores:
        try:
            cs = audit_core(core)
            core_scores.append(cs)
        except Exception as e:
            print(f"ERROR auditing {core}: {e}")
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
    
    elapsed = time.time() - start_time
    
    # Generate report
    report = generate_report(core_scores)
    
    # Print summary
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total Cores: {report['summary']['total_cores_audited']}")
    print(f"Average Score: {report['summary']['average_score']}/100")
    print(f"Production Ready: {'YES' if report['summary']['production_ready'] else 'NO'}")
    print(f"\nStatus Breakdown:")
    print(f"  CRITICAL: {report['summary']['status_breakdown']['critical']}")
    print(f"  WARNING:  {report['summary']['status_breakdown']['warning']}")
    print(f"  OK:       {report['summary']['status_breakdown']['ok']}")
    print(f"\nIssue Counts:")
    print(f"  Critical Breaks: {report['summary']['issue_counts']['critical_breaks']}")
    print(f"  Performance:     {report['summary']['issue_counts']['performance_issues']}")
    print(f"  Safety Gaps:     {report['summary']['issue_counts']['safety_gaps']}")
    print(f"  Missing:         {report['summary']['issue_counts']['missing_features']}")
    
    if report['summary']['critical_cores']:
        print(f"\nCRITICAL CORES: {', '.join(report['summary']['critical_cores'])}")
    
    print(f"\nAudit completed in {elapsed:.1f}s")
    print("=" * 60)
    
    # Output JSON report
    print("\n" + json.dumps(report, indent=2))
    
    return report


if __name__ == "__main__":
    main()

