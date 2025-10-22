"""
CARMA Integrity Verification System
Ensures cache files and fragments haven't been corrupted.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class IntegrityVerifier:
    """
    Verifies integrity of CARMA cache files and fragments.
    
    Uses SHA256 hashes to detect corruption and ensure data consistency.
    """
    
    def __init__(self, cache_dir: str = 'data_core/FractalCache'):
        self.cache_dir = Path(cache_dir)
        self.integrity_file = self.cache_dir / 'integrity_hashes.json'
        self.hashes = self._load_integrity_hashes()
    
    def _load_integrity_hashes(self) -> Dict[str, str]:
        """Load stored integrity hashes"""
        if self.integrity_file.exists():
            try:
                with open(self.integrity_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load integrity hashes: {e}")
        return {}
    
    def _save_integrity_hashes(self):
        """Save integrity hashes to file"""
        try:
            self.integrity_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.integrity_file, 'w', encoding='utf-8') as f:
                json.dump(self.hashes, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save integrity hashes: {e}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def calculate_content_hash(self, content: Any) -> str:
        """Calculate SHA256 hash of content (JSON serialized)"""
        try:
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = json.dumps(content, sort_keys=True).encode('utf-8')
            return hashlib.sha256(content_bytes).hexdigest()
        except Exception as e:
            print(f"Error calculating content hash: {e}")
            return ""
    
    def verify_file(self, file_path: Path, expected_hash: str = None) -> Dict[str, Any]:
        """
        Verify a file's integrity.
        
        Args:
            file_path: Path to file to verify
            expected_hash: Expected hash (if None, will use stored hash)
            
        Returns:
            Verification result with status and details
        """
        if not file_path.exists():
            return {
                'status': 'error',
                'message': f'File not found: {file_path}',
                'file_path': str(file_path),
                'verified': False
            }
        
        # Get expected hash
        if expected_hash is None:
            file_key = str(file_path.relative_to(self.cache_dir))
            expected_hash = self.hashes.get(file_key)
        
        if not expected_hash:
            return {
                'status': 'warning',
                'message': f'No stored hash for: {file_path}',
                'file_path': str(file_path),
                'verified': False
            }
        
        # Calculate current hash
        current_hash = self.calculate_file_hash(file_path)
        
        if not current_hash:
            return {
                'status': 'error',
                'message': f'Could not calculate hash for: {file_path}',
                'file_path': str(file_path),
                'verified': False
            }
        
        # Verify integrity
        verified = current_hash == expected_hash
        
        return {
            'status': 'verified' if verified else 'corrupted',
            'message': f'Hash {"matches" if verified else "mismatch"} for: {file_path}',
            'file_path': str(file_path),
            'expected_hash': expected_hash,
            'current_hash': current_hash,
            'verified': verified
        }
    
    def verify_fragment(self, fragment: Dict[str, Any], expected_hash: str = None) -> Dict[str, Any]:
        """
        Verify a memory fragment's integrity.
        
        Args:
            fragment: Memory fragment to verify
            expected_hash: Expected hash (if None, will use stored hash)
            
        Returns:
            Verification result with status and details
        """
        fragment_id = fragment.get('id', 'unknown')
        
        # Get expected hash
        if expected_hash is None:
            expected_hash = self.hashes.get(f'fragment_{fragment_id}')
        
        if not expected_hash:
            return {
                'status': 'warning',
                'message': f'No stored hash for fragment: {fragment_id}',
                'fragment_id': fragment_id,
                'verified': False
            }
        
        # Calculate current hash
        current_hash = self.calculate_content_hash(fragment)
        
        if not current_hash:
            return {
                'status': 'error',
                'message': f'Could not calculate hash for fragment: {fragment_id}',
                'fragment_id': fragment_id,
                'verified': False
            }
        
        # Verify integrity
        verified = current_hash == expected_hash
        
        return {
            'status': 'verified' if verified else 'corrupted',
            'message': f'Fragment {"verified" if verified else "corrupted"}: {fragment_id}',
            'fragment_id': fragment_id,
            'expected_hash': expected_hash,
            'current_hash': current_hash,
            'verified': verified
        }
    
    def register_file(self, file_path: Path) -> str:
        """
        Register a file and store its hash.
        
        Args:
            file_path: Path to file to register
            
        Returns:
            Calculated hash
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_hash = self.calculate_file_hash(file_path)
        if not file_hash:
            raise ValueError(f"Could not calculate hash for: {file_path}")
        
        # Store hash relative to cache directory
        file_key = str(file_path.relative_to(self.cache_dir))
        self.hashes[file_key] = file_hash
        
        # Save updated hashes
        self._save_integrity_hashes()
        
        return file_hash
    
    def register_fragment(self, fragment: Dict[str, Any]) -> str:
        """
        Register a memory fragment and store its hash.
        
        Args:
            fragment: Memory fragment to register
            
        Returns:
            Calculated hash
        """
        fragment_id = fragment.get('id', 'unknown')
        fragment_hash = self.calculate_content_hash(fragment)
        
        if not fragment_hash:
            raise ValueError(f"Could not calculate hash for fragment: {fragment_id}")
        
        # Store hash
        self.hashes[f'fragment_{fragment_id}'] = fragment_hash
        
        # Save updated hashes
        self._save_integrity_hashes()
        
        return fragment_hash
    
    def verify_cache_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all registered cache files.
        
        Returns:
            Overall verification result
        """
        results = []
        verified_count = 0
        corrupted_count = 0
        error_count = 0
        
        for file_key, expected_hash in self.hashes.items():
            if file_key.startswith('fragment_'):
                # Skip fragments - they're verified individually
                continue
            
            file_path = self.cache_dir / file_key
            result = self.verify_file(file_path, expected_hash)
            results.append(result)
            
            if result['verified']:
                verified_count += 1
            elif result['status'] == 'corrupted':
                corrupted_count += 1
            else:
                error_count += 1
        
        return {
            'status': 'success' if corrupted_count == 0 else 'corruption_detected',
            'total_files': len(results),
            'verified': verified_count,
            'corrupted': corrupted_count,
            'errors': error_count,
            'results': results,
            'integrity_file': str(self.integrity_file)
        }
    
    def get_integrity_stats(self) -> Dict[str, Any]:
        """Get integrity verification statistics"""
        total_hashes = len(self.hashes)
        file_hashes = sum(1 for key in self.hashes.keys() if not key.startswith('fragment_'))
        fragment_hashes = total_hashes - file_hashes
        
        return {
            'total_hashes': total_hashes,
            'file_hashes': file_hashes,
            'fragment_hashes': fragment_hashes,
            'integrity_file': str(self.integrity_file),
            'integrity_file_exists': self.integrity_file.exists(),
            'cache_dir': str(self.cache_dir)
        }
