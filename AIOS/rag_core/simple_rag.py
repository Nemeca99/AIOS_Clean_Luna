"""
Simple Industry-Standard RAG System
A basic RAG implementation that can be swapped in for CARMA
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

# Lazy imports for heavy dependencies (defer until needed)
# from sentence_transformers import SentenceTransformer
# import faiss


class SimpleRAGSystem:
    """Simple, industry-standard RAG system for testing modularity"""
    
    def __init__(self, base_dir: str = "data_core", silent: bool = False):
        self.base_dir = Path(base_dir)
        self.embeddings_dir = self.base_dir / "simple_embeddings"
        self.documents_dir = self.base_dir / "simple_documents"
        self.silent = silent
        
        # Create directories
        self.embeddings_dir.mkdir(exist_ok=True)
        self.documents_dir.mkdir(exist_ok=True)
        
        # Initialize embedding model (using a lightweight model)
        if not silent:
            print("Initializing Simple RAG System...")
            print(f"   Documents directory: {self.documents_dir}")
            print(f"   Embeddings directory: {self.embeddings_dir}")
        
        try:
            # Use local SentenceTransformers with auto GPU detection
            from sentence_transformers import SentenceTransformer
            import torch
            
            # Auto-detect best device
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            self.embedding_dim = 384  # MiniLM dimension
            self.embedding_model = "all-MiniLM-L6-v2"
            self.embedding_device = device
            
            if not silent:
                device_name = torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'
                print(f"   Embedder: {self.embedding_model} ({device_name}, {self.embedding_dim}d)")
        except ImportError:
            print(f"   Warning: sentence-transformers not installed")
            print("   Simple RAG disabled - embeddings not available")
            self.embedder = None
            self.embedding_dim = 384
        except Exception as e:
            print(f"   Warning: Could not load embedder: {e}")
            print("   Simple RAG disabled - embeddings not available")
            self.embedder = None
            self.embedding_dim = 384
        
        # Initialize document store
        self.document_store = []
        self.embeddings_file = self.embeddings_dir / "embeddings.json"
        self.documents_file = self.documents_dir / "documents.json"
        
        # Note: Not using FAISS - using simple numpy similarity instead
        self.index = None
        
        # Load existing data
        self._load_documents()
        self._load_embeddings()
        
        if not silent:
            print(f"   Loaded {len(self.document_store)} documents")
            print("Simple RAG System Initialized")
    
    def _load_documents(self):
        """Load existing documents"""
        if self.documents_file.exists():
            try:
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    self.document_store = json.load(f)
            except Exception as e:
                print(f"   Error loading documents: {e}")
                self.document_store = []
        else:
            self.document_store = []
    
    def _save_documents(self):
        """Save documents to file"""
        try:
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.document_store, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   Error saving documents: {e}")
    
    def _load_embeddings(self):
        """Load existing embeddings and rebuild FAISS index"""
        if self.embeddings_file.exists():
            try:
                with open(self.embeddings_file, 'r', encoding='utf-8') as f:
                    embeddings_data = json.load(f)
                
                if embeddings_data and self.embedder:
                    # Rebuild FAISS index
                    embeddings = np.array(embeddings_data['embeddings'], dtype=np.float32)
                    self.index.add(embeddings)
                    print(f"   Loaded {len(embeddings)} embeddings into FAISS index")
            except Exception as e:
                print(f"   Error loading embeddings: {e}")
                # Lazy import if not already imported
                if self.index is None:
                    try:
                        import faiss as faiss_module
                        self.index = faiss_module.IndexFlatIP(self.embedding_dim)
                    except:
                        pass
    
    def _save_embeddings(self):
        """Save embeddings to file"""
        if self.embedder:
            try:
                # Get all embeddings from documents
                embeddings_list = [doc.get('embedding', []) for doc in self.document_store if 'embedding' in doc]
                embeddings_data = {
                    'embeddings': embeddings_list,
                    'metadata': {
                        'model': self.embedding_model,
                        'dimension': self.embedding_dim,
                        'count': len(embeddings_list)
                    }
                }
                
                with open(self.embeddings_file, 'w', encoding='utf-8') as f:
                    json.dump(embeddings_data, f, indent=2)
            except Exception as e:
                print(f"   Error saving embeddings: {e}")
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text using local SentenceTransformers"""
        if not self.embedder:
            return None
        
        try:
            # Local embedding (6ms vs 2000ms for API!)
            embedding = self.embedder.encode(text[:512], convert_to_numpy=True, show_progress_bar=False)
            return embedding / np.linalg.norm(embedding)  # Normalize
        except Exception:
            return None
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the RAG system"""
        if not content.strip():
            return None
        
        doc_id = f"doc_{len(self.document_store)}_{hash(content) % 10000}"
        
        # Create document entry
        document = {
            'id': doc_id,
            'content': content,
            'metadata': metadata or {},
            'timestamp': str(Path().cwd())  # Simple timestamp
        }
        
        # Add to document store
        self.document_store.append(document)
        
        # Generate embedding if embedder is available
        if self.embedder:
            try:
                embedding = self._get_embedding(content)
                if embedding is None:
                    return doc_id
                # Store embedding with document (no FAISS needed)
                document['embedding'] = embedding.tolist()
            except Exception as e:
                print(f"   Warning: Could not generate embedding: {e}")
        
        # Save documents
        self._save_documents()
        
        return doc_id
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not query.strip() or not self.embedder:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                return []
            
            # Calculate similarity with all documents (simple numpy search)
            results = []
            for doc in self.document_store:
                if 'embedding' not in doc:
                    continue
                
                doc_embedding = np.array(doc['embedding'])
                similarity = np.dot(query_embedding, doc_embedding)
                
                results.append({
                    'id': doc['id'],
                    'content': doc['content'],
                    'metadata': doc.get('metadata', {}),
                    'score': float(similarity)
                })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"   Error during search: {e}")
            return []
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query and return results in CARMA-compatible format"""
        # Search for relevant documents
        results = self.search(query, top_k=5)
        
        # Format results to match CARMA's expected output
        return {
            'query': query,
            'fragments_found': len(results),
            'conversation_memories_found': [],  # Simple RAG doesn't have conversation memory
            'fragments': [r['content'] for r in results],
            'results': results,
            'source': 'simple_rag'
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'total_documents': len(self.document_store),
            'embedded_documents': len([d for d in self.document_store if 'embedding' in d]),
            'embedding_dimension': self.embedding_dim,
            'embedder_model': self.embedding_model if self.embedder else 'none',
            'documents_file': str(self.documents_file),
            'embeddings_file': str(self.embeddings_file)
        }
