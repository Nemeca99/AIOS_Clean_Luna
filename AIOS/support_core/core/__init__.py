#!/usr/bin/env python3
"""
Support Core - Core Modules
Modular components of the support system.
"""

# Configuration
from .config import AIOSConfig, AIOSConfigError, aios_config

# Logging
from .logger import AIOSLogger, AIOSLoggerError

# Health Checking
from .health_checker import AIOSHealthChecker, AIOSHealthError

# Security
from .security import AIOSSecurityValidator

# Cache Operations
from .cache_operations import (
    CacheStatus,
    CacheMetrics,
    CacheOperations,
    CacheRegistry,
    CacheBackup
)

# Embedding Operations
from .embedding_operations import (
    EmbeddingStatus,
    EmbeddingMetrics,
    SimpleEmbedder,
    EmbeddingCache,
    FAISSOperations,
    EmbeddingSimilarity
)

# Recovery Operations
from .recovery_operations import (
    RecoveryStatus,
    RecoveryOperations,
    SemanticReconstruction,
    ProgressiveHealing,
    RecoveryAssessment
)

# System Classes
from .system_classes import (
    SystemConfig,
    FilePaths,
    SystemMessages
)

__all__ = [
    # Configuration
    'AIOSConfig',
    'AIOSConfigError',
    'aios_config',
    
    # Logging
    'AIOSLogger',
    'AIOSLoggerError',
    
    # Health
    'AIOSHealthChecker',
    'AIOSHealthError',
    
    # Security
    'AIOSSecurityValidator',
    
    # Cache
    'CacheStatus',
    'CacheMetrics',
    'CacheOperations',
    'CacheRegistry',
    'CacheBackup',
    
    # Embeddings
    'EmbeddingStatus',
    'EmbeddingMetrics',
    'SimpleEmbedder',
    'EmbeddingCache',
    'FAISSOperations',
    'EmbeddingSimilarity',
    
    # Recovery
    'RecoveryStatus',
    'RecoveryOperations',
    'SemanticReconstruction',
    'ProgressiveHealing',
    'RecoveryAssessment',
    
    # System
    'SystemConfig',
    'FilePaths',
    'SystemMessages',
]

