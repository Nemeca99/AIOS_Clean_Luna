#!/usr/bin/env python3
"""
Compatibility shim for refactored unicode_safety module
This file redirects old imports to the new location
"""

# Import from new location
from .base.unicode_safety import (
    setup_unicode_safe_output,
    safe_print,
    safe_log
)

# Alias for compatibility
unicode_safe_print = safe_print

__all__ = [
    'setup_unicode_safe_output',
    'unicode_safe_print',
    'safe_print',
    'safe_log'
]

