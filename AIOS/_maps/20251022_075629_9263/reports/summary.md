# AIOS CodeGraph Summary

**Generated:** 2025-10-22T07:56:37.453816+00:00
**Run ID:** 20251022_075629_9263
**Tool Version:** 1.0.0

---

## Overall Statistics

- **Total Files:** 1729
- **Python Files:** 1722
- **Modules:** 1729
- **Total Nodes:** 9170
- **Total Edges:** 78950
- **Parse Failures:** 7

## Top 20 Most Imported Modules

| Rank | Module | Import Count |
|------|--------|-------------|
| 1 | `pathlib` | 1615 |
| 2 | `sys` | 1568 |
| 3 | `utils.unicode_safe_output` | 1263 |
| 4 | `streamlit` | 847 |
| 5 | `typing` | 537 |
| 6 | `__future__` | 403 |
| 7 | `os` | 233 |
| 8 | `json` | 225 |
| 9 | `pandas` | 213 |
| 10 | `pytest` | 203 |
| 11 | `playwright.sync_api` | 202 |
| 12 | `datetime` | 191 |
| 13 | `re` | 178 |
| 14 | `time` | 174 |
| 15 | `streamlit.errors` | 174 |
| 16 | `e2e_playwright.conftest` | 158 |
| 17 | `numpy` | 150 |
| 18 | `e2e_playwright.shared.app_utils` | 134 |
| 19 | `unittest` | 122 |
| 20 | `unittest.mock` | 105 |

## Orphan Modules

Found 28 modules with no imports (in or out):

- `consciousness_core`
- `consciousness_core.biological.anchor`
- `consciousness_core.biological.body`
- `consciousness_core.biological.brain`
- `consciousness_core.biological.ears`
- `consciousness_core.biological.eyes`
- `consciousness_core.biological.hands`
- `consciousness_core.biological.mouth`
- `consciousness_core.biological.nerves`
- `consciousness_core.biological.shield`
- `consciousness_core.biological.skin`
- `consciousness_core.biological.soul`
- `consciousness_core.biological.spine`
- `data_core`
- `enterprise_core`
- `infra_core`
- `luna_core.prompts`
- `luna_core.systems`
- `luna_core.utilities`
- `python.Tools.scripts.make_ctype`

... and 8 more

## Hotspot Modules (Highest Degree)

| Rank | Module | In-Degree | Out-Degree | Total |
|------|--------|-----------|------------|-------|
| 1 | `pathlib` | 1615 | 0 | 1615 |
| 2 | `sys` | 1568 | 0 | 1568 |
| 3 | `utils.unicode_safe_output` | 1263 | 0 | 1263 |
| 4 | `streamlit` | 847 | 0 | 847 |
| 5 | `typing` | 537 | 0 | 537 |
| 6 | `__future__` | 403 | 0 | 403 |
| 7 | `os` | 233 | 0 | 233 |
| 8 | `json` | 225 | 0 | 225 |
| 9 | `pandas` | 213 | 0 | 213 |
| 10 | `pytest` | 203 | 0 | 203 |
| 11 | `playwright.sync_api` | 202 | 0 | 202 |
| 12 | `datetime` | 191 | 0 | 191 |
| 13 | `re` | 178 | 0 | 178 |
| 14 | `streamlit.errors` | 174 | 0 | 174 |
| 15 | `time` | 174 | 0 | 174 |
| 16 | `e2e_playwright.conftest` | 158 | 0 | 158 |
| 17 | `numpy` | 150 | 0 | 150 |
| 18 | `e2e_playwright.shared.app_utils` | 134 | 0 | 134 |
| 19 | `unittest` | 122 | 0 | 122 |
| 20 | `unittest.mock` | 105 | 0 | 105 |

## Largest Python Files

| Rank | File | Size (KB) |
|------|------|----------|
| 1 | `luna_core\core\response_generator.py` | 162.5 |
| 2 | `main_core\main_core_windows.py` | 129.3 |
| 3 | `streamlit_core\streamlit_main\lib\tests\streamlit\elements\vega_charts_test.py` | 111.4 |
| 4 | `streamlit_core\streamlit_main\lib\streamlit\elements\lib\column_types.py` | 96.5 |
| 5 | `streamlit_core\streamlit_main\lib\streamlit\elements\vega_charts.py` | 95.0 |
| 6 | `streamlit_core\streamlit_main\lib\tests\streamlit\config_test.py` | 92.6 |
| 7 | `streamlit_core\streamlit_main\lib\streamlit\vendor\pympler\asizeof.py` | 89.0 |
| 8 | `streamlit_core\streamlit_main\lib\tests\streamlit\runtime\app_session_test.py` | 80.3 |
| 9 | `streamlit_core\streamlit_main\lib\streamlit\emojis.py` | 79.7 |
| 10 | `streamlit_core\streamlit_main\lib\streamlit\config.py` | 78.1 |
| 11 | `python\Tools\scripts\texi2html.py` | 70.7 |
| 12 | `streamlit_core\streamlit_main\lib\streamlit\material_icon_names.py` | 66.8 |
| 13 | `streamlit_core\streamlit_main\lib\streamlit\testing\v1\element_tree.py` | 64.7 |
| 14 | `enterprise_core\enterprise_core.py` | 59.4 |
| 15 | `luna_core\systems\luna_arbiter_system.py` | 53.6 |
| 16 | `support_core\extra\gui\streamlit_app.py` | 53.2 |
| 17 | `streamlit_core\streamlit_app.py` | 50.5 |
| 18 | `streamlit_core\streamlit_main\lib\tests\streamlit\runtime\scriptrunner\script_runner_test.py` | 49.9 |
| 19 | `streamlit_core\streamlit_main\lib\streamlit\dataframe_util.py` | 49.4 |
| 20 | `carma_core\core\fractal_cache.py` | 49.4 |

## Integrity Metrics

- **Total Imports:** 13531
- **Unresolved Imports:** 13162
- **Resolution Rate:** 2.7%

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

