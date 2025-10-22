#!/usr/bin/env python3
"""
Branch Management - Git-like branching operations
Create, switch, merge, and manage branches
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from .objects import ObjectStore
from .refs import RefManager
from .commits import CommitManager
from .staging import StagingArea


class BranchManager:
    """
    Manages Git-like branches
    Handles branch creation, switching, merging, and deletion
    """
    
    def __init__(self, repo_dir: Path, object_store: ObjectStore,
                 ref_manager: RefManager, commit_manager: CommitManager,
                 staging_area: StagingArea):
        self.repo_dir = repo_dir
        self.object_store = object_store
        self.ref_manager = ref_manager
        self.commit_manager = commit_manager
        self.staging_area = staging_area
    
    def create(self, branch_name: str, start_point: Optional[str] = None) -> bool:
        """
        Create a new branch
        Args:
            branch_name: Name of the new branch
            start_point: Commit hash or ref to start from (defaults to HEAD)
        Returns:
            True if successful, False otherwise
        """
        # Check if branch already exists
        if self.ref_manager.branch_exists(branch_name):
            print(f"❌ Branch '{branch_name}' already exists")
            return False
        
        # Resolve start point
        if start_point is None:
            commit_hash = self.ref_manager.get_head_commit()
        else:
            commit_hash = self.ref_manager.resolve_ref(start_point)
        
        if not commit_hash:
            print(f"❌ Cannot create branch: no commits yet")
            return False
        
        # Create branch
        self.ref_manager.create_branch(branch_name, commit_hash)
        print(f"✅ Created branch: {branch_name}")
        print(f"   Starting from: {commit_hash[:8]}")
        
        return True
    
    def delete(self, branch_name: str, force: bool = False) -> bool:
        """
        Delete a branch
        Args:
            branch_name: Name of branch to delete
            force: Force deletion even if not merged
        Returns:
            True if successful, False otherwise
        """
        # Check if branch exists
        if not self.ref_manager.branch_exists(branch_name):
            print(f"❌ Branch '{branch_name}' does not exist")
            return False
        
        # Don't delete current branch
        current_branch = self.ref_manager.get_current_branch()
        if current_branch == branch_name:
            print(f"❌ Cannot delete current branch '{branch_name}'")
            print(f"   Switch to another branch first")
            return False
        
        # TODO: Check if branch is merged (unless force)
        if not force:
            # For now, skip merge check
            pass
        
        # Delete branch
        self.ref_manager.delete_branch(branch_name)
        print(f"✅ Deleted branch: {branch_name}")
        
        return True
    
    def rename(self, old_name: str, new_name: str) -> bool:
        """
        Rename a branch
        Args:
            old_name: Current branch name
            new_name: New branch name
        Returns:
            True if successful, False otherwise
        """
        # Check if old branch exists
        if not self.ref_manager.branch_exists(old_name):
            print(f"❌ Branch '{old_name}' does not exist")
            return False
        
        # Check if new name already exists
        if self.ref_manager.branch_exists(new_name):
            print(f"❌ Branch '{new_name}' already exists")
            return False
        
        # Rename
        self.ref_manager.rename_branch(old_name, new_name)
        print(f"✅ Renamed branch: {old_name} → {new_name}")
        
        return True
    
    def switch(self, branch_name: str, create: bool = False) -> bool:
        """
        Switch to a different branch
        Args:
            branch_name: Name of branch to switch to
            create: Create branch if it doesn't exist
        Returns:
            True if successful, False otherwise
        """
        # Check for uncommitted changes
        if not self.staging_area.is_empty():
            print(f"⚠️ Warning: You have staged changes")
            print(f"   Commit or unstage them before switching branches")
            return False
        
        # Create branch if requested
        if create and not self.ref_manager.branch_exists(branch_name):
            if not self.create(branch_name):
                return False
        
        # Check if branch exists
        if not self.ref_manager.branch_exists(branch_name):
            print(f"❌ Branch '{branch_name}' does not exist")
            if not create:
                print(f"   Use create=True to create it")
            return False
        
        # Switch HEAD to branch
        self.ref_manager.set_head(f"refs/heads/{branch_name}")
        print(f"✅ Switched to branch: {branch_name}")
        
        commit_hash = self.ref_manager.get_branch_commit(branch_name)
        if commit_hash:
            print(f"   At commit: {commit_hash[:8]}")
        
        return True
    
    def list(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        List all branches
        Args:
            verbose: Include detailed info
        Returns:
            List of branch information
        """
        branches = []
        current_branch = self.ref_manager.get_current_branch()
        
        for branch_name in self.ref_manager.list_branches():
            commit_hash = self.ref_manager.get_branch_commit(branch_name)
            
            branch_info = {
                'name': branch_name,
                'is_current': branch_name == current_branch,
                'commit': commit_hash,
                'short_commit': commit_hash[:8] if commit_hash else None
            }
            
            if verbose and commit_hash:
                commit_info = self.commit_manager.get_commit_info(commit_hash)
                if commit_info:
                    branch_info['commit_message'] = commit_info.get('message', '')
                    branch_info['commit_date'] = commit_info.get('date', '')
            
            branches.append(branch_info)
        
        return branches
    
    def format_branch_list(self, branches: List[Dict[str, Any]]) -> str:
        """Format branch list as readable output"""
        lines = []
        
        for branch in branches:
            prefix = "* " if branch['is_current'] else "  "
            name = branch['name']
            commit = branch['short_commit'] or '(no commits)'
            
            line = f"{prefix}{name} → {commit}"
            
            if 'commit_message' in branch:
                msg = branch['commit_message'].split('\n')[0]  # First line only
                line += f" - {msg}"
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def get_current(self) -> Optional[str]:
        """Get name of current branch"""
        return self.ref_manager.get_current_branch()
    
    def exists(self, branch_name: str) -> bool:
        """Check if branch exists"""
        return self.ref_manager.branch_exists(branch_name)
    
    def merge(self, branch_name: str, message: Optional[str] = None) -> bool:
        """
        Merge branch into current branch
        Simple fast-forward merge implementation
        Args:
            branch_name: Branch to merge
            message: Optional merge commit message
        Returns:
            True if successful, False otherwise
        """
        current_branch = self.ref_manager.get_current_branch()
        if not current_branch:
            print(f"❌ Not on a branch (detached HEAD)")
            return False
        
        if not self.ref_manager.branch_exists(branch_name):
            print(f"❌ Branch '{branch_name}' does not exist")
            return False
        
        # Get commits
        current_commit = self.ref_manager.get_branch_commit(current_branch)
        merge_commit = self.ref_manager.get_branch_commit(branch_name)
        
        if not merge_commit:
            print(f"❌ Branch '{branch_name}' has no commits")
            return False
        
        # Check if already up to date
        if current_commit == merge_commit:
            print(f"✅ Already up to date")
            return True
        
        # Check if fast-forward is possible
        if current_commit and not self.commit_manager.is_ancestor(current_commit, merge_commit):
            print(f"⚠️ Cannot fast-forward merge")
            print(f"   Advanced merge strategies not yet implemented")
            print(f"   Consider rebasing or using a different approach")
            return False
        
        # Fast-forward merge
        self.ref_manager.update_branch(current_branch, merge_commit)
        print(f"✅ Fast-forward merge: {branch_name} → {current_branch}")
        print(f"   New HEAD: {merge_commit[:8]}")
        
        return True
    
    def get_info(self, branch_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a branch"""
        if not self.ref_manager.branch_exists(branch_name):
            return None
        
        commit_hash = self.ref_manager.get_branch_commit(branch_name)
        
        info = {
            'name': branch_name,
            'commit': commit_hash,
            'is_current': branch_name == self.ref_manager.get_current_branch()
        }
        
        if commit_hash:
            info['short_commit'] = commit_hash[:8]
            commit_metadata = self.commit_manager.get_commit_info(commit_hash)
            if commit_metadata:
                info.update(commit_metadata)
            
            # Get commit count
            info['commit_count'] = self.commit_manager.count_commits(commit_hash)
        
        return info

