#!/usr/bin/env python3
"""
Fractal Core - Factorian Architecture
Engineering compassion through efficiency.

Implements unified Fractal Controller applying Information Bottleneck
at all scales (token, memory, code, arbiter) with type-conditioned policies.
"""

from fractal_core.fractal_core import FractalCore

__version__ = "1.0.0"
__all__ = ['FractalCore']


def get_commands():
    """AIOS plugin interface - declare commands."""
    return {
        "commands": {
            "--fractal-status": {
                "help": "Show fractal controller status and policies",
                "usage": "python main.py --fractal-status",
                "examples": ["python main.py --fractal-status"]
            },
            "--fractal-tune": {
                "help": "Tune thresholds with current data",
                "usage": "python main.py --fractal-tune",
                "examples": ["python main.py --fractal-tune"]
            }
        },
        "description": "Fractal optimization controller - multiscale efficiency",
        "version": __version__,
        "capabilities": [
            "type_mixture_classification",
            "knapsack_allocation",
            "learned_thresholds",
            "cross_scale_policies"
        ],
        "can_run_standalone": False
    }


def handle_command(args):
    """AIOS plugin interface - handle commands."""
    if '--fractal-status' in args:
        fractal = FractalCore()
        status = fractal.get_status()
        
        print("\nFractal Controller Status")
        print("=" * 60)
        print(f"Version: {status['version']}")
        print(f"Policy Table: {status['policy_version']}")
        print(f"Thresholds: {status['threshold_version']}")
        print(f"Telemetry: {'Enabled' if status['telemetry_enabled'] else 'Disabled'}")
        print()
        return True
    
    elif '--fractal-tune' in args:
        fractal = FractalCore()
        result = fractal.tune_thresholds()
        
        print("\nThreshold Tuning Complete")
        print("=" * 60)
        print(f"Thresholds updated: {result['updated_count']}")
        print(f"Improvement: {result['improvement_pct']:.2f}%")
        print()
        return True
    
    return False

