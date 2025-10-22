#!/usr/bin/env python3
"""
Verify Manual and TOC are in sync
Hard gate - fails if out of sync
"""

import sys
import json
import hashlib
from pathlib import Path

def calculate_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file"""
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    print("=" * 70)
    print("MANUAL SYNC VERIFICATION")
    print("=" * 70)
    
    repo_root = Path.cwd()
    manual_path = repo_root / "AIOS_MANUAL.md"
    toc_path = repo_root / "MANUAL_TOC.md"
    oracle_path = repo_root / "rag_core" / "manual_oracle" / "oracle_index.json"
    
    failures = []
    
    # Check files exist
    print("\n[1/4] Checking files exist...")
    if not manual_path.exists():
        failures.append("AIOS_MANUAL.md not found")
    else:
        print(f"   ✅ Manual: {manual_path.name}")
    
    if not toc_path.exists():
        failures.append("MANUAL_TOC.md not found")
    else:
        print(f"   ✅ TOC: {toc_path.name}")
    
    if not oracle_path.exists():
        failures.append("oracle_index.json not found")
    else:
        print(f"   ✅ Oracle: {oracle_path.name}")
    
    if failures:
        print(f"\n❌ SYNC: BROKEN")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    
    # Calculate current hashes
    print("\n[2/4] Calculating current hashes...")
    manual_hash = calculate_hash(manual_path)[:8]
    toc_hash = calculate_hash(toc_path)[:8]
    
    print(f"   Manual SHA: {manual_hash}")
    print(f"   TOC SHA: {toc_hash}")
    
    # Load oracle index
    print("\n[3/4] Checking oracle index...")
    with open(oracle_path, 'r') as f:
        oracle_data = json.load(f)
    
    oracle_manual_hash = oracle_data.get('manual_sha256', '')[:8]
    oracle_toc_hash = oracle_data.get('toc_sha256', '')[:8]
    chunks = len(oracle_data.get('sections', []))
    
    print(f"   Oracle manual SHA: {oracle_manual_hash}")
    print(f"   Oracle TOC SHA: {oracle_toc_hash}")
    print(f"   Chunks: {chunks}")
    
    # Verify sync
    print("\n[4/4] Verifying sync...")
    
    if manual_hash != oracle_manual_hash:
        failures.append(f"Manual out of sync (current={manual_hash}, oracle={oracle_manual_hash})")
    else:
        print(f"   ✅ Manual hash matches")
    
    if toc_hash != oracle_toc_hash:
        failures.append(f"TOC out of sync (current={toc_hash}, oracle={oracle_toc_hash})")
    else:
        print(f"   ✅ TOC hash matches")
    
    # Final verdict
    print("\n" + "=" * 70)
    if failures:
        print("❌ SYNC: BROKEN")
        print("=" * 70)
        for f in failures:
            print(f"  - {f}")
        print(f"\n⚠️  Run: py scripts/update_manual_complete.py")
        sys.exit(1)
    else:
        print("✅ SYNC: VERIFIED")
        print("=" * 70)
        print(f"\n  Manual SHA: {manual_hash}")
        print(f"  TOC SHA: {toc_hash}")
        print(f"  Oracle chunks: {chunks}")
        print(f"\n  Manual, TOC, and Oracle are in sync!")
        sys.exit(0)

if __name__ == "__main__":
    main()

