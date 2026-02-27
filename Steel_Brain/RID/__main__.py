# ==========================================
# RID CLI: python -m RID [--demo | --extract-pdf | --version]
# ==========================================

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="RID: RLE-LTP-RSR Stability Framework",
        epilog="Examples:\n  python -m RID --check\n  python -m RID --demo\n  python -m RID --extract-pdf\n  python -m RID --version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--demo", action="store_true", help="Run the RID demo")
    parser.add_argument("--check", action="store_true", help="Validate RID: imports, equations, FIDF loop")
    parser.add_argument("--extract-pdf", action="store_true", help="Extract text from all PDFs in RID folder")
    parser.add_argument("--version", action="store_true", help="Show version / doc source")
    args = parser.parse_args()

    if args.check:
        from .validate_rid import main as check_main
        sys.exit(check_main())
    if args.demo:
        from .run_rid_demo import main as demo_main
        demo_main()
    elif args.extract_pdf:
        from .extract_pdf_text import main as extract_main
        extract_main()
    elif args.version:
        print("RID: RLE-LTP-RSR (all 9 PDFs in RID/)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
