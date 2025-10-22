# CARMA Core - Cognitive Adaptive Recursive Memory Architecture

**Purpose:** STM/LTM memory consolidation with compression, retrieval, and learning

## What It Does

- Short-term memory (STM) buffering
- Long-term memory (LTM) compression and storage
- Semantic clustering and fragment fusion
- Memory retrieval with relevance scoring
- Automatic consolidation during sleep cycles

## Key Components

- `carma_core.py` - Main memory engine
- `core/fragment_manager.py` - Memory fragment operations
- `core/compression.py` - Memory compression algorithms
- `core/retrieval.py` - Semantic search and retrieval
- `implementations/` - Rust-accelerated implementations

## Usage

```python
from carma_core.carma_core import CARMACore

carma = CARMACore()
carma.store_stm(fragment)
carma.consolidate()
results = carma.retrieve("query")
```

## Configuration

See `config/carma_config.json` for compression thresholds, clustering parameters, and storage settings.

