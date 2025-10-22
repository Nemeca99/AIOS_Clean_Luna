#!/usr/bin/env python3
"""
Core System Base Classes
Shared base functionality for all AIOS core systems to eliminate duplicate code.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import argparse
from datetime import datetime

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils_core.base.unicode_safety import setup_unicode_safe_output
setup_unicode_safe_output()


class CoreSystemBase:
    """Base class for all AIOS core systems to eliminate duplicate code."""
    
    # System emoji mapping for consistent initialization messages
    SYSTEM_EMOJIS = {
        'backup': '🔒',
        'data': '🗄️',
        'dream': '💤',
        'enterprise': '🏢',
        'luna': '🌙',
        'streamlit': '🎨',
        'utils': '🔧',
        'carma': '🧠',
        'support': '🛠️'
    }
    
    def __init__(self, system_name: str, system_dir: str):
        """Initialize base system with common functionality."""
        self.system_name = system_name
        self.system_dir = Path(system_dir)
        self.system_dir.mkdir(exist_ok=True)
        
        # Initialize common directories
        self._ensure_common_directories()
        
        # Print initialization message
        self._print_initialization_message()
    
    def _ensure_common_directories(self):
        """Ensure common directories exist."""
        common_dirs = [
            self.system_dir / "logs",
            self.system_dir / "temp",
            self.system_dir / "cache"
        ]
        
        for directory in common_dirs:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _print_initialization_message(self):
        """Print standardized initialization message."""
        emoji = self.SYSTEM_EMOJIS.get(self.system_name.lower(), '⚙️')
        print(f"{emoji} {self.system_name.title()} Core System Initialized")
        print(f"   Directory: {self.system_dir}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get standardized system information."""
        return {
            "system_name": self.system_name,
            "system_dir": str(self.system_dir),
            "initialized_at": datetime.now().isoformat(),
            "status": "active"
        }
    
    def create_arg_parser(self, description: str) -> argparse.ArgumentParser:
        """Create standardized argument parser."""
        return argparse.ArgumentParser(
            description=f"AIOS {self.system_name.title()} Core System - {description}",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )


class CoreSystemManager:
    """Manager for common core system operations."""
    
    @staticmethod
    def create_directory_structure(base_path: Path, directories: List[str]) -> None:
        """Create standardized directory structure."""
        for directory in directories:
            dir_path = base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_system_emoji(system_name: str) -> str:
        """Get emoji for system name."""
        return CoreSystemBase.SYSTEM_EMOJIS.get(system_name.lower(), '⚙️')
    
    @staticmethod
    def print_system_status(system_name: str, status: str, details: Dict[str, Any] = None):
        """Print standardized system status."""
        emoji = CoreSystemManager.get_system_emoji(system_name)
        print(f"{emoji} {system_name.title()} System: {status}")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")


def create_standard_arg_parser(system_name: str, description: str) -> argparse.ArgumentParser:
    """Create a standardized argument parser for core systems."""
    return argparse.ArgumentParser(
        description=f"AIOS {system_name.title()} Core System - {description}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )


def add_common_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add common arguments to a parser."""
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--debug', '-d', action='store_true', 
                       help='Enable debug mode')
    parser.add_argument('--config', '-c', type=str, 
                       help='Path to configuration file')
    return parser


def print_system_banner(system_name: str, version: str = "1.0.0"):
    """Print standardized system banner."""
    emoji = CoreSystemManager.get_system_emoji(system_name)
    print(f"\n{'='*60}")
    print(f"{emoji} AIOS {system_name.title()} Core System v{version}")
    print(f"{'='*60}")


def get_common_directories() -> List[str]:
    """Get list of common directories that all cores should have."""
    return [
        "logs",
        "temp", 
        "cache",
        "config",
        "data"
    ]


if __name__ == "__main__":
    # Test the core utilities
    print("🔧 Testing Core System Base...")
    
    # Test system base
    test_system = CoreSystemBase("test", "test_core")
    
    # Test system manager
    CoreSystemManager.print_system_status("test", "active", {"files": 0, "status": "ready"})
    
    # Test argument parser
    parser = create_standard_arg_parser("test", "Test system")
    parser = add_common_arguments(parser)
    
    print("✅ Core utilities test completed!")

