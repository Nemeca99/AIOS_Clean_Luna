# RID "Completeness" Options — What Each One Is (with examples)

These are **optional** additions. The spec is already fully implemented; these make RID easier to use or more robust.

---

## 1. FIDF "duration" (doc says: define duration + granularity)

**What the doc says:**  
"You must define the **duration** and the **granularity** (e.g., 'Measure a 10-year span at 1-minute intervals')."

**What we have now:**  
Only granularity (`dt`) and optional step limit (`max_steps`). No explicit "run for 10 years then stop."

```python
# CURRENT: you stop by step count or external_reset
config = FIDFConfig(dt=1.0, max_steps=100)  # stop after 100 steps
# If you want "10 years at 1-min intervals" you have to compute max_steps yourself:
# max_steps = 10 * 365 * 24 * 60  # 525600
```

**What the addition would be:**  
Add an optional `duration_sec` (or `duration_dt_units`). Loop exits when `step * dt >= duration`.

```python
# OPTION: config can carry duration; loop exits when "time expires"
@dataclass
class FIDFConfig:
    dt: float = 1.0
    max_steps: Optional[int] = None
    duration_sec: Optional[float] = None   # NEW: e.g. 10*365*24*3600 for 10 years

# In run_fidf_loop, add:
# if config.duration_sec is not None and (n * config.dt) >= config.duration_sec:
#     break
```

**Example use after adding:**

```python
# "Run for 1 hour at 1-second granularity"
config = FIDFConfig(dt=1.0, duration_sec=3600.0)
run_fidf_loop(config, get_observable, get_reconstruction, get_support_demand, get_capacity)
# Loop exits when n * 1.0 >= 3600, i.e. after 3600 steps
```

---

## 2. SEOL voltage law in code (efficiency cannot exceed Input LTP)

**What the doc says:**  
"Efficiency can never exceed the quality of the Input LTP. You cannot engineer your way out of a dirty source."

**What we have now:**  
Only the *text* of that law in `voltage_law_summary()`. No function that takes Input LTP and S_n and enforces the cap.

```python
# CURRENT: you can compute S_n yourself; nothing stops you from treating S_n > LTP_input as valid
S_n = stability_scalar(RSR_n, LTP_n, RLE_n)  # might be 0.95
LTP_input = 0.8   # "dirty source" — max possible is 0.8
# Doc says observed efficiency can't exceed 0.8, but we don't have a function for that
```

**What the addition would be:**  
A small helper that applies the voltage law: observed efficiency is capped by Input LTP.

```python
# OPTION: in seol.py

def effective_system_efficiency(S_n: float, LTP_input: float) -> float:
    """
    Voltage law: efficiency cannot exceed Input LTP (the source ceiling).
    Returns min(S_n, LTP_input) so you never report more than the source allows.
    """
    return min(S_n, max(0.0, min(1.0, LTP_input)))

def voltage_law_violated(S_n: float, LTP_input: float) -> bool:
    """True if raw S_n would exceed Input LTP (shouldn't happen in a lawful system)."""
    return S_n > LTP_input
```

**Example use after adding:**

```python
from RID import stability_scalar, effective_system_efficiency

RSR_n, LTP_n, RLE_n = 0.9, 0.95, 0.9
S_n_raw = stability_scalar(RSR_n, LTP_n, RLE_n)   # 0.7695
LTP_input = 0.8   # e.g. from your "inlet" or source

# Reported efficiency (capped by source)
S_reported = effective_system_efficiency(S_n_raw, LTP_input)  # 0.7695 (under 0.8, OK)
# If S_n_raw were 0.95, S_reported would be 0.8 (capped).
```

---

## 3. Unit tests

**What we have now:**  
No `test_*.py` in RID. If we change an equation, we don't have a single command to check we didn't break anything.

**What the addition would be:**  
A small test module that checks a few equations and known values.

**Example:** create `RID/tests/test_rid.py` (or `Steel_Brain/tests/test_rid.py`):

```python
# OPTION: RID/tests/test_rid.py

import pytest

# Run from Steel_Brain: python -m pytest RID/tests/ -v

def test_rle_n_basic():
    from RID import rle_n
    assert rle_n(E_next=95.0, U_n=5.0, E_n=100.0) == 0.9

def test_ltp_n_adequacy():
    from RID import ltp_n
    assert ltp_n(10.0, 10.0) == 1.0
    assert ltp_n(5.0, 10.0) == 0.5

def test_stability_scalar_unity():
    from RID import stability_scalar
    assert stability_scalar(1.0, 1.0, 1.0) == 1.0
    assert stability_scalar(0.5, 0.5, 0.5) == 0.125

def test_carnot_bound():
    from RID import lambda_min_carnot, eta_max_carnot
    assert lambda_min_carnot(300.0, 600.0) == 0.5
    assert eta_max_carnot(300.0, 600.0) == 0.5

def test_coupling_amplified_loss():
    from RID import coupling_amplified_loss
    # 1 - (1-0.1)*(1-0.1) = 1 - 0.81 = 0.19
    assert abs(coupling_amplified_loss([0.1, 0.1]) - 0.19) < 1e-9
```

**Example use after adding:**

```bash
cd l:\Steel_Brain
.venv\Scripts\activate
pip install pytest
python -m pytest RID/tests/ -v
```

---

## 4. CLI entry point (single command to run demo or extract PDFs)

**What we have now:**  
You run the demo or extractor as modules:

```bash
python -m RID.run_rid_demo
python -m RID.extract_pdf_text
```

**What the addition would be:**  
One entry point so you can run `python -m RID` and optionally pass flags.

**Example:** add `RID/__main__.py`:

```python
# OPTION: RID/__main__.py

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="RID: RLE-LTP-RSR Stability Framework")
    parser.add_argument("--demo", action="store_true", help="Run the RID demo")
    parser.add_argument("--extract-pdf", action="store_true", help="Extract text from all PDFs in RID folder")
    parser.add_argument("--version", action="store_true", help="Show version / doc source")
    args = parser.parse_args()

    if args.demo:
        from .run_rid_demo import main as demo_main
        demo_main()
    elif args.extract_pdf:
        from .extract_pdf_text import main as extract_main
        extract_main()
    elif args.version:
        print("RID: RLE-LTP-RSR (all 9 PDFs in RID/)")
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python -m RID --demo")
        print("  python -m RID --extract-pdf")

if __name__ == "__main__":
    main()
```

**Example use after adding:**

```bash
cd l:\Steel_Brain
.venv\Scripts\activate

python -m RID --demo
python -m RID --extract-pdf
python -m RID --version
python -m RID
# (prints help and examples)
```

---

## Summary

| Option              | What it is in one line                                      |
|---------------------|-------------------------------------------------------------|
| **1. FIDF duration**| Config field `duration_sec`; loop stops when time expires.   |
| **2. SEOL voltage** | Function that caps efficiency by Input LTP (e.g. `min(S_n, LTP_input)`). |
| **3. Unit tests**   | A `tests/` with pytest checks for RLE, LTP, S_n, Carnot, coupling. |
| **4. CLI**          | `python -m RID --demo` / `--extract-pdf` / `--version` from `__main__.py`. |

If you tell me which of these you want (e.g. "2 and 4 only"), I can add exactly those.
