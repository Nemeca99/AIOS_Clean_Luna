#!/usr/bin/env python3
"""
STREAMLIT CORE - AIOS Dashboard System
========================================

Self-contained UI system for AIOS.
Provides dashboard, chat interface, and CodeGraph viewer.

Author: AIOS Development Team
Version: 1.0.0
"""

from .streamlit_core import StreamlitCore, main, handle_command, get_commands

__all__ = ['StreamlitCore', 'main', 'handle_command', 'get_commands']

