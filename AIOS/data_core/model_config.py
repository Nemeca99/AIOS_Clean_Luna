#!/usr/bin/env python3
"""
Data Core Model Configuration
Self-contained model configuration for Data core
"""

import sys
from pathlib import Path

# Add parent directory to path to access main model config
sys.path.append(str(Path(__file__).parent.parent))

# Use local config file
from model_config_loader import ModelConfigLoader

# Load from local config (now in system/config)
_config_loader = ModelConfigLoader(str(Path(__file__).parent / "system" / "config" / "model_config.json"))

def get_main_model():
    return _config_loader.get_main_model()

def get_embedder_model():
    return _config_loader.get_embedder_model()

def get_draft_model():
    return _config_loader.get_draft_model()

# Re-export for easy access within Data core
__all__ = ['get_main_model', 'get_embedder_model', 'get_draft_model']

# Convenience functions for Data-specific model access
def get_data_embedder_model():
    """Get the embedder model for Data operations"""
    return get_embedder_model()

def get_data_main_model():
    """Get the main model for Data operations"""
    return get_main_model()
