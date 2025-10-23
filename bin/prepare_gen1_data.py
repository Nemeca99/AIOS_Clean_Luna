#!/usr/bin/env python3
"""Prepare smaller dataset for Gen 1 to prevent catastrophic forgetting."""

import json
import random
from pathlib import Path

random.seed(42)

# Load full dataset
full_data = Path("L:/infra_core/unsloth_integration/data/train.jsonl")
examples = []

with open(full_data, encoding='utf-8') as f:
    for line in f:
        if line.strip():
            examples.append(json.loads(line))

print(f"Full dataset: {len(examples)} examples")

# For Gen 1: Use 1000 examples (manageable for DialoGPT-small)
# Prioritize:
# 1. AIOS knowledge (152)
# 2. Personality (79)
# 3. Sample of Travis chatlogs (769)

aios_ex = []
personality_ex = []
chatlog_ex = []

for ex in examples:
    prompt = ex.get('prompt', '').lower()
    
    # AIOS knowledge (mentions AIOS, Luna, CFIA, CARMA, etc.)
    if any(word in prompt for word in ['aios', 'luna', 'cfia', 'carma', 'arbiter', 'generation', 'evolution', 'karma']):
        aios_ex.append(ex)
    # Personality (mentions Big Five, personality, etc.)
    elif any(word in prompt for word in ['personality', 'openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism', 'who are you', 'yourself']):
        personality_ex.append(ex)
    # Travis chatlogs
    else:
        chatlog_ex.append(ex)

print(f"AIOS examples: {len(aios_ex)}")
print(f"Personality examples: {len(personality_ex)}")
print(f"Chatlog examples: {len(chatlog_ex)}")

# Sample 1000 total
gen1_data = []
gen1_data.extend(aios_ex[:200])  # All AIOS knowledge
gen1_data.extend(personality_ex[:100])  # All personality
gen1_data.extend(random.sample(chatlog_ex, min(700, len(chatlog_ex))))  # 700 chatlogs

random.shuffle(gen1_data)

print(f"\nGen 1 dataset: {len(gen1_data)} examples")

# Save
output = Path("L:/infra_core/unsloth_integration/data/train_gen1.jsonl")
with open(output, 'w', encoding='utf-8') as f:
    for ex in gen1_data:
        f.write(json.dumps(ex, ensure_ascii=False) + '\n')

print(f"Saved to: {output}")

