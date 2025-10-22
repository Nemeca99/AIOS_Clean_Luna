#!/usr/bin/env python3
"""
Speculative Decoding Metrics
Extract and visualize SD performance data

Usage:
    python sd_metrics.py --session latest --export dev_core/metrics/sd_metrics.csv
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def load_sd_session_logs(session="latest"):
    """Load speculative decoding logs (simulated for demo)"""
    # In real implementation, would parse from LM Studio logs
    # For demo, generate sample data
    
    sample_data = [
        {
            "timestamp": "2025-10-13T14:00:00Z",
            "model": "Dolphin-Mistral-24B",
            "draft_model": "Mistral-Small-0.5B",
            "draft_acceptance_rate": 0.72,
            "avg_stride": 3.2,
            "tokens_generated": 150,
            "wall_clock_saved_ms": 450
        },
        {
            "timestamp": "2025-10-13T14:01:30Z",
            "model": "Dolphin-Mistral-24B",
            "draft_model": "Mistral-Small-0.5B",
            "draft_acceptance_rate": 0.68,
            "avg_stride": 2.9,
            "tokens_generated": 120,
            "wall_clock_saved_ms": 380
        },
        {
            "timestamp": "2025-10-13T14:03:15Z",
            "model": "Dolphin-Mistral-24B",
            "draft_model": "Mistral-Small-0.5B",
            "draft_acceptance_rate": 0.75,
            "avg_stride": 3.5,
            "tokens_generated": 200,
            "wall_clock_saved_ms": 620
        },
        {
            "timestamp": "2025-10-13T14:05:45Z",
            "model": "Dolphin-Mistral-24B",
            "draft_model": "Mistral-Small-0.5B",
            "draft_acceptance_rate": 0.70,
            "avg_stride": 3.1,
            "tokens_generated": 175,
            "wall_clock_saved_ms": 510
        },
        {
            "timestamp": "2025-10-13T14:08:20Z",
            "model": "Dolphin-Mistral-24B",
            "draft_model": "Mistral-Small-0.5B",
            "draft_acceptance_rate": 0.73,
            "avg_stride": 3.3,
            "tokens_generated": 165,
            "wall_clock_saved_ms": 485
        }
    ]
    
    return sample_data

def compute_metrics(sd_data):
    """Compute aggregate SD metrics"""
    total_tokens = sum(d["tokens_generated"] for d in sd_data)
    total_time_saved_ms = sum(d["wall_clock_saved_ms"] for d in sd_data)
    
    metrics = {
        "total_sessions": len(sd_data),
        "total_tokens_generated": total_tokens,
        "avg_acceptance_rate": sum(d["draft_acceptance_rate"] for d in sd_data) / len(sd_data),
        "avg_stride": sum(d["avg_stride"] for d in sd_data) / len(sd_data),
        "total_time_saved_ms": total_time_saved_ms,
        "time_saved_per_1k_tokens_ms": (total_time_saved_ms / total_tokens * 1000) if total_tokens > 0 else 0
    }
    
    return metrics

def export_csv(sd_data, output_file):
    """Export SD metrics to CSV"""
    print(f"\nExporting to CSV: {output_file}")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "model", "draft_model", "draft_acceptance_rate",
            "avg_stride", "tokens_generated", "wall_clock_saved_ms",
            "time_saved_per_1k_tokens"
        ])
        
        writer.writeheader()
        for entry in sd_data:
            row = entry.copy()
            # Compute per-1k-token metric
            row["time_saved_per_1k_tokens"] = (
                (entry["wall_clock_saved_ms"] / entry["tokens_generated"] * 1000)
                if entry["tokens_generated"] > 0 else 0
            )
            writer.writerow(row)
    
    print(f"Exported {len(sd_data)} entries")

def generate_ascii_chart(metrics):
    """Generate simple ASCII chart for acceptance rate"""
    print("\n[Acceptance Rate Chart]")
    print("0%        25%        50%        75%       100%")
    print("|---------|---------|---------|---------|")
    
    acceptance = metrics["avg_acceptance_rate"]
    bar_length = int(acceptance * 40)
    bar = "=" * bar_length
    print(f"{bar}> {acceptance:.1%}")

def main():
    parser = argparse.ArgumentParser(description="Speculative Decoding Metrics")
    parser.add_argument("--session", type=str, default="latest", help="Session ID or 'latest'")
    parser.add_argument("--export", type=str, help="Export to CSV file")
    args = parser.parse_args()
    
    print("="*60)
    print("SPECULATIVE DECODING METRICS")
    print("="*60)
    print(f"\nSession: {args.session}")
    
    # Load data
    sd_data = load_sd_session_logs(args.session)
    print(f"Loaded {len(sd_data)} SD session logs")
    
    # Compute metrics
    metrics = compute_metrics(sd_data)
    
    print("\n[Aggregate Metrics]")
    print(f"  Total Sessions: {metrics['total_sessions']}")
    print(f"  Total Tokens Generated: {metrics['total_tokens_generated']:,}")
    print(f"  Avg Draft Acceptance Rate: {metrics['avg_acceptance_rate']:.1%}")
    print(f"  Avg Stride: {metrics['avg_stride']:.2f} tokens")
    print(f"  Total Time Saved: {metrics['total_time_saved_ms']:,.0f}ms")
    print(f"  Time Saved per 1k Tokens: {metrics['time_saved_per_1k_tokens_ms']:.1f}ms")
    
    # Generate chart
    generate_ascii_chart(metrics)
    
    print(f"\n[Efficiency Summary]")
    speedup_factor = 1.0 + (metrics['time_saved_per_1k_tokens_ms'] / 1000)
    print(f"  Estimated Speedup: {speedup_factor:.2f}x")
    print(f"  Draft Model: Mistral-Small-0.5B (BF16)")
    print(f"  Target Model: Dolphin-Mistral-24B (Q5_K_M)")
    
    # Export
    if args.export:
        export_csv(sd_data, args.export)
    
    print("\n" + "="*60)
    print("METRICS EXPORT COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()

