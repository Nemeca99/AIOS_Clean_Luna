#!/usr/bin/env python3
"""
Pipeline Module
Handles data ingestion, export, and pipeline metrics tracking
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .stats import get_dir_stats


def load_pipeline_stats(data_dir: Path) -> Dict[str, Any]:
    """Load data pipeline statistics."""
    stats_file = data_dir / "pipeline_stats.json"
    if stats_file.exists():
        try:
            with open(stats_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Stats file doesn't exist yet or is corrupted - return defaults
            print(f"Note: Pipeline stats not found, using defaults: {e}")
    return {
        "total_operations": 0,
        "data_ingested": 0,
        "data_processed": 0,
        "data_exported": 0,
        "pipeline_uptime": datetime.now().isoformat(),
        "last_operation": None
    }


def save_pipeline_stats(data_dir: Path, pipeline_stats: Dict[str, Any]):
    """Save data pipeline statistics."""
    stats_file = data_dir / "pipeline_stats.json"
    try:
        with open(stats_file, 'w') as f:
            json.dump(pipeline_stats, f, indent=2)
    except Exception as e:
        print(f"⚠️ Warning: Could not save pipeline stats: {e}")


def load_data_registry(data_dir: Path) -> Dict[str, Any]:
    """Load data registry for tracking all data operations."""
    registry_file = data_dir / "data_registry.json"
    if registry_file.exists():
        try:
            with open(registry_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Registry doesn't exist yet or is corrupted - return empty
            print(f"Note: Pipeline registry not found, using defaults: {e}")
    return {"data_sources": {}, "data_sinks": {}, "data_transforms": {}}


def save_data_registry(data_dir: Path, data_registry: Dict[str, Any]):
    """Save data registry."""
    registry_file = data_dir / "data_registry.json"
    try:
        with open(registry_file, 'w') as f:
            json.dump(data_registry, f, indent=2)
    except Exception as e:
        print(f"⚠️ Warning: Could not save data registry: {e}")


def ingest_data(data: Any, source: str, data_type: str, data_dir: Path,
                fractal_cache_dir: Path, arbiter_cache_dir: Path, 
                conversations_dir: Path, logs_dir: Path, temp_dir: Path,
                pipeline_stats: Dict[str, Any], data_registry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest data into the AIOS data pipeline.
    
    Args:
        data: Data to ingest
        source: Source system/core
        data_type: Type of data
        
    Returns:
        Ingestion results
    """
    ingestion_id = f"ING_{int(time.time())}_{hash(str(data)) % 10000:04d}"
    
    result = {
        "ingestion_id": ingestion_id,
        "source": source,
        "data_type": data_type,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "storage_path": None,
        "error": None
    }
    
    try:
        # Store data in appropriate location
        if data_type == "fragment":
            storage_path = fractal_cache_dir / f"{ingestion_id}.json"
        elif data_type == "arbiter":
            storage_path = arbiter_cache_dir / f"{ingestion_id}.json"
        elif data_type == "conversation":
            storage_path = conversations_dir / f"{ingestion_id}.json"
        elif data_type == "log":
            storage_path = logs_dir / f"{ingestion_id}.log"
        else:
            storage_path = temp_dir / f"{ingestion_id}.json"
        
        # Write data
        with open(storage_path, 'w', encoding='utf-8') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2, default=str)
            else:
                f.write(str(data))
        
        result["success"] = True
        result["storage_path"] = str(storage_path)
        
        # Update pipeline stats
        pipeline_stats["total_operations"] += 1
        pipeline_stats["data_ingested"] += 1
        pipeline_stats["last_operation"] = datetime.now().isoformat()
        save_pipeline_stats(data_dir, pipeline_stats)
        
        # Update data registry
        if source not in data_registry["data_sources"]:
            data_registry["data_sources"][source] = {"count": 0, "last_ingestion": None}
        data_registry["data_sources"][source]["count"] += 1
        data_registry["data_sources"][source]["last_ingestion"] = datetime.now().isoformat()
        save_data_registry(data_dir, data_registry)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def export_data(data_type: str, target_format: str, filter_criteria: Dict[str, Any],
                data_dir: Path, fractal_cache_dir: Path, arbiter_cache_dir: Path,
                conversations_dir: Path, logs_dir: Path, temp_dir: Path, exports_dir: Path,
                pipeline_stats: Dict[str, Any],
                export_to_json_func, export_to_csv_func, export_to_text_func) -> Dict[str, Any]:
    """
    Export data from the AIOS data pipeline.
    
    Args:
        data_type: Type of data to export
        target_format: Export format (json, csv, txt)
        filter_criteria: Criteria to filter data
        
    Returns:
        Export results
    """
    export_id = f"EXP_{int(time.time())}_{os.urandom(4).hex()[:4]}"
    
    result = {
        "export_id": export_id,
        "data_type": data_type,
        "format": target_format,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "export_path": None,
        "records_exported": 0,
        "error": None
    }
    
    try:
        # Determine source directory
        if data_type == "fragment":
            source_dir = fractal_cache_dir
        elif data_type == "arbiter":
            source_dir = arbiter_cache_dir
        elif data_type == "conversation":
            source_dir = conversations_dir
        elif data_type == "log":
            source_dir = logs_dir
        else:
            source_dir = temp_dir
        
        # Create export file
        export_path = exports_dir / f"{export_id}.{target_format}"
        
        # Export data based on format
        if target_format == "json":
            export_to_json_func(source_dir, export_path, filter_criteria)
        elif target_format == "csv":
            export_to_csv_func(source_dir, export_path, filter_criteria)
        else:
            export_to_text_func(source_dir, export_path, filter_criteria)
        
        result["success"] = True
        result["export_path"] = str(export_path)
        
        # Update pipeline stats
        pipeline_stats["total_operations"] += 1
        pipeline_stats["data_exported"] += 1
        pipeline_stats["last_operation"] = datetime.now().isoformat()
        save_pipeline_stats(data_dir, pipeline_stats)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def get_pipeline_metrics(data_dir: Path, fractal_cache_dir: Path, arbiter_cache_dir: Path,
                        conversations_dir: Path, logs_dir: Path, temp_dir: Path, 
                        exports_dir: Path, pipeline_stats: Dict[str, Any], 
                        data_registry: Dict[str, Any]) -> Dict[str, Any]:
    """Get comprehensive data pipeline metrics."""
    return {
        "pipeline_stats": pipeline_stats,
        "data_registry": data_registry,
        "directory_stats": {
            "fractal_cache": get_dir_stats(fractal_cache_dir),
            "arbiter_cache": get_dir_stats(arbiter_cache_dir),
            "conversations": get_dir_stats(conversations_dir),
            "logs": get_dir_stats(logs_dir),
            "temp": get_dir_stats(temp_dir),
            "exports": get_dir_stats(exports_dir)
        },
        "timestamp": datetime.now().isoformat()
    }

