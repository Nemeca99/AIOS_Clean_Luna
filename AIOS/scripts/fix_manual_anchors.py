#!/usr/bin/env python3
"""
Add anchors to ALL numbered sections in the manual
Skips only the inline TOC (lines 1-250)
"""

import re
from pathlib import Path

manual_path = Path("AIOS_MANUAL.md")
backup_path = Path("AIOS_MANUAL.md.backup")

# Read manual
with open(manual_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Backup
with open(backup_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Backup created: {backup_path}")
print(f"Processing {len(lines):,} lines...")

new_lines = []
in_code_block = False
added = 0
skipped = 0

for i, line in enumerate(lines, 1):
    stripped = line.rstrip()
    
    # Track code blocks
    if stripped.startswith('```'):
        in_code_block = not in_code_block
        new_lines.append(line)
        continue
    
    if in_code_block:
        new_lines.append(line)
        continue
    
    # Skip inline TOC (lines 1-250)
    if i <= 250:
        new_lines.append(line)
        continue
    
    # Process ALL ## and ### headings (numbered or not)
    if (stripped.startswith('## ') or stripped.startswith('### ')) and not ' {#' in stripped:
        # Extract level and title
        if stripped.startswith('### '):
            level = 3
            title = stripped[4:].strip()
        else:
            level = 2
            title = stripped[3:].strip()
        
        # Process ALL headings (not just numbered)
        if True:  # Changed from: if re.match(r'^\d+\.', title):
            # Generate anchor from title
            # e.g., "1.1 What is AIOS?" → "section.11.what.is.aios"
            # e.g., "Installation" → "installation"
            
            # Check if numbered
            section_match = re.match(r'^(\d+\.\d+\.?\d*\.?\d*)', title)
            if section_match:
                section_num = section_match.group(1)
                section_clean = section_num.replace('.', '')
            else:
                section_clean = ''
            
            title_text = re.sub(r'^\d+\.\d+\.?\d*\.?\d*\s*', '', title)
            anchor_text = title_text.lower()
            anchor_text = re.sub(r'[^\w\s-]', '', anchor_text)
            anchor_text = re.sub(r'[-\s]+', '.', anchor_text).strip('.')
            
            # Build anchor (handle numbered and non-numbered)
            if section_clean:
                anchor = f"section.{section_clean}.{anchor_text}"
            else:
                anchor = anchor_text
            
            # Create new heading
            prefix = '#' * level
            new_line = f"{prefix} {title} {{#{anchor}}}\n"
            new_lines.append(new_line)
            added += 1
            
            if added % 50 == 0:
                print(f"  Processed {added} sections...")
        else:
            new_lines.append(line)
    elif ' {#' in stripped:
        skipped += 1
        new_lines.append(line)
    else:
        new_lines.append(line)

# Write
with open(manual_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\nComplete!")
print(f"  Added: {added} anchors")
print(f"  Skipped: {skipped} (already had)")
print(f"  Total: {added + skipped}")
print(f"\nNow run: py scripts/update_manual_complete.py")

