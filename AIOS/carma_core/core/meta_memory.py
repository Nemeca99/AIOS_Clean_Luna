#!/usr/bin/env python3
"""
CARMA Meta Memory
Hierarchical memory management system
"""

from __future__ import annotations
import sys
from pathlib import Path
import time
import uuid
from typing import Dict, List, TYPE_CHECKING

sys.path.append(str(Path(__file__).parent.parent.parent))
from support_core.support_core import SystemConfig

if TYPE_CHECKING:
    from .fractal_cache import FractalMyceliumCache


class CARMAMetaMemory:
    """Meta-memory system for hierarchical memory management."""
    
    def __init__(self, cache: FractalMyceliumCache):
        self.cache = cache
        self.episodic_memory = {}
        self.semantic_memory = {}
        self.super_fragments = {}
        self.memory_hierarchy = {}
        
        print(" CARMA Meta-Memory System Initialized")
        print(f"   Compression threshold: {SystemConfig.CONSOLIDATION_THRESHOLD}")
        print(f"   Semantic clustering: {SystemConfig.SEMANTIC_CLUSTERING}")
        print(f"   Episodic decay rate: {SystemConfig.EPISODIC_DECAY_RATE}")
    
    def create_episodic_memory(self, event_data: Dict) -> str:
        """Create an episodic memory."""
        memory_id = f"episode_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        episodic_memory = {
            'id': memory_id,
            'content': event_data.get('content', ''),
            'importance': event_data.get('importance', 0.5),
            'emotional_valence': event_data.get('emotional_valence', 0.0),
            'timestamp': time.time(),
            'context': event_data.get('context', {}),
            'tags': event_data.get('tags', [])
        }
        
        self.episodic_memory[memory_id] = episodic_memory
        print(f"Created episodic memory {memory_id} with importance {event_data.get('importance', 0.5)}")
        return memory_id
    
    def consolidate_episodic_to_semantic(self, theme: str) -> str:
        """Consolidate episodic memories to semantic memory."""
        related_episodes = []
        for episode_id, episode in self.episodic_memory.items():
            if theme.lower() in episode['content'].lower():
                related_episodes.append(episode)
        
        if len(related_episodes) < 2:
            return None
        
        semantic_id = f"semantic_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        patterns = self._extract_patterns(related_episodes)
        summary = f"Semantic memory for '{theme}': {patterns}"
        
        semantic_memory = {
            'id': semantic_id,
            'theme': theme,
            'summary': summary,
            'source_episodes': [ep['id'] for ep in related_episodes],
            'consolidation_timestamp': time.time(),
            'confidence': min(1.0, len(related_episodes) / 5.0)
        }
        
        self.semantic_memory[semantic_id] = semantic_memory
        return semantic_id
    
    def _extract_patterns(self, episodes: List[Dict]) -> str:
        """Extract patterns from episodes."""
        if not episodes:
            return "No patterns found"
        
        common_words = {}
        for episode in episodes:
            words = episode['content'].lower().split()
            for word in words:
                if len(word) > 3:
                    common_words[word] = common_words.get(word, 0) + 1
        
        top_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:5]
        pattern_words = [word for word, count in top_words]
        
        return f"Key patterns: {', '.join(pattern_words)}"
    
    def get_memory_statistics(self) -> Dict:
        """Get memory statistics."""
        return {
            'episodic_memories': len(self.episodic_memory),
            'semantic_memories': len(self.semantic_memory),
            'super_fragments': len(self.super_fragments),
            'hierarchy_levels': len(set(level for level in self.memory_hierarchy.values()))
        }

