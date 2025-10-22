#!/usr/bin/env python3
"""
Config Loader - Dream core configuration loading
Handles model configuration for the Dream system
"""

import sys
from pathlib import Path

# Add parent directory to path to access main model config
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from model_config_loader import ModelConfigLoader
except ImportError:
    print("⚠️ Warning: model_config_loader not found in parent directory")
    ModelConfigLoader = None

# Use local config file
_config_path = Path(__file__).parent.parent / "config" / "model_config.json"
_config_loader = ModelConfigLoader(str(_config_path)) if ModelConfigLoader else None


def get_main_model():
    """Get the main LLM model configuration."""
    if _config_loader:
        return _config_loader.get_main_model()
    return "llama-3.2-pkd-deckard-almost-human-abliterated-uncensored-7b-i1"


def get_embedder_model():
    """Get the embedder model configuration."""
    if _config_loader:
        return _config_loader.get_embedder_model()
    return "llama-3.2-1b-instruct-abliterated"


def get_draft_model():
    """Get the draft model configuration."""
    if _config_loader:
        return _config_loader.get_draft_model()
    return "mlabonne_qwen3-0.6b-abliterated"


def get_config_path():
    """Get the path to the configuration file."""
    return _config_path


# Re-export for easy access within Dream core
__all__ = ['get_main_model', 'get_embedder_model', 'get_draft_model', 'get_config_path']

