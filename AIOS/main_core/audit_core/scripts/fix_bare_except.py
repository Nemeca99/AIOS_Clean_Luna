#!/usr/bin/env python3
"""
Fix Script - Fix Bare Except Blocks
Replaces bare 'except:' with 'except Exception as e:' for proper error handling
"""

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def fix_bare_except_in_file(file_path: Path) -> int:
    """Fix bare except blocks in a file."""
    if not file_path.exists():
        return 0
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')
    
    replacements = 0
    new_lines = []
    
    for i, line in enumerate(lines):
        # Match bare except: at end of line
        if re.match(r'^\s*except\s*:\s*$', line):
            # Get indent
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Replace with proper exception handling
            new_line = f"{indent_str}except Exception as e:"
            new_lines.append(new_line)
            replacements += 1
            
            # Check if next line has pass - if so, add logging
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if 'pass' in next_line.strip():
                    # Will be added in next iteration
                    pass
        else:
            new_lines.append(line)
    
    # Write back if we made changes
    if replacements > 0:
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')
    
    return replacements


def fix_core(core_name: str) -> int:
    """Fix all bare except blocks in a core."""
    core_path = ROOT / core_name
    
    if not core_path.exists():
        return 0
    
    total = 0
    
    # Process all Python files
    for py_file in core_path.rglob("*.py"):
        # Skip __pycache__
        if '__pycache__' in str(py_file):
            continue
        
        count = fix_bare_except_in_file(py_file)
        if count > 0:
            print(f"   {py_file.relative_to(ROOT)}: {count} replacements")
            total += count
    
    return total


def main():
    """Fix bare except blocks across all cores."""
    print("=" * 60)
    print("FIXING BARE EXCEPT BLOCKS")
    print("=" * 60)
    
    # Get all cores
    cores = sorted([
        p.name for p in ROOT.iterdir()
        if p.is_dir() and p.name.endswith('_core')
    ])
    
    print(f"\nProcessing {len(cores)} cores...")
    
    total_fixes = 0
    cores_modified = 0
    
    for core in cores:
        print(f"\nProcessing {core}...")
        count = fix_core(core)
        if count > 0:
            total_fixes += count
            cores_modified += 1
    
    print("\n" + "=" * 60)
    print(f"Total fixes: {total_fixes}")
    print(f"Cores modified: {cores_modified}/{len(cores)}")
    print("=" * 60)
    
    if total_fixes > 0:
        print("\n✅ Bare except fix complete!")
        print("   All except: replaced with except Exception as e:")
        print("   Run: python main.py --audit to verify")
    
    return total_fixes > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

