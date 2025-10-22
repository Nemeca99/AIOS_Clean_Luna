#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from rag_core.manual_oracle import ManualOracle
import numpy as np

oracle = ManualOracle()

print(f"Oracle loaded: {len(oracle.oracle_index)} sections")
print(f"mmap: {oracle.manual_mmap is not None}")
print(f"embedder: {oracle.embedder is not None}")

# Manually run embedding search
query = "Luna personality"
query_embedding = oracle._get_embedding(query)

print(f"\nQuery embedding: {query_embedding is not None}")
if query_embedding is not None:
    print(f"  Shape: {query_embedding.shape}")

candidates = []
for i, section in enumerate(oracle.oracle_index):
    print(f"\nSection {i+1}: {section['title']}")
    print(f"  Has embedding: {'embedding' in section}")
    print(f"  byte_start: {section.get('byte_start')}")
    print(f"  byte_end: {section.get('byte_end')}")
    
    if 'embedding' in section:
        section_embedding = np.array(section['embedding'])
        similarity = np.dot(query_embedding, section_embedding)
        print(f"  Similarity: {similarity:.4f}")
        
        # Try to extract content
        if oracle.manual_mmap and section.get('byte_start') and section.get('byte_end'):
            try:
                content = oracle.manual_mmap[section['byte_start']:section['byte_end']].decode('utf-8')
                print(f"  Content: {len(content)} chars")
                print(f"  Preview: {content[:80]}")
            except Exception as e:
                print(f"  Content ERROR: {e}")

