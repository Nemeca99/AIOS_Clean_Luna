#!/usr/bin/env python3
"""
Object Storage System - Git-like content-addressable storage
Stores blobs (files), trees (directories), and commits
"""

import hashlib
import json
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum


class ObjectType(Enum):
    """Types of Git objects"""
    BLOB = "blob"      # File content
    TREE = "tree"      # Directory structure
    COMMIT = "commit"  # Commit metadata


class GitObject:
    """Base class for all Git objects"""
    
    def __init__(self, obj_type: ObjectType, content: bytes):
        self.obj_type = obj_type
        self.content = content
        self._hash = None
    
    def hash(self) -> str:
        """Calculate SHA256 hash of object"""
        if self._hash is None:
            header = f"{self.obj_type.value} {len(self.content)}\0".encode()
            self._hash = hashlib.sha256(header + self.content).hexdigest()
        return self._hash
    
    def serialize(self) -> bytes:
        """Serialize object for storage"""
        header = f"{self.obj_type.value} {len(self.content)}\0".encode()
        return header + self.content
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'GitObject':
        """Deserialize object from storage"""
        # Split header and content
        null_idx = data.index(b'\0')
        header = data[:null_idx].decode()
        content = data[null_idx + 1:]
        
        # Parse header
        obj_type_str, size_str = header.split(' ')
        obj_type = ObjectType(obj_type_str)
        
        # Create appropriate object type
        if obj_type == ObjectType.BLOB:
            return BlobObject.from_content(content)
        elif obj_type == ObjectType.TREE:
            return TreeObject.from_content(content)
        elif obj_type == ObjectType.COMMIT:
            return CommitObject.from_content(content)
        else:
            raise ValueError(f"Unknown object type: {obj_type_str}")


class BlobObject(GitObject):
    """Blob object - stores file content"""
    
    def __init__(self, content: bytes):
        super().__init__(ObjectType.BLOB, content)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'BlobObject':
        """Create blob from file"""
        with open(file_path, 'rb') as f:
            content = f.read()
        return cls(content)
    
    @classmethod
    def from_content(cls, content: bytes) -> 'BlobObject':
        """Create blob from raw content"""
        return cls(content)
    
    def get_content(self) -> bytes:
        """Get file content"""
        return self.content


class TreeObject(GitObject):
    """Tree object - stores directory structure"""
    
    def __init__(self, entries: List[Dict[str, str]]):
        """
        Create tree object
        entries: List of {'mode': '100644', 'name': 'file.py', 'hash': 'abc123...'}
        """
        self.entries = sorted(entries, key=lambda x: x['name'])
        content = self._serialize_entries()
        super().__init__(ObjectType.TREE, content)
    
    def _serialize_entries(self) -> bytes:
        """Serialize tree entries to bytes"""
        result = b''
        for entry in self.entries:
            # Format: mode name\0hash
            line = f"{entry['mode']} {entry['name']}\0".encode()
            line += bytes.fromhex(entry['hash'])
            result += line
        return result
    
    @classmethod
    def from_content(cls, content: bytes) -> 'TreeObject':
        """Deserialize tree from content"""
        entries = []
        pos = 0
        while pos < len(content):
            # Find null byte
            null_idx = content.index(b'\0', pos)
            header = content[pos:null_idx].decode()
            mode, name = header.split(' ', 1)
            
            # Hash is 32 bytes (SHA256)
            hash_bytes = content[null_idx + 1:null_idx + 33]
            hash_str = hash_bytes.hex()
            
            entries.append({
                'mode': mode,
                'name': name,
                'hash': hash_str
            })
            
            pos = null_idx + 33
        
        return cls(entries)
    
    def get_entries(self) -> List[Dict[str, str]]:
        """Get tree entries"""
        return self.entries


class CommitObject(GitObject):
    """Commit object - stores commit metadata"""
    
    def __init__(self, tree_hash: str, parent_hashes: List[str], 
                 author: str, message: str, timestamp: Optional[float] = None):
        self.tree_hash = tree_hash
        self.parent_hashes = parent_hashes
        self.author = author
        self.message = message
        self.timestamp = timestamp or datetime.now().timestamp()
        
        content = self._serialize_commit()
        super().__init__(ObjectType.COMMIT, content)
    
    def _serialize_commit(self) -> bytes:
        """Serialize commit to bytes"""
        lines = []
        lines.append(f"tree {self.tree_hash}")
        for parent in self.parent_hashes:
            lines.append(f"parent {parent}")
        lines.append(f"author {self.author}")
        lines.append(f"timestamp {self.timestamp}")
        lines.append("")  # Blank line before message
        lines.append(self.message)
        
        return '\n'.join(lines).encode()
    
    @classmethod
    def from_content(cls, content: bytes) -> 'CommitObject':
        """Deserialize commit from content"""
        lines = content.decode().split('\n')
        
        tree_hash = None
        parent_hashes = []
        author = None
        timestamp = None
        message_lines = []
        in_message = False
        
        for line in lines:
            if in_message:
                message_lines.append(line)
            elif line.startswith('tree '):
                tree_hash = line[5:]
            elif line.startswith('parent '):
                parent_hashes.append(line[7:])
            elif line.startswith('author '):
                author = line[7:]
            elif line.startswith('timestamp '):
                timestamp = float(line[10:])
            elif line == '':
                in_message = True
        
        message = '\n'.join(message_lines)
        return cls(tree_hash, parent_hashes, author, message, timestamp)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get commit metadata"""
        return {
            'tree': self.tree_hash,
            'parents': self.parent_hashes,
            'author': self.author,
            'message': self.message,
            'timestamp': self.timestamp,
            'date': datetime.fromtimestamp(self.timestamp).isoformat()
        }


class ObjectStore:
    """
    Content-addressable object storage system
    Stores objects in .aios_backup/objects/ with deduplication
    """
    
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.objects_dir = repo_dir / "objects"
        self.objects_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_object_path(self, obj_hash: str) -> Path:
        """
        Get path for object storage
        Uses Git-like sharding: first 2 chars as directory, rest as filename
        Example: abc123... -> objects/ab/c123...
        """
        return self.objects_dir / obj_hash[:2] / obj_hash[2:]
    
    def write_object(self, obj: GitObject) -> str:
        """
        Write object to storage
        Returns: Object hash
        """
        obj_hash = obj.hash()
        obj_path = self._get_object_path(obj_hash)
        
        # Skip if already exists (deduplication)
        if obj_path.exists():
            return obj_hash
        
        # Create directory
        obj_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Compress and write
        compressed = zlib.compress(obj.serialize())
        with open(obj_path, 'wb') as f:
            f.write(compressed)
        
        return obj_hash
    
    def read_object(self, obj_hash: str) -> Optional[GitObject]:
        """
        Read object from storage
        Returns: GitObject or None if not found
        """
        obj_path = self._get_object_path(obj_hash)
        
        if not obj_path.exists():
            return None
        
        # Read and decompress
        with open(obj_path, 'rb') as f:
            compressed = f.read()
        
        data = zlib.decompress(compressed)
        return GitObject.deserialize(data)
    
    def object_exists(self, obj_hash: str) -> bool:
        """Check if object exists"""
        return self._get_object_path(obj_hash).exists()
    
    def write_blob_from_file(self, file_path: Path) -> str:
        """
        Create blob from file and write to storage
        Returns: Blob hash
        """
        blob = BlobObject.from_file(file_path)
        return self.write_object(blob)
    
    def write_tree(self, entries: List[Dict[str, str]]) -> str:
        """
        Create tree and write to storage
        Returns: Tree hash
        """
        tree = TreeObject(entries)
        return self.write_object(tree)
    
    def write_commit(self, tree_hash: str, parent_hashes: List[str],
                     author: str, message: str) -> str:
        """
        Create commit and write to storage
        Returns: Commit hash
        """
        commit = CommitObject(tree_hash, parent_hashes, author, message)
        return self.write_object(commit)
    
    def get_blob_content(self, blob_hash: str) -> Optional[bytes]:
        """Get content of a blob"""
        obj = self.read_object(blob_hash)
        if obj and isinstance(obj, BlobObject):
            return obj.get_content()
        return None
    
    def get_tree_entries(self, tree_hash: str) -> Optional[List[Dict[str, str]]]:
        """Get entries of a tree"""
        obj = self.read_object(tree_hash)
        if obj and isinstance(obj, TreeObject):
            return obj.get_entries()
        return None
    
    def get_commit_metadata(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get metadata of a commit"""
        obj = self.read_object(commit_hash)
        if obj and isinstance(obj, CommitObject):
            return obj.get_metadata()
        return None
    
    def list_all_objects(self) -> List[Tuple[str, ObjectType]]:
        """List all objects in storage"""
        objects = []
        for dir_path in self.objects_dir.iterdir():
            if dir_path.is_dir():
                for obj_file in dir_path.iterdir():
                    if obj_file.is_file():
                        obj_hash = dir_path.name + obj_file.name
                        obj = self.read_object(obj_hash)
                        if obj:
                            objects.append((obj_hash, obj.obj_type))
        return objects
    
    def get_stats(self) -> Dict[str, int]:
        """Get storage statistics"""
        stats = {
            'total_objects': 0,
            'blobs': 0,
            'trees': 0,
            'commits': 0,
            'total_size_bytes': 0
        }
        
        for obj_hash, obj_type in self.list_all_objects():
            stats['total_objects'] += 1
            if obj_type == ObjectType.BLOB:
                stats['blobs'] += 1
            elif obj_type == ObjectType.TREE:
                stats['trees'] += 1
            elif obj_type == ObjectType.COMMIT:
                stats['commits'] += 1
            
            obj_path = self._get_object_path(obj_hash)
            stats['total_size_bytes'] += obj_path.stat().st_size
        
        return stats

