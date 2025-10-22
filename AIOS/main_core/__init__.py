"""
AIOS Main Core - System Orchestration Plugin

This core handles system-level commands like:
- --system (system operations)
- --config-health (configuration validation)
- --whoami (system identity)
- Model management
- Health checks

This is AIOS managing itself as a plugin!
"""

import platform
import sys
from pathlib import Path

# Detect OS and load appropriate implementation
_os_type = platform.system().lower()

# Try to import OS-specific version first
_core_module = None

if _os_type == 'windows':
    try:
        from .main_core_windows import handle_command, AIOSClean
        _core_module = 'windows'
    except ImportError:
        pass

if _core_module is None and _os_type == 'darwin':
    try:
        from .main_core_macos import handle_command, AIOSClean
        _core_module = 'macos'
    except ImportError:
        pass

if _core_module is None and _os_type == 'linux':
    try:
        from .main_core_linux import handle_command, AIOSClean
        _core_module = 'linux'
    except ImportError:
        pass

# Fallback to generic if OS-specific not found
if _core_module is None:
    try:
        from .main_core import handle_command, AIOSClean
        _core_module = 'generic'
    except ImportError:
        # No implementation found - create a minimal one
        def handle_command(args):
            """Minimal fallback if no main_core implementation exists."""
            if '--system' in args or '--config-health' in args or '--whoami' in args:
                print(f"⚠️  System commands not available yet.")
                print(f"   OS: {_os_type}")
                print(f"   Please add main_core_{_os_type}.py to main_core/ folder")
                return True
            return False
        
        class AIOSClean:
            """Minimal placeholder class."""
            pass
        
        _core_module = 'minimal_fallback'

# Define system commands
def get_commands():
    """Declare main_core system commands."""
    return {
        "commands": {
            "--system": {
                "help": "System operations and management",
                "usage": "python main.py --system [options]",
                "examples": [
                    "python main.py --system --config-health",
                    "python main.py --system --luna --whoami"
                ]
            },
            "--config-health": {
                "help": "Check configuration health of all cores",
                "usage": "python main.py --system --config-health",
                "examples": ["python main.py --system --config-health"]
            },
            "--whoami": {
                "help": "Show system identity and model configuration",
                "usage": "python main.py --system --luna --whoami",
                "examples": ["python main.py --system --luna --whoami"]
            },
            "--modchange": {
                "help": "Change model configuration",
                "usage": "python main.py --system --modchange [options]",
                "examples": ["python main.py --system --luna --modchange --main --model-name 'model'"]
            },
            "--show-models": {
                "help": "Show all model configurations",
                "usage": "python main.py --system --show-models",
                "examples": ["python main.py --system --show-models"]
            }
        },
        "description": "Main Core - AIOS System Orchestration (self-hosting!)",
        "version": "1.0.0",
        "author": "AIOS System"
    }

# Export for main.py to use
__all__ = ['handle_command', 'get_commands', 'AIOSClean']

# Let users know which implementation loaded
if __name__ != "__main__":
    # Only show on import, not when run directly
    pass  # Silent loading - no spam

