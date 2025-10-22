#!/usr/bin/env python3
"""
Differential Auditing - Only audit what changed.
Massive speed improvement: 90s → 15s for single-core changes.
"""

import subprocess
import hashlib
import json
import logging
from pathlib import Path
from typing import List, Set, Dict, Optional

logger = logging.getLogger(__name__)


class DifferentialAuditor:
    """
    Determines which cores need auditing based on git diff.
    Caches results by file hash to skip unchanged files.
    """
    
    def __init__(self, root_dir: Path, cache_file: Path = None):
        self.root = root_dir
        self.cache_file = cache_file or (root_dir / "reports" / ".audit_cache.json")
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load audit cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return {'version': '1.0.0', 'file_hashes': {}, 'core_results': {}}
    
    def _save_cache(self):
        """Save audit cache to disk."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _hash_file(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        try:
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.debug(f"Failed to hash {file_path}: {e}")
            return ""
    
    def _get_changed_files_from_git(self, base_branch: str = "main") -> List[str]:
        """
        Get list of changed files from git diff.
        
        Args:
            base_branch: Branch to compare against (default: main)
        
        Returns:
            List of changed file paths
        """
        try:
            # Get merge base (common ancestor)
            merge_base_cmd = ['git', 'merge-base', base_branch, 'HEAD']
            result = subprocess.run(
                merge_base_cmd,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # Fallback: just compare against HEAD~1
                logger.debug("No merge-base found, using HEAD~1")
                merge_base = "HEAD~1"
            else:
                merge_base = result.stdout.strip()
            
            # Get changed files
            diff_cmd = ['git', 'diff', '--name-only', merge_base]
            result = subprocess.run(
                diff_cmd,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
                logger.info(f"Git diff found {len(files)} changed files")
                return files
            
        except Exception as e:
            logger.warning(f"Git diff failed: {e}")
        
        return []
    
    def _file_has_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last audit."""
        file_str = str(file_path.relative_to(self.root))
        current_hash = self._hash_file(file_path)
        cached_hash = self.cache['file_hashes'].get(file_str)
        
        return current_hash != cached_hash
    
    def _update_file_hash(self, file_path: Path):
        """Update file hash in cache."""
        file_str = str(file_path.relative_to(self.root))
        current_hash = self._hash_file(file_path)
        self.cache['file_hashes'][file_str] = current_hash
    
    def get_cores_to_audit(self, 
                          all_cores: List[str], 
                          force_full: bool = False,
                          use_git: bool = True) -> Set[str]:
        """
        Determine which cores need auditing.
        
        Args:
            all_cores: List of all discovered cores
            force_full: If True, audit all cores (ignore cache)
            use_git: If True, use git diff to find changes
        
        Returns:
            Set of core names that need auditing
        """
        if force_full:
            logger.info("Force full audit - auditing all cores")
            return set(all_cores)
        
        cores_to_audit = set()
        
        if use_git:
            # Method 1: Git diff
            changed_files = self._get_changed_files_from_git()
            
            for file_path in changed_files:
                # Extract core name from path
                parts = file_path.split('/')
                if len(parts) > 0 and parts[0].endswith('_core'):
                    core_name = parts[0]
                    if core_name in all_cores:
                        cores_to_audit.add(core_name)
                        logger.debug(f"Core {core_name} changed (from git diff)")
        
        # Method 2: Hash comparison for all cores
        # (Catches changes not in git, like new files)
        for core_name in all_cores:
            core_path = self.root / core_name
            
            if not core_path.exists():
                continue
            
            # Check all Python files in core
            for py_file in core_path.rglob("*.py"):
                if self._file_has_changed(py_file):
                    cores_to_audit.add(core_name)
                    logger.debug(f"Core {core_name} changed (file hash: {py_file.name})")
                    break  # One changed file is enough
        
        if not cores_to_audit:
            logger.info("No changes detected - no cores to audit")
        else:
            logger.info(f"Differential audit: {len(cores_to_audit)}/{len(all_cores)} cores need auditing")
        
        return cores_to_audit
    
    def update_cache_for_core(self, core_name: str, audit_result: Dict):
        """
        Update cache after auditing a core.
        
        Args:
            core_name: Name of the core
            audit_result: Audit result dict (score, status, etc.)
        """
        core_path = self.root / core_name
        
        if not core_path.exists():
            return
        
        # Update file hashes for all Python files in core
        for py_file in core_path.rglob("*.py"):
            self._update_file_hash(py_file)
        
        # Store audit result
        self.cache['core_results'][core_name] = {
            'score': audit_result.get('score', 0),
            'status': audit_result.get('status', 'UNKNOWN'),
            'last_audit': audit_result.get('timestamp', '')
        }
        
        # Save cache to disk
        self._save_cache()
    
    def get_cached_result(self, core_name: str) -> Optional[Dict]:
        """Get cached audit result for core."""
        return self.cache['core_results'].get(core_name)
    
    def invalidate_cache(self):
        """Clear entire cache (force full audit on next run)."""
        self.cache = {'version': '1.0.0', 'file_hashes': {}, 'core_results': {}}
        self._save_cache()
        logger.info("Audit cache invalidated")

