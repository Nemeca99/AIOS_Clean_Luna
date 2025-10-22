#!/usr/bin/env python3
"""
BACKUP CORE SYSTEM - Git-like Version Control for AIOS
Full-featured version control with commits, branches, and history
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

from typing import Dict, List, Optional, Any
from datetime import datetime

# Import all core modules
from .core.objects import ObjectStore
from .core.refs import RefManager
from .core.staging import StagingArea
from .core.commits import CommitManager
from .core.branches import BranchManager
from .core.diff import DiffEngine
from .core.file_ops import FileOperations
from .core.config import BackupConfig


class BackupCore:
    """
    Git-like backup and version control system for AIOS Clean.
    
    Features:
    - Content-addressable object storage
    - Full commit history
    - Branching and merging
    - Staging area
    - Diff and status tracking
    - Tag support
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize the backup core system.
        
        Args:
            workspace_root: Root directory of workspace (defaults to parent of backup_core)
        """
        # Determine paths
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent
        
        self.workspace_root = Path(workspace_root)
        self.repo_dir = self.workspace_root / ".aios_backup"
        
        # Initialize repository if needed
        self._init_repository()
        
        # Initialize all components
        self.object_store = ObjectStore(self.repo_dir)
        self.ref_manager = RefManager(self.repo_dir)
        self.staging_area = StagingArea(self.repo_dir)
        self.file_ops = FileOperations(self.workspace_root)
        self.config = BackupConfig(self.repo_dir)
        
        # Initialize managers
        self.commit_manager = CommitManager(
            self.repo_dir,
            self.object_store,
            self.ref_manager,
            self.staging_area
        )
        
        self.branch_manager = BranchManager(
            self.repo_dir,
            self.object_store,
            self.ref_manager,
            self.commit_manager,
            self.staging_area
        )
        
        self.diff_engine = DiffEngine(
            self.workspace_root,
            self.repo_dir,
            self.object_store,
            self.ref_manager,
            self.staging_area,
            self.file_ops
        )
        
        print(f"🔒 AIOS Backup Core (Git-like)")
        print(f"   Repository: {self.repo_dir}")
        
        # Show current branch/commit
        current_branch = self.ref_manager.get_current_branch()
        if current_branch:
            print(f"   Branch: {current_branch}")
        else:
            head_commit = self.ref_manager.get_head_commit()
            if head_commit:
                print(f"   Detached HEAD: {head_commit[:8]}")
            else:
                print(f"   No commits yet")
    
    def _init_repository(self):
        """Initialize repository structure if it doesn't exist"""
        if not self.repo_dir.exists():
            print(f"📁 Initializing new repository...")
            
            # Create directory structure
            self.repo_dir.mkdir(parents=True, exist_ok=True)
            (self.repo_dir / "objects").mkdir(exist_ok=True)
            (self.repo_dir / "refs" / "heads").mkdir(parents=True, exist_ok=True)
            (self.repo_dir / "refs" / "tags").mkdir(parents=True, exist_ok=True)
            
            # Create HEAD pointing to main branch
            head_file = self.repo_dir / "HEAD"
            with open(head_file, 'w') as f:
                f.write("refs/heads/main")
            
            print(f"✅ Repository initialized")
    
    # ===== Staging Operations =====
    
    def add(self, paths: Optional[List[str]] = None, all_files: bool = False):
        """
        Add files to staging area.
        
        Args:
            paths: List of file/directory paths to add
            all_files: Add all files in workspace
        """
        if all_files:
            # Add all files
            files_to_add = self.file_ops.get_all_files()
        elif paths:
            # Add specified paths
            path_objs = [Path(p) for p in paths]
            files_to_add = self.file_ops.get_files_in_paths(path_objs)
        else:
            print("⚠️ No files specified. Use all_files=True or provide paths")
            return
        
        if not files_to_add:
            print("⚠️ No files to add")
            return
        
        print(f"📦 Staging {len(files_to_add)} files...")
        
        added_count = 0
        for file_path in files_to_add:
            try:
                # Create blob and add to staging
                blob_hash = self.object_store.write_blob_from_file(
                    self.workspace_root / file_path
                )
                mode = self.file_ops.get_file_mode(file_path)
                self.staging_area.add(str(file_path), blob_hash, mode)
                added_count += 1
            except Exception as e:
                print(f"⚠️ Could not stage {file_path}: {e}")
        
        print(f"✅ Staged {added_count} files")
    
    def unstage(self, file_path: str):
        """Remove file from staging area"""
        self.staging_area.remove(file_path)
        print(f"✅ Unstaged: {file_path}")
    
    def unstage_all(self):
        """Remove all files from staging area"""
        self.staging_area.clear()
        print(f"✅ Cleared staging area")
    
    # ===== Commit Operations =====
    
    def commit(self, message: str, author: Optional[str] = None) -> Optional[str]:
        """
        Create a commit from staged files.
        
        Args:
            message: Commit message
            author: Commit author (defaults to config)
        
        Returns:
            Commit hash or None
        """
        if author is None:
            author = self.config.get_author_name()
        
        return self.commit_manager.create_commit(message, author)
    
    def log(self, max_count: Optional[int] = 20):
        """Show commit history"""
        commits = self.commit_manager.get_commit_history(max_count=max_count)
        
        if not commits:
            print("No commits yet")
            return
        
        formatted_log = self.commit_manager.format_commit_log(commits)
        print(formatted_log)
    
    def show(self, commit_hash: Optional[str] = None):
        """Show commit details"""
        if commit_hash is None:
            commit_hash = self.ref_manager.get_head_commit()
        
        if not commit_hash:
            print("No commits yet")
            return
        
        # Get commit info
        info = self.commit_manager.get_commit_info(commit_hash)
        if not info:
            print(f"❌ Commit not found: {commit_hash}")
            return
        
        # Print commit details
        print(f"commit {commit_hash}")
        print(f"Author: {info['author']}")
        print(f"Date:   {info['date']}")
        print()
        print(f"    {info['message']}")
        print()
        
        # Show files changed
        files = self.commit_manager.get_commit_diff_files(commit_hash)
        if files:
            print(f"Files changed: {len(files)}")
            for file_path in files[:10]:  # Show first 10
                print(f"    {file_path}")
            if len(files) > 10:
                print(f"    ... and {len(files) - 10} more")
    
    # ===== Branch Operations =====
    
    def branch_create(self, branch_name: str, start_point: Optional[str] = None) -> bool:
        """Create a new branch"""
        return self.branch_manager.create(branch_name, start_point)
    
    def branch_delete(self, branch_name: str, force: bool = False) -> bool:
        """Delete a branch"""
        return self.branch_manager.delete(branch_name, force)
    
    def branch_rename(self, old_name: str, new_name: str) -> bool:
        """Rename a branch"""
        return self.branch_manager.rename(old_name, new_name)
    
    def branch_switch(self, branch_name: str, create: bool = False) -> bool:
        """Switch to a different branch"""
        return self.branch_manager.switch(branch_name, create)
    
    def branch_list(self, verbose: bool = False):
        """List all branches"""
        branches = self.branch_manager.list(verbose)
        formatted = self.branch_manager.format_branch_list(branches)
        print(formatted)
    
    def branch_merge(self, branch_name: str, message: Optional[str] = None) -> bool:
        """Merge branch into current branch"""
        return self.branch_manager.merge(branch_name, message)
    
    # ===== Status and Diff Operations =====
    
    def status(self):
        """Show working directory status"""
        status_dict = self.diff_engine.get_status()
        formatted = self.diff_engine.format_status(status_dict)
        print(formatted)
    
    def diff(self, file_path: Optional[str] = None, cached: bool = False):
        """Show file changes"""
        if file_path:
            # Show diff for specific file
            diff_text = self.diff_engine.get_diff(file_path, cached)
            if diff_text:
                print(diff_text)
            else:
                print(f"No changes to show for {file_path}")
        else:
            # Show status instead
            self.status()
    
    # ===== Tag Operations =====
    
    def tag_create(self, tag_name: str, commit_hash: Optional[str] = None):
        """
        Create a tag at commit.
        
        Args:
            tag_name: Name of tag
            commit_hash: Commit to tag (defaults to HEAD)
        """
        if commit_hash is None:
            commit_hash = self.ref_manager.get_head_commit()
        
        if not commit_hash:
            print("❌ No commits to tag")
            return
        
        self.ref_manager.create_tag(tag_name, commit_hash)
        print(f"✅ Created tag: {tag_name} → {commit_hash[:8]}")
    
    def tag_delete(self, tag_name: str):
        """Delete a tag"""
        self.ref_manager.delete_tag(tag_name)
        print(f"✅ Deleted tag: {tag_name}")
    
    def tag_list(self):
        """List all tags"""
        tags = self.ref_manager.get_all_tags_with_commits()
        
        if not tags:
            print("No tags")
            return
        
        for tag_name, commit_hash in sorted(tags.items()):
            print(f"  {tag_name} → {commit_hash[:8]}")
    
    # ===== Checkout and Restore Operations =====
    
    def checkout(self, ref: str):
        """
        Checkout a commit, branch, or tag.
        
        Args:
            ref: Branch name, tag name, or commit hash
        """
        # Resolve reference
        commit_hash = self.ref_manager.resolve_ref(ref)
        
        if not commit_hash:
            print(f"❌ Could not resolve reference: {ref}")
            return
        
        # Check if it's a branch
        if self.ref_manager.branch_exists(ref):
            # Switch to branch
            self.branch_manager.switch(ref)
        else:
            # Detached HEAD checkout
            self.ref_manager.set_head(commit_hash)
            print(f"✅ Checked out commit: {commit_hash[:8]}")
            print(f"   HEAD is now detached")
    
    # ===== Information and Statistics =====
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        obj_stats = self.object_store.get_stats()
        diff_stats = self.diff_engine.get_stats()
        ref_info = self.ref_manager.get_ref_info()
        
        return {
            'repository_type': 'Git-like Version Control',
            'repository_path': str(self.repo_dir),
            'workspace_root': str(self.workspace_root),
            'current_branch': ref_info['current_branch'],
            'current_commit': ref_info['head_commit'],
            'is_detached': ref_info['is_detached'],
            'total_commits': obj_stats['commits'],
            'total_objects': obj_stats['total_objects'],
            'total_blobs': obj_stats['blobs'],
            'total_trees': obj_stats['trees'],
            'storage_size_bytes': obj_stats['total_size_bytes'],
            'branches': list(ref_info['branches'].keys()),
            'tags': list(ref_info['tags'].keys()),
            'staged_files': diff_stats['staged_count'],
            'modified_files': diff_stats['modified_count'],
            'untracked_files': diff_stats['untracked_count'],
            'working_dir_clean': diff_stats['is_clean']
        }
    
    def info(self):
        """Print system information"""
        info = self.get_system_info()
        
        print("\n=== AIOS Backup System Info ===")
        print(f"Type: {info['repository_type']}")
        print(f"Repository: {info['repository_path']}")
        print(f"Workspace: {info['workspace_root']}")
        print()
        print(f"Current Branch: {info['current_branch'] or '(detached)'}")
        if info['current_commit']:
            print(f"Current Commit: {info['current_commit'][:8]}")
        print()
        print(f"Total Commits: {info['total_commits']}")
        print(f"Total Objects: {info['total_objects']}")
        print(f"  - Blobs: {info['total_blobs']}")
        print(f"  - Trees: {info['total_trees']}")
        print(f"  - Commits: {info['total_commits']}")
        print(f"Storage Size: {info['storage_size_bytes'] / 1024:.1f} KB")
        print()
        print(f"Branches: {len(info['branches'])}")
        for branch in info['branches']:
            print(f"  - {branch}")
        if info['tags']:
            print(f"Tags: {len(info['tags'])}")
            for tag in info['tags'][:5]:
                print(f"  - {tag}")
        print()
        print(f"Working Directory:")
        print(f"  Staged: {info['staged_files']}")
        print(f"  Modified: {info['modified_files']}")
        print(f"  Untracked: {info['untracked_files']}")
        print(f"  Clean: {info['working_dir_clean']}")
        print()
    
    # ===== Legacy Compatibility Methods =====
    
    def create_backup(self, backup_name: Optional[str] = None,
                     include_data: bool = True,
                     include_logs: bool = True,
                     include_config: bool = True,
                     incremental: bool = True) -> str:
        """
        Legacy method for compatibility with old backup system.
        Creates a commit with all files.
        
        Returns:
            Commit hash
        """
        print(f"🔄 Creating backup (legacy compatibility mode)...")
        
        # Stage all files
        self.add(all_files=True)
        
        # Create commit
        message = f"Backup: {backup_name or 'auto'} at {datetime.now().isoformat()}"
        commit_hash = self.commit(message)
        
        if commit_hash:
            print(f"✅ Backup created as commit: {commit_hash[:8]}")
            return commit_hash
        else:
            print(f"⚠️ No changes to backup")
            return ""


def handle_command(args: List[str]) -> bool:
    """
    Handle backup_core commands from main.py
    
    Commands:
    - --backup create [message] - Create new backup
    - --backup list - List all backups
    - --backup restore <commit> - Restore from backup
    - --backup status - Show backup status
    - --backup verify - Verify backup integrity
    """
    if not args or '--backup' not in args:
        return False
    
    try:
        backup = BackupCore()
        
        if 'create' in args:
            # Get message  
            msg_idx = args.index('create') + 1
            message = args[msg_idx] if msg_idx < len(args) else "Auto backup"
            
            print(f"Creating backup: {message}")
            
            # Use backup.add(all_files=True) which now respects .gitignore
            # This will scan all files but exclude patterns from .gitignore
            print(f"  Scanning files (respecting .gitignore)...")
            backup.add(all_files=True)
            
            commit_hash = backup.commit(message)
            
            if commit_hash:
                print(f"✅ Backup created: {commit_hash[:8]}")
            else:
                print(f"⚠️  No changes to backup")
            
            return True
        
        elif 'list' in args:
            print("Recent backups:")
            commits = backup.commit_manager.get_commit_history(max_count=10)
            if commits:
                for commit in commits:
                    commit_hash = commit.get('hash', '')[:8]
                    message = commit.get('message', 'No message')
                    timestamp = commit.get('timestamp', '')
                    print(f"  {commit_hash} - {message} ({timestamp})")
            else:
                print("  No backups yet")
            return True
        
        elif 'status' in args:
            backup.info()
            return True
        
        elif 'verify' in args:
            print("Verifying backup integrity...")
            # Check if backup directory exists and has commits
            backup_dir = backup.repo_dir
            if backup_dir.exists():
                commit_count = len(list((backup_dir / "objects").glob("*/*"))) if (backup_dir / "objects").exists() else 0
                print(f"  Backup directory: {backup_dir}")
                print(f"  Objects: {commit_count}")
                print(f"  ✅ Backup core operational")
            else:
                print(f"  ⚠️  Backup directory not initialized")
            return True
        
        else:
            print("Backup Core Commands:")
            print("  --backup create [message] - Create new backup")
            print("  --backup list - List all backups")
            print("  --backup status - Show backup status")
            print("  --backup verify - Verify backup integrity")
            return True
    
    except Exception as e:
        print(f"Backup core error: {e}")
        return True


if __name__ == "__main__":
    # Test the backup system
    backup = BackupCore()
    backup.info()
