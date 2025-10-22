#!/usr/bin/env python3
"""
Staging Area (Index) - Git-like staging system
Tracks files to be included in next commit
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime


class StagingArea:
    """
    Git-like staging area (index)
    Tracks which files should be included in the next commit
    """
    
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.index_file = repo_dir / "index"
        self._staged_files: Dict[str, Dict[str, any]] = {}
        self._load_index()
    
    def _load_index(self):
        """Load staging area from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self._staged_files = data.get('staged_files', {})
            except Exception:
                self._staged_files = {}
        else:
            self._staged_files = {}
    
    def _save_index(self):
        """Save staging area to disk"""
        data = {
            'version': 1,
            'staged_files': self._staged_files,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.index_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add(self, file_path: str, blob_hash: str, mode: str = "100644"):
        """
        Add file to staging area
        Args:
            file_path: Relative path to file
            blob_hash: Hash of blob object
            mode: File mode (100644 for normal file, 100755 for executable)
        """
        self._staged_files[file_path] = {
            'hash': blob_hash,
            'mode': mode,
            'staged_at': datetime.now().timestamp()
        }
        self._save_index()
    
    def remove(self, file_path: str):
        """Remove file from staging area"""
        if file_path in self._staged_files:
            del self._staged_files[file_path]
            self._save_index()
    
    def clear(self):
        """Clear all staged files"""
        self._staged_files = {}
        self._save_index()
    
    def is_staged(self, file_path: str) -> bool:
        """Check if file is staged"""
        return file_path in self._staged_files
    
    def get_staged_files(self) -> Dict[str, Dict[str, any]]:
        """Get all staged files"""
        return self._staged_files.copy()
    
    def get_staged_file_paths(self) -> List[str]:
        """Get list of all staged file paths"""
        return sorted(self._staged_files.keys())
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Get blob hash for staged file"""
        if file_path in self._staged_files:
            return self._staged_files[file_path]['hash']
        return None
    
    def get_file_mode(self, file_path: str) -> Optional[str]:
        """Get file mode for staged file"""
        if file_path in self._staged_files:
            return self._staged_files[file_path]['mode']
        return None
    
    def is_empty(self) -> bool:
        """Check if staging area is empty"""
        return len(self._staged_files) == 0
    
    def get_staged_count(self) -> int:
        """Get number of staged files"""
        return len(self._staged_files)
    
    def build_tree_entries(self) -> List[Dict[str, str]]:
        """
        Build tree entries from staged files for commit
        Returns list of entries suitable for TreeObject
        """
        # Group files by directory
        tree_structure = {}
        
        for file_path, file_info in self._staged_files.items():
            parts = Path(file_path).parts
            
            # Build nested structure
            current_level = tree_structure
            for i, part in enumerate(parts[:-1]):
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            # Add file entry
            filename = parts[-1]
            current_level[filename] = {
                'type': 'blob',
                'hash': file_info['hash'],
                'mode': file_info['mode']
            }
        
        # Convert to flat tree entries (for now, simple approach)
        # TODO: Implement proper hierarchical tree building
        entries = []
        for file_path, file_info in self._staged_files.items():
            entries.append({
                'mode': file_info['mode'],
                'name': file_path,
                'hash': file_info['hash']
            })
        
        return entries
    
    def get_stats(self) -> Dict[str, any]:
        """Get staging area statistics"""
        return {
            'staged_files': len(self._staged_files),
            'is_empty': self.is_empty(),
            'total_size': sum(
                len(path) for path in self._staged_files.keys()
            )
        }

