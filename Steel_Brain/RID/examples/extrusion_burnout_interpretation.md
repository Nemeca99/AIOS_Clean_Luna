# What the RID numbers suggest about your heater burnout (and how to move forward)

## 1. What RID pointed to (from the sweep and analysis)

With your setup (415°F setpoint, 420°F actual, 75A demand, demand 0–100%):

| RID leg | Your numbers | What it means for burnout |
|--------|---------------|----------------------------|
| **LTP** (capacity vs demand) | LTP = 1 across 0–100% demand | **Electrical overload is not indicated.** 75A is within both 90A (6×15) and 80A (2×40). Sizing is not the primary cause. |
| **RSR** (setpoint vs actual) | RSR ≈ 0.95 (415 vs 420°F) | Small, steady error. **Severe setpoint chasing or control oscillation is not indicated.** Not pointing to “controller thrashing” the heaters. |
| **RLE** (loss / retained fraction) | RLE was the “worst” leg in the sweep; it drops as demand increases | **Loss and dissipation** are where the triangle is stressed. RID is saying: look at where energy is “lost” or where **thermal/mechanical stress** is high—not at undersizing or control noise. |

So RID does **not** point to:
- Undersized amps (LTP is fine).
- Wild control behavior (RSR is stable).

It **does** point to:
- **Loss/stress path:** cycling, heat path, contamination, or mechanical stress (e.g. on leads or at the interface to the die).

That fits your story: **lead tension** and **melt on the leads** are both good candidates for “extra loss” and stress that don’t show up as simple amp overload.

---

## 2. How your physical setup maps to “loss” (RLE) and stress

| What you described | How it fits RID (RLE / loss / stress) |
|--------------------|---------------------------------------|
| **Lateral die movement → tension on leads** | Repeated flex and pull → wire fatigue, insulation damage, hot spots, possible partial short. Energy is “lost” into mechanical degradation and local heating, not into clean heating of the die. |
| **Melt stream around pistons → melt on/near leads** | Contamination → insulation breakdown, carbonization, tracking. Again: extra “loss” and local stress, not reflected in total amps. |
| **Cartridge heaters close to edge (1" from edge, 12"×18" die)** | Concentrated heat near perimeter; mechanical coupling to a moving die can create hot spots and thermal cycling at the cartridge–bore interface. |
| **Switch to Dalton split sheath + 90° clip** | Gets **leads away from melt** and can reduce **tension** by routing. Directly addresses two of the “loss/stress” mechanisms RID is pointing at. |

So:
- RID’s “RLE / loss” message is **consistent with** lead tension and melt on leads as drivers of burnout, not with simple overload or bad control.

---

## 3. Best way to move forward (order of action)

### A. Protect the leads (you’re already doing this)

- **Dalton split sheath + 90° clip** addresses:
  - **Melt on leads:** Leads away from melt path → less contamination and tracking.
  - **Lead tension:** 90° clip and good routing can take flex and pull off the terminations and reduce cyclic stress.
- **Do:** Ensure the clip and routing are such that **lateral die movement does not pull or bend the heater terminals**. Use strain relief and enough slack so the **die** moves, not the **connections**. If there’s still tension, add a second fix (e.g. flexible lead, junction box on a floating mount).

### B. Reduce melt at the source (medium term)

- Melt around pistons is a **recurring source of contamination** near the heaters.
- **Do:** Plan for seal or piston/barrel refurb so less melt exits around the pistons. Even partial improvement reduces the “loss/stress” environment RID is flagging.
- **Monitor:** After changes, log setpoint, actual temp, heater %, and (if possible) lead resistance or any thermal imaging; re-run RID on real data to see if RLE and S_n improve.

### C. Confirm with real data in RID (recommended)

- So far, RID has been run on **synthetic or proxy** data. To see if your **process** numbers point to the same story:
  - Log from the Eurotherm: **time, setpoint, actual temp, heater %** (and optional pressure) at 1–5 s over a typical run (including periods when you’ve had burnouts before).
  - Run:  
    `python extrusion_rid_analysis.py your_log.csv`  
    and optionally `--ssr 2x40` if you switch SSRs.
- **Look for:**
  - **LTP** staying near 1 (confirms no electrical overload).
  - **RSR** not collapsing (confirms control isn’t thrashing).
  - **RLE** or **S_n** dipping before or during problem periods (would support “loss/stress” as the main issue).
- That gives you a **data-backed** reason (aligned with RID) to keep focusing on leads and melt, not on amp capacity or control tuning.

### D. Heat path and heater type (split sheath vs cartridge)

- **Split sheath** can improve contact and heat path to the die and reduce hot spots compared to some cartridge installations.
- **Do:** Follow Dalton’s torque/spec for the clamp and surface contact. Good mechanical contact reduces local “loss” (heat stuck at the heater instead of in the die) and can extend life.
- If you have thermocouples at multiple locations, compare RSR (setpoint vs actual) **by zone** after the change; more even temps support a better heat path.

---

## 4. Short summary

| Question | Answer |
|----------|--------|
| Do the numbers point to a **reason** for burnout? | Yes: **loss/stress path** (RLE), not overload (LTP) or control chasing (RSR). |
| What does that mean in your plant? | Focus on **lead tension**, **melt on leads**, and **heat path/contact**—not on increasing amp capacity or retuning the loop. |
| Best way to move forward? | (1) Keep leads away from melt and tension (90° clip + routing/strain relief). (2) Reduce melt leak at pistons when possible. (3) Log real runs and re-run RID to confirm RLE/S_n and to watch for improvement after changes. (4) Install and torque split sheaths per spec for a better, more even heat path. |

If you want, we can add a one-page “checklist” version of this (what to log, what to run in RID, what to inspect on the die and leads) for the floor or for a tech.
