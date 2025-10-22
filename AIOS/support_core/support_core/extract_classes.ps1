# PowerShell script to extract classes from support_core.py

$source = "support_core.py"
$outputDir = "core"

# Read the entire file
$content = Get-Content $source -Raw

# Define modules and their classes
$modules = @{
    "config" = @("AIOSConfigError", "AIOSConfig")
    "logger" = @("AIOSLoggerError", "AIOSLogger")
    "health_checker" = @("AIOSHealthError", "AIOSHealthChecker")
    "security" = @("AIOSSecurityValidator")
    "cache_operations" = @("CacheStatus", "CacheMetrics", "CacheOperations", "CacheRegistry", "CacheBackup")
    "embedding_operations" = @("EmbeddingStatus", "EmbeddingMetrics", "SimpleEmbedder", "EmbeddingCache", "FAISSOperations", "EmbeddingSimilarity")
    "recovery_operations" = @("RecoveryStatus", "RecoveryOperations", "SemanticReconstruction", "ProgressiveHealing", "RecoveryAssessment")
    "system_classes" = @("SystemConfig", "FilePaths", "SystemMessages")
}

# Common header for all modules
$header = @"
#!/usr/bin/env python3
"""
Support Core Module
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


"@

# Helper function to extract a class with its content
function Extract-Class {
    param(
        [string]$className,
        [string]$fileContent
    )
    
    # Find class definition
    $pattern = "(?ms)^class $className[\s\S]*?(?=^class |^def |^# ===|${'$'})"
    $matches = [regex]::Matches($fileContent, $pattern)
    
    if ($matches.Count -gt 0) {
        return $matches[0].Value.TrimEnd()
    }
    return $null
}

Write-Host "Starting class extraction from $source..."

foreach ($moduleName in $modules.Keys) {
    $outputFile = Join-Path $outputDir "$moduleName.py"
    $classes = $modules[$moduleName]
    
    Write-Host "Creating $outputFile with classes: $($classes -join ', ')"
    
    $moduleContent = $header
    
    foreach ($className in $classes) {
        Write-Host "  - Extracting $className..."
        $classContent = Extract-Class -className $className -fileContent $content
        
        if ($classContent) {
            $moduleContent += "`n`n$classContent"
        } else {
            Write-Host "    WARNING: Could not extract $className" -ForegroundColor Yellow
        }
    }
    
    # Write module file
    Set-Content -Path $outputFile -Value $moduleContent -Encoding UTF8
    Write-Host "  Created $outputFile" -ForegroundColor Green
}

Write-Host "`nExtraction complete!" -ForegroundColor Green

