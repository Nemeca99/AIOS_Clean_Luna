"""
CARMA Core Module
Cognitive Adaptive Recursive Memory Architecture
"""

from .carma_core import CARMASystem, main
from .core import (
    FractalMyceliumCache,
    CARMAExecutiveBrain,
    CARMAMetaMemory,
    CARMA100PercentPerformance,
    CARMAMyceliumNetwork,
    ConnectionStatus,
    TrafficType,
    UserConnection,
    TrafficEvent,
    ServerBlock,
    CARMAMemoryCompressor,
    CARMAMemoryClusterer,
    CARMAMemoryAnalytics,
)

__all__ = [
    # Main system
    'CARMASystem',
    'main',
    
    # Core components
    'FractalMyceliumCache',
    'CARMAExecutiveBrain',
    'CARMAMetaMemory',
    'CARMA100PercentPerformance',
    'CARMAMyceliumNetwork',
    
    # Network types
    'ConnectionStatus',
    'TrafficType',
    'UserConnection',
    'TrafficEvent',
    'ServerBlock',
    
    # Memory systems
    'CARMAMemoryCompressor',
    'CARMAMemoryClusterer',
    'CARMAMemoryAnalytics',
]

__version__ = '2.0.0'

