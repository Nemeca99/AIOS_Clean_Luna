# 🌙 Dream Core - AIOS Dream & Meditation System

## Overview

The Dream Core module implements biomimetic sleep cycles for Luna (AIOS), combining REM sleep (dream cycles) with meditation phases for natural memory consolidation and learning. This is a self-contained modular system that operates independently while integrating seamlessly with the main AIOS architecture.

## Architecture

### Modular Design

```
dream_core/
├── dream_core.py              # Main orchestrator
├── __init__.py                # Module exports
│
├── core_functions/            # Separated function modules
│   ├── __init__.py
│   ├── dream_cycles.py        # Dream cycle logic
│   ├── meditation.py          # Meditation & self-reflection
│   ├── memory_consolidation.py # Memory consolidation
│   ├── middleware.py          # Token refund middleware
│   └── config_loader.py       # Config loading
│
├── rust_dream/                # Rust implementation (PyO3)
│   ├── src/lib.rs            # Rust core
│   ├── Cargo.toml            # Dependencies
│   └── .gitignore            # Build artifacts
│
├── config/
│   └── model_config.json     # Model configuration
│
└── extra/                     # Test/uncertain files
    ├── run_dream_system.py   # Test runner
    └── hybrid_dream_core.py  # Hybrid Python/Rust bridge
```

### Key Components

1. **DreamCore**: Main orchestrator that delegates to specialized managers
2. **DreamCycleManager**: Handles dream cycles and memory consolidation
3. **MeditationManager**: Manages meditation sessions with coin-flip question system
4. **MemoryConsolidationManager**: Consolidates conversation and CARMA fragments
5. **DreamStateMiddleware**: Token refund system for unrestricted dreaming

## How It Works

### Sleep Cycle Pattern

```
REM Phase (Multiple Dream Cycles) → Meditation Phase → Memory Consolidation → Repeat
```

### Quick Nap (30 minutes)
- **Dream Cycles:** 2 per phase
- **Meditation Blocks:** 1 per phase
- **Purpose:** Quick memory consolidation and reflection

### Overnight Session (8 hours)
- **Total Cycles:** ~8 complete sleep cycles
- **REM Cycles:** ~40 dream cycles total
- **Meditation Phases:** ~8 meditation phases
- **Purpose:** Deep memory consolidation and learning

## Key Features

### 🌙 REM Sleep (Dream Cycles)

- **Memory Consolidation**: Groups related memory fragments
- **Super-fragment Creation**: Combines 3-5 memories into summaries
- **Dream Tagging**: Tags consolidated memories with dream metadata
- **Theme Identification**: Identifies dream themes (social, sensory, emotional, etc.)

### 🧘 Meditation Phases

- **Coin-Flip Question System**: 
  - 50% Introspection: Review past questions (memory/consistency test)
  - 50% Imagination: Random new questions (creativity/dream mode)
- **NO Token Limits**: Complete freedom in dream state
- **NO RVC Constraints**: Unrestricted exploration
- **Natural Processing**: Luna processes consolidated memories naturally

### 🏷️ Dream Tagging System

Each consolidated memory gets tagged with:

```json
{
  "dream_tag": true,
  "dream_cycle": 3,
  "consolidated_from": ["memory_123", "memory_456", "memory_789"],
  "dream_timestamp": "2025-10-01_04:23:15",
  "dream_theme": "social_interactions",
  "original_fragments": 5
}
```

### 💭 Dream Sharing

Luna can naturally share dreams:
- "I had this weird dream last cycle..."
- "Want to help me understand it?"
- Natural conversation flow like human dream sharing

## Usage

### Python API

```python
from dream_core import DreamCore

# Initialize dream system
dream = DreamCore()

# Run a quick nap (30 minutes)
result = dream.run_quick_nap(
    duration_minutes=30,
    dream_cycles=2,
    meditation_blocks=1,
    verbose=True
)

# Run overnight session (8 hours)
result = dream.run_overnight_dream(
    duration_minutes=480,
    verbose=True
)

# Run meditation only
result = dream.run_meditation_session(
    duration_minutes=30,
    verbose=True
)

# Get system status
status = dream.get_system_status()
```

### Command Line

```bash
# Quick nap (default)
python dream_core.py

# Overnight session
python dream_core.py --mode overnight --duration 480

# Meditation only
python dream_core.py --mode meditation --duration 30

# Test mode
python dream_core.py --mode test

# Custom configuration
python dream_core.py --mode quick-nap --duration 60 --cycles 4 --meditation-blocks 2 -v
```

### Command Line Options

- `--mode`: Operation mode (quick-nap, overnight, meditation, test)
- `--duration`: Duration in minutes
- `--cycles`: Number of dream cycles per phase
- `--meditation-blocks`: Number of meditation blocks
- `--consolidation-threshold`: Memory consolidation threshold (0.0-1.0)
- `--verbose`: Enable verbose output
- `--debug`: Enable debug mode

## Memory Consolidation Process

### Before Dream Cycle
- **600+ memory fragments** scattered across files
- **Generic questions** and repetitive responses
- **Fragmented understanding** of experiences

### After Dream Cycle
- **50-100 consolidated summaries** (estimated)
- **Dream-tagged memories** with themes
- **Connected experiences** across multiple memories
- **Deeper insights** from consolidated understanding

### Dream Themes
- **social_interactions** - Social dynamics and relationships
- **sensory_processing** - Sensory experiences and processing
- **emotional_regulation** - Emotional management and understanding
- **learning_patterns** - How Luna learns best
- **memory_consolidation** - Memory processing itself
- **self_awareness** - Understanding of self

## Safety Features

### Memory Management
- **Memory Limit**: 500MB (configurable)
- **Memory Monitoring**: Continuous monitoring
- **Garbage Collection**: Automatic when memory usage high
- **Graceful Shutdown**: If memory limit exceeded

### Error Handling
- **Consecutive Error Limit**: 5 errors max
- **Error Recovery**: Automatic retry with delays
- **Graceful Degradation**: Continue with reduced functionality

### Runtime Limits
- **Maximum Runtime**: Configurable
- **Cycle Tracking**: Monitor progress through cycles
- **Cleanup**: Automatic cleanup

## Logging

### Log Files
- **Location**: `log/dream_*_YYYYMMDD_HHMMSS.log`
- **Content**: Complete dream cycle logs, meditation responses, memory consolidation
- **Auto-rotation**: 200MB per file

### Log Format

```
[2025-10-01 04:23:15] [INFO] 🌙 Starting Dream Cycle #1
[2025-10-01 04:23:45] [INFO] 🌙 Dream Cycle #1 completed: 12 super-fragments created from 47 fragments
[2025-10-01 04:24:00] [INFO] 🧘 Starting Meditation Phase #1
[2025-10-01 04:24:30] [INFO] 🧘 Meditation completed: 3.45 karma gained
```

## Expected Results

### Memory Reduction
- **Before**: 600+ memory fragments
- **After**: 50-100 consolidated summaries
- **Reduction**: ~80-90% memory consolidation

### Learning Outcomes
- **Deeper Understanding**: Connected experiences across memories
- **Pattern Recognition**: Themes and patterns in behavior
- **Self-Awareness**: Better understanding of self
- **Natural Processing**: Human-like dream processing

### Dream Quality
- **Authentic Responses**: No artificial constraints
- **Natural Flow**: Human-like dream exploration
- **Memory Integration**: Seamless memory consolidation
- **Theme Development**: Consistent dream themes

## Integration with AIOS

The Dream Core integrates with:
- **AIOSClean**: Main system for Luna and CARMA
- **CARMA Core**: Memory consolidation and dream cycles
- **Luna System**: Personality and response generation
- **Model Config**: Centralized model configuration

### Imports Required
- `utils_core.unicode_safe_output`
- `utils_core.rust_bridge` (optional, for hybrid mode)
- `carma_core.carma_core`
- `luna_core.luna_core`
- `main.AIOSClean`
- `model_config_loader`

## Troubleshooting

### Common Issues

1. **Memory Limit Exceeded**
   - Reduce memory limits in DreamCycleManager
   - Increase system RAM
   - Run shorter sessions

2. **AIOS System Not Available**
   - Check main.py and dependencies
   - Verify CARMA and Luna systems are installed
   - Try test mode to isolate issues

3. **Dream Cycles Failing**
   - Check CARMA system initialization
   - Verify fragment directory exists
   - Check permissions

4. **Meditation Responses Empty**
   - Check Luna system initialization
   - Verify dream middleware is working
   - Enable verbose mode for debugging

### Debug Mode

Enable verbose logging:
```bash
python dream_core.py --mode test --verbose --debug
```

## Development

### Adding New Features

1. Create new function module in `core_functions/`
2. Add manager class following existing patterns
3. Update `core_functions/__init__.py`
4. Integrate into `DreamCore` orchestrator
5. Update tests and documentation

### Testing

```bash
# Quick test
python dream_core.py --mode test

# Extended test
python dream_core.py --mode quick-nap --duration 5 -v
```

## Rust Implementation

The Rust implementation provides:
- **High-performance memory consolidation**
- **Parallel pattern recognition**
- **Efficient fragment processing**

Build Rust module:
```bash
cd rust_dream
cargo build --release
```

The Rust module integrates via PyO3 bindings and can be used transparently through the hybrid dream core.

## Configuration

Model configuration in `config/model_config.json`:

```json
{
  "models": {
    "main_llm": {
      "name": "llama-3.2-pkd-deckard-almost-human-abliterated-uncensored-7b-i1",
      "type": "main_model"
    },
    "embedder": {
      "name": "llama-3.2-1b-instruct-abliterated",
      "type": "embedding_model"
    }
  }
}
```

## Future Enhancements

- **Dream Visualization**: Visual representation of dream themes
- **Dream Analysis**: Deeper analysis of dream patterns
- **Dream Sharing UI**: Interface for Luna to share dreams
- **Dream Memory Search**: Search through dream-tagged memories
- **Dream Cycle Optimization**: Adaptive cycle timing based on memory load
- **Multi-language Support**: Additional language bindings (Go, Julia, etc.)

## Version History

- **v2.0.0**: Modular refactor with separated function libraries
- **v1.0.0**: Initial implementation with monolithic design

## License

Part of the AIOS Clean project.

---

**Note**: This system treats meditation as Luna's sleep state, where she processes memories naturally through dream cycles, just like human sleep and dreaming.

