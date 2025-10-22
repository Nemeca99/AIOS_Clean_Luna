"""
Creative Index Info API
Returns index metadata for observability and startup checks

V5.1.1 CreativeRAG Hardening
"""

import json
from pathlib import Path
from typing import Dict, Optional


def get_creative_index_info(cfg: Dict) -> Dict:
    """
    Get creative index metadata for observability
    
    Returns counts, embedder, mtime, checksum, size
    
    Args:
        cfg: AIOS config dict with creative_mode
    
    Returns:
        dict with index info or error status
    """
    cm = cfg.get("creative_mode", {})
    idx_path = Path(cm.get("index_path", ""))
    meta_path = Path(cm.get("meta_path", ""))
    
    if not idx_path.exists() or not meta_path.exists():
        return {
            "status": "not_built",
            "reason": "index or metadata missing"
        }
    
    # Load metadata header
    header = None
    template_count = 0
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line:
                first = json.loads(first_line)
                if first.get("__meta__"):
                    header = first
                    # Count remaining lines
                    template_count = sum(1 for _ in f)
                else:
                    # No header, count all
                    template_count = 1 + sum(1 for _ in f)
    except Exception as e:
        return {
            "status": "error",
            "reason": f"metadata_read_failed: {e}"
        }
    
    # Get index file stats
    idx_stat = idx_path.stat()
    
    info = {
        "status": "ok",
        "templates_count": template_count,
        "embedder": header.get("embedder") if header else "unknown",
        "embedder_sha": header.get("embedder_sha") if header else "unknown",
        "index_schema_version": header.get("index_schema_version") if header else 0,
        "embedder_dimensions": header.get("embedder_dimensions") if header else 0,
        "index_size_bytes": idx_stat.st_size,
        "index_size_mb": round(idx_stat.st_size / (1024*1024), 2),
        "index_mtime": idx_stat.st_mtime,
        "meta_mtime": meta_path.stat().st_mtime
    }
    
    return info


def check_creative_index_parity(cfg: Dict) -> Dict:
    """
    Artifact parity guard: Check embedder match, FAISS freshness, size sanity
    
    V5.1.1 Ship Lock - call on startup
    
    Returns:
        dict with parity_ok (bool) and any issues (list)
    """
    info = get_creative_index_info(cfg)
    
    if info.get("status") != "ok":
        return {"parity_ok": False, "issues": ["index_not_built"]}
    
    issues = []
    
    # 1. Index schema version (fail loud on mismatch)
    expected_schema = 1
    if info.get("index_schema_version", 0) != expected_schema:
        issues.append(f"schema_mismatch: expected={expected_schema}, got={info.get('index_schema_version')}")
    
    # 2. Embedder name matches manifest
    expected_embedder = "sentence-transformers/all-MiniLM-L6-v2"
    if info.get("embedder") != expected_embedder:
        issues.append(f"embedder_mismatch: expected={expected_embedder}, got={info.get('embedder')}")
    
    # 3. FAISS size >= 8 KB when templates >= 50
    if info.get("templates_count", 0) >= 50:
        if info.get("index_size_bytes", 0) < 8192:
            issues.append(f"index_too_small: {info.get('index_size_bytes')} bytes for {info.get('templates_count')} templates")
    
    # 4. Check if cleaned corpus exists and is newer (freshness check)
    cm = cfg.get("creative_mode", {})
    cleaned_path = Path(cm.get("clean_corpus_path", ""))
    if cleaned_path.exists():
        cleaned_mtime = cleaned_path.stat().st_mtime
        if info.get("index_mtime", 0) < cleaned_mtime:
            issues.append(f"stale_index: FAISS older than cleaned corpus")
    
    return {
        "parity_ok": len(issues) == 0,
        "issues": issues,
        "info": info
    }

