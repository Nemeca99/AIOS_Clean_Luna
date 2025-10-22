#!/usr/bin/env python3
"""
Add Anchor IDs to All Manual Headings
Transforms manual headings to include proper anchor IDs for RAG indexing
"""

import re
import sys
from pathlib import Path

def generate_anchor(title: str, section_num: str = "") -> str:
    """Generate a kebab-case anchor ID from title"""
    # Remove section numbers
    title_clean = re.sub(r'^\d+\.?\d*\.?\d*\s*', '', title)
    
    # Convert to lowercase
    anchor = title_clean.lower()
    
    # Replace spaces and special chars with hyphens
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[-\s]+', '.', anchor)
    
    # Remove leading/trailing dots
    anchor = anchor.strip('.')
    
    # Add section prefix if available
    if section_num:
        section_clean = section_num.replace('.', '').replace(' ', '')
        anchor = f"section.{section_clean}.{anchor}"
    
    return anchor

def main():
    manual_path = Path("AIOS_MANUAL.md")
    backup_path = Path("AIOS_MANUAL.md.backup")
    
    if not manual_path.exists():
        print("ERROR: AIOS_MANUAL.md not found!")
        return 1
    
    print("=" * 70)
    print("ADDING ANCHOR IDS TO MANUAL HEADINGS")
    print("=" * 70)
    
    # Backup original
    print("\n1. Creating backup...")
    with open(manual_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(original_lines)
    print(f"   Backup saved: {backup_path}")
    print(f"   Original lines: {len(original_lines):,}")
    
    # Process manual
    print("\n2. Processing headings...")
    new_lines = []
    in_code_block = False
    in_toc = False
    added_anchors = 0
    skipped_anchors = 0
    
    for i, line in enumerate(original_lines, 1):
        line_stripped = line.rstrip()
        
        # Track code blocks
        if line_stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
        
        # Skip code blocks
        if in_code_block:
            new_lines.append(line)
            continue
        
        # Track TOC section (very specific bounds)
        if line_stripped == '## TABLE OF CONTENTS':
            in_toc = True
            new_lines.append(line)
            continue
        elif in_toc:
            # End TOC at first numbered section (# 1. Getting Started)
            if line_stripped.startswith('# ') and len(line_stripped) > 2 and line_stripped[2].isdigit():
                in_toc = False
                # Don't skip this line, process it
            else:
                # Skip TOC content
                new_lines.append(line)
                continue
        
        # Process headings (## and ### level only, skip # top-level)
        if line_stripped.startswith('## ') or line_stripped.startswith('### '):
            # Check if already has anchor
            if ' {#' in line_stripped:
                skipped_anchors += 1
                new_lines.append(line)
                continue
            
            # Determine heading level
            level = 2 if line_stripped.startswith('## ') else 3
            title = line_stripped[level+1:].strip()
            
            # Skip TABLE OF CONTENTS heading
            if 'TABLE OF CONTENTS' in title.upper():
                new_lines.append(line)
                continue
            
            # Extract section number if present
            section_match = re.match(r'^(\d+\.?\d*\.?\d*\.?\d*)\s+(.+)', title)
            if section_match:
                section_num = section_match.group(1)
                title_text = section_match.group(2)
            else:
                section_num = ""
                title_text = title
            
            # Generate anchor
            anchor = generate_anchor(title_text, section_num)
            
            # Create new heading with anchor
            heading_prefix = '#' * level
            new_heading = f"{heading_prefix} {title} {{#{anchor}}}\n"
            new_lines.append(new_heading)
            added_anchors += 1
            
            if added_anchors % 100 == 0:
                print(f"   Processed {added_anchors} headings...")
        else:
            new_lines.append(line)
    
    print(f"   Added anchors: {added_anchors}")
    print(f"   Skipped (already had): {skipped_anchors}")
    print(f"   Total headings: {added_anchors + skipped_anchors}")
    
    # Write updated manual
    print("\n3. Writing updated manual...")
    with open(manual_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"   Updated manual: {len(new_lines):,} lines")
    
    # Summary
    print("\n" + "=" * 70)
    print("ANCHOR IDS ADDED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Original: {len(original_lines):,} lines")
    print(f"  Updated: {len(new_lines):,} lines")
    print(f"  Anchors added: {added_anchors}")
    print(f"  Backup: {backup_path}")
    print(f"\nNext steps:")
    print(f"  1. Review changes: code AIOS_MANUAL.md")
    print(f"  2. Update TOC and RAG: py scripts/update_manual_complete.py")
    print(f"  3. Test search: py main.py --rag search 'test'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

