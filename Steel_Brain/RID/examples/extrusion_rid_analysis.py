#!/usr/bin/env python3
# ==========================================
# RID analysis for extrusion heater burnout investigation
# Setup: 415°F setpoint, ~420°F actual, 1200 PSI, Eurotherm 3216, 15A SSR
#
# Usage:
#   python extrusion_rid_analysis.py                        # synthetic data, 6x15A SSR
#   python extrusion_rid_analysis.py data.csv                # your CSV
#   python extrusion_rid_analysis.py data.csv --ssr 2x40    # same data, 2x 3-phase 40A SSRs (LTP uses 80A capacity)
#
# CSV columns: time_s, setpoint_F, actual_F, heater_pct [, pressure_psi, demand_01]
# demand_01: bounded [0,1] = 0A at 0, full 75A at 1. If missing, derived as heater_pct/100.
# --ssr 6x15  (default): capacity = 90A total
# --ssr 2x40:            capacity = 80A total (2x40)
# ==========================================

import sys
import csv
from pathlib import Path

# Add repo root for RID import when run as script
_repo_root = Path(__file__).resolve().parent.parent.parent
if _repo_root not in sys.path:
    sys.path.insert(0, str(_repo_root))

from RID import rsr_n, ltp_n, rle_n, stability_scalar, diagnostic_step


# Temp range for normalization (°F)
TEMP_LO, TEMP_HI = 350.0, 450.0

def norm_temp(f):
    return max(0.0, min(1.0, (f - TEMP_LO) / (TEMP_HI - TEMP_LO)))


# Full heater demand (amps) when demand_01 = 1
DEMAND_AMPS_FULL = 75.0


def run_rid_on_rows(rows, ssr_config="6x15"):
    """rows: list of dicts with setpoint_F, actual_F, heater_pct; optional demand_01 in [0,1].
    demand_01: 0 = 0A, 1 = full 75A. Used in RSR (as context), LTP (demand_amps = 75*demand_01), RLE (loss scales with demand_01).
    """
    capacity_amps = 90.0 if ssr_config == "6x15" else 80.0
    results = []
    for i, r in enumerate(rows):
        setpoint_F = float(r["setpoint_F"])
        actual_F = float(r["actual_F"])
        heater_pct = float(r.get("heater_pct", 50.0))
        heater_pct = max(0.0, min(100.0, heater_pct))
        # Bounded demand on system [0,1]: 0 = 0A, 1 = full 75A. From CSV or derived from heater_pct.
        if "demand_01" in r and r["demand_01"].strip() != "":
            demand_01 = max(0.0, min(1.0, float(r["demand_01"])))
        else:
            demand_01 = heater_pct / 100.0

        y_n = norm_temp(actual_F)
        recon = norm_temp(setpoint_F)
        RSR_n = rsr_n(y_n, recon)

        # LTP: capacity (amps) vs demand. demand_amps = 75 * demand_01 (0 at 0, 75A at 1)
        demand_amps = DEMAND_AMPS_FULL * demand_01
        if demand_amps <= 0:
            demand_amps = 1e-6  # avoid div by zero; no demand -> no strain
        LTP_n = ltp_n(capacity_amps, demand_amps)

        # RLE: loss scales with demand_01 (higher demand -> more energy spent -> more loss proxy)
        E_n = 100.0
        U_n = 20.0 * demand_01  # 0 at demand=0, 20 at full demand
        E_next = max(1.0, E_n - U_n)
        RLE_n = rle_n(E_next, U_n, E_n)

        S_n = stability_scalar(RSR_n, LTP_n, RLE_n)
        diag = diagnostic_step(RSR_n, LTP_n, RLE_n, step=i)
        worst = min(
            [("RSR", RSR_n), ("LTP", LTP_n), ("RLE", RLE_n)],
            key=lambda x: x[1],
        )
        results.append({
            "step": i,
            "demand_01": demand_01,
            "RSR_n": RSR_n,
            "LTP_n": LTP_n,
            "RLE_n": RLE_n,
            "S_n": S_n,
            "worst_leg": worst[0],
            "action": diag.action,
            "setpoint_F": setpoint_F,
            "actual_F": actual_F,
            "heater_pct": heater_pct,
        })
    return results


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def demand_sweep_data():
    """Rows with demand_01 from 0% to 100% in 10% steps. Fixed 415 setpoint, 420 actual."""
    rows = []
    for pct in range(0, 101, 10):
        demand_01 = pct / 100.0
        rows.append({
            "time_s": pct,
            "setpoint_F": 415.0,
            "actual_F": 420.0,
            "heater_pct": pct,
            "demand_01": str(demand_01),
            "pressure_psi": 1200,
        })
    return rows


def synthetic_data():
    """Typical scenario: 415 setpoint, 420 actual, some oscillation in heater %."""
    rows = []
    for i in range(40):
        t = i * 2.0  # every 2 s
        setpoint_F = 415.0
        # Simulate slight overshoot and some oscillation (controller chasing)
        actual_F = 420.0 + (5.0 if i % 4 < 2 else -3.0) + (i % 3 - 1) * 2.0
        # Heater often high (trying to hold 415 with melt at 420 → possible overdrive then cutback)
        heater_pct = 75.0 + (i % 5) * 5 + (10 if actual_F < 415 else -5)
        heater_pct = max(0, min(100, heater_pct))
        rows.append({
            "time_s": t,
            "setpoint_F": setpoint_F,
            "actual_F": actual_F,
            "heater_pct": heater_pct,
            "pressure_psi": 1200,
        })
    return rows


def main():
    argv = sys.argv[1:]
    positional = []
    ssr_config = "6x15"
    sweep = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--sweep" or a == "-s":
            sweep = True
            i += 1
            continue
        if a == "--ssr" and i + 1 < len(argv):
            ssr_config = argv[i + 1].strip().lower()
            i += 2
            continue
        if a.startswith("--ssr="):
            ssr_config = a.split("=", 1)[1].strip().lower()
            i += 1
            continue
        if not a.startswith("--"):
            positional.append(a)
        i += 1
    if ssr_config not in ("6x15", "2x40"):
        ssr_config = "6x15"

    if sweep:
        rows = demand_sweep_data()
        print("Demand sweep 0-100% (demand_01: 0=0A, 1=75A). Fixed 415°F setpoint, 420°F actual.")
        # Run both SSR configs for comparison
        results_6x15 = run_rid_on_rows(rows, ssr_config="6x15")
        results_2x40 = run_rid_on_rows(rows, ssr_config="2x40")
        print()
        print("=" * 95)
        print("Comparison: 6x15 (90A) vs 2x40 (80A) — same demand sweep, 415°F setpoint, 420°F actual")
        print("=" * 95)
        print(f"{'demand%':<8} {'demand_A':<10} {'RSR':<8} {'LTP_90A':<10} {'LTP_80A':<10} {'RLE':<8} {'S_n_90A':<10} {'S_n_80A':<10}")
        print("-" * 95)
        for r6, r40 in zip(results_6x15, results_2x40):
            demand_pct = r6["demand_01"] * 100.0
            demand_A = DEMAND_AMPS_FULL * r6["demand_01"]
            print(f"{demand_pct:<8.0f} {demand_A:<10.1f} {r6['RSR_n']:<8.3f} {r6['LTP_n']:<10.3f} {r40['LTP_n']:<10.3f} {r6['RLE_n']:<8.3f} {r6['S_n']:<10.3f} {r40['S_n']:<10.3f}")
        print("=" * 95)
        print("(RSR and RLE are process-based; identical for both. LTP/S_n differ by capacity: 90A vs 80A.)")
        return
    elif positional:
        csv_path = Path(positional[0])
        if not csv_path.exists():
            print("File not found:", csv_path)
            sys.exit(1)
        rows = load_csv(csv_path)
        print("Loaded", len(rows), "rows from", csv_path)
    else:
        rows = synthetic_data()
        print("No CSV provided. Using synthetic data (415°F setpoint, ~420°F actual, oscillating heater %).")
        print("To use your own data: python extrusion_rid_analysis.py your_log.csv [--ssr 2x40]")
        print("For 0-100% demand table: python extrusion_rid_analysis.py --sweep [--ssr 2x40]")
        print()
    print("SSR config for LTP: ", ssr_config, " (capacity ", 90 if ssr_config == "6x15" else 80, "A total)", sep="")
    print()

    results = run_rid_on_rows(rows, ssr_config=ssr_config)

    print()
    if sweep:
        print("=" * 82)
        print("RID table: demand 0-100% (demand_01: 0=0A, 1=75A full demand)")
        print("=" * 82)
        print(f"{'demand%':<8} {'demand_01':<10} {'demand_A':<10} {'RSR':<8} {'LTP':<8} {'RLE':<8} {'S_n':<8} worst")
        print("-" * 82)
        for r in results:
            demand_pct = r["demand_01"] * 100.0
            demand_A = DEMAND_AMPS_FULL * r["demand_01"]
            print(f"{demand_pct:<8.0f} {r['demand_01']:<10.3f} {demand_A:<10.1f} {r['RSR_n']:<8.3f} {r['LTP_n']:<8.3f} {r['RLE_n']:<8.3f} {r['S_n']:<8.3f} {r['worst_leg']}")
    else:
        print("=" * 78)
        print("RID per-step summary (demand_01: 0=0A, 1=75A full demand)")
        print("=" * 78)
        print(f"{'step':<6} {'demand_01':<10} {'SP°F':<8} {'actual°F':<10} {'heater%':<10} {'RSR':<8} {'LTP':<8} {'RLE':<8} {'S_n':<8} worst")
        print("-" * 78)
        for r in results[:10]:
            print(f"{r['step']:<6} {r['demand_01']:<10.3f} {r['setpoint_F']:<8.1f} {r['actual_F']:<10.1f} {r['heater_pct']:<10.1f} {r['RSR_n']:<8.3f} {r['LTP_n']:<8.3f} {r['RLE_n']:<8.3f} {r['S_n']:<8.3f} {r['worst_leg']}")
        if len(results) > 15:
            print("...")
            for r in results[-5:]:
                print(f"{r['step']:<6} {r['demand_01']:<10.3f} {r['setpoint_F']:<8.1f} {r['actual_F']:<10.1f} {r['heater_pct']:<10.1f} {r['RSR_n']:<8.3f} {r['LTP_n']:<8.3f} {r['RLE_n']:<8.3f} {r['S_n']:<8.3f} {r['worst_leg']}")

    # Which leg is worst most often?
    worst_counts = {"RSR": 0, "LTP": 0, "RLE": 0}
    for r in results:
        worst_counts[r["worst_leg"]] += 1
    total = len(results)
    print()
    print("=" * 70)
    print("Which RID leg is worst most often? (points to category of cause)")
    print("=" * 70)
    for leg in ["RSR", "LTP", "RLE"]:
        pct = 100.0 * worst_counts[leg] / total if total else 0
        print(f"  {leg}: {worst_counts[leg]}/{total} steps ({pct:.0f}%)")
    winner = max(worst_counts, key=worst_counts.get)
    print()
    if winner == "RSR":
        print(">> RSR (reconstruction) is worst most often.")
        print("   Suggests: Setpoint chasing / control oscillation. Controller belief (setpoint) vs actual melt temp is off.")
        print("   Look at: PID tuning, thermocouple lag/placement, deadband, SSR cycle time.")
    elif winner == "LTP":
        print(">> LTP (structure vs demand) is worst most often.")
        print("   Suggests: Demand often at or above capacity (heater/SSR running flat out or borderline).")
        print("   Look at: Heater/SSR sizing (15A adequate?), sustained high heater %, thermal margin.")
    else:
        print(">> RLE (loss / retained fraction) is worst most often.")
        print("   Suggests: High dissipation or stress per step (energy going in but 'lost' as thermal stress).")
        print("   Look at: Cycling frequency, heat path to barrel, element rating vs duty, ambient cooling.")
    print("=" * 70)


if __name__ == "__main__":
    main()
