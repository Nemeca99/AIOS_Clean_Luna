"""
Privacy Core - Privacy Mode Management for AIOS

Handles:
- Semi-auto mode (default - conversation only)
- Full-auto mode (opt-in - passive monitoring)
- Privacy settings and consent
"""

from .privacy_core import handle_command, get_commands, PrivacyCore

__all__ = ['handle_command', 'get_commands', 'PrivacyCore']


