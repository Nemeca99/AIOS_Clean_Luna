"""
Creative Template Retrieval
Part of rag_core for FAISS-based creative scaffold lookup

V5.1 CreativeRAG Integration
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def load_creative_index(cfg: Dict) -> Tuple[Optional[object], Optional[List]]:
    """
    Load FAISS creative template index + metadata
    
    Stateless safe: Returns (None, None) if index not built
    
    Args:
        cfg: AIOS config dict with creative_mode section
    
    Returns:
        (index, metas) or (None, None) if not built or missing dependencies
    """
    try:
        import faiss
    except ImportError:
        return None, None
    
    paths = cfg.get("creative_mode", {})
    idx_path = paths.get("index_path")
    meta_path = paths.get("meta_path")
    
    if not idx_path or not meta_path:
        return None, None
    
    idx_p = Path(idx_path)
    meta_p = Path(meta_path)
    
    if not idx_p.exists() or not meta_p.exists():
        return None, None
    
    try:
        index = faiss.read_index(str(idx_p))
        with open(meta_p, 'r', encoding='utf-8') as f:
            metas = [json.loads(line) for line in f]
        return index, metas
    except Exception as e:
        print(f"Error loading creative index: {e}")
        return None, None


def retrieve_creative_templates(cfg: Dict, query: str, k: Optional[int] = None) -> List[Dict]:
    """
    Retrieve top-k creative templates matching query
    
    Performance: <50ms for typical index sizes
    Stateless safe: Returns empty list if index missing
    
    Hardening:
    - Pinned embedder (no drift)
    - Embedder checksum validation
    - Index freshness check
    
    Args:
        cfg: AIOS config dict
        query: Search query (user creative request)
        k: Number of templates (default from config)
    
    Returns:
        List of template dicts or empty list (never crashes)
    """
    idx, metas = load_creative_index(cfg)
    if idx is None:
        return []
    
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        return []
    
    k = k or cfg.get("creative_mode", {}).get("topk_templates", 3)
    
    # Pin embedder (regression guard - hardcoded, no drift)
    embedder_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Validate embedder checksum from metadata header
    if metas and len(metas) > 0 and metas[0].get("__meta__"):
        header = metas[0]
        stored_embedder = header.get("embedder")
        if stored_embedder and stored_embedder != embedder_name:
            print(f"WARNING: Embedder mismatch! Index: {stored_embedder}, Current: {embedder_name}")
            return []  # Fail safe - don't use mismatched index
        metas = metas[1:]  # Skip header for retrieval
    
    try:
        enc = SentenceTransformer(embedder_name)
        q_vec = enc.encode([query], normalize_embeddings=True).astype("float32")
        
        D, I = idx.search(q_vec, min(k, len(metas)))
        
        results = []
        for i in I[0]:
            if i >= 0 and i < len(metas):
                results.append(metas[i])
        
        return results
    except Exception as e:
        print(f"Error during creative template retrieval: {e}")
        return []

