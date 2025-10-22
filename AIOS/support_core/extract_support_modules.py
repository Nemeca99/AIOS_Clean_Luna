#!/usr/bin/env python3
"""
Comprehensive extraction script for support_core refactor.
Extracts all classes from the monolithic support_core.py into separate modules.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

def extract_section_between_markers(content: str, start_marker: str, end_marker: str) -> str:
    """Extract content between two comment markers."""
    pattern = f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def extract_classes_by_pattern(content: str, class_names: List[str]) -> str:
    """Extract specified classes from content."""
    extracted = []
    lines = content.split('\n')
    
    for class_name in class_names:
        in_class = False
        class_lines = []
        indent_level = None
        
        for i, line in enumerate(lines):
            # Found the class definition
            if re.match(f'^class {re.escape(class_name)}', line):
                in_class = True
                class_lines.append(line)
                indent_level = 0
                continue
            
            if in_class:
                # Check if we've reached the end of the class
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    # New top-level definition, end of class
                    break
                
                class_lines.append(line)
        
        if class_lines:
            extracted.append('\n'.join(class_lines))
    
    return '\n\n'.join(extracted)

def create_module_header(module_name: str) -> str:
    """Create standard header for extracted modules."""
    return f'''#!/usr/bin/env python3
"""
Support Core - {module_name.replace('_', ' ').title()}
Extracted from monolithic support_core.py for better modularity.
"""

import sys
from pathlib import Path
import time
import json
import os
import shutil
import re
import hashlib
import math
import random
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
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

def main():
    """Main extraction process."""
    print("="*60)
    print("Support Core Module Extraction")
    print("="*60)
    
    # Read source file
    source_path = Path("support_core.py")
    if not source_path.exists():
        print(f"ERROR: Source file not found: {source_path}")
        return
    
    print(f"\nReading source file: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Source file size: {len(content)} characters")
    
    # Define extraction mappings (comment markers in the source)
    extractions = {
        'logger': {
            'start': '# === UNIFIED LOGGING SYSTEM ===',
            'end': '# === HEALTH CHECK SYSTEM ===',
            'classes': ['AIOSLoggerError', 'AIOSLogger']
        },
        'health_checker': {
            'start': '# === HEALTH CHECK SYSTEM ===',
            'end': '# === SECURITY VALIDATOR ===',
            'classes': ['AIOSHealthError', 'AIOSHealthChecker']
        },
        'security': {
            'start': '# === SECURITY VALIDATOR ===',
            'end': '# === CACHE OPERATIONS ===',
            'classes': ['AIOSSecurityValidator']
        },
        'cache_operations': {
            'start': '# === CACHE OPERATIONS ===',
            'end': '# === EMBEDDING OPERATIONS ===',
            'classes': ['CacheStatus', 'CacheMetrics', 'CacheOperations', 'CacheRegistry', 'CacheBackup']
        },
        'embedding_operations': {
            'start': '# === EMBEDDING OPERATIONS ===',
            'end': '# === RECOVERY OPERATIONS ===',
            'classes': ['EmbeddingStatus', 'EmbeddingMetrics', 'SimpleEmbedder', 'EmbeddingCache', 'FAISSOperations', 'EmbeddingSimilarity']
        },
        'recovery_operations': {
            'start': '# === RECOVERY OPERATIONS ===',
            'end': '# === SYSTEM CONFIGURATION ===',
            'classes': ['RecoveryStatus', 'RecoveryOperations', 'SemanticReconstruction', 'ProgressiveHealing', 'RecoveryAssessment']
        },
        'system_classes': {
            'start': '# === SYSTEM CONFIGURATION ===',
            'end': '# === SUPPORT SYSTEM ===',
            'classes': ['SystemConfig', 'FilePaths', 'SystemMessages']
        },
    }
    
    # Create core directory
    core_dir = Path("core")
    core_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nCore directory: {core_dir}")
    
    # Extract each module
    for module_name, config in extractions.items():
        print(f"\n{'='*60}")
        print(f"Processing: {module_name}")
        print(f"{'='*60}")
        
        # Extract section
        section_content = extract_section_between_markers(
            content, config['start'], config['end']
        )
        
        if not section_content:
            print(f"  WARNING: Could not find section markers for {module_name}")
            # Try to extract by class names directly
            section_content = extract_classes_by_pattern(content, config['classes'])
        
        if section_content:
            # Create module file
            module_path = core_dir / f"{module_name}.py"
            module_content = create_module_header(module_name) + '\n\n' + section_content + '\n'
            
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(module_content)
            
            print(f"  ✓ Created: {module_path}")
            print(f"    Size: {len(module_content)} characters")
            print(f"    Classes: {', '.join(config['classes'])}")
        else:
            print(f"  ✗ Failed to extract {module_name}")
    
    # Config already created manually, skip it
    print(f"\n{'='*60}")
    print("Module extraction complete!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Create core/__init__.py")
    print("2. Review extracted modules")
    print("3. Update main support_core.py")

if __name__ == "__main__":
    main()

