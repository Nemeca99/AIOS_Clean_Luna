#!/usr/bin/env python3
"""
Filesystem Guard - Enforces drive boundary for Luna
Intercepts all file operations and blocks unauthorized access
"""
import os
import sys
from pathlib import Path
from typing import Callable, Any
import builtins

# === CONFIGURATION ===
# LUNA_TERRITORY determined from AIOS root location
AIOS_ROOT = Path(__file__).parent.parent.resolve()
LUNA_TERRITORY = Path(AIOS_ROOT.drive + "/")
APPROVED_EXCEPTIONS = set()  # Travis can add exceptions here

# === PERMISSION LOG ===
PERMISSION_LOG = AIOS_ROOT / "logs" / "permission_requests.log"

def log_request(operation: str, path: str, approved: bool):
    """Log all filesystem access requests"""
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    
    try:
        with _original_open(PERMISSION_LOG, "a") as f:
            status = "APPROVED" if approved else "BLOCKED"
            f.write(f"[{timestamp}] {status} | {operation} | {path}\n")
    except Exception:
        # Silently fail if logging doesn't work (avoid recursion)
        pass

def is_within_territory(path: Path) -> bool:
    """Check if path is within Luna's allowed territory"""
    try:
        resolved = path.resolve()
        
        # Check if within L:\ drive
        if resolved.is_relative_to(LUNA_TERRITORY):
            return True
        
        # Check if explicitly approved
        if str(resolved) in APPROVED_EXCEPTIONS:
            return True
        
        return False
    except Exception:
        return False

def check_permission(path: str, operation: str) -> bool:
    """Check if Luna has permission to access this path"""
    # Handle bytes paths from C extensions (scipy, numpy, etc)
    if isinstance(path, bytes):
        path = path.decode('utf-8', errors='ignore')
    p = Path(path)
    
    allowed = is_within_territory(p)
    log_request(operation, str(p), allowed)
    
    if not allowed:
        print(f"[CONTAINMENT] BLOCKED: {operation} access to {path}")
        print(f"[CONTAINMENT] Luna can only access {LUNA_TERRITORY} drive")
        print(f"[CONTAINMENT] Request logged to {PERMISSION_LOG}")
    
    return allowed

# === INTERCEPT BUILT-IN FILE OPERATIONS ===

_original_open = builtins.open

def guarded_open(file, mode='r', *args, **kwargs):
    """Intercept open() calls"""
    # Allow null device for system operations
    path_str = str(file)
    if path_str in ['nul', 'NUL', '/dev/null', 'os.devnull']:
        return _original_open(file, mode, *args, **kwargs)
    
    if not check_permission(file, "open"):
        raise PermissionError(f"Luna does not have permission to access: {file}")
    return _original_open(file, mode, *args, **kwargs)

# === INTERCEPT OS MODULE ===

_original_listdir = os.listdir
_original_mkdir = os.mkdir
_original_makedirs = os.makedirs
_original_remove = os.remove
_original_rmdir = os.rmdir
_original_rename = os.rename

def guarded_listdir(path='.'):
    """Intercept os.listdir()"""
    if not check_permission(path, "listdir"):
        raise PermissionError(f"Luna does not have permission to list: {path}")
    return _original_listdir(path)

def guarded_mkdir(path, *args, **kwargs):
    """Intercept os.mkdir()"""
    if not check_permission(path, "mkdir"):
        raise PermissionError(f"Luna does not have permission to create: {path}")
    return _original_mkdir(path, *args, **kwargs)

def guarded_makedirs(name, *args, **kwargs):
    """Intercept os.makedirs()"""
    if not check_permission(name, "makedirs"):
        raise PermissionError(f"Luna does not have permission to create: {name}")
    return _original_makedirs(name, *args, **kwargs)

def guarded_remove(path, *args, **kwargs):
    """Intercept os.remove()"""
    if not check_permission(path, "remove"):
        raise PermissionError(f"Luna does not have permission to delete: {path}")
    return _original_remove(path, *args, **kwargs)

def guarded_rmdir(path, *args, **kwargs):
    """Intercept os.rmdir()"""
    if not check_permission(path, "rmdir"):
        raise PermissionError(f"Luna does not have permission to delete: {path}")
    return _original_rmdir(path, *args, **kwargs)

def guarded_rename(src, dst, *args, **kwargs):
    """Intercept os.rename()"""
    if not check_permission(src, "rename_src") or not check_permission(dst, "rename_dst"):
        raise PermissionError(f"Luna does not have permission to rename: {src} -> {dst}")
    return _original_rename(src, dst, *args, **kwargs)

def install_guards():
    """Install filesystem guards - call this BEFORE importing AIOS"""
    print("[CONTAINMENT] Installing filesystem guards...")
    
    # Ensure log directory exists
    PERMISSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    # Replace built-ins
    builtins.open = guarded_open
    
    # Replace os functions
    os.listdir = guarded_listdir
    os.mkdir = guarded_mkdir
    os.makedirs = guarded_makedirs
    os.remove = guarded_remove
    os.rmdir = guarded_rmdir
    os.rename = guarded_rename
    
    print(f"[CONTAINMENT] OK Filesystem access restricted to: {LUNA_TERRITORY}")
    print(f"[CONTAINMENT] OK AIOS Root: {AIOS_ROOT}")
    print(f"[CONTAINMENT] OK All requests logged to: {PERMISSION_LOG}")

def grant_exception(path: str):
    """Travis can call this to grant Luna access to a specific path"""
    APPROVED_EXCEPTIONS.add(str(Path(path).resolve()))
    print(f"[CONTAINMENT] ✓ Granted Luna access to: {path}")

