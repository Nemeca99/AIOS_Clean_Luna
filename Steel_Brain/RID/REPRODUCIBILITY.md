# RID Framework: Reproducibility Instructions

This document gives exact steps to reproduce the RID implementation and verification. All commands are run from the **project root** (the directory that contains the `RID` package folder). On Windows the root might be `L:\Steel_Brain` or your clone path; on Unix, e.g. `~/Steel_Brain`.

---

## 1. Environment

- **Python:** 3.10 or 3.11 recommended (3.9+ may work).
- **Dependencies:** From project root, install with:
  ```bash
  pip install -r requirements.txt
  ```
  If the project has no root `requirements.txt`, install at least:
  ```bash
  pip install pypdf pytest
  ```
  (RID core uses only the standard library plus optional pypdf for PDF extraction and pytest for tests.)

---

## 2. One-command full verification

From project root run:

```bash
python RID/run_all_verification.py
```

**Expected:** All four steps report `[PASS]`, and the script exits with code 0. Two files are written:

- `RID/verification_report.json` — machine-readable report (timestamp, Python version, per-step pass/fail).
- `RID/verification_report.txt` — short human-readable summary.

If any step fails, the script prints the failing step and exits with code 1. Inspect the report files or the step output for details.

---

## 3. Step-by-step reproduction

You can run each verification step separately and compare with the expected outputs below.

### 3.1 RID package check

```bash
python -m RID --check
```

**Expected output (last line):**
```
[OK] RID validation passed: imports, equations, FIDF loop (2 steps).
```
**Exit code:** 0.

---

### 3.2 Unit tests

```bash
python -m pytest RID/tests/ -v
```

**Expected:** All tests pass (about 20 tests). Last lines should include something like:
```
RID/tests/test_rid.py::test_... PASSED
...
====== N passed in X.XXs ======
```
**Exit code:** 0.

---

### 3.3 Accomplishments document verification

```bash
python RID/verify_accomplishments_doc.py
```

**Expected:** Sixteen checks, each showing `[PASS]`. Final line:
```
No contradictions found; document and RID implementation are consistent.
```
**Exit code:** 0.

---

### 3.4 Real-world example

```bash
python -m RID.examples.real_world_example
```

**Expected:** Printed header and per-step lines with S_n, RSR, LTP, RLE, and diagnostic actions. Final line:
```
RID run complete. Use S_n < 1 or non-'continue' actions to trigger alerts or descent in your system.
```
**Exit code:** 0.

---

## 4. Optional: PDF text extraction

To extract text from the nine source PDFs (requires `pypdf`):

```bash
python -m RID --extract-pdf
```

**Expected:** Text files written under `RID/extracted_text/` (one per PDF). No strict exit-code requirement; useful for search and reference.

---

## 5. Optional: Extrusion analysis script

From project root or from `RID/examples`:

```bash
python RID/examples/extrusion_rid_analysis.py
```
or with sweep:
```bash
python RID/examples/extrusion_rid_analysis.py --sweep
```

**Expected:** Printed table of RSR, LTP, RLE, S_n and (with `--sweep`) a comparison table for two SSR configurations. Exit code 0.

---

## 6. Artifact completeness check

To verify that all required files for the “proof” artifact are present (PDFs, modules, docs, scripts):

```bash
python RID/check_artifact_completeness.py
```

**Expected:** All listed checks `[PASS]` and exit code 0. See that script’s docstring for what it checks.

---

## 7. Summary checklist

| Step | Command | Expected |
|------|---------|----------|
| Full verification | `python RID/run_all_verification.py` | 4× [PASS], exit 0 |
| RID check | `python -m RID --check` | `[OK] RID validation passed...` |
| Tests | `python -m pytest RID/tests/ -v` | N passed |
| Doc verification | `python RID/verify_accomplishments_doc.py` | 16 PASS, no contradictions |
| Example | `python -m RID.examples.real_world_example` | S_n lines, “RID run complete” |
| Completeness | `python RID/check_artifact_completeness.py` | All PASS |

---

*Document version: for use with RID framework accomplishments and verification report.*
