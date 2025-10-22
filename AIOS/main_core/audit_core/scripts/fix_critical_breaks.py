#!/usr/bin/env python3
"""
Automated Fix Script - Critical Breaks
Fixes the 2 critical import/initialization bugs found in audit
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def fix_carma_analytics_import():
    """Fix CARMA analytics.py missing defaultdict import."""
    file_path = ROOT / "carma_core" / "core" / "analytics.py"
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already fixed
    if "from collections import defaultdict" in content:
        print(f"✓ {file_path.name} already has defaultdict import")
        return True
    
    # Check if defaultdict is used
    if "defaultdict" not in content:
        print(f"✓ {file_path.name} doesn't use defaultdict")
        return True
    
    # Find the import section and add the import
    lines = content.split('\n')
    insert_pos = 0
    
    # Find last import statement
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_pos = i + 1
        elif line.strip() and not line.startswith('#') and insert_pos > 0:
            break
    
    # Insert the import
    lines.insert(insert_pos, 'from collections import defaultdict')
    
    # Write back
    new_content = '\n'.join(lines)
    file_path.write_text(new_content, encoding='utf-8')
    
    print(f"✓ Fixed {file_path.name} - added defaultdict import at line {insert_pos + 1}")
    return True


def fix_fractal_safety_rails_init():
    """Fix Fractal safety_rails.py uninitialized self.conflicts_logged."""
    file_path = ROOT / "fractal_core" / "core" / "safety_rails.py"
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already fixed
    if "self.conflicts_logged = []" in content:
        print(f"✓ {file_path.name} already has conflicts_logged initialization")
        return True
    
    # Check if conflicts_logged is used
    if "self.conflicts_logged" not in content:
        print(f"✓ {file_path.name} doesn't use conflicts_logged")
        return True
    
    # Find the __init__ method and add initialization
    lines = content.split('\n')
    
    # Find __init__ method
    init_found = False
    insert_pos = None
    indent = ""
    
    for i, line in enumerate(lines):
        if "def __init__" in line:
            init_found = True
            # Find the indent level
            if line.startswith(' '):
                indent = line[:len(line) - len(line.lstrip())]
        elif init_found and line.strip().startswith("self."):
            # Found first self assignment, insert before it
            if insert_pos is None:
                insert_pos = i
    
    if not init_found:
        print(f"Warning: Could not find __init__ method in {file_path.name}")
        return False
    
    if insert_pos is None:
        # No self assignments found, insert after __init__ definition
        for i, line in enumerate(lines):
            if "def __init__" in line:
                insert_pos = i + 1
                break
    
    # Add the initialization
    lines.insert(insert_pos, f"{indent}        self.conflicts_logged = []")
    
    # Write back
    new_content = '\n'.join(lines)
    file_path.write_text(new_content, encoding='utf-8')
    
    print(f"✓ Fixed {file_path.name} - added conflicts_logged initialization at line {insert_pos + 1}")
    return True


def main():
    """Run all critical fixes."""
    print("=" * 60)
    print("FIXING CRITICAL BREAKS")
    print("=" * 60)
    
    fixes = [
        ("CARMA analytics.py", fix_carma_analytics_import),
        ("Fractal safety_rails.py", fix_fractal_safety_rails_init)
    ]
    
    fixed_count = 0
    failed_count = 0
    
    for name, fix_func in fixes:
        print(f"\nFixing: {name}")
        try:
            if fix_func():
                fixed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed_count += 1
    
    print("\n" + "=" * 60)
    print(f"Fixed: {fixed_count}/{len(fixes)}")
    print(f"Failed: {failed_count}/{len(fixes)}")
    print("=" * 60)
    
    if fixed_count == len(fixes):
        print("\n✅ All critical breaks fixed!")
        print("   Run: python main.py --audit to verify")
    
    return fixed_count == len(fixes)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

