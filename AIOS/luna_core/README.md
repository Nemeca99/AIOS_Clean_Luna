# Luna Core - Conversational Intelligence

**Purpose:** Main conversational AI personality with context-aware responses

## What It Does

- Natural language understanding
- Context-aware response generation
- Personality consistency
- Emotional intelligence
- Multi-turn conversation management

## Key Components

- `core/luna_core.py` - Main Luna orchestrator
- `core/response_generator.py` - Response generation with LinguaCalc integration
- `core/personality.py` - Personality management
- `core/luna_lingua_calc.py` - Linguistic calculus operators
- `systems/luna_arbiter_system.py` - Response quality assessment
- `prompts/` - System prompts and playbooks

## Usage

```python
from luna_core.core.luna_core import LunaCore

luna = LunaCore()
response = luna.respond(user_input, context)
```

## Configuration

See `config/luna_config.json` for personality settings, prompt templates, and arbiter thresholds.

