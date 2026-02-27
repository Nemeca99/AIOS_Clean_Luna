#!/usr/bin/env python3
# ==========================================
# RID Framework — non-interactive demo
# Run from Steel_Brain: python -m RID.run_rid_demo
# ==========================================

from . import (
    Axiom,
    rle_n,
    loss_fraction,
    law_statement,
    ltp_n,
    rsr_n,
    stability_scalar,
    rate_scaling,
    divergence_indicator,
    diagnostic_step,
    frequency_from_dt,
    frequency_from_rpm,
)

def main():
    print("=" * 60)
    print("RID: RLE-LTP-RSR Stability Framework (Demo)")
    print("=" * 60)

    # --- Axioms ---
    print("\n[AXIOMS] Law of Compressed State Dynamics")
    for ax in Axiom:
        print(f"  Axiom {ax.value}: {ax.name}")
    print("\n  Law:", law_statement()[:80] + "...")

    # --- RLE ---
    print("\n[RLE] Recursive Loss Equation")
    E_n, U_n, E_next = 100.0, 5.0, 95.0
    rle = rle_n(E_next, U_n, E_n)
    lam = loss_fraction(rle)
    print(f"  E_n={E_n}, U_n={U_n}, E_{{n+1}}={E_next} -> RLE_n={rle:.4f}, loss_fraction={lam:.4f}")

    # --- LTP ---
    print("\n[LTP] Layer Transition Principle")
    n_n, d_n = 8.0, 10.0
    ltp = ltp_n(n_n, d_n)
    print(f"  n_n={n_n}, d_n={d_n} -> LTP_n={ltp:.4f} (structure {'meets' if ltp >= 1 else 'below'} demand)")

    # --- RSR ---
    print("\n[RSR] Recursive State Reconstruction")
    y_n, recon = 0.9, 0.85
    rsr = rsr_n(y_n, recon)
    print(f"  y_n={y_n}, reconstruction={recon} -> RSR_n={rsr:.4f}")

    # --- Stability scalar S_n ---
    print("\n[STABILITY] S_n = RSR_n * LTP_n * RLE_n")
    S = stability_scalar(rsr, ltp, rle)
    print(f"  S_n = {rsr:.4f} * {ltp:.4f} * {rle:.4f} = {S:.4f}")

    # --- Rate normalization ---
    print("\n[RATE NORMALIZATION]")
    dt_old, dt_new = 1.0, 0.5
    m = dt_old / dt_new
    S_expected = rate_scaling(S, m)
    print(f"  dt_old={dt_old}, dt_new={dt_new} -> m={m}, S_expected(new)={S_expected:.4f}")
    f_hz = frequency_from_dt(dt_new)
    print(f"  f = 1/dt = {f_hz} Hz")

    # --- Divergence ---
    S_observed_new = 0.35
    dS = divergence_indicator(S_observed_new, S_expected)
    print(f"  S_observed(new)={S_observed_new}, dS={dS:.4f} ({'headroom' if dS >= 0 else 'feedback risk'})")

    # --- Diagnostic loop ---
    print("\n[DIAGNOSTIC] Minimal logic gate")
    for name, (rsr, ltp, rle) in [
        ("Nominal", (1.0, 1.0, 1.0)),
        ("RSR low", (0.7, 1.0, 1.0)),
        ("LTP strain", (0.95, 0.6, 1.0)),
        ("RLE loss", (1.0, 1.0, 0.8)),
    ]:
        res = diagnostic_step(rsr, ltp, rle, rsr_low_threshold=0.9)
        print(f"  {name}: S_n={res.state.S_n:.2f} -> {res.action}: {res.message[:50]}")

    print("\n" + "=" * 60)
    print("[SYSTEM] RID demo complete.")
    print("=" * 60)

if __name__ == "__main__":
    main()
