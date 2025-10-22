"""
Music Core - AI-Controlled Music System

Gives AI the ability to:
- Play music from your library
- Create playlists
- Learn your preferences
- Suggest music based on mood
- Remember what you like
"""

from .music_core import handle_command, get_commands, MusicCore

__all__ = ['handle_command', 'get_commands', 'MusicCore']


