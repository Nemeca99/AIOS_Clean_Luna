# Support Core - Utilities & Helpers

**Purpose:** Common utilities and helper functions

## What It Does

- Logging utilities
- File operations
- Path resolution
- Configuration management
- Common data structures

## Key Components

- `logger.py` - Centralized logging
- `file_utils.py` - File operations
- `config_loader.py` - Configuration loading
- `time_utils.py` - Time and date utilities

## Usage

```python
from support_core.logger import Logger

logger = Logger("component_name")
logger.log("INFO", "message")
```

## Configuration

See `config/support_config.json` for logging levels and paths.

