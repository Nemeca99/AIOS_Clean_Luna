# Support Core Module

The Support Core module provides comprehensive system monitoring, health checks, caching, embedding operations, recovery systems, and security validation for the AIOS Clean system.

## Architecture

This module has been refactored from a monolithic 2,587-line file into a clean, modular structure with separate functional modules.

### Directory Structure

```
support_core/
├── core/                          # Core functionality modules
│   ├── __init__.py               # Export main classes
│   ├── config.py                 # Configuration system
│   ├── logger.py                 # Logging system
│   ├── health_checker.py         # Health monitoring
│   ├── security.py               # Security validation
│   ├── cache_operations.py       # Cache management
│   ├── embedding_operations.py   # Embedding & FAISS operations
│   ├── recovery_operations.py    # Recovery & healing systems
│   └── system_classes.py         # System configuration classes
│
├── support_core.py               # Main SupportSystem class
├── hybrid_support_core.py        # Rust/Python hybrid interface (main entry point)
├── system_monitor.py             # Real-time system monitoring
├── model_config.py               # Model configuration
│
├── config/                       # Configuration files
│   └── model_config.json
│
├── rust_support/                 # Rust implementation
│   ├── Cargo.toml
│   ├── Cargo.lock
│   └── src/
│       └── lib.rs
│
└── extra/                        # Non-core files
    ├── gui/                      # GUI applications
    ├── scripts/                  # Shell/PowerShell scripts
    ├── integration/              # Integration modules
    ├── build/                    # Build tools
    ├── docs/                     # Documentation
    └── misc/                     # Miscellaneous files
```

## Core Modules

### 1. Configuration (`core/config.py`)
- **Classes**: `AIOSConfig`, `AIOSConfigError`
- **Purpose**: Unified AIOS configuration system with validation and real-time updates
- **Features**:
  - Environment variable support
  - Atomic file operations
  - Configuration watchers
  - Validation rules

### 2. Logging (`core/logger.py`)
- **Classes**: `AIOSLogger`, `AIOSLoggerError`
- **Purpose**: Advanced logging system with structured output
- **Features**:
  - Log rotation
  - Level filtering
  - Buffer management
  - Background flushing

### 3. Health Checker (`core/health_checker.py`)
- **Classes**: `AIOSHealthChecker`, `AIOSHealthError`
- **Purpose**: System health monitoring and diagnostics
- **Features**:
  - Comprehensive health checks
  - Component status tracking
  - Performance monitoring
  - Issue detection and recommendations

### 4. Security (`core/security.py`)
- **Classes**: `AIOSSecurityValidator`
- **Purpose**: Security validation and input sanitization
- **Features**:
  - Path validation
  - Input sanitization
  - Security policy enforcement

### 5. Cache Operations (`core/cache_operations.py`)
- **Classes**: `CacheOperations`, `CacheRegistry`, `CacheBackup`, `CacheStatus`, `CacheMetrics`
- **Purpose**: Comprehensive cache management
- **Features**:
  - Fragment caching
  - Cache registry
  - Backup and restore
  - Statistics tracking

### 6. Embedding Operations (`core/embedding_operations.py`)
- **Classes**: `SimpleEmbedder`, `EmbeddingCache`, `FAISSOperations`, `EmbeddingSimilarity`
- **Purpose**: Embedding generation and vector operations
- **Features**:
  - Text embedding
  - FAISS vector indexing
  - Similarity calculations
  - Embedding caching

### 7. Recovery Operations (`core/recovery_operations.py`)
- **Classes**: `RecoveryOperations`, `SemanticReconstruction`, `ProgressiveHealing`, `RecoveryAssessment`
- **Purpose**: System recovery and healing
- **Features**:
  - Data recovery
  - Semantic reconstruction
  - Progressive healing
  - Health assessment

### 8. System Classes (`core/system_classes.py`)
- **Classes**: `SystemConfig`, `FilePaths`, `SystemMessages`
- **Purpose**: Core system configuration and utilities
- **Features**:
  - System configuration dataclasses
  - Path management
  - Message templates

## Main Components

### SupportSystem (`support_core.py`)
The main orchestrator that integrates all core modules into a unified system.

**Usage**:
```python
from support_core.support_core import SupportSystem

# Initialize system
support = SupportSystem(cache_dir="data_core/FractalCache")

# Run health check
health_status = support.run_health_check()

# Get system status
status = support.get_system_status()

# Create backup
backup_id = support.create_system_backup("my_backup")
```

### HybridSupportCore (`hybrid_support_core.py`)
Provides a hybrid Rust/Python implementation with automatic fallback.

**Usage**:
```python
from support_core.hybrid_support_core import HybridSupportCore

# Initialize hybrid system
hybrid = HybridSupportCore(cache_dir="data_core/FractalCache")

# System automatically uses Rust when available, falls back to Python
health = hybrid.run_health_check()

# Get current implementation
status = hybrid.get_status()
print(f"Using: {status['current_implementation']}")  # "rust" or "python"

# Manually switch implementations
hybrid.switch_implementation("python")
```

### SystemMonitor (`system_monitor.py`)
Real-time monitoring dashboard for all AIOS systems.

**Usage**:
```python
from support_core.system_monitor import AIOSSystemMonitor

monitor = AIOSSystemMonitor(update_interval=5.0)
monitor.start()

# Get metrics
metrics = monitor.get_current_metrics()
```

## Integration with Main System

The support_core module is designed to be imported and used by the main AIOS system located at `F:\AIOS_Clean\main.py`.

**From main.py**:
```python
from support_core.hybrid_support_core import HybridSupportCore

# Initialize support system
support = HybridSupportCore()

# Use throughout the application
health = support.run_health_check()
```

## Extra Files

The `extra/` directory contains non-core files organized by type:

- **extra/gui/**: GUI applications (PySimpleGUI, Streamlit, monitoring dashboard)
- **extra/scripts/**: Shell scripts (.bat, .ps1, .sh) for automation
- **extra/integration/**: Integration modules (CARMA hypothesis, conversation math, documentation loader)
- **extra/build/**: Build tools (Docker, executables)
- **extra/docs/**: Documentation files
- **extra/misc/**: Miscellaneous utility scripts and files

These files are kept for reference but are not required for core functionality.

## Development

### Running Tests
```python
# Run the main entry point
python support_core.py
```

### Adding New Modules
1. Create module in `core/` directory
2. Add exports to `core/__init__.py`
3. Import and use in `support_core.py`

### Modifying Existing Modules
Each module is independent and can be modified without affecting others, as long as the public interface remains consistent.

## Dependencies

See `requirements.txt` for Python dependencies.

### Core Dependencies
- numpy >= 1.21.0
- requests >= 2.25.0
- psutil >= 5.8.0

### Optional Dependencies  
- plotly >= 5.0.0 (for visualization)
- pandas >= 1.3.0 (for data analysis)

### Rust Dependencies
See `rust_support/Cargo.toml` for Rust dependencies.

## Relationship to Main Project

This module is part of the AIOS Clean project located at `F:\AIOS_Clean\`. It operates as a self-contained module that provides support functionality to the main system.

### Module Interconnections
- **Main System** (`F:\AIOS_Clean\main.py`): Entry point that uses all core modules
- **CARMA Core**: Uses support_core for caching and embeddings
- **Luna Core**: Uses support_core for health monitoring
- **Enterprise Core**: Uses support_core for system validation
- **Utils Core**: Provides utilities used by support_core (unicode_safe_output, rust_bridge)

## Refactoring Summary

This module was refactored from a single 2,587-line `support_core.py` file into:
- 8 focused core modules (~100-400 lines each)
- 1 orchestrator class (`SupportSystem`)
- 1 hybrid interface (`HybridSupportCore`)
- Clean separation of concerns
- Improved maintainability and testability

**Previous Structure**: Monolithic file with 27 classes
**New Structure**: Modular architecture with clear boundaries

## License

Part of the AIOS Clean project.

## Author

Travis Miner (Refactored by AI Assistant - Kia)

