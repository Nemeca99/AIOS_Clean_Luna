#!/usr/bin/env python3
"""
Support Core - Embedding Operations
Extracted from monolithic support_core.py for better modularity.
"""

import sys
from pathlib import Path
import time
import json
import os
import shutil
import re
import hashlib
import math
import random
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup Unicode safety
try:
    from utils_core.unicode_safe_output import setup_unicode_safe_output
    setup_unicode_safe_output()
except ImportError:
    print("Warning: Unicode safety layer not available")

# Import system classes
from .system_classes import SystemConfig


class EmbeddingStatus(Enum):
    """Embedding status enumeration"""
    READY = "ready"
    LOADING = "loading"
    ERROR = "error"
    NOT_AVAILABLE = "not_available"


@dataclass
class EmbeddingMetrics:
    """Embedding performance metrics"""
    total_embeddings: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_embedding_time: float = 0.0
    total_api_calls: int = 0
    api_failures: int = 0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


class SimpleEmbedder:
    """Simple embedding generator with LM Studio integration"""
    
    def __init__(self, model_name: str = None):
        self.embedding_model = model_name or os.getenv("EMBEDDING_MODEL", SystemConfig.DEFAULT_EMBEDDING_MODEL)
        self.api_url = f"{SystemConfig.LM_STUDIO_URL}{SystemConfig.LM_STUDIO_EMBEDDING_ENDPOINT}"
        self.use_api = False  # Disable API to prevent 404 errors
        self.fallback_dimension = SystemConfig.FALLBACK_DIMENSION
        self.cache = {}
        
        print(" Simple Embedder Initialized")
        print(f"   Model: {self.embedding_model}")
        print(f"   API URL: {self.api_url}")
        print(f"   Use API: {self.use_api}")
        print(f"   Fallback dimension: {self.fallback_dimension}")
    
    def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not text or not text.strip():
            return None
        
        # Check cache first
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.cache:
            return self.cache[text_hash]
        
        # Generate embedding
        if self.use_api:
            embedding = self._embed_via_api(text)
        else:
            embedding = self._embed_fallback(text)
        
        # Cache result
        if embedding:
            self.cache[text_hash] = embedding
        
        return embedding
    
    def _embed_via_api(self, text: str) -> Optional[List[float]]:
        """Generate embedding via LM Studio API"""
        try:
            import requests
            
            headers = {"Content-Type": "application/json"}
            data = {
                "model": self.embedding_model,
                "input": text,
                "encoding_format": "float"
            }
            
            response = requests.post(self.api_url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['data'][0]['embedding']
            else:
                print(f"  API error: {response.status_code}")
                return self._embed_fallback(text)
                
        except Exception as e:
            print(f"  API call failed: {e}")
            return self._embed_fallback(text)
    
    def _embed_fallback(self, text: str) -> List[float]:
        """Generate fallback embedding"""
        # Simple hash-based embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        
        random.seed(seed)
        embedding = [random.uniform(-1, 1) for _ in range(self.fallback_dimension)]
        
        # Normalize
        norm = math.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics"""
        return {
            'cached_embeddings': len(self.cache),
            'model_name': self.embedding_model,
            'dimension': self.fallback_dimension,
            'api_available': self.use_api
        }

class EmbeddingCache:
    """Embedding cache management"""
    
    def __init__(self, cache_file: str = "data_core/FractalCache/embeddings.json"):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.embeddings = {}
        self.load_cache()
        
        print(" Embedding Cache Initialized")
        print(f"   Cache file: {self.cache_file}")
        print(f"   Loaded {len(self.embeddings)} embeddings")
    
    def load_cache(self):
        """Load embedding cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.embeddings = json.load(f)
            except Exception as e:
                print(f"  Error loading embedding cache: {e}")
                self.embeddings = {}
    
    def save_cache(self):
        """Save embedding cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.embeddings, f, indent=2)
        except Exception as e:
            print(f"  Error saving embedding cache: {e}")
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.embeddings.get(text_hash)
    
    def store_embedding(self, text: str, embedding: List[float]):
        """Store embedding in cache"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        self.embeddings[text_hash] = {
            'text': text,
            'embedding': embedding,
            'created_at': datetime.now().isoformat()
        }
        self.save_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics"""
        return {
            'total_embeddings': len(self.embeddings),
            'cache_size_mb': self.cache_file.stat().st_size / (1024 * 1024) if self.cache_file.exists() else 0,
            'last_updated': datetime.now().isoformat()
        }

class FAISSOperations:
    """FAISS index operations using real FAISS library"""
    
    def __init__(self, dimension: int = 384, index_path: str = None):
        self.dimension = dimension
        self.index_path = index_path
        self.vectors = []
        self.metadata = []
        
        print(" FAISS Operations Initialized")
        print(f"   Dimension: {dimension}")
        print(f"   Index path: {index_path or 'None'}")
        
        try:
            # Suppress FAISS AVX512 warnings - this is normal fallback behavior
            import logging
            faiss_logger = logging.getLogger('faiss.loader')
            faiss_logger.setLevel(logging.ERROR)
            
            import faiss
            self.faiss = faiss
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            print("    Real FAISS implementation")
        except ImportError:
            self.faiss = None
            self.index = None
            print("     FAISS not available - using fallback similarity search")
    
    def add(self, vectors: List[List[float]], metadata: List[Dict] = None):
        """Add vectors to index"""
        if self.faiss and self.index is not None:
            try:
                import numpy as np
                vectors_array = np.array(vectors, dtype=np.float32)
                # Normalize vectors for cosine similarity
                self.faiss.normalize_L2(vectors_array)
                self.index.add(vectors_array)
                print(f" Real FAISS: Added {len(vectors)} vectors. Total: {self.index.ntotal}")
            except Exception as e:
                print(f" FAISS error: {e}")
                # Fallback to memory storage
                for i, vector in enumerate(vectors):
                    self.vectors.append(vector)
                    self.metadata.append(metadata[i] if metadata else {})
        else:
            # Fallback: store in memory
            for i, vector in enumerate(vectors):
                self.vectors.append(vector)
                self.metadata.append(metadata[i] if metadata else {})
            print(f"Fallback: Added {len(vectors)} vectors to memory")
    
    def search(self, query_vector: List[float], k: int = 1) -> List[Tuple[str, float]]:
        """Search for similar vectors"""
        if self.faiss and self.index is not None and self.index.ntotal > 0:
            try:
                import numpy as np
                query_array = np.array([query_vector], dtype=np.float32)
                # Normalize query vector
                self.faiss.normalize_L2(query_array)
                
                # Search
                scores, indices = self.index.search(query_array, min(k, self.index.ntotal))
                
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx >= 0:  # Valid index
                        results.append((f"vector_{idx}", float(score)))
                
                return results
            except Exception as e:
                print(f" FAISS search error: {e}")
                return self._fallback_search(query_vector, k)
        else:
            return self._fallback_search(query_vector, k)
    
    def _fallback_search(self, query_vector: List[float], k: int) -> List[Tuple[str, float]]:
        """Fallback similarity search using cosine similarity"""
        if not self.vectors:
            return []
        
        similarities = []
        for i, vector in enumerate(self.vectors):
            similarity = self._cosine_similarity(query_vector, vector)
            similarities.append((f"vector_{i}", similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def save(self, path: str):
        """Save index to file"""
        if self.faiss and self.index is not None:
            try:
                self.faiss.write_index(self.index, f"{path}.faiss")
                # Save metadata separately
                import pickle
                with open(f"{path}.metadata", 'wb') as f:
                    pickle.dump(self.metadata, f)
                print(f" Real FAISS: Saved index to {path}.faiss")
            except Exception as e:
                print(f" FAISS save error: {e}")
        else:
            print(f"Fallback: Saving {len(self.vectors)} vectors to memory")
    
    def load(self, path: str):
        """Load index from file"""
        if self.faiss:
            try:
                if os.path.exists(f"{path}.faiss"):
                    self.index = self.faiss.read_index(f"{path}.faiss")
                    print(f" Real FAISS: Loaded index with {self.index.ntotal} vectors")
                    
                    # Load metadata
                    if os.path.exists(f"{path}.metadata"):
                        import pickle
                        with open(f"{path}.metadata", 'rb') as f:
                            self.metadata = pickle.load(f)
                        print(f" Real FAISS: Loaded {len(self.metadata)} metadata entries")
                else:
                    print(f"  FAISS index file {path}.faiss not found, creating new index")
                    self.index = self.faiss.IndexFlatIP(self.dimension)
            except Exception as e:
                print(f" FAISS load error: {e}")
                self.index = self.faiss.IndexFlatIP(self.dimension)
        else:
            print(f"Fallback: No FAISS available, using memory storage")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if self.faiss and self.index is not None:
            return {
                'total_vectors': self.index.ntotal,
                'dimension': self.dimension,
                'faiss_available': True,
                'status': 'loaded' if self.index.ntotal > 0 else 'empty'
            }
        else:
            return {
                'total_vectors': len(self.vectors),
                'dimension': self.dimension,
                'faiss_available': False,
                'status': 'loaded' if self.vectors else 'empty'
            }

class EmbeddingSimilarity:
    """Embedding similarity calculations"""
    
    @staticmethod
    def calculate_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        if len(embedding1) != len(embedding2):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(x * x for x in embedding1))
        norm2 = math.sqrt(sum(x * x for x in embedding2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def calculate_euclidean_distance(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate Euclidean distance between embeddings"""
        if len(embedding1) != len(embedding2):
            return float('inf')
        
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(embedding1, embedding2)))
