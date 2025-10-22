"""
SCP-001 Law Gates for CodeGraph Mapper
Entry and pre-commit validation
"""

import hashlib
from pathlib import Path
from typing import Tuple, List


class LawsGate:
    """Enforces SCP-001 laws for CGM tool"""
    
    def __init__(self, root: Path):
        self.root = root
        self.aios_root = Path("L:\\AIOS")
        self.law_files = [
            "security_core/laws/origin_lock.txt",
            "security_core/laws/reflection_only_memory.txt",
            "security_core/laws/containment_by_morality.txt",
            "security_core/laws/replication_restriction.txt",
            "security_core/laws/foreign_dormancy.txt",
            "security_core/laws/oblivion.txt"
        ]
    
    def check_entry(self, root_path: Path, out_path: Path) -> Tuple[bool, str]:
        """
        Entry gate: Validate paths are within allowed boundaries
        Returns: (ok, message)
        """
        # Resolve to absolute paths
        try:
            root_abs = root_path.resolve()
            out_abs = out_path.resolve()
        except Exception as e:
            return False, f"Path resolution failed: {e}"
        
        # Check root is within L:\AIOS
        if not str(root_abs).startswith("L:\\AIOS"):
            return False, f"Root path {root_abs} violates OriginLock (must be within L:\\AIOS)"
        
        # Check out is within L:\AIOS\_maps
        if not str(out_abs).startswith("L:\\AIOS\\_maps"):
            return False, f"Output path {out_abs} violates write restrictions (must be within L:\\AIOS\\_maps)"
        
        return True, "Entry gate passed"
    
    def check_precommit(self, artifact_paths: List[Path]) -> Tuple[bool, str]:
        """
        Pre-commit gate: Verify all writes are within approved output directory
        Returns: (ok, message)
        """
        for path in artifact_paths:
            try:
                path_abs = path.resolve()
            except Exception as e:
                return False, f"Cannot resolve artifact path {path}: {e}"
            
            if not str(path_abs).startswith("L:\\AIOS\\_maps"):
                return False, f"Artifact {path_abs} violates write restrictions (must be within L:\\AIOS\\_maps)"
        
        return True, f"Pre-commit gate passed ({len(artifact_paths)} artifacts)"
    
    def compute_law_hash(self) -> str:
        """
        Compute SHA-256 hash of all 6 law files
        Returns: hex digest
        """
        hasher = hashlib.sha256()
        
        for law_file in self.law_files:
            law_path = self.aios_root / law_file
            if law_path.exists():
                with open(law_path, 'rb') as f:
                    hasher.update(f.read())
            else:
                # If law file missing, use empty bytes (degraded mode)
                hasher.update(b"")
        
        return hasher.hexdigest()

