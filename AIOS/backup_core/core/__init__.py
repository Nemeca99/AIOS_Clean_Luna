#!/usr/bin/env python3
"""
BACKUP CORE - Core Module Components
Git-like version control system for AIOS Clean
"""

# Use relative imports since this is a subpackage
try:
    from .objects import ObjectStore, GitObject, BlobObject, TreeObject, CommitObject
    from .refs import RefManager
    from .staging import StagingArea
    from .commits import CommitManager
    from .branches import BranchManager
    from .diff import DiffEngine
    from .file_ops import FileOperations
    from .config import BackupConfig
except ImportError:
    # Fallback for different import contexts
    from objects import ObjectStore, GitObject, BlobObject, TreeObject, CommitObject
    from refs import RefManager
    from staging import StagingArea
    from commits import CommitManager
    from branches import BranchManager
    from diff import DiffEngine
    from file_ops import FileOperations
    from config import BackupConfig

__all__ = [
    'ObjectStore',
    'GitObject',
    'BlobObject',
    'TreeObject',
    'CommitObject',
    'RefManager',
    'StagingArea',
    'CommitManager',
    'BranchManager',
    'DiffEngine',
    'FileOperations',
    'BackupConfig',
]

