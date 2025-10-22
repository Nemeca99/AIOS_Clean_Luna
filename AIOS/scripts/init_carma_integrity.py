#!/usr/bin/env python3
"""
Initialize CARMA integrity hashing for all cache files
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from carma_core import CARMASystem


def init_carma_integrity():
    """Register all FractalCache files for integrity verification"""
    print("Initializing CARMA integrity verification...")
    print("=" * 60)
    
    carma = CARMASystem()
    cache_dir = Path("data_core/FractalCache")
    
    if not cache_dir.exists():
        print(f"⚠️  Cache directory not found: {cache_dir}")
        return
    
    # Find all JSON files in cache
    cache_files = list(cache_dir.glob("*.json"))
    cache_files += list(cache_dir.glob("*/*.json"))
    
    # Exclude integrity file itself
    cache_files = [f for f in cache_files if f.name != "integrity_hashes.json"]
    
    print(f"Found {len(cache_files)} cache files to register")
    print()
    
    registered = 0
    for file_path in cache_files:
        try:
            file_hash = carma.integrity_verifier.register_file(file_path)
            if file_hash and file_hash not in ["file_not_found", "error"]:
                print(f"  ✅ {file_path.name[:40]:<40} {file_hash[:12]}")
                registered += 1
            else:
                print(f"  ⚠️  {file_path.name[:40]:<40} SKIP")
        except Exception as e:
            print(f"  ❌ {file_path.name}: {e}")
    
    print()
    print(f"Registered {registered}/{len(cache_files)} files")
    
    # Show stats
    stats = carma.get_integrity_stats()
    print()
    print("Integrity Stats:")
    print(f"  Total hashes: {stats['total_hashes']}")
    print(f"  File hashes: {stats['file_hashes']}")
    print(f"  Fragment hashes: {stats['fragment_hashes']}")
    
    # Verify integrity
    print()
    print("Running integrity verification...")
    result = carma.verify_integrity()
    print(f"  Status: {result['status']}")
    print(f"  Verified: {result['verified']}")
    print(f"  Corrupted: {result['corrupted']}")
    print(f"  Errors: {result['errors']}")
    
    if result['status'] == 'success':
        print()
        print("✅ CARMA integrity system initialized successfully!")
    else:
        print()
        print(f"⚠️  Integrity check status: {result['status']}")


if __name__ == "__main__":
    init_carma_integrity()

