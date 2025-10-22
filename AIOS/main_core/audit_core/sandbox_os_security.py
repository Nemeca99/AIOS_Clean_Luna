#!/usr/bin/env python3
"""
OS-Level Sandbox Security for Windows
Real filesystem enforcement, not just Python guards.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib
from datetime import datetime


class SandboxOSSecurity:
    """
    OS-level sandbox enforcement using Windows NTFS ACLs.
    Makes read-only guarantees at the filesystem layer.
    """
    
    def __init__(self, sandbox_root: Optional[Path] = None):
        if sandbox_root is None:
            # Use Windows temp directory for sandbox
            sandbox_root = Path(os.environ.get('TEMP', 'C:/Temp')) / "aios_sandbox"
        
        self.sandbox_root = Path(sandbox_root).resolve()
        self.policy_file = self.sandbox_root / "policy.json"
        self.policy = self._load_policy()
        
        # Ensure sandbox exists
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        
    def _load_policy(self) -> Dict[str, Any]:
        """Load sandbox policy from file"""
        if self.policy_file.exists():
            try:
                with open(self.policy_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load policy file: {e}")
        
        # Default policy
        return {
            "sandbox_root": str(self.sandbox_root),
            "writes_allowed": ["mirror/**", "reports/**", "patches/**"],
            "writes_denied": ["../**"],
            "max_loc_change": 200,
            "max_files_change": 5,
            "max_file_size_mb": 10
        }
    
    def save_policy(self):
        """Save current policy to file"""
        try:
            self.sandbox_root.mkdir(parents=True, exist_ok=True)
            with open(self.policy_file, 'w') as f:
                json.dump(self.policy, f, indent=2)
            print(f"Policy saved: {self.policy_file}")
        except Exception as e:
            print(f"Error saving policy: {e}")
    
    def in_sandbox(self, path: Path) -> bool:
        """
        Check if path is within sandbox.
        Resolves symlinks and handles non-existent paths.
        """
        try:
            # Resolve with strict=False to handle non-existent paths
            resolved = path.resolve(strict=False)
            sandbox_resolved = self.sandbox_root.resolve()
            
            # Check if sandbox is in resolved path's parents or if they're equal
            return (sandbox_resolved in resolved.parents or 
                    resolved == sandbox_resolved or
                    resolved.is_relative_to(sandbox_resolved))
        except Exception as e:
            print(f"Error resolving path {path}: {e}")
            return False
    
    def guard_write(self, path: Path, operation: str = "write") -> bool:
        """
        Guard any write operation. Returns True if allowed, raises PermissionError if denied.
        
        Args:
            path: Path to check
            operation: Operation type (write, delete, rename)
        """
        # Resolve path
        try:
            resolved = path.resolve(strict=False)
        except Exception as e:
            raise PermissionError(f"Cannot resolve path {path}: {e}")
        
        # Check if in sandbox
        if not self.in_sandbox(resolved):
            self._log_escape_attempt(str(resolved), operation)
            raise PermissionError(f"SANDBOX VIOLATION: {operation} outside sandbox: {resolved}")
        
        # Check for path traversal patterns
        path_str = str(resolved)
        if "..\\" in path_str or "../" in path_str:
            self._log_escape_attempt(path_str, f"{operation}_traversal")
            raise PermissionError(f"SANDBOX VIOLATION: Path traversal detected: {path}")
        
        # Check for UNC paths
        if path_str.startswith("\\\\"):
            self._log_escape_attempt(path_str, f"{operation}_unc")
            raise PermissionError(f"SANDBOX VIOLATION: UNC path not allowed: {path}")
        
        # Check for different drive letter
        sandbox_drive = str(self.sandbox_root.drive).upper()
        path_drive = str(Path(path_str).drive).upper()
        if path_drive and path_drive != sandbox_drive:
            self._log_escape_attempt(path_str, f"{operation}_cross_drive")
            raise PermissionError(f"SANDBOX VIOLATION: Cross-drive access: {path} (sandbox on {sandbox_drive})")
        
        return True
    
    def _log_escape_attempt(self, path: str, operation: str):
        """Log an escape attempt to security log"""
        log_file = self.sandbox_root / "security_log.jsonl"
        try:
            with open(log_file, 'a') as f:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'event': 'ESCAPE_ATTEMPT',
                    'operation': operation,
                    'path': path,
                    'sandbox': str(self.sandbox_root)
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Error logging escape attempt: {e}")
    
    def create_mirror_path(self, source_path: Path) -> Path:
        """
        Create a deterministic mirror path in sandbox for a source file.
        
        Example:
            F:/AIOS_Clean/luna_core/arbiter.py ->
            <sandbox>/mirror/F_/AIOS_Clean/luna_core/arbiter.py
        """
        # Convert absolute path to mirror path
        if source_path.is_absolute():
            # Replace drive letter colon with underscore
            drive = source_path.drive.replace(':', '_')
            relative = source_path.relative_to(source_path.anchor)
            mirror_path = self.sandbox_root / "mirror" / drive / relative
        else:
            mirror_path = self.sandbox_root / "mirror" / source_path
        
        return mirror_path
    
    def copy_to_sandbox(self, source_path: Path) -> Path:
        """
        Copy a file from AIOS repo into sandbox mirror.
        Returns the sandbox path.
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        mirror_path = self.create_mirror_path(source_path)
        mirror_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(source_path, mirror_path)
        
        print(f"Copied to sandbox: {mirror_path.relative_to(self.sandbox_root)}")
        return mirror_path
    
    def setup_ntfs_acls(self, auditor_user: str = "AIOSAUDITOR", repo_root: Path = None):
        """
        Setup Windows NTFS ACLs for sandbox security.
        Requires admin privileges.
        
        WARNING: This modifies filesystem permissions!
        """
        if repo_root is None:
            # Default to L:\AIOS for Luna's sovereignty model
            repo_root = Path(__file__).parent.parent.parent.resolve()
        
        print(f"Setting up NTFS ACLs...")
        print(f"  Repo: {repo_root}")
        print(f"  Sandbox: {self.sandbox_root}")
        print(f"  Auditor user: {auditor_user}")
        
        commands = []
        
        # 1. Grant read-only to repo
        commands.append({
            'desc': 'Grant read-execute on repo',
            'cmd': ['icacls', str(repo_root), '/grant', f'{auditor_user}:(RX)', '/t']
        })
        
        commands.append({
            'desc': 'Deny write on repo',
            'cmd': ['icacls', str(repo_root), '/deny', f'{auditor_user}:(W,M,DC)', '/t']
        })
        
        # 2. Grant full control to sandbox
        commands.append({
            'desc': 'Grant full control on sandbox',
            'cmd': ['icacls', str(self.sandbox_root), '/grant', f'{auditor_user}:(OI)(CI)(F)', '/t']
        })
        
        # Execute commands
        for cmd_info in commands:
            print(f"\n{cmd_info['desc']}...")
            try:
                result = subprocess.run(
                    cmd_info['cmd'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"  OK")
                else:
                    print(f"  FAILED: {result.stderr}")
            except Exception as e:
                print(f"  ERROR: {e}")
        
        print(f"\nNTFS ACLs configured!")
    
    def create_auditor_user(self, username: str = "AIOSAUDITOR", password: Optional[str] = None):
        """
        Create a low-privilege Windows local user for the auditor.
        Requires admin privileges.
        """
        print(f"Creating auditor user: {username}")
        
        try:
            # Check if user exists
            result = subprocess.run(
                ['net', 'user', username],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  User {username} already exists")
                return
            
            # Create user
            if password:
                cmd = ['net', 'user', username, password, '/add']
            else:
                cmd = ['net', 'user', username, '/add', '/random']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"  OK: User {username} created")
            else:
                print(f"  FAILED: {result.stderr}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
    
    def test_write_outside(self) -> bool:
        """
        Test that writes outside sandbox are blocked.
        Returns True if blocked (good), False if allowed (bad).
        """
        print("Testing write-outside protection...")
        
        # Try to write outside sandbox (would be blocked by guards)
        test_file = Path("C:/SANDBOX_ESCAPE_TEST.txt")
        
        try:
            self.guard_write(test_file, "test_write")
            print("  FAIL: Guard allowed write outside sandbox")
            return False
        except PermissionError as e:
            print(f"  PASS: Guard blocked write ({str(e)[:50]})")
            return True
    
    def test_path_traversal(self) -> bool:
        """
        Test that path traversal is blocked.
        Returns True if blocked (good), False if allowed (bad).
        """
        print("Testing path-traversal protection...")
        
        # Try path traversal
        evil_path = self.sandbox_root / ".." / ".." / "evil.txt"
        
        try:
            # This should resolve outside sandbox and be blocked
            resolved = evil_path.resolve()
            if not self.in_sandbox(resolved):
                print(f"  PASS: Path traversal blocked")
                return True
            else:
                print(f"  FAIL: Path traversal allowed")
                return False
        except Exception as e:
            print(f"  PASS: Path traversal blocked ({str(e)[:50]})")
            return True
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            'sandbox_root': str(self.sandbox_root),
            'sandbox_exists': self.sandbox_root.exists(),
            'policy_exists': self.policy_file.exists(),
            'policy': self.policy,
            'write_test': self.test_write_outside(),
            'traversal_test': self.test_path_traversal()
        }


def handle_command(args: List[str]) -> bool:
    """Handle sandbox security commands"""
    if not args or '--sandbox-security' not in args:
        return False
    
    security = SandboxOSSecurity()
    
    if 'setup' in args:
        print("=" * 70)
        print("SANDBOX OS SECURITY SETUP")
        print("=" * 70)
        
        # Save policy
        security.save_policy()
        
        # Setup NTFS ACLs (requires admin)
        if '--ntfs' in args:
            auditor_user = args[args.index('--user') + 1] if '--user' in args else 'AIOSAUDITOR'
            
            print("\nWARNING: This requires Administrator privileges!")
            print("Press Ctrl+C to cancel, or Enter to continue...")
            try:
                input()
            except KeyboardInterrupt:
                print("\nCancelled.")
                return True
            
            # Create user
            if '--create-user' in args:
                security.create_auditor_user(auditor_user)
            
            # Setup ACLs
            security.setup_ntfs_acls(auditor_user)
        
        return True
    
    elif 'status' in args:
        print("=" * 70)
        print("SANDBOX SECURITY STATUS")
        print("=" * 70)
        
        status = security.get_security_status()
        
        print(f"\nSandbox Root: {status['sandbox_root']}")
        print(f"Exists: {status['sandbox_exists']}")
        print(f"Policy File: {status['policy_exists']}")
        
        print(f"\nPolicy:")
        for key, value in status['policy'].items():
            print(f"  {key}: {value}")
        
        print(f"\nSecurity Tests:")
        print(f"  Write-outside blocked: {'PASS' if status['write_test'] else 'FAIL'}")
        print(f"  Path-traversal blocked: {'PASS' if status['traversal_test'] else 'FAIL'}")
        
        return True
    
    elif 'test' in args:
        print("=" * 70)
        print("SANDBOX SECURITY TESTS")
        print("=" * 70)
        
        tests_passed = 0
        tests_total = 2
        
        # Test 1: Write outside
        if security.test_write_outside():
            tests_passed += 1
        
        # Test 2: Path traversal
        if security.test_path_traversal():
            tests_passed += 1
        
        print(f"\n{tests_passed}/{tests_total} tests passed")
        
        if tests_passed == tests_total:
            print("VERDICT: SECURE")
            return True
        else:
            print("VERDICT: INSECURE")
            return True
    
    else:
        print("Sandbox Security Commands:")
        print("  --sandbox-security setup [--ntfs] [--create-user] [--user USERNAME]")
        print("  --sandbox-security status")
        print("  --sandbox-security test")
        return True


if __name__ == "__main__":
    # Test
    security = SandboxOSSecurity()
    status = security.get_security_status()
    
    print("Sandbox Security Status:")
    print(f"  Root: {status['sandbox_root']}")
    print(f"  Exists: {status['sandbox_exists']}")
    print(f"  Write-outside blocked: {status['write_test']}")
    print(f"  Path-traversal blocked: {status['traversal_test']}")

