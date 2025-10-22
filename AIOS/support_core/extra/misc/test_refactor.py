#!/usr/bin/env python3
"""
Quick test to verify the refactored support_core module works correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_core_imports():
    """Test that all core modules can be imported."""
    print("Testing core module imports...")
    
    try:
        from core import (
            AIOSConfig, AIOSConfigError,
            AIOSLogger, AIOSLoggerError,
            AIOSHealthChecker, AIOSHealthError,
            AIOSSecurityValidator,
            CacheOperations, CacheRegistry, CacheBackup,
            SimpleEmbedder, EmbeddingCache, FAISSOperations,
            RecoveryOperations, SemanticReconstruction,
            SystemConfig, FilePaths, SystemMessages
        )
        print("✅ All core imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_support_system():
    """Test that SupportSystem can be instantiated."""
    print("\nTesting SupportSystem initialization...")
    
    try:
        from support_core import SupportSystem
        
        # Create a test instance
        support = SupportSystem(cache_dir="test_cache")
        print("✅ SupportSystem initialized successfully!")
        
        # Test basic functionality
        print("\nTesting basic functionality...")
        status = support.get_system_status()
        print(f"✅ System status retrieved: {list(status.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hybrid_support():
    """Test that HybridSupportCore works."""
    print("\nTesting HybridSupportCore...")
    
    try:
        from hybrid_support_core import HybridSupportCore
        
        # Create instance (this will try Rust, fall back to Python)
        hybrid = HybridSupportCore(cache_dir="test_cache")
        print(f"✅ HybridSupportCore initialized!")
        print(f"   Implementation: {hybrid.current_implementation}")
        
        # Test status
        status = hybrid.get_status()
        print(f"✅ Hybrid status retrieved: {status['core_name']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("Support Core Refactor Verification Tests")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Core Imports", test_core_imports()))
    results.append(("SupportSystem", test_support_system()))
    results.append(("HybridSupportCore", test_hybrid_support()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Refactor successful!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

