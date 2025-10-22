#!/usr/bin/env python3
"""
Bridges Layer - External system integrations
Contains: Rust bridge, PowerShell bridge
"""

from .rust_bridge import (
    RustBridge,
    MultiLanguageCore
)
from .powershell_bridge import PowerShellBridge

__all__ = [
    'RustBridge',
    'MultiLanguageCore',
    'PowerShellBridge'
]

