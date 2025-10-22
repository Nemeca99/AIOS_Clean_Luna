#!/usr/bin/env python3
"""
Support Core - Configuration Module
AIOS configuration system with validation and real-time updates.
Extracted from monolithic support_core.py for better modularity.
"""

import sys
from pathlib import Path
import time
import json
import os
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup Unicode safety
try:
    from utils_core.unicode_safe_output import setup_unicode_safe_output
    setup_unicode_safe_output()
except ImportError:
    print("Warning: Unicode safety layer not available")


class AIOSConfigError(Exception):
    """Custom exception for AIOS configuration errors"""
    pass


class AIOSConfig:
    """Unified AIOS configuration system with validation and real-time updates"""
    
    def __init__(self, config_file: str = "data_core/config/aios_config.json"):
        self.config_file = Path(config_file)
        self.config = {}
        self._validation_rules = self._setup_validation_rules()
        self._watchers = []
        self._lock = threading.RLock()
        
        # Load configuration with proper error handling
        try:
            self.config = self._load_default_config()
            self._load_config()
            self._validate_config()
        except Exception as e:
            raise AIOSConfigError(f"Failed to initialize AIOS configuration: {e}")
    
    def _setup_validation_rules(self) -> Dict[str, Callable]:
        """Setup configuration validation rules"""
        return {
            "AIOS_ROOT": lambda x: Path(x).exists() and Path(x).is_dir(),
            "PYTHON_ENV_PATH": lambda x: Path(x).exists() and Path(x).is_dir(),
            "LOG_DIR": lambda x: True,  # Will be created if needed
            "DEBUG_DIR": lambda x: True,  # Will be created if needed
            "MONITORING_ENABLED": lambda x: isinstance(x, bool),
            "ADMIN_MODE": lambda x: isinstance(x, bool),
            "DEBUG_MODE": lambda x: isinstance(x, bool),
            "SILENT_MODE": lambda x: isinstance(x, bool),
            "UNICODE_SAFE": lambda x: isinstance(x, bool),
            "CACHE_TTL_SECONDS": lambda x: isinstance(x, int) and x > 0,
            "MAX_CACHE_SIZE_MB": lambda x: isinstance(x, int) and x > 0,
            "METRICS_REFRESH_INTERVAL": lambda x: isinstance(x, int) and x > 0,
            "PROCESS_MONITORING_INTERVAL": lambda x: isinstance(x, int) and x > 0,
            "SECURITY_VALIDATION": lambda x: isinstance(x, bool),
            "THROTTLING_ENABLED": lambda x: isinstance(x, bool),
            "TELEMETRY_ENABLED": lambda x: isinstance(x, bool),
            "STATE_SYNC_ENABLED": lambda x: isinstance(x, bool),
            "AUTO_RECOVERY": lambda x: isinstance(x, bool),
            "MAX_RETRIES": lambda x: isinstance(x, int) and 0 <= x <= 10,
            "CIRCUIT_BREAKER_ENABLED": lambda x: isinstance(x, bool),
            "FAILOVER_ENABLED": lambda x: isinstance(x, bool)
        }
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values with environment variable support"""
        root_path = Path(__file__).parent.parent.parent
        
        return {
            "AIOS_ROOT": str(root_path),
            "PYTHON_ENV_PATH": str(root_path / "venv"),
            "LOG_DIR": str(root_path / "data_core" / "log" / "monitoring"),
            "DEBUG_DIR": str(root_path / "data_core" / "temp" / "debug"),
            "MONITORING_ENABLED": os.getenv("AIOS_MONITORING_ENABLED", "true").lower() == "true",
            "ADMIN_MODE": os.getenv("AIOS_ADMIN_MODE", "false").lower() == "true",
            "DEBUG_MODE": os.getenv("AIOS_DEBUG_MODE", "false").lower() == "true",
            "SILENT_MODE": os.getenv("AIOS_SILENT_MODE", "false").lower() == "true",
            "UNICODE_SAFE": os.getenv("AIOS_UNICODE_SAFE", "true").lower() == "true",
            "CACHE_TTL_SECONDS": int(os.getenv("AIOS_CACHE_TTL_SECONDS", "300")),
            "MAX_CACHE_SIZE_MB": int(os.getenv("AIOS_MAX_CACHE_SIZE_MB", "100")),
            "METRICS_REFRESH_INTERVAL": int(os.getenv("AIOS_METRICS_REFRESH_INTERVAL", "5")),
            "PROCESS_MONITORING_INTERVAL": int(os.getenv("AIOS_PROCESS_MONITORING_INTERVAL", "10")),
            "SECURITY_VALIDATION": os.getenv("AIOS_SECURITY_VALIDATION", "true").lower() == "true",
            "THROTTLING_ENABLED": os.getenv("AIOS_THROTTLING_ENABLED", "true").lower() == "true",
            "TELEMETRY_ENABLED": os.getenv("AIOS_TELEMETRY_ENABLED", "true").lower() == "true",
            "STATE_SYNC_ENABLED": os.getenv("AIOS_STATE_SYNC_ENABLED", "true").lower() == "true",
            "AUTO_RECOVERY": os.getenv("AIOS_AUTO_RECOVERY", "true").lower() == "true",
            "MAX_RETRIES": int(os.getenv("AIOS_MAX_RETRIES", "3")),
            "CIRCUIT_BREAKER_ENABLED": os.getenv("AIOS_CIRCUIT_BREAKER_ENABLED", "true").lower() == "true",
            "FAILOVER_ENABLED": os.getenv("AIOS_FAILOVER_ENABLED", "true").lower() == "true",
            # Additional configuration options
            "API_TIMEOUT": int(os.getenv("AIOS_API_TIMEOUT", "30")),
            "MAX_WORKERS": int(os.getenv("AIOS_MAX_WORKERS", "4")),
            "ENABLE_METRICS": os.getenv("AIOS_ENABLE_METRICS", "true").lower() == "true",
            "LOG_LEVEL": os.getenv("AIOS_LOG_LEVEL", "INFO").upper(),
            "BACKUP_RETENTION_DAYS": int(os.getenv("AIOS_BACKUP_RETENTION_DAYS", "30")),
            "HEALTH_CHECK_INTERVAL": int(os.getenv("AIOS_HEALTH_CHECK_INTERVAL", "60")),
            "PERFORMANCE_MONITORING": os.getenv("AIOS_PERFORMANCE_MONITORING", "true").lower() == "true"
        }
    
    def _load_config(self):
        """Load configuration from file with comprehensive error handling"""
        if not self.config_file.exists():
            self._log_message("Configuration file not found, using defaults", "WARN")
            self._save_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Merge with defaults, preserving type safety
            for key, value in file_config.items():
                if key in self.config:
                    # Type conversion based on default value type
                    if isinstance(self.config[key], bool):
                        self.config[key] = bool(value)
                    elif isinstance(self.config[key], int):
                        self.config[key] = int(value)
                    elif isinstance(self.config[key], str):
                        self.config[key] = str(value)
                    else:
                        self.config[key] = value
                else:
                    self.config[key] = value
            
            self._log_message("Configuration loaded successfully", "INFO")
            
        except json.JSONDecodeError as e:
            raise AIOSConfigError(f"Invalid JSON in configuration file: {e}")
        except PermissionError as e:
            raise AIOSConfigError(f"Permission denied accessing configuration file: {e}")
        except Exception as e:
            raise AIOSConfigError(f"Error loading configuration: {e}")
    
    def _validate_config(self):
        """Validate configuration values"""
        for key, validator in self._validation_rules.items():
            if key in self.config:
                try:
                    if not validator(self.config[key]):
                        raise AIOSConfigError(f"Invalid value for {key}: {self.config[key]}")
                except Exception as e:
                    raise AIOSConfigError(f"Validation error for {key}: {e}")
    
    def _save_config(self):
        """Save current configuration to file with atomic write"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Atomic write using temporary file
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Atomic move
            temp_file.replace(self.config_file)
            self._log_message("Configuration saved successfully", "INFO")
            
        except PermissionError as e:
            raise AIOSConfigError(f"Permission denied saving configuration: {e}")
        except Exception as e:
            raise AIOSConfigError(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with thread safety"""
        with self._lock:
            return self.config.get(key, default)
    
    def set(self, key: str, value: Any, validate: bool = True):
        """Set configuration value with validation and notification"""
        with self._lock:
            if validate and key in self._validation_rules:
                if not self._validation_rules[key](value):
                    raise AIOSConfigError(f"Invalid value for {key}: {value}")
            
            old_value = self.config.get(key)
            self.config[key] = value
            
            # Notify watchers
            for watcher in self._watchers:
                try:
                    watcher(key, old_value, value)
                except Exception as e:
                    self._log_message(f"Error in config watcher: {e}", "ERROR")
            
            self._save_config()
    
    def add_watcher(self, callback: Callable[[str, Any, Any], None]):
        """Add a configuration change watcher"""
        self._watchers.append(callback)
    
    def remove_watcher(self, callback: Callable[[str, Any, Any], None]):
        """Remove a configuration change watcher"""
        if callback in self._watchers:
            self._watchers.remove(callback)
    
    def reload(self):
        """Reload configuration from file"""
        with self._lock:
            self._load_config()
            self._validate_config()
    
    def export_config(self, file_path: str = None) -> str:
        """Export current configuration to a file"""
        if not file_path:
            file_path = f"aios_config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_path = Path(file_path)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        return str(export_path)
    
    def _log_message(self, message: str, level: str = "INFO"):
        """Internal logging for configuration system"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] [AIOS-CONFIG-{level}] {message}"
        
        if not self.get("SILENT_MODE", False):
            print(log_msg)
        
        # Also log to file if logging is enabled
        if self.get("ENABLE_METRICS", True):
            try:
                log_file = Path(self.get("LOG_DIR")) / f"config_{datetime.now().strftime('%Y-%m-%d')}.log"
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(log_msg + "\n")
            except Exception:
                pass  # Don't fail on logging errors


# Global AIOS configuration instance
aios_config = AIOSConfig()

