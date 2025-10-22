# Main Core - System Orchestration

**Purpose:** Central orchestration and audit subsystems

## What It Does

- System initialization and coordination
- Core routing and dispatch
- Audit and self-healing (audit_core/)
- Command-line interface
- System health monitoring

## Key Components

- `main_core.py` - Main orchestrator
- `audit_core/` - Self-healing and verification
  - `audit_v3_sovereign.py` - Main audit engine
  - `sandbox_ide.py` - Sandboxed code execution
- `cli/` - Command-line interface

## Usage

```python
from main_core.main_core import MainCore

main = MainCore()
main.initialize()
result = main.dispatch(command)
```

## Audit Core

The internal auditor performs:
- Static code analysis
- Runtime verification
- Self-healing repairs
- Security scans

See `audit_core/README.md` for audit-specific documentation.

