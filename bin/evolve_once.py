#!/usr/bin/env python3
"""
Evolution CLI - Manual trigger for evolution cycles.

Usage:
    python bin/evolve_once.py --reason "smoke test" --steps 200
    python bin/evolve_once.py --reason "production run"
"""

import sys
import argparse
from pathlib import Path

# Add AIOS to path
aios_root = Path(__file__).parent.parent
sys.path.insert(0, str(aios_root))

from infra_core.unsloth_integration.evolution_orchestrator import run_evolution_window


def main():
    parser = argparse.ArgumentParser(
        description="Trigger one evolution cycle manually",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Smoke test (200 steps)
  python bin/evolve_once.py --reason "smoke test" --steps 200
  
  # Production run (1200 steps)
  python bin/evolve_once.py --reason "production evolution"
  
  # Specific generation
  python bin/evolve_once.py --reason "manual" --gen-id 3
"""
    )
    
    parser.add_argument(
        '--reason',
        required=True,
        help='Reason for manual evolution (logged)'
    )
    
    parser.add_argument(
        '--steps',
        type=int,
        default=None,
        help='Override training steps (default: from config)'
    )
    
    parser.add_argument(
        '--gen-id',
        type=int,
        default=None,
        help='Generation ID (default: auto-detect next)'
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"MANUAL EVOLUTION TRIGGER")
    print(f"{'='*60}")
    print(f"Reason: {args.reason}")
    if args.steps:
        print(f"Steps: {args.steps} (override)")
    if args.gen_id is not None:
        print(f"Generation: {args.gen_id} (manual)")
    print(f"{'='*60}\n")
    
    # Run evolution
    result = run_evolution_window(
        mode="cli",
        gen_id=args.gen_id,
        steps_override=args.steps
    )
    
    # Print summary
    print("\n" + "="*60)
    print("RESULT SUMMARY")
    print("="*60)
    print(f"Generation: {result['gen_id']}")
    print(f"Status: {'✅ PROMOTED' if result['promoted'] else '❌ REJECTED'}")
    print(f"Reason: {result['reason']}")
    print(f"Time: {result['walltime_seconds']:.1f}s")
    
    if result['promoted']:
        print(f"\n✅ SUCCESS: Generation {result['gen_id']} promoted to HEAD")
        return 0
    else:
        print(f"\n❌ FAILED: {result['reason']}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

