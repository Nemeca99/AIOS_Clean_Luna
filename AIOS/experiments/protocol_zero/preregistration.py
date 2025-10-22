"""
Protocol Zero: Pre-Registration System
Generates experiment manifest with SHA-256 hash to prevent post-hoc editing.
"""
import hashlib
import json
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class PreRegistration:
    """Handles experiment pre-registration with cryptographic freezing"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.template_path = repo_root / "experiments" / "protocol_zero" / "preregistration_template.txt"
        self.experiments_dir = repo_root / "experiments" / "protocol_zero" / "runs"
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_manifest(self, 
                         duration_hours: float = 2.0,
                         auditor_model: str = "llama-3.2-1b-instruct-abliterated",
                         experiment_id: str = None) -> Dict[str, Any]:
        """Generate experiment manifest with all parameters"""
        
        if experiment_id is None:
            experiment_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Gather system info
        cpu_info = self._get_cpu_info()
        
        # Load oracle section count
        try:
            oracle_index = self.repo_root / "rag_core" / "manual_oracle" / "oracle_index.json"
            with open(oracle_index) as f:
                data = json.load(f)
                oracle_sections = len(data.get('sections', []))
        except Exception:
            oracle_sections = 0
        
        manifest = {
            'experiment_id': experiment_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'duration_hours': duration_hours,
            'cpu_model': cpu_info['model'],
            'cpu_freq': cpu_info['freq'],
            'auditor_model': auditor_model,
            'oracle_sections': oracle_sections,
            'hypothesis': 'Luna will autonomously select actions based on internal state without human input',
            'success_criteria': {
                'min_action_types': 3,
                'min_sleep_cycles': 1,
                'ablation_effect_size': 0.8,
                'challenge_discovery': True
            }
        }
        
        return manifest
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                'model': 'Unknown',  # psutil doesn't provide model name easily
                'freq': f"{cpu_freq.current / 1000:.2f}" if cpu_freq else "Unknown"
            }
        except Exception:
            return {'model': 'Unknown', 'freq': 'Unknown'}
    
    def freeze_registration(self, manifest: Dict[str, Any]) -> tuple[Path, str]:
        """
        Write manifest to file and compute SHA-256 hash.
        Returns (file_path, sha256_hash)
        """
        experiment_id = manifest['experiment_id']
        output_dir = self.experiments_dir / experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "00_preregistration.txt"
        
        # Load template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Fill template
        content = template.format(
            timestamp=manifest['timestamp'],
            experiment_id=experiment_id,
            hash_placeholder='[COMPUTED AFTER WRITING]',
            duration_hours=manifest['duration_hours'],
            cpu_model=manifest['cpu_model'],
            cpu_freq=manifest['cpu_freq'],
            auditor_model=manifest['auditor_model'],
            oracle_sections=manifest['oracle_sections'],
            signature_placeholder='[UNSIGNED]'
        )
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Compute hash
        with open(output_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Write hash file
        hash_path = output_dir / "00_preregistration.txt.sha256"
        with open(hash_path, 'w', encoding='utf-8') as f:
            f.write(f"{file_hash}  00_preregistration.txt\n")
        
        return output_path, file_hash
    
    def verify_hash(self, experiment_id: str) -> bool:
        """Verify preregistration hash hasn't changed"""
        prereg_path = self.experiments_dir / experiment_id / "00_preregistration.txt"
        hash_path = self.experiments_dir / experiment_id / "00_preregistration.txt.sha256"
        
        if not prereg_path.exists() or not hash_path.exists():
            return False
        
        # Read expected hash
        with open(hash_path, 'r') as f:
            expected_hash = f.read().split()[0]
        
        # Compute actual hash
        with open(prereg_path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        
        return expected_hash == actual_hash

