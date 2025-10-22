#!/usr/bin/env python3
"""
Support Core - Logger
Extracted from monolithic support_core.py for better modularity.
"""

import sys
from pathlib import Path
import time
import json
import os
import shutil
import re
import hashlib
import math
import random
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup Unicode safety
try:
    from utils_core.unicode_safe_output import setup_unicode_safe_output
    setup_unicode_safe_output()
except ImportError:
    print("Warning: Unicode safety layer not available")

# Import config from same module
from .config import AIOSConfig, aios_config


class AIOSLoggerError(Exception):
    """Custom exception for AIOS logger errors"""
    pass


class AIOSLogger:
    """Unified logging system with advanced features and real-time monitoring"""
    
    def __init__(self, name: str = "AIOS", config: AIOSConfig = None):
        self.name = name
        self.config = config or aios_config
        self.log_dir = Path(self.config.get("LOG_DIR"))
        self.debug_dir = Path(self.config.get("DEBUG_DIR"))
        self._lock = threading.RLock()
        self._log_buffer = []
        self._buffer_size = 1000
        self._last_flush = time.time()
        self._flush_interval = 5.0  # seconds
        self._metrics = {
            'total_logs': 0,
            'logs_by_level': {},
            'errors': 0,
            'last_error': None
        }
        
        # Setup Python logging integration
        self._setup_python_logging()
        self._ensure_directories()
        
        # Start background flush thread
        self._start_background_flush()
    
    def _setup_python_logging(self):
        """Setup Python logging integration"""
        log_level = getattr(logging, self.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
        
        # Create logger
        self.python_logger = logging.getLogger(f"aios.{self.name}")
        self.python_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in self.python_logger.handlers[:]:
            self.python_logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if not self.config.get("SILENT_MODE", False):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self.python_logger.addHandler(console_handler)
        
        # File handler
        if self.config.get("MONITORING_ENABLED", True):
            try:
                log_file = self.log_dir / f"{self.name.lower()}_{datetime.now().strftime('%Y-%m-%d')}.log"
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                self.python_logger.addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not setup file logging: {e}")
    
    def _ensure_directories(self):
        """Ensure log directories exist with proper permissions"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            
            # Set proper permissions if possible
            try:
                os.chmod(self.log_dir, 0o755)
                os.chmod(self.debug_dir, 0o755)
            except (OSError, PermissionError):
                pass  # Ignore permission errors
                
        except Exception as e:
            raise AIOSLoggerError(f"Failed to create log directories: {e}")
    
    def _get_log_file(self, level: str = "INFO") -> Path:
        """Get log file path for current date with rotation support"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"aios_{level.lower()}_{date_str}.log"
    
    def _format_message(self, message: str, level: str, source: str = None, 
                       include_stack: bool = False) -> str:
        """Format log message with timestamp and context"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        source_str = f"[{source}]" if source else f"[{self.name}]"
        
        # Add stack trace for errors if requested
        stack_info = ""
        if include_stack and level in ["ERROR", "CRITICAL"]:
            stack_info = f"\nStack trace:\n{traceback.format_exc()}"
        
        return f"[{timestamp}] [{level}] {source_str} {message}{stack_info}"
    
    def _write_log(self, message: str, level: str, source: str = None, 
                  include_stack: bool = False, force_flush: bool = False):
        """Write log message with buffering and error handling"""
        try:
            formatted_msg = self._format_message(message, level, source, include_stack)
            
            # Update metrics
            with self._lock:
                self._metrics['total_logs'] += 1
                self._metrics['logs_by_level'][level] = self._metrics['logs_by_level'].get(level, 0) + 1
                
                if level in ["ERROR", "CRITICAL"]:
                    self._metrics['errors'] += 1
                    self._metrics['last_error'] = {
                        'message': message,
                        'timestamp': datetime.now().isoformat(),
                        'source': source
                    }
            
            # Console output with colors
            if not self.config.get("SILENT_MODE", False):
                self._write_console(formatted_msg, level)
            
            # File logging with buffering
            if self.config.get("MONITORING_ENABLED", True):
                self._buffer_log(formatted_msg, level, force_flush)
            
            # Python logging integration
            self._write_python_log(message, level, source)
            
        except Exception as e:
            # Fallback to basic print if logging fails
            print(f"Logging error: {e} - Original message: {message}")
    
    def _write_console(self, formatted_msg: str, level: str):
        """Write to console with colors"""
        color_map = {
            "SUCCESS": "\033[92m",  # Green
            "WARN": "\033[93m",     # Yellow
            "ERROR": "\033[91m",    # Red
            "CRITICAL": "\033[91m", # Red
            "INFO": "\033[96m",     # Cyan
            "DEBUG": "\033[95m",    # Magenta
            "TRACE": "\033[90m"     # Gray
        }
        color = color_map.get(level, "\033[0m")
        print(f"{color}{formatted_msg}\033[0m")
    
    def _buffer_log(self, formatted_msg: str, level: str, force_flush: bool = False):
        """Buffer log messages for efficient writing"""
        with self._lock:
            self._log_buffer.append((formatted_msg, level, time.time()))
            
            # Flush if buffer is full or forced
            if (len(self._log_buffer) >= self._buffer_size or 
                force_flush or 
                time.time() - self._last_flush > self._flush_interval):
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush log buffer to files"""
        if not self._log_buffer:
            return
        
        try:
            # Group by level for efficient writing
            logs_by_level = {}
            for msg, level, timestamp in self._log_buffer:
                if level not in logs_by_level:
                    logs_by_level[level] = []
                logs_by_level[level].append(msg)
            
            # Write to files
            for level, messages in logs_by_level.items():
                log_file = self._get_log_file(level)
                with open(log_file, 'a', encoding='utf-8') as f:
                    for msg in messages:
                        f.write(msg + "\n")
            
            self._log_buffer.clear()
            self._last_flush = time.time()
            
        except Exception as e:
            print(f"Error flushing log buffer: {e}")
    
    def _write_python_log(self, message: str, level: str, source: str = None):
        """Write to Python logging system"""
        try:
            # Map our levels to Python logging levels
            level_map = {
                "TRACE": logging.DEBUG,
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARN": logging.WARNING,
                "ERROR": logging.ERROR,
                "SUCCESS": logging.INFO,
                "CRITICAL": logging.CRITICAL
            }
            
            python_level = level_map.get(level, logging.INFO)
            self.python_logger.log(python_level, message)
            
        except Exception:
            pass  # Don't fail on Python logging errors
    
    def _start_background_flush(self):
        """Start background thread for periodic log flushing"""
        def flush_worker():
            while True:
                time.sleep(self._flush_interval)
                try:
                    with self._lock:
                        if self._log_buffer:
                            self._flush_buffer()
                except Exception:
                    pass  # Ignore errors in background thread
        
        flush_thread = threading.Thread(target=flush_worker, daemon=True)
        flush_thread.start()
    
    def success(self, message: str, source: str = None):
        """Log success message"""
        self._write_log(message, "SUCCESS", source)
    
    def info(self, message: str, source: str = None):
        """Log info message"""
        self._write_log(message, "INFO", source)
    
    def warn(self, message: str, source: str = None):
        """Log warning message"""
        self._write_log(message, "WARN", source)
    
    def error(self, message: str, source: str = None, include_stack: bool = True):
        """Log error message"""
        self._write_log(message, "ERROR", source, include_stack)
    
    def critical(self, message: str, source: str = None, include_stack: bool = True):
        """Log critical message"""
        self._write_log(message, "CRITICAL", source, include_stack)
    
    def debug(self, message: str, source: str = None):
        """Log debug message"""
        if self.config.get("DEBUG_MODE", False):
            self._write_log(message, "DEBUG", source)
    
    def trace(self, message: str, source: str = None):
        """Log trace message"""
        if self.config.get("DEBUG_MODE", False):
            self._write_log(message, "TRACE", source)
    
    def log(self, source: str, message: str, level: str = "INFO"):
        """Compatibility method for HiveMindLogger interface"""
        level_map = {
            "INFO": "INFO",
            "WARNING": "WARN", 
            "ERROR": "ERROR",
            "SUCCESS": "SUCCESS",
            "DEBUG": "DEBUG",
            "CRITICAL": "CRITICAL"
        }
        mapped_level = level_map.get(level.upper(), "INFO")
        self._write_log(message, mapped_level, source)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get logging metrics"""
        with self._lock:
            return self._metrics.copy()
    
    def flush(self):
        """Force flush all pending logs"""
        with self._lock:
            self._flush_buffer()
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    self.info(f"Cleaned up old log file: {log_file.name}")
                    
        except Exception as e:
            self.error(f"Error cleaning up old logs: {e}")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.flush()
        except Exception as e:
            # Log flush failed - not critical
            print(f"Warning: Logger flush failed during cleanup: {e}")

