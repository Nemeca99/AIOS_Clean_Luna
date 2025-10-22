#!/usr/bin/env python3
"""
Dream Core Functions - Modular function library for Dream system
All core functionality separated into clean, focused modules
"""

from .dream_cycles import DreamCycleManager
from .meditation import MeditationManager
from .memory_consolidation import MemoryConsolidationManager
from .middleware import DreamStateMiddleware, create_dream_middleware
from .config_loader import get_main_model, get_embedder_model, get_draft_model

__all__ = [
    'DreamCycleManager',
    'MeditationManager',
    'MemoryConsolidationManager',
    'DreamStateMiddleware',
    'create_dream_middleware',
    'get_main_model',
    'get_embedder_model',
    'get_draft_model'
]

