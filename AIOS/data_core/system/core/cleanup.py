#!/usr/bin/env python3
"""
Cleanup Module
Handles data cleanup, maintenance, and export operations
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


def cleanup_old_data(fractal_cache_dir: Path, arbiter_cache_dir: Path, 
                    conversations_dir: Path, days_old: int = 30, 
                    dry_run: bool = True) -> Dict[str, Any]:
    """
    Clean up old data files.
    
    Args:
        days_old: Delete files older than this many days
        dry_run: If True, only report what would be deleted
        
    Returns:
        Dictionary with cleanup results
    """
    cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
    
    cleanup_results = {
        'fractal_cache': {'deleted': 0, 'size_freed_mb': 0},
        'arbiter_cache': {'deleted': 0, 'size_freed_mb': 0},
        'conversations': {'deleted': 0, 'size_freed_mb': 0},
        'total_deleted': 0,
        'total_size_freed_mb': 0
    }
    
    # Clean FractalCache
    if fractal_cache_dir.exists():
        for file_path in fractal_cache_dir.glob("*.json"):
            if file_path.stat().st_mtime < cutoff_time:
                file_size = file_path.stat().st_size
                if not dry_run:
                    file_path.unlink()
                cleanup_results['fractal_cache']['deleted'] += 1
                cleanup_results['fractal_cache']['size_freed_mb'] += file_size / (1024 * 1024)
    
    # Clean ArbiterCache
    if arbiter_cache_dir.exists():
        for file_path in arbiter_cache_dir.glob("*.json"):
            if file_path.stat().st_mtime < cutoff_time:
                file_size = file_path.stat().st_size
                if not dry_run:
                    file_path.unlink()
                cleanup_results['arbiter_cache']['deleted'] += 1
                cleanup_results['arbiter_cache']['size_freed_mb'] += file_size / (1024 * 1024)
    
    # Clean old conversations
    if conversations_dir.exists():
        for file_path in conversations_dir.glob("*.json"):
            if file_path.stat().st_mtime < cutoff_time:
                file_size = file_path.stat().st_size
                if not dry_run:
                    file_path.unlink()
                cleanup_results['conversations']['deleted'] += 1
                cleanup_results['conversations']['size_freed_mb'] += file_size / (1024 * 1024)
    
    cleanup_results['total_deleted'] = (
        cleanup_results['fractal_cache']['deleted'] +
        cleanup_results['arbiter_cache']['deleted'] +
        cleanup_results['conversations']['deleted']
    )
    
    cleanup_results['total_size_freed_mb'] = (
        cleanup_results['fractal_cache']['size_freed_mb'] +
        cleanup_results['arbiter_cache']['size_freed_mb'] +
        cleanup_results['conversations']['size_freed_mb']
    )
    
    action = "Would delete" if dry_run else "Deleted"
    print(f"🗑️ {action} {cleanup_results['total_deleted']} files ({cleanup_results['total_size_freed_mb']:.1f} MB)")
    
    return cleanup_results


def export_to_json(source_dir: Path, export_path: Path, filter_criteria: Dict[str, Any] = None):
    """Export data to JSON format."""
    data_list = []
    
    for file_path in source_dir.glob("*"):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if matches_filter(data, filter_criteria):
                        data_list.append(data)
            except (IOError, json.JSONDecodeError) as e:
                # Skip files that can't be read or have invalid JSON
                print(f"Warning: Skipping {file_path.name}: {e}")
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=2, default=str)


def export_to_csv(source_dir: Path, export_path: Path, filter_criteria: Dict[str, Any] = None):
    """Export data to CSV format."""
    all_data = []
    for file_path in source_dir.glob("*"):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if matches_filter(data, filter_criteria):
                        all_data.append(data)
            except (IOError, json.JSONDecodeError) as e:
                # Skip files that can't be read or have invalid JSON
                print(f"Warning: Skipping {file_path.name} during CSV export: {e}")
    
    if all_data:
        fieldnames = set()
        for item in all_data:
            if isinstance(item, dict):
                fieldnames.update(item.keys())
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(fieldnames))
            writer.writeheader()
            for item in all_data:
                if isinstance(item, dict):
                    writer.writerow(item)


def export_to_text(source_dir: Path, export_path: Path, filter_criteria: Dict[str, Any] = None):
    """Export data to text format."""
    with open(export_path, 'w', encoding='utf-8') as f:
        for file_path in source_dir.glob("*"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as source_f:
                        content = source_f.read()
                        f.write(f"=== {file_path.name} ===\n")
                        f.write(content)
                        f.write("\n\n")
                except (IOError, OSError, UnicodeDecodeError) as e:
                    # Skip files that can't be read
                    print(f"Warning: Could not read {file_path.name}: {e}")


def matches_filter(data: Any, filter_criteria: Dict[str, Any] = None) -> bool:
    """Check if data matches filter criteria."""
    if not filter_criteria:
        return True
    
    if not isinstance(data, dict):
        return False
    
    for key, value in filter_criteria.items():
        if key not in data or data[key] != value:
            return False
    
    return True

