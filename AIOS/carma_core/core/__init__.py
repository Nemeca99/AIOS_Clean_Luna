"""
CARMA Core Components
All core CARMA system components

Week 3: Imports FractalCache and MemoryCompressor from fractal_core
CARMA extends with psychological features
"""

# Core fractal components (from fractal_core)
from fractal_core.core import FractalCache, MemoryCompressor

# CARMA extends fractal with psychological features
from .fractal_cache import FractalMyceliumCache

# CARMA-specific components
from .executive_brain import CARMAExecutiveBrain
from .meta_memory import CARMAMetaMemory
from .performance import CARMA100PercentPerformance
from .mycelium_network import (
    CARMAMyceliumNetwork,
    ConnectionStatus,
    TrafficType,
    UserConnection,
    TrafficEvent,
    ServerBlock
)

# For backward compatibility, alias compressor
CARMAMemoryCompressor = MemoryCompressor

from .clusterer import CARMAMemoryClusterer
from .analytics import CARMAMemoryAnalytics

__all__ = [
    'FractalMyceliumCache',
    'CARMAExecutiveBrain',
    'CARMAMetaMemory',
    'CARMA100PercentPerformance',
    'CARMAMyceliumNetwork',
    'ConnectionStatus',
    'TrafficType',
    'UserConnection',
    'TrafficEvent',
    'ServerBlock',
    'CARMAMemoryCompressor',
    'CARMAMemoryClusterer',
    'CARMAMemoryAnalytics',
]

