"""
Left Hemisphere (Short-Term Memory)

Handles short-term memory operations for the Lyra Blackwall system.
Uses /memshort/ for persistent STM storage.
Includes hooks for future semantic and vector memory integration.
"""

import os
import json

MEMSHORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'memshort')
STM_FILE = os.path.join(MEMSHORT_DIR, 'stm_buffer.json')

class ShortTermMemory:
    def __init__(self, buffer_size=100):
        self.memory = []
        self.buffer_size = buffer_size
        self._ensure_dir()
        self.load()
        # Semantic/vector memory stubs
        self.semantic_hook = None
        self.vector_hook = None

    def _ensure_dir(self):
        os.makedirs(MEMSHORT_DIR, exist_ok=True)

    def store(self, item):
        """Add an item to short-term memory and flush if needed."""
        self.memory.append(item)
        if len(self.memory) > self.buffer_size:
            self.memory = self.memory[-self.buffer_size:]
        self.save()
        # TODO: Add semantic/vector update logic here

    def get_recent(self, n=5):
        """Retrieve the most recent n items from STM."""
        return self.memory[-n:]

    def should_compress(self):
        """Determine if STM should be compressed (REM trigger)."""
        return len(self.memory) >= self.buffer_size

    def compress(self):
        """Compress STM into a summary for LTM storage."""
        summary = " | ".join(self.memory[-10:])
        # TODO: Add semantic/vector compression logic here
        return summary

    def clear(self):
        """Clear STM after consolidation and save."""
        self.memory = []
        self.save()

    def save(self):
        """Persist STM buffer to disk."""
        with open(STM_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f)

    def load(self):
        """Load STM buffer from disk if available."""
        if os.path.exists(STM_FILE):
            with open(STM_FILE, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
        else:
            self.memory = []

    # --- Semantic/Vector Memory Hooks ---
    def set_semantic_hook(self, semantic_memory):
        """Attach a semantic memory engine for advanced search (future)."""
        self.semantic_hook = semantic_memory

    def set_vector_hook(self, vector_memory):
        """Attach a vector memory engine for advanced search (future)."""
        self.vector_hook = vector_memory

    def semantic_search(self, query, top_n=5):
        """Search STM using semantic memory engine (if attached)."""
        if self.semantic_hook:
            return self.semantic_hook.semantic_search(query, top_n=top_n)
        return []

    def vector_search(self, query, top_n=5):
        """Search STM using vector memory engine (if attached)."""
        if self.vector_hook:
            return self.vector_hook.vector_search(query, top_n=top_n)
        return []