#!/usr/bin/env python3
"""
Fractal Cache - Core Caching Logic (EXTRACTED from CARMA)
Week 3: Basic cache with policy support
CARMA extends this with psychological features
"""

import sys
from pathlib import Path
import time
import json
import hashlib
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))
from support_core.support_core import SystemConfig, SimpleEmbedder


class FractalCache:
    """
    Core fractal caching with split/merge operations.
    
    Extracted from CARMA, policy-aware for fractal_core.
    CARMA extends this as FractalMyceliumCache with psychological features.
    """
    
    def __init__(self, base_dir: str = "data_core/FractalCache"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Embedder
        self.embedder = SimpleEmbedder()
        
        # Registry
        self.file_registry = {}
        self.semantic_links = {}
        
        # Policy (set by fractal controller)
        self.current_policy = None
        
        # Metrics
        self.metrics = {
            'total_fragments': 0,
            'total_splits': 0,
            'total_merges': 0,
            'cache_hit_rate': 0.0
        }
        
        # Load existing
        self.load_registry()
        
        print(" Fractal Cache Initialized")
        print(f"    Base directory: {self.base_dir}")
        print(f"    Fragments: {len(self.file_registry)}")
    
    def apply_policy(self, memory_policy: 'MemoryPolicy'):
        """Apply memory policy from fractal controller."""
        self.current_policy = memory_policy
        
        # Policy-driven split/merge
        if memory_policy:
            self._apply_policy_operations()
    
    def _apply_policy_operations(self):
        """Apply split/merge based on current policy."""
        if not self.current_policy:
            return
        
        # Count operations for churn tracking
        splits_before = self.metrics['total_splits']
        merges_before = self.metrics['total_merges']
        
        # Split fragments if needed
        for frag_id, frag_data in list(self.file_registry.items()):
            entropy = self._calculate_entropy(frag_data)
            
            if entropy > self.current_policy.split_threshold:
                self._split_fragment(frag_id)
        
        # Merge similar fragments
        self._merge_similar_fragments(self.current_policy.merge_threshold)
        
        # Calculate churn
        splits_after = self.metrics['total_splits']
        merges_after = self.metrics['total_merges']
        
        return {
            'splits': splits_after - splits_before,
            'merges': merges_after - merges_before
        }
    
    def _calculate_entropy(self, frag_data: Dict) -> float:
        """Calculate fragment entropy (diversity measure)."""
        content = frag_data.get('content', '')
        if not content:
            return 0.0
        
        words = content.lower().split()
        if not words:
            return 0.0
        
        # Word diversity as entropy proxy
        unique_words = len(set(words))
        total_words = len(words)
        
        return unique_words / total_words
    
    def _split_fragment(self, frag_id: str):
        """Split a fragment into smaller pieces."""
        frag_data = self.file_registry.get(frag_id)
        if not frag_data:
            return
        
        content = frag_data.get('content', '')
        if len(content) < 100:  # Too small to split
            return
        
        # Simple split: middle point
        mid = len(content) // 2
        part1 = content[:mid]
        part2 = content[mid:]
        
        # Create child fragments
        frag_data['split'] = True
        frag_data['children'] = [
            f"{frag_id}_A",
            f"{frag_id}_B"
        ]
        
        # Add children to registry
        for part, suffix in [(part1, 'A'), (part2, 'B')]:
            child_id = f"{frag_id}_{suffix}"
            self.file_registry[child_id] = {
                'file_id': child_id,
                'content': part,
                'parent_id': frag_id,
                'level': frag_data.get('level', 0) + 1,
                'created': datetime.now().isoformat()
            }
        
        self.metrics['total_splits'] += 1
    
    def _merge_similar_fragments(self, threshold: float):
        """Merge fragments with similarity above threshold."""
        # Simple version: merge fragments with same parent
        # Full version: semantic similarity based
        
        parents = {}
        for frag_id, frag_data in self.file_registry.items():
            parent_id = frag_data.get('parent_id')
            if parent_id:
                if parent_id not in parents:
                    parents[parent_id] = []
                parents[parent_id].append(frag_id)
        
        # Merge siblings if policy allows
        for parent_id, children in parents.items():
            if len(children) >= 2:
                # Check if should merge
                # Simplified: merge if both small
                total_size = sum(
                    len(self.file_registry[child]['content']) 
                    for child in children 
                    if child in self.file_registry
                )
                
                if total_size < SystemConfig.MAX_FILE_SIZE:
                    self._merge_fragments(children, parent_id)
    
    def _merge_fragments(self, frag_ids: List[str], new_id: str):
        """Merge multiple fragments into one."""
        merged_content = []
        
        for frag_id in frag_ids:
            if frag_id in self.file_registry:
                merged_content.append(self.file_registry[frag_id]['content'])
                # Remove child
                del self.file_registry[frag_id]
        
        # Create merged fragment
        self.file_registry[new_id] = {
            'file_id': new_id,
            'content': '\n'.join(merged_content),
            'level': 0,
            'merged_from': frag_ids,
            'created': datetime.now().isoformat()
        }
        
        self.metrics['total_merges'] += 1
    
    def add_content(self, content: str, parent_id: str = None) -> str:
        """Add content to cache."""
        file_id = hashlib.md5((content + str(time.time())).encode()).hexdigest()[:16]
        
        self.file_registry[file_id] = {
            'file_id': file_id,
            'content': content,
            'parent_id': parent_id,
            'level': 0,
            'hits': 0,
            'created': datetime.now().isoformat()
        }
        
        self.metrics['total_fragments'] = len(self.file_registry)
        self.save_registry()
        
        return file_id
    
    def find_relevant(self, query_embedding, topk=3):
        """Find relevant fragments."""
        if not query_embedding:
            return []
        
        similarities = []
        for frag_id, frag_data in self.file_registry.items():
            if 'embedding' in frag_data and frag_data['embedding']:
                try:
                    similarity = self.calculate_similarity(query_embedding, frag_data['embedding'])
                    similarities.append((frag_id, similarity, frag_data))
                except Exception:
                    continue
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return FragmentResult objects
        class FragmentResult:
            def __init__(self, frag_id, frag_data, score):
                self.id = frag_id
                self.content = frag_data.get('content', '')
                self.score = score
                self.hits = frag_data.get('hits', 0)
                self.level = frag_data.get('level', 0)
        
        return [FragmentResult(fid, data, sim) for fid, sim, data in similarities[:topk]]
    
    def calculate_similarity(self, emb1, emb2):
        """Cosine similarity."""
        if not emb1 or not emb2:
            return 0.0
        
        try:
            emb1 = np.array(emb1)
            emb2 = np.array(emb2)
            
            dot = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def load_registry(self):
        """Load registry from disk."""
        registry_file = self.base_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    self.file_registry = data.get('file_registry', {})
                    self.semantic_links = data.get('semantic_links', {})
                    self.metrics = data.get('metrics', self.metrics)
            except Exception as e:
                print(f"  Error loading registry: {e}")
    
    def save_registry(self):
        """Save registry to disk."""
        registry_file = self.base_dir / "registry.json"
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            data = {
                'file_registry': self.file_registry,
                'semantic_links': self.semantic_links,
                'metrics': self.metrics
            }
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  Error saving registry: {e}")
    
    def get_cache_statistics(self) -> Dict:
        """Get cache statistics."""
        return {
            'total_fragments': len(self.file_registry),
            'total_splits': self.metrics.get('total_splits', 0),
            'total_merges': self.metrics.get('total_merges', 0),
            'cache_hit_rate': self.metrics.get('cache_hit_rate', 0.0)
        }

