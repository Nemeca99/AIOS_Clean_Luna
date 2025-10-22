"""
Template Core - Reference Plugin Implementation

Copy this folder and modify it to create your own AIOS core!

This template shows:
- How to structure a core plugin
- How to implement handle_command()
- How to add configuration
- How to add logging
- How to make it OS-independent
"""

from .template_core import handle_command, get_commands, TemplateCore

__all__ = ['handle_command', 'get_commands', 'TemplateCore']

