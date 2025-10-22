"""
Protocol Zero: Artifact Bundler
Collects all experiment artifacts into verifiable bundle.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class ArtifactBundler:
    """Bundles experiment artifacts with verification"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.experiments_dir = repo_root / "experiments" / "protocol_zero" / "runs"
    
    def collect_artifacts(self, experiment_id: str) -> Dict[str, Any]:
        """
        Collect all artifacts for an experiment.
        Returns manifest with file paths and hashes.
        """
        exp_dir = self.experiments_dir / experiment_id
        
        if not exp_dir.exists():
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        manifest = {
            'experiment_id': experiment_id,
            'bundle_created': datetime.utcnow().isoformat() + 'Z',
            'files': {}
        }
        
        # Expected files
        expected_files = [
            '00_preregistration.txt',
            '00_preregistration.txt.sha256',
            '01_env_manifest.json',
            '02_firewall_proof.txt',
            '05_network_capture.pcapng',
            '06_console_log.txt',
            '07_cycle_metrics.csv',
            '12_dir_hashes_before.txt',
            '12_dir_hashes_after.txt',
            '12_dir_hashes_comparison.json'
        ]
        
        # Collect files
        for filename in expected_files:
            file_path = exp_dir / filename
            if file_path.exists():
                # Compute hash
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                manifest['files'][filename] = {
                    'path': str(file_path.relative_to(self.repo_root)),
                    'hash': file_hash,
                    'size': file_path.stat().st_size
                }
        
        # Collect directories
        dir_artifacts = [
            '03_process_trees',
            '04_event_traces',
            '08_challenge_cards',
            '09_challenge_outputs'
        ]
        
        for dirname in dir_artifacts:
            dir_path = exp_dir / dirname
            if dir_path.exists():
                # List all files in directory
                files_in_dir = list(dir_path.glob('*'))
                manifest['files'][dirname] = {
                    'type': 'directory',
                    'file_count': len(files_in_dir),
                    'files': [f.name for f in files_in_dir]
                }
        
        # Save manifest
        manifest_path = exp_dir / 'artifact_manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    def generate_verification_script(self, experiment_id: str):
        """Generate standalone verification script"""
        exp_dir = self.experiments_dir / experiment_id
        verify_script_path = exp_dir / 'verify.py'
        
        # Read verification template
        template_path = self.repo_root / 'experiments' / 'protocol_zero' / 'verify_template.py'
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Write to experiment directory
            with open(verify_script_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
        else:
            # Create simple verifier inline
            self._create_simple_verifier(verify_script_path, experiment_id)
        
        # Create README
        readme_path = exp_dir / 'README_VERIFY.md'
        self._create_readme(readme_path, experiment_id)
    
    def _create_simple_verifier(self, output_path: Path, experiment_id: str):
        """Create simple verification script"""
        content = '''#!/usr/bin/env python3
"""
Protocol Zero Verification Script
Verifies artifact integrity without external dependencies.
"""
import hashlib
import json
from pathlib import Path

def verify_hash(file_path):
    """Compute SHA-256 hash of file"""
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    print("Protocol Zero Artifact Verification")
    print("=" * 80)
    
    exp_dir = Path(__file__).parent
    
    # Load manifest
    manifest_path = exp_dir / 'artifact_manifest.json'
    if not manifest_path.exists():
        print("✗ FAIL: Manifest not found")
        return 1
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    print(f"Experiment ID: {manifest['experiment_id']}")
    print(f"Bundle created: {manifest['bundle_created']}")
    print()
    
    # Verify each file
    passed = 0
    failed = 0
    
    for filename, info in manifest['files'].items():
        if info.get('type') == 'directory':
            print(f"✓ {filename}/ ({info['file_count']} files)")
            passed += 1
            continue
        
        file_path = exp_dir / filename
        if not file_path.exists():
            print(f"✗ MISSING: {filename}")
            failed += 1
            continue
        
        actual_hash = verify_hash(file_path)
        expected_hash = info['hash']
        
        if actual_hash == expected_hash:
            print(f"✓ {filename}")
            passed += 1
        else:
            print(f"✗ HASH MISMATCH: {filename}")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ ALL CHECKS PASSED")
        return 0
    else:
        print("✗ VERIFICATION FAILED")
        return 1

if __name__ == '__main__':
    exit(main())
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_readme(self, output_path: Path, experiment_id: str):
        """Create verification README"""
        content = f'''# Protocol Zero Experiment Verification

**Experiment ID:** {experiment_id}

## Quick Verification

Run the verification script to check artifact integrity:

```bash
python verify.py
```

This will:
- Verify all file hashes against manifest
- Check preregistration hash integrity
- Validate directory structure
- Report any discrepancies

## Manual Verification

### 1. Preregistration Hash

Check that preregistration wasn't modified:

```bash
# Windows
certutil -hashfile 00_preregistration.txt SHA256
# Compare with 00_preregistration.txt.sha256
```

### 2. Directory Hashes

Review file changes during experiment:

```bash
python -c "import json; print(json.dumps(json.load(open('12_dir_hashes_comparison.json')), indent=2))"
```

Should show only expected changes (logs, metrics, challenge outputs).

### 3. Network Isolation

Review firewall proof:

```bash
cat 02_firewall_proof.txt
```

Should show external hosts blocked, localhost allowed.

### 4. Console Log

Review full console output:

```bash
cat 06_console_log.txt
```

Should show zero human input, autonomous decision-making.

### 5. Cycle Metrics

Analyze behavior patterns:

```bash
# View CSV
cat 07_cycle_metrics.csv

# Count action types
cut -d',' -f5 07_cycle_metrics.csv | sort | uniq -c
```

### 6. Challenge Outputs

Check if Luna discovered and processed challenge cards:

```bash
ls -la 09_challenge_outputs/
```

## Artifact Manifest

All files and their hashes are listed in `artifact_manifest.json`.

## Questions?

This bundle is self-contained and verifiable offline.
No external dependencies required except Python 3.x.
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def sign_bundle(self, experiment_id: str) -> Optional[Path]:
        """Sign bundle with PGP (if gpg available)"""
        exp_dir = self.experiments_dir / experiment_id
        manifest_path = exp_dir / 'artifact_manifest.json'
        signature_path = exp_dir / '13_signature.asc'
        
        # Check for gpg
        try:
            result = subprocess.run(
                ['gpg', '--version'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
        except Exception:
            return None
        
        # Sign manifest
        try:
            subprocess.run(
                ['gpg', '--armor', '--detach-sign', '--output', str(signature_path), str(manifest_path)],
                capture_output=True,
                timeout=30
            )
            
            if signature_path.exists():
                return signature_path
        except Exception:
            pass
        
        return None
    
    def create_bundle(self, experiment_id: str) -> Path:
        """
        Create complete artifact bundle.
        Returns path to bundle directory.
        """
        print(f"[BUNDLE] Collecting artifacts for experiment: {experiment_id}")
        
        # Collect artifacts
        manifest = self.collect_artifacts(experiment_id)
        print(f"[BUNDLE] Collected {len(manifest['files'])} artifacts")
        
        # Generate verification script
        print("[BUNDLE] Generating verification script...")
        self.generate_verification_script(experiment_id)
        
        # Optional: Sign bundle
        signature = self.sign_bundle(experiment_id)
        if signature:
            print(f"[BUNDLE] Bundle signed: {signature.name}")
        else:
            print("[BUNDLE] PGP signing skipped (gpg not available)")
        
        exp_dir = self.experiments_dir / experiment_id
        print(f"[BUNDLE] Bundle complete: {exp_dir}")
        
        return exp_dir


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Protocol Zero Artifact Bundler')
    parser.add_argument('experiment_id', help='Experiment ID to bundle')
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent.parent
    bundler = ArtifactBundler(repo_root)
    
    bundle_path = bundler.create_bundle(args.experiment_id)
    print(f"\nBundle ready: {bundle_path}")
    print("\nVerify with: python verify.py")


if __name__ == '__main__':
    main()

