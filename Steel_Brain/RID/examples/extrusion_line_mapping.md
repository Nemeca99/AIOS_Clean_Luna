# RID for an extrusion line (heaters + melt plastic)

To plug **real-world numbers** from your extrusion line into RID, we need to define one quantity for each of RID’s four inputs. Below is what each RID concept means in your domain and what information you’d need to provide (per time step or per zone).

---

## 1. RSR: “Reality” vs “system’s belief” (reconstruction fidelity)

**RID asks:** How well does the system’s *estimate* of the process match *what’s actually happening*?

| RID term | In your extrusion line | What we need from you |
|----------|------------------------|------------------------|
| **y_n** (observable) | The “true” process value you care about | **Actual melt temperature** (e.g. from melt thermocouple), **actual pressure** at die/screw, or **actual throughput** (kg/h). Pick one main variable per “step” (e.g. per zone or per time interval). |
| **reconstruction** | The system’s *estimate* of that same quantity | **Setpoint**, **model-predicted** melt temp (from heater power + screw speed), or **delayed/filtered** reading (e.g. previous step’s value, or a soft sensor). |

**Example:**  
- y_n = melt temp at zone 4 (e.g. 215 °C)  
- reconstruction = what the controller *thinks* it is (e.g. 210 °C from a model or last scan).  
→ RID will tell you how much “reconstruction error” you have (RSR). If you normalize temps to 0–1 (e.g. 150–250 °C → 0–1), you can use RID’s default RSR; otherwise we use a normalized discrepancy.

**What to provide:**  
- Per step (or per zone): **actual value** and **estimated/controlled value** for the same quantity (e.g. melt temp, pressure, or throughput).

---

## 2. LTP: “Capacity” vs “demand” (structure vs load)

**RID asks:** Does the system have enough *structural support* (capacity) to meet the *demand* placed on it?

| RID term | In your extrusion line | What we need from you |
|----------|------------------------|------------------------|
| **n_n** (structural support) | What the process *can* deliver | **Heater capacity** (kW or % available) for the zone(s) you care about, **screw speed capacity**, **cooling capacity**, or **barrel thermal mass** in useful units. |
| **d_n** (demand) | What the process *needs* right now | **Heat load required** to hold or reach target melt temp, **throughput demand** (kg/h), **cooling demand** to stabilize, or **power demand** (kW) to maintain setpoint. |

**Example:**  
- n_n = 12 kW heater capacity at zone 4  
- d_n = 10 kW required to hold 215 °C at current throughput  
→ LTP = min(1, 12/10) = 1 (adequate). If d_n = 14 kW, LTP &lt; 1 (structural strain).

**What to provide:**  
- Per step (or per zone): **one capacity number** (n_n) and **one demand number** (d_n) in the same units (e.g. kW, kg/h, or normalized 0–1).

---

## 3. RLE: “Before”, “loss”, “after” (retained usable fraction)

**RID asks:** How much *usable capacity* is *retained* across a transition, and how much is *lost*?

| RID term | In your extrusion line | What we need from you |
|----------|------------------------|------------------------|
| **E_n** (capacity before) | Usable “resource” at the start of the step | **Available energy** (e.g. kWh in a buffer), **thermal headroom** (how much margin before limit), **hopper level** (kg), or **remaining heater life** in comparable units. |
| **U_n** (loss) | Irreversible loss during the step | **Heat loss to environment** (kW or kWh), **material waste** (kg), **degradation** (e.g. viscosity drop), or **energy dissipated** (friction, cooling). |
| **E_next** (capacity after) | Usable “resource” at the end of the step | Same type as E_n, but *after* the transition (e.g. E_n − U_n if that’s how you define it, or measured “remaining” capacity). |

**Example:**  
- E_n = 100 (e.g. 100% thermal headroom or 100 kWh equivalent)  
- U_n = 5 (loss this step)  
- E_next = 95  
→ RLE = (95 − 5) / 100 = 0.9 (90% retained).

**What to provide:**  
- Per step: **three numbers** in consistent units: **before** (E_n), **loss** (U_n), **after** (E_next). They can be normalized (e.g. 0–100 or 0–1) as long as E_n &gt; 0 and the formula RLE = (E_next − U_n) / E_n makes sense for your definition.

---

## 4. Time steps and sampling

**RID also needs:**

- **What one “step” is:** e.g. one controller scan (e.g. 1 s), one barrel zone, one “cycle” (screw revolution), or one batch.
- **How many steps** you want to evaluate (e.g. 60 for 1 minute at 1 Hz, or one step per zone along the barrel).

---

## Summary: minimal list for your extrusion line

If you can provide, **per step** (or per zone):

1. **RSR:** One “actual” value (y_n) and one “estimated/setpoint” value (reconstruction) for the same thing (e.g. melt temp, pressure, or throughput).  
2. **LTP:** One “capacity” (n_n) and one “demand” (d_n) in the same units (e.g. kW, kg/h, or 0–1).  
3. **RLE:** Three numbers: capacity before (E_n), loss this step (U_n), capacity after (E_next).  
4. **Step definition:** What one step is and how many steps you want to run.

With that, we can plug your numbers into the same pattern as `real_world_example.py` (or a small extrusion-specific script) and get S_n and the diagnostic action (continue / check_ltp / mandatory_descent / intervene_rle, etc.) for each step. If you tell me your data source (PLC, historian, CSV, live API), I can suggest exact variable names or a CSV format next.
