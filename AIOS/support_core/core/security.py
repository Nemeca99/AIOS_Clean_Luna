#!/usr/bin/env python3
"""
Support Core - Security
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

# Import dependencies from same module
from .config import AIOSConfig, aios_config
from .logger import AIOSLogger

# Create a global logger instance for security validator
aios_logger = AIOSLogger("SecurityValidator")


class AIOSSecurityValidator:
    """Unified security and validation system inspired by PowerShell wrapper"""
    
    def __init__(self, config: AIOSConfig = None, logger: AIOSLogger = None):
        self.config = config or aios_config
        self.logger = logger or aios_logger
        self.security_rules = self._load_security_rules()
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load security validation rules"""
        return {
            "input_sanitization": {
                "enabled": self.config.get("SECURITY_VALIDATION", True),
                "max_length": 10000,
                "allowed_characters": r"a-zA-Z0-9\s\-_.,!?@#$%^&*()+={}[]|\\:;\"'<>/`~",
                "blocked_patterns": [
                    r"<script.*?>.*?</script>",
                    r"javascript:",
                    r"vbscript:",
                    r"on\w+\s*="
                ]
            },
            "rate_limiting": {
                "enabled": self.config.get("THROTTLING_ENABLED", True),
                "max_requests_per_minute": 100,
                "max_requests_per_hour": 1000
            },
            "admin_operations": {
                "require_confirmation": True,
                "log_all_operations": True,
                "audit_trail": True
            }
        }
    
    def validate_input(self, input_data: str, input_type: str = "general") -> Dict[str, Any]:
        """Validate and sanitize input data"""
        if not self.security_rules["input_sanitization"]["enabled"]:
            return {"valid": True, "sanitized": input_data, "warnings": []}
        
        warnings = []
        sanitized = input_data
        
        # Length validation
        max_length = self.security_rules["input_sanitization"]["max_length"]
        if len(input_data) > max_length:
            warnings.append(f"Input truncated from {len(input_data)} to {max_length} characters")
            sanitized = input_data[:max_length]
        
        # Pattern validation
        for pattern in self.security_rules["input_sanitization"]["blocked_patterns"]:
            if re.search(pattern, sanitized, re.IGNORECASE):
                warnings.append(f"Potentially malicious pattern detected: {pattern}")
                sanitized = re.sub(pattern, "[BLOCKED]", sanitized, flags=re.IGNORECASE)
        
        # Character validation
        allowed_chars = self.security_rules["input_sanitization"]["allowed_characters"]
        if not re.match(f"^[{allowed_chars}]*$", sanitized):
            warnings.append("Input contains disallowed characters")
            sanitized = re.sub(f"[^{allowed_chars}]", "?", sanitized)
        
        return {
            "valid": len(warnings) == 0,
            "sanitized": sanitized,
            "warnings": warnings,
            "original_length": len(input_data),
            "sanitized_length": len(sanitized)
        }
    
    def check_admin_permissions(self, operation: str) -> bool:
        """Check if admin permissions are required and available"""
        admin_ops = ["delete", "restore", "backup", "update", "install", "uninstall"]
        
        if any(op in operation.lower() for op in admin_ops):
            return self.config.get("ADMIN_MODE", False)
        
        return True

