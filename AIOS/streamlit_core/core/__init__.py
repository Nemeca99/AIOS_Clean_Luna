"""
Streamlit Core - Core Functionality Modules
============================================

This package contains the core functionality modules for the AIOS Streamlit UI system.
All modules are self-contained and link through streamlit_core.py orchestrator.

Modules:
- state_manager: Session and persistent state management
- meditation_engine: Meditation mode and session tracking
- ui_renderer: UI rendering for all interface components
- model_config_manager: Model configuration management
- dashboard_analytics: Quality dashboard analytics and metrics

Author: AIOS Development Team
Version: 1.0.0
"""

from .state_manager import StateManager
from .meditation_engine import MeditationEngine
from .ui_renderer import UIRenderer
from .model_config_manager import ModelConfigLoader, get_model_config_loader, get_main_model, get_embedder_model, get_draft_model
from .dashboard_analytics import DashboardAnalytics

__all__ = [
    'StateManager',
    'MeditationEngine',
    'UIRenderer',
    'ModelConfigLoader',
    'DashboardAnalytics',
    'get_model_config_loader',
    'get_main_model',
    'get_embedder_model',
    'get_draft_model'
]

