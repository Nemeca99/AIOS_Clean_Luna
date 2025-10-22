#!/usr/bin/env python3
"""
Quick smoke test for evolution loop skeleton.

Tests:
1. Config loads correctly
2. Orchestrator imports
3. Can create generation directory
4. Can run complete cycle (dry-run mode)
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    
    try:
        from infra_core.unsloth_integration import evolution_orchestrator
        print("  ✅ evolution_orchestrator")
    except Exception as e:
        print(f"  ❌ evolution_orchestrator: {e}")
        return False
    
    try:
        from infra_core.unsloth_integration.training import train_micro_gen
        print("  ✅ train_micro_gen")
    except Exception as e:
        print(f"  ❌ train_micro_gen: {e}")
        return False
    
    try:
        from infra_core.unsloth_integration.evals import eval_suite
        print("  ✅ eval_suite")
    except Exception as e:
        print(f"  ❌ eval_suite: {e}")
        return False
    
    try:
        from infra_core.unsloth_integration.fossils import fossilize_generation
        print("  ✅ fossilize_generation")
    except Exception as e:
        print(f"  ❌ fossilize_generation: {e}")
        return False
    
    return True

def test_config():
    """Test that config loads correctly."""
    print("\nTesting config...")
    
    try:
        from infra_core.unsloth_integration.evolution_orchestrator import load_config
        config = load_config()
        
        assert 'budget' in config
        assert 'training' in config
        assert 'evals' in config
        
        print(f"  ✅ Config loaded")
        print(f"     Budget: {config['budget']['max_steps']} steps")
        print(f"     Evals: recall={config['evals']['recall_threshold']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Config failed: {e}")
        return False

def test_directory_creation():
    """Test generation directory creation."""
    print("\nTesting directory creation...")
    
    try:
        from infra_core.unsloth_integration.fossils.fossilize_generation import create_generation_directory
        
        gen_dir = create_generation_directory(999, parent_gen="test")
        
        assert gen_dir.exists()
        assert gen_dir.name.startswith("Luna-G999-")
        
        # Cleanup
        import shutil
        shutil.rmtree(gen_dir)
        
        print(f"  ✅ Directory creation works")
        return True
    except Exception as e:
        print(f"  ❌ Directory creation failed: {e}")
        return False

def test_lineage_exists():
    """Test that lineage.csv exists."""
    print("\nTesting lineage.csv...")
    
    lineage_path = Path("models/lineage.csv")
    
    if lineage_path.exists():
        content = lineage_path.read_text()
        if "gen_id" in content:
            print(f"  ✅ Lineage.csv exists with headers")
            return True
        else:
            print(f"  ❌ Lineage.csv exists but no headers")
            return False
    else:
        print(f"  ❌ Lineage.csv not found")
        return False

def main():
    print("="*60)
    print("EVOLUTION LOOP SKELETON - SMOKE TEST")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config", test_config()))
    results.append(("Directory Creation", test_directory_creation()))
    results.append(("Lineage CSV", test_lineage_exists()))
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Skeleton is operational!")
        print("\nNext step: Run full cycle test")
        print("  python bin/evolve_once.py --reason 'smoke test' --steps 200")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())

