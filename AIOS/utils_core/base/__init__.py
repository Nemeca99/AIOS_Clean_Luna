#!/usr/bin/env python3
"""
Base Layer - Foundation components for utils_core module
Contains: Unicode safety, system base classes, and initializers
"""

from .unicode_safety import setup_unicode_safe_output, UnicodeSafeTextWrapper, safe_print, safe_log
from .system_base import CoreSystemBase, CoreSystemManager
from .initializer import SystemInitializer, initialize_core_system

__all__ = [
    'setup_unicode_safe_output',
    'UnicodeSafeTextWrapper',
    'safe_print',
    'safe_log',
    'CoreSystemBase',
    'CoreSystemManager',
    'SystemInitializer',
    'initialize_core_system'
]

