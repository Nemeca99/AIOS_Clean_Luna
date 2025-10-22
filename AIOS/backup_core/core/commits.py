#!/usr/bin/env python3
"""
Commit Management - Git-like commit operations
Create, read, and manage commits
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .objects import ObjectStore
from .refs import RefManager
from .staging import StagingArea


class CommitManager:
    """
    Manages Git-like commits
    Creates commits from staging area, tracks commit history
    """
    
    def __init__(self, repo_dir: Path, object_store: ObjectStore,
                 ref_manager: RefManager, staging_area: StagingArea):
        self.repo_dir = repo_dir
        self.object_store = object_store
        self.ref_manager = ref_manager
        self.staging_area = staging_area
    
    def create_commit(self, message: str, author: str = "AIOS") -> Optional[str]:
        """
        Create a new commit from staged files
        Args:
            message: Commit message
            author: Commit author
        Returns:
            Commit hash or None if nothing staged
        """
        # Check if anything is staged
        if self.staging_area.is_empty():
            print("⚠️ Nothing staged for commit")
            return None
        
        # Build tree from staging area
        tree_entries = self.staging_area.build_tree_entries()
        tree_hash = self.object_store.write_tree(tree_entries)
        
        # Get parent commit(s)
        parent_hashes = []
        current_commit = self.ref_manager.get_head_commit()
        if current_commit:
            parent_hashes.append(current_commit)
        
        # Create commit object
        commit_hash = self.object_store.write_commit(
            tree_hash=tree_hash,
            parent_hashes=parent_hashes,
            author=author,
            message=message
        )
        
        # Update current branch or HEAD
        current_branch = self.ref_manager.get_current_branch()
        if current_branch:
            # Update branch to point to new commit
            self.ref_manager.update_branch(current_branch, commit_hash)
        else:
            # Detached HEAD - update HEAD directly
            self.ref_manager.set_head(commit_hash)
        
        # Clear staging area
        self.staging_area.clear()
        
        print(f"✅ Created commit: {commit_hash[:8]}")
        print(f"   Message: {message}")
        print(f"   Author: {author}")
        print(f"   Files: {len(tree_entries)}")
        
        return commit_hash
    
    def get_commit_info(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get commit information"""
        return self.object_store.get_commit_metadata(commit_hash)
    
    def get_commit_tree(self, commit_hash: str) -> Optional[str]:
        """Get tree hash from commit"""
        metadata = self.get_commit_info(commit_hash)
        if metadata:
            return metadata.get('tree')
        return None
    
    def get_commit_parents(self, commit_hash: str) -> List[str]:
        """Get parent commit hashes"""
        metadata = self.get_commit_info(commit_hash)
        if metadata:
            return metadata.get('parents', [])
        return []
    
    def get_commit_history(self, start_commit: Optional[str] = None,
                          max_count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get commit history starting from a commit
        Args:
            start_commit: Starting commit hash (defaults to HEAD)
            max_count: Maximum number of commits to return
        Returns:
            List of commit metadata dictionaries
        """
        if start_commit is None:
            start_commit = self.ref_manager.get_head_commit()
        
        if not start_commit:
            return []
        
        history = []
        visited = set()
        to_visit = [start_commit]
        
        while to_visit and (max_count is None or len(history) < max_count):
            commit_hash = to_visit.pop(0)
            
            # Skip if already visited
            if commit_hash in visited:
                continue
            
            visited.add(commit_hash)
            
            # Get commit info
            commit_info = self.get_commit_info(commit_hash)
            if not commit_info:
                continue
            
            # Add to history with hash
            commit_info['hash'] = commit_hash
            commit_info['short_hash'] = commit_hash[:8]
            history.append(commit_info)
            
            # Add parents to visit queue
            parents = commit_info.get('parents', [])
            to_visit.extend(parents)
        
        return history
    
    def format_commit_log(self, commits: List[Dict[str, Any]]) -> str:
        """Format commit history as readable log"""
        lines = []
        
        for commit in commits:
            lines.append(f"commit {commit['hash']}")
            lines.append(f"Author: {commit['author']}")
            lines.append(f"Date:   {commit['date']}")
            lines.append("")
            
            # Indent message
            for msg_line in commit['message'].split('\n'):
                lines.append(f"    {msg_line}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_commit_diff_files(self, commit_hash: str) -> List[str]:
        """
        Get list of files changed in a commit
        Compares commit tree with parent tree
        """
        # Get commit tree
        tree_hash = self.get_commit_tree(commit_hash)
        if not tree_hash:
            return []
        
        current_files = set()
        tree_entries = self.object_store.get_tree_entries(tree_hash)
        if tree_entries:
            current_files = {entry['name'] for entry in tree_entries}
        
        # Get parent tree
        parents = self.get_commit_parents(commit_hash)
        parent_files = set()
        
        if parents:
            parent_tree_hash = self.get_commit_tree(parents[0])
            if parent_tree_hash:
                parent_entries = self.object_store.get_tree_entries(parent_tree_hash)
                if parent_entries:
                    parent_files = {entry['name'] for entry in parent_entries}
        
        # Find differences
        changed_files = list(current_files.symmetric_difference(parent_files))
        return sorted(changed_files)
    
    def is_ancestor(self, ancestor_hash: str, descendant_hash: str) -> bool:
        """
        Check if ancestor_hash is an ancestor of descendant_hash
        """
        if ancestor_hash == descendant_hash:
            return True
        
        # Walk back from descendant to see if we hit ancestor
        visited = set()
        to_visit = [descendant_hash]
        
        while to_visit:
            commit_hash = to_visit.pop(0)
            
            if commit_hash == ancestor_hash:
                return True
            
            if commit_hash in visited:
                continue
            
            visited.add(commit_hash)
            
            # Add parents
            parents = self.get_commit_parents(commit_hash)
            to_visit.extend(parents)
        
        return False
    
    def get_merge_base(self, commit1: str, commit2: str) -> Optional[str]:
        """
        Find common ancestor of two commits (merge base)
        Simple implementation - finds first common ancestor
        """
        # Get all ancestors of commit1
        ancestors1 = set()
        to_visit = [commit1]
        
        while to_visit:
            commit_hash = to_visit.pop(0)
            
            if commit_hash in ancestors1:
                continue
            
            ancestors1.add(commit_hash)
            
            parents = self.get_commit_parents(commit_hash)
            to_visit.extend(parents)
        
        # Walk commit2 ancestors until we find one in commit1's ancestors
        to_visit = [commit2]
        visited = set()
        
        while to_visit:
            commit_hash = to_visit.pop(0)
            
            if commit_hash in visited:
                continue
            
            visited.add(commit_hash)
            
            # Check if in commit1's ancestors
            if commit_hash in ancestors1:
                return commit_hash
            
            parents = self.get_commit_parents(commit_hash)
            to_visit.extend(parents)
        
        return None
    
    def count_commits(self, start_commit: Optional[str] = None) -> int:
        """Count total commits in history"""
        history = self.get_commit_history(start_commit)
        return len(history)

