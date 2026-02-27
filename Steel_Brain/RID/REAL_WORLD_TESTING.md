# Testing RID on a real-world application

RID needs **four kinds of inputs** from your system. Map your domain to these, then run the triangle (or FIDF loop) and use **S_n** and the **diagnostic action** to decide what to do.

---

## 1. Map your system to RID inputs

| RID input | Meaning | Real-world examples |
|-----------|---------|----------------------|
| **y_n** (observable) | Current “true” signal you care about | Sensor reading, actual utilization, throughput, error rate (normalize to 0–1 if using default RSR) |
| **reconstruction** | System’s estimate of that signal (often delayed or filtered) | Last step’s estimate, Kalman output, model prediction, delayed echo |
| **n_n** (structural support) | Capacity or resources available | Server capacity, thread pool size, battery capacity, budget |
| **d_n** (demand) | Load or requirement | Incoming load, requested precision, required SLA |
| **E_n, U_n, E_next** | Capacity before step, loss during step, capacity after | Battery before/after and drain; budget and spend; throughput and drop |

**Important:** Default RSR uses a 0–1 discrepancy. If your observable and reconstruction are not in [0, 1], either **normalize** them (e.g. divide by max or scale to [0,1]) or pass a **custom discrepancy** (e.g. `discrepancy_l1`) to `rsr_n()`.

---

## 2. Single-step check (no loop)

Use this when you have **one snapshot** (e.g. one time window, one request, one batch).

```python
from RID import rsr_n, ltp_n, rle_n, stability_scalar, diagnostic_step, effective_system_efficiency

# Your data (example: utilization 0.8, estimate 0.75, capacity 10, demand 9, budget 100→95 with loss 5)
y_n = 0.8
recon_n = 0.75
n_n = 10.0
d_n = 9.0
E_n, U_n, E_next = 100.0, 5.0, 95.0

RSR_n = rsr_n(y_n, recon_n)           # reconstruction fidelity
LTP_n = ltp_n(n_n, d_n)               # structure vs demand
RLE_n = rle_n(E_next, U_n, E_n)       # retained fraction
S_n = stability_scalar(RSR_n, LTP_n, RLE_n)

diag = diagnostic_step(RSR_n, LTP_n, RLE_n)
print("S_n:", S_n, "| action:", diag.action, "|", diag.message)

# Optional: cap by input LTP (SEOL voltage law)
LTP_input = 0.95
S_reported = effective_system_efficiency(S_n, LTP_input)
```

Interpretation:

- **S_n == 1**: No issue in this snapshot.
- **S_n < 1**: Use `diag.action` (e.g. `check_ltp`, `mandatory_descent`, `intervene_rle`) to know where to act.
- Use **S_reported** if you enforce “efficiency cannot exceed input LTP”.

---

## 3. Multi-step (FIDF loop)

Use this when you have **a time series or stream** (e.g. every second, every request, every batch).

Implement four callbacks that return, for step index `n`, the observable, reconstruction, (n_n, d_n), and (E_n, U_n, E_next). Then run:

```python
from RID import FIDFConfig, run_fidf_loop

config = FIDFConfig(dt=1.0, max_steps=100)  # or duration_sec=3600
state = run_fidf_loop(
    config,
    get_observable=your_get_y_n,
    get_reconstruction=your_get_recon_n,
    get_support_demand=your_get_n_d,
    get_capacity=your_get_E_U_Enext,
    on_step=lambda n, st, d: print(f"step {n}: S_n={st.S_n:.3f} action={d.action}"),
)
```

See **`RID/examples/real_world_example.py`** for a full runnable example with synthetic data.

---

## 4. Run the included example

**Option A – Run the script from the RID folder** (works from `L:\Steel_Brain\RID` or `L:\Steel_Brain\RID\examples`):

```powershell
cd L:\Steel_Brain\RID
python examples\real_world_example.py
```

Or from `RID\examples`:

```powershell
cd L:\Steel_Brain\RID\examples
python real_world_example.py
```

**Option B – Run as module from project root** (must be in `L:\Steel_Brain`):

```powershell
cd L:\Steel_Brain
python -m RID.examples.real_world_example
```

This runs a 5-step pipeline with:

- Observable vs reconstruction (RSR),
- Support vs demand (LTP),
- Capacity and loss (RLE),
- SEOL voltage law (effective_system_efficiency, voltage_law_violated),

and prints S_n and the diagnostic action each step so you can see how to interpret RID in a real-world-style flow.

---

## 5. Checklist for your own app

1. **Choose your signals**: What is “reality” (y_n) and “system’s view” (reconstruction)? Normalize to [0,1] or pick a discrepancy.
2. **Choose structure vs demand**: What is capacity (n_n) and what is demand (d_n)?
3. **Choose capacity transition**: What is “before” (E_n), “loss” (U_n), “after” (E_next)?
4. **Single-step**: Call `rsr_n`, `ltp_n`, `rle_n`, `stability_scalar`, `diagnostic_step` once per snapshot; optionally `effective_system_efficiency`.
5. **Multi-step**: Implement the four callbacks and run `run_fidf_loop`; use `on_step` to log or alert when S_n < 1 or action != "continue".

After that, “testing RID on a real-world application” means feeding these inputs from your app (logs, metrics, DB) and checking that S_n and the diagnostic actions match what you expect and that you can trigger your own alerts or descent logic from them.
