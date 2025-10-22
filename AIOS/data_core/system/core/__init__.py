#!/usr/bin/env python3
"""
Data Core - Modular Function Library
Exports all core functionality for the data management system
"""

from .stats import (
    get_fractal_cache_stats,
    get_arbiter_cache_stats,
    get_conversation_stats,
    get_database_stats,
    get_system_overview,
    get_dir_stats
)

from .pipeline import (
    ingest_data,
    export_data,
    get_pipeline_metrics,
    load_pipeline_stats,
    save_pipeline_stats,
    load_data_registry,
    save_data_registry
)

from .cleanup import (
    cleanup_old_data,
    export_to_json,
    export_to_csv,
    export_to_text,
    matches_filter
)

from .lessons import (
    get_relevant_lessons
)

from .database import (
    get_database_info
)

__all__ = [
    # Stats
    'get_fractal_cache_stats',
    'get_arbiter_cache_stats',
    'get_conversation_stats',
    'get_database_stats',
    'get_system_overview',
    'get_dir_stats',
    # Pipeline
    'ingest_data',
    'export_data',
    'get_pipeline_metrics',
    'load_pipeline_stats',
    'save_pipeline_stats',
    'load_data_registry',
    'save_data_registry',
    # Cleanup
    'cleanup_old_data',
    'export_to_json',
    'export_to_csv',
    'export_to_text',
    'matches_filter',
    # Lessons
    'get_relevant_lessons',
    # Database
    'get_database_info',
]

