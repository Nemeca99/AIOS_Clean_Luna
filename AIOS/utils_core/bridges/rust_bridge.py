#!/usr/bin/env python3
"""
RUST BRIDGE - Python-Rust Integration Layer
Handles loading and interfacing with Rust implementations of AIOS cores
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import time

class RustBridge:
    """
    Bridge between Python and Rust implementations.
    Handles compilation, loading, and error handling for Rust modules.
    """
    
    def __init__(self, core_name: str, rust_module_path: str):
        """
        Initialize Rust bridge for a specific core.
        
        Args:
            core_name: Name of the core (e.g., 'backup', 'support')
            rust_module_path: Path to the Rust module directory
        """
        self.core_name = core_name
        self.rust_module_path = Path(rust_module_path)
        self.module_name = f"aios_{core_name}_rust"
        self.compiled_module = None
        self.compilation_status = None
        
        # Try to use virtual environment Python if available
        self.python_executable = self._get_python_executable()
        
        print(f"🌉 Rust Bridge initialized for {core_name}")
        print(f"   Module path: {self.rust_module_path}")
        print(f"   Module name: {self.module_name}")
        print(f"   Python executable: {self.python_executable}")
    
    def _get_python_executable(self) -> str:
        """
        Get the appropriate Python executable to use.
        Prioritizes virtual environment Python if available.
        """
        # Check if we're in a virtual environment
        venv_python = os.environ.get('VIRTUAL_ENV')
        if venv_python:
            # Use the virtual environment's Python executable
            venv_python_path = Path(venv_python) / "Scripts" / "python.exe"
            if venv_python_path.exists():
                return str(venv_python_path)
        
        # Check if current Python is in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # We're in a virtual environment, use current executable
            return sys.executable
        
        # Fall back to current Python executable
        return sys.executable
    
    def compile_rust_module(self, force_recompile: bool = False) -> bool:
        """
        Compile the Rust module using maturin.
        
        Args:
            force_recompile: Force recompilation even if module exists
            
        Returns:
            True if compilation successful, False otherwise
        """
        print(f"🔨 Compiling Rust module for {self.core_name}...")
        
        # Check if maturin is installed using the correct Python executable
        try:
            subprocess.run([self.python_executable, "-m", "maturin", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Maturin not found. Installing...")
            try:
                subprocess.run([self.python_executable, "-m", "pip", "install", "maturin"], 
                             check=True)
            except subprocess.CalledProcessError:
                print("❌ Failed to install maturin")
                return False
        
        # Check if already compiled and not forcing recompile
        if not force_recompile and self._is_module_compiled():
            print(f"✅ Module already compiled for {self.core_name}")
            self.compilation_status = "already_compiled"
            # Module is already loaded in _is_module_compiled()
            return True
        
        # Compile the Rust module
        try:
            start_time = time.time()
            result = subprocess.run(
                [self.python_executable, "-m", "maturin", "develop", "--release"],
                cwd=self.rust_module_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                encoding='utf-8',
                errors='replace',
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            if result.returncode == 0:
                elapsed = time.time() - start_time
                print(f"✅ Rust module compiled successfully in {elapsed:.2f}s")
                self.compilation_status = "compiled"
                return True
            else:
                print(f"❌ Compilation failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                self.compilation_status = "failed"
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Compilation timed out after 5 minutes")
            self.compilation_status = "timeout"
            return False
        except Exception as e:
            print(f"❌ Compilation error: {e}")
            self.compilation_status = "error"
            return False
    
    def load_rust_module(self) -> bool:
        """
        Load the compiled Rust module.
        
        Returns:
            True if loading successful, False otherwise
        """
        print(f"📦 Loading Rust module for {self.core_name}...")
        
        try:
            # Import the compiled module
            self.compiled_module = __import__(self.module_name)
            print(f"✅ Rust module loaded successfully for {self.core_name}")
            return True
            
        except ImportError as e:
            print(f"❌ Failed to import Rust module: {e}")
            print("   Try running: maturin develop")
            return False
        except Exception as e:
            print(f"❌ Error loading Rust module: {e}")
            return False
    
    def is_available(self) -> bool:
        """
        Check if Rust implementation is available.
        
        Returns:
            True if Rust module is compiled and available (either loaded or external)
        """
        if self.compiled_module is not None:
            return True
        
        # Try to load the module directly first
        try:
            import importlib
            self.compiled_module = importlib.import_module(self.module_name)
            print(f"✅ Rust module {self.module_name} loaded successfully")
            return True
        except ImportError as e:
            # Rust module not found in sys.path - try fallback
            print(f"Note: Direct import of {self.module_name} failed: {e}")
        
        # Check if module is available externally (lazy loading approach)
        try:
            import subprocess
            result = subprocess.run(
                [self.python_executable, '-c', f'import {self.module_name}; print("SUCCESS")'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Module is available externally, try to load it again
                try:
                    import importlib
                    self.compiled_module = importlib.import_module(self.module_name)
                    return True
                except ImportError as e:
                    # Rust module not available - will use Python fallback
                    print(f"Note: Fallback import of {self.module_name} failed: {e}")
            return False
        except Exception:
            return False
    
    def get_rust_class(self, class_name: str):
        """
        Get a Rust class from the loaded module.
        
        Args:
            class_name: Name of the class to retrieve
            
        Returns:
            Rust class or None if not available
        """
        if not self.is_available():
            print(f"❌ Rust module not available for {self.core_name}")
            return None
        
        # Lazy load the module if not already loaded
        if self.compiled_module is None:
            print(f"🔄 Lazy loading Rust module for {self.core_name}...")
            if not self._is_module_compiled():
                print(f"❌ Failed to lazy load module for {self.core_name}")
                return None
        
        try:
            return getattr(self.compiled_module, class_name)
        except AttributeError:
            print(f"❌ Class {class_name} not found in Rust module")
            return None
    
    def create_rust_instance(self, class_name: str, *args, **kwargs):
        """
        Create an instance of a Rust class.
        
        Args:
            class_name: Name of the class to instantiate
            *args: Positional arguments for constructor
            **kwargs: Keyword arguments for constructor
            
        Returns:
            Rust instance or None if failed
        """
        rust_class = self.get_rust_class(class_name)
        if rust_class is None:
            return None
        
        try:
            return rust_class(*args, **kwargs)
        except Exception as e:
            print(f"❌ Failed to create Rust instance: {e}")
            return None
    
    def _is_module_compiled(self) -> bool:
        """Check if the Rust module is already compiled."""
        try:
            # Try to import the module directly in current process first
            try:
                self.compiled_module = __import__(self.module_name)
                print(f"✅ Module {self.module_name} already available")
                return True
            except ImportError as e:
                print(f"❌ Direct import failed: {e}")
                # If direct import fails, check if it's available in virtual environment
                import subprocess
                result = subprocess.run(
                    [self.python_executable, '-c', f'import {self.module_name}; print("SUCCESS")'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ Module {self.module_name} available (external)")
                    # Try alternative import methods
                    try:
                        # Method 1: Try importing with importlib
                        import importlib
                        self.compiled_module = importlib.import_module(self.module_name)
                        print(f"✅ Module {self.module_name} loaded via importlib")
                        return True
                    except ImportError:
                        try:
                            # Method 2: Try importing with sys.modules manipulation
                            import sys
                            if self.module_name in sys.modules:
                                self.compiled_module = sys.modules[self.module_name]
                                print(f"✅ Module {self.module_name} found in sys.modules")
                                return True
                            else:
                                # Method 3: Force reload via subprocess and capture
                                import os
                                import tempfile
                                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                                    f.write(f"import {self.module_name}\nprint('SUCCESS')\n")
                                    temp_file = f.name
                                
                                result2 = subprocess.run(
                                    [self.python_executable, temp_file],
                                    capture_output=True, text=True, cwd=os.getcwd()
                                )
                                os.unlink(temp_file)
                                
                                if result2.returncode == 0:
                                    print(f"✅ Module {self.module_name} confirmed working via subprocess")
                                    # One more attempt with fresh import
                                    try:
                                        import importlib
                                        importlib.invalidate_caches()
                                        self.compiled_module = importlib.import_module(self.module_name)
                                        print(f"✅ Module {self.module_name} loaded after cache invalidation")
                                        return True
                                    except ImportError:
                                        print(f"❌ Still can't import {self.module_name} after cache invalidation")
                                        return False
                                else:
                                    print(f"❌ Module {self.module_name} subprocess test failed: {result2.stderr}")
                                    return False
                        except Exception as e2:
                            print(f"❌ Alternative import methods failed: {e2}")
                            return False
                else:
                    print(f"❌ Module {self.module_name} not available: {result.stderr}")
                    return False
        except Exception as e:
            print(f"❌ Error checking module {self.module_name}: {e}")
            return False
    
    def get_performance_comparison(self, python_func, rust_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Compare performance between Python and Rust implementations.
        
        Args:
            python_func: Python function to test
            rust_func: Rust function to test
            *args: Arguments for both functions
            **kwargs: Keyword arguments for both functions
            
        Returns:
            Dictionary with performance comparison data
        """
        print(f"⚡ Running performance comparison for {self.core_name}...")
        
        results = {
            "core_name": self.core_name,
            "python_available": True,
            "rust_available": self.is_available(),
            "python_time": None,
            "rust_time": None,
            "speedup": None,
            "error": None
        }
        
        # Test Python implementation
        try:
            start_time = time.time()
            python_result = python_func(*args, **kwargs)
            python_time = time.time() - start_time
            results["python_time"] = python_time
            print(f"   Python: {python_time:.3f}s")
        except Exception as e:
            results["python_available"] = False
            results["error"] = f"Python error: {e}"
            print(f"   Python: Failed - {e}")
        
        # Test Rust implementation
        if self.is_available():
            try:
                start_time = time.time()
                rust_result = rust_func(*args, **kwargs)
                rust_time = time.time() - start_time
                results["rust_time"] = rust_time
                print(f"   Rust: {rust_time:.3f}s")
                
                # Calculate speedup
                if results["python_time"] and results["python_time"] > 0:
                    results["speedup"] = results["python_time"] / results["rust_time"]
                    print(f"   Speedup: {results['speedup']:.2f}x")
                    
            except Exception as e:
                results["rust_available"] = False
                results["error"] = f"Rust error: {e}"
                print(f"   Rust: Failed - {e}")
        
        return results

class MultiLanguageCore:
    """
    Wrapper that automatically chooses between Python and Rust implementations.
    Falls back to Python if Rust is not available.
    """
    
    def __init__(self, core_name: str, python_implementation, rust_bridge: Optional[RustBridge] = None):
        """
        Initialize multi-language core.
        
        Args:
            core_name: Name of the core
            python_implementation: Python implementation class
            rust_bridge: Optional Rust bridge instance
        """
        self.core_name = core_name
        self.python_implementation = python_implementation
        self.rust_bridge = rust_bridge
        self.current_implementation = "python"  # Default to Python
        
        # Try to use Rust if available
        if rust_bridge and rust_bridge.is_available():
            self.current_implementation = "rust"
            print(f"🚀 Using Rust implementation for {core_name}")
        else:
            print(f"🐍 Using Python implementation for {core_name}")
    
    def get_implementation(self):
        """Get the current implementation (Python or Rust)."""
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            return self.rust_bridge.compiled_module
        else:
            return self.python_implementation
    
    def switch_to_rust(self) -> bool:
        """Switch to Rust implementation if available."""
        if self.rust_bridge and self.rust_bridge.is_available():
            self.current_implementation = "rust"
            print(f"🔄 Switched to Rust implementation for {self.core_name}")
            return True
        else:
            print(f"❌ Rust implementation not available for {self.core_name}")
            return False
    
    def switch_to_python(self):
        """Switch to Python implementation."""
        self.current_implementation = "python"
        print(f"🔄 Switched to Python implementation for {self.core_name}")
    
    def benchmark(self, *args, **kwargs) -> Dict[str, Any]:
        """Benchmark both implementations."""
        if not self.rust_bridge:
            return {"error": "No Rust bridge available"}
        
        return self.rust_bridge.get_performance_comparison(
            self.python_implementation, 
            self.get_implementation(),
            *args, **kwargs
        )
