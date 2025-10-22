# RAG Core - Retrieval-Augmented Generation

**Purpose:** Document retrieval and knowledge augmentation

## What It Does

- Document embedding and indexing
- Semantic search
- Manual oracle (AIOS documentation retrieval)
- Context injection for LLM prompts
- Citation tracking

## Key Components

- `embedder.py` - Document embedding (Nomic)
- `vector_store.py` - Vector storage and search
- `manual_oracle/` - AIOS manual RAG system
- `citation_tracker.py` - Source attribution

## Usage

```python
from rag_core.embedder import Embedder

embedder = Embedder()
results = embedder.search("query", top_k=5)
```

## Configuration

See `config/rag_config.json` for embedding models and search parameters.
See `docs/RAG_CORE_EMBEDDER_CONFIG.md` for setup guide.

