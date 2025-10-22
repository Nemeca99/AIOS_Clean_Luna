#!/usr/bin/env python3
"""
Support Core - Health Checker
Extracted from monolithic support_core.py for better modularity.
"""

import sys
from pathlib import Path
import time
import json
import os
import shutil
import re
import hashlib
import math
import random
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup Unicode safety
try:
    from utils_core.unicode_safe_output import setup_unicode_safe_output
    setup_unicode_safe_output()
except ImportError:
    print("Warning: Unicode safety layer not available")

# Import dependencies from same module
from .config import AIOSConfig, aios_config
from .logger import AIOSLogger

# Create a global logger instance for health checker
aios_logger = AIOSLogger("HealthChecker")


class AIOSHealthError(Exception):
    """Custom exception for AIOS health check errors"""
    pass


class AIOSHealthChecker:
    """Comprehensive health check system with real-time monitoring and diagnostics"""
    
    def __init__(self, config: AIOSConfig = None, logger: AIOSLogger = None):
        self.config = config or aios_config
        self.logger = logger or aios_logger
        self.health_status = {}
        self.last_check = None
        self._check_history = []
        self._max_history = 100
        self._executor = ThreadPoolExecutor(max_workers=self.config.get("MAX_WORKERS", 4))
        
        # Initialize the missing lock for thread safety
        import threading
        self._lock = threading.Lock()
        
    def check_system_health(self, async_checks: bool = True, quick_mode: bool = False) -> Dict[str, Any]:
        """Comprehensive system health check with parallel execution and quick mode option"""
        self.logger.info("Starting comprehensive AIOS system health check...")
        start_time = time.time()
        
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "HEALTHY",
            "checks": {},
            "recommendations": [],
            "errors": [],
            "warnings": [],
            "performance_metrics": {},
            "check_duration": 0,
            "quick_mode": quick_mode
        }
        
        try:
            if quick_mode:
                # Run only essential checks for fast initialization
                health_results["checks"] = self._run_quick_checks()
            elif async_checks:
                # Run checks in parallel for better performance
                health_results["checks"] = self._run_parallel_checks()
            else:
                # Run checks sequentially
                health_results["checks"] = self._run_sequential_checks()
            
            # Analyze results and determine overall status
            health_results.update(self._analyze_health_results(health_results["checks"]))
            
            # Add performance metrics (skip in quick mode)
            if not quick_mode:
                health_results["performance_metrics"] = self._collect_performance_metrics()
            
            # Store in history
            self._store_health_history(health_results)
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", include_stack=True)
            health_results["overall_status"] = "CRITICAL"
            health_results["errors"].append(f"Health check system error: {e}")
        
        finally:
            health_results["check_duration"] = time.time() - start_time
            self.health_status = health_results
            self.last_check = datetime.now()
            
            mode_text = "quick mode" if quick_mode else "full mode"
            self.logger.info(f"Health check completed in {health_results['check_duration']:.2f}s ({mode_text}). Status: {health_results['overall_status']}")
        
        return health_results
    
    def _run_parallel_checks(self) -> Dict[str, Any]:
        """Run health checks in parallel"""
        check_functions = {
            "python_environment": self._check_python_environment,
            "dependencies": self._check_dependencies,
            "file_system": self._check_file_system,
            "memory": self._check_memory_usage,
            "disk_space": self._check_disk_space,
            "network": self._check_network_connectivity,
            "processes": self._check_running_processes,
            "ports": self._check_port_availability,
            "database": self._check_database_connectivity,
            "api_endpoints": self._check_api_endpoints
        }
        
        results = {}
        future_to_check = {self._executor.submit(func): name for name, func in check_functions.items()}
        
        for future in as_completed(future_to_check):
            check_name = future_to_check[future]
            try:
                results[check_name] = future.result()
            except Exception as e:
                results[check_name] = {
                    "status": False,
                    "error": str(e),
                    "message": f"Check failed with exception: {e}"
                }
        
        return results
    
    def _run_quick_checks(self) -> Dict[str, Any]:
        """Run only essential checks for fast initialization"""
        results = {}
        
        # Only check critical components that could prevent system startup
        essential_checks = [
            ("python_environment", self._check_python_environment),
            ("file_system", self._check_file_system),
            ("memory", self._check_memory_usage)
        ]
        
        for check_name, check_func in essential_checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                results[check_name] = {
                    "status": False,
                    "error": str(e),
                    "message": f"Quick check failed: {e}",
                    "critical": True
                }
        
        return results
    
    def _run_sequential_checks(self) -> Dict[str, Any]:
        """Run health checks sequentially"""
        results = {}
        
        checks = [
            ("python_environment", self._check_python_environment),
            ("dependencies", self._check_dependencies),
            ("file_system", self._check_file_system),
            ("memory", self._check_memory_usage),
            ("disk_space", self._check_disk_space),
            ("network", self._check_network_connectivity),
            ("processes", self._check_running_processes),
            ("ports", self._check_port_availability),
            ("database", self._check_database_connectivity),
            ("api_endpoints", self._check_api_endpoints)
        ]
        
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                results[check_name] = {
                    "status": False,
                    "error": str(e),
                    "message": f"Check failed with exception: {e}"
                }
        
        return results
    
    def _analyze_health_results(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze health check results and generate recommendations"""
        failed_checks = []
        warning_checks = []
        critical_checks = []
        
        for check_name, result in checks.items():
            if not result.get("status", False):
                if result.get("critical", False):
                    critical_checks.append(check_name)
                else:
                    failed_checks.append(check_name)
            elif result.get("warning", False):
                warning_checks.append(check_name)
        
        # Determine overall status
        if critical_checks:
            overall_status = "CRITICAL"
        elif failed_checks:
            overall_status = "DEGRADED"
        elif warning_checks:
            overall_status = "WARNING"
        else:
            overall_status = "HEALTHY"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(checks, failed_checks, warning_checks, critical_checks)
        
        return {
            "overall_status": overall_status,
            "errors": failed_checks + critical_checks,
            "warnings": warning_checks,
            "critical": critical_checks,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(self, checks: Dict[str, Any], failed: List[str], 
                                 warnings: List[str], critical: List[str]) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if "python_environment" in failed + critical:
            recommendations.append("Update Python to version 3.8 or higher")
        
        if "dependencies" in failed + critical:
            recommendations.append("Install missing dependencies: pip install -r requirements.txt")
        
        if "file_system" in failed + critical:
            recommendations.append("Check file system permissions and disk health")
        
        if "memory" in failed + critical:
            recommendations.append("Increase available memory or optimize memory usage")
        
        if "disk_space" in failed + critical:
            recommendations.append("Free up disk space or expand storage")
        
        if "network" in failed + critical:
            recommendations.append("Check network connectivity and firewall settings")
        
        if "database" in failed + critical:
            recommendations.append("Check database connectivity and configuration")
        
        if "api_endpoints" in failed + critical:
            recommendations.append("Verify API endpoint availability and configuration")
        
        if not recommendations:
            recommendations.append("System is healthy - continue monitoring")
        
        return recommendations
    
    def _check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment health with comprehensive diagnostics"""
        try:
            import sys
            import platform
            
            python_version = sys.version_info
            is_compatible = python_version >= (3, 8)
            
            # Additional environment checks
            virtual_env = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            executable_path = sys.executable
            path_info = sys.path[:5]  # First 5 paths
            
            # Check for common issues
            warnings = []
            if not virtual_env and not self.config.get("ADMIN_MODE", False):
                warnings.append("Not running in virtual environment")
            
            if sys.maxsize < 2**32:
                warnings.append("Running 32-bit Python (consider 64-bit for better performance)")
            
            return {
                "status": is_compatible,
                "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                "platform": platform.system(),
                "architecture": platform.architecture()[0],
                "virtual_env": virtual_env,
                "executable": executable_path,
                "path_sample": path_info,
                "warning": len(warnings) > 0,
                "warnings": warnings,
                "message": "Python environment is compatible" if is_compatible else "Python version too old",
                "critical": not is_compatible
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check Python environment",
                "critical": True
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check critical dependencies with version validation"""
        try:
            # Core Python modules (should always be available)
            core_modules = ["json", "pathlib", "datetime", "typing", "dataclasses", "enum", "sqlite3"]
            
            # Optional but important modules
            optional_modules = {
                "numpy": "numpy",
                "requests": "requests", 
                "psutil": "psutil",
                "faiss": "faiss",
                "pandas": "pandas",
                "scikit-learn": "sklearn",
                "matplotlib": "matplotlib",
                "seaborn": "seaborn"
            }
            
            missing_core = []
            missing_optional = []
            module_versions = {}
            
            # Check core modules
            for module in core_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_core.append(module)
            
            # Check optional modules and get versions
            for module_name, import_name in optional_modules.items():
                try:
                    module = __import__(import_name)
                    version = getattr(module, '__version__', 'unknown')
                    module_versions[module_name] = version
                except ImportError:
                    missing_optional.append(module_name)
            
            # Determine status
            status = len(missing_core) == 0
            warning = len(missing_optional) > 3  # Warning if many optional modules missing
            
            return {
                "status": status,
                "missing_core": missing_core,
                "missing_optional": missing_optional,
                "module_versions": module_versions,
                "warning": warning,
                "message": "All core dependencies available" if status else f"Missing core modules: {missing_core}",
                "critical": len(missing_core) > 0
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check dependencies",
                "critical": True
            }
    
    def _check_file_system(self) -> Dict[str, Any]:
        """Check file system health with comprehensive diagnostics"""
        try:
            root_path = Path(self.config.get("AIOS_ROOT"))
            log_dir = Path(self.config.get("LOG_DIR"))
            debug_dir = Path(self.config.get("DEBUG_DIR"))
            cache_dir = Path(self.config.get("CACHE_DIR", "data_core/FractalCache"))
            
            checks = {
                "root_exists": root_path.exists(),
                "root_writable": root_path.is_dir() and os.access(root_path, os.W_OK),
                "log_dir_exists": log_dir.exists(),
                "log_dir_writable": log_dir.exists() and os.access(log_dir, os.W_OK),
                "debug_dir_exists": debug_dir.exists(),
                "debug_dir_writable": debug_dir.exists() and os.access(debug_dir, os.W_OK),
                "cache_dir_exists": cache_dir.exists(),
                "cache_dir_writable": cache_dir.exists() and os.access(cache_dir, os.W_OK)
            }
            
            # Check disk space for each directory
            disk_checks = {}
            for name, path in [("root", root_path), ("log", log_dir), ("debug", debug_dir), ("cache", cache_dir)]:
                if path.exists():
                    try:
                        total, used, free = shutil.disk_usage(path)
                        free_percent = (free / total) * 100
                        disk_checks[f"{name}_free_percent"] = round(free_percent, 2)
                        disk_checks[f"{name}_free_gb"] = round(free / (1024**3), 2)
                    except Exception:
                        disk_checks[f"{name}_free_percent"] = "unknown"
            
            # Check for common issues
            warnings = []
            if not checks["root_writable"]:
                warnings.append("Root directory not writable")
            if not checks["log_dir_writable"]:
                warnings.append("Log directory not writable")
            if not checks["cache_dir_writable"]:
                warnings.append("Cache directory not writable")
            
            all_good = all(checks.values())
            warning = len(warnings) > 0
            
            return {
                "status": all_good,
                "checks": checks,
                "disk_checks": disk_checks,
                "warning": warning,
                "warnings": warnings,
                "message": "File system is healthy" if all_good else "File system issues detected"
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check file system",
                "critical": True
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage with detailed analysis"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get swap memory info
            swap = psutil.swap_memory()
            
            # Check if memory usage is concerning
            is_healthy = memory_percent < 85
            warning = memory_percent > 75
            
            # Get process memory usage
            current_process = psutil.Process()
            process_memory = current_process.memory_info()
            
            return {
                "status": is_healthy,
                "memory_percent": memory_percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "process_memory_mb": round(process_memory.rss / (1024**2), 2),
                "warning": warning,
                "message": f"Memory usage: {memory_percent}%" + (" (healthy)" if is_healthy else " (high)"),
                "critical": memory_percent > 95
            }
        except ImportError:
            return {
                "status": True,
                "message": "psutil not available, skipping memory check",
                "warning": True
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check memory usage",
                "critical": True
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space with detailed analysis"""
        try:
            root_path = Path(self.config.get("AIOS_ROOT"))
            total, used, free = shutil.disk_usage(root_path)
            
            free_percent = (free / total) * 100
            is_healthy = free_percent > 15  # More conservative threshold
            warning = free_percent < 25
            
            # Check specific directories
            directory_usage = {}
            for dir_name, dir_path in [
                ("log", Path(self.config.get("LOG_DIR"))),
                ("cache", Path(self.config.get("CACHE_DIR", "data_core/FractalCache"))),
                ("temp", Path(self.config.get("DEBUG_DIR")))
            ]:
                if dir_path.exists():
                    try:
                        dir_total, dir_used, dir_free = shutil.disk_usage(dir_path)
                        directory_usage[dir_name] = {
                            "free_percent": round((dir_free / dir_total) * 100, 2),
                            "free_gb": round(dir_free / (1024**3), 2),
                            "used_gb": round(dir_used / (1024**3), 2)
                        }
                    except Exception:
                        directory_usage[dir_name] = {"error": "Could not check directory usage"}
            
            return {
                "status": is_healthy,
                "free_percent": round(free_percent, 2),
                "free_gb": round(free / (1024**3), 2),
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "directory_usage": directory_usage,
                "warning": warning,
                "message": f"Disk space: {free_percent:.1f}% free" + (" (healthy)" if is_healthy else " (low)"),
                "critical": free_percent < 5
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check disk space",
                "critical": True
            }
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity with multiple endpoints"""
        try:
            import requests
            
            # Test multiple endpoints
            test_endpoints = [
                ("httpbin", "https://httpbin.org/get"),
                ("google_dns", "https://8.8.8.8"),
                ("cloudflare_dns", "https://1.1.1.1")
            ]
            
            results = {}
            successful_tests = 0
            
            for name, url in test_endpoints:
                try:
                    response = requests.get(url, timeout=5)
                    results[name] = {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds(),
                        "success": response.status_code == 200
                    }
                    if response.status_code == 200:
                        successful_tests += 1
                except Exception as e:
                    results[name] = {
                        "error": str(e),
                        "success": False
                    }
            
            is_healthy = successful_tests > 0
            warning = successful_tests < len(test_endpoints)
            
            return {
                "status": is_healthy,
                "successful_tests": successful_tests,
                "total_tests": len(test_endpoints),
                "test_results": results,
                "warning": warning,
                "message": f"Network connectivity: {successful_tests}/{len(test_endpoints)} tests passed",
                "critical": successful_tests == 0
            }
        except ImportError:
            return {
                "status": True,
                "message": "requests not available, skipping network check",
                "warning": True
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Network connectivity check failed",
                "critical": True
            }
    
    def _check_running_processes(self) -> Dict[str, Any]:
        """Check running processes and system load"""
        try:
            import psutil
            
            # Get system load
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get process count
            process_count = len(psutil.pids())
            
            # Check for AIOS-related processes
            aios_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'aios' in ' '.join(proc.info['cmdline'] or []).lower():
                        aios_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': ' '.join(proc.info['cmdline'] or [])
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check if system is overloaded
            is_healthy = cpu_percent < 80 and load_avg[0] < 4.0
            warning = cpu_percent > 60 or load_avg[0] > 2.0
            
            return {
                "status": is_healthy,
                "cpu_percent": cpu_percent,
                "load_avg": load_avg,
                "process_count": process_count,
                "aios_processes": aios_processes,
                "warning": warning,
                "message": f"System load: CPU {cpu_percent}%, Load {load_avg[0]:.2f}",
                "critical": cpu_percent > 95 or load_avg[0] > 8.0
            }
        except ImportError:
            return {
                "status": True,
                "message": "psutil not available, skipping process check",
                "warning": True
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check running processes",
                "critical": True
            }
    
    def _check_port_availability(self) -> Dict[str, Any]:
        """Check port availability for common services"""
        try:
            import socket
            
            # Common ports to check
            ports_to_check = [
                ("http", 80),
                ("https", 443),
                ("aios_api", 1234),  # LM Studio default
                ("aios_web", 8501),  # Streamlit default
                ("postgres", 5432),
                ("redis", 6379)
            ]
            
            port_results = {}
            available_ports = 0
            
            for name, port in ports_to_check:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex(('localhost', port))
                        port_results[name] = {
                            "port": port,
                            "available": result == 0,
                            "status": "open" if result == 0 else "closed"
                        }
                        if result == 0:
                            available_ports += 1
                except Exception as e:
                    port_results[name] = {
                        "port": port,
                        "available": False,
                        "error": str(e)
                    }
            
            is_healthy = available_ports > 0
            warning = available_ports < len(ports_to_check) // 2
            
            return {
                "status": is_healthy,
                "available_ports": available_ports,
                "total_ports": len(ports_to_check),
                "port_results": port_results,
                "warning": warning,
                "message": f"Port availability: {available_ports}/{len(ports_to_check)} ports available",
                "critical": available_ports == 0
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check port availability",
                "critical": True
            }
    
    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Check SQLite database
            db_path = Path(self.config.get("AIOS_ROOT")) / "aios.db"
            db_exists = db_path.exists()
            
            if db_exists:
                # Test database connection
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    conn.close()
                    db_working = True
                except Exception:
                    db_working = False
            else:
                db_working = False
            
            # For file-based systems, database is optional
            is_healthy = True  # File-based storage doesn't require database
            warning = False
            
            return {
                "status": is_healthy,
                "database_exists": db_exists,
                "database_working": db_working,
                "database_path": str(db_path),
                "warning": warning,
                "storage_type": "file-based",
                "message": "File-based storage system (database optional)",
                "critical": False  # Database is optional for basic functionality
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check database connectivity",
                "critical": False
            }
    
    def _check_api_endpoints(self) -> Dict[str, Any]:
        """Check API endpoint availability"""
        try:
            import requests
            
            # Check LM Studio API
            lm_studio_url = self.config.get("LM_STUDIO_URL", "http://localhost:1234")
            api_endpoints = [
                ("lm_studio_chat", f"{lm_studio_url}/v1/chat/completions"),
                ("lm_studio_embeddings", f"{lm_studio_url}/v1/embeddings"),
                ("lm_studio_models", f"{lm_studio_url}/v1/models")
            ]
            
            endpoint_results = {}
            working_endpoints = 0
            
            for name, url in api_endpoints:
                try:
                    # Use POST for chat/completions and embeddings, GET for models
                    if "models" in url:
                        response = requests.get(url, timeout=5)
                    else:
                        # For chat/completions and embeddings, use POST with minimal payload
                        response = requests.post(url, json={}, timeout=5)
                    
                    endpoint_results[name] = {
                        "url": url,
                        "status_code": response.status_code,
                        "working": response.status_code in [200, 404, 405]  # 405 (Method Not Allowed) is OK for health check
                    }
                    if response.status_code in [200, 404, 405]:
                        working_endpoints += 1
                except Exception as e:
                    endpoint_results[name] = {
                        "url": url,
                        "error": str(e),
                        "working": False
                    }
            
            is_healthy = working_endpoints > 0
            warning = working_endpoints < len(api_endpoints)
            
            return {
                "status": is_healthy,
                "working_endpoints": working_endpoints,
                "total_endpoints": len(api_endpoints),
                "endpoint_results": endpoint_results,
                "warning": warning,
                "message": f"API endpoints: {working_endpoints}/{len(api_endpoints)} working",
                "critical": False  # API endpoints are optional
            }
        except ImportError:
            return {
                "status": True,
                "message": "requests not available, skipping API check",
                "warning": True
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e),
                "message": "Failed to check API endpoints",
                "critical": False
            }
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Process metrics
            current_process = psutil.Process()
            process_memory = current_process.memory_info()
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "process_memory_mb": round(process_memory.rss / (1024**2), 2),
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _store_health_history(self, health_results: Dict[str, Any]):
        """Store health check results in history"""
        with self._lock:
            self._check_history.append(health_results)
            if len(self._check_history) > self._max_history:
                self._check_history.pop(0)
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get health check history"""
        with self._lock:
            return self._check_history[-limit:]
    
    def get_health_trends(self) -> Dict[str, Any]:
        """Analyze health check trends"""
        if len(self._check_history) < 2:
            return {"error": "Insufficient history for trend analysis"}
        
        recent_checks = self._check_history[-10:]  # Last 10 checks
        
        # Analyze trends
        status_counts = {}
        for check in recent_checks:
            status = check.get("overall_status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate trend
        if len(recent_checks) >= 2:
            recent_status = recent_checks[-1].get("overall_status")
            previous_status = recent_checks[-2].get("overall_status")
            trend = "improving" if recent_status == "HEALTHY" and previous_status != "HEALTHY" else "stable"
        else:
            trend = "unknown"
        
        return {
            "status_distribution": status_counts,
            "trend": trend,
            "checks_analyzed": len(recent_checks),
            "most_common_status": max(status_counts, key=status_counts.get) if status_counts else "UNKNOWN"
        }

