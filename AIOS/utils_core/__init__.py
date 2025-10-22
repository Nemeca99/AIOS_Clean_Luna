#!/usr/bin/env python3
"""
AIOS Utils Core Module
Unified utility system for AIOS

Main Components:
- Core: Unified utils core system (UtilsCore)
- Base: Foundation layer (unicode safety, system base, initializer)
- Validation: Data validation and standards
- Operations: File, hash, and data operations
- Monitoring: Provenance, cost tracking, adaptive routing
- Resilience: Retry logic, caching, timeout handling
- Bridges: Rust and PowerShell integrations
- Services: Specialized utility services

Links to: F:\AIOS_Clean\main.py
Internal structure: All files reference only utils_core/
"""

# CRITICAL: Import Unicode safety layer FIRST
from .base.unicode_safety import setup_unicode_safe_output
setup_unicode_safe_output()

# Import the unified core
from .core import UtilsCore

# Import base components
from .base import (
    CoreSystemBase,
    CoreSystemManager,
    SystemInitializer,
    initialize_core_system,
    safe_print,
    safe_log
)

# Import validation components
from .validation import (
    AIOSFileStandards,
    AIOSFileValidator,
    AIOSJSONStandards,
    AIOSJSONHandler,
    validate_timestamps,
    PIIRedactor
)

# Import monitoring components
from .monitoring import (
    ProvenanceLogger,
    get_hypothesis_logger,
    CostTracker,
    get_cost_tracker,
    CanaryController,
    AdaptiveRouter,
    get_adaptive_router
)

# Import resilience components
from .resilience import (
    RetryPolicy,
    with_timeout,
    with_retry,
    ResultCache,
    get_result_cache
)

# Import bridges
from .bridges import (
    RustBridge,
    MultiLanguageCore,
    PowerShellBridge
)

# Import services
from .services import (
    DataDeletionService,
    SchemaMigrator,
    get_main_model,
    get_embedder_model,
    get_draft_model
)

__all__ = [
    # Core
    'UtilsCore',
    # Base
    'CoreSystemBase',
    'CoreSystemManager',
    'SystemInitializer',
    'initialize_core_system',
    'safe_print',
    'safe_log',
    # Validation
    'AIOSFileStandards',
    'AIOSFileValidator',
    'AIOSJSONStandards',
    'AIOSJSONHandler',
    'validate_timestamps',
    'PIIRedactor',
    # Monitoring
    'ProvenanceLogger',
    'get_hypothesis_logger',
    'CostTracker',
    'get_cost_tracker',
    'CanaryController',
    'AdaptiveRouter',
    'get_adaptive_router',
    # Resilience
    'RetryPolicy',
    'with_timeout',
    'with_retry',
    'ResultCache',
    'get_result_cache',
    # Bridges
    'RustBridge',
    'MultiLanguageCore',
    'PowerShellBridge',
    # Services
    'DataDeletionService',
    'SchemaMigrator',
    'get_main_model',
    'get_embedder_model',
    'get_draft_model'
]

__version__ = "2.0.0"
__author__ = "AIOS System"
__description__ = "Unified utility core for AIOS - Clean, organized, modular"
