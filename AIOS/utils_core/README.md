# AIOS Utils Core Module

**Version:** 2.0.0  
**Status:** Refactored and Unified  
**Module Type:** Utilities  
**Links to:** `F:\AIOS_Clean\main.py`

## Overview

The Utils Core module is the central utility hub for all AIOS core files. It provides common functionality, data validation, inter-core communication utilities, and hybrid Python/Rust execution capabilities.

**Key Features:**
- ✅ **Unified Core**: Single `core.py` file combining all core functionality
- ✅ **Modular Structure**: Organized into logical subdirectories by function
- ✅ **Self-Contained**: All files reference only `utils_core/` (no external dependencies)
- ✅ **Hybrid Execution**: Python/Rust hybrid for performance-critical operations
- ✅ **No Duplicate Code**: Eliminated all duplicate patterns across files

## Architecture

```
utils_core/
├── core.py                      # THE UNIFIED CORE FILE ⭐
├── __init__.py                  # Module exports
│
├── base/                        # Foundation Layer
│   ├── unicode_safety.py        # Unicode handling (loads FIRST)
│   ├── system_base.py           # CoreSystemBase & CoreSystemManager
│   └── initializer.py           # SystemInitializer
│
├── validation/                  # Validation & Standards
│   ├── file_standards.py        # AIOS file standards
│   ├── json_standards.py        # AIOS JSON standards
│   ├── timestamp_validator.py   # Timestamp validation
│   └── pii_redactor.py          # PII redaction
│
├── operations/                  # Core Operations
│   └── (functionality in core.py)
│
├── monitoring/                  # Monitoring & Tracking
│   ├── provenance.py            # Provenance logging
│   ├── cost_tracker.py          # Cost & performance tracking
│   ├── canary_controller.py     # Canary rollout control
│   └── adaptive_routing.py      # Adaptive routing
│
├── resilience/                  # Resilience & Recovery
│   └── resilience_policies.py   # Retry, timeout, caching
│
├── bridges/                     # External Integrations
│   ├── rust_bridge.py           # Rust integration
│   └── powershell_bridge.py     # PowerShell integration
│
├── services/                    # Specialized Services
│   ├── data_deletion.py         # GDPR data deletion
│   ├── schema_migrator.py       # Schema migration
│   └── model_config.py          # Model configuration
│
├── rust_utils/                  # Rust Implementations
│   ├── Cargo.toml
│   ├── src/lib.rs
│   └── target/
│
├── extra/                       # Uncertain Files (Review Later)
│   ├── chatgpt_conversation_extractor.py
│   ├── psycho_semantic_rag_system.py
│   ├── refactor_cores.py
│   └── refactored_example_backup_core.py
│
├── logs/                        # Log files
├── cache/                       # Cache files
├── temp/                        # Temporary files
└── config/                      # Configuration files
```

## The Unified Core (`core.py`)

The `core.py` file is the heart of the utils_core module, combining functionality from:

1. **Base System**: Initialization, directory management, system info
2. **Data Validation**: JSON, text, file path validation
3. **File Operations**: Safe read/write with atomic operations
4. **Hashing**: File hashing, content IDs
5. **Inter-Core Communication**: Standardized message format
6. **System Monitoring**: Metrics, usage tracking, cleanup
7. **Hybrid Execution**: Python/Rust switching for performance

### Usage Examples

```python
from utils_core import UtilsCore

# Initialize the core system
utils = UtilsCore(use_rust=True)

# Data validation
result = utils.validate_data(my_data, data_type="json")
print(f"Valid: {result['valid']}")

# Safe file operations
content = utils.safe_file_read("myfile.txt")
utils.safe_file_write("output.txt", "Hello World")

# Generate content IDs
content_id = utils.generate_content_id("My content", prefix="DOC")

# Inter-core messaging
message = utils.create_core_message(
    source_core="utils",
    target_core="data",
    message_type="request",
    data={"query": "get_stats"}
)

# System metrics
metrics = utils.get_system_metrics()
print(f"Uptime: {metrics['system_uptime']:.2f}s")
print(f"Implementation: {metrics['implementation']}")
```

## Module Layers

### 1. Base Layer

**Purpose:** Foundation components that all other layers depend on

**Components:**
- `unicode_safety.py` - Handles Unicode encoding (CRITICAL - loads first)
- `system_base.py` - Base classes for all AIOS cores
- `initializer.py` - Standardized system initialization

**Usage:**
```python
from utils_core.base import CoreSystemBase, SystemInitializer

class MyCore(CoreSystemBase):
    def __init__(self):
        super().__init__("mycore", "mycore_dir")
```

### 2. Validation Layer

**Purpose:** Data validation and standards enforcement

**Components:**
- File standards validation
- JSON standards validation
- Timestamp validation
- PII redaction

**Usage:**
```python
from utils_core.validation import AIOSFileValidator, PIIRedactor

validator = AIOSFileValidator()
result = validator.validate_file("myfile.py")

redactor = PIIRedactor()
clean_text, redactions = redactor.redact_text("Email: user@example.com")
```

### 3. Monitoring Layer

**Purpose:** System monitoring, tracking, and analytics

**Components:**
- Provenance logging (NDJSON)
- Cost & performance tracking
- Canary rollout control
- Adaptive routing

**Usage:**
```python
from utils_core.monitoring import get_hypothesis_logger, get_cost_tracker

logger = get_hypothesis_logger()
logger.append({"event": "test", "data": "value"})

tracker = get_cost_tracker()
summary = tracker.get_session_summary()
```

### 4. Resilience Layer

**Purpose:** Error handling, retry logic, and recovery

**Components:**
- Retry policies with exponential backoff
- Timeout handling
- Result caching

**Usage:**
```python
from utils_core.resilience import with_retry, with_timeout, get_result_cache

@with_retry()
@with_timeout(30)
def my_function():
    # Function with retry and timeout
    pass

cache = get_result_cache()
cache.put("key", "value")
```

### 5. Bridges Layer

**Purpose:** Integration with external systems

**Components:**
- Rust bridge for performance
- PowerShell bridge for system operations

**Usage:**
```python
from utils_core.bridges import RustBridge, PowerShellBridge

# Rust integration
rust = RustBridge("utils", "./rust_utils")
if rust.is_available():
    print("Rust acceleration enabled")

# PowerShell integration
ps = PowerShellBridge()
result = ps.get_system_status()
```

### 6. Services Layer

**Purpose:** Specialized utility services

**Components:**
- Data deletion (GDPR compliance)
- Schema migration
- Model configuration

**Usage:**
```python
from utils_core.services import DataDeletionService, SchemaMigrator

# GDPR data deletion
service = DataDeletionService()
result = service.delete_user_data(conv_id="123", dry_run=False)

# Schema migration
migrator = SchemaMigrator("data.ndjson")
migrator.migrate(target_version="1.0")
```

## Hybrid Python/Rust Execution

The utils_core module supports hybrid execution, automatically using Rust implementations when available for performance-critical operations.

**Rust Acceleration Benefits:**
- 🚀 **Performance**: 10-100x faster for computational tasks
- 🔒 **Safety**: Memory-safe operations
- ⚡ **Parallel**: Built-in parallelization support

**Automatic Fallback:**
If Rust is not compiled or available, the system automatically falls back to Python implementations without any code changes.

```python
# The system automatically chooses the best implementation
utils = UtilsCore(use_rust=True)  # Try Rust first
print(f"Using: {utils.current_implementation}")

# Manually switch implementations
utils.switch_to_python()  # Force Python
utils.switch_to_rust()    # Try to switch to Rust
```

## Internal Module Structure

### Key Principles

1. **Self-Contained**: All files reference only `utils_core/`
2. **No External Dependencies**: Except link to `F:\AIOS_Clean\main.py`
3. **Modular Design**: Each subdirectory has clear responsibility
4. **No Duplicates**: All duplicate code eliminated
5. **Clean Imports**: Proper `__init__.py` files in each directory

### Import Patterns

**✅ CORRECT:**
```python
from utils_core import UtilsCore
from utils_core.base import CoreSystemBase
from utils_core.validation import AIOSFileValidator
from utils_core.monitoring import get_hypothesis_logger
```

**❌ INCORRECT:**
```python
from luna_core import something  # External dependency
from support_core import other   # External dependency
```

## Files Moved to Extra/

These files have been moved to `extra/` for later review:

- `chatgpt_conversation_extractor.py` - Specific tool, not core utility
- `psycho_semantic_rag_system.py` - Has external dependencies (luna_core, support_core)
- `refactor_cores.py` - Helper script for refactoring
- `refactored_example_backup_core.py` - Example file

**Reason:** These files either have external dependencies that violate the module's self-contained principle, or are specialized tools rather than core utilities.

## Linking to Main.py

The utils_core module links to the main AIOS system at:

```
F:\AIOS_Clean\main.py
```

**How to Use from Main:**
```python
# In F:\AIOS_Clean\main.py
from utils_core import UtilsCore

utils = UtilsCore()
# Use all utility functions...
```

## Command Line Usage

The core can be run standalone for utility operations:

```bash
# Get system info
python core.py --action info

# Validate data
python core.py --action validate --data '{"test": "value"}' --type json

# Clean up old data
python core.py --action cleanup --days 30

# Get system metrics
python core.py --action metrics

# Disable Rust acceleration
python core.py --action info --no-rust
```

## Testing

Each subdirectory contains testable components:

```bash
# Test base layer
python base/unicode_safety.py
python base/system_base.py
python base/initializer.py

# Test validation layer
python validation/file_standards.py
python validation/json_standards.py

# Test core
python core.py --action info
```

## Maintenance

### Adding New Utilities

1. Determine which layer the utility belongs to
2. Add to appropriate subdirectory
3. Update the subdirectory's `__init__.py`
4. Import in `core.py` if needed
5. Export in main `__init__.py` if public API

### Updating Rust Components

```bash
cd rust_utils
cargo build --release
```

The Rust bridge will automatically detect and use the compiled module.

## Module Statistics

- **Total Files**: ~22 Python files organized
- **Subdirectories**: 7 functional layers
- **Core Files Combined**: 3 → 1 unified core
- **Lines of Code**: ~15,000 LOC organized and deduplicated
- **External Dependencies**: 0 (except main.py link)
- **Rust Integration**: Yes, with automatic fallback

## Version History

### v2.0.0 (Current - Refactored)
- ✅ Unified 3 core files into single `core.py`
- ✅ Organized into 7 functional subdirectories
- ✅ Eliminated all duplicate code
- ✅ Created clean, modular structure
- ✅ Maintained all existing functionality
- ✅ Added comprehensive documentation

### v1.0.0 (Previous)
- Multiple core files with overlapping functionality
- Flat file structure (all files in root)
- Duplicate initialization patterns
- Mixed responsibilities

## Support

For issues or questions about the utils_core module:

1. Check this README.md for usage examples
2. Review the code in `core.py` for implementation details
3. Check `extra/` folder for specialized tools
4. Refer to individual subdirectory `__init__.py` files for component exports

---

**Remember:** This module is self-contained and modular. All files reference only `utils_core/` internally, and the module links to `F:\AIOS_Clean\main.py` for integration with the broader AIOS system.

