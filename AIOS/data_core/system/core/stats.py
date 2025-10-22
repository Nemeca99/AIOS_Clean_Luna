#!/usr/bin/env python3
"""
Statistics Module
Handles all statistics gathering for data core directories and files
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


def get_fractal_cache_stats(fractal_cache_dir: Path) -> Dict[str, Any]:
    """Get statistics about the FractalCache."""
    if not fractal_cache_dir.exists():
        return {'total_files': 0, 'total_size_mb': 0, 'files': []}
    
    files = []
    total_size = 0
    
    for file_path in fractal_cache_dir.glob("*.json"):
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            total_size += file_size
            
            # Try to read file metadata
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                files.append({
                    'name': file_path.name,
                    'size_bytes': file_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'content_type': data.get('specialization', 'unknown'),
                    'tags': data.get('tags', []),
                    'word_count': len(data.get('content', '').split()) if data.get('content') else 0
                })
            except Exception as e:
                files.append({
                    'name': file_path.name,
                    'size_bytes': file_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'content_type': 'corrupted',
                    'tags': [],
                    'word_count': 0
                })
                
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")
    
    return {
        'total_files': len(files),
        'total_size_mb': total_size / (1024 * 1024),
        'files': sorted(files, key=lambda x: x['modified'], reverse=True)
    }


def get_arbiter_cache_stats(arbiter_cache_dir: Path) -> Dict[str, Any]:
    """Get statistics about the ArbiterCache."""
    if not arbiter_cache_dir.exists():
        return {'total_files': 0, 'total_size_mb': 0, 'files': []}
    
    files = []
    total_size = 0
    
    for file_path in arbiter_cache_dir.glob("*.json"):
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            total_size += file_size
            
            files.append({
                'name': file_path.name,
                'size_bytes': file_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
                
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")
    
    return {
        'total_files': len(files),
        'total_size_mb': total_size / (1024 * 1024),
        'files': sorted(files, key=lambda x: x['modified'], reverse=True)
    }


def get_conversation_stats(conversations_dir: Path) -> Dict[str, Any]:
    """Get statistics about conversations."""
    if not conversations_dir.exists():
        return {'total_conversations': 0, 'total_size_mb': 0}
    
    conversations = list(conversations_dir.glob("*.json"))
    total_size = sum(f.stat().st_size for f in conversations)
    
    return {
        'total_conversations': len(conversations),
        'total_size_mb': total_size / (1024 * 1024),
        'latest_conversation': max(conversations, key=lambda x: x.stat().st_mtime).name if conversations else None
    }


def get_database_stats(database_dir: Path) -> Dict[str, Any]:
    """Get statistics about databases."""
    if not database_dir.exists():
        return {'databases': []}
    
    databases = []
    for db_file in database_dir.glob("*.db"):
        try:
            stat = db_file.stat()
            db_size = stat.st_size
            
            # Get table info
            tables = []
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
            except Exception as e:
                # Skip databases that can't be opened
                print(f"Warning: Could not read database {db_file}: {e}")
            
            databases.append({
                'name': db_file.name,
                'size_mb': db_size / (1024 * 1024),
                'tables': tables,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
            
        except Exception as e:
            print(f"⚠️ Error processing {db_file}: {e}")
    
    return {'databases': databases}


def get_system_overview(fractal_cache_dir: Path, arbiter_cache_dir: Path, 
                       conversations_dir: Path, database_dir: Path) -> Dict[str, Any]:
    """Get comprehensive system overview."""
    return {
        'fractal_cache': get_fractal_cache_stats(fractal_cache_dir),
        'arbiter_cache': get_arbiter_cache_stats(arbiter_cache_dir),
        'conversations': get_conversation_stats(conversations_dir),
        'databases': get_database_stats(database_dir),
        'timestamp': datetime.now().isoformat()
    }


def get_dir_stats(directory: Path) -> Dict[str, Any]:
    """Get statistics for a directory."""
    if not directory.exists():
        return {"total_files": 0, "total_size_mb": 0}
    
    files = list(directory.iterdir())
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    
    return {
        "total_files": len([f for f in files if f.is_file()]),
        "total_size_mb": total_size / (1024 * 1024)
    }

