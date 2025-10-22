"""
Smoke test for CodeGraph Mapper
Basic sanity checks to verify tool works
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.codegraph_mapper.cgm.runner import run_map, CGMParams


def test_dry_run():
    """Test dry-run mode (no writes)"""
    print("Testing dry-run mode...")
    
    params = CGMParams(
        root="L:\\AIOS\\tools\\codegraph_mapper",
        out_base="L:\\AIOS\\_maps",
        include=["**/*.py"],
        exclude=["**/__pycache__/**", "**/.venv/**"],
        dry_run=True,
        require_approval=False
    )
    
    result = run_map(params)
    
    assert result.ok, f"Dry-run failed: {result.error}"
    assert result.plan_path is not None, "No plan generated"
    assert result.plan_path.exists(), f"Plan file not found: {result.plan_path}"
    
    # Load plan
    with open(result.plan_path) as f:
        plan = json.load(f)
    
    assert 'writes' in plan, "Plan missing 'writes' key"
    assert len(plan['writes']) > 0, "Plan has no writes"
    
    print(f"  ✅ Dry-run OK - Plan generated with {len(plan['writes'])} artifacts")
    print(f"  ✅ Metrics: {result.metrics}")
    
    return True


def test_small_real_run():
    """Test real run on small directory (cgm itself)"""
    print("\nTesting real run on small directory...")
    
    params = CGMParams(
        root="L:\\AIOS\\tools\\codegraph_mapper",
        out_base="L:\\AIOS\\_maps",
        include=["**/*.py"],
        exclude=["**/__pycache__/**"],
        dry_run=False,
        require_approval=False
    )
    
    try:
        result = run_map(params)
    except Exception as e:
        import traceback
        print(f"\n❌ Exception during run_map: {e}")
        traceback.print_exc()
        raise
    
    assert result.ok, f"Real run failed: {result.error}"
    assert len(result.artifacts) > 0, "No artifacts generated"
    assert result.provenance_path is not None, "No provenance generated"
    assert result.provenance_path.exists(), f"Provenance not found: {result.provenance_path}"
    
    # Check key artifacts exist
    run_dir = result.provenance_path.parent
    assert (run_dir / "graph" / "code_graph.json").exists(), "code_graph.json missing"
    assert (run_dir / "reports" / "summary.md").exists(), "summary.md missing"
    assert (run_dir / "reports" / "summary.html").exists(), "summary.html missing"
    
    print(f"  ✅ Real run OK - {len(result.artifacts)} artifacts written")
    print(f"  ✅ Run directory: {run_dir}")
    
    return True


def main():
    """Run smoke tests"""
    print("=" * 60)
    print("CodeGraph Mapper - Smoke Tests")
    print("=" * 60)
    
    try:
        test_dry_run()
        test_small_real_run()
        
        print("\n" + "=" * 60)
        print("✅ All smoke tests PASSED")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

