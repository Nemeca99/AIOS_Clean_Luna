#!/usr/bin/env python3
"""
Master Fix Runner
Runs all automated fixes in priority order and tracks score improvement
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).parent


def run_audit():
    """Run audit and return score."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--audit", "--production-ready"],
        capture_output=True,
        text=True,
        cwd=ROOT
    )
    
    # Extract score from output
    for line in result.stdout.split('\n'):
        if "Score:" in line:
            try:
                score_str = line.split("Score:")[1].split("/")[0].strip()
                return float(score_str)
            except Exception as e:
                pass
    return 0.0


def run_fix_script(script_name):
    """Run a fix script and return success status."""
    script_path = SCRIPTS / script_name
    
    if not script_path.exists():
        print(f"Script not found: {script_name}")
        return False
    
    print(f"\nRunning: {script_name}")
    print("-" * 60)
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT
    )
    
    return result.returncode == 0


def main():
    """Run all fixes in priority order."""
    print("=" * 60)
    print("AIOS AUTOMATED FIX RUNNER")
    print("=" * 60)
    
    # Get baseline score
    print("\nGetting baseline score...")
    baseline_score = run_audit()
    print(f"Baseline Score: {baseline_score}/100")
    
    # Fix scripts in priority order
    fix_scripts = [
        "fix_critical_breaks.py",      # Priority 1: Critical breaks
        "fix_carma_caching.py",        # Priority 2: Major performance
        # Add more as they're created
    ]
    
    fixes_applied = 0
    fixes_failed = 0
    
    for script in fix_scripts:
        try:
            if run_fix_script(script):
                fixes_applied += 1
            else:
                fixes_failed += 1
        except Exception as e:
            print(f"Error running {script}: {e}")
            fixes_failed += 1
    
    # Get final score
    print("\n" + "=" * 60)
    print("FINAL AUDIT")
    print("=" * 60)
    
    final_score = run_audit()
    improvement = final_score - baseline_score
    
    print(f"\nBaseline Score: {baseline_score}/100")
    print(f"Final Score:    {final_score}/100")
    print(f"Improvement:    {improvement:+.1f} points")
    print(f"\nFixes Applied:  {fixes_applied}")
    print(f"Fixes Failed:   {fixes_failed}")
    
    if final_score >= 85:
        print("\n✅ SYSTEM IS NOW PRODUCTION READY!")
    elif improvement > 0:
        print(f"\n📈 Progress made! {85 - final_score:.1f} points to production ready")
    else:
        print("\n⚠️ No improvement - manual intervention needed")
    
    return final_score >= 85


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

