#!/usr/bin/env python3
"""
Script to extract classes from support_core.py into separate modules.
This automates the refactoring process.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

def read_file_content(file_path: str) -> str:
    """Read entire file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def find_class_ranges(content: str) -> Dict[str, Tuple[int, int]]:
    """Find start and end line numbers for each class."""
    lines = content.split('\n')
    class_ranges = {}
    current_class = None
    class_start = 0
    base_indent = 0
    
    for i, line in enumerate(lines, 1):
        # Check if this is a class definition
        if re.match(r'^class \w+', line):
            # Save previous class if exists
            if current_class:
                class_ranges[current_class] = (class_start, i - 1)
            
            # Extract class name
            match = re.match(r'^class (\w+)', line)
            current_class = match.group(1)
            class_start = i
            base_indent = 0
        
        # Check if we're at a new top-level definition (end of class)
        elif current_class and re.match(r'^(class |def |# ===|$)', line):
            if line.strip() and not line.startswith(' '):
                class_ranges[current_class] = (class_start, i - 1)
                current_class = None
    
    # Don't forget the last class
    if current_class:
        class_ranges[current_class] = (class_start, len(lines))
    
    return class_ranges

def extract_class_content(content: str, start_line: int, end_line: int) -> str:
    """Extract lines for a class including docstrings and methods."""
    lines = content.split('\n')
    return '\n'.join(lines[start_line-1:end_line])

def get_class_imports(content: str, class_name: str, class_content: str) -> List[str]:
    """Determine which imports a class needs based on its content."""
    # Get all imports from original file
    lines = content.split('\n')
    all_imports = []
    
    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            if 'unicode_safe_output' not in line:  # Skip unicode import for now
                all_imports.append(line)
            if line.startswith('# ==='):  # Stop at first section marker
                break
    
    # Filter imports based on what's actually used in the class
    needed_imports = []
    for imp in all_imports:
        # Extract module names from import
        if 'import ' in imp:
            parts = imp.split('import')[1].split(',')
            for part in parts:
                module = part.strip().split(' as ')[0].strip()
                if module in class_content:
                    needed_imports.append(imp)
                    break
    
    return needed_imports

def create_module_file(output_dir: Path, module_name: str, classes: List[str], 
                       content: str, class_ranges: Dict[str, Tuple[int, int]]):
    """Create a module file with specified classes."""
    output_file = output_dir / f"{module_name}.py"
    
    # Header
    header = f'''#!/usr/bin/env python3
"""
Support Core - {module_name.replace('_', ' ').title()}
Extracted from monolithic support_core.py for better modularity.
"""

import sys
from pathlib import Path
import time
import json
import os
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup Unicode safety
try:
    from utils_core.unicode_safe_output import setup_unicode_safe_output
    setup_unicode_safe_output()
except ImportError:
    print("Warning: Unicode safety layer not available")

'''
    
    # Extract classes
    class_contents = []
    for class_name in classes:
        if class_name in class_ranges:
            start, end = class_ranges[class_name]
            class_content = extract_class_content(content, start, end)
            class_contents.append(class_content)
    
    # Combine
    full_content = header + '\n\n'.join(class_contents) + '\n'
    
    # Write file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"Created {output_file}")

def main():
    """Main extraction process."""
    # Read source file
    source_file = Path('support_core.py')
    content = read_file_content(source_file)
    
    # Find all class ranges
    class_ranges = find_class_ranges(content)
    
    print(f"Found {len(class_ranges)} classes:")
    for class_name, (start, end) in class_ranges.items():
        print(f"  - {class_name}: lines {start}-{end}")
    
    # Create core directory
    core_dir = Path('core')
    core_dir.mkdir(exist_ok=True)
    
    # Module definitions (class names to extract for each module)
    modules = {
        'config': ['AIOSConfigError', 'AIOSConfig'],
        'logger': ['AIOSLoggerError', 'AIOSLogger'],
        'health_checker': ['AIOSHealthError', 'AIOSHealthChecker'],
        'security': ['AIOSSecurityValidator'],
        'cache_operations': ['CacheStatus', 'CacheMetrics', 'CacheOperations', 'CacheRegistry', 'CacheBackup'],
        'embedding_operations': ['EmbeddingStatus', 'EmbeddingMetrics', 'SimpleEmbedder', 'EmbeddingCache', 'FAISSOperations', 'EmbeddingSimilarity'],
        'recovery_operations': ['RecoveryStatus', 'RecoveryOperations', 'SemanticReconstruction', 'ProgressiveHealing', 'RecoveryAssessment'],
        'system_classes': ['SystemConfig', 'FilePaths', 'SystemMessages'],
    }
    
    # Create each module
    for module_name, class_list in modules.items():
        print(f"\nCreating {module_name}.py...")
        create_module_file(core_dir, module_name, class_list, content, class_ranges)
    
    print("\nExtraction complete!")
    print("\nNext steps:")
    print("1. Review extracted modules for any missing dependencies")
    print("2. Create core/__init__.py to export classes")
    print("3. Refactor main support_core.py to use extracted modules")

if __name__ == "__main__":
    main()

