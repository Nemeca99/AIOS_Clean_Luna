#!/usr/bin/env python3
"""
Script to automatically refactor carma_core.py into modular components
"""

import re
from pathlib import Path

# Define class extraction ranges (line numbers)
class_extractions = {
    'core/fractal_cache.py': {
        'start': 96,
        'end': 1135,
        'classes': ['FractalMyceliumCache'],
        'needs_imports': [
            'import sys',
            'from pathlib import Path',
            'import time',
            'import json',
            'import random',
            'import hashlib',
            'import numpy as np',
            'from typing import Dict, List, Optional',
            'from datetime import datetime',
            '',
            'sys.path.append(str(Path(__file__).parent.parent.parent))',
            'from support_core.support_core import SystemConfig, SimpleEmbedder',
        ]
    },
    'core/executive_brain.py': {
        'start': 1138,
        'end': 1398,
        'classes': ['CARMAExecutiveBrain'],
        'needs_imports': [
            'import sys',
            'from pathlib import Path',
            'import time',
            'import random',
            'import uuid',
            'from typing import Dict, List, Optional',
            'from datetime import datetime',
            '',
            'sys.path.append(str(Path(__file__).parent.parent.parent))',
            'from support_core.support_core import SystemConfig',
        ]
    },
    'core/meta_memory.py': {
        'start': 1401,
        'end': 1486,
        'classes': ['CARMAMetaMemory'],
        'needs_imports': [
            'import sys',
            'from pathlib import Path',
            'import time',
            'import uuid',
            'from typing import Dict, List',
            '',
            'sys.path.append(str(Path(__file__).parent.parent.parent))',
            'from support_core.support_core import SystemConfig',
        ]
    },
    'core/performance.py': {
        'start': 1489,
        'end': 1668,
        'classes': ['CARMA100PercentPerformance'],
        'needs_imports': [
            'import sys',
            'from pathlib import Path',
            'import time',
            'import math',
            'import uuid',
            'from typing import Dict',
            'from datetime import datetime',
            '',
            'sys.path.append(str(Path(__file__).parent.parent.parent))',
            'from support_core.support_core import SystemConfig',
        ]
    },
    'core/compressor.py': {
        'start': 2087,
        'end': 2238,
        'classes': ['CARMAMemoryCompressor'],
        'needs_imports': [
            'import time',
            'from typing import Dict, List',
        ]
    },
    'core/clusterer.py': {
        'start': 2240,
        'end': 2376,
        'classes': ['CARMAMemoryClusterer'],
        'needs_imports': [
            'import numpy as np',
            'from typing import Dict, List',
        ]
    },
    'core/analytics.py': {
        'start': 2378,
        'end': 2505,
        'classes': ['CARMAMemoryAnalytics'],
        'needs_imports': [
            'from typing import Dict, List',
            'from datetime import datetime',
        ]
    },
}

def extract_class(source_file, start_line, end_line, output_file, imports_list, header_comment):
    """Extract a class from source file and save to output file"""
    
    # Read source file
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract the class (line numbers are 1-indexed, list is 0-indexed)
    extracted_lines = lines[start_line-1:end_line]
    
    # Create output content
    output_lines = [
        '#!/usr/bin/env python3\n',
        '"""\n',
        header_comment + '\n',
        '"""\n',
        '\n',
    ]
    
    # Add imports
    for imp in imports_list:
        output_lines.append(imp + '\n')
    
    output_lines.append('\n\n')
    
    # Add extracted class
    output_lines.extend(extracted_lines)
    
    # Write to output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"✓ Extracted to {output_file}")

def main():
    source_file = 'carma_core.py'
    
    print("=" * 70)
    print("CARMA Core Refactor Script")
    print("=" * 70)
    
    # Extract FractalMyceliumCache
    extract_class(
        source_file,
        96, 1135,
        'core/fractal_cache.py',
        class_extractions['core/fractal_cache.py']['needs_imports'],
        'CARMA Fractal Mycelium Cache\nFractal cache with Psycho-Semantic RAG Loop integration'
    )
    
    # Extract CARMAExecutiveBrain
    extract_class(
        source_file,
        1138, 1398,
        'core/executive_brain.py',
        class_extractions['core/executive_brain.py']['needs_imports'],
        'CARMA Executive Brain\nAutonomous goal generation and execution system'
    )
    
    # Extract CARMAMetaMemory
    extract_class(
        source_file,
        1401, 1486,
        'core/meta_memory.py',
        class_extractions['core/meta_memory.py']['needs_imports'],
        'CARMA Meta Memory\nHierarchical memory management system'
    )
    
    # Extract CARMA100PercentPerformance
    extract_class(
        source_file,
        1489, 1668,
        'core/performance.py',
        class_extractions['core/performance.py']['needs_imports'],
        'CARMA 100% Performance System\nPerformance optimization and dream cycle management'
    )
    
    # Extract CARMAMemoryCompressor
    extract_class(
        source_file,
        2087, 2238,
        'core/compressor.py',
        class_extractions['core/compressor.py']['needs_imports'],
        'CARMA Memory Compressor\nAdvanced memory compression system'
    )
    
    # Extract CARMAMemoryClusterer
    extract_class(
        source_file,
        2240, 2376,
        'core/clusterer.py',
        class_extractions['core/clusterer.py']['needs_imports'],
        'CARMA Memory Clusterer\nMemory clustering system for organizing fragments'
    )
    
    # Extract CARMAMemoryAnalytics
    extract_class(
        source_file,
        2378, 2505,
        'core/analytics.py',
        class_extractions['core/analytics.py']['needs_imports'],
        'CARMA Memory Analytics\nMemory analytics system for insights'
    )
    
    print("\n" + "=" * 70)
    print("Core component extraction complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()

