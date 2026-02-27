#!/usr/bin/env python3
# ==========================================
# RID: Extract text from ALL PDFs in this folder
# Run from Steel_Brain: python -m RID.extract_pdf_text
# Requires: pip install pypdf
# Writes one .txt per PDF into extracted_text/
# ==========================================

import os
import sys
from pathlib import Path

# RID package root (where this script lives)
RID_DIR = Path(__file__).resolve().parent
OUT_DIR = RID_DIR / "extracted_text"
OUT_DIR.mkdir(exist_ok=True)


def extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("[ERR] pip install pypdf")
        sys.exit(1)

    reader = PdfReader(str(path))
    parts = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
            if text:
                parts.append(f"--- Page {i + 1} ---\n{text}")
        except Exception as e:
            parts.append(f"--- Page {i + 1} [extract error: {e}] ---\n")
    return "\n\n".join(parts) if parts else ""


def main():
    pdfs = sorted(RID_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in", RID_DIR)
        return

    print("Extracting", len(pdfs), "PDF(s) to", OUT_DIR)
    for path in pdfs:
        stem = path.stem
        out_path = OUT_DIR / f"{stem}.txt"
        text = extract_pdf(path)
        out_path.write_text(text, encoding="utf-8")
        print("  ", path.name, "->", out_path.name, "(%d chars)" % len(text))

    print("Done.")


if __name__ == "__main__":
    main()
