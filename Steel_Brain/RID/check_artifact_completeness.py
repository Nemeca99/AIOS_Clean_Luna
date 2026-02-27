#!/usr/bin/env python3
"""
Check that all artifacts required for the RID "proof" and paper are present.

Verifies:
  - Nine source PDFs in RID/
  - Core package modules (axioms, triangle, ltp_principle, thermodynamics, fidf, seol, discrepancy, validate_rid, __main__)
  - Documentation (README, ACCOMPLISHMENTS_AND_PROOFS, REAL_WORLD_TESTING, REPRODUCIBILITY, RID_FRAMEWORK_PAPER)
  - Verification scripts (verify_accomplishments_doc, run_all_verification, this script)
  - Tests (RID/tests/test_rid.py)
  - Examples (real_world_example, extrusion_rid_analysis)
  - Optional: verification_report.json exists and all_passed is true

Run from project root (L:\\Steel_Brain):
  python RID/check_artifact_completeness.py

Exit 0 if all required checks pass; 1 otherwise.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Project root = parent of RID
ROOT = Path(__file__).resolve().parent.parent
RID_DIR = ROOT / "RID"

# PDFs: each substring must match exactly one .pdf in RID/ (allows minor naming differences)
EXPECTED_PDF_SUBSTRINGS = [
    "RLE_Axioms_Law_of_Compressed_State_Dynamics.pdf",
    "RLE-LTP-RSR_Stability_Equation_Canonical_Spec.pdf",
    "Layer Transition Principle (LTP).pdf",
    "Bridge Document",
    "Equation.pdf",
    "Fourth Invariant Dimensionless Framework (FIDF).pdf",
    "Recursive State Reconstruction (RSR) as a universal system law.pdf",
    "LTP Framework.pdf",
    "the SEOL (System Efficiency Operations Layer) framework.pdf",
]

REQUIRED_MODULES = [
    "RID/__init__.py",
    "RID/axioms.py",
    "RID/triangle.py",
    "RID/ltp_principle.py",
    "RID/thermodynamics.py",
    "RID/fidf.py",
    "RID/seol.py",
    "RID/discrepancy.py",
    "RID/validate_rid.py",
    "RID/extract_pdf_text.py",
    "RID/__main__.py",
]

REQUIRED_DOCS = [
    "RID/README.md",
    "RID/ACCOMPLISHMENTS_AND_PROOFS.md",
    "RID/REAL_WORLD_TESTING.md",
    "RID/REPRODUCIBILITY.md",
    "RID/RID_FRAMEWORK_PAPER.md",
]

REQUIRED_SCRIPTS = [
    "RID/verify_accomplishments_doc.py",
    "RID/run_all_verification.py",
    "RID/verify_external_consistency.py",
    "RID/check_artifact_completeness.py",
]

REQUIRED_TESTS = [
    "RID/tests/test_rid.py",
]

REQUIRED_EXAMPLES = [
    "RID/examples/real_world_example.py",
    "RID/examples/extrusion_rid_analysis.py",
]


def run_checks() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    # PDFs (in RID dir): match by substring so minor naming differences (dash, space) are OK
    pdf_files = list(RID_DIR.glob("*.pdf"))
    for sub in EXPECTED_PDF_SUBSTRINGS:
        matches = [f for f in pdf_files if sub in f.name]
        ok = len(matches) >= 1
        results.append((f"PDF: ...{sub[:50]}...", ok, "" if ok else f"no PDF containing '{sub[:40]}...' in RID/"))

    # Modules (relative to ROOT)
    for rel in REQUIRED_MODULES:
        p = ROOT / rel
        ok = p.is_file()
        results.append((f"Module: {rel}", ok, "" if ok else f"missing: {p}"))

    # Docs
    for rel in REQUIRED_DOCS:
        p = ROOT / rel
        ok = p.is_file()
        results.append((f"Doc: {rel}", ok, "" if ok else f"missing: {p}"))

    # Scripts
    for rel in REQUIRED_SCRIPTS:
        p = ROOT / rel
        ok = p.is_file()
        results.append((f"Script: {rel}", ok, "" if ok else f"missing: {p}"))

    # Tests
    for rel in REQUIRED_TESTS:
        p = ROOT / rel
        ok = p.is_file()
        results.append((f"Test: {rel}", ok, "" if ok else f"missing: {p}"))

    # Examples
    for rel in REQUIRED_EXAMPLES:
        p = ROOT / rel
        ok = p.is_file()
        results.append((f"Example: {rel}", ok, "" if ok else f"missing: {p}"))

    # Optional: verification report exists and all_passed
    report_path = RID_DIR / "verification_report.json"
    if report_path.is_file():
        try:
            with open(report_path, encoding="utf-8") as f:
                data = json.load(f)
            all_passed = data.get("all_passed", False)
            results.append(("Report: verification_report.json all_passed", all_passed, "" if all_passed else "run run_all_verification.py"))
        except Exception as e:
            results.append(("Report: verification_report.json readable", False, str(e)))
    else:
        results.append(("Report: verification_report.json exists", False, "run run_all_verification.py first"))

    return results


def main() -> int:
    print("RID artifact completeness check")
    print("===============================")
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
    print("Artifact set is complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
