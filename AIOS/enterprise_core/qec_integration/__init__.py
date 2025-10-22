"""
QEC → AIOS Integration Package

Borrows battle-tested code from Quantum Entanglement Chess (QEC) project
to enhance AIOS with:
- Invariant budget system (quality control)
- Performance benchmarks (regression detection)
- Schema validation (data integrity)
- Hypothesis testing (research validation)

Author: Travis Miner
"""

__version__ = "1.0.0"
__author__ = "Travis Miner"

# Import key components
INTEGRATION_AVAILABLE = True
__all__ = []

# Try to import each component separately
try:
    from .qec_invariant_budget import QECInvariantBudget as AIOSInvariantBudget
    __all__.append('AIOSInvariantBudget')
except ImportError as e:
    print(f"⚠️ AIOSInvariantBudget not available: {e}")

try:
    from .qec_performance_benchmarks import QECPerformanceBenchmark as AIOSPerformanceBenchmark
    __all__.append('AIOSPerformanceBenchmark')
except ImportError as e:
    print(f"⚠️ AIOSPerformanceBenchmark not available: {e}")

try:
    from .qec_schema_validator import QECSchemaValidator as AIOSSchemaValidator
    __all__.append('AIOSSchemaValidator')
except ImportError as e:
    print(f"⚠️ AIOSSchemaValidator not available: {e}")

try:
    from .aios_hypothesis_tester import AIOSHypothesisTester
    __all__.append('AIOSHypothesisTester')
except ImportError as e:
    print(f"⚠️ AIOSHypothesisTester not available: {e}")
    print(f"   (Check dependencies)")

if len(__all__) == 0:
    INTEGRATION_AVAILABLE = False

# Integration status
print(f"🎯 QEC → AIOS Integration v{__version__}")
if INTEGRATION_AVAILABLE:
    print("   ✅ All components loaded successfully")
else:
    print("   ⚠️ Some components unavailable")

