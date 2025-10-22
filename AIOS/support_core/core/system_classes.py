#!/usr/bin/env python3
"""
Support Core - System Classes
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



class SystemConfig:
    """System configuration constants"""
    # File and Cache Settings
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    MAX_CACHE_SIZE = 1000
    MAX_SPLITS = 6
    CACHE_DIR = "data_core/FractalCache"
    CONFIG_DIR = "config"
    LOG_DIR = "log"
    # Note: BACKUP_DIR removed - backup_core manages all backups
    TEMP_DIR = "temp"
    
    # Embedding Settings
    DEFAULT_EMBEDDING_DIMENSION = 1024  # mixedbread-ai/mxbai-embed-large-v1 uses 1024 dimensions
    DEFAULT_EMBEDDING_MODEL = "llama-3.2-1b-instruct-abliterated"  # Standardized embedder (1B)
    EMBEDDING_BATCH_SIZE = 32
    FALLBACK_DIMENSION = 1024
    
    # API Settings
    LM_STUDIO_URL = "http://localhost:1234"
    LM_STUDIO_CHAT_ENDPOINT = "/v1/chat/completions"
    LM_STUDIO_EMBEDDING_ENDPOINT = "/v1/embeddings"
    DEFAULT_TIMEOUT = 0  # No timeout for localhost
    MAX_RETRIES = 3
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60
    
    # Performance Settings
    CACHE_CLEANUP_INTERVAL = 3600  # 1 hour
    RECOVERY_RETRY_LIMIT = 3
    GOAL_INTERVAL = 300  # 5 minutes
    CONSOLIDATION_THRESHOLD = 0.8
    SEMANTIC_CLUSTERING = 0.6
    EPISODIC_DECAY_RATE = 0.1
    
    # Personality Settings
    DEFAULT_EMPATHY = 0.9
    DEFAULT_HUMOR = 0.7
    LEARNING_RATE = 0.01
    ADAPTATION_THRESHOLD = 0.1
    EMOTION_DECAY_RATE = 0.95
    BOOST_THRESHOLD = 0.7
    
    # Memory Settings
    SLOW_WAVE_THRESHOLD = 0.6
    REM_THRESHOLD = 0.8
    SLOW_WAVE_DURATION = 5
    REM_DURATION = 3
    UNCERTAINTY_THRESHOLD = 0.3
    CONFIDENCE_THRESHOLD = 0.7
    TEMPORAL_WINDOW = 300
    WEAK_THRESHOLD = 0.3
    STRONG_THRESHOLD = 0.7
    TAGGING_STRENGTH = 0.2
    PREDICTION_WINDOW = 5
    PREDICTION_THRESHOLD = 0.3
    
    # Network Settings
    SERVER_BLOCKS = 20
    MAX_USERS_PER_BLOCK = 60
    TOTAL_CAPACITY = 1200
    
    # Performance Settings
    TARGET_PERFORMANCE = 100  # 100% performance
    PERFORMANCE_INDICATORS = 12


class FilePaths:
    """File path constants"""
    CACHE_DIR = "data_core/FractalCache"
    CONFIG_DIR = "config"
    LOG_DIR = "log"
    BACKUP_DIR = "backups"
    TEMP_DIR = "temp"
    
    # Specific files
    CACHE_REGISTRY = "data_core/FractalCache/registry.json"
    EMBEDDING_CACHE = "data_core/FractalCache/embeddings.json"
    RECOVERY_LOG = "log/recovery.log"
    SYSTEM_LOG = "log/system.log"


class SystemMessages:
    """System status messages"""
    CACHE_INITIALIZED = " Cache system initialized"
    EMBEDDING_READY = " Embedding system ready"
    RECOVERY_SUCCESS = " Recovery completed successfully"
    SYSTEM_READY = " System ready for operation"
    
    CACHE_ERROR = " Cache error occurred"
    EMBEDDING_ERROR = " Embedding error occurred"
    RECOVERY_ERROR = " Recovery failed"
    SYSTEM_ERROR = " System error occurred"

