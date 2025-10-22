#!/usr/bin/env python3
"""
Luna Core Utilities
Helper functions and classes for Luna core system
"""

import json
from pathlib import Path
from datetime import datetime
from functools import wraps

# === ERROR HANDLER DECORATOR ===

def error_handler(component: str, error_type: str, recovery_action: str, auto_recover: bool = False):
    """Decorator for error handling and recovery"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"⚠ Error in {component}.{func.__name__}: {e}")
                
                if auto_recover:
                    print(f"🔧 Attempting recovery: {recovery_action}")
                    try:
                        # Simple recovery logic
                        if recovery_action == "CLEAR_CACHE":
                            if hasattr(args[0], 'cache'):
                                args[0].cache = {}
                        elif recovery_action == "RESET_PERSONALITY":
                            if hasattr(args[0], 'personality_dna'):
                                args[0].personality_dna = args[0]._create_default_personality()
                        elif recovery_action == "FALLBACK_MODE":
                            return "I'm experiencing some technical difficulties, but I'm still here to help!"
                        
                        # Retry the function
                        return func(*args, **kwargs)
                    except Exception as recovery_error:
                        print(f"❌ Recovery failed: {recovery_error}")
                        return None
                else:
                    raise e
        return wrapper
    return decorator

# === HIVE MIND LOGGER ===

class HiveMindLogger:
    """Logging system for Luna AI"""
    
    def __init__(self, log_file: str = "data_core/log/hive_mind/hive_mind.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_levels = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3,
            'CRITICAL': 4
        }
        self.current_level = 'INFO'
        
        # Initialize log file
        with open(self.log_file, 'a') as f:
            f.write(f"\n=== Luna AI Session Started: {datetime.now().isoformat()} ===\n")
        
        print("00:00:00 | INFO | HiveMindLogger initialized")
    
    def log(self, component: str, message: str, level: str = "INFO"):
        """Log a message with timestamp and component"""
        if self.log_levels[level] >= self.log_levels[self.current_level]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"{timestamp} | {level} | {component}: {message}"
            
            print(log_entry)
            
            # Write to file
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")
    
    def log_error(self, component: str, function: str, error_type: str, error_message: str, 
                  traceback: str, args: tuple, kwargs: dict, duration: float, 
                  timestamp: str, recovery_action: str):
        """Log detailed error information"""
        error_data = {
            "component": component,
            "function": function,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback,
            "args": str(args),
            "kwargs": str(kwargs),
            "duration": duration,
            "timestamp": timestamp,
            "recovery_action": recovery_action
        }
        
        self.log(component, f"ERROR in {function}: {error_message} | Extra: {json.dumps(error_data)}", "ERROR")

