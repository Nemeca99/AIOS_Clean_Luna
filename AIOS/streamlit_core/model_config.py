#!/usr/bin/env python3
"""
Streamlit Core Model Configuration
===================================

Self-contained model configuration for Streamlit core module.
Uses internal model_config_manager from core package.

This module provides convenience functions for accessing model configuration
throughout the streamlit_core module.

Author: AIOS Development Team
Version: 1.0.0
"""

from pathlib import Path
from core.model_config_manager import ModelConfigLoader

# Load from local config
_config_loader = ModelConfigLoader(str(Path(__file__).parent / "config" / "model_config.json"))


def get_main_model() -> str:
    """Get the main LLM model name."""
    return _config_loader.get_main_model()


def get_embedder_model() -> str:
    """Get the embedder model name."""
    return _config_loader.get_embedder_model()


def get_draft_model() -> str:
    """Get the draft model name (if enabled)."""
    return _config_loader.get_draft_model()


def get_config_loader() -> ModelConfigLoader:
    """Get the config loader instance."""
    return _config_loader


# Re-export for easy access within Streamlit core
__all__ = ['get_main_model', 'get_embedder_model', 'get_draft_model', 'get_config_loader']
