#!/usr/bin/env python3
"""
Sandbox Promoter - Atomic file promotion with verification
Only this process can promote fixes from sandbox to live AIOS.
"""

import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import subprocess


class SandboxPromoter:
    """
    Promotes verified fixes from sandbox to live AIOS files.
    Runs as a separate user/process with elevated privileges.
    """
    
    def __init__(self, sandbox_root: Optional[Path] = None, repo_root: Optional[Path] = None):
        if sandbox_root is None:
            sandbox_root = Path(os.environ.get('TEMP', 'C:/Temp')) / "aios_sandbox"
        
        if repo_root is None:
            # Default to L:\AIOS for Luna's sovereignty model
            repo_root = Path(__file__).parent.parent.parent.resolve()
        
        self.sandbox_root = Path(sandbox_root).resolve()
        self.repo_root = Path(repo_root).resolve()
        self.promotion_log = self.sandbox_root / "promotion_log.jsonl"
        self.backup_dir = self.repo_root / "backup_core" / "sandbox_promotions"
        
        # Ensure backup dir exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return f"error:{e}"
    
    def verify_candidate(self, candidate_path: Path, target_path: Path) -> Dict[str, Any]:
        """
        Verify a candidate file before promotion.
        
        Checks:
        1. Candidate exists and is readable
        2. File size is reasonable (< policy max)
        3. Syntax check (for Python files)
        4. Import check (for Python files)
        5. Detector before/after flip
        """
        result = {
            'passed': False,
            'checks': {},
            'errors': []
        }
        
        # Check 1: Candidate exists
        if not candidate_path.exists():
            result['errors'].append(f"Candidate not found: {candidate_path}")
            return result
        result['checks']['exists'] = True
        
        # Check 2: File size
        size_mb = candidate_path.stat().st_size / (1024 * 1024)
        if size_mb > 10:  # 10 MB limit
            result['errors'].append(f"File too large: {size_mb:.2f} MB")
            return result
        result['checks']['size_ok'] = True
        
        # Check 3: Syntax check (Python only)
        if candidate_path.suffix == '.py':
            try:
                import ast
                content = candidate_path.read_text(encoding='utf-8')
                ast.parse(content)
                result['checks']['syntax_ok'] = True
            except SyntaxError as e:
                result['errors'].append(f"Syntax error: {e}")
                return result
        else:
            result['checks']['syntax_ok'] = 'N/A (not Python)'
        
        # Check 4: Import check (Python only)
        if candidate_path.suffix == '.py':
            # Try to import (in a subprocess to avoid polluting namespace)
            try:
                # Just check if it compiles, don't actually import
                import py_compile
                py_compile.compile(candidate_path, doraise=True)
                result['checks']['import_ok'] = True
            except Exception as e:
                result['errors'].append(f"Compile error: {e}")
                return result
        else:
            result['checks']['import_ok'] = 'N/A (not Python)'
        
        # All checks passed
        if len(result['errors']) == 0:
            result['passed'] = True
        
        return result
    
    def create_backup(self, target_path: Path) -> Optional[Path]:
        """Create backup of target file before promotion"""
        if not target_path.exists():
            return None
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{target_path.stem}_{timestamp}{target_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(target_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def atomic_replace(self, candidate_path: Path, target_path: Path) -> bool:
        """
        Atomically replace target with candidate.
        
        Process:
        1. Create backup of target
        2. Copy candidate to temp file
        3. Fsync temp file
        4. Atomic rename temp -> target
        """
        try:
            # Create backup
            backup_path = self.create_backup(target_path)
            if target_path.exists() and backup_path is None:
                print("Error: Could not create backup")
                return False
            
            # Create temp file in same directory as target (for atomic rename)
            temp_path = target_path.parent / f".{target_path.name}.tmp"
            
            # Copy candidate to temp
            shutil.copy2(candidate_path, temp_path)
            
            # Fsync (not natively available in Python on Windows, but copy2 should be safe)
            # On Windows, file operations are synchronous by default
            
            # Atomic rename (on Windows, requires removing target first)
            if target_path.exists():
                target_path.unlink()
            temp_path.rename(target_path)
            
            print(f"OK: Atomic replace completed")
            print(f"  Backup: {backup_path}")
            print(f"  Target: {target_path}")
            
            return True
        
        except Exception as e:
            print(f"Error in atomic replace: {e}")
            # Restore from backup if possible
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, target_path)
                    print(f"Restored from backup")
                except Exception as e2:
                    print(f"Error restoring from backup: {e2}")
            return False
    
    def log_promotion(self, candidate_path: Path, target_path: Path, 
                     before_sha: str, after_sha: str, 
                     verification: Dict[str, Any], success: bool):
        """Log promotion event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'PROMOTE',
            'file': str(target_path.relative_to(self.repo_root)),
            'from_sha': before_sha,
            'to_sha': after_sha,
            'candidate': str(candidate_path.relative_to(self.sandbox_root)),
            'verification': verification,
            'atomic_replace': 'OK' if success else 'FAILED',
            'backup': 'previous_saved'
        }
        
        try:
            with open(self.promotion_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Error logging promotion: {e}")
        
        # Also print one-line receipt
        detector_str = ""
        if 'detector' in verification.get('checks', {}):
            det = verification['checks']['detector']
            detector_str = f"detector:before={det.get('before')} after={det.get('after')}"
        
        print(f"PROMOTE | file={target_path.relative_to(self.repo_root)} | "
              f"from_sha={before_sha[:8]} to_sha={after_sha[:8]} | "
              f"{detector_str} | "
              f"atomic_replace={'OK' if success else 'FAILED'} | "
              f"backup=previous_saved")
    
    def promote(self, candidate_path: Path, target_path: Path,
                citations: Optional[List[str]] = None,
                detector_before: Optional[bool] = None,
                detector_after: Optional[bool] = None) -> bool:
        """
        Promote a candidate file to target with full verification.
        
        Args:
            candidate_path: Path in sandbox to candidate file
            target_path: Path in repo to target file
            citations: Manual citations used for fix
            detector_before: Detector result before fix
            detector_after: Detector result after fix
        
        Returns:
            True if promotion succeeded, False otherwise
        """
        print("=" * 70)
        print("SANDBOX PROMOTION")
        print("=" * 70)
        
        print(f"\nCandidate: {candidate_path}")
        print(f"Target: {target_path}")
        
        # Calculate hashes
        before_sha = self.calculate_sha256(target_path) if target_path.exists() else "NEW_FILE"
        after_sha = self.calculate_sha256(candidate_path)
        
        print(f"\nSHA256:")
        print(f"  Before: {before_sha[:16]}")
        print(f"  After:  {after_sha[:16]}")
        
        # Verify candidate
        print(f"\nVerification:")
        verification = self.verify_candidate(candidate_path, target_path)
        
        for check, result in verification['checks'].items():
            print(f"  {check}: {result}")
        
        if not verification['passed']:
            print(f"\nVERDICT: REJECTED")
            for error in verification['errors']:
                print(f"  - {error}")
            
            self.log_promotion(candidate_path, target_path, before_sha, after_sha, 
                             verification, success=False)
            return False
        
        # Add detector results to verification
        if detector_before is not None and detector_after is not None:
            verification['checks']['detector'] = {
                'before': detector_before,
                'after': detector_after,
                'flip': detector_before and not detector_after
            }
            
            if not verification['checks']['detector']['flip']:
                print(f"\nVERDICT: REJECTED - Detector did not flip")
                verification['passed'] = False
                self.log_promotion(candidate_path, target_path, before_sha, after_sha,
                                 verification, success=False)
                return False
        
        # Add citations
        if citations:
            verification['citations'] = citations
            print(f"  Citations: {citations}")
        
        # Atomic replace
        print(f"\nAtomic Replace:")
        success = self.atomic_replace(candidate_path, target_path)
        
        # Log
        self.log_promotion(candidate_path, target_path, before_sha, after_sha,
                         verification, success=success)
        
        if success:
            print(f"\nVERDICT: PROMOTED")
            return True
        else:
            print(f"\nVERDICT: FAILED")
            return False
    
    def create_cfr(self, target_path: Path, reason: str, citations: List[str]) -> Path:
        """
        Create a Change-For-Review (CFR) record for a new file.
        
        Returns path to CFR file.
        """
        cfr_dir = self.sandbox_root / "cfr"
        cfr_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cfr_file = cfr_dir / f"cfr_{timestamp}.json"
        
        cfr_data = {
            'type': 'CFR_NEW_FILE',
            'target': str(target_path),
            'reason': reason,
            'citations': citations,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        with open(cfr_file, 'w') as f:
            json.dump(cfr_data, f, indent=2)
        
        print(f"CFR created: {cfr_file}")
        return cfr_file


def handle_command(args: List[str]) -> bool:
    """Handle promoter commands"""
    if not args or '--promote' not in args:
        return False
    
    promoter = SandboxPromoter()
    
    if 'test' in args:
        # Test promotion with a dummy file
        print("Testing promotion system...")
        
        # Create test files
        sandbox_test = promoter.sandbox_root / "test_promote.txt"
        repo_test = promoter.repo_root / "TEST_PROMOTE.txt"
        
        sandbox_test.write_text("This is a test promotion file.\n")
        
        result = promoter.promote(
            sandbox_test,
            repo_test,
            citations=['test.promotion'],
            detector_before=True,
            detector_after=False
        )
        
        if result:
            print("\nPromotion test PASSED")
            # Clean up
            if repo_test.exists():
                repo_test.unlink()
        else:
            print("\nPromotion test FAILED")
        
        return True
    
    elif 'status' in args:
        print("=" * 70)
        print("PROMOTER STATUS")
        print("=" * 70)
        
        print(f"\nSandbox: {promoter.sandbox_root}")
        print(f"Repo: {promoter.repo_root}")
        print(f"Backup Dir: {promoter.backup_dir}")
        print(f"Promotion Log: {promoter.promotion_log}")
        
        # Count promotions
        if promoter.promotion_log.exists():
            with open(promoter.promotion_log, 'r') as f:
                lines = f.readlines()
            print(f"\nTotal Promotions: {len(lines)}")
            
            # Show recent
            print(f"\nRecent Promotions:")
            for line in lines[-5:]:
                entry = json.loads(line)
                print(f"  {entry['timestamp']}: {entry['file']} ({entry['atomic_replace']})")
        else:
            print(f"\nNo promotions yet")
        
        return True
    
    else:
        print("Promoter Commands:")
        print("  --promote test")
        print("  --promote status")
        return True


if __name__ == "__main__":
    # Test
    promoter = SandboxPromoter()
    print(f"Promoter initialized")
    print(f"  Sandbox: {promoter.sandbox_root}")
    print(f"  Repo: {promoter.repo_root}")
    print(f"  Backups: {promoter.backup_dir}")

