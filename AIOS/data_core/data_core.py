#!/usr/bin/env python3
"""
DATA CORE SYSTEM - UNIFIED
Self-contained data management system for AIOS Clean
Merges Python-only and Python-Rust hybrid implementations
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path

# Try to import utils_core dependencies (graceful degradation if not available)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils_core.unicode_safe_output import setup_unicode_safe_output
    setup_unicode_safe_output()
    UNICODE_SAFE = True
except ImportError:
    print("⚠️ utils_core.unicode_safe_output not available - using standard output")
    UNICODE_SAFE = False

try:
    from utils_core.bridges import RustBridge, MultiLanguageCore
    RUST_BRIDGE_AVAILABLE = True
except ImportError:
    print("⚠️ utils_core.bridges not available - Python-only mode")
    RUST_BRIDGE_AVAILABLE = False
    # Create stub classes for compatibility
    class RustBridge:
        def __init__(self, *args, **kwargs):
            self.available = False
        def is_available(self):
            return False
        def compile_rust_module(self):
            return False
        def load_rust_module(self):
            return False
    
    class MultiLanguageCore:
        def __init__(self, core_name, python_impl, rust_bridge):
            self.core_name = core_name
            self.python_impl = python_impl
            self.rust_bridge = rust_bridge
            self.current_implementation = "python"

import os
import json
import sqlite3
import shutil
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import modular functions from system/core
sys.path.insert(0, str(Path(__file__).parent / "system"))
from core.stats import (
    get_fractal_cache_stats, get_arbiter_cache_stats,
    get_conversation_stats, get_database_stats,
    get_system_overview, get_dir_stats
)
from core.pipeline import (
    ingest_data, export_data, get_pipeline_metrics,
    load_pipeline_stats, save_pipeline_stats,
    load_data_registry, save_data_registry
)
from core.cleanup import (
    cleanup_old_data, export_to_json, export_to_csv,
    export_to_text, matches_filter
)
from core.lessons import get_relevant_lessons
from core.database import get_database_info


class DataCore:
    """
    Unified Data Core System for AIOS Clean.
    
    Features:
    - Self-contained data management
    - Python-Rust hybrid support (when available)
    - Modular architecture with separate function modules
    - Graceful degradation when dependencies unavailable
    """
    
    def __init__(self, use_hybrid: bool = True):
        """
        Initialize the data core system.
        
        Args:
            use_hybrid: Attempt to use Rust hybrid mode if available
        """
        # Use current directory (we're already in data_core/)
        self.data_dir = Path(__file__).parent
        # Ensure it exists (though it should already)
        self.data_dir.mkdir(exist_ok=True)
        
        # System directories
        self.core_dir = self.data_dir / "system" / "core"
        self.config_dir = self.data_dir / "system" / "config"
        self.rust_data_dir = self.data_dir / "system" / "rust_data"
        self.docs_dir = self.data_dir / "system" / "docs"
        
        # Storage directories - Main data storage
        self.fractal_cache_dir = self.data_dir / "storage" / "caches" / "fractal"
        self.arbiter_cache_dir = self.data_dir / "storage" / "caches" / "arbiter"
        self.cache_dir = self.data_dir / "storage" / "caches" / "general"
        self.database_dir = self.data_dir / "storage" / "databases" / "database"
        self.conversations_dir = self.data_dir / "storage" / "conversations"
        self.embeddings_dir = self.data_dir / "storage" / "embeddings"
        self.documents_dir = self.data_dir / "storage" / "documents"
        
        # Learning directories
        self.learning_system_dir = self.data_dir / "learning" / "system"
        self.lesson_data_dir = self.data_dir / "learning" / "data"
        self.lesson_memory_dir = self.data_dir / "learning" / "memory"
        
        # Analytics directories
        self.analytics_dir = self.data_dir / "analytics" / "metrics"
        self.goldens_dir = self.data_dir / "analytics" / "goldens"
        self.analysis_dir = self.data_dir / "analytics" / "analysis"
        self.qa_dir = self.data_dir / "analytics" / "qa"
        
        # Working directories
        self.logs_dir = self.data_dir / "working" / "logs"
        self.temp_dir = self.data_dir / "working" / "temp"
        self.exports_dir = self.data_dir / "working" / "exports"
        self.imports_dir = self.data_dir / "working" / "imports"
        
        # Archive and extra directories
        self.archive_dir = self.data_dir / "archive"
        self.extra_dir = self.data_dir / "extra"
        
        # Initialize data pipeline tracking
        self.pipeline_stats = load_pipeline_stats(self.data_dir)
        self.data_registry = load_data_registry(self.data_dir)
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Initialize Rust bridge if requested and available
        self.rust_bridge = None
        self.rust_core_instance = None
        self.current_implementation = "python"
        
        if use_hybrid and RUST_BRIDGE_AVAILABLE:
            self._initialize_rust_bridge()
        
        print(f"🗄️ Data Core System Initialized - {'Hybrid' if self.rust_core_instance else 'Python'} Mode")
        print(f"   Data Directory: {self.data_dir}")
        print(f"   Implementation: {self.current_implementation.upper()}")
        print(f"   Fractal Cache: {self.fractal_cache_dir}")
        print(f"   Arbiter Cache: {self.arbiter_cache_dir}")
        print(f"   Conversations: {self.conversations_dir}")
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            # System
            self.core_dir,
            self.config_dir,
            self.rust_data_dir,
            self.docs_dir,
            # Storage
            self.fractal_cache_dir,
            self.arbiter_cache_dir,
            self.cache_dir,
            self.database_dir,
            self.conversations_dir,
            self.embeddings_dir,
            self.documents_dir,
            # Learning
            self.learning_system_dir,
            self.lesson_data_dir,
            self.lesson_memory_dir,
            # Analytics
            self.analytics_dir,
            self.goldens_dir,
            self.analysis_dir,
            self.qa_dir,
            # Working
            self.logs_dir,
            self.temp_dir,
            self.exports_dir,
            self.imports_dir,
            # Archive/Extra
            self.archive_dir,
            self.extra_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _initialize_rust_bridge(self):
        """Initialize Rust bridge for hybrid operations."""
        try:
            self.rust_bridge = RustBridge("data", str(self.rust_data_dir))
            
            if self.rust_bridge.compile_rust_module():
                self.rust_bridge.load_rust_module()
                
                # Try to create Rust core instance
                RustDataCore = self.rust_bridge.get_rust_class("PyRustDataCore")
                if RustDataCore:
                    self.rust_core_instance = RustDataCore(str(self.data_dir))
                    self.current_implementation = "rust"
                    print("✅ Rust acceleration enabled")
        except Exception as e:
            print(f"⚠️ Rust initialization failed: {e} - Using Python implementation")
    
    # ==================== STATISTICS METHODS ====================
    
    def get_fractal_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the FractalCache."""
        if self.current_implementation == "rust" and self.rust_core_instance:
            try:
                result = self.rust_core_instance.get_fractal_cache_stats()
                return self._convert_rust_stats(result, "rust")
            except Exception as e:
                print(f"❌ Rust stats failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return get_fractal_cache_stats(self.fractal_cache_dir)
    
    def get_arbiter_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the ArbiterCache."""
        if self.current_implementation == "rust" and self.rust_core_instance:
            try:
                result = self.rust_core_instance.get_arbiter_cache_stats()
                return self._convert_rust_stats(result, "rust")
            except Exception as e:
                print(f"❌ Rust stats failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return get_arbiter_cache_stats(self.arbiter_cache_dir)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about conversations."""
        if self.current_implementation == "rust" and self.rust_core_instance:
            try:
                result = self.rust_core_instance.get_conversation_stats()
                return self._convert_rust_stats(result, "rust")
            except Exception as e:
                print(f"❌ Rust stats failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return get_conversation_stats(self.conversations_dir)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about databases."""
        if self.current_implementation == "rust" and self.rust_core_instance:
            try:
                result = self.rust_core_instance.get_database_stats()
                return self._convert_rust_stats(result, "rust")
            except Exception as e:
                print(f"❌ Rust stats failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return get_database_stats(self.database_dir)
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview."""
        if self.current_implementation == "rust" and self.rust_core_instance:
            try:
                overview = self.rust_core_instance.get_system_overview()
                overview_dict = json.loads(overview) if isinstance(overview, str) else overview
                overview_dict["implementation"] = "rust"
                return overview_dict
            except Exception as e:
                print(f"❌ Rust overview failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return get_system_overview(
            self.fractal_cache_dir, self.arbiter_cache_dir,
            self.conversations_dir, self.database_dir
        )
    
    def _convert_rust_stats(self, result, implementation: str) -> Dict[str, Any]:
        """Convert Rust struct to Python dict."""
        return {
            "total_files": getattr(result, 'total_files', 0),
            "total_dirs": getattr(result, 'total_dirs', 0),
            "total_size_bytes": getattr(result, 'total_size_bytes', 0),
            "total_size_mb": getattr(result, 'total_size_mb', 0.0),
            "last_modified": getattr(result, 'last_modified', None),
            "file_types": dict(getattr(result, 'file_types', {})),
            "implementation": implementation
        }
    
    # ==================== LESSON METHODS ====================
    
    def get_relevant_lessons(self, current_prompt: str, max_lessons: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant lessons from ArbiterCache for the current prompt."""
        return get_relevant_lessons(self.arbiter_cache_dir, current_prompt, max_lessons)
    
    # ==================== PIPELINE METHODS ====================
    
    def ingest_data(self, data: Any, source: str, data_type: str = "unknown") -> Dict[str, Any]:
        """Ingest data into the AIOS data pipeline."""
        return ingest_data(
            data, source, data_type, self.data_dir,
            self.fractal_cache_dir, self.arbiter_cache_dir,
            self.conversations_dir, self.logs_dir, self.temp_dir,
            self.pipeline_stats, self.data_registry
        )
    
    def export_data(self, data_type: str, target_format: str = "json", 
                   filter_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export data from the AIOS data pipeline."""
        if self.current_implementation == "rust" and self.rust_core_instance and target_format == "json":
            try:
                source_dir_map = {
                    "fractal_cache": str(self.fractal_cache_dir),
                    "arbiter_cache": str(self.arbiter_cache_dir),
                    "conversations": str(self.conversations_dir),
                }
                source_dir = source_dir_map.get(data_type, str(self.data_dir))
                export_path = str(self.exports_dir / f"{data_type}_export_{int(time.time())}.json")
                
                filter_str = json.dumps(filter_criteria) if filter_criteria else None
                result = self.rust_core_instance.export_to_json(source_dir, export_path, filter_str)
                
                return {
                    "success": getattr(result, 'success', False),
                    "files_processed": getattr(result, 'files_processed', 0),
                    "export_path": getattr(result, 'export_path', ''),
                    "implementation": "rust"
                }
            except Exception as e:
                print(f"❌ Rust export failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return export_data(
            data_type, target_format, filter_criteria,
            self.data_dir, self.fractal_cache_dir, self.arbiter_cache_dir,
            self.conversations_dir, self.logs_dir, self.temp_dir, self.exports_dir,
            self.pipeline_stats, export_to_json, export_to_csv, export_to_text
        )
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get comprehensive data pipeline metrics."""
        if self.current_implementation == "rust" and self.rust_core_instance:
            try:
                metrics = self.rust_core_instance.get_pipeline_metrics()
                return {
                    "total_ingestions": getattr(metrics, 'total_ingestions', 0),
                    "total_exports": getattr(metrics, 'total_exports', 0),
                    "last_ingestion": getattr(metrics, 'last_ingestion', None),
                    "last_export": getattr(metrics, 'last_export', None),
                    "cache_hit_rate": getattr(metrics, 'cache_hit_rate', 0.0),
                    "implementation": "rust"
                }
            except Exception as e:
                print(f"❌ Rust metrics failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return get_pipeline_metrics(
            self.data_dir, self.fractal_cache_dir, self.arbiter_cache_dir,
            self.conversations_dir, self.logs_dir, self.temp_dir,
            self.exports_dir, self.pipeline_stats, self.data_registry
        )
    
    # ==================== CLEANUP METHODS ====================
    
    def cleanup_old_data(self, days_old: int = 30, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up old data files."""
        if self.current_implementation == "rust" and self.rust_core_instance:
            try:
                cleaned_files = self.rust_core_instance.cleanup_old_data(days_old, dry_run)
                return {
                    "files_removed": len(cleaned_files),
                    "files_list": cleaned_files,
                    "days_old": days_old,
                    "dry_run": dry_run,
                    "implementation": "rust"
                }
            except Exception as e:
                print(f"❌ Rust cleanup failed: {e}, falling back to Python")
                self.current_implementation = "python"
        
        return cleanup_old_data(
            self.fractal_cache_dir, self.arbiter_cache_dir,
            self.conversations_dir, days_old, dry_run
        )
    
    # ==================== BACKUP METHODS ====================
    
    def backup_data(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of all data."""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"data_backup_{timestamp}"
        
        backup_path = self.archive_dir / f"{backup_name}"
        
        print(f"🗄️ Creating data backup: {backup_name}")
        
        # Copy fractal cache
        if self.fractal_cache_dir.exists():
            shutil.copytree(self.fractal_cache_dir, backup_path / "FractalCache", dirs_exist_ok=True)
        
        # Copy arbiter cache
        if self.arbiter_cache_dir.exists():
            shutil.copytree(self.arbiter_cache_dir, backup_path / "ArbiterCache", dirs_exist_ok=True)
        
        # Copy conversations
        if self.conversations_dir.exists():
            shutil.copytree(self.conversations_dir, backup_path / "conversations", dirs_exist_ok=True)
        
        print(f"✅ Data backup created: {backup_path}")
        
        return str(backup_path)
    
    # ==================== COMPATIBILITY METHODS ====================
    
    def get_current_implementation(self) -> str:
        """Get the current implementation (Python or Rust)."""
        return self.current_implementation
    
    def switch_to_rust(self) -> bool:
        """Switch to Rust implementation if available."""
        if RUST_BRIDGE_AVAILABLE and self.rust_bridge and self.rust_bridge.is_available():
            self.current_implementation = "rust"
            print(f"✅ Switched to Rust implementation")
            return True
        print(f"⚠️ Rust implementation not available")
        return False
    
    def switch_to_python(self) -> bool:
        """Switch to Python implementation."""
        self.current_implementation = "python"
        print(f"✅ Switched to Python implementation")
        return True


# Main entry point for standalone usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AIOS Data Core System")
    parser.add_argument('--action', choices=['stats', 'overview', 'cleanup', 'backup'], 
                       default='overview', help='Action to perform')
    parser.add_argument('--days', type=int, default=30, help='Days old for cleanup')
    parser.add_argument('--dry-run', action='store_true', help='Dry run for cleanup')
    parser.add_argument('--backup-name', help='Name for backup')
    parser.add_argument('--no-hybrid', action='store_true', help='Disable Rust hybrid mode')
    
    args = parser.parse_args()
    
    data_system = DataCore(use_hybrid=not args.no_hybrid)
    
    if args.action == 'stats':
        print("📊 Fractal Cache Stats:")
        fractal_stats = data_system.get_fractal_cache_stats()
        print(f"  Files: {fractal_stats.get('total_files', 0)}")
        print(f"  Size: {fractal_stats.get('total_size_mb', 0):.1f} MB")
        
        print("\n📊 Arbiter Cache Stats:")
        arbiter_stats = data_system.get_arbiter_cache_stats()
        print(f"  Files: {arbiter_stats.get('total_files', 0)}")
        print(f"  Size: {arbiter_stats.get('total_size_mb', 0):.1f} MB")
        
        print("\n📊 Conversation Stats:")
        conv_stats = data_system.get_conversation_stats()
        print(f"  Conversations: {conv_stats.get('total_conversations', conv_stats.get('total_files', 0))}")
        print(f"  Size: {conv_stats.get('total_size_mb', 0):.1f} MB")
        
    elif args.action == 'overview':
        overview = data_system.get_system_overview()
        print("🗄️ Data System Overview:")
        fc = overview.get('fractal_cache', {})
        ac = overview.get('arbiter_cache', {})
        cv = overview.get('conversations', {})
        db = overview.get('databases', {})
        print(f"  Fractal Cache: {fc.get('total_files', 0)} files, {fc.get('total_size_mb', 0):.1f} MB")
        print(f"  Arbiter Cache: {ac.get('total_files', 0)} files, {ac.get('total_size_mb', 0):.1f} MB")
        print(f"  Conversations: {cv.get('total_conversations', cv.get('total_files', 0))} files, {cv.get('total_size_mb', 0):.1f} MB")
        print(f"  Databases: {len(db.get('databases', []))} databases")
        
    elif args.action == 'cleanup':
        results = data_system.cleanup_old_data(args.days, args.dry_run)
        print(f"🗑️ Cleanup Results:")
        print(f"  Total Files: {results.get('total_deleted', results.get('files_removed', 0))}")
        print(f"  Size Freed: {results.get('total_size_freed_mb', 0):.1f} MB")
        
    elif args.action == 'backup':
        data_system.backup_data(args.backup_name)

