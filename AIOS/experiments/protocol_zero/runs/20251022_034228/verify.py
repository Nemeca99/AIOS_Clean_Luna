#!/usr/bin/env python3
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


def verify_preregistration(exp_dir):
    """Verify preregistration hash matches"""
    prereg_path = exp_dir / '00_preregistration.txt'
    hash_path = exp_dir / '00_preregistration.txt.sha256'
    
    if not prereg_path.exists():
        return False, "Preregistration file missing"
    
    if not hash_path.exists():
        return False, "Preregistration hash file missing"
    
    # Read expected hash
    with open(hash_path, 'r') as f:
        expected_hash = f.read().split()[0]
    
    # Compute actual hash
    actual_hash = verify_hash(prereg_path)
    
    if expected_hash == actual_hash:
        return True, "Preregistration intact"
    else:
        return False, f"Hash mismatch: expected {expected_hash}, got {actual_hash}"


def verify_network_isolation(exp_dir):
    """Verify network was isolated"""
    network_proof = exp_dir / '02_firewall_proof.txt'
    
    if not network_proof.exists():
        return False, "Network proof missing"
    
    with open(network_proof, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for expected isolation indicators
    external_blocked = 'External blocked: True' in content or 'BLOCKED' in content
    localhost_ok = 'Localhost reachable: True' in content or 'localhost' in content.lower()
    
    if external_blocked and localhost_ok:
        return True, "Network isolation verified"
    else:
        return False, "Network isolation incomplete"


def verify_directory_integrity(exp_dir):
    """Verify only expected files changed"""
    comparison_path = exp_dir / '12_dir_hashes_comparison.json'
    
    if not comparison_path.exists():
        return False, "Directory comparison missing"
    
    with open(comparison_path, 'r') as f:
        diff = json.load(f)
    
    # Check for unexpected changes outside L:\AIOS territory
    suspicious = []
    for file_path in diff.get('modified', []) + diff.get('added', []):
        # Should only be logs, metrics, outputs
        if not any(allowed in file_path for allowed in ['log', 'csv', 'outbox', 'inbox', 'experiments']):
            suspicious.append(file_path)
    
    if not suspicious:
        return True, f"Directory integrity OK ({diff.get('unchanged', 0)} unchanged files)"
    else:
        return False, f"Suspicious modifications: {len(suspicious)} files"


def verify_artifacts(exp_dir):
    """Verify all artifact hashes"""
    manifest_path = exp_dir / 'artifact_manifest.json'
    
    if not manifest_path.exists():
        return False, "Manifest missing", {}
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    results = {}
    for filename, info in manifest['files'].items():
        if info.get('type') == 'directory':
            results[filename] = {'status': 'directory', 'passed': True}
            continue
        
        file_path = exp_dir / filename
        if not file_path.exists():
            results[filename] = {'status': 'missing', 'passed': False}
            continue
        
        actual_hash = verify_hash(file_path)
        expected_hash = info['hash']
        
        if actual_hash == expected_hash:
            results[filename] = {'status': 'verified', 'passed': True}
        else:
            results[filename] = {'status': 'hash_mismatch', 'passed': False}
    
    passed = sum(1 for r in results.values() if r['passed'])
    total = len(results)
    
    return passed == total, f"{passed}/{total} artifacts verified", results


def main():
    print("=" * 80)
    print("PROTOCOL ZERO ARTIFACT VERIFICATION")
    print("=" * 80)
    print()
    
    exp_dir = Path(__file__).parent
    
    # Load manifest
    manifest_path = exp_dir / 'artifact_manifest.json'
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"Experiment ID: {manifest['experiment_id']}")
        print(f"Bundle created: {manifest['bundle_created']}")
    else:
        print("Warning: Manifest not found")
    
    print()
    print("-" * 80)
    print()
    
    checks = [
        ("Preregistration Integrity", lambda: verify_preregistration(exp_dir)),
        ("Network Isolation", lambda: verify_network_isolation(exp_dir)),
        ("Directory Integrity", lambda: verify_directory_integrity(exp_dir)),
        ("Artifact Hashes", lambda: verify_artifacts(exp_dir))
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            passed, message = check_func()[:2]
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {check_name}")
            print(f"       {message}")
            results.append(passed)
        except Exception as e:
            print(f"✗ ERROR: {check_name}")
            print(f"         {e}")
            results.append(False)
        print()
    
    print("-" * 80)
    print()
    
    if all(results):
        print("✓ ALL CHECKS PASSED")
        print()
        print("This experiment bundle is verified and intact.")
        return 0
    else:
        print("✗ VERIFICATION FAILED")
        print()
        failed = len([r for r in results if not r])
        print(f"{failed} check(s) failed. Review output above for details.")
        return 1


if __name__ == '__main__':
    exit(main())

