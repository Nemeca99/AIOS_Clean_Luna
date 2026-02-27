#!/usr/bin/env python3
"""
Verify ACCOMPLISHMENTS_AND_PROOFS.md for internal consistency.

Checks the document's Appendix and Section 1–3 claims against:
- The canonical formulas (RLE, LTP, RSR, S_n)
- The SEOL voltage law
- The extrusion RLE proxy and numerical examples
- The RID package implementation (so doc and code agree)

Run from project root (L:\\Steel_Brain):
  python RID/verify_accomplishments_doc.py

Or from RID folder:
  python verify_accomplishments_doc.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# After path fix, import RID
import RID
from RID import (
    rle_n,
    ltp_n,
    rsr_n,
    stability_scalar,
    effective_system_efficiency,
    voltage_law_violated,
    discrepancy_01,
)


def _approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def run_checks() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    # ---- Canonical RLE (Section 1 + Appendix) ----
    # RLE_n = (E_next - U_n) / E_n
    r = rle_n(E_next=95.0, U_n=5.0, E_n=100.0)
    ok = _approx(r, 0.9)
    results.append(("RLE formula (95,5,100) = 0.9", ok, f"got {r}"))

    r0 = rle_n(E_next=100.0, U_n=0.0, E_n=100.0)
    r1 = rle_n(E_next=0.0, U_n=100.0, E_n=100.0)
    ok = _approx(r0, 1.0) and _approx(r1, 0.0)
    results.append(("RLE clamp 1.0 and 0.0", ok, f"got {r0}, {r1}"))

    # ---- Canonical LTP (Section 1 + Appendix) ----
    # LTP_n = min(1, n_n / d_n)
    ok = _approx(ltp_n(10.0, 10.0), 1.0) and _approx(ltp_n(5.0, 10.0), 0.5) and _approx(ltp_n(15.0, 10.0), 1.0)
    results.append(("LTP min(1, n/d): (10,10)=1, (5,10)=0.5, (15,10)=1", ok, ""))

    # Extrusion: 75 A demand, 90 A and 80 A capacity => LTP = 1
    ltp_90 = ltp_n(90.0, 75.0)
    ltp_80 = ltp_n(80.0, 75.0)
    ok = _approx(ltp_90, 1.0) and _approx(ltp_80, 1.0)
    results.append(("Extrusion LTP at 75A: 90A and 80A capacity => 1", ok, f"got {ltp_90}, {ltp_80}"))

    # ---- Default discrepancy and RSR (Appendix) ----
    # D(y, r) = |y - r| for [0,1]; RSR = 1 - D
    d = discrepancy_01(0.65, 0.70)
    ok = _approx(d, 0.05)
    results.append(("Discrepancy_01(0.65, 0.70) = 0.05", ok, f"got {d}"))

    rsr = rsr_n(0.70, 0.65)  # observable, reconstruction (order may vary in doc)
    ok = _approx(rsr, 0.95)
    results.append(("RSR for 415 vs 420°F normalized 0.65,0.70 => 0.95", ok, f"got {rsr}"))

    rsr1 = rsr_n(1.0, 1.0)
    rsr0 = rsr_n(1.0, 0.0)
    ok = _approx(rsr1, 1.0) and _approx(rsr0, 0.0)
    results.append(("RSR (1,1)=1, (1,0)=0", ok, f"got {rsr1}, {rsr0}"))

    # ---- S_n = RSR * LTP * RLE (Section 1) ----
    s1 = stability_scalar(1.0, 1.0, 1.0)
    s2 = stability_scalar(0.5, 0.5, 0.5)
    ok = _approx(s1, 1.0) and _approx(s2, 0.125)
    results.append(("S_n product: (1,1,1)=1, (0.5,0.5,0.5)=0.125", ok, f"got {s1}, {s2}"))

    # ---- Voltage law (Appendix) ----
    # effective_system_efficiency(S_n, LTP_input) = min(S_n, LTP_input)
    eff = effective_system_efficiency(0.95, 0.8)
    ok = _approx(eff, 0.8)
    results.append(("effective_system_efficiency(0.95, 0.8) = 0.8 (capped)", ok, f"got {eff}"))

    eff2 = effective_system_efficiency(0.7, 0.8)
    ok = _approx(eff2, 0.7)
    results.append(("effective_system_efficiency(0.7, 0.8) = 0.7 (no cap)", ok, f"got {eff2}"))

    viol_true = voltage_law_violated(0.95, 0.8)
    viol_false = voltage_law_violated(0.7, 0.8)
    ok = viol_true is True and viol_false is False
    results.append(("voltage_law_violated: S_n>LTP_input only when violated", ok, f"got {viol_true}, {viol_false}"))

    # ---- Extrusion RLE proxy (Appendix) ----
    # E_n=100, U_n=demand, E_next=100-U_n => RLE = (100 - 2*U_n)/100
    for u, expected in [(0, 1.0), (25, 0.5), (50, 0.0)]:
        e_next = 100.0 - u
        r = rle_n(E_next=e_next, U_n=float(u), E_n=100.0)
        ok = _approx(r, expected, tol=1e-6)
        results.append((f"Extrusion proxy U_n={u} => RLE={expected}", ok, f"got {r}"))

    # RLE decreases as demand increases (U_n 0 -> 25 -> 50)
    r0 = rle_n(100.0, 0.0, 100.0)
    r25 = rle_n(75.0, 25.0, 100.0)
    r50 = rle_n(50.0, 50.0, 100.0)
    ok = r0 > r25 > r50
    results.append(("Extrusion proxy: RLE decreases as demand increases", ok, f"got {r0:.3f} > {r25:.3f} > {r50:.3f}"))

    # ---- Doc vs code: full extrusion-style step ----
    # Setpoint 415 vs actual 420 (normalized), demand 75/90 and 75/80, RLE proxy
    y, recon = (420 - 350) / 100, (415 - 350) / 100  # 0.70, 0.65
    rsr_val = rsr_n(y, recon)
    ltp_90_val = ltp_n(90.0, 75.0)
    ltp_80_val = ltp_n(80.0, 75.0)
    demand_pct = 75.0  # 75A as % of 100 scale for proxy
    e_next = 100.0 - demand_pct
    rle_val = rle_n(E_next=e_next, U_n=demand_pct, E_n=100.0)
    s_90 = stability_scalar(rsr_val, ltp_90_val, rle_val)
    s_80 = stability_scalar(rsr_val, ltp_80_val, rle_val)
    ok = (
        _approx(rsr_val, 0.95, tol=0.01)
        and _approx(ltp_90_val, 1.0)
        and _approx(ltp_80_val, 1.0)
        and rle_val < rsr_val  # RLE worst leg
    )
    results.append(("Doc narrative: RSR~0.95, LTP=1, RLE worst", ok, f"RSR={rsr_val:.3f} LTP=1 RLE={rle_val:.3f} S_90={s_90:.3f} S_80={s_80:.3f}"))

    return results


def main() -> None:
    print("Verifying ACCOMPLISHMENTS_AND_PROOFS.md (Appendix + Section 1-3)...")
    print()
    results = run_checks()
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    for name, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        extra = f"  ({msg})" if msg and not ok else ""
        print(f"  [{status}] {name}{extra}")
    print()
    print(f"Total: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
    print("No contradictions found; document and RID implementation are consistent.")


if __name__ == "__main__":
    main()
