# RID: RLE-LTP-RSR Stability Framework

Framework implemented from **all PDFs** in this folder.

## How to make sure RID works

Run from **`l:\Steel_Brain`** (so the `RID` package is on the path). Use the project venv if you have one: `\.venv\Scripts\python.exe` or activate it first.

| Step | Command | What it does |
|------|---------|--------------|
| **1. Validate** | `python -m RID --check` | Imports all modules, checks equations, runs a 2-step FIDF loop. One command to confirm RID works. |
| **2. Unit tests** | `python -m pytest RID/tests/ -v` | 20 pytest tests (axioms, triangle, thermodynamics, SEOL, diagnostic, etc.). |
| **3. Demo** | `python -m RID --demo` | Prints axioms, RLE/LTP/RSR/S_n, rate normalization, diagnostic logic. |
| **4. Version** | `python -m RID --version` | Prints version line. |

**Minimal “did it work?” check:**

```bash
cd l:\Steel_Brain
python -m RID --check
```

You should see: `[OK] RID validation passed: imports, equations, FIDF loop (2 steps).`

**Testing RID on a real-world application:** see **`REAL_WORLD_TESTING.md`** and run **`python -m RID.examples.real_world_example`** for a full mapping and a 5-step pipeline example.

**Full verification (all checks + report):** from project root run **`python RID/run_all_verification.py`**. Writes `RID/verification_report.json` and `.txt`. Exit 0 only if all pass.

**Documentation for publication or review:** see **`ACCOMPLISHMENTS_AND_PROOFS.md`** (generic accomplishments and proofs), **`RID_FRAMEWORK_PAPER.md`** (paper-style document), and **`REPRODUCIBILITY.md`** (exact reproduction steps). Run **`python RID/verify_accomplishments_doc.py`** to verify the doc against the implementation, and **`python RID/check_artifact_completeness.py`** to confirm all required artifacts are present.

---

## PDFs (9 total)

- RLE_Axioms_Law_of_Compressed_State_Dynamics.pdf  
- RLE-LTP-RSR_Stability_Equation_Canonical_Spec.pdf  
- (V2) The Layer Transition Principle (LTP).pdf  
- Bridge Document – From Experimental RLE to Mathematical RLE.pdf  
- Equation.pdf  
- Fourth Invariant Dimensionless Framework (FIDF).pdf  
- Recursive State Reconstruction (RSR) as a universal system law.pdf  
- RLE–LTP Framework.pdf  
- the SEOL (System Efficiency Operations Layer) framework.pdf  

## Extracting PDF text

```bash
python -m RID --extract-pdf
```

Output: `RID/extracted_text/*.txt` (one file per PDF). Requires `pypdf` (in requirements.txt).

## Package layout

- **axioms** – RLE core, five axioms, law statement  
- **triangle** – LTP_n, RSR_n, S_n, rate normalization, diagnostic loop, interface_efficiency_rsr  
- **ltp_principle** – Descent triggers, compression baseline, phase transition, canonical statement  
- **thermodynamics** – Carnot (Lambda_min, eta_max), Lambda_mismatch, coupling_amplified_loss  
- **fidf** – Layers 0–3, run_fidf_loop  
- **seol** – Operational protocol, voltage law, interface_efficiency  
- **discrepancy** – D(·,·) for RSR (L1, L2, [0,1])

---

## Optional next steps (RID only)

- **FIDF duration**: Add `duration_sec` to `FIDFConfig` so the loop can exit when `step * dt >= duration_sec` (see `COMPLETENESS_EXAMPLES.md`).
