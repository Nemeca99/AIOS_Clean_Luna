#!/usr/bin/env python3
"""
Enterprise Core Model Configuration
Self-contained model configuration for Enterprise core
"""

import sys
from pathlib import Path

# Add parent directory to path to access main model config
sys.path.append(str(Path(__file__).parent.parent))

# Use local config file
from model_config_loader import ModelConfigLoader

# Load from local config
_config_loader = ModelConfigLoader(str(Path(__file__).parent / "config" / "model_config.json"))

def get_main_model():
    return _config_loader.get_main_model()

def get_embedder_model():
    return _config_loader.get_embedder_model()

def get_draft_model():
    return _config_loader.get_draft_model()

# Re-export for easy access within Enterprise core
__all__ = ['get_main_model', 'get_embedder_model', 'get_draft_model']
