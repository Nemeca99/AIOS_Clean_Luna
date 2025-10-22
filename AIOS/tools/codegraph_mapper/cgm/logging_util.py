"""
Logging utility for CodeGraph Mapper
Append-only JSONL logging to L:\AIOS\logs\tools\codegraph-mapper.jsonl
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any


class CGMLogger:
    """Append-only JSONL logger for CGM"""
    
    def __init__(self, log_path: str = "L:\\AIOS\\logs\\tools\\codegraph-mapper.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.start_time = time.perf_counter()
    
    def log(self, level: str, event: str, **kwargs):
        """Write a log entry"""
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event": event,
            **kwargs
        }
        
        # Append to log file
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def info(self, event: str, **kwargs):
        """Log INFO event"""
        self.log("INFO", event, **kwargs)
    
    def warn(self, event: str, **kwargs):
        """Log WARN event"""
        self.log("WARN", event, **kwargs)
    
    def error(self, event: str, **kwargs):
        """Log ERROR event"""
        self.log("ERROR", event, **kwargs)
    
    def elapsed_ms(self) -> int:
        """Get elapsed milliseconds since start"""
        return int((time.perf_counter() - self.start_time) * 1000)

