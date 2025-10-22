#!/usr/bin/env python3
"""
Support Core - Cache Operations
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

# Import system classes
from .system_classes import SystemConfig


class CacheStatus(Enum):
    """Cache status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CORRUPTED = "corrupted"
    RECOVERING = "recovering"


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    total_fragments: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0
    avg_response_time: float = 0.0
    memory_usage: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


class CacheOperations:
    """Core cache operations and management"""
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(SystemConfig.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metrics = CacheMetrics()
        
        print(" Cache Operations Initialized")
        print(f"   Cache directory: {self.cache_dir}")
    
    def create_file_id(self, content: str, parent_id: str = None) -> str:
        """Create unique file ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"frag_{content_hash}_{timestamp}_{random_suffix}"
    
    def save_fragment(self, file_id: str, fragment_data: Dict, cache_dir: Path) -> bool:
        """Save fragment to cache"""
        try:
            fragment_file = cache_dir / f"{file_id}.json"
            with open(fragment_file, 'w') as f:
                json.dump(fragment_data, f, indent=2)
            return True
        except Exception as e:
            print(f" Error saving fragment {file_id}: {e}")
            return False
    
    def load_fragment(self, file_id: str, cache_dir: Path) -> Optional[Dict]:
        """Load fragment from cache"""
        try:
            fragment_file = cache_dir / f"{file_id}.json"
            if fragment_file.exists():
                with open(fragment_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f" Error loading fragment {file_id}: {e}")
        return None
    
    def delete_fragment(self, file_id: str, cache_dir: Path) -> bool:
        """Delete fragment from cache"""
        try:
            fragment_file = cache_dir / f"{file_id}.json"
            if fragment_file.exists():
                fragment_file.unlink()
                return True
        except Exception as e:
            print(f" Error deleting fragment {file_id}: {e}")
        return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        fragment_files = list(self.cache_dir.glob("*.json"))
        
        return {
            'total_fragments': len(fragment_files),
            'cache_size_mb': sum(f.stat().st_size for f in fragment_files) / (1024 * 1024),
            'cache_directory': str(self.cache_dir),
            'status': 'active' if fragment_files else 'empty'
        }

class CacheRegistry:
    """Cache registry for tracking fragments"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.registry_file = cache_dir / "registry.json"
        self.fragments = {}
        self.load_registry()
        
        print(" Cache Registry Initialized")
        print(f"   Registry file: {self.registry_file}")
        print(f"   Loaded {len(self.fragments)} fragments")
    
    def load_registry(self):
        """Load registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    # Check for both 'fragments' and 'file_registry' keys
                    self.fragments = data.get('file_registry', data.get('fragments', {}))
            except Exception as e:
                print(f"  Error loading registry: {e}")
                self.fragments = {}
    
    def save_registry(self):
        """Save registry to file"""
        try:
            data = {
                'fragments': self.fragments,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"  Error saving registry: {e}")
    
    def add_fragment(self, file_id: str, fragment_data: Dict):
        """Add fragment to registry"""
        self.fragments[file_id] = {
            'id': file_id,
            'created': fragment_data.get('created', datetime.now().isoformat()),
            'size': len(str(fragment_data)),
            'status': 'active'
        }
        self.save_registry()
    
    def remove_fragment(self, file_id: str):
        """Remove fragment from registry"""
        if file_id in self.fragments:
            del self.fragments[file_id]
            self.save_registry()
    
    def get_fragment(self, file_id: str) -> Optional[Dict]:
        """Get fragment from registry"""
        return self.fragments.get(file_id)
    
    def list_fragments(self) -> List[str]:
        """List all fragment IDs"""
        return list(self.fragments.keys())
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'total_fragments': len(self.fragments),
            'active_fragments': sum(1 for f in self.fragments.values() if f.get('status') == 'active'),
            'total_size': sum(f.get('size', 0) for f in self.fragments.values()),
            'last_updated': datetime.now().isoformat()
        }

class CacheBackup:
    """Cache backup and restore operations"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        # Note: backup functionality moved to backup_core
        # This class no longer creates backup directories
        
        print(" Cache Backup System Initialized")
        print(f"   Note: Backup functionality moved to backup_core")
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create cache backup - DEPRECATED: Use backup_core instead"""
        print("⚠️ Warning: Cache backup functionality moved to backup_core")
        return ""
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore cache from backup - DEPRECATED: Use backup_core instead"""
        print("⚠️ Warning: Cache restore functionality moved to backup_core")
        return False
    
    def list_backups(self) -> List[str]:
        """List available backups - DEPRECATED: Use backup_core instead"""
        print("⚠️ Warning: List backups functionality moved to backup_core")
        return []
