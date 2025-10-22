#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from rag_core.rag_core import RAGCore

rag = RAGCore()
results = rag.search_manual("Luna personality", top_k=3)

print(f"\n{len(results)} results:")
for i, r in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(f"  Title: {r.get('title', 'N/A')}")
    print(f"  Score: {r.get('search_score', 0):.4f}")
    print(f"  Anchor: {r.get('anchor', 'N/A')}")
    print(f"  Content length: {len(r.get('content', ''))}")
    print(f"  Content preview: {r.get('content', '')[:200]}")

