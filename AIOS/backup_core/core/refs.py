#!/usr/bin/env python3
"""
Reference Management System - Git-like refs, branches, tags, and HEAD
Manages refs/heads/, refs/tags/, and HEAD pointer
"""

from pathlib import Path
from typing import Optional, List, Dict


class RefManager:
    """
    Manages Git-like references (branches, tags, HEAD)
    """
    
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.refs_dir = repo_dir / "refs"
        self.heads_dir = self.refs_dir / "heads"
        self.tags_dir = self.refs_dir / "tags"
        self.head_file = repo_dir / "HEAD"
        
        # Create directory structure
        self.heads_dir.mkdir(parents=True, exist_ok=True)
        self.tags_dir.mkdir(parents=True, exist_ok=True)
    
    # ===== HEAD Management =====
    
    def get_head(self) -> Optional[str]:
        """
        Get current HEAD
        Returns: commit hash or branch ref (e.g., "refs/heads/main")
        """
        if not self.head_file.exists():
            return None
        
        with open(self.head_file, 'r') as f:
            return f.read().strip()
    
    def set_head(self, ref: str):
        """
        Set HEAD to a ref or commit hash
        Args:
            ref: Branch ref (refs/heads/main) or commit hash
        """
        with open(self.head_file, 'w') as f:
            f.write(ref)
    
    def get_head_commit(self) -> Optional[str]:
        """
        Resolve HEAD to actual commit hash
        Returns: commit hash or None
        """
        head = self.get_head()
        if not head:
            return None
        
        # If HEAD points to a branch
        if head.startswith("refs/heads/"):
            branch_name = head.replace("refs/heads/", "")
            return self.get_branch_commit(branch_name)
        
        # HEAD is detached (points directly to commit)
        return head
    
    def is_detached(self) -> bool:
        """Check if HEAD is detached (not pointing to a branch)"""
        head = self.get_head()
        if not head:
            return True
        return not head.startswith("refs/heads/")
    
    def get_current_branch(self) -> Optional[str]:
        """Get current branch name, or None if detached"""
        head = self.get_head()
        if head and head.startswith("refs/heads/"):
            return head.replace("refs/heads/", "")
        return None
    
    # ===== Branch Management =====
    
    def create_branch(self, branch_name: str, commit_hash: str):
        """Create a new branch pointing to commit"""
        branch_file = self.heads_dir / branch_name
        with open(branch_file, 'w') as f:
            f.write(commit_hash)
    
    def delete_branch(self, branch_name: str):
        """Delete a branch"""
        branch_file = self.heads_dir / branch_name
        if branch_file.exists():
            branch_file.unlink()
    
    def rename_branch(self, old_name: str, new_name: str):
        """Rename a branch"""
        old_file = self.heads_dir / old_name
        new_file = self.heads_dir / new_name
        
        if old_file.exists():
            commit_hash = self.get_branch_commit(old_name)
            self.create_branch(new_name, commit_hash)
            self.delete_branch(old_name)
            
            # Update HEAD if on renamed branch
            if self.get_current_branch() == old_name:
                self.set_head(f"refs/heads/{new_name}")
    
    def branch_exists(self, branch_name: str) -> bool:
        """Check if branch exists"""
        return (self.heads_dir / branch_name).exists()
    
    def get_branch_commit(self, branch_name: str) -> Optional[str]:
        """Get commit hash that branch points to"""
        branch_file = self.heads_dir / branch_name
        if not branch_file.exists():
            return None
        
        with open(branch_file, 'r') as f:
            return f.read().strip()
    
    def update_branch(self, branch_name: str, commit_hash: str):
        """Update branch to point to new commit"""
        self.create_branch(branch_name, commit_hash)
    
    def list_branches(self) -> List[str]:
        """List all branches"""
        branches = []
        if self.heads_dir.exists():
            for branch_file in self.heads_dir.iterdir():
                if branch_file.is_file():
                    branches.append(branch_file.name)
        return sorted(branches)
    
    def get_all_branches_with_commits(self) -> Dict[str, str]:
        """Get all branches with their commit hashes"""
        branches = {}
        for branch_name in self.list_branches():
            commit = self.get_branch_commit(branch_name)
            if commit:
                branches[branch_name] = commit
        return branches
    
    # ===== Tag Management =====
    
    def create_tag(self, tag_name: str, commit_hash: str):
        """Create a tag pointing to commit"""
        tag_file = self.tags_dir / tag_name
        with open(tag_file, 'w') as f:
            f.write(commit_hash)
    
    def delete_tag(self, tag_name: str):
        """Delete a tag"""
        tag_file = self.tags_dir / tag_name
        if tag_file.exists():
            tag_file.unlink()
    
    def tag_exists(self, tag_name: str) -> bool:
        """Check if tag exists"""
        return (self.tags_dir / tag_name).exists()
    
    def get_tag_commit(self, tag_name: str) -> Optional[str]:
        """Get commit hash that tag points to"""
        tag_file = self.tags_dir / tag_name
        if not tag_file.exists():
            return None
        
        with open(tag_file, 'r') as f:
            return f.read().strip()
    
    def list_tags(self) -> List[str]:
        """List all tags"""
        tags = []
        if self.tags_dir.exists():
            for tag_file in self.tags_dir.iterdir():
                if tag_file.is_file():
                    tags.append(tag_file.name)
        return sorted(tags)
    
    def get_all_tags_with_commits(self) -> Dict[str, str]:
        """Get all tags with their commit hashes"""
        tags = {}
        for tag_name in self.list_tags():
            commit = self.get_tag_commit(tag_name)
            if commit:
                tags[tag_name] = commit
        return tags
    
    # ===== Utility Methods =====
    
    def resolve_ref(self, ref: str) -> Optional[str]:
        """
        Resolve a reference to commit hash
        Accepts: branch name, tag name, commit hash, or HEAD
        """
        # Try HEAD
        if ref.lower() == "head":
            return self.get_head_commit()
        
        # Try branch
        if self.branch_exists(ref):
            return self.get_branch_commit(ref)
        
        # Try tag
        if self.tag_exists(ref):
            return self.get_tag_commit(ref)
        
        # Assume it's a commit hash
        # TODO: Validate commit hash exists in object store
        return ref
    
    def get_ref_info(self) -> Dict[str, any]:
        """Get comprehensive ref information"""
        return {
            'head': self.get_head(),
            'head_commit': self.get_head_commit(),
            'current_branch': self.get_current_branch(),
            'is_detached': self.is_detached(),
            'branches': self.get_all_branches_with_commits(),
            'tags': self.get_all_tags_with_commits()
        }

