"""
CLI interface for CodeGraph Mapper
"""

import sys
import argparse
from pathlib import Path

from .runner import run_map, CGMParams


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AIOS CodeGraph Mapper - Generate structural code graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default)
  python -m cgm.cli --root L:\\AIOS --out L:\\AIOS\\_maps
  
  # Real run with approval required
  python -m cgm.cli --root L:\\AIOS --out L:\\AIOS\\_maps --no-dry-run --require-approval
  
  # Quick run, no approval, skip optional outputs
  python -m cgm.cli --root L:\\AIOS --out L:\\AIOS\\_maps --no-dry-run --no-dot --no-mermaid
  
  # Allow large graphs (>250k edges)
  python -m cgm.cli --root L:\\AIOS --out L:\\AIOS\\_maps --no-dry-run --allow-large
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--root',
        required=True,
        help='Root directory to scan (must be within L:\\AIOS)'
    )
    
    parser.add_argument(
        '--out',
        required=True,
        help='Base output directory (must be L:\\AIOS\\_maps)'
    )
    
    # Optional filters
    parser.add_argument(
        '--include',
        nargs='+',
        default=["**/*.py"],
        help='Glob patterns to include (default: **/*.py)'
    )
    
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=["**/__pycache__/**", "**/.venv/**", "**/.git/**", "**/python/Lib/**"],
        help='Glob patterns to exclude'
    )
    
    # Mode flags
    parser.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        default=True,
        help='Dry-run mode (default): generate plan only, no writes'
    )
    
    parser.add_argument(
        '--no-dry-run',
        dest='dry_run',
        action='store_false',
        help='Disable dry-run mode and actually write artifacts'
    )
    
    parser.add_argument(
        '--require-approval',
        action='store_true',
        help='Pause before writing and wait for approval.ok file'
    )
    
    parser.add_argument(
        '--allow-large',
        action='store_true',
        help='Allow graphs with >250k edges (disables circuit breaker)'
    )
    
    # Output toggles
    parser.add_argument(
        '--no-dot',
        action='store_true',
        help='Skip Graphviz DOT output'
    )
    
    parser.add_argument(
        '--no-mermaid',
        action='store_true',
        help='Skip Mermaid diagram output'
    )
    
    # Budget
    parser.add_argument(
        '--budget-ms',
        type=int,
        help='CPU budget in milliseconds (default: 180000 = 3 minutes)'
    )
    
    args = parser.parse_args()
    
    # Build params
    params = CGMParams(
        root=args.root,
        out_base=args.out,
        include=args.include,
        exclude=args.exclude,
        dry_run=args.dry_run,
        require_approval=args.require_approval,
        allow_large=args.allow_large,
        no_dot=args.no_dot,
        no_mermaid=args.no_mermaid,
        budget_ms=args.budget_ms
    )
    
    # Run mapper
    result = run_map(params)
    
    # Print result
    if result.ok:
        print(f"\n✅ CodeGraph Mapper completed successfully!")
        print(f"   Run ID: {result.run_id}")
        
        if params.dry_run:
            print(f"   Plan: {result.plan_path}")
            print(f"   (Dry-run mode - no artifacts written)")
        else:
            print(f"   Artifacts: {len(result.artifacts)}")
            print(f"   Provenance: {result.provenance_path}")
        
        print(f"\n   Metrics:")
        for key, value in result.metrics.items():
            print(f"     {key}: {value:,}")
    else:
        print(f"\n❌ CodeGraph Mapper failed!")
        print(f"   Error: {result.error}")
        print(f"   Exit code: {result.exit_code}")
    
    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()

