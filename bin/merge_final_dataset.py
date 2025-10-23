#!/usr/bin/env python3
"""Merge all datasets into final train.jsonl on L: drive."""

import json
import random
from pathlib import Path

random.seed(42)

base = Path("L:/infra_core/unsloth_integration/data")

files = [
    'travis_all_chatlogs_v2.jsonl',
    'aios_knowledge.jsonl',
    'personality.jsonl'
]

all_ex = []
for f in files:
    file_path = base / f
    if file_path.exists():
        for line in file_path.read_text(encoding='utf-8').split('\n'):
            if line.strip():
                all_ex.append(json.loads(line))

print(f'Total loaded: {len(all_ex)}')

# Deduplicate and filter
seen = set()
unique = []
for ex in all_ex:
    if not ex.get('prompt') or not ex.get('response'):
        continue
    if len(ex['prompt']) < 10 or len(ex['response']) < 10:
        continue
    
    key = (ex['prompt'][:50].lower(), ex['response'][:50].lower())
    if key not in seen:
        seen.add(key)
        unique.append(ex)

print(f'Unique: {len(unique)}')

# Shuffle
random.shuffle(unique)

# Save
output = base / 'train.jsonl'
with open(output, 'w', encoding='utf-8') as f:
    for ex in unique:
        f.write(json.dumps(ex, ensure_ascii=False) + '\n')

print(f'\n✅ Saved {len(unique)} examples to L:/infra_core/unsloth_integration/data/train.jsonl')

# Stats
detailed = len([ex for ex in unique if len(ex['prompt']) > 100])
print(f'📊 {detailed} detailed examples (prompt > 100 chars)')
print(f'📊 {len(unique) - detailed} short examples')

