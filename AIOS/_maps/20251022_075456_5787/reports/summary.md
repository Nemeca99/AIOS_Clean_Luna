# AIOS CodeGraph Summary

**Generated:** 2025-10-22T07:54:56.617233+00:00
**Run ID:** 20251022_075456_5787
**Tool Version:** 1.0.0

---

## Overall Statistics

- **Total Files:** 21
- **Python Files:** 21
- **Modules:** 21
- **Total Nodes:** 72
- **Total Edges:** 708
- **Parse Failures:** 0

## Top 20 Most Imported Modules

| Rank | Module | Import Count |
|------|--------|-------------|
| 1 | `typing` | 17 |
| 2 | `pathlib` | 15 |
| 3 | `ast` | 5 |
| 4 | `collections` | 5 |
| 5 | `json` | 5 |
| 6 | `hashlib` | 4 |
| 7 | `datetime` | 3 |
| 8 | `sys` | 2 |
| 9 | `time` | 2 |
| 10 | `argparse` | 1 |
| 11 | `cgm.runner` | 1 |
| 12 | `csv` | 1 |
| 13 | `os` | 1 |
| 14 | `fnmatch` | 1 |
| 15 | `cgm.py_ast` | 1 |
| 16 | `cgm.imports` | 1 |
| 17 | `cgm.symbols` | 1 |
| 18 | `cgm.callgraph` | 1 |
| 19 | `cgm.xref` | 1 |
| 20 | `yaml` | 1 |

## Orphan Modules

Found 1 modules with no imports (in or out):

- `cgm`

## Hotspot Modules (Highest Degree)

| Rank | Module | In-Degree | Out-Degree | Total |
|------|--------|-----------|------------|-------|
| 1 | `cgm.runner` | 1 | 18 | 19 |
| 2 | `typing` | 17 | 0 | 17 |
| 3 | `pathlib` | 15 | 0 | 15 |
| 4 | `cgm.graph_build` | 1 | 7 | 8 |
| 5 | `cgm.fs_walk` | 1 | 6 | 7 |
| 6 | `cgm.emit_csv` | 1 | 5 | 6 |
| 7 | `cgm.logging_util` | 1 | 5 | 6 |
| 8 | `collections` | 5 | 0 | 5 |
| 9 | `cgm.py_ast` | 1 | 4 | 5 |
| 10 | `ast` | 5 | 0 | 5 |
| 11 | `tests.test_smoke` | 0 | 5 | 5 |
| 12 | `cgm.manifest` | 1 | 4 | 5 |
| 13 | `cgm.cli` | 1 | 4 | 5 |
| 14 | `json` | 5 | 0 | 5 |
| 15 | `cgm.emit_mermaid` | 1 | 3 | 4 |
| 16 | `hashlib` | 4 | 0 | 4 |
| 17 | `cgm.report_html` | 1 | 3 | 4 |
| 18 | `cgm.report_md` | 1 | 3 | 4 |
| 19 | `cgm.emit_json` | 1 | 3 | 4 |
| 20 | `cgm.laws_gate` | 1 | 3 | 4 |

## Largest Python Files

| Rank | File | Size (KB) |
|------|------|----------|
| 1 | `cgm\runner.py` | 12.0 |
| 2 | `cgm\report_html.py` | 7.4 |
| 3 | `cgm\report_md.py` | 7.3 |
| 4 | `cgm\graph_build.py` | 6.7 |
| 5 | `cgm\fs_walk.py` | 5.3 |
| 6 | `cgm\emit_dot.py` | 4.9 |
| 7 | `cgm\symbols.py` | 4.5 |
| 8 | `cgm\cli.py` | 4.1 |
| 9 | `cgm\emit_mermaid.py` | 3.5 |
| 10 | `tests\test_smoke.py` | 3.1 |
| 11 | `cgm\emit_csv.py` | 3.0 |
| 12 | `cgm\laws_gate.py` | 2.9 |
| 13 | `cgm\py_ast.py` | 2.9 |
| 14 | `cgm\callgraph.py` | 2.8 |
| 15 | `cgm\imports.py` | 2.7 |
| 16 | `cgm\emit_json.py` | 2.6 |
| 17 | `cgm\xref.py` | 2.2 |
| 18 | `cgm\logging_util.py` | 1.5 |
| 19 | `cgm\manifest.py` | 1.3 |
| 20 | `cgm\__init__.py` | 0.2 |

## Integrity Metrics

- **Total Imports:** 85
- **Unresolved Imports:** 67
- **Resolution Rate:** 21.2%

---

## Generated Artifacts

- `graph/code_graph.json` - Complete graph (nodes + edges)
- `graph/nodes.json` - All nodes
- `graph/edges.json` - All edges
- `graph/symbol_index.json` - Symbol lookup index
- `graph/call_index.json` - Call graph per file
- `graph/file_index.json` - File inventory
- `graph/import_matrix.csv` - Module import matrix
- `graph/edges.csv` - Edge list
- `graph/code_graph.dot` - Graphviz DOT
- `graph/code_graph.mmd` - Mermaid diagram
- `provenance.json` - Run metadata

