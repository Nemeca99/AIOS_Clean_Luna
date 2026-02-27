#!/usr/bin/env python3
# ==========================================
# RID validation: import all modules and run a minimal FIDF loop.
# Run from Steel_Brain: python -m RID.validate_rid
# Or: python -m RID --check
# ==========================================

import sys


def main():
    errors = []

    # 1. Import all public API
    try:
        from RID import (
            Axiom,
            rle_n,
            loss_fraction,
            law_statement,
            invariant_preserving_factorization_identity,
            ltp_n,
            rsr_n,
            stability_scalar,
            rate_scaling,
            divergence_indicator,
            diagnostic_step,
            frequency_from_dt,
            frequency_from_rpm,
            interface_efficiency_rsr,
            DescentTrigger,
            mandatory_descent_triggers,
            canonical_statement,
            phase_boundary_divergence_near,
            lambda_min_carnot,
            eta_max_carnot,
            lambda_mismatch,
            lambda_total,
            coupling_amplified_loss,
            temporal_mismatch_condition,
            cost_depth_factorial,
            operational_protocol,
            voltage_law_summary,
            effective_system_efficiency,
            voltage_law_violated,
            interface_efficiency,
            FIDFConfig,
            FIDFState,
            layer1_rsr_ltp_rle,
            layer2_logic_gate,
            run_fidf_loop,
        )
    except Exception as e:
        errors.append(f"Import failed: {e}")
        print("[FAIL] RID import:", e)
        sys.exit(1)

    # 2. Quick equation checks
    try:
        assert rle_n(95.0, 5.0, 100.0) == 0.9
        assert abs(loss_fraction(0.9) - 0.1) < 1e-9
        assert ltp_n(10.0, 10.0) == 1.0
        assert stability_scalar(1.0, 1.0, 1.0) == 1.0
        assert lambda_min_carnot(300.0, 600.0) == 0.5
        assert effective_system_efficiency(0.95, 0.8) == 0.8
        assert len(mandatory_descent_triggers()) == 6
        assert len(operational_protocol()) == 4
    except AssertionError as e:
        errors.append(f"Equation check: {e}")

    # 3. FIDF loop for 2 steps (trivial callbacks)
    try:
        config = FIDFConfig(dt=1.0, max_steps=2)
        steps_seen = []

        def get_obs(n):
            return 0.9

        def get_recon(n):
            return 0.88

        def get_supp(n):
            return (9.0, 10.0)

        def get_cap(n):
            return (100.0, 5.0, 95.0)

        state = run_fidf_loop(
            config,
            get_obs,
            get_recon,
            get_supp,
            get_cap,
            on_step=lambda n, st, d: steps_seen.append(n),
        )
        assert len(steps_seen) == 2
        assert state.step == 1
    except Exception as e:
        errors.append(f"FIDF loop: {e}")

    if errors:
        for e in errors:
            print("[FAIL]", e)
        sys.exit(1)

    print("[OK] RID validation passed: imports, equations, FIDF loop (2 steps).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
