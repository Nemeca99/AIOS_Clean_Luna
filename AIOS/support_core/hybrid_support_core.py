#!/usr/bin/env python3
"""
HYBRID SUPPORT CORE - Multi-Language Support System
Automatically uses Rust implementation when available, falls back to Python
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add utils_core to path for rust_bridge
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils_core.bridges.rust_bridge import RustBridge, MultiLanguageCore

# Import original Python implementation
from .support_core import SupportSystem

class HybridSupportCore(MultiLanguageCore):
    """
    Hybrid support core that uses Rust when available, Python as fallback.
    Provides identical interface to original SupportSystem.
    """
    
    def __init__(self, cache_dir: str = "data_core/FractalCache"):
        """Initialize hybrid support core."""
        # Initialize Python implementation
        python_support = SupportSystem(cache_dir)
        
        # Initialize Rust bridge
        rust_bridge = None
        try:
            rust_path = Path(__file__).parent / "rust_support"
            if rust_path.exists():
                rust_bridge = RustBridge("support", str(rust_path))
                
                # Try to compile and load Rust module
                if rust_bridge.compile_rust_module():
                    rust_bridge.load_rust_module()
        except Exception as e:
            print(f"⚠️ Rust support initialization failed: {e}")
            print("   Falling back to Python implementation")
        
        # Initialize multi-language core
        super().__init__("support", python_support, rust_bridge)
        
        # Expose key attributes for compatibility
        self.cache_dir = Path(cache_dir)
        
        # Create a health checker instance for Python fallback
        from support_core.core.health_checker import AIOSHealthChecker
        self.health_checker = AIOSHealthChecker()
        
        # Expose support system components
        self.cache_operations = python_support.cache_ops
        self.faiss_operations = python_support.faiss_ops
        self.embedding_cache = python_support.embedding_cache
        self.recovery_operations = python_support.recovery_ops
        self.registry = python_support.registry
        self.embedder = python_support.embedder
        
        print(f"🔀 Hybrid Support Core Initialized")
        print(f"   Current implementation: {self.current_implementation.upper()}")
        print(f"   Cache directory: {self.cache_dir}")
    
    def run_health_check(self, quick_mode: bool = False) -> Dict[str, Any]:
        """
        Run health check using current implementation (Rust or Python).
        
        Args:
            quick_mode: Run only essential checks for fast initialization
            
        Returns:
            Health check results dictionary
        """
        print(f"🔍 Running health check using {self.current_implementation.upper()} implementation...")
        
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._run_rust_health_check(quick_mode)
        else:
            return self._run_python_health_check(quick_mode)
    
    def _run_rust_health_check(self, quick_mode: bool) -> Dict[str, Any]:
        """Run health check using Rust implementation."""
        try:
            # Get Rust class
            PyRustSupportCore = self.rust_bridge.get_rust_class("PyRustSupportCore")
            if PyRustSupportCore is None:
                raise Exception("Rust support class not available")
            
            # Create Rust instance
            rust_support = PyRustSupportCore(str(self.cache_dir), 384)  # 384 is default dimension
            
            # Perform health check
            result = rust_support.run_health_checks(quick_mode)
            
            # Convert Rust result to Python format
            python_result = {
                "timestamp": result.timestamp,
                "overall_status": result.overall_status,
                "total_checks": result.total_checks,
                "passed_checks": result.passed_checks,
                "failed_checks": result.failed_checks,
                "warnings": result.warnings,
                "check_duration": result.total_duration_ms / 1000.0,  # Convert to seconds
                "quick_mode": quick_mode,
                "implementation": "rust"
            }
            
            print(f"✅ Rust health check completed")
            print(f"   Status: {result.overall_status}")
            print(f"   Checks: {result.passed_checks}/{result.total_checks} passed")
            print(f"   Time: {result.total_duration_ms}ms")
            
            return python_result
            
        except Exception as e:
            print(f"❌ Rust health check failed: {e}")
            print("   Falling back to Python implementation...")
            self.switch_to_python()
            return self._run_python_health_check(quick_mode)
    
    def _run_python_health_check(self, quick_mode: bool) -> Dict[str, Any]:
        """Run health check using Python implementation."""
        # Get Python implementation
        python_support = self.python_implementation
        
        # Run health check
        result = python_support.health_checker.check_system_health(
            async_checks=True, 
            quick_mode=quick_mode
        )
        
        # Add implementation info
        result["implementation"] = "python"
        
        return result
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get system performance metrics using current implementation.
        
        Returns:
            Performance metrics dictionary
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self._get_rust_performance_metrics()
        else:
            return self._get_python_performance_metrics()
    
    def _get_rust_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics using Rust implementation."""
        try:
            PyRustSupportCore = self.rust_bridge.get_rust_class("PyRustSupportCore")
            if PyRustSupportCore is None:
                raise Exception("Rust support class not available")
            
            rust_support = PyRustSupportCore(str(self.cache_dir), 384)
            metrics = rust_support.get_performance_metrics()
            
            # Convert to Python dict
            python_metrics = {k: v for k, v in metrics.items()}
            python_metrics["implementation"] = "rust"
            
            return python_metrics
            
        except Exception as e:
            print(f"❌ Rust metrics failed: {e}")
            self.switch_to_python()
            return self._get_python_performance_metrics()
    
    def _get_python_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics using Python implementation."""
        python_support = self.python_implementation
        
        # Get metrics from Python implementation
        metrics = {
            "implementation": "python",
            "cache_files": len(list(self.cache_dir.glob("*.json"))),
            "cache_size_mb": sum(f.stat().st_size for f in self.cache_dir.glob("*.json")) / 1024 / 1024,
        }
        
        return metrics
    
    def benchmark_health_check(self, quick_mode: bool = False) -> Dict[str, Any]:
        """
        Benchmark both Python and Rust health check implementations.
        
        Args:
            quick_mode: Run quick health checks for benchmarking
            
        Returns:
            Dictionary with performance comparison data
        """
        print(f"⚡ Running health check performance benchmark...")
        
        def python_health_func():
            return self.python_implementation.health_checker.check_system_health(
                async_checks=True, 
                quick_mode=quick_mode
            )
        
        def rust_health_func():
            if not (self.rust_bridge and self.rust_bridge.is_available()):
                raise Exception("Rust implementation not available")
            
            PyRustSupportCore = self.rust_bridge.get_rust_class("PyRustSupportCore")
            if PyRustSupportCore is None:
                raise Exception("Rust support class not available")
            
            rust_support = PyRustSupportCore(str(self.cache_dir), 384)
            result = rust_support.run_health_checks(quick_mode)
            
            return {
                "overall_status": result.overall_status,
                "total_duration_ms": result.total_duration_ms
            }
        
        return self.benchmark(quick_mode)
    
    def switch_implementation(self, implementation: str) -> bool:
        """
        Switch between Python and Rust implementations.
        
        Args:
            implementation: 'python' or 'rust'
            
        Returns:
            True if switch successful, False otherwise
        """
        if implementation.lower() == "rust":
            return self.switch_to_rust()
        elif implementation.lower() == "python":
            self.switch_to_python()
            return True
        else:
            print(f"❌ Invalid implementation: {implementation}")
            print("   Valid options: 'python', 'rust'")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about the hybrid support core.
        
        Returns:
            Dictionary with status information
        """
        return {
            "core_name": "hybrid_support",
            "current_implementation": self.current_implementation,
            "rust_available": self.rust_bridge and self.rust_bridge.is_available(),
            "python_available": True,
            "cache_dir": str(self.cache_dir),
            "health_checker": "available",
            "faiss_operations": "available",
            "cache_operations": "available",
            "embedding_cache": "available",
            "recovery_operations": "available",
            "security_validator": "available"
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status (compatibility method).
        
        Returns:
            Dictionary with system status information
        """
        try:
            # Get status from Python implementation
            python_status = self.python_implementation.get_system_status()
            
            # Add hybrid-specific information
            python_status.update({
                "hybrid_implementation": self.current_implementation,
                "rust_available": self.rust_bridge and self.rust_bridge.is_available(),
                "cache_dir": str(self.cache_dir)
            })
            
            return python_status
            
        except Exception as e:
            # Fallback status if Python implementation fails
            return {
                "core_name": "hybrid_support",
                "current_implementation": self.current_implementation,
                "rust_available": self.rust_bridge and self.rust_bridge.is_available(),
                "python_available": True,
                "cache_dir": str(self.cache_dir),
                "status": "available",
                "error": str(e)
            }
