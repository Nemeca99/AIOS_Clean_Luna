# Streamlit Core Module

**Self-contained, modular Streamlit UI system for AIOS Clean**

## Overview

The `streamlit_core` module provides a clean, organized, self-contained Streamlit-based UI system for the AIOS Clean project. It handles user interaction, state management, meditation engine, quality analytics, and model configuration.

This module is designed as a **modular system** where:
- All files reference only this folder
- The core file (`streamlit_core.py`) acts as the orchestrator
- All core functionality is broken into focused modules
- External dependencies are internalized
- Links to `F:\AIOS_Clean\main.py` for system-wide integration

## Architecture

```
streamlit_core/
├── core/                          # Core functionality modules
│   ├── __init__.py               # Module exports
│   ├── state_manager.py          # Session & persistent state management
│   ├── meditation_engine.py      # Meditation mode & heartbeat tracking
│   ├── ui_renderer.py            # UI rendering (chat, learning, analytics)
│   ├── model_config_manager.py   # Model configuration loader
│   └── dashboard_analytics.py    # Quality dashboard data processing
│
├── utils/                         # Internal utilities
│   ├── __init__.py
│   └── unicode_safety.py         # PowerShell Unicode compatibility
│
├── config/                        # Configuration files
│   └── model_config.json         # Model configuration (LLM, embedder, draft)
│
├── streamlit_core.py              # Main orchestrator - links all modules
├── quality_dashboard.py           # Quality metrics dashboard UI
├── model_config.py                # Model config convenience wrapper
│
├── streamlit_main/                # Streamlit open-source repo (keep as-is)
├── streamlit_docs/                # Streamlit documentation (keep as-is)
├── streamlit_components/          # Custom component templates (keep as-is)
├── streamlit_llm_examples/        # LLM example apps (keep as-is)
├── streamlit_examples/            # Example Streamlit apps (keep as-is)
│
├── extra/                         # Uncertain/future files
│   └── streamlit_frontend/       # Markdown documentation only
│
└── README.md                      # This file
```

## Core Modules

### 1. `streamlit_core.py` - Orchestrator

The main entry point and orchestrator for the entire UI system.

**Responsibilities:**
- Initialize all core components (StateManager, MeditationEngine, UIRenderer)
- Coordinate between modules
- Provide main() entry point for Streamlit
- Expose convenience methods for external access (links to main.py)

**Key Methods:**
- `run()` - Run the Streamlit application
- `get_state(key, default)` - Get state value
- `set_state(key, value)` - Set state value
- `start_meditation()` - Start meditation session
- `stop_meditation()` - Stop meditation session
- `get_meditation_info()` - Get meditation session info

**Usage:**
```python
from streamlit_core import StreamlitCore

# Initialize and run
core = StreamlitCore()
core.run()
```

### 2. `core/state_manager.py` - State Management

Handles session state and persistent state with memory leak protection.

**Features:**
- Session state via Streamlit
- Persistent state via pickle files
- Memory limits (10MB file size, 1000 keys max, 1MB per value)
- Backup and recovery
- Automatic validation

**Key Methods:**
- `load_persistent_state()` - Load from file
- `save_persistent_state(state)` - Save to file
- `get_state(key, default)` - Get state value
- `set_state(key, value, persistent)` - Set state value
- `clear_persistent_state()` - Clear all state

### 3. `core/meditation_engine.py` - Meditation System

Manages Luna's autonomous self-reflection mode (meditation).

**Features:**
- Heartbeat tracking for browser activity
- Session management (start, stop, track progress)
- Karma and efficiency scoring
- Session persistence

**Key Methods:**
- `update_heartbeat()` - Update browser activity timestamp
- `check_browser_active(max_idle_seconds)` - Check if browser is active
- `get_meditation_session_info()` - Get session status
- `start_meditation_session()` - Start new session
- `stop_meditation_session()` - Stop active session
- `update_meditation_progress(karma_delta, efficiency_score)` - Update metrics

### 4. `core/ui_renderer.py` - UI Rendering

Renders all user interface components and coordinates UI updates.

**Features:**
- Sidebar with system controls
- Main interface with tabs (Chat, Learning, Analytics, Settings)
- Chat interface with Luna
- Learning interface with meditation controls
- Analytics dashboard placeholder
- Settings interface

**Key Methods:**
- `render_sidebar()` - Render sidebar
- `render_main_interface()` - Render main UI with tabs
- `_render_chat_interface()` - Chat tab
- `_render_learning_interface()` - Learning tab with meditation
- `_render_analytics_interface()` - Analytics tab
- `_render_settings_interface()` - Settings tab

### 5. `core/model_config_manager.py` - Model Configuration

Loads and manages model configuration from JSON file.

**Features:**
- Load main LLM, embedder, and draft model configs
- Alternative model support
- Configuration reload
- Default fallback values

**Key Methods:**
- `get_main_model()` - Get main LLM name
- `get_embedder_model()` - Get embedder model name
- `get_draft_model()` - Get draft model name (if enabled)
- `get_model_config(model_type)` - Get full config for model type
- `reload_config()` - Reload from file

### 6. `core/dashboard_analytics.py` - Analytics Engine

Processes quality metrics, hypothesis tests, and routing data for the dashboard.

**Features:**
- NDJSON hypothesis data loading
- Adaptive routing state analysis
- Golden report comparisons
- SLO status calculations
- Chart data preparation

**Key Methods:**
- `load_frames()` - Load hypothesis and response dataframes
- `load_adaptive_state()` - Load routing state
- `load_golden_reports()` - Load golden reports
- `calculate_hypothesis_pass_rate(hdf)` - Calculate pass rates
- `get_routing_metrics(adaptive_state)` - Extract routing metrics
- `get_slo_status(adaptive_state, last_report)` - Calculate SLO status

### 7. `utils/unicode_safety.py` - Unicode Safety

Provides Unicode-safe output for PowerShell compatibility.

**Features:**
- Automatic character replacement (arrows, math symbols, etc.)
- Stdout/stderr wrapping
- Safe print functions
- ASCII fallback for problematic characters

**Key Functions:**
- `setup_unicode_safe_output()` - Initialize Unicode safety (auto-called on import)
- `safe_print(*args)` - Print with Unicode safety
- `safe_log(message, level)` - Log with Unicode safety

## Additional Files

### `quality_dashboard.py` - Quality Dashboard UI

Streamlit dashboard for visualizing quality metrics, hypothesis tests, A/B testing, and SLO monitoring.

**Features:**
- Hypothesis pass rate tracking
- A/B bucket distribution
- Routing source analysis
- Boundary drift monitoring with SLO alerts
- Latency P95 tracking
- Per-message drilldown

**Tabs:**
1. **Overview** - Traffic split and sources
2. **Hypotheses** - Hypothesis batch results and trends
3. **Routing** - Boundary drift and adaptive signals
4. **Drill-down** - Per-message event details
5. **Settings** - Paths and diagnostics

### `model_config.py` - Configuration Wrapper

Convenience wrapper for accessing model configuration throughout the module.

**Functions:**
- `get_main_model()` - Get main LLM name
- `get_embedder_model()` - Get embedder name
- `get_draft_model()` - Get draft model name
- `get_config_loader()` - Get loader instance

## Configuration

### Model Configuration (`config/model_config.json`)

```json
{
  "schema_version": 1,
  "model_config": {
    "models": {
      "main_llm": {
        "name": "llama-3.2-pkd-deckard-almost-human-abliterated-uncensored-7b-i1",
        "type": "main_model",
        "tier": "high_complexity"
      },
      "embedder": {
        "name": "llama-3.2-1b-instruct-abliterated",
        "type": "embedding_model",
        "tier": "trivial"
      },
      "draft_model": {
        "name": "mlabonne_qwen3-0.6b-abliterated",
        "enabled": false
      }
    }
  }
}
```

## Installation & Usage

### Prerequisites

- Python 3.8+
- Streamlit
- pandas
- plotly

### Running the Main UI

```bash
cd F:\AIOS_Clean\streamlit_core
streamlit run streamlit_core.py
```

### Running the Quality Dashboard

```bash
cd F:\AIOS_Clean\streamlit_core
streamlit run quality_dashboard.py
```

### Integration with main.py

```python
# In F:\AIOS_Clean\main.py
from streamlit_core.streamlit_core import StreamlitCore

# Initialize
ui = StreamlitCore()

# Access state
value = ui.get_state('my_key', default='default_value')
ui.set_state('my_key', 'new_value')

# Control meditation
ui.start_meditation()
info = ui.get_meditation_info()
ui.stop_meditation()
```

## Key Design Principles

1. **Modular**: Each core module has a single, clear responsibility
2. **Self-contained**: No external dependencies outside streamlit_core folder
3. **Orchestrated**: streamlit_core.py coordinates all modules
4. **Clean**: No duplicate code, everything in its logical place
5. **Maintainable**: Clear separation of concerns with focused modules
6. **Memory-safe**: Built-in protections against memory leaks
7. **Unicode-safe**: PowerShell compatibility on Windows

## File Responsibilities Summary

| File | Lines | Responsibility |
|------|-------|----------------|
| `streamlit_core.py` | ~100 | Orchestrator - coordinates all modules |
| `core/state_manager.py` | ~180 | State persistence and session management |
| `core/meditation_engine.py` | ~150 | Meditation mode and heartbeat tracking |
| `core/ui_renderer.py` | ~200 | All UI rendering logic |
| `core/model_config_manager.py` | ~180 | Model configuration loading |
| `core/dashboard_analytics.py` | ~270 | Analytics data processing |
| `utils/unicode_safety.py` | ~140 | Unicode safety for PowerShell |
| `quality_dashboard.py` | ~280 | Quality dashboard UI |
| `model_config.py` | ~45 | Configuration wrapper |

## Other Directories (Keep As-Is)

- **`streamlit_main/`** - Full Streamlit open-source repository (for reference/development)
- **`streamlit_docs/`** - Streamlit documentation site (for reference)
- **`streamlit_components/`** - Custom Streamlit component templates
- **`streamlit_llm_examples/`** - LLM integration example apps
- **`streamlit_examples/`** - General Streamlit example apps

## Future Enhancements

- Enhanced analytics visualizations
- Real-time Luna chat integration
- Advanced meditation tracking
- Multi-user session support
- Theme customization
- Extended SLO monitoring

## Version History

- **v1.0.0** (2025-10-10) - Initial refactored modular structure

## Author

AIOS Development Team

---

**Note:** This module is part of the AIOS Clean ecosystem and is designed to work independently while providing integration points to the main system through `F:\AIOS_Clean\main.py`.

