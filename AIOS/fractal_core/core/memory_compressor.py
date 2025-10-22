#!/usr/bin/env python3
"""
Memory Compressor - EXTRACTED from CARMA
Advanced memory compression with semantic, temporal, hierarchical algorithms
"""

import time
from typing import Dict, List
from collections import defaultdict


class MemoryCompressor:
    """
    Advanced memory compression system.
    
    Algorithms:
    - Semantic: Remove duplicate concepts
    - Temporal: Cluster by time windows
    - Hierarchical: Group and summarize
    """
    
    def __init__(self):
        self.compression_ratio = 0.0
        self.compression_history = []
        self.compression_algorithms = {
            'semantic': self._semantic_compression,
            'temporal': self._temporal_compression,
            'hierarchical': self._hierarchical_compression
        }
    
    def compress_memory(self, fragments: List[Dict], algorithm: str = 'semantic') -> Dict:
        """Compress memory fragments using specified algorithm."""
        if algorithm not in self.compression_algorithms:
            algorithm = 'semantic'
        
        original_size = sum(len(f.get('content', '')) for f in fragments)
        compressed_fragments = self.compression_algorithms[algorithm](fragments)
        compressed_size = sum(len(f.get('content', '')) for f in compressed_fragments)
        
        self.compression_ratio = (original_size - compressed_size) / original_size if original_size > 0 else 0.0
        self.compression_history.append({
            'timestamp': time.time(),
            'algorithm': algorithm,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'ratio': self.compression_ratio
        })
        
        return {
            'compressed_fragments': compressed_fragments,
            'compression_ratio': self.compression_ratio,
            'space_saved': original_size - compressed_size
        }
    
    def _semantic_compression(self, fragments: List[Dict]) -> List[Dict]:
        """Compress fragments by removing redundant semantic information."""
        compressed = []
        seen_concepts = set()
        
        for fragment in fragments:
            content = fragment.get('content', '')
            concepts = self._extract_concepts(content)
            
            # Only keep if new concepts present
            if not concepts.issubset(seen_concepts):
                compressed.append(fragment)
                seen_concepts.update(concepts)
        
        return compressed
    
    def _temporal_compression(self, fragments: List[Dict]) -> List[Dict]:
        """Compress fragments by temporal clustering."""
        time_groups = defaultdict(list)
        
        for fragment in fragments:
            timestamp = fragment.get('timestamp', 0)
            time_window = int(timestamp // 3600)  # 1-hour windows
            time_groups[time_window].append(fragment)
        
        # Keep most important per window
        compressed = []
        for window_fragments in time_groups.values():
            if window_fragments:
                most_important = max(window_fragments, key=lambda f: len(f.get('content', '')))
                compressed.append(most_important)
        
        return compressed
    
    def _hierarchical_compression(self, fragments: List[Dict]) -> List[Dict]:
        """Compress fragments using hierarchical summarization."""
        if len(fragments) <= 1:
            return fragments
        
        groups = self._group_by_similarity(fragments)
        compressed = []
        
        for group in groups:
            if len(group) == 1:
                compressed.append(group[0])
            else:
                summary = self._create_group_summary(group)
                compressed.append(summary)
        
        return compressed
    
    def _extract_concepts(self, text: str) -> set:
        """Extract key concepts (simplified keyword extraction)."""
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        concepts = {word for word in words if len(word) > 3 and word not in stop_words}
        return concepts
    
    def _group_by_similarity(self, fragments: List[Dict]) -> List[List[Dict]]:
        """Group fragments by content similarity."""
        groups = []
        used = set()
        
        for i, fragment in enumerate(fragments):
            if i in used:
                continue
            
            group = [fragment]
            used.add(i)
            
            for j, other in enumerate(fragments[i+1:], i+1):
                if j in used:
                    continue
                
                if self._calculate_similarity(fragment, other) > 0.7:
                    group.append(other)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_similarity(self, frag1: Dict, frag2: Dict) -> float:
        """Calculate similarity between fragments."""
        content1 = frag1.get('content', '').lower()
        content2 = frag2.get('content', '').lower()
        
        if not content1 or not content2:
            return 0.0
        
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _create_group_summary(self, group: List[Dict]) -> Dict:
        """Create summary of fragment group."""
        all_content = ' '.join(f.get('content', '') for f in group)
        return {
            'content': f"Summary: {all_content[:200]}...",
            'timestamp': max(f.get('timestamp', 0) for f in group),
            'source_fragments': len(group),
            'type': 'summary'
        }

