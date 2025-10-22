#!/usr/bin/env python3
"""
HYBRID BACKUP CORE - Multi-Language Backup System
Automatically uses Rust implementation when available, falls back to Python
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add utils_core to path for rust_bridge
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils_core.bridges.rust_bridge import RustBridge, MultiLanguageCore
except ImportError:
    # Silently fall back to Python - Rust is optional
    RustBridge = None
    MultiLanguageCore = None

# Import original Python implementation
from backup_core import BackupCore


class HybridBackupCore:
    """
    Hybrid backup core that uses Rust when available, Python as fallback.
    Provides identical interface to original BackupCore.
    
    Note: Full Git-like features are currently Python-only.
    Rust implementation provides basic backup functionality.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize hybrid backup core."""
        # Initialize Python implementation (always available)
        self.python_implementation = BackupCore(workspace_root)
        
        # Initialize Rust bridge if available
        self.rust_bridge = None
        self.rust_available = False
        
        if RustBridge is not None:
            try:
                rust_path = Path(__file__).parent / "rust_backup"
                if rust_path.exists():
                    self.rust_bridge = RustBridge("backup", str(rust_path))
                    
                    # Try to compile and load Rust module
                    if self.rust_bridge.compile_rust_module():
                        if self.rust_bridge.load_rust_module():
                            self.rust_available = True
            except Exception as e:
                print(f"⚠️ Rust backup initialization failed: {e}")
                print("   Falling back to Python implementation")
        
        # Default to Python (Rust has limited Git features)
        self.current_implementation = "python"
        
        print(f"🔀 Hybrid Backup Core Initialized")
        print(f"   Python: Available ✅")
        print(f"   Rust: {'Available ✅' if self.rust_available else 'Not Available ❌'}")
        print(f"   Current: {self.current_implementation.upper()}")
    
    # ===== Pass-through methods to Python implementation =====
    # All Git-like methods use Python implementation
    
    def add(self, paths: Optional[List[str]] = None, all_files: bool = False):
        """Add files to staging area"""
        return self.python_implementation.add(paths, all_files)
    
    def unstage(self, file_path: str):
        """Remove file from staging area"""
        return self.python_implementation.unstage(file_path)
    
    def unstage_all(self):
        """Remove all files from staging area"""
        return self.python_implementation.unstage_all()
    
    def commit(self, message: str, author: Optional[str] = None) -> Optional[str]:
        """Create a commit from staged files"""
        return self.python_implementation.commit(message, author)
    
    def log(self, max_count: Optional[int] = 20):
        """Show commit history"""
        return self.python_implementation.log(max_count)
    
    def show(self, commit_hash: Optional[str] = None):
        """Show commit details"""
        return self.python_implementation.show(commit_hash)
    
    def branch_create(self, branch_name: str, start_point: Optional[str] = None) -> bool:
        """Create a new branch"""
        return self.python_implementation.branch_create(branch_name, start_point)
    
    def branch_delete(self, branch_name: str, force: bool = False) -> bool:
        """Delete a branch"""
        return self.python_implementation.branch_delete(branch_name, force)
    
    def branch_rename(self, old_name: str, new_name: str) -> bool:
        """Rename a branch"""
        return self.python_implementation.branch_rename(old_name, new_name)
    
    def branch_switch(self, branch_name: str, create: bool = False) -> bool:
        """Switch to a different branch"""
        return self.python_implementation.branch_switch(branch_name, create)
    
    def branch_list(self, verbose: bool = False):
        """List all branches"""
        return self.python_implementation.branch_list(verbose)
    
    def branch_merge(self, branch_name: str, message: Optional[str] = None) -> bool:
        """Merge branch into current branch"""
        return self.python_implementation.branch_merge(branch_name, message)
    
    def status(self):
        """Show working directory status"""
        return self.python_implementation.status()
    
    def diff(self, file_path: Optional[str] = None, cached: bool = False):
        """Show file changes"""
        return self.python_implementation.diff(file_path, cached)
    
    def tag_create(self, tag_name: str, commit_hash: Optional[str] = None):
        """Create a tag"""
        return self.python_implementation.tag_create(tag_name, commit_hash)
    
    def tag_delete(self, tag_name: str):
        """Delete a tag"""
        return self.python_implementation.tag_delete(tag_name)
    
    def tag_list(self):
        """List all tags"""
        return self.python_implementation.tag_list()
    
    def checkout(self, ref: str):
        """Checkout a commit, branch, or tag"""
        return self.python_implementation.checkout(ref)
    
    def info(self):
        """Print system information"""
        return self.python_implementation.info()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        info = self.python_implementation.get_system_info()
        info['rust_available'] = self.rust_available
        info['current_implementation'] = self.current_implementation
        return info
    
    # ===== Legacy compatibility method with potential Rust optimization =====
    
    def create_backup(self, backup_name: Optional[str] = None,
                     include_data: bool = True,
                     include_logs: bool = True,
                     include_config: bool = True,
                     incremental: bool = True) -> str:
        """
        Legacy backup method.
        Can use Rust for simple backup operations if available.
        """
        if self.current_implementation == "rust" and self.rust_available:
            return self._create_rust_backup(include_data, include_logs, include_config)
        else:
            return self.python_implementation.create_backup(
                backup_name, include_data, include_logs, include_config, incremental
            )
    
    def _create_rust_backup(self, include_data: bool, include_logs: bool, 
                           include_config: bool) -> str:
        """Create backup using Rust implementation (basic)"""
        try:
            # Get Rust class
            PyRustBackupCore = self.rust_bridge.get_rust_class("PyRustBackupCore")
            if PyRustBackupCore is None:
                raise Exception("Rust backup class not available")
            
            # Create Rust instance
            rust_backup = PyRustBackupCore(str(self.python_implementation.repo_dir))
            
            # Perform backup
            result = rust_backup.create_backup(include_data, include_logs, include_config)
            
            # Access attributes
            success = getattr(result, 'success', False)
            if success:
                files_processed = getattr(result, 'files_processed', 0)
                files_changed = getattr(result, 'files_changed', 0)
                time_taken_ms = getattr(result, 'time_taken_ms', 0)
                backup_path = getattr(result, 'backup_path', '')
                
                print(f"✅ Rust backup completed successfully")
                print(f"   Files processed: {files_processed}")
                print(f"   Files changed: {files_changed}")
                print(f"   Time taken: {time_taken_ms / 1000:.2f}s")
                
                return backup_path
            else:
                error_message = getattr(result, 'error_message', "Unknown Rust backup error")
                raise Exception(error_message)
                
        except Exception as e:
            print(f"❌ Rust backup failed: {e}")
            print("   Falling back to Python implementation...")
            self.current_implementation = "python"
            return self.python_implementation.create_backup()
    
    # ===== Implementation Switching =====
    
    def switch_to_rust(self) -> bool:
        """Switch to Rust implementation (if available)"""
        if self.rust_available:
            self.current_implementation = "rust"
            print("✅ Switched to Rust implementation")
            print("   Note: Git-like features still use Python")
            return True
        else:
            print("❌ Rust implementation not available")
            return False
    
    def switch_to_python(self):
        """Switch to Python implementation"""
        self.current_implementation = "python"
        print("✅ Switched to Python implementation")
    
    def benchmark(self) -> Dict[str, Any]:
        """
        Benchmark Python vs Rust implementations
        Only tests basic backup operations
        """
        if not self.rust_available:
            print("❌ Rust not available for benchmarking")
            return {}
        
        print("⚡ Running backup performance benchmark...")
        
        # Test Python
        print("\n📊 Testing Python implementation...")
        start = time.time()
        self.switch_to_python()
        py_result = self.create_backup("benchmark_py")
        py_time = time.time() - start
        
        # Test Rust
        print("\n📊 Testing Rust implementation...")
        start = time.time()
        self.switch_to_rust()
        rust_result = self.create_backup("benchmark_rust")
        rust_time = time.time() - start
        
        # Reset to Python (default)
        self.switch_to_python()
        
        results = {
            'python_time_seconds': py_time,
            'rust_time_seconds': rust_time,
            'speedup': py_time / rust_time if rust_time > 0 else 0,
            'rust_faster': rust_time < py_time
        }
        
        print(f"\n=== Benchmark Results ===")
        print(f"Python: {py_time:.3f}s")
        print(f"Rust:   {rust_time:.3f}s")
        if results['rust_faster']:
            print(f"🚀 Rust is {results['speedup']:.2f}x faster")
        else:
            print(f"📊 Python is {1/results['speedup']:.2f}x faster")
        
        return results


if __name__ == "__main__":
    # Test the hybrid backup system
    backup = HybridBackupCore()
    backup.info()
