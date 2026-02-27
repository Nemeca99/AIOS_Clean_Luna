# RID: A Dimensionless Stability Framework from RLE–LTP–RSR

**Paper-style document for submission or presentation.**  
No identifying information. All claims are backed by implemented code and verification scripts.

---

## Abstract

We present **RID** (RLE–LTP–RSR), a dimensionless stability framework for recursive and resource-constrained systems. RID combines three legs—Recursive Load Efficiency (RLE), Layer Transition Principle (LTP), and Recursive State Reconstruction (RSR)—into a single stability scalar S_n and supports multi-step analysis via the Fourth Invariant Dimensionless Framework (FIDF) and an operational voltage law (SEOL). The framework is fully implemented from nine source specifications, with automated validation, unit tests, and a document-consistency verifier. We apply it to a generic extrusion heater process where repeated failures occurred; RID indicates the loss/stress path (RLE) rather than electrical overload (LTP) or control instability (RSR), consistent with physical failure modes and mitigations. Reproducibility is ensured by a single master verification script, step-by-step instructions, and an artifact-completeness checker. This document is self-contained and suitable for review or publication.

**Keywords:** stability framework, recursive systems, RLE, LTP, RSR, dimensionless analysis, FIDF, SEOL, extrusion, verification, reproducibility.

---

## 1. Introduction

### 1.1 Motivation

Recursive and resource-constrained systems (control loops, thermal processes, capacity-limited services) need a compact way to decide whether observed behavior is stable and where to act when it is not. Ad hoc metrics often mix units and scales; a **dimensionless** framework allows comparison across domains and clear diagnostic actions.

### 1.2 Contribution

- **RID framework:** A triple-leg stability model (RLE, LTP, RSR) and composite scalar S_n, with thermodynamics, multi-step FIDF loop, and SEOL voltage law, fully implemented from nine PDF specifications.
- **Verification:** Single-command validation, 20 unit tests, and a 16-check document verifier that ensures the written claims match the code. A master script runs all checks and writes a timestamped report.
- **Application:** Mapping and analysis of a generic extrusion heater process (temperature control, SSRs, heater failures). RID identifies the limiting leg (loss/stress) and supports physical interpretation and mitigations.
- **Reproducibility:** Exact commands, expected outputs, and an artifact-completeness script so that any reviewer can reproduce the results.

### 1.3 Scope

This document and the associated code cover the **PDF-derived** RID framework only. A separate thermal/computational RLE line of work (hardware monitoring, red-team gauntlet) exists in the same repository and is referenced as complementary.

---

## 2. Framework

### 2.1 Source

The framework is derived from nine specification documents (PDFs):

1. RLE Axioms – Law of Compressed State Dynamics  
2. RLE–LTP–RSR Stability Equation Canonical Spec  
3. (V2) The Layer Transition Principle (LTP)  
4. Bridge Document – From Experimental RLE to Mathematical RLE  
5. Equation  
6. Fourth Invariant Dimensionless Framework (FIDF)  
7. Recursive State Reconstruction (RSR) as a universal system law  
8. RLE–LTP Framework  
9. The SEOL (System Efficiency Operations Layer) framework  

Text can be extracted from the PDFs via `python -m RID --extract-pdf` for search and reference.

### 2.2 Three legs and stability scalar

- **RLE_n** (Recursive Load Efficiency): Retained usable fraction across a step.  
  **Formula:** RLE_n = (E_next − U_n) / E_n  
  with E_n = capacity before, U_n = loss during step, E_next = capacity after. All positive; E_n > 0.

- **LTP_n** (Layer Transition Principle): Structure vs demand.  
  **Formula:** LTP_n = min(1, n_n / d_n)  
  with n_n = structural support (capacity), d_n = demand. Both positive; d_n > 0.

- **RSR_n** (Recursive State Reconstruction): Fidelity of the system’s estimate to the observable.  
  **Formula:** RSR_n = 1 − D(y_n, reconstruction)  
  with D a discrepancy in [0,1]. Default for scalars in [0,1]: D(y, r) = |y − r|, so RSR_n = 1 − |y_n − reconstruction|.

- **S_n** (stability scalar):  
  **Formula:** S_n = RSR_n × LTP_n × RLE_n  
  S_n = 1 indicates no stress; S_n < 1 indicates which leg is limiting.

### 2.3 Additional elements

- **Thermodynamics:** Carnot bound (lambda_min, eta_max), lambda_mismatch, coupling_amplified_loss, temporal_mismatch_condition, cost_depth_factorial (from the specs).
- **FIDF:** Multi-step loop with configurable dt and max_steps; four callbacks supply observable, reconstruction, (n_n, d_n), and (E_n, U_n, E_next) per step.
- **SEOL voltage law:** Efficiency cannot exceed input LTP. Implemented as effective_system_efficiency(S_n, LTP_input) = min(S_n, LTP_input) and voltage_law_violated(S_n, LTP_input) ⟺ S_n > LTP_input.
- **Diagnostics:** Per-step action (continue, check_ltp, mandatory_descent, intervene_rle, check_rsr) from the triangle state; exact thresholds are in the codebase.

---

## 3. Implementation and Verification

### 3.1 Code layout

Package `RID`: axioms, triangle (LTP, RSR, S_n, diagnostic_step), ltp_principle, thermodynamics, fidf, seol, discrepancy. CLI: `python -m RID --check | --demo | --extract-pdf | --version`.

### 3.2 Validation pipeline

| Check | Command | Criterion |
|-------|---------|-----------|
| RID check | `python -m RID --check` | Imports, equation checks, 2-step FIDF complete; output contains “[OK] RID validation passed”. |
| Unit tests | `python -m pytest RID/tests/ -v` | All tests pass (≈20). |
| Doc verifier | `python RID/verify_accomplishments_doc.py` | 16 checks PASS; “No contradictions found”. |
| Example | `python -m RID.examples.real_world_example` | Runs without error; prints S_n and actions. |

### 3.3 Master verification script

Running `python RID/run_all_verification.py` from the project root executes the four steps above and writes:

- `RID/verification_report.json` (timestamp, Python version, per-step pass/fail),
- `RID/verification_report.txt` (short summary).

Exit code 0 only if all steps pass. This is the single entry point for “proof” verification.

### 3.4 Document–code consistency

The document *ACCOMPLISHMENTS_AND_PROOFS.md* includes an appendix with canonical formulas, the extrusion RLE proxy, and numerical examples. The script `verify_accomplishments_doc.py` recomputes these from the RID package and asserts agreement. Thus the written claims and the implementation are kept in sync and machine-checkable.

---

## 4. Application: Extrusion Heater Process

### 4.1 Context

Generic extrusion process: heated die, temperature control, setpoint on the order of 400–420°F, melt slightly above setpoint, heater demand on the order of tens of amperes, solid-state relays. Multiple heater failures (burnouts); cause unknown (overload, control instability, or loss/stress).

### 4.2 RID mapping

- **RSR:** y_n = actual melt temp (normalized 0–1), reconstruction = setpoint (normalized).  
- **LTP:** n_n = total SSR capacity (A), d_n = total heater demand (A) or demand_01 × max amps.  
- **RLE:** Proxy: E_n = 100, U_n = demand (%), E_next = 100 − U_n; RLE_n = (E_next − U_n)/E_n.

One demand scalar in [0,1] is used for both LTP and RLE proxy. Inputs: time, setpoint, actual temp, heater % (or demand_01); optional pressure.

### 4.3 Analysis and results

A script reads a CSV (or synthetic data), computes per-step RSR, LTP, RLE, S_n, and worst leg; optionally sweeps demand and compares two SSR configurations.

**Results (synthetic/sweep):**

- LTP = 1 for nominal demand (e.g. 75 A) vs both 90 A and 80 A capacity ⇒ electrical overload not indicated.
- RSR high (e.g. ~0.95 for 415 vs 420°F) ⇒ control thrashing not indicated.
- RLE was the worst leg and decreased as demand increased ⇒ triangle points to **loss/stress** path.

Physical failure modes (lead tension, melt on/near leads, cartridge near die edge) align with loss and stress; mitigations (lead protection, 90° clip, split-sheath, reduce melt at source) are documented. **Recommended next step:** Log real controller data and re-run the script to confirm RLE/S_n on process data.

---

## 5. Reproducibility

- **Environment:** Python 3.10+; dependencies: pypdf, pytest (and any project requirements.txt).
- **Full verification:** From project root: `python RID/run_all_verification.py`. Expect four [PASS] and exit 0.
- **Step-by-step:** See `REPRODUCIBILITY.md` for each command and expected output.
- **Artifact completeness:** `python RID/check_artifact_completeness.py` checks presence of required PDFs, modules, docs, and scripts; exit 0 if complete.

---

## 6. Limitations

- **Extrusion case:** Conclusions are from synthetic/proxy data and a demand sweep; confirmation on real logged data is recommended.
- **Diagnostic thresholds:** The exact rules for diagnostic actions are in code, not fully written in this document.
- **Thermal RLE:** A different (thermal/computational) RLE formulation and red-team gauntlet exist in the same repo; they are complementary, not a replacement for the PDF-derived RID.

---

## 7. References

1. RLE Axioms – Law of Compressed State Dynamics (PDF, in RID folder).  
2. RLE–LTP–RSR Stability Equation Canonical Spec (PDF).  
3. (V2) The Layer Transition Principle (LTP) (PDF).  
4. Bridge Document – From Experimental RLE to Mathematical RLE (PDF).  
5. Equation (PDF).  
6. Fourth Invariant Dimensionless Framework (FIDF) (PDF).  
7. Recursive State Reconstruction (RSR) as a universal system law (PDF).  
8. RLE–LTP Framework (PDF).  
9. The SEOL (System Efficiency Operations Layer) framework (PDF).

---

## Data and Code Availability

- **Code:** RID package, tests, examples, and verification scripts are in the project repository under the `RID` directory.
- **Specifications:** Nine PDFs in the same directory; extracted text via `python -m RID --extract-pdf`.
- **Verification reports:** Generated by `python RID/run_all_verification.py` (JSON and TXT in `RID/`).
- **Documentation:** README.md, REAL_WORLD_TESTING.md, ACCOMPLISHMENTS_AND_PROOFS.md, REPRODUCIBILITY.md, ORIGINAL_RLE_INDEX.md (for the separate RLE line of work).

---

*This document is written in generic terms with no identifying information. It is intended for submission, presentation, or review.*
