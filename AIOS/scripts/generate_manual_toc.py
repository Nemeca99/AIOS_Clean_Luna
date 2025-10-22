#!/usr/bin/env python3
"""
AIOS Manual TOC Generator

Automatically generates MANUAL_TOC.md by parsing AIOS_MANUAL.md section headers.
Can be integrated into the audit system for automatic updates.

Usage:
    py scripts/generate_manual_toc.py
    py scripts/generate_manual_toc.py --output MANUAL_TOC.md
    py scripts/generate_manual_toc.py --check  # Verify TOC is up to date
"""

import re
from pathlib import Path
from typing import List, Tuple
import sys
import argparse


def parse_manual_sections(manual_path: Path) -> List[Tuple[int, str, str]]:
    """
    Parse AIOS_MANUAL.md and extract all section headers with line numbers.
    
    Returns:
        List of (line_number, section_number, section_title) tuples
    """
    sections = []
    
    with open(manual_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Match patterns like: ## 1.1 What is AIOS? {#section.11.what.is.aios}
    section_pattern = re.compile(r'^##\s+(\d+\.\d+)\s+(.+?)\s+\{#')
    
    for i, line in enumerate(lines, start=1):
        match = section_pattern.match(line)
        if match:
            section_num = match.group(1)
            section_title = match.group(2).strip()
            sections.append((i, section_num, section_title))
    
    return sections


def generate_toc_content(sections: List[Tuple[int, str, str]]) -> str:
    """
    Generate the MANUAL_TOC.md content from parsed sections.
    """
    content = """# AIOS Manual - Table of Contents

**Note:** Use line numbers for navigation. Canonical PDF is 660 pages (Letter, 1" margins).

| Line | Section | Topic |
|------|---------|-------|
| 2 |  | Comprehensive Guide to the Adaptive Intelligence Operating System |
| 23 |  | DOCUMENT PURPOSE |
| 61 |  | QUICK NAVIGATION |
"""
    
    # Add all parsed sections
    for line_num, section_num, title in sections:
        content += f"| {line_num} | {section_num} | {section_num} {title} |\n"
    
    return content


def check_toc_up_to_date(manual_path: Path, toc_path: Path) -> bool:
    """
    Check if MANUAL_TOC.md is up to date with AIOS_MANUAL.md.
    
    Returns:
        True if up to date, False otherwise
    """
    # Parse current sections
    current_sections = parse_manual_sections(manual_path)
    
    # Read existing TOC
    if not toc_path.exists():
        print(f"❌ TOC file not found: {toc_path}")
        return False
    
    with open(toc_path, 'r', encoding='utf-8') as f:
        toc_content = f.read()
    
    # Check if all sections are present with correct line numbers
    errors = []
    for line_num, section_num, title in current_sections:
        # Look for line in TOC
        expected_pattern = f"| {line_num} | {section_num} |"
        if expected_pattern not in toc_content:
            errors.append(f"Section {section_num} at line {line_num}: not found or incorrect")
    
    if errors:
        print(f"❌ TOC is out of date:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
        return False
    
    print("✅ TOC is up to date")
    return True


def main():
    parser = argparse.ArgumentParser(description='Generate AIOS Manual TOC')
    parser.add_argument('--manual', default='AIOS_MANUAL.md', help='Path to manual file')
    parser.add_argument('--output', default='MANUAL_TOC.md', help='Path to TOC output file')
    parser.add_argument('--check', action='store_true', help='Check if TOC is up to date')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    manual_path = Path(args.manual)
    toc_path = Path(args.output)
    
    if not manual_path.exists():
        print(f"❌ Manual file not found: {manual_path}")
        sys.exit(1)
    
    # Check mode
    if args.check:
        is_up_to_date = check_toc_up_to_date(manual_path, toc_path)
        sys.exit(0 if is_up_to_date else 1)
    
    # Generate mode
    print(f"📖 Parsing {manual_path}...")
    sections = parse_manual_sections(manual_path)
    
    if args.verbose:
        print(f"   Found {len(sections)} sections")
        print(f"   First section: {sections[0][1]} at line {sections[0][0]}")
        print(f"   Last section: {sections[-1][1]} at line {sections[-1][0]}")
    
    print(f"✍️  Generating TOC...")
    toc_content = generate_toc_content(sections)
    
    print(f"💾 Writing to {toc_path}...")
    with open(toc_path, 'w', encoding='utf-8') as f:
        f.write(toc_content)
    
    print(f"✅ TOC generated successfully!")
    print(f"   Sections: {len(sections)}")
    print(f"   Output: {toc_path}")
    print(f"   Size: {len(toc_content):,} bytes")


if __name__ == '__main__':
    main()

