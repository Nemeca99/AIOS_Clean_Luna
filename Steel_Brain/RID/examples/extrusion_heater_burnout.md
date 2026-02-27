# Using RID to investigate heater burnout (415°F setpoint, 420°F actual, 15A SSR)

**Your setup:** 415°F setpoint, melt typically 420°F at 1200 PSI; Eurotherm 3216 + 15A solid state relay; heaters burning up repeatedly.

RID can’t measure the relay or heater directly, but it can use **process numbers you already have** (or can log) to see which of three “stress directions” is worst: **reconstruction error** (RSR), **capacity vs demand** (LTP), or **loss / dissipation** (RLE). That points to a *category* of cause and what to log next.

---

## What to log (minimum)

From the **Eurotherm 3216** (and if available, pressure), capture a time series. One row per time step (e.g. every 1–5 seconds). Suggested columns:

| Column        | Source / meaning                    | Example |
|---------------|-------------------------------------|--------|
| `time_s`      | Elapsed seconds (or timestamp)      | 0, 1, 2, … |
| `setpoint_F`  | Temperature setpoint (°F)           | 415    |
| `actual_F`    | Process (melt) temperature (°F)    | 420    |
| `heater_pct`  | Heater output 0–100% (Eurotherm OP) | 0–100  |
| `pressure_psi`| Melt pressure (if available)        | 1200   |

If the 3216 only gives you setpoint and PV (actual), that’s enough to start: we’ll use **setpoint vs actual** for RSR and **heater %** to approximate demand for LTP. If you can log **heater output %** (or on/off and cycle time), that’s very helpful for LTP and RLE.

---

## How this maps to RID and to “why heaters burn”

| RID leg | In your process | If this leg is bad, it often suggests |
|--------|------------------|----------------------------------------|
| **RSR** (reconstruction) | Setpoint (what the controller “believes” is the target) vs actual melt temp | **Setpoint chasing / oscillation.** Controller constantly correcting (overshoot/undershoot) → SSR and heaters cycle hard → thermal cycling and burnout. |
| **LTP** (structure vs demand) | Heater/SSR capacity (15A) vs instantaneous heat demand (from heater % or error) | **Sustained overload or borderline sizing.** Demand often at or above capacity → relay and heaters run flat out or cycle at high current → burnout. |
| **RLE** (loss / retained) | How much “usable” state is retained vs lost each step (e.g. thermal headroom, energy dissipated) | **High dissipation or poor heat transfer.** A lot of energy going in but “lost” (thermal stress on elements, cycling losses) → elements overheat and fail. |

So:

- **RSR often low** → look at control tuning (PID, deadband, cycle time) and thermocouple placement/lag.
- **LTP often &lt; 1** → look at heater/SSR sizing and whether demand routinely exceeds 15A capability.
- **RLE often low** → look at thermal path, cycling frequency, and where energy is really going (elements, barrel, ambient).

---

## Normalizing your numbers for RID

- **Temp for RSR:** Normalize °F to 0–1, e.g. `(temp_F - 350) / 100` so 350°F→0, 450°F→1. Then **y_n = actual** (normalized), **reconstruction = setpoint** (normalized). RID’s default RSR uses a 0–1 discrepancy.
- **LTP:** Use **capacity** = 15 (A) or 100 (%) as “max available”, **demand** = heater output % (or a scaled value from error × gain if you don’t have %). Same units top and bottom (e.g. % vs %).
- **RLE:** If you don’t have explicit “before/loss/after”, use a proxy: e.g. **E_n = 100** (%), **U_n = heater_pct** (energy “spent” this step), **E_next = 100 - U_n** (simplified). Or use deviation from setpoint as “stress” and derive a loss term. The script below uses a simple proxy so you can run on minimal data.

---

## What the script does

The script **`extrusion_rid_analysis.py`** (in this folder):

1. Reads a CSV with columns like: `time_s`, `setpoint_F`, `actual_F`, `heater_pct`, (optional) `pressure_psi`.
2. Computes RSR (setpoint vs actual, normalized), LTP (capacity 100% vs demand from heater %), RLE (simple proxy from heater % and retention).
3. Outputs per-step RSR, LTP, RLE, S_n, and which leg is **worst** (min of the three).
4. Summarizes: e.g. “RSR lowest in 70% of steps” → prioritize control/reconstruction; “LTP &lt; 1 in 80% of steps” → prioritize capacity/demand; “RLE lowest” → prioritize loss/dissipation.

That gives you a **specific direction** (RSR vs LTP vs RLE) from their current process numbers. You can then log more detail (e.g. SSR cycle count, element temps) in that direction.

---

## Eurotherm 3216 – what to pull

- **Setpoint** (SP) and **process value** (PV) for the controlled zone.
- **Output %** (heater demand) if available (analog out or register).
- **Sample rate:** 1–5 s is usually enough to see oscillation and demand; faster if you want to catch short cycling.

Export to CSV with the column names above so the script can read it. A sample format is in **`extrusion_log_sample.csv`**.

---

## Run the analysis

From `L:\Steel_Brain\RID\examples` (or with path):

```bash
# Synthetic data (415°F setpoint, ~420°F actual, oscillating heater %)
python extrusion_rid_analysis.py

# Your logged CSV from the Eurotherm
python extrusion_rid_analysis.py your_log.csv
```

The script prints per-step RSR, LTP, RLE, S_n, and which leg is worst, then a one-line **suggested direction** (RSR → control/chasing; LTP → capacity/demand; RLE → loss/dissipation) so you can focus on one category of cause for the burnups.
