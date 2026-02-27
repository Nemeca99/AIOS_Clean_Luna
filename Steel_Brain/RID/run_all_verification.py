#!/usr/bin/env python3
"""
Run all RID verification steps and write a report.

Runs in order:
  1. python -m RID --check
  2. python -m pytest RID/tests/ -v
  3. python RID/verify_accomplishments_doc.py
  4. python -m RID.examples.real_world_example
  5. python RID/verify_external_consistency.py (code vs source specs; requires RID/extracted_text/)

Writes:
  - RID/verification_report.json  (machine-readable: timestamp, Python version, per-step pass/fail, counts)
  - RID/verification_report.txt   (human-readable summary)

Exit code: 0 if all pass, 1 otherwise.

Run from project root (L:\\Steel_Brain):
  python RID/run_all_verification.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Project root = parent of RID
ROOT = Path(__file__).resolve().parent.parent
RID_DIR = ROOT / "RID"


def _run(cmd: list[str], cwd: Path, timeout_s: int = 120) -> tuple[bool, str, str]:
    """Run command; return (success, stdout, stderr)."""
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return r.returncode == 0, (r.stdout or ""), (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:
        return False, "", str(e)


def main() -> int:
    py = sys.executable
    report: dict = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "project_root": str(ROOT),
        "steps": [],
        "all_passed": False,
    }

    # 1. RID --check
    ok, out, err = _run([py, "-m", "RID", "--check"], ROOT)
    report["steps"].append({
        "name": "rid_check",
        "command": "python -m RID --check",
        "passed": ok,
        "stdout": out[-500:] if len(out) > 500 else out,
        "stderr": err[-300:] if len(err) > 300 else err,
    })
    if not ok:
        print("[FAIL] python -m RID --check")
        print(err or out)
    else:
        print("[PASS] python -m RID --check")

    # 2. pytest RID/tests/
    ok, out, err = _run([py, "-m", "pytest", "RID/tests/", "-v", "--tb=short"], ROOT, timeout_s=60)
    report["steps"].append({
        "name": "pytest",
        "command": "python -m pytest RID/tests/ -v",
        "passed": ok,
        "stdout": out[-1500:] if len(out) > 1500 else out,
        "stderr": err[-300:] if len(err) > 300 else err,
    })
    if not ok:
        print("[FAIL] pytest RID/tests/")
        print(err or out[-800:])
    else:
        print("[PASS] pytest RID/tests/")

    # 3. verify_accomplishments_doc.py
    ok, out, err = _run([py, str(RID_DIR / "verify_accomplishments_doc.py")], ROOT)
    report["steps"].append({
        "name": "verify_accomplishments_doc",
        "command": "python RID/verify_accomplishments_doc.py",
        "passed": ok,
        "stdout": out[-800:] if len(out) > 800 else out,
        "stderr": err[-300:] if len(err) > 300 else err,
    })
    if not ok:
        print("[FAIL] verify_accomplishments_doc.py")
        print(err or out)
    else:
        print("[PASS] verify_accomplishments_doc.py")

    # 4. real_world_example
    ok, out, err = _run([py, "-m", "RID.examples.real_world_example"], ROOT, timeout_s=30)
    report["steps"].append({
        "name": "real_world_example",
        "command": "python -m RID.examples.real_world_example",
        "passed": ok,
        "stdout": out[-800:] if len(out) > 800 else out,
        "stderr": err[-300:] if len(err) > 300 else err,
    })
    if not ok:
        print("[FAIL] real_world_example")
        print(err or out[-500:])
    else:
        print("[PASS] real_world_example")

    # 5. verify_external_consistency (code vs source specs; needs extracted_text/)
    ok, out, err = _run([py, str(RID_DIR / "verify_external_consistency.py")], ROOT)
    report["steps"].append({
        "name": "verify_external_consistency",
        "command": "python RID/verify_external_consistency.py",
        "passed": ok,
        "stdout": out[-800:] if len(out) > 800 else out,
        "stderr": err[-300:] if len(err) > 300 else err,
    })
    if not ok:
        print("[FAIL] verify_external_consistency (run 'python -m RID --extract-pdf' first if needed)")
        print(err or out[-500:])
    else:
        print("[PASS] verify_external_consistency")

    report["all_passed"] = all(s["passed"] for s in report["steps"])
    report["summary"] = {
        "total_steps": len(report["steps"]),
        "passed": sum(1 for s in report["steps"] if s["passed"]),
        "failed": sum(1 for s in report["steps"] if not s["passed"]),
    }

    # Write reports
    out_dir = RID_DIR
    json_path = out_dir / "verification_report.json"
    txt_path = out_dir / "verification_report.txt"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("RID verification report\n")
        f.write("======================\n")
        f.write(f"Timestamp (UTC): {report['timestamp_utc']}\n")
        f.write(f"Python: {report['python_version']}\n")
        f.write(f"Project root: {report['project_root']}\n\n")
        f.write(f"Result: {'ALL PASSED' if report['all_passed'] else 'ONE OR MORE FAILED'}\n\n")
        for s in report["steps"]:
            f.write(f"  [{('PASS' if s['passed'] else 'FAIL')}] {s['name']}: {s['command']}\n")
        f.write("\n")
    print()
    print(f"Report written: {json_path}, {txt_path}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
