#!/usr/bin/env python3
"""Compare Protocol Zero experiment runs"""
import sys
from pathlib import Path

experiments = {
    '20251022_035530': 'Baseline (with challenge cards)',
    '20251022_040336_nodream': 'NoDream Ablation',
    '20251022_041025_noauditor': 'NoAuditor Ablation'
}

print("PROTOCOL ZERO EXPERIMENT COMPARISON")
print("=" * 80)
print()

for exp_id, label in experiments.items():
    log_path = Path(f'experiments/protocol_zero/runs/{exp_id}/06_console_log.txt')
    if not log_path.exists():
        print(f"{label}: LOG NOT FOUND")
        continue
    
    with open(log_path) as f:
        content = f.read()
    
    # Count key metrics
    iterations = content.count('Iteration')
    actions = content.count('[ACTION @')
    idles = content.count('[ACTION @') - content.count('[ACTION @') + content.count('idle')
    sleep_entries = content.count('[SLEEP]')
    dream_cycles = content.count('Dream consolidation')
    
    # Extract action types
    action_types = set()
    for line in content.split('\n'):
        if '[ACTION @' in line and '[RESULT]' in line:
            parts = line.split('[RESULT]')
            if len(parts) > 1:
                action = parts[1].split(':')[0].strip()
                action_types.add(action)
    
    print(f"{label} ({exp_id})")
    print(f"  Iterations: {iterations}")
    print(f"  Total Actions: {actions}")
    print(f"  Unique Action Types: {len(action_types)} - {sorted(action_types)}")
    print(f"  Sleep Cycles: {dream_cycles}")
    print()

print("=" * 80)
print("COMPARISON COMPLETE")

