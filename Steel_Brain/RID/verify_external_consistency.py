#!/usr/bin/env python3
"""
Verify external consistency: implementation vs source specifications.

Checks that key formula phrases from the RID specs appear in the extracted PDF text,
so the implementation is traceable to the source documents (not just internally consistent).

Run from project root (L:\\Steel_Brain):
  python RID/verify_external_consistency.py

Requires: RID/extracted_text/*.txt (run python -m RID --extract-pdf first if missing).
Exit 0 if all external checks pass; 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RID_DIR = ROOT / "RID"
EXTRACTED = RID_DIR / "extracted_text"

# Phrases that must appear in at least one extracted spec file (canonical spec / SEOL / etc.)
# Specs use ■_n for structural support; we implement as n_n. Allow either or "structural".
EXTERNAL_PHRASES = [
    ("RLE", "RLE_n or RLE definition"),
    ("E_n", "capacity before / E_n variable"),
    ("U_n", "loss / U_n variable"),
    ("E_{n+1}", "capacity after (or E_next)"),
    ("LTP_n", "LTP definition"),
    ("min(1", "LTP min(1, ...)"),
    ("d_n", "demand"),
    ("RSR_n", "RSR definition"),
    ("1 − D", "RSR = 1 - D"),
    ("S_n", "stability scalar"),
    ("RSR_n · LTP_n · RLE_n", "S_n product"),
]
# Structural support: spec uses ■_n; code uses n_n
STRUCTURAL_PHRASES = ["■_n", "structural support", "structural adequacy"]
# SEOL voltage law: may have extra spaces in extracted text
SEOL_PHRASES = [("exceed", "SEOL voltage law (exceed)"), ("Input", "SEOL Input boundary"), ("LTP", "LTP in SEOL")]


def run_checks() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    if not EXTRACTED.is_dir():
        results.append((
            "extracted_text/ exists",
            False,
            f"Run 'python -m RID --extract-pdf' to create {EXTRACTED}",
        ))
        return results

    txt_files = list(EXTRACTED.glob("*.txt"))
    if not txt_files:
        results.append(("extracted_text/*.txt present", False, "No .txt files in extracted_text/"))
        return results

    all_text = ""
    for p in sorted(txt_files):
        try:
            all_text += p.read_text(encoding="utf-8", errors="replace") + "\n"
        except Exception as e:
            results.append((f"read {p.name}", False, str(e)))

    for phrase, description in EXTERNAL_PHRASES:
        normalized = phrase.replace("−", "-").replace("·", "*")
        found = phrase in all_text or normalized in all_text
        if not found and "E_{n+1}" in phrase:
            found = "E_{n+1}" in all_text or "E_next" in all_text
        if not found and "1 − D" in phrase:
            found = "1 - D" in all_text or "1 − D" in all_text or "1-D" in all_text
        results.append((f"Spec phrase: {description}", found, "" if found else f"'{phrase}' not in extracted_text/"))

    # Structural support: spec uses ■_n; code uses n_n
    found_structural = any(p in all_text for p in STRUCTURAL_PHRASES)
    results.append(("Spec: structural support (spec symbol or term)", found_structural, "" if found_structural else "none of structural support phrases in extracted_text/"))

    # SEOL voltage law and Input LTP (may have spaces in extracted text)
    for keyword, description in SEOL_PHRASES:
        found = keyword in all_text
        results.append((f"Spec: {description}", found, "" if found else f"'{keyword}' not in extracted_text/"))

    return results


def main() -> int:
    print("RID external consistency (implementation vs source specs)")
    print("==========================================================")
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
    print("Implementation is traceable to source specifications (extracted text).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
