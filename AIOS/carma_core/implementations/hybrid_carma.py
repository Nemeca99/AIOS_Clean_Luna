#!/usr/bin/env python3
"""
HYBRID CARMA CORE - Python-Rust Integration
Provides a unified interface that can switch between Python and Rust implementations
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils_core.bridges.rust_bridge import RustBridge, MultiLanguageCore
from carma_core.carma_core import CARMASystem
import time
import json
from typing import Dict, List, Optional, Any

class HybridCarmaCore(MultiLanguageCore):
    """
    Hybrid CARMA Core that can use either Python or Rust implementation.
    Automatically detects and uses Rust when available, falls back to Python.
    """
    
    def __init__(self, base_dir: str = "data_core/FractalCache"):
        """
        Initialize the Hybrid CARMA Core.
        
        Args:
            base_dir: Directory for CARMA cache operations
        """
        print("🧠 Initializing Hybrid CARMA Core...")
        
        # Initialize Python implementation
        python_carma = CARMASystem(base_dir=base_dir)
        
        # Initialize Rust bridge
        rust_bridge = None
        try:
            rust_path = Path(__file__).parent / "rust_carma"
            if rust_path.exists():
                rust_bridge = RustBridge("carma", str(rust_path))
                
                # Try to compile and load Rust module
                if rust_bridge.compile_rust_module():
                    rust_bridge.load_rust_module()
        except Exception as e:
            print(f"⚠️ Rust CARMA initialization failed: {e}")
            print("   Falling back to Python implementation")
        
        # Initialize multi-language core
        super().__init__("carma", python_carma, rust_bridge)
        
        # Expose key attributes for compatibility
        self.cache_dir = Path(base_dir)
        self.total_queries = getattr(python_carma, 'total_queries', 0)
        # CARMA uses cache.file_registry for fragments, not a direct fragments attribute
        cache = getattr(python_carma, 'cache', None)
        if cache and hasattr(cache, 'file_registry'):
            self.fragments = list(cache.file_registry.values())
            print(f"🔍 DEBUG: Loaded {len(self.fragments)} fragments from cache")
        else:
            self.fragments = []
            print(f"🔍 DEBUG: No cache or file_registry found")
        self.clusters = getattr(python_carma, 'clusters', {})
        
        print(f"🚀 Hybrid CARMA Core Initialized")
        print(f"   Current implementation: {self.current_implementation.upper()}")
        print(f"   Base directory: {base_dir}")
    
    def process_query(self, query: str, context: Dict = None) -> Dict:
        """
        Process a query through the CARMA system.
        
        Args:
            query: The query to process
            context: Optional context information
            
        Returns:
            Dictionary containing processing results
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._process_query_rust(query, context)
        else:
            return self.python_implementation.process_query(query, context)
    
    def _process_query_rust(self, query: str, context: Dict = None) -> Dict:
        """Process query using Rust implementation."""
        try:
            # For now, we'll use a simple approach since we can't directly call Rust methods
            # In a full implementation, we'd use subprocess calls or a more sophisticated bridge
            print("🦀 Processing query with Rust implementation (placeholder)")
            
            # Fallback to Python for now
            return self.python_implementation.process_query(query, context)
            
        except Exception as e:
            print(f"⚠️ Rust query processing failed: {e}")
            print("   Falling back to Python implementation")
            self.switch_to_python()
            return self.python_implementation.process_query(query, context)
    
    def optimize_memory_system(self) -> Dict:
        """Optimize the memory system."""
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._optimize_memory_rust()
        else:
            return self.python_implementation.optimize_memory_system()
    
    def _optimize_memory_rust(self) -> Dict:
        """Optimize memory using Rust implementation."""
        try:
            print("🦀 Optimizing memory with Rust implementation (placeholder)")
            # Fallback to Python for now
            return self.python_implementation.optimize_memory_system()
        except Exception as e:
            print(f"⚠️ Rust memory optimization failed: {e}")
            print("   Falling back to Python implementation")
            self.switch_to_python()
            return self.python_implementation.optimize_memory_system()
    
    def analyze_memory_system(self) -> Dict:
        """Analyze the memory system."""
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._analyze_memory_rust()
        else:
            return self.python_implementation.analyze_memory_system()
    
    def _analyze_memory_rust(self) -> Dict:
        """Analyze memory using Rust implementation."""
        try:
            print("🦀 Analyzing memory with Rust implementation (placeholder)")
            # Fallback to Python for now
            return self.python_implementation.analyze_memory_system()
        except Exception as e:
            print(f"⚠️ Rust memory analysis failed: {e}")
            print("   Falling back to Python implementation")
            self.switch_to_python()
            return self.python_implementation.analyze_memory_system()
    
    def compress_memories(self, algorithm: str = 'semantic') -> Dict:
        """Compress memories using specified algorithm."""
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._compress_memories_rust(algorithm)
        else:
            return self.python_implementation.compress_memories(algorithm)
    
    def _compress_memories_rust(self, algorithm: str) -> Dict:
        """Compress memories using Rust implementation."""
        try:
            print(f"🦀 Compressing memories with Rust implementation (algorithm: {algorithm}) (placeholder)")
            # Fallback to Python for now
            return self.python_implementation.compress_memories(algorithm)
        except Exception as e:
            print(f"⚠️ Rust memory compression failed: {e}")
            print("   Falling back to Python implementation")
            self.switch_to_python()
            return self.python_implementation.compress_memories(algorithm)
    
    def cluster_memories(self, num_clusters: int = 5) -> Dict:
        """Cluster memory fragments."""
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._cluster_memories_rust(num_clusters)
        else:
            return self.python_implementation.cluster_memories(num_clusters)
    
    def _cluster_memories_rust(self, num_clusters: int) -> Dict:
        """Cluster memories using Rust implementation."""
        try:
            print(f"🦀 Clustering memories with Rust implementation (clusters: {num_clusters}) (placeholder)")
            # Fallback to Python for now
            return self.python_implementation.cluster_memories(num_clusters)
        except Exception as e:
            print(f"⚠️ Rust memory clustering failed: {e}")
            print("   Falling back to Python implementation")
            self.switch_to_python()
            return self.python_implementation.cluster_memories(num_clusters)
    
    def get_system_stats(self) -> Dict:
        """Get system statistics."""
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._get_stats_rust()
        else:
            # Get Python stats
            return {
                "implementation": "python",
                "total_queries": getattr(self.python_implementation, 'total_queries', 0),
                "fragments_count": len(getattr(self.python_implementation, 'fragments', [])),
                "clusters_count": len(getattr(self.python_implementation, 'clusters', {})),
            }
    
    def _get_stats_rust(self) -> Dict:
        """Get statistics from Rust implementation."""
        try:
            print("🦀 Getting stats from Rust implementation (placeholder)")
            # Fallback to Python for now
            return self.get_system_stats()
        except Exception as e:
            print(f"⚠️ Rust stats retrieval failed: {e}")
            print("   Falling back to Python implementation")
            self.switch_to_python()
            return self.get_system_stats()
    
    def run_health_check(self) -> Dict:
        """Run health check for the CARMA system."""
        start_time = time.time()
        
        try:
            # Test basic functionality
            test_result = self.process_query("test query")
            
            health_status = {
                "status": "healthy",
                "implementation": self.current_implementation,
                "response_time": time.time() - start_time,
                "total_queries": getattr(self.python_implementation, 'total_queries', 0),
                "fragments_count": len(getattr(self.python_implementation, 'fragments', [])),
                "clusters_count": len(getattr(self.python_implementation, 'clusters', {})),
                "rust_available": self.rust_bridge and self.rust_bridge.is_available(),
            }
            
            print(f"✅ CARMA health check passed ({health_status['response_time']:.3f}s)")
            return health_status
            
        except Exception as e:
            health_status = {
                "status": "unhealthy",
                "implementation": self.current_implementation,
                "error": str(e),
                "response_time": time.time() - start_time,
                "rust_available": self.rust_bridge and self.rust_bridge.is_available(),
            }
            
            print(f"❌ CARMA health check failed: {e}")
            return health_status
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics for the CARMA system."""
        try:
            # Get Python implementation stats
            python_stats = {
                "implementation": "python",
                "total_queries": getattr(self.python_implementation, 'total_queries', 0),
                "fragments_count": len(getattr(self.python_implementation, 'fragments', [])),
                "clusters_count": len(getattr(self.python_implementation, 'clusters', {})),
                "cache_size": len(getattr(self.python_implementation.cache, 'fragments', {})),
                "base_dir": str(self.cache_dir),
            }
            
            return python_stats
        except Exception as e:
            return {
                "implementation": "python",
                "error": str(e),
                "base_dir": str(self.cache_dir),
            }
    
    def get_hybrid_status(self) -> Dict:
        """Get detailed status of the hybrid system."""
        return {
            "current_implementation": self.current_implementation,
            "rust_available": self.rust_bridge and self.rust_bridge.is_available(),
            "rust_compilation_status": self.rust_bridge.compilation_status if self.rust_bridge else None,
            "python_available": self.python_implementation is not None,
            "cache_dir": str(self.cache_dir),
        }
