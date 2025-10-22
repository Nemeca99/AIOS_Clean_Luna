#!/usr/bin/env python3
"""
System Initializer - Standardized initialization for all AIOS core systems
Provides consistent initialization patterns and eliminates duplicate code.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils_core.base.unicode_safety import setup_unicode_safe_output
setup_unicode_safe_output()

from utils_core.base.system_base import CoreSystemManager, get_common_directories


class SystemInitializer:
    """Standardized system initialization for all AIOS cores."""
    
    def __init__(self, system_name: str, system_dir: str, custom_directories: List[str] = None):
        """Initialize a core system with standardized setup."""
        self.system_name = system_name
        self.system_dir = Path(system_dir)
        self.custom_directories = custom_directories or []
        
        # Create system directory
        self.system_dir.mkdir(exist_ok=True)
        
        # Create directory structure
        self._create_directory_structure()
        
        # Print initialization message
        self._print_initialization_message()
    
    def _create_directory_structure(self):
        """Create standardized directory structure."""
        # Common directories for all systems
        common_dirs = get_common_directories()
        
        # Add custom directories if provided
        all_directories = common_dirs + self.custom_directories
        
        # Create directories
        CoreSystemManager.create_directory_structure(self.system_dir, all_directories)
        
        print(f"   Created {len(all_directories)} standard directories")
    
    def _print_initialization_message(self):
        """Print standardized initialization message."""
        emoji = CoreSystemManager.get_system_emoji(self.system_name)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{emoji} {self.system_name.title()} Core System Initialized")
        print(f"   Directory: {self.system_dir}")
        print(f"   Timestamp: {timestamp}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get standardized system information."""
        return {
            "system_name": self.system_name,
            "system_dir": str(self.system_dir),
            "initialized_at": datetime.now().isoformat(),
            "directories_created": len(get_common_directories()) + len(self.custom_directories),
            "status": "active"
        }
    
    def create_subdirectory(self, subdir_name: str) -> Path:
        """Create a subdirectory and return its path."""
        subdir_path = self.system_dir / subdir_name
        subdir_path.mkdir(parents=True, exist_ok=True)
        return subdir_path
    
    def get_log_file_path(self, log_name: str = "system.log") -> Path:
        """Get standardized log file path."""
        return self.system_dir / "logs" / log_name
    
    def get_temp_file_path(self, temp_name: str) -> Path:
        """Get standardized temporary file path."""
        return self.system_dir / "temp" / temp_name
    
    def get_cache_file_path(self, cache_name: str) -> Path:
        """Get standardized cache file path."""
        return self.system_dir / "cache" / cache_name


def initialize_core_system(system_name: str, system_dir: str, custom_directories: List[str] = None) -> SystemInitializer:
    """Convenience function to initialize a core system."""
    return SystemInitializer(system_name, system_dir, custom_directories)


def get_system_initialization_template(system_name: str) -> str:
    """Get a template for system initialization code."""
    emoji = CoreSystemManager.get_system_emoji(system_name)
    
    template = f'''#!/usr/bin/env python3
"""
{system_name.upper()} CORE SYSTEM
Auto-generated initialization template using SystemInitializer
"""

import sys
from pathlib import Path

# CRITICAL: Import Unicode safety layer FIRST
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils_core.base.unicode_safety import setup_unicode_safe_output
from utils_core.base.initializer import initialize_core_system

setup_unicode_safe_output()

class {system_name.title()}Core:
    """{system_name.title()} Core System"""
    
    def __init__(self):
        """Initialize {system_name} core system."""
        # Initialize with standard directories
        self.initializer = initialize_core_system(
            "{system_name}",
            "{system_name}_core",
            # Add custom directories here if needed
        )
        
        # Set up system-specific directories
        self._setup_system_directories()
        
        print(f"{emoji} {system_name.title()} Core System Ready")
    
    def _setup_system_directories(self):
        """Set up system-specific directories."""
        # Add system-specific directory creation here
        pass
    
    def get_system_info(self):
        """Get system information."""
        return self.initializer.get_system_info()

if __name__ == "__main__":
    system = {system_name.title()}Core()
    print("System initialized successfully!")
'''
    
    return template


if __name__ == "__main__":
    # Test the system initializer
    print("🔧 Testing System Initializer...")
    
    # Test basic initialization
    test_system = initialize_core_system("test", "test_core", ["custom_dir"])
    
    # Test system info
    info = test_system.get_system_info()
    print(f"System info: {info}")
    
    # Test template generation
    template = get_system_initialization_template("example")
    print("✅ System initializer test completed!")

