#!/usr/bin/env python3
"""
AIOS CLEAN - CENTRAL ORCHESTRATOR (Linux/Unix)
Modular system architecture with self-contained core systems.

This is the main entry point that:
- Orchestrates all 8 core systems (Backup, CARMA, Data, Dream, Enterprise, Luna, Streamlit, Support, Utils)
- Provides CLI interface with comprehensive commands
- Manages inter-core communication and coordination
- Serves as the central hub for all system operations
- Linux/Unix specific implementations
"""

# CRITICAL: Import os first for environment variables
import os

# CRITICAL: Disable Rich shell integration to fix input() issues
os.environ["RICH_SHELL_INTEGRATION"] = "false"
os.environ["RICH_FORCE_TERMINAL"] = "false"
os.environ["RICH_DISABLE_CONSOLE"] = "true"

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import sys
import argparse
import time
import shutil
import json
import random
import hashlib
import uuid
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from functools import wraps

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import all core systems
from backup_core.hybrid_backup_core import HybridBackupCore as BackupCore
from carma_core.implementations.hybrid_carma import HybridCarmaCore as CARMASystem
from data_core.data_core import DataCore  # Import DataCore directly (no hybrid version)
from dream_core.extra.hybrid_dream_core import HybridDreamCore as DreamCore
from enterprise_core.enterprise_core import EnterpriseCore, PiBasedEncryption, GlobalAPIDistribution, CARMAChainProcessor, EnterpriseBilling, KeyRotationManager, ComplianceManager, AdvancedSecurity
from luna_core.hybrid_luna_core import HybridLunaCore as LunaSystem
from streamlit_core.streamlit_core import StreamlitCore
from support_core.support_core import (
    SystemConfig, FilePaths, SystemMessages, ensure_directories,
    aios_config, aios_logger, aios_health_checker, aios_security_validator
)
from support_core.hybrid_support_core import HybridSupportCore as SupportSystem
# from utils_core.hybrid_utils_core import HybridUtilsCore as UtilsCore  # TODO: doesn't exist, use direct imports

# Import utilities
from utils_core.validation.json_standards import AIOSJSONHandler, AIOSDataType, AIOSJSONStandards, ConversationMessage

# No model configuration needed - each core handles its own

# === ENUMS AND DATA CLASSES ===

class SystemMode(Enum):
    LUNA = "luna"
    CARMA = "carma"
    MEMORY = "memory"
    HEALTH = "health"
    OPTIMIZE = "optimize"
    API = "api"
    TEST = "test"
    CLEANUP = "cleanup"
    INTERACTIVE = "interactive"
    EXPORT = "export"
    INFO = "info"

class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class SystemMetrics:
    """System performance metrics"""
    uptime: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    api_requests: int = 0
    errors: int = 0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

# === LINUX-SPECIFIC UTILITIES ===

def get_linux_environment():
    """Get Linux-specific environment information"""
    return {
        "os": "linux",
        "shell": os.environ.get("SHELL", "/bin/bash"),
        "user": os.environ.get("USER", "luna"),
        "home": os.environ.get("HOME", "/home/luna"),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "venv_active": "VIRTUAL_ENV" in os.environ,
        "venv_path": os.environ.get("VIRTUAL_ENV", ""),
        "is_tty": sys.stdin.isatty(),
        "is_interactive": sys.stdin.isatty() and sys.stdout.isatty()
    }

def check_lm_studio_linux():
    """Check if LM Studio is running on Linux (via network check)"""
    import socket
    try:
        # Check if LM Studio is running on localhost:1234 (default port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 1234))
        sock.close()
        return result == 0
    except:
        return False

def get_network_proxy_config():
    """Get network proxy configuration for Luna's isolated environment"""
    return {
        "proxy_enabled": os.environ.get("LUNA_PROXY_ENABLED", "false").lower() == "true",
        "proxy_host": os.environ.get("LUNA_PROXY_HOST", "127.0.0.1"),
        "proxy_port": int(os.environ.get("LUNA_PROXY_PORT", "8080")),
        "proxy_username": os.environ.get("LUNA_PROXY_USERNAME", ""),
        "proxy_password": os.environ.get("LUNA_PROXY_PASSWORD", ""),
        "allowed_domains": os.environ.get("LUNA_ALLOWED_DOMAINS", "").split(",") if os.environ.get("LUNA_ALLOWED_DOMAINS") else []
    }

def setup_venv_if_needed():
    """Set up Python virtual environment if not already active"""
    env_info = get_linux_environment()
    
    if not env_info["venv_active"]:
        print("⚠️  No virtual environment detected. Setting up...")
        
        # Check if .venv exists
        venv_path = Path(".venv")
        if not venv_path.exists():
            print("Creating Python 3.11 virtual environment...")
            import subprocess
            result = subprocess.run([sys.executable, "-m", "venv", ".venv"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to create venv: {result.stderr}")
                return False
        
        print("✅ Virtual environment ready. Please run: source .venv/bin/activate")
        return False
    else:
        print(f"✅ Virtual environment active: {env_info['venv_path']}")
        return True

# === UNIFIED AIOS CLEAN SYSTEM (Linux) ===

class AIOSCleanLinux:
    """Unified AIOS Clean system for Linux/Unix environments."""
    
    def __init__(self):
        # Initialize unified AIOS systems
        self.aios_config = aios_config
        self.logger = aios_logger
        self.health_checker = aios_health_checker
        self.security_validator = aios_security_validator
        
        # Log system initialization
        self.logger.info("Initializing AIOS Clean System (Linux)...", "AIOS")
        
        # Get Linux environment info
        self.env_info = get_linux_environment()
        self.proxy_config = get_network_proxy_config()
        
        # Ensure directories exist
        ensure_directories()
        
        # Initialize core systems with lazy loading for faster startup
        self._core_systems = {}
        self._initialized_systems = set()
        
        # Only initialize essential systems immediately
        self.logger.info("Initializing essential systems...", "AIOS")
        self._initialize_essential_systems()
        
        # System state
        self.initialized = True
        self.start_time = time.time()
        self.metrics = SystemMetrics()
        
        self.logger.success("AIOS Clean System (Linux) Initialized Successfully", "AIOS")
        self._display_system_status()
    
    def _initialize_essential_systems(self):
        """Initialize only the systems needed for basic operation"""
        # Initialize data system first (needed for logging and basic operations)
        self.logger.info("Initializing Data system...", "AIOS")
        self.data_system = DataCore()
        self._core_systems['data'] = self.data_system
        self._initialized_systems.add('data')
        
        # Initialize support system (needed for basic operations)
        self.logger.info("Initializing Support system...", "AIOS")
        self.support_system = SupportSystem()
        self._core_systems['support'] = self.support_system
        self._initialized_systems.add('support')
    
    def _lazy_load_system(self, system_name: str):
        """Lazy load a system when first accessed"""
        if system_name in self._initialized_systems:
            return self._core_systems.get(system_name)
        
        self.logger.info(f"Lazy loading {system_name} system...", "AIOS")
        
        if system_name == 'backup':
            self.backup_system = BackupCore()
            self._core_systems['backup'] = self.backup_system
        elif system_name == 'carma':
            self.carma_system = CARMASystem()
            self._core_systems['carma'] = self.carma_system
        elif system_name == 'dream':
            self.dream_system = DreamCore()
            self._core_systems['dream'] = self.dream_system
        elif system_name == 'enterprise':
            self.enterprise_system = EnterpriseCore()
            self._core_systems['enterprise'] = self.enterprise_system
        elif system_name == 'luna':
            self.luna_system = LunaSystem()
            self._core_systems['luna'] = self.luna_system
        elif system_name == 'streamlit':
            self.streamlit_system = StreamlitCore()
            self._core_systems['streamlit'] = self.streamlit_system
        elif system_name == 'utils':
            self.utils_system = UtilsCore()
            self._core_systems['utils'] = self.utils_system
        
        self._initialized_systems.add(system_name)
        return self._core_systems.get(system_name)
    
    def _get_system(self, system_name: str):
        """Get a system, loading it if necessary"""
        return self._lazy_load_system(system_name)
    
    def _display_system_status(self):
        """Display current system status using unified logging"""
        try:
            # Display Linux environment info
            self.logger.info(f"Linux Environment: {self.env_info['user']}@{self.env_info['shell']}", "AIOS")
            self.logger.info(f"Python: {self.env_info['python_version']}", "AIOS")
            self.logger.info(f"Virtual Env: {'Active' if self.env_info['venv_active'] else 'Inactive'}", "AIOS")
            self.logger.info(f"Interactive: {'Yes' if self.env_info['is_interactive'] else 'No'}", "AIOS")
            
            # Display proxy configuration
            if self.proxy_config["proxy_enabled"]:
                self.logger.info(f"Proxy: {self.proxy_config['proxy_host']}:{self.proxy_config['proxy_port']}", "AIOS")
            else:
                self.logger.info("Proxy: Disabled (Direct network access)", "AIOS")
            
            # Display status for initialized systems only
            for system_name in self._initialized_systems:
                if system_name == 'backup':
                    backup_info = self.backup_system.get_system_info()
                    self.logger.info(f"Backup: {backup_info['total_backups']} backups", "AIOS")
                elif system_name == 'carma':
                    carma_fragments = self.carma_system.cache.file_registry
                    if hasattr(carma_fragments, '__len__'):
                        self.logger.info(f"CARMA: {len(carma_fragments)} fragments", "AIOS")
                    else:
                        self.logger.info(f"CARMA: {carma_fragments} fragments", "AIOS")
                elif system_name == 'data':
                    data_overview = self.data_system.get_system_overview()
                    total_data_files = (data_overview['fractal_cache']['total_files'] + 
                                      data_overview['arbiter_cache']['total_files'])
                    
                    # Add conversations count if available (Python vs Rust implementation difference)
                    if 'conversations' in data_overview and 'total_conversations' in data_overview['conversations']:
                        total_data_files += data_overview['conversations']['total_conversations']
                    
                    self.logger.info(f"Data: {total_data_files} files", "AIOS")
                elif system_name == 'dream':
                    dream_stats = self.dream_system.get_system_stats()
                    self.logger.info(f"Dream: {dream_stats['total_dreams']} dreams", "AIOS")
                elif system_name == 'enterprise':
                    enterprise_stats = self.enterprise_system.get_system_stats()
                    self.logger.info(f"Enterprise: {enterprise_stats['total_users']} users", "AIOS")
                elif system_name == 'luna':
                    self.logger.info(f"Luna: {self.luna_system.total_interactions} interactions", "AIOS")
                elif system_name == 'streamlit':
                    streamlit_stats = self.streamlit_system.get_system_stats()
                    self.logger.info(f"Streamlit: {streamlit_stats['total_sessions']} sessions", "AIOS")
                elif system_name == 'utils':
                    utils_stats = self.utils_system.get_system_stats()
                    self.logger.info(f"Utils: {utils_stats['total_operations']} operations", "AIOS")
                elif system_name == 'support':
                    support_status = self.safe_method_call(self.support_system, 'get_system_status')
                    if support_status['success']:
                        support_fragments = support_status['result'].get('cache', {}).get('total_fragments', 0)
                        self.logger.info(f"Support: {support_fragments} fragments", "AIOS")
                    else:
                        self.logger.info(f"Support: Status unavailable ({support_status['error']})", "AIOS")
            
            # Show lazy loading status
            unloaded_systems = set(['backup', 'carma', 'dream', 'enterprise', 'luna', 'streamlit', 'utils']) - self._initialized_systems
            if unloaded_systems:
                self.logger.info(f"Other systems ({', '.join(unloaded_systems)}) will load on-demand", "AIOS")
                
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}", "AIOS")
    
    # === METHOD VALIDATION AND ERROR HANDLING ===
    
    def validate_method_exists(self, obj: Any, method_name: str) -> bool:
        """Check if a method exists on an object."""
        return hasattr(obj, method_name) and callable(getattr(obj, method_name, None))
    
    def safe_method_call(self, obj: Any, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Safely call a method with error handling."""
        if not self.validate_method_exists(obj, method_name):
            return {
                "success": False,
                "error": f"Method '{method_name}' does not exist on {type(obj).__name__}",
                "available_methods": [method for method in dir(obj) if not method.startswith('_')]
            }
        
        try:
            result = getattr(obj, method_name)(*args, **kwargs)
            return {
                "success": True,
                "result": result,
                "method": method_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": method_name,
                "args": args,
                "kwargs": kwargs
            }
    
    # === LINUX-SPECIFIC METHODS ===
    
    def check_lm_studio_status(self) -> Dict[str, Any]:
        """Check LM Studio status on Linux"""
        is_running = check_lm_studio_linux()
        return {
            "running": is_running,
            "host": "127.0.0.1",
            "port": 1234,
            "platform": "linux"
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information for Linux"""
        return {
            "platform": "linux",
            "environment": self.env_info,
            "proxy_config": self.proxy_config,
            "lm_studio": self.check_lm_studio_status(),
            "python_version": sys.version,
            "virtual_env": self.env_info["venv_active"],
            "interactive": self.env_info["is_interactive"]
        }
    
    def create_systemd_service(self, service_name: str = "luna-aios") -> bool:
        """Create systemd service for Luna AIOS (optional)"""
        try:
            service_content = f"""[Unit]
Description=Luna AIOS Consciousness System
After=network.target

[Service]
Type=simple
User={self.env_info['user']}
WorkingDirectory={os.getcwd()}
Environment=VIRTUAL_ENV={os.environ.get('VIRTUAL_ENV', '')}
Environment=PATH={os.environ.get('PATH', '')}
ExecStart={sys.executable} main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            
            service_file = Path(f"/etc/systemd/system/{service_name}.service")
            
            # Note: This requires sudo privileges
            print(f"To create systemd service, run:")
            print(f"sudo tee {service_file} << 'EOF'")
            print(service_content)
            print("EOF")
            print(f"sudo systemctl enable {service_name}")
            print(f"sudo systemctl start {service_name}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to create systemd service: {e}", "AIOS")
            return False
    
    # === CORE SYSTEM METHODS (same as Windows version) ===
    
    def run_luna_learning(self, questions: int = 3, test_runs: int = 1) -> Dict:
        """Run Luna learning session."""
        
        print(f"\nStarting Luna Learning Session (Linux)")
        print(f"   Questions: {questions}")
        print(f"   Test runs: {test_runs}")
        print("=" * 80)
        
        # Generate Big Five questions
        big_five_questions = self._generate_big_five_questions(questions)
        
        # Lazy load Luna system and run learning session
        luna_system = self._get_system('luna')
        results = luna_system.run_learning_session(big_five_questions)
        
        print(f"\nLuna Learning Complete")
        print(f"   Duration: {results.get('session_duration', 0):.2f}s")
        print(f"   Dream cycles: {results.get('dream_cycles_triggered', 0)}")
        print(f"   Total interactions: {luna_system.total_interactions}")
        
        return results
    
    def _generate_big_five_questions(self, count: int) -> List[str]:
        """Generate Big Five personality questions"""
        questions = [
            "How do you typically respond to new social situations?",
            "What motivates you most in your daily activities?",
            "How do you handle stress and pressure?",
            "What is your approach to making decisions?",
            "How do you prefer to spend your free time?",
            "What kind of work environment suits you best?",
            "How do you handle conflicts with others?",
            "What drives your curiosity and learning?",
            "How do you manage your time and priorities?",
            "What gives you the most satisfaction in life?"
        ]
        return random.sample(questions, min(count, len(questions)))
    
    # === CLI INTERFACE ===
    
    def run_cli(self, args: List[str] = None):
        """Run CLI interface for Linux"""
        parser = argparse.ArgumentParser(description="AIOS Clean System (Linux)")
        parser.add_argument("--mode", choices=[mode.value for mode in SystemMode], 
                          default=SystemMode.INTERACTIVE.value, help="System mode")
        parser.add_argument("--luna-questions", type=int, default=3, help="Number of Luna learning questions")
        parser.add_argument("--test-runs", type=int, default=1, help="Number of test runs")
        parser.add_argument("--create-service", action="store_true", help="Create systemd service")
        parser.add_argument("--info", action="store_true", help="Show system information")
        
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = parser.parse_args(args)
        
        if parsed_args.create_service:
            self.create_systemd_service()
            return
        
        if parsed_args.info:
            info = self.get_system_info()
            print(json.dumps(info, indent=2))
            return
        
        if parsed_args.mode == SystemMode.LUNA.value:
            self.run_luna_learning(parsed_args.luna_questions, parsed_args.test_runs)
        else:
            print(f"Mode '{parsed_args.mode}' not implemented yet for Linux")

# === MAIN EXECUTION ===

if __name__ == "__main__":
    # Check if we're in a virtual environment
    if not setup_venv_if_needed():
        print("Please activate your virtual environment first:")
        print("source .venv/bin/activate")
        sys.exit(1)
    
    # Initialize and run AIOS Clean Linux
    aios = AIOSCleanLinux()
    aios.run_cli()
