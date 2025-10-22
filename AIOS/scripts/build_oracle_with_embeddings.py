#!/usr/bin/env python3
"""
Build Oracle Index with Pre-computed Embeddings
Pre-compute all manual section embeddings for instant searches
"""

import sys
import time
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from rag_core.manual_oracle import ManualOracle

def main():
    print("=" * 60)
    print("BUILDING ORACLE WITH PRE-COMPUTED EMBEDDINGS")
    print("=" * 60)
    
    # Initialize oracle
    print("\n1. Initializing Manual Oracle...")
    start = time.perf_counter()
    oracle = ManualOracle(str(repo_root))
    init_time = (time.perf_counter() - start) * 1000
    print(f"   Initialized in {init_time:.1f}ms")
    print(f"   Total sections: {len(oracle.oracle_index)}")
    
    if not oracle.embedder:
        print("\n   ERROR: Embedder not available!")
        print("   Install sentence-transformers: pip install sentence-transformers")
        return
    
    # Pre-compute all embeddings
    print("\n2. Pre-computing section embeddings...")
    embedded_count = 0
    skipped_count = 0
    total_time = 0
    
    for i, section in enumerate(oracle.oracle_index, 1):
        # Check if already embedded
        if 'embedding' in section:
            skipped_count += 1
            continue
        
        # Get section content
        if oracle.manual_mmap and section['byte_start'] is not None:
            try:
                content = oracle.manual_mmap[section['byte_start']:section['byte_end']].decode('utf-8')
                
                # Generate embedding
                start = time.perf_counter()
                embedding = oracle._get_embedding(content[:512])  # Limit to 512 chars
                elapsed = (time.perf_counter() - start) * 1000
                total_time += elapsed
                
                if embedding is not None:
                    section['embedding'] = embedding.tolist()
                    embedded_count += 1
                    print(f"   [{i}/{len(oracle.oracle_index)}] {section['title'][:50]:50s} {elapsed:6.1f}ms")
                
            except Exception as e:
                print(f"   ERROR on section {i}: {e}")
                continue
    
    avg_time = total_time / embedded_count if embedded_count > 0 else 0
    print(f"\n   Embedded: {embedded_count} sections")
    print(f"   Skipped: {skipped_count} sections (already embedded)")
    print(f"   Total time: {total_time:.1f}ms")
    print(f"   Average: {avg_time:.1f}ms per section")
    
    # Save updated index
    print("\n3. Saving oracle index with embeddings...")
    oracle._save_oracle_index()
    
    # Calculate index size
    index_size = oracle.index_file.stat().st_size / (1024 * 1024) if oracle.index_file.exists() else 0
    print(f"   Index file: {oracle.index_file}")
    print(f"   Index size: {index_size:.2f} MB")
    
    # Test search speed
    print("\n4. Testing search speed...")
    test_queries = [
        "How do I optimize CARMA memory?",
        "Luna personality configuration",
        "Audit system features"
    ]
    
    for query in test_queries:
        start = time.perf_counter()
        results = oracle.search_sections(query, top_k=3)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"\n   Query: '{query}'")
        print(f"   Time: {elapsed:.1f}ms")
        print(f"   Results: {len(results)}")
        if results:
            for i, result in enumerate(results, 1):
                score = result.get('search_score', 0.0)
                title = result.get('title', 'N/A')
                print(f"      {i}. {title} (score: {score:.3f})")
    
    print("\n" + "=" * 60)
    print("ORACLE BUILT SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nNext time you search, it will be ~{avg_time:.0f}ms per section")
    print(f"vs ~6ms with cached embeddings (instant!)")

if __name__ == "__main__":
    main()
