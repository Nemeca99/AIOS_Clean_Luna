# Your original RLE work and how it fits with RID

This index summarizes what lives under **`RID/RLE/`** (your original work, tests, and docs) and how it relates to the **RID** framework built from the PDFs in `RID/`.

---

## Two “RLE” layers

| Layer | Location | What it is |
|-------|----------|------------|
| **RID (PDF framework)** | `RID/` (this package) | RLE–LTP–RSR stability triangle from the 9 PDFs: **RLE_n** = (E_{n+1} − U_n)/E_n, **LTP_n** = min(1, n_n/d_n), **RSR_n** = 1−D(y_n, n_n), **S_n** = RSR·LTP·RLE. Dimensionless, resource-agnostic. Used for extrusion analysis, validation script, FIDF, SEOL. |
| **Original RLE (lab + V2)** | `RID/RLE/` | Your thermal/computational RLE: formula with **η, σ, α, τ** (util, stability, a_load, t_sustain); collapse detection; hardware monitoring; Break-RLE Gauntlet; Miner’s Law; consciousness-switching experiments. |

They are **complementary**: the PDF RID is the abstract stability framework; your RLE is an applied, thermal/computational instantiation with real hardware and stress tests.

---

## Structure of `RID/RLE/` (your original work)

### Lab – monitoring and experiments

- **`lab/`** – Main monitoring lab: daemons, analysis, stress generators, session data (CSVs, screenshots).
- **`lab/docs/`**
  - **THERMAL_COGNITIVE_COUPLING.md** – RLE as a “consciousness switch” for dual-brain (CPU/GPU) thermal management; 45/55 balance, 0.448 system RLE; thermal-cognitive coupling.
  - **MINERS_LAW_EXPERIMENTAL_VALIDATION.md** – Validation of Miner’s Law (speed = thermal change rate, 50/50 hot/cold balance); RLE oscillator as Q-Cache router; hardware: i7-11700F + RTX 3060 Ti.
  - **RLE_CONSCIOUSNESS_SWITCHING.md** – Switching logic driven by RLE/thermal state.
- **`rle_core.py`** – Canonical engine: (η, σ, α, τ) → RLE, E_th, E_pw; collapse detection; CSV CLI; optional micro-scale correction (Planck-ish penalty).
- **`hardware_monitor.py`**, **`start_monitor.py`**, **LibreHardwareMonitor** – Hardware monitoring (CPU/GPU temp, power, utilization).
- **Streamlit/Pygame** – Live SCADA-style dashboards, stress tests, session replay.

### V2 – Break-RLE Gauntlet and validation

- **`V2/`**
  - **`scripts/break_rle_gauntlet.py`** – Red-team suite: **17 adversarial stress tests** (timebase chaos, autocorr starvation, sensor desync, quantization, governor resonance, phase-change topology flip, adversarial resample, heavy-tailed noise, regenerative paradox, extreme domain cryo/furnace). **9 trip-wires** (boundedness, NaN/Inf, clock stability, etc.).
  - **`validation_output/`** – Per-test artifacts: `*_attack.csv`, `*_timeseries.png`, `diagnostics.json`, `meta.json`; **BASELINE** plus 10 attack classes.
  - **`GAUNTLET_SUMMARY.md`**, **`REPRODUCIBILITY_METHODS.md`**, **`README_GAUNTLET.md`** – How to run, interpret, and reproduce.
  - **`break_rle_gauntlet_results.json`** – Full results (all 17 PASS); environment and seed for reproducibility.
- **Makefile** – e.g. `make gauntlet` to run the gauntlet.
- **Reproducibility** – Seeded runs; real-hardware workflow (load session CSV, apply attacks) documented in README_GAUNTLET.

### Final Proof / Codex

- **`Final Proof/Collection/Codex/`**
  - **RIS Volume 0 – Section 6: Recursive Thermodynamics** – Conceptual layer: “Heat is time, cooling is intelligence”; power/heat/time entanglement; RIS cooling principle (over-isolate, don’t overclock); workload split and heat distribution.

### Other

- **Magic/** – Separate project (magic squares), not RLE core.
- **`.github/workflows/gauntlet.yml`** – CI for gauntlet (if enabled).
- **AGENTS.md**, **CLAUDE.md**, **CREDITS.md**, **REPRODUCE.md**, **requirements.txt**, **requirements_lab.txt** – Project and reproducibility metadata.

---

## How to run your original tests and docs

| What | Where | Command / action |
|------|--------|-------------------|
| **Break-RLE Gauntlet** | `RID/RLE/V2/` | `py -3 scripts/break_rle_gauntlet.py` or `make gauntlet` from V2. Reproducible: `run_gauntlet(seed=42)`. |
| **Gauntlet results** | `RID/RLE/V2/validation_output/` | `break_rle_gauntlet_results.json`, `BREAK_RLE_GAUNTLET_REPORT.md`, per-test folders. |
| **Live monitoring** | `RID/RLE/lab/` | `RUN_RLE.bat` or `cd lab/monitoring && streamlit run scada_dashboard_live.py`. |
| **RLE core (CSV)** | `RID/RLE/` | `python rle_core.py --in sessions/recent/rle_*.csv --out out.csv`. |
| **Docs** | `RID/RLE/lab/docs/`, `RID/RLE/V2/` | Read THERMAL_COGNITIVE_COUPLING, MINERS_LAW, GAUNTLET_SUMMARY, REPRODUCIBILITY_METHODS. |

---

## Relation to the RID package (parent folder)

- **RID** (from PDFs) gives: axioms, RLE_n, LTP_n, RSR_n, S_n, FIDF, SEOL, thermodynamics, diagnostics. It does **not** implement your thermal formula (η, σ, α, τ) or the gauntlet.
- **Your RLE** implements that thermal formula, hardware monitoring, and the 17-test gauntlet. It is the **applied** side; RID (PDF) is the **abstract** stability framework.
- **Extrusion work** (in `RID/examples/`) uses the **PDF RID** (RLE/LTP/RSR triangle, demand_01, S_n) for process interpretation, not the lab’s rle_core.py.

If you later want a **single** pipeline that uses both, options include: (1) feeding lab session CSVs into the PDF RID (e.g. as y_n, recon, n_n, d_n, E, U, E_next) for S_n and diagnostics; or (2) using your rle_core.py output as one input channel (e.g. “reconstruction” or “demand”) into the triangle. The index above is enough to navigate and run your original work and to see how it fits with RID.
