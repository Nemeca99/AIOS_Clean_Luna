"""
Manifest loader and validator
"""

import yaml
import hashlib
from pathlib import Path
from typing import Dict


def load_manifest(manifest_path: Path) -> Dict:
    """Load and parse tool manifest"""
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def hash_manifest(manifest_path: Path) -> str:
    """Compute SHA-256 hash of manifest file"""
    with open(manifest_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def validate_params(params: Dict, manifest: Dict) -> bool:
    """Validate run parameters against manifest capabilities"""
    # Check root path
    root = Path(params['root'])
    allowed_read = manifest['capabilities']['fs']['read']
    
    # Simple check: root must match at least one allowed read pattern
    root_str = str(root)
    if not any(root_str.startswith(pattern.rstrip('*').rstrip('\\')) for pattern in allowed_read):
        return False
    
    # Check output path
    out = Path(params.get('out_base', params.get('out', '')))
    allowed_write = manifest['capabilities']['fs']['write']
    
    out_str = str(out)
    if not any(out_str.startswith(pattern.rstrip('*').rstrip('\\')) for pattern in allowed_write):
        return False
    
    return True

