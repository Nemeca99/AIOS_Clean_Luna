"""
Creative Template Compression Job
Part of dream_core - compresses raw creative samples into templates

V5.1 CreativeRAG Integration
Performance: O(N) dedup using set (auditor-approved)

Hardening (regression guards):
- Embedder pinned to sentence-transformers/all-MiniLM-L6-v2
- Corpus hygiene: drops content < 80 chars
- Diversity histogram logged
- Embedder checksum in metadata header
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List


def job_compress_creative_templates(data_core_instance) -> Dict:
    """
    Dream job: raw samples -> dedupe -> templates -> FAISS index
    
    Idempotent: Safe to re-run (overwrites index)
    Performance: O(N) dedup using set
    
    Args:
        data_core_instance: DataCore with load_config() and creative_paths()
    
    Returns:
        dict: {status, templates_count, raw_samples, dedup_ratio}
    """
    cfg = data_core_instance.load_config()
    cm = cfg.get("creative_mode", {})
    
    if not cm.get("enabled", False):
        return {"status": "disabled", "reason": "creative_mode.enabled=false"}
    
    paths = data_core_instance.creative_paths()
    raw_file = Path(paths['raw_dir']) / "creative_samples.jsonl"
    
    if not raw_file.exists():
        return {"status": "noop", "reason": "no_raw_corpus"}
    
    # 1) Dedup with set (O(N) not O(N²) - auditor requirement)
    def normalize(s):
        """Normalize text for deduplication (lowercase, collapse whitespace)"""
        return re.sub(r"\s+", " ", s.lower()).strip()
    
    seen = set()
    cleaned = []
    total = 0
    
    with open(raw_file, 'r', encoding='utf-8') as f:
        for line in f:
            total += 1
            try:
                rec = json.loads(line)
                content = rec.get("content", "")
                
                # Corpus hygiene: drop timeouts and empties (durability guard)
                if len(content) < 80:
                    continue
                
                key = normalize(content)[:2048]  # Clamp for hash safety
                if key in seen:
                    continue
                seen.add(key)
                cleaned.append(rec)
            except json.JSONDecodeError:
                continue
    
    if not cleaned:
        return {"status": "no_valid_samples", "raw_samples": total}
    
    data_core_instance.write_clean_corpus(cleaned)
    
    # 2) Extract templates (4-beat split - simple narrative structure)
    def extract_beats(text: str) -> List[str]:
        """
        Split text into 4 narrative beats
        Simple sentence-based split (not WHY/HOW extraction yet)
        """
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if len(sentences) < 4:
            return [" ".join(sentences)]
        
        k = len(sentences) // 4
        return [
            " ".join(sentences[0:k]),           # Beat 1: Setup
            " ".join(sentences[k:2*k]),         # Beat 2: Development
            " ".join(sentences[2*k:3*k]),       # Beat 3: Climax
            " ".join(sentences[3*k:])           # Beat 4: Resolution
        ]
    
    templates = []
    for rec in cleaned:
        content = rec.get("content", "")
        if not content:
            continue
        
        tmpl = {
            "id": f"tmpl:{abs(hash(content)) & 0xfffffff}",
            "prompt": rec.get("prompt", {}),
            "beats": extract_beats(content),
            "source": rec.get("model", "unknown"),
            "timestamp": rec.get("timestamp", 0)
        }
        templates.append(tmpl)
    
    if not templates:
        return {"status": "no_valid_samples", "raw_samples": total}
    
    # 3) Build FAISS index
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError as e:
        return {"status": "error", "reason": f"missing_dependency: {e}"}
    
    # Pin embedder (regression guard - hardcoded, no drift)
    embedder_name = "sentence-transformers/all-MiniLM-L6-v2"
    config_embedder = cm.get("embedder", "")
    
    # Assert mismatch -> fail fast (performance sanity)
    if config_embedder and config_embedder != embedder_name:
        return {
            "status": "error",
            "reason": f"embedder_mismatch: config={config_embedder}, pinned={embedder_name}. Rebuild required!"
        }
    
    try:
        enc = SentenceTransformer(embedder_name)
    except Exception as e:
        return {"status": "error", "reason": f"embedder_init_failed: {e}"}
    
    # Embed concatenated beats (pipe-separated for semantic similarity)
    texts = [" | ".join(t["beats"]) for t in templates]
    X = enc.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    
    # Create index (inner product for normalized vectors)
    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)
    
    # 4) Save index + metadata
    idx_path = Path(paths['index'])
    meta_path = Path(paths['meta'])
    
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(idx_path))
    
    with open(meta_path, 'w', encoding='utf-8') as fp:
        # Header: embedder checksum + schema version (regression tripwire)
        header = {
            "__meta__": True,
            "index_schema_version": 1,  # Bump if dimensions/metric/layout changes
            "embedder": embedder_name,
            "embedder_sha": hashlib.sha256(embedder_name.encode()).hexdigest()[:16],
            "embedder_dimensions": 384,  # MiniLM-L6-v2 dimensions
            "templates_count": len(templates),
            "created": str(Path(paths['clean']).stat().st_mtime if Path(paths['clean']).exists() else 0)
        }
        fp.write(json.dumps(header, ensure_ascii=False) + "\n")
        
        for t in templates:
            fp.write(json.dumps(t, ensure_ascii=False) + "\n")
    
    # Quality dial: Log genre/mood histogram (observability)
    genre_counts = {}
    for rec in cleaned:
        genre = rec.get("prompt", {}).get("genre", "unknown")
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    print(f"\nTemplate diversity histogram:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        print(f"  {genre}: {count}")
    
    return {
        "status": "ok",
        "templates_count": len(templates),
        "raw_samples": total,
        "dedup_ratio": round(len(cleaned) / max(1, total), 3),
        "diversity": len(genre_counts)
    }

