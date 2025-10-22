"""
Right Hemisphere (Long-Term Memory)

Handles long-term memory operations for the Lyra Blackwall system.
Uses /memlong/ for persistent LTM storage.
Includes hooks for future semantic and vector memory integration.
"""

import os
import json

MEMLONG_DIR = os.path.join(os.path.dirname(__file__), '..', 'memlong')
LTM_FILE = os.path.join(MEMLONG_DIR, 'ltm_buffer.json')

class LongTermMemory:
    def __init__(self):
        self.memory = []
        self._ensure_dir()
        self.load()
        # Semantic/vector memory stubs
        self.semantic_hook = None
        self.vector_hook = None

    def _ensure_dir(self):
        os.makedirs(MEMLONG_DIR, exist_ok=True)

    def store(self, summary):
        """Store a compressed STM summary in LTM and persist."""
        self.memory.append(summary)
        self.save()
        # TODO: Add semantic/vector update logic here

    def retrieve_relevant(self, query=None, n=5):
        """Retrieve relevant memories (placeholder: return last n, or use semantic/vector search if available)."""
        if query and self.semantic_hook:
            return self.semantic_hook.semantic_search(query, top_n=n)
        if query and self.vector_hook:
            return self.vector_hook.vector_search(query, top_n=n)
        return self.memory[-n:] if self.memory else []

    def save(self):
        """Persist LTM buffer to disk."""
        with open(LTM_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f)

    def load(self):
        """Load LTM buffer from disk if available."""
        if os.path.exists(LTM_FILE):
            with open(LTM_FILE, 'r', encoding='utf-8') as f:
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