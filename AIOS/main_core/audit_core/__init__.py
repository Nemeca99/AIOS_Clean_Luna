#!/usr/bin/env python3
"""
AIOS Audit Core Module
Automated system health checks and production readiness scoring
"""

from .audit_runner import (
    discover_cores,
    audit_core as audit_core_runner,
    generate_report,
    CoreScore
)

# Note: handle_command is in audit_interface.py to avoid circular import

__all__ = [
    'discover_cores',
    'audit_core_runner',
    'generate_report',
    'CoreScore'
]

__version__ = "1.0.0"
__description__ = "Automated audit harness for AIOS system health"

