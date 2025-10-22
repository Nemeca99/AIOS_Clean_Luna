# Data Core Module

**Self-contained, organized data management system for AIOS Clean**

## Overview

The Data Core module is a unified, modular data management system that serves as the central data pipeline for the entire AIOS ecosystem. Fully reorganized with clean folder structure and logical categorization.

### Key Features

- **Clean Organization**: 5 main categories instead of 31 scattered folders
- **Unified Architecture**: Merged Python-only and Python-Rust hybrid implementations
- **Modular Design**: Core functionality split into specialized modules
- **Graceful Degradation**: Falls back to Python when Rust dependencies unavailable
- **Self-Contained**: All operations self-managed within this module
- **Comprehensive Analytics**: Full data pipeline tracking and metrics

## Module Structure

```
data_core/
├── data_core.py              # Main unified core (entry point)
├── model_config.py           # Model configuration loader
├── README.md                 # This file
├── REFACTOR_SUMMARY.md       # Refactoring history
│
├── system/                   # System code & configuration
│   ├── core/                # Modular function library
│   │   ├── __init__.py     # Exports
│   │   ├── stats.py        # Statistics gathering
│   │   ├── pipeline.py     # Data pipeline operations
│   │   ├── cleanup.py      # Cleanup & maintenance
│   │   ├── lessons.py      # Lesson retrieval
│   │   └── database.py     # Database operations
│   ├── config/             # Configuration files
│   ├── rust_data/          # Rust acceleration (optional)
│   └── docs/               # Project documentation
│
├── storage/                 # All data storage
│   ├── caches/
│   │   ├── fractal/       # Fractal fragment cache
│   │   ├── arbiter/       # Arbiter lesson cache
│   │   └── general/       # General cache
│   ├── databases/         # SQLite databases
│   ├── conversations/     # Conversation history
│   ├── embeddings/        # Embeddings storage
│   └── documents/         # Document storage
│
├── learning/               # Learning systems
│   ├── system/            # Learning system data
│   ├── data/              # Lesson data & templates
│   └── memory/            # Lesson memory
│
├── analytics/              # Analytics & testing
│   ├── metrics/           # Analytics metrics
│   ├── goldens/           # Golden test sets
│   ├── analysis/          # Analysis data
│   └── qa/                # QA retrieval data
│
├── working/                # Working directories
│   ├── logs/              # System logs
│   ├── temp/              # Temporary files
│   ├── exports/           # Data exports
│   └── imports/           # Data imports
│
├── archive/                # Archived & backup files
├── extra/                  # Unrelated files
└── journey_dont_delete/    # Journey documentation
```

## Folder Organization

### System (system/)
Contains all system-level code and configuration:
- **core/**: Modular Python functions (stats, pipeline, cleanup, lessons, database)
- **config/**: System configurations and model configs
- **rust_data/**: Rust acceleration code (optional)
- **docs/**: Project-level documentation

### Storage (storage/)
All data storage in one place:
- **caches/**: Fractal, Arbiter, and general caches
- **databases/**: SQLite database files
- **conversations/**: Conversation history
- **embeddings/**: Embeddings data
- **documents/**: Document storage

### Learning (learning/)
All learning-related systems:
- **system/**: Core learning system data
- **data/**: Lesson templates and user data
- **memory/**: Lesson memory and history

### Analytics (analytics/)
All analytics and testing:
- **metrics/**: Analytics metrics and state
- **goldens/**: Golden test sets and baselines
- **analysis/**: Analysis results and data
- **qa/**: QA retrieval and evaluation

### Working (working/)
Active working directories:
- **logs/**: All system logs
- **temp/**: Temporary files
- **exports/**: Data export outputs
- **imports/**: Import staging area

## Core API

### DataCore Class

Main class providing all data management functionality.

#### Initialization

```python
from data_core import DataCore

# Initialize with hybrid mode (auto-detect Rust)
core = DataCore(use_hybrid=True)

# Force Python-only mode
core = DataCore(use_hybrid=False)
```

#### New Directory Properties

```python
# System directories
core.core_dir              # system/core
core.config_dir            # system/config
core.rust_data_dir         # system/rust_data
core.docs_dir              # system/docs

# Storage directories
core.fractal_cache_dir     # storage/caches/fractal
core.arbiter_cache_dir     # storage/caches/arbiter
core.cache_dir             # storage/caches/general
core.database_dir          # storage/databases/database
core.conversations_dir     # storage/conversations
core.embeddings_dir        # storage/embeddings
core.documents_dir         # storage/documents

# Learning directories
core.learning_system_dir   # learning/system
core.lesson_data_dir       # learning/data
core.lesson_memory_dir     # learning/memory

# Analytics directories
core.analytics_dir         # analytics/metrics
core.goldens_dir           # analytics/goldens
core.analysis_dir          # analytics/analysis
core.qa_dir                # analytics/qa

# Working directories
core.logs_dir              # working/logs
core.temp_dir              # working/temp
core.exports_dir           # working/exports
core.imports_dir           # working/imports
```

#### Statistics Methods

```python
# Get cache statistics
fractal_stats = core.get_fractal_cache_stats()
arbiter_stats = core.get_arbiter_cache_stats()

# Get conversation statistics
conv_stats = core.get_conversation_stats()

# Get database statistics
db_stats = core.get_database_stats()

# Get comprehensive system overview
overview = core.get_system_overview()
```

#### Lesson Methods

```python
# Retrieve relevant lessons for a prompt
lessons = core.get_relevant_lessons(
    current_prompt="How do I implement authentication?",
    max_lessons=3
)
```

#### Pipeline Methods

```python
# Ingest data into the pipeline
result = core.ingest_data(
    data={"key": "value"},
    source="my_system",
    data_type="fragment"  # or "arbiter", "conversation", "log"
)

# Export data from the pipeline
result = core.export_data(
    data_type="fragment",
    target_format="json",  # or "csv", "txt"
    filter_criteria={"tag": "important"}
)

# Get pipeline metrics
metrics = core.get_pipeline_metrics()
```

#### Cleanup Methods

```python
# Cleanup old data (dry run)
results = core.cleanup_old_data(days_old=30, dry_run=True)

# Actually delete old data
results = core.cleanup_old_data(days_old=30, dry_run=False)
```

#### Backup Methods

```python
# Create a backup (stored in archive/)
backup_path = core.backup_data()

# Create named backup
backup_path = core.backup_data("my_backup_20251009")
```

## Command Line Usage

```bash
# Get system overview (default)
py data_core.py --action overview

# Get detailed statistics
py data_core.py --action stats

# Cleanup old data (dry run)
py data_core.py --action cleanup --days 30 --dry-run

# Actually cleanup old data
py data_core.py --action cleanup --days 30

# Create a backup
py data_core.py --action backup

# Create a named backup
py data_core.py --action backup --backup-name my_backup

# Force Python-only mode
py data_core.py --action overview --no-hybrid
```

## Integration with main.py

The data core is designed to be called from the main AIOS system at `F:\AIOS_Clean\main.py`.

**Integration Example:**

```python
# In main.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "data_core"))

from data_core import DataCore

# Initialize data core
data = DataCore()

# Use throughout application
stats = data.get_system_overview()
lessons = data.get_relevant_lessons("user prompt here")
data.ingest_data(some_data, "main_system", "fragment")
```

## Benefits of Reorganization

### Before
- 31 folders at root level
- Scattered organization
- Duplicate folders (log/logs, database/AIOS_Database)
- Empty folders mixed with active data
- Unclear purpose of folders

### After
- 9 organized categories
- Clear logical grouping
- No duplicates
- Clean separation of concerns
- Self-documenting structure

### Improvements
1. **80% Fewer Root Folders**: 31 → 9
2. **Logical Categorization**: System, Storage, Learning, Analytics, Working
3. **Easier Navigation**: Clear hierarchy
4. **Better Maintenance**: Related files together
5. **Cleaner Architecture**: Self-documenting structure

## Dependencies

### Required (Python Standard Library)
- `pathlib`, `json`, `sqlite3`, `shutil`, `time`, `datetime`, `typing`, `os`, `csv`, `argparse`

### Optional (External)
- `utils_core.unicode_safe_output`: Unicode output safety
- `utils_core.rust_bridge`: Rust acceleration bridge
- Rust toolchain (for Rust acceleration)

### Internal
- `system.core.stats`, `system.core.pipeline`, `system.core.cleanup`, `system.core.lessons`, `system.core.database`

## Configuration

Model configuration is loaded from `system/config/model_config.json` via `model_config.py`.

**Available Functions:**
- `get_main_model()`: Get main LLM model
- `get_embedder_model()`: Get embedder model
- `get_draft_model()`: Get draft model
- `get_data_embedder_model()`: Get data-specific embedder
- `get_data_main_model()`: Get data-specific main model

## Development Notes

### Adding New Functionality

1. **Modular Functions**: Add to appropriate `system/core/*.py` module
2. **Core Methods**: Add wrapper method in `DataCore` class
3. **Export**: Add to `system/core/__init__.py` exports
4. **Documentation**: Update this README

### File Organization Guidelines

- **System files**: Code, configs, docs → `system/`
- **Data files**: Any data storage → `storage/`
- **Learning data**: Lessons, training → `learning/`
- **Analytics**: Metrics, tests → `analytics/`
- **Temporary**: Logs, temp, exports → `working/`
- **Old files**: Backups, archives → `archive/`
- **Unrelated**: External projects → `extra/`

## Troubleshooting

### Import Errors

If you see import errors for `system.core`:
- Check that `system/core/` directory exists
- Ensure `system/core/__init__.py` is present
- Verify Python path includes data_core directory

### Path Errors

If paths seem wrong:
- Check new folder structure exists (system/, storage/, etc.)
- Run `py data_core.py --action overview` to verify
- Ensure _ensure_directories() has run

### Rust Compilation Errors

If Rust compilation fails:
- System automatically falls back to Python
- All functionality remains available
- Rust is optional for performance boost

## Version History

- **Organized Version (2025-10-09)**: Restructured 31 folders into 5 logical categories
- **Unified Version (2025-10-09)**: Merged data_core.py and hybrid_data_core.py
- **Hybrid Version**: Added Rust acceleration support
- **Original Version**: Pure Python implementation

## Quick Reference

**Root Files:**
- `data_core.py` - Main entry point
- `model_config.py` - Configuration loader
- `README.md` - This documentation

**Main Folders:**
- `system/` - Code & configuration
- `storage/` - Data storage
- `learning/` - Learning systems
- `analytics/` - Analytics & testing
- `working/` - Logs, temp, exports

**Special Folders:**
- `archive/` - Archived/backup files
- `extra/` - Unrelated files
- `journey_dont_delete/` - Journey docs (keep as-is)

## Support

For issues or questions:
1. Check this README for usage
2. Review `REFACTOR_SUMMARY.md` for changes
3. Check `working/logs/` for error messages
4. Review `system/docs/` for detailed documentation

---

**Clean, organized, and ready for production!** 🎯
