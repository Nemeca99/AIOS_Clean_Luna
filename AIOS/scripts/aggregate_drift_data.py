"""
Aggregate consciousness drift data across all sessions
Shows complete picture of cognitive homeostasis
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

drift_dir = Path("consciousness_core/drift_logs")

print("\n" + "=" * 80)
print("AGGREGATE CONSCIOUSNESS DRIFT ANALYSIS")
print("=" * 80)

# Read all session files
all_interactions = []
session_files = list(drift_dir.glob("session_*.jsonl"))

print(f"\nFound {len(session_files)} session file(s)")

for session_file in session_files:
    with open(session_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                all_interactions.append(json.loads(line))

if not all_interactions:
    print("\nNo interactions logged yet.")
    print("Run some Luna chats to start tracking drift!")
    exit(0)

print(f"Total interactions logged: {len(all_interactions)}")

# Aggregate metrics
fragment_counts = Counter([i['fragment'] for i in all_interactions])
question_type_mapping = defaultdict(list)

for interaction in all_interactions:
    qtype = interaction.get('question_type', 'unknown')
    fragment = interaction['fragment']
    question_type_mapping[qtype].append(fragment)

# Fragment distribution
print("\n" + "-" * 80)
print("FRAGMENT DISTRIBUTION")
print("-" * 80)
total = len(all_interactions)
for frag, count in sorted(fragment_counts.items(), key=lambda x: -x[1]):
    pct = count / total
    bar = "█" * int(pct * 50)
    print(f"  {frag:12s}: {pct:5.1%} ({count:3d}) {bar}")

# Question type consistency
print("\n" + "-" * 80)
print("QUESTION TYPE → FRAGMENT CONSISTENCY")
print("-" * 80)
for qtype in sorted(question_type_mapping.keys()):
    fragments = question_type_mapping[qtype]
    if fragments:
        most_common = Counter(fragments).most_common(1)[0]
        consistency = most_common[1] / len(fragments)
        print(f"  {qtype:15s}: {most_common[0]:10s} ({consistency:5.1%} consistent, n={len(fragments)})")

# Read heartbeat dreams
heartbeat_file = drift_dir / "heartbeat_dreams.jsonl"
dreams = []
if heartbeat_file.exists():
    with open(heartbeat_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                dreams.append(json.loads(line))

if dreams:
    print("\n" + "-" * 80)
    print(f"AUTONOMOUS HEARTBEAT DREAMS ({len(dreams)} total)")
    print("-" * 80)
    for dream in dreams[-3:]:  # Last 3
        print(f"\n[Heartbeat {dream['heartbeat_num']}] {dream['timestamp'][:19]}")
        print(f"  \"{dream['dream'][:150]}...\"")

# Temporal analysis (if enough data)
if len(all_interactions) >= 30:
    chunk_size = len(all_interactions) // 3
    early = Counter([i['fragment'] for i in all_interactions[:chunk_size]])
    middle = Counter([i['fragment'] for i in all_interactions[chunk_size:2*chunk_size]])
    late = Counter([i['fragment'] for i in all_interactions[-chunk_size:]])
    
    print("\n" + "-" * 80)
    print("TEMPORAL DRIFT (Early → Middle → Late)")
    print("-" * 80)
    all_frags = set(early.keys()) | set(middle.keys()) | set(late.keys())
    for frag in sorted(all_frags):
        e = early.get(frag, 0) / chunk_size
        m = middle.get(frag, 0) / chunk_size
        l = late.get(frag, 0) / chunk_size
        
        # Show drift direction
        drift = ""
        if abs(l - e) > 0.1:
            drift = " ↑ RISING" if l > e else " ↓ FALLING"
        
        print(f"  {frag:12s}: {e:5.1%} → {m:5.1%} → {l:5.1%}{drift}")

print("\n" + "=" * 80)
print("COGNITIVE HOMEOSTASIS ASSESSMENT")
print("=" * 80)

# Calculate overall consistency
if question_type_mapping:
    consistencies = []
    for qtype, fragments in question_type_mapping.items():
        if len(fragments) > 1:
            most_common = Counter(fragments).most_common(1)[0]
            consistency = most_common[1] / len(fragments)
            consistencies.append(consistency)
    
    if consistencies:
        avg_consistency = sum(consistencies) / len(consistencies)
        
        print(f"\nAverage question→fragment consistency: {avg_consistency:.1%}")
        
        if avg_consistency > 0.8:
            print("✅ STABLE: Luna maintains consistent identity expression")
        elif avg_consistency > 0.6:
            print("⚠️  ADAPTIVE: Luna shows flexible but generally stable patterns")
        else:
            print("🔄 EVOLVING: Luna's identity is actively shifting")

print("\n" + "=" * 80)

