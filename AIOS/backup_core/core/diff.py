#!/usr/bin/env python3
"""
Diff Engine - Git-like diff and status operations
Show file changes, working directory status, and diffs
"""

from pathlib import Path
from typing import List, Dict, Set, Optional, Any
from enum import Enum

from .objects import ObjectStore
from .refs import RefManager
from .staging import StagingArea
from .file_ops import FileOperations


class FileStatus(Enum):
    """File status in working directory"""
    UNTRACKED = "untracked"      # New file, never committed
    MODIFIED = "modified"          # File changed since last commit
    STAGED = "staged"              # File staged for commit
    DELETED = "deleted"            # File deleted from working directory
    UNMODIFIED = "unmodified"      # File unchanged


class DiffEngine:
    """
    Handles diff and status operations
    """
    
    def __init__(self, workspace_root: Path, repo_dir: Path,
                 object_store: ObjectStore, ref_manager: RefManager,
                 staging_area: StagingArea, file_ops: FileOperations):
        self.workspace_root = workspace_root
        self.repo_dir = repo_dir
        self.object_store = object_store
        self.ref_manager = ref_manager
        self.staging_area = staging_area
        self.file_ops = file_ops
    
    def get_status(self) -> Dict[str, List[str]]:
        """
        Get working directory status (like git status)
        Returns files categorized by status
        """
        status = {
            'staged': [],
            'modified': [],
            'untracked': [],
            'deleted': []
        }
        
        # Get all files in working directory
        working_files = set(str(f) for f in self.file_ops.get_all_files())
        
        # Get files from last commit
        committed_files = {}
        head_commit = self.ref_manager.get_head_commit()
        if head_commit:
            committed_files = self._get_commit_files(head_commit)
        
        # Get staged files
        staged_files = self.staging_area.get_staged_files()
        
        # Check staged files
        for file_path in staged_files:
            status['staged'].append(file_path)
        
        # Check working files
        for file_path in working_files:
            # Skip if already staged
            if file_path in staged_files:
                continue
            
            # Check if modified from last commit
            if file_path in committed_files:
                # File exists in last commit - check if modified
                current_hash = self._get_file_hash(Path(file_path))
                if current_hash != committed_files[file_path]:
                    status['modified'].append(file_path)
            else:
                # File doesn't exist in last commit - untracked
                status['untracked'].append(file_path)
        
        # Check for deleted files
        for file_path in committed_files:
            if file_path not in working_files and file_path not in staged_files:
                status['deleted'].append(file_path)
        
        # Sort all lists
        for key in status:
            status[key] = sorted(status[key])
        
        return status
    
    def _get_commit_files(self, commit_hash: str) -> Dict[str, str]:
        """
        Get all files from a commit
        Returns: {file_path: blob_hash}
        """
        files = {}
        
        # Get commit metadata
        metadata = self.object_store.get_commit_metadata(commit_hash)
        if not metadata:
            return files
        
        # Get tree
        tree_hash = metadata.get('tree')
        if not tree_hash:
            return files
        
        # Get tree entries
        entries = self.object_store.get_tree_entries(tree_hash)
        if not entries:
            return files
        
        # Build file map
        for entry in entries:
            files[entry['name']] = entry['hash']
        
        return files
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file in working directory"""
        import hashlib
        
        full_path = self.workspace_root / file_path
        if not full_path.exists():
            return ""
        
        try:
            content = self.file_ops.read_file(file_path)
            # Use same hashing as blob objects
            header = f"blob {len(content)}\0".encode()
            return hashlib.sha256(header + content).hexdigest()
        except Exception:
            return ""
    
    def format_status(self, status: Dict[str, List[str]]) -> str:
        """Format status output (like git status)"""
        lines = []
        
        # Current branch
        current_branch = self.ref_manager.get_current_branch()
        if current_branch:
            lines.append(f"On branch: {current_branch}")
        else:
            head_commit = self.ref_manager.get_head_commit()
            if head_commit:
                lines.append(f"HEAD detached at {head_commit[:8]}")
            else:
                lines.append("No commits yet")
        
        lines.append("")
        
        # Staged changes
        if status['staged']:
            lines.append("Changes to be committed:")
            lines.append("  (use 'unstage <file>' to unstage)")
            lines.append("")
            for file_path in status['staged']:
                lines.append(f"    staged:     {file_path}")
            lines.append("")
        
        # Modified files
        if status['modified']:
            lines.append("Changes not staged for commit:")
            lines.append("  (use 'add <file>' to stage changes)")
            lines.append("")
            for file_path in status['modified']:
                lines.append(f"    modified:   {file_path}")
            lines.append("")
        
        # Deleted files
        if status['deleted']:
            lines.append("Deleted files:")
            lines.append("")
            for file_path in status['deleted']:
                lines.append(f"    deleted:    {file_path}")
            lines.append("")
        
        # Untracked files
        if status['untracked']:
            lines.append("Untracked files:")
            lines.append("  (use 'add <file>' to track)")
            lines.append("")
            for file_path in status['untracked']:
                lines.append(f"    untracked:  {file_path}")
            lines.append("")
        
        # Summary
        if not any(status.values()):
            lines.append("Working directory clean")
        
        return '\n'.join(lines)
    
    def get_diff(self, file_path: str, cached: bool = False) -> Optional[str]:
        """
        Get diff for a file
        Args:
            file_path: Path to file
            cached: Show diff of staged changes (vs unstaged)
        Returns:
            Diff string or None
        """
        # Get current file content
        current_content = ""
        full_path = self.workspace_root / file_path
        if full_path.exists():
            try:
                current_content = self.file_ops.read_file(Path(file_path)).decode('utf-8', errors='replace')
            except Exception:
                return None
        
        # Get comparison content
        if cached:
            # Compare staged vs last commit
            old_content = self._get_committed_file_content(file_path)
        else:
            # Compare working vs staged (or last commit if not staged)
            if self.staging_area.is_staged(file_path):
                old_hash = self.staging_area.get_file_hash(file_path)
                old_content_bytes = self.object_store.get_blob_content(old_hash)
                old_content = old_content_bytes.decode('utf-8', errors='replace') if old_content_bytes else ""
            else:
                old_content = self._get_committed_file_content(file_path)
        
        # Generate simple diff
        return self._simple_diff(file_path, old_content, current_content)
    
    def _get_committed_file_content(self, file_path: str) -> str:
        """Get file content from last commit"""
        head_commit = self.ref_manager.get_head_commit()
        if not head_commit:
            return ""
        
        files = self._get_commit_files(head_commit)
        if file_path not in files:
            return ""
        
        blob_hash = files[file_path]
        content_bytes = self.object_store.get_blob_content(blob_hash)
        return content_bytes.decode('utf-8', errors='replace') if content_bytes else ""
    
    def _simple_diff(self, file_path: str, old_content: str, new_content: str) -> str:
        """Generate simple unified diff"""
        lines = []
        
        lines.append(f"diff --aios a/{file_path} b/{file_path}")
        lines.append(f"--- a/{file_path}")
        lines.append(f"+++ b/{file_path}")
        
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        # Simple line-by-line comparison
        max_lines = max(len(old_lines), len(new_lines))
        
        for i in range(max_lines):
            if i < len(old_lines) and i < len(new_lines):
                if old_lines[i] != new_lines[i]:
                    lines.append(f"- {old_lines[i]}")
                    lines.append(f"+ {new_lines[i]}")
            elif i < len(old_lines):
                lines.append(f"- {old_lines[i]}")
            else:
                lines.append(f"+ {new_lines[i]}")
        
        return '\n'.join(lines)
    
    def get_commit_diff(self, commit_hash: str, parent_commit: Optional[str] = None) -> Dict[str, str]:
        """
        Get diff between commit and its parent
        Returns: {file_path: diff_string}
        """
        # Get parent if not specified
        if parent_commit is None:
            metadata = self.object_store.get_commit_metadata(commit_hash)
            if metadata and metadata.get('parents'):
                parent_commit = metadata['parents'][0]
        
        # Get files from both commits
        current_files = self._get_commit_files(commit_hash)
        parent_files = self._get_commit_files(parent_commit) if parent_commit else {}
        
        # Find changed files
        all_files = set(current_files.keys()) | set(parent_files.keys())
        
        diffs = {}
        for file_path in sorted(all_files):
            old_hash = parent_files.get(file_path)
            new_hash = current_files.get(file_path)
            
            if old_hash != new_hash:
                # File changed
                old_content = ""
                if old_hash:
                    content_bytes = self.object_store.get_blob_content(old_hash)
                    old_content = content_bytes.decode('utf-8', errors='replace') if content_bytes else ""
                
                new_content = ""
                if new_hash:
                    content_bytes = self.object_store.get_blob_content(new_hash)
                    new_content = content_bytes.decode('utf-8', errors='replace') if content_bytes else ""
                
                diffs[file_path] = self._simple_diff(file_path, old_content, new_content)
        
        return diffs
    
    def get_stats(self) -> Dict[str, Any]:
        """Get diff/status statistics"""
        status = self.get_status()
        
        return {
            'staged_count': len(status['staged']),
            'modified_count': len(status['modified']),
            'untracked_count': len(status['untracked']),
            'deleted_count': len(status['deleted']),
            'total_changes': sum(len(v) for v in status.values()),
            'is_clean': not any(status.values())
        }

