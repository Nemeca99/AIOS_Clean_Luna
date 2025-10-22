# Fractal Core - Recursive Reasoning Engine

**Purpose:** Multi-scale reasoning with recursive depth control

## What It Does

- Fractal question decomposition
- Recursive reasoning chains
- Depth-controlled exploration
- Cross-scale pattern matching
- Compression via abstraction layers

## Key Components

- `fractal_engine.py` - Main fractal reasoning engine
- `decomposer.py` - Question decomposition
- `recursion_controller.py` - Depth management
- `pattern_matcher.py` - Cross-scale patterns

## Usage

```python
from fractal_core.fractal_engine import FractalEngine

fractal = FractalEngine()
result = fractal.decompose(question, max_depth=3)
```

## Configuration

See `config/fractal_config.json` for recursion limits and decomposition strategies.

