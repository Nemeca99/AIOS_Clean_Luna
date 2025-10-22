#!/usr/bin/env python3
"""
Database Module
Handles database operations and information retrieval
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


def get_database_info(database_dir: Path) -> Dict[str, Any]:
    """
    Get detailed information about all databases in the database directory.
    
    Args:
        database_dir: Path to database directory
        
    Returns:
        Dictionary containing database information
    """
    if not database_dir.exists():
        return {'databases': [], 'total_count': 0, 'total_size_mb': 0}
    
    databases = []
    total_size = 0
    
    for db_file in database_dir.glob("*.db"):
        try:
            stat = db_file.stat()
            db_size = stat.st_size
            total_size += db_size
            
            # Get table info
            tables = []
            table_info = {}
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get row count for each table
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table};")
                        count = cursor.fetchone()[0]
                        table_info[table] = {'row_count': count}
                    except Exception as e:
                        table_info[table] = {'row_count': 'unknown'}
                
                conn.close()
            except Exception as e:
                print(f"⚠️ Could not read database {db_file.name}: {e}")
            
            databases.append({
                'name': db_file.name,
                'path': str(db_file),
                'size_bytes': db_size,
                'size_mb': db_size / (1024 * 1024),
                'tables': tables,
                'table_info': table_info,
                'table_count': len(tables),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
            
        except Exception as e:
            print(f"⚠️ Error processing database {db_file}: {e}")
    
    return {
        'databases': databases,
        'total_count': len(databases),
        'total_size_mb': total_size / (1024 * 1024)
    }

