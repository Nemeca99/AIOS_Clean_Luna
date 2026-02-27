# RID unit tests. Run from Steel_Brain: python -m pytest RID/tests/ -v

import pytest


def test_rle_n_basic():
    from RID import rle_n
    assert rle_n(E_next=95.0, U_n=5.0, E_n=100.0) == 0.9


def test_rle_n_clamp():
    from RID import rle_n
    assert rle_n(100.0, 0.0, 100.0) == 1.0
    assert rle_n(0.0, 100.0, 100.0) == 0.0


def test_loss_fraction():
    from RID import loss_fraction
    assert abs(loss_fraction(0.9) - 0.1) < 1e-9


def test_ltp_n_adequacy():
    from RID import ltp_n
    assert ltp_n(10.0, 10.0) == 1.0
    assert ltp_n(5.0, 10.0) == 0.5
    assert ltp_n(15.0, 10.0) == 1.0


def test_ltp_n_invalid():
    from RID import ltp_n
    with pytest.raises(ValueError):
        ltp_n(1.0, 0.0)


def test_stability_scalar_unity():
    from RID import stability_scalar
    assert stability_scalar(1.0, 1.0, 1.0) == 1.0
    assert stability_scalar(0.5, 0.5, 0.5) == 0.125


def test_rsr_n():
    from RID import rsr_n
    assert rsr_n(1.0, 1.0) == 1.0
    assert rsr_n(0.9, 0.9) == 1.0
    assert rsr_n(1.0, 0.0) == 0.0


def test_carnot_bound():
    from RID import lambda_min_carnot, eta_max_carnot
    assert lambda_min_carnot(300.0, 600.0) == 0.5
    assert eta_max_carnot(300.0, 600.0) == 0.5


def test_lambda_mismatch():
    from RID import lambda_mismatch
    assert lambda_mismatch(10.0, 10.0) == 0.0
    assert lambda_mismatch(5.0, 10.0) == 0.5


def test_coupling_amplified_loss():
    from RID import coupling_amplified_loss
    # 1 - (1-0.1)*(1-0.1) = 1 - 0.81 = 0.19
    assert abs(coupling_amplified_loss([0.1, 0.1]) - 0.19) < 1e-9
    assert coupling_amplified_loss([]) == 0.0


def test_temporal_mismatch_condition():
    from RID import temporal_mismatch_condition
    assert temporal_mismatch_condition(2.0, 1.0) is True
    assert temporal_mismatch_condition(1.0, 2.0) is False


def test_cost_depth_factorial():
    from RID import cost_depth_factorial
    assert cost_depth_factorial(0) == 1.0
    assert cost_depth_factorial(4) == 24.0


def test_effective_system_efficiency():
    from RID import effective_system_efficiency
    assert effective_system_efficiency(0.95, 1.0) == 0.95
    assert effective_system_efficiency(0.95, 0.8) == 0.8
    assert effective_system_efficiency(0.5, 0.8) == 0.5


def test_voltage_law_violated():
    from RID import voltage_law_violated
    assert voltage_law_violated(0.95, 0.8) is True
    assert voltage_law_violated(0.7, 0.8) is False


def test_invariant_preserving_factorization_identity():
    from RID import invariant_preserving_factorization_identity
    assert invariant_preserving_factorization_identity(5.0, 3.0) is True
    assert invariant_preserving_factorization_identity(5.0, 0.0) is False


def test_phase_boundary_divergence_near():
    from RID import phase_boundary_divergence_near
    assert phase_boundary_divergence_near(0.1, 1e7) is True
    assert phase_boundary_divergence_near(2.0, 1e7) is False
    assert phase_boundary_divergence_near(0.1, 100.0) is False


def test_rate_scaling():
    from RID import rate_scaling
    assert rate_scaling(1.0, 2.0) == 0.5
    assert rate_scaling(0.8, 1.0) == 0.8


def test_divergence_indicator():
    from RID import divergence_indicator
    assert divergence_indicator(0.4, 0.35) > 0  # headroom
    assert divergence_indicator(0.3, 0.35) < 0  # feedback risk


def test_diagnostic_step_nominal():
    from RID import diagnostic_step
    res = diagnostic_step(1.0, 1.0, 1.0)
    assert res.action == "continue"
    assert res.state.S_n >= 0.999


def test_diagnostic_step_intervene_rle():
    from RID import diagnostic_step
    res = diagnostic_step(1.0, 1.0, 0.8)
    assert res.action == "intervene_rle"
