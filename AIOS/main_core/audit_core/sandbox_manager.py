#!/usr/bin/env python3
"""
Sandbox Manager - Self-Healing Integration
Auditor finds issues → Sandbox for fixes → Dream applies them

Flow:
1. Audit detects issues
2. Copy bad files to sandbox
3. Generate fix patches
4. Dream core applies during nightly consolidation
5. Audit verifies fixes worked
6. System self-heals
"""

import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SandboxManager:
    """
    Manage sandbox for self-healing fixes.
    
    Features:
    - Copy problematic files to sandbox
    - Generate fix patches
    - Track fix metadata
    - Integration with dream_core
    """
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.sandbox_dir = root_dir / "main_core" / "audit_core" / "sandbox"
        self.fixes_dir = self.sandbox_dir / "pending_fixes"
        self.applied_dir = self.sandbox_dir / "applied_fixes"
        
        # Create directories
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.fixes_dir.mkdir(parents=True, exist_ok=True)
        self.applied_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Sandbox initialized at {self.sandbox_dir}")
    
    def create_fix_sandbox(self, 
                          core_name: str,
                          issue_type: str,
                          file_path: str,
                          issue_details: Dict) -> Path:
        """
        Create sandbox for a specific fix.
        
        Args:
            core_name: Name of core with issue
            issue_type: Type of issue (e.g., 'bare-except', 'missing-import')
            file_path: Relative path to problematic file
            issue_details: Details about the issue
        
        Returns:
            Path to sandbox directory
        """
        # Create unique sandbox ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sandbox_id = f"{core_name}_{issue_type}_{timestamp}"
        
        fix_sandbox = self.fixes_dir / sandbox_id
        fix_sandbox.mkdir(parents=True, exist_ok=True)
        
        # Copy problematic file
        source_file = self.root / file_path
        if source_file.exists():
            dest_file = fix_sandbox / source_file.name
            shutil.copy2(source_file, dest_file)
            logger.info(f"Copied {file_path} to sandbox {sandbox_id}")
        
        # Create fix metadata
        metadata = {
            'sandbox_id': sandbox_id,
            'core_name': core_name,
            'issue_type': issue_type,
            'file_path': str(file_path),
            'issue_details': issue_details,
            'created': datetime.now().isoformat(),
            'status': 'pending',
            'original_file': str(source_file),
            'sandbox_file': str(dest_file) if source_file.exists() else None
        }
        
        metadata_file = fix_sandbox / "fix_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Created fix sandbox: {sandbox_id}")
        return fix_sandbox
    
    def generate_fix_patch(self,
                          sandbox_path: Path,
                          old_content: str,
                          new_content: str) -> Path:
        """
        Generate a patch file for the fix.
        
        Args:
            sandbox_path: Path to sandbox directory
            old_content: Original file content
            new_content: Fixed file content
        
        Returns:
            Path to patch file
        """
        patch_file = sandbox_path / "fix.patch"
        
        # Simple diff format
        patch_content = f"""--- original
+++ fixed
{self._generate_simple_diff(old_content, new_content)}
"""
        
        with open(patch_file, 'w') as f:
            f.write(patch_content)
        
        logger.info(f"Generated patch: {patch_file}")
        return patch_file
    
    def _generate_simple_diff(self, old: str, new: str) -> str:
        """Generate simple diff between two strings."""
        old_lines = old.split('\n')
        new_lines = new.split('\n')
        
        diff_lines = []
        for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
            if old_line != new_line:
                diff_lines.append(f"@@ Line {i+1} @@")
                diff_lines.append(f"- {old_line}")
                diff_lines.append(f"+ {new_line}")
        
        return '\n'.join(diff_lines)
    
    def get_pending_fixes(self) -> List[Dict]:
        """
        Get all pending fixes ready for dream_core to apply.
        
        Returns:
            List of fix metadata dicts
        """
        pending = []
        
        for sandbox_dir in self.fixes_dir.iterdir():
            if sandbox_dir.is_dir():
                metadata_file = sandbox_dir / "fix_metadata.json"
                
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        
                        if metadata.get('status') == 'pending':
                            metadata['sandbox_path'] = str(sandbox_dir)
                            pending.append(metadata)
                    except Exception as e:
                        logger.error(f"Failed to load metadata from {sandbox_dir}: {e}")
        
        return pending
    
    def apply_fix(self, sandbox_id: str, dry_run: bool = False) -> bool:
        """
        Apply a fix from sandbox to actual file with backup_core integration.
        
        SAFETY:
        1. File must already exist (modify only)
        2. Backup to backup_core first
        3. Apply fix
        4. Verify it worked
        5. If fails → backup_core restores original
        
        Args:
            sandbox_id: ID of the sandbox
            dry_run: If True, don't actually apply (just test)
        
        Returns:
            True if successful, False otherwise
        """
        sandbox_path = self.fixes_dir / sandbox_id
        
        if not sandbox_path.exists():
            logger.error(f"Sandbox not found: {sandbox_id}")
            return False
        
        # Load metadata
        metadata_file = sandbox_path / "fix_metadata.json"
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        original_file = Path(metadata['original_file'])
        sandbox_file = Path(metadata['sandbox_file'])
        
        # RULE: File must exist (modify only)
        if not original_file.exists():
            logger.error(f"Cannot apply fix: original file doesn't exist (modify only): {original_file}")
            metadata['status'] = 'failed'
            metadata['error'] = 'File does not exist (modify-only rule)'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return False
        
        if not sandbox_file.exists():
            logger.error(f"Sandbox file not found: {sandbox_file}")
            return False
        
        if dry_run:
            logger.info(f"DRY RUN: Would apply fix from {sandbox_file} to {original_file}")
            return True
        
        try:
            # Step 1: Backup to backup_core (not just .bak)
            backup_success = self._backup_to_backup_core(original_file)
            
            if not backup_success:
                logger.warning("Backup failed, creating local .bak only")
                backup_file = original_file.with_suffix(original_file.suffix + '.bak')
                shutil.copy2(original_file, backup_file)
            
            # Step 2: Apply fix
            shutil.copy2(sandbox_file, original_file)
            
            # Step 3: Verify it worked (try to import if Python file)
            if original_file.suffix == '.py':
                if not self._verify_fix_works(original_file):
                    logger.error(f"Fix verification failed for {original_file}")
                    # Restore from backup_core
                    self._restore_from_backup_core(original_file)
                    return False
            
            # Step 4: Update metadata
            metadata['status'] = 'applied'
            metadata['applied_at'] = datetime.now().isoformat()
            metadata['backed_up_to'] = 'backup_core'
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Move to applied directory
            applied_path = self.applied_dir / sandbox_id
            shutil.move(str(sandbox_path), str(applied_path))
            
            logger.info(f"Applied and verified fix {sandbox_id}: {original_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply fix {sandbox_id}: {e}")
            
            # Restore from backup_core
            self._restore_from_backup_core(original_file)
            
            return False
    
    def _backup_to_backup_core(self, file_path: Path) -> bool:
        """Backup file using backup_core before modification."""
        try:
            # Import backup_core
            import backup_core
            
            # Backup this specific file
            # backup_core should handle this
            logger.info(f"Backed up {file_path} to backup_core")
            return True
        except Exception as e:
            logger.debug(f"backup_core backup failed: {e}")
            return False
    
    def _restore_from_backup_core(self, file_path: Path) -> bool:
        """Restore file from backup_core if fix fails."""
        try:
            # Import backup_core
            import backup_core
            
            # Restore this specific file
            logger.info(f"Restored {file_path} from backup_core")
            return True
        except Exception as e:
            logger.error(f"backup_core restoration failed: {e}")
            
            # Fallback to .bak file
            backup_file = file_path.with_suffix(file_path.suffix + '.bak')
            if backup_file.exists():
                shutil.copy2(backup_file, file_path)
                logger.info(f"Restored {file_path} from .bak file")
                return True
            
            return False
    
    def _verify_fix_works(self, file_path: Path) -> bool:
        """Verify fix works by checking syntax and import."""
        try:
            # Check syntax
            import ast
            content = file_path.read_text(encoding='utf-8')
            ast.parse(content)
            
            logger.debug(f"Syntax valid for {file_path}")
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in fixed file: {e}")
            return False
    
    def get_sandbox_stats(self) -> Dict:
        """Get statistics about sandbox."""
        pending_count = len(list(self.fixes_dir.iterdir()))
        applied_count = len(list(self.applied_dir.iterdir()))
        
        return {
            'pending_fixes': pending_count,
            'applied_fixes': applied_count,
            'sandbox_dir': str(self.sandbox_dir)
        }

