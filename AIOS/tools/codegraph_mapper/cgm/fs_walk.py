"""
Filesystem walker for CodeGraph Mapper
Walks AIOS tree and builds file inventory with hashes
"""

import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Callable
from fnmatch import fnmatch


class FileInventory:
    """Builds file inventory with hashes and metadata"""
    
    def __init__(self, root: Path, include: List[str], exclude: List[str], 
                 logger, progress_callback: Callable = None):
        self.root = root
        self.include = include or ["**/*"]
        self.exclude = exclude or []
        self.logger = logger
        self.progress_callback = progress_callback
        
        self.files = {}  # path -> metadata
        self.files_scanned = 0
        self.dirs_scanned = 0
        self.bytes_hashed = 0
    
    def walk(self) -> Dict[str, Dict]:
        """
        Walk filesystem and build inventory
        Returns: {path: {size, mtime, sha256, mime, ...}}
        """
        self.logger.info("scan_start", root=str(self.root))
        
        for dirpath, dirnames, filenames in os.walk(self.root):
            # Filter directories based on exclude patterns
            dirnames[:] = [d for d in dirnames if not self._should_exclude(os.path.join(dirpath, d))]
            
            self.dirs_scanned += 1
            
            for filename in filenames:
                filepath = Path(dirpath) / filename
                
                # Check if file matches include/exclude patterns
                if self._should_exclude(filepath):
                    continue
                
                if not any(self._matches_pattern(filepath, pattern) for pattern in self.include):
                    continue
                
                # Build metadata
                try:
                    stat = filepath.stat()
                    
                    metadata = {
                        "path": str(filepath),
                        "size": stat.st_size,
                        "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                        "mime": self._guess_mime(filepath),
                    }
                    
                    # Hash file content (chunked for large files)
                    metadata["sha256"] = self._hash_file(filepath)
                    
                    self.files[str(filepath)] = metadata
                    self.files_scanned += 1
                    self.bytes_hashed += stat.st_size
                    
                    # Progress callback
                    if self.progress_callback and self.files_scanned % 100 == 0:
                        self.progress_callback(self.files_scanned, self.dirs_scanned)
                    
                except (OSError, PermissionError) as e:
                    self.logger.warn("file_skip", path=str(filepath), reason=str(e))
        
        self.logger.info("scan_complete", 
                        files=self.files_scanned, 
                        dirs=self.dirs_scanned,
                        bytes_hashed=self.bytes_hashed)
        
        return self.files
    
    def _hash_file(self, filepath: Path) -> str:
        """Compute SHA-256 hash of file (chunked)"""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(65536):  # 64KB chunks
                    hasher.update(chunk)
        except Exception as e:
            self.logger.warn("hash_failed", path=str(filepath), reason=str(e))
            return "HASH_FAILED"
        
        return hasher.hexdigest()
    
    def _guess_mime(self, filepath: Path) -> str:
        """Guess MIME type from extension"""
        ext = filepath.suffix.lower()
        mime_map = {
            '.py': 'text/x-python',
            '.json': 'application/json',
            '.yaml': 'text/x-yaml',
            '.yml': 'text/x-yaml',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.toml': 'text/x-toml',
            '.ini': 'text/plain',
            '.cfg': 'text/plain'
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path matches any exclude pattern"""
        path_str = str(path)
        for pattern in self.exclude:
            if self._matches_pattern(path, pattern):
                return True
        return False
    
    def _matches_pattern(self, path: Path, pattern: str) -> bool:
        """Check if path matches glob pattern"""
        path_str = str(path).replace('\\', '/')
        
        # Handle ** patterns
        if '**' in pattern:
            # Convert ** pattern to simple wildcard for fnmatch
            pattern_parts = pattern.split('**')
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                # Check if path starts with prefix (if any) and ends with suffix (if any)
                if prefix and not path_str.startswith(prefix.rstrip('/')):
                    return False
                if suffix and not fnmatch(path_str, '*' + suffix):
                    return False
                return True
        
        return fnmatch(path_str, pattern)

