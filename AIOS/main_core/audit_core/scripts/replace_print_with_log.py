#!/usr/bin/env python3
"""
Fix Script - Replace Print with Proper Logging
Replaces print() statements in production code with proper logging
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[3]


def should_replace_print(line: str, file_path: Path) -> bool:
    """Determine if a print statement should be replaced."""
    # Skip test files
    if "test" in str(file_path).lower():
        return False
    
    # Skip if already commented out
    if line.strip().startswith('#'):
        return False
    
    # Skip if in docstring
    if '"""' in line or "'''" in line:
        return False
    
    # Skip debug prints (keep for now)
    if "DEBUG" in line or "debug" in line.lower():
        return False
    
    # Skip main.py bootstrap messages (user-facing)
    if "main.py" in str(file_path):
        return False
    
    # Skip __main__ test blocks
    if 'if __name__ == "__main__"' in line:
        return False
    
    return True


def replace_prints_in_file(file_path: Path) -> int:
    """Replace print statements in a single file with logging."""
    if not file_path.exists():
        return 0
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')
    
    # Check if logging already imported
    has_logging = any('import logging' in line for line in lines[:50])
    has_logger = any('logger =' in line or 'self.logger' in line for line in lines)
    
    # If file uses support_core logger, skip
    if 'from support_core' in content and 'aios_logger' in content:
        return 0
    
    replacements = 0
    new_lines = []
    in_main_block = False
    
    for i, line in enumerate(lines):
        # Track if we're in __main__ block
        if 'if __name__ == "__main__"' in line:
            in_main_block = True
        
        # Check for print statements
        if 'print(' in line and not in_main_block:
            if should_replace_print(line, file_path):
                # Extract indent
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Extract print content
                print_match = re.search(r'print\s*\((.*)\)', line)
                if print_match:
                    print_content = print_match.group(1)
                    
                    # Determine log level from content
                    content_lower = print_content.lower()
                    if any(word in content_lower for word in ['error', 'failed', 'crash']):
                        level = 'error'
                    elif any(word in content_lower for word in ['warning', 'warn']):
                        level = 'warning'
                    elif any(word in content_lower for word in ['debug', 'trace']):
                        level = 'debug'
                    else:
                        level = 'info'
                    
                    # Replace with logging
                    if has_logger or 'self.logger' in content:
                        new_line = f"{indent_str}self.logger.{level}({print_content})"
                    else:
                        new_line = f"{indent_str}logging.{level}({print_content})"
                    
                    new_lines.append(new_line)
                    replacements += 1
                    continue
        
        new_lines.append(line)
    
    # Add logging import if we made replacements and it's not there
    if replacements > 0 and not has_logging and not has_logger:
        # Find import section
        import_end = 0
        for i, line in enumerate(new_lines):
            if line.startswith('import ') or line.startswith('from '):
                import_end = i + 1
        
        new_lines.insert(import_end, 'import logging')
    
    # Write back if we made changes
    if replacements > 0:
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')
    
    return replacements


def fix_core(core_name: str) -> int:
    """Fix all print statements in a core."""
    core_path = ROOT / core_name
    
    if not core_path.exists():
        return 0
    
    total = 0
    
    # Process all Python files
    for py_file in core_path.rglob("*.py"):
        # Skip __pycache__ and test files
        if '__pycache__' in str(py_file) or 'test' in str(py_file):
            continue
        
        count = replace_prints_in_file(py_file)
        if count > 0:
            print(f"   {py_file.relative_to(ROOT)}: {count} replacements")
            total += count
    
    return total


def main():
    """Replace print with logging across all cores."""
    print("=" * 60)
    print("REPLACING PRINT WITH PROPER LOGGING")
    print("=" * 60)
    
    # Get all cores
    cores = sorted([
        p.name for p in ROOT.iterdir()
        if p.is_dir() and p.name.endswith('_core')
    ])
    
    print(f"\nProcessing {len(cores)} cores...")
    
    total_replacements = 0
    cores_modified = 0
    
    for core in cores:
        print(f"\nProcessing {core}...")
        count = fix_core(core)
        if count > 0:
            total_replacements += count
            cores_modified += 1
    
    print("\n" + "=" * 60)
    print(f"Total replacements: {total_replacements}")
    print(f"Cores modified: {cores_modified}/{len(cores)}")
    print("=" * 60)
    
    if total_replacements > 0:
        print("\n✅ Print-to-log migration complete!")
        print("   Run: python main.py --audit to verify improvement")
    
    return total_replacements > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

