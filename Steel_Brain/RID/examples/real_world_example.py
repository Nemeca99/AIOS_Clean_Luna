#!/usr/bin/env python3
# ==========================================
# RID on a real-world-style application
#
# Run from anywhere as a script (recommended):
#   python real_world_example.py
#   (from L:\Steel_Brain\RID\examples\ or with path)
#
# Or from project root L:\Steel_Brain:
#   python -m RID.examples.real_world_example
#
# Scenario: A small "pipeline" with
#   - Observable (y_n): e.g. current utilization or sensor reading
#   - Reconstruction (recon_n): delayed/filtered estimate (RSR checks fidelity)
#   - Structural support (n_n) vs demand (d_n): e.g. server capacity vs load (LTP)
#   - Capacity transition (E_n, U_n, E_next): e.g. budget or battery (RLE)
# ==========================================

import sys
from pathlib import Path

# Add project root so "from RID import ..." works when run as script from RID/ or RID/examples/
_repo_root = Path(__file__).resolve().parent.parent.parent
if _repo_root not in sys.path:
    sys.path.insert(0, str(_repo_root))

from RID import (
    FIDFConfig,
    run_fidf_loop,
    stability_scalar,
    diagnostic_step,
    effective_system_efficiency,
    voltage_law_violated,
)


def main():
    print("=" * 60)
    print("RID real-world example: pipeline with sensor, capacity, and loss")
    print("=" * 60)

    # ---- 1. Define your "real" data (here: synthetic over 5 steps) ----
    # In a real app these come from your system (logs, metrics, DB, sensors).

    # Observable: e.g. actual utilization [0,1] each step
    observed_util = [0.7, 0.72, 0.68, 0.85, 0.90]

    # Reconstruction: e.g. delayed estimate (previous step + small error)
    # RID interprets this as "how well does the system's model match reality?"
    reconstructed_util = [0.65, 0.70, 0.71, 0.70, 0.82]  # lag + drift at step 4

    # Structural support (n_n) vs demand (d_n): e.g. capacity vs load
    # LTP = min(1, n_n/d_n). If demand exceeds support, LTP < 1.
    support_per_step = [10.0, 10.0, 10.0, 8.0, 8.0]   # capacity drops at step 3
    demand_per_step = [8.0, 8.5, 9.0, 9.0, 10.0]      # demand rises

    # Capacity transition: E_n (before), U_n (loss), E_next (after)
    # RLE = (E_next - U_n) / E_n. E.g. battery or budget per step.
    capacity_before = [100.0, 95.0, 90.0, 85.0, 80.0]
    loss_per_step = [5.0, 5.0, 5.0, 8.0, 10.0]       # loss grows
    capacity_after = [95.0, 90.0, 85.0, 77.0, 70.0]

    # Optional: Input LTP ceiling (SEOL voltage law). E.g. "source" max efficiency.
    LTP_input_ceiling = 0.95

    # ---- 2. Wire your data into RID callbacks ----
    def get_observable(n):
        return observed_util[n] if n < len(observed_util) else 0.0

    def get_reconstruction(n):
        return reconstructed_util[n] if n < len(reconstructed_util) else 0.0

    def get_support_demand(n):
        s = support_per_step[n] if n < len(support_per_step) else 10.0
        d = demand_per_step[n] if n < len(demand_per_step) else 8.0
        return (s, d)

    def get_capacity(n):
        if n >= len(capacity_before):
            return (100.0, 0.0, 100.0)
        return (capacity_before[n], loss_per_step[n], capacity_after[n])

    # ---- 3. Run FIDF loop ----
    config = FIDFConfig(dt=1.0, max_steps=len(observed_util))
    results = []

    def on_step(n, state, diagnostic):
        # Apply voltage law: reported efficiency cannot exceed input ceiling
        S_reported = effective_system_efficiency(state.S_n, LTP_input_ceiling)
        violated = voltage_law_violated(state.S_n, LTP_input_ceiling)
        results.append({
            "step": n,
            "RSR_n": state.RSR_n,
            "LTP_n": state.LTP_n,
            "RLE_n": state.RLE_n,
            "S_n": state.S_n,
            "S_reported": S_reported,
            "voltage_violated": violated,
            "action": diagnostic.action,
            "message": diagnostic.message,
        })
        print(f"  step {n}: S_n={state.S_n:.3f} RSR={state.RSR_n:.3f} LTP={state.LTP_n:.3f} RLE={state.RLE_n:.3f} -> {diagnostic.action}")

    run_fidf_loop(
        config,
        get_observable,
        get_reconstruction,
        get_support_demand,
        get_capacity,
        on_step=on_step,
    )

    # ---- 4. Interpret for your application ----
    print()
    print("Interpretation (for your app):")
    for r in results:
        if r["action"] != "continue":
            print(f"  Step {r['step']}: {r['action']} -- {r['message'][:60]}...")
        if r["voltage_violated"]:
            print(f"  Step {r['step']}: Voltage law violated (S_n > input LTP ceiling); cap to {r['S_reported']:.3f}.")
    print()
    print("RID run complete. Use S_n < 1 or non-'continue' actions to trigger alerts or descent in your system.")
    print("=" * 60)


if __name__ == "__main__":
    main()
