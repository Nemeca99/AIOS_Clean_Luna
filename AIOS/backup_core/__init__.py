#!/usr/bin/env python3
"""
BACKUP CORE MODULE - AIOS Clean Git-like Version Control System

A full-featured version control system inspired by Git, providing:
- Content-addressable object storage
- Commit history and branching
- Staging area for selective commits
- Diff and status tracking
- Tag support for versioning

Both Python and Rust implementations available.
"""

__version__ = "2.0.0"
__author__ = "AIOS Team"

from .backup_core import BackupCore, handle_command
from .hybrid_backup_core import HybridBackupCore

__all__ = ['BackupCore', 'HybridBackupCore', 'handle_command', '__version__']
