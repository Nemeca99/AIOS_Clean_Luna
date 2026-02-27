# How LTP is affected: 6× 1-phase 15A SSRs vs 2× 3-phase 40A SSRs

**LTP** in RID is: **LTP_n = min(1, n_n / d_n)**  
- **n_n** = structural support (capacity the system can deliver)  
- **d_n** = demand (what the process needs at that moment)  

Same units for both (e.g. amps, kW, or 0–100%). When **demand exceeds capacity**, LTP &lt; 1 (structural strain; RID suggests mandatory descent / intervention).

---

## 1. Capacity and demand in amps (per circuit)

Rough comparison (same voltage, resistive load):

| Setup | Circuits | Amps per circuit | Total current (all circuits) |
|-------|----------|-------------------|------------------------------|
| **Current** | 6 × 1-phase 15A | 15A each | 6 × 15 = **90A** total (if all on) |
| **Proposed** | 2 × 3-phase 40A | 40A per phase per relay | 2 × 40 = **80A per phase** (3-phase total power is √3 × V × I_line) |

**Total power** (assuming single phase 240V for 1-phase, 240V line for 3-phase):  
- 6×15A 1-phase: 6 × 240 × 15 = **21.6 kW**  
- 2×40A 3-phase: 2 × √3 × 240 × 40 ≈ **33.2 kW**  

So in **total capacity** (kW), the 2×40A 3-phase setup is **higher** than 6×15A 1-phase. If you define **n_n = total available kW** (or total available amps) and **d_n = total demand** (same units), then switching to 2×40A 3-phase **increases n_n** → LTP goes **up** (more headroom, LTP stays at 1 more often or gets closer to 1).

---

## 2. Per-circuit view (fewer, bigger circuits)

If you instead think **per circuit** (each SSR as one “structure”):

- **Current:** 6 circuits, each **n_n = 15A** capacity. Demand per zone **d_n** (amps or %) is spread across 6.  
- **Proposed:** 2 circuits, each **n_n = 40A** capacity. The same total load is now split across **2** circuits, so **demand per circuit d_n** is about **3×** what it was per zone (one 40A circuit feeds what used to be 3×15A zones).

So:

- **Capacity per circuit:** 15A → 40A ⇒ **n_n goes up** (40/15 ≈ 2.67×).  
- **Demand per circuit:** one circuit now carries ~3 zones’ load ⇒ **d_n goes up** (~3× per circuit).

**LTP per circuit** = min(1, 40 / d_n_new).  

- If each old 15A zone was running at e.g. 12A, then **d_n_old = 12A**, LTP_old = min(1, 15/12) = 1.  
- New: one 40A circuit carries 3×12 = 36A ⇒ **d_n_new = 36A**, LTP_new = min(1, 40/36) ≈ **1.11 → 1**. So still OK.  
- If old zones were often at 14A, LTP_old = 15/14 ≈ 1.07 → 1. New: 3×14 = 42A on one 40A circuit ⇒ **d_n_new = 42 &gt; 40** ⇒ **LTP_new = 40/42 &lt; 1** (structural strain). So with fewer, bigger circuits, **LTP can get worse** if per-circuit demand exceeds the new per-circuit capacity (40A).

So:

- **Total system:** 2×40A 3-phase usually gives **more total capacity** → LTP (system-wide) tends to **improve**.  
- **Per circuit:** Each circuit has **more capacity** (40A vs 15A) but **more demand** (load of 3 zones). LTP **improves** if 40A is enough for that combined load; **worsens** if demand per circuit often exceeds 40A.

---

## 3. Summary table (effect on LTP)

| Question | Effect on LTP |
|----------|----------------|
| Total capacity (kW or total amps) | 2×40A 3-phase is **higher** total capacity → **n_n up** → LTP **better** (all else equal). |
| Per-circuit capacity vs per-circuit demand | Each circuit: **n_n = 40A** (up from 15A), **d_n = load of 3 zones** (up). LTP **better** if 40A ≥ combined load; **worse** if combined load &gt; 40A. |
| Fewer SSRs (6 → 2) | Demand is concentrated on fewer circuits → **d_n per circuit up** → LTP can **drop** if you don’t also increase capacity enough per circuit (40A must handle 3× previous zone load). |

So: **LTP is improved** by the change if total and per-circuit **capacity (n_n)** increase more than **demand (d_n)** (total or per circuit). **LTP is worsened** if, per circuit, demand (3 zones’ load) regularly exceeds 40A.

---

## 4. How to see it in your RID analysis

To make LTP reflect the **real** SSR change, define capacity and demand in **amps** (or kW) instead of “100%”:

- **Current setup (6×15A):**  
  - n_n = 15 (A per zone) or 90 (A total); d_n = measured or estimated amps per zone or total.  
- **Proposed (2×40A):**  
  - n_n = 40 (A per circuit) or 2×40 = 80 (A total per phase); d_n = amps per circuit or total.

Then **LTP_n = min(1, n_n / d_n)**.  

- If you have **heater %** only: assume a scale, e.g. 100% = 15A (current) or 40A (proposed), so **d_n = (heater_pct / 100) × 15** or **× 40**.  
- Compare runs: same process, same demand in kW or amps; change only **n_n** from 15 to 40 per circuit (and combine 3 zones into one d_n for the 40A circuit). You’ll see LTP go up or down depending on whether 40A is enough for the combined load.

**In the script:** Use **`--ssr 2x40`** to compute LTP with 80A total capacity (2×40A) instead of 90A (6×15A). Same process demand (from heater_pct) then yields **LTP &lt; 1** whenever demand &gt; 80A (e.g. heater_pct &gt; ~89). So you can compare runs:

```bash
python extrusion_rid_analysis.py your_log.csv          # LTP with 6×15A (90A)
python extrusion_rid_analysis.py your_log.csv --ssr 2x40   # LTP with 2×40A (80A)
```
