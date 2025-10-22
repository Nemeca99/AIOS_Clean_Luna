# AIOS Scripts - Central Repository

**Location:** `F:\AIOS_Clean\scripts\`  
**Purpose:** All system scripts in one place

---

## Master Scripts

### MASTER_TEST.ps1
**Master test suite orchestrator**

```powershell
# Interactive menu
.\MASTER_TEST.ps1

# Targeted testing
.\MASTER_TEST.ps1 -demos
.\MASTER_TEST.ps1 -unit
.\MASTER_TEST.ps1 -fractal

# Full validation
.\MASTER_TEST.ps1 -all
```

**Features:**
- Runs all test suites
- Generates SYSTEM_REPORT.md
- Health scoring
- CLI flags for targeted testing

---

### reproduce.ps1
**Architecture validation and reproducibility bundle**

```powershell
# Architecture validation
.\scripts\reproduce.ps1

# Full system test
.\scripts\reproduce.ps1 -fullTest
```

**Features:**
- Runs all 5 demos with seed 42
- Updates spec timestamps
- Generates provenance log
- Exports metrics
- Validates documentation

---

## Utility Scripts

### provenance_to_rules.py
**Materialize provenance NDJSON into rules index**

```powershell
python scripts/provenance_to_rules.py `
  --in data_core/analytics/provenance.ndjson `
  --out dev_core/rules_index.json
```

**Purpose:** Convert append-only provenance logs into queryable rules (materialized view)

---

### memory_graph.py
**Memory graph maintenance operations**

```powershell
python scripts/memory_graph.py `
  --compact --prune --evict `
  --report dev_core/metrics/memory_maintenance.json
```

**Purpose:** Cleanup duplicates, prune low-value nodes, evict by LRU × centrality

---

### sd_metrics.py
**Speculative decoding telemetry**

```powershell
python scripts/sd_metrics.py `
  --session latest `
  --export dev_core/metrics/sd_metrics.csv
```

**Purpose:** Extract draft acceptance rate, stride, wall-clock savings

---

## Adding New Scripts

### Guidelines

1. **Place in this folder:** `F:\AIOS_Clean\scripts\`
2. **Add to this README:** Document purpose and usage
3. **Use relative paths:** Reference from project root
4. **Include help:** Add `-h` or `--help` flag
5. **Return exit codes:** 0 = success, 1 = failure

### Template

```python
#!/usr/bin/env python3
"""
My New Script
Brief description

Usage:
    python scripts/my_script.py --option value
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    parser = argparse.ArgumentParser(description="My script")
    parser.add_argument("--option", help="Option description")
    args = parser.parse_args()
    
    # Your logic here
    
    return 0  # Success

if __name__ == "__main__":
    sys.exit(main())
```

---

## Script Organization

```
scripts/
├── README.md                   # This file
├── MASTER_TEST.ps1             # Test orchestrator
├── reproduce.ps1               # Architecture validation
├── provenance_to_rules.py      # Provenance materialization
├── memory_graph.py             # Memory maintenance
└── sd_metrics.py               # SD telemetry
```

**All scripts in one place. Easy to find. Professional organization.**

---

*For usage examples, see: [QUICK_REFERENCE.md](../dev_core/QUICK_REFERENCE.md)*

