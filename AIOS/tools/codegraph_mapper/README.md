# AIOS CodeGraph Mapper (CGM)

**Version:** 1.0.0  
**Status:** Production-ready  
**Owner:** AIOS Core Team

## What It Does

CodeGraph Mapper (CGM) is a **read-only** repository structural analyzer that generates a complete map of the AIOS codebase:

- 📁 **File inventory** - Every file with size, timestamps, SHA-256 hashes
- 📦 **Module graph** - Import relationships between Python modules
- 🔍 **Symbol index** - All classes, functions, and constants with locations
- 🔗 **Cross-file references** - Where symbols are used across files
- 📞 **Call graph** - Function calls within files
- 📊 **Multiple formats** - JSON, CSV, DOT, Mermaid
- 📝 **Human reports** - Markdown + interactive HTML

## Why You Need It

**Before CGM:**
- "Where is `ConsciousnessCore` used?"
- "What imports `carma_core`?"
- "Which modules have no dependencies?"
- Manual grep, fragile assumptions

**After CGM:**
- Query the graph: `jq '.nodes[] | select(.name=="ConsciousnessCore")' code_graph.json`
- See import matrix in Excel/Numbers
- Navigate interactive HTML report
- **Luna can understand her own architecture**

## Quick Start

### 1. Dry-Run (Safe - Default)

```powershell
cd L:\AIOS
python -m tools.codegraph_mapper.cgm.cli ^
  --root L:\AIOS ^
  --out L:\AIOS\_maps ^
  --dry-run
```

**Output:** `L:\AIOS\_maps\plan_<timestamp>.json` (no actual artifacts)

### 2. Real Run (Writes Artifacts)

```powershell
python -m tools.codegraph_mapper.cgm.cli ^
  --root L:\AIOS ^
  --out L:\AIOS\_maps ^
  --no-dry-run
```

**Output:** `L:\AIOS\_maps\<timestamp>\**` (all artifacts + provenance)

### 3. Real Run with Approval Gate

```powershell
python -m tools.codegraph_mapper.cgm.cli ^
  --root L:\AIOS ^
  --out L:\AIOS\_maps ^
  --no-dry-run ^
  --require-approval
```

**Flow:**
1. Tool scans and builds plan
2. Creates `APPROVAL_REQUIRED.txt` and pauses
3. Review the plan
4. Create `approval.ok` file to resume
5. Tool writes all artifacts

## Usage Examples

### Scan Specific Subdirectory

```powershell
python -m tools.codegraph_mapper.cgm.cli ^
  --root L:\AIOS\luna_core ^
  --out L:\AIOS\_maps ^
  --no-dry-run
```

### Include/Exclude Patterns

```powershell
python -m tools.codegraph_mapper.cgm.cli ^
  --root L:\AIOS ^
  --out L:\AIOS\_maps ^
  --include "**/*.py" "**/*.pyx" ^
  --exclude "**/__pycache__/**" "**/.venv/**" "**/test_*.py" ^
  --no-dry-run
```

### Skip Optional Outputs

```powershell
# Skip DOT and Mermaid (faster)
python -m tools.codegraph_mapper.cgm.cli ^
  --root L:\AIOS ^
  --out L:\AIOS\_maps ^
  --no-dry-run ^
  --no-dot ^
  --no-mermaid
```

### Allow Large Graphs

```powershell
# Disable 250k edge circuit breaker
python -m tools.codegraph_mapper.cgm.cli ^
  --root L:\AIOS ^
  --out L:\AIOS\_maps ^
  --no-dry-run ^
  --allow-large
```

## Output Structure

```
L:\AIOS\_maps\<YYYYMMDD_HHMMSS_runid>\
├─ graph\
│  ├─ code_graph.json         ← Complete graph (nodes + edges)
│  ├─ nodes.json              ← All nodes
│  ├─ edges.json              ← All edges
│  ├─ symbol_index.json       ← Qualname -> symbol lookup
│  ├─ call_index.json         ← File -> call relationships
│  ├─ file_index.json         ← File inventory with hashes
│  ├─ import_matrix.csv       ← Module import matrix
│  ├─ edges.csv               ← Edge list (CSV)
│  ├─ code_graph.dot          ← Graphviz DOT (optional)
│  └─ code_graph.mmd          ← Mermaid diagram (optional)
├─ reports\
│  ├─ summary.md              ← Human-readable summary
│  └─ summary.html            ← Interactive HTML report
├─ plan.json                  ← Shadow plan (actual run) or plan (dry-run)
└─ provenance.json            ← Run metadata + integrity hashes
```

## Safety Guarantees

### Read-Only by Default
- ✅ Only reads from `L:\AIOS\**`
- ✅ Only writes to `L:\AIOS\_maps\**`
- ✅ No code execution, no dynamic imports
- ✅ No network access
- ✅ No subprocess spawning

### Law Enforcement
- ✅ **Entry gate:** Validates paths before scanning
- ✅ **Pre-commit gate:** Validates all writes before committing
- ✅ **SCP-001 laws:** Origin lock, containment, oblivion
- ✅ **Manifest-driven:** All capabilities declared in `tool.manifest.yaml`

### Budget & Rate Limits
- ✅ CPU budget: 180s (3 minutes) default
- ✅ Max open files: 512 concurrent
- ✅ Rate limit: 200 ops/minute
- ✅ Circuit breaker: Aborts on >250k edges (override with `--allow-large`)

### Logging & Provenance
- ✅ Append-only JSONL: `L:\AIOS\logs\tools\codegraph-mapper.jsonl`
- ✅ Provenance tracking: Tool version, law hash, manifest hash, code hash
- ✅ Deterministic output: Same repo -> same graph

## Programmatic Usage

```python
from tools.codegraph_mapper.cgm.runner import run_map, CGMParams

params = CGMParams(
    root="L:\\AIOS",
    out_base="L:\\AIOS\\_maps",
    include=["**/*.py"],
    exclude=["**/__pycache__/**"],
    dry_run=False,
    require_approval=False,
    allow_large=False
)

result = run_map(params)

if result.ok:
    print(f"✅ Success! Artifacts: {len(result.artifacts)}")
    print(f"   Nodes: {result.metrics['nodes']}")
    print(f"   Edges: {result.metrics['edges']}")
else:
    print(f"❌ Failed: {result.error}")
    sys.exit(result.exit_code)
```

## Querying the Graph

### Using jq (JSON queries)

```powershell
# Find all classes
jq '.nodes[] | select(.kind=="class")' L:\AIOS\_maps\<run>\graph\code_graph.json

# Find modules importing carma_core
jq '.edges[] | select(.dst | contains("carma_core"))' L:\AIOS\_maps\<run>\graph\edges.json

# Count functions per module
jq '[.nodes[] | select(.kind=="function")] | group_by(.qualname | split(".")[0]) | map({module: .[0].qualname | split(".")[0], count: length})' L:\AIOS\_maps\<run>\graph\nodes.json
```

### Using Python

```python
import json

# Load graph
with open("L:\\AIOS\\_maps\\<run>\\graph\\code_graph.json") as f:
    graph = json.load(f)

# Find all orphan modules
module_nodes = {n['qualname'] for n in graph['nodes'] if n['kind'] == 'module'}
connected = {e['src'].split(':')[1] for e in graph['edges']} | {e['dst'].split(':')[1] for e in graph['edges']}
orphans = module_nodes - connected
print(f"Orphan modules: {orphans}")

# Find hottest modules (most imports)
from collections import Counter
imports = Counter(e['dst'].split(':')[1] for e in graph['edges'] if e['type'] in ['import', 'from_import'])
print(f"Top 10 imports: {imports.most_common(10)}")
```

## Integration with Luna

Luna can use CGM to understand AIOS architecture:

```python
# Luna autonomous mode can query graph
from tools.codegraph_mapper.cgm.runner import run_map, CGMParams

# Generate map
params = CGMParams(root="L:\\AIOS", out_base="L:\\AIOS\\_maps", dry_run=False)
result = run_map(params)

# Load and query
import json
with open(result.provenance_path.parent / "graph" / "symbol_index.json") as f:
    symbols = json.load(f)

# Luna can now answer: "Where is ConsciousnessCore defined?"
for qual, info in symbols.items():
    if "ConsciousnessCore" in qual:
        print(f"Found at: {info['file']}:{info['span'][0]}")
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Law violation (entry or pre-commit) |
| 3 | Budget exceeded |
| 4 | Circuit breaker (output explosion) |
| 5 | Approval timeout |
| 6 | Invalid parameters |

## Troubleshooting

### "Law violation: Output path outside L:\AIOS\_maps"

**Fix:** Use `--out L:\AIOS\_maps` (not `--out C:\temp`)

### "Circuit breaker: too many edges"

**Fix:** Add `--allow-large` flag or scan a subdirectory instead of full AIOS

### "Budget exceeded"

**Fix:** Increase budget with `--budget-ms 300000` or scan smaller directory

### "Parse failures" in summary

**Normal:** Some files may have encoding issues or syntax errors - they're logged and skipped

## Performance

**Typical AIOS scan (~10k Python files):**
- Duration: 2-3 minutes
- Memory: ~500MB peak
- Output size: ~50MB (JSON + CSV)
- Log size: ~2MB JSONL

**Scaling:**
- Handles repos up to ~50k Python files
- Uses chunked hashing (constant memory)
- Streams large outputs where possible

## Files Changed

CGM is **read-only** except for its own output directory. Directory hash comparison will show:
- ✅ Changed: Only `L:\AIOS\_maps\<run>\**` and `L:\AIOS\logs\tools\codegraph-mapper.jsonl`
- ✅ Unchanged: Everything else in AIOS

## License

Part of AIOS - follows AIOS license terms.

## Support

- **Logs:** `L:\AIOS\logs\tools\codegraph-mapper.jsonl`
- **Issues:** Check provenance.json for run details
- **Questions:** See AIOS manual section on development tools

