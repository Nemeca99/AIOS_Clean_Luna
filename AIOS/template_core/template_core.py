#!/usr/bin/env python3
"""
Template Core - Reference Implementation

Copy this file and modify it to create your own AIOS core plugin!
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class TemplateCore:
    """
    Main class for your core functionality.
    
    This is where you put your actual logic.
    Keep it clean and modular!
    """
    
    def __init__(self):
        """Initialize your core."""
        self.name = "template_core"
        self.version = "1.0.0"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration for this core.
        Auto-creates if missing - plug and play!
        """
        config_file = Path(__file__).parent / "config" / "template_config.json"
        
        # Default configuration
        default_config = {
            "enabled": True,
            "debug_mode": False,
            "max_retries": 3,
            "timeout": 30
        }
        
        # Create config if it doesn't exist
        if not config_file.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        # Load existing config
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load config, using defaults: {e}")
            return default_config
    
    def do_something(self, message: str) -> str:
        """
        Your core's main functionality goes here.
        
        Args:
            message: Input message
            
        Returns:
            Response string
        """
        return f"Template Core received: {message}"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Return core health status.
        Used by --ping --health command.
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.config.get("enabled", True),
            "status": "healthy"
        }


# === PLUGIN INTERFACE ===

def get_commands() -> Dict[str, Any]:
    """
    Declare what commands this core supports.
    main.py calls this to auto-discover CLI commands!
    
    Returns:
        Dictionary of commands with their metadata
    """
    return {
        "commands": {
            "--template": {
                "help": "Main template command",
                "usage": "python main.py --template 'your message'",
                "examples": [
                    "python main.py --template 'hello world'",
                    "python main.py --template 'test the system'"
                ]
            },
            "--template-test": {
                "help": "Test the template core",
                "usage": "python main.py --template-test",
                "examples": ["python main.py --template-test"]
            }
        },
        "description": "Template Core - Reference implementation for AIOS plugins",
        "version": "1.0.0",
        "author": "AIOS System"
    }


def handle_command(args: List[str]) -> bool:
    """
    Plugin entry point - called by main.py
    
    This is the REQUIRED function for all cores!
    
    Args:
        args: Command line arguments (as list)
        
    Returns:
        True if this core handled the command
        False if command is not for this core
    """
    
    # Define what commands this core listens for
    # Change these to match your core's purpose!
    my_commands = [
        '--template',      # Main command for this core
        '--template-test', # Sub-command example
    ]
    
    # Check if any of our commands are in the args
    if not any(cmd in args for cmd in my_commands):
        return False  # Not for us - let other cores handle it
    
    # This command is for us! Handle it.
    try:
        core = TemplateCore()
        
        # Parse what specific action to take
        if '--template-test' in args:
            # Test command
            print("✅ Template Core is working!")
            print(f"   Version: {core.version}")
            print(f"   Config: {core.config}")
            
        elif '--template' in args:
            # Main command - get message if provided
            message_idx = args.index('--template') + 1
            if message_idx < len(args):
                message = args[message_idx]
                response = core.do_something(message)
                print(response)
            else:
                print("Usage: python main.py --template 'your message'")
        
        return True  # We handled it!
        
    except Exception as e:
        # Friendly error message - not cryptic stack traces!
        print(f"❌ Template Core error: {e}")
        if '--debug' in args:
            import traceback
            traceback.print_exc()
        return True  # We tried to handle it


# === DIRECT EXECUTION (for testing) ===

if __name__ == "__main__":
    """
    Allow running this core directly for testing.
    Example: python template_core.py --template-test
    """
    result = handle_command(sys.argv[1:])
    if result:
        print("\n✅ Command handled successfully!")
    else:
        print("\n⚠️  Command not recognized by this core.")
        print("Try: python template_core.py --template-test")

