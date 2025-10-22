#!/usr/bin/env python3
"""
Provenance to Rules Materialization
Compacts NDJSON provenance logs into rules_index.json

Usage:
    python provenance_to_rules.py --in data_core/analytics/provenance.ndjson --out dev_core/rules_index.json
"""

import argparse
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def extract_if_fragments(prompt_assembly):
    """Extract condition fragments from prompt assembly"""
    fragments = []
    
    # Extract from CARMA memories
    if "carma_memories" in prompt_assembly.get("layers", {}):
        memories = prompt_assembly["layers"]["carma_memories"]
        # Simplified: extract memory IDs
        fragments.append("carma_memory_present")
    
    # Extract from arbiter lessons
    if "arbiter_lessons" in prompt_assembly.get("layers", {}):
        lessons = prompt_assembly["layers"]["arbiter_lessons"]
        fragments.append("arbiter_lesson_present")
    
    # Extract RVC grade
    if "rvc_guidance" in prompt_assembly.get("layers", {}):
        fragments.append(f"rvc_{prompt_assembly.get('rvc_grade', 'moderate')}")
    
    return fragments

def extract_context_tags(prompt_assembly):
    """Extract context tags from prompt"""
    tags = []
    
    # Extract from query
    query = prompt_assembly.get("query", "").lower()
    
    # Simple keyword extraction
    keywords = ["quantum", "consciousness", "entanglement", "philosophy", "physics"]
    for keyword in keywords:
        if keyword in query:
            tags.append(keyword)
    
    return tags

def compute_rule_hash(rule):
    """Compute hash for rule deduplication"""
    rule_str = json.dumps({
        "if_fragments": rule["if_fragments"],
        "context_tags": rule["context_tags"],
        "then": rule["then"]
    }, sort_keys=True)
    return hashlib.sha256(rule_str.encode()).hexdigest()[:16]

def materialize_rules(provenance_file, output_file):
    """
    Convert provenance NDJSON to materialized rules_index.json
    
    Rules are a view, not source of truth
    Provenance is append-only and never overwritten
    """
    print(f"Reading provenance from: {provenance_file}")
    
    if not Path(provenance_file).exists():
        print(f"WARNING: Provenance file not found, creating empty rules index")
        rules_index = {
            "version": "1.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "source": str(provenance_file),
            "rules": []
        }
        
        with open(output_file, 'w') as f:
            json.dump(rules_index, f, indent=2)
        
        print(f"Created empty rules index: {output_file}")
        return
    
    # Read all provenance entries
    entries = []
    with open(provenance_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # Skip malformed lines
    
    print(f"Loaded {len(entries)} provenance entries")
    
    # Group by similar conditions
    rule_groups = defaultdict(list)
    
    for entry in entries:
        # Extract conditions
        if_fragments = extract_if_fragments(entry)
        context_tags = extract_context_tags(entry)
        
        # Extract outcome (then)
        then = {
            "token_count": entry.get("token_count", 0),
            "final_prompt_length": len(entry.get("final_prompt", ""))
        }
        
        # Group by condition hash
        condition_key = json.dumps({
            "if_fragments": sorted(if_fragments),
            "context_tags": sorted(context_tags)
        }, sort_keys=True)
        
        rule_groups[condition_key].append({
            "if_fragments": if_fragments,
            "context_tags": context_tags,
            "then": then,
            "timestamp": entry.get("timestamp", "")
        })
    
    print(f"Grouped into {len(rule_groups)} rule patterns")
    
    # Materialize rules
    rules = []
    for condition_key, group in rule_groups.items():
        # Aggregate outcomes
        avg_token_count = sum(r["then"]["token_count"] for r in group) / len(group)
        
        rule = {
            "id": f"rule_{hashlib.sha256(condition_key.encode()).hexdigest()[:8]}",
            "if_fragments": sorted(group[0]["if_fragments"]),
            "context_tags": sorted(group[0]["context_tags"]),
            "then": {
                "avg_token_count": int(avg_token_count)
            },
            "confidence": min(1.0, len(group) / 10),  # Confidence grows with support
            "support": len(group),  # Number of times this pattern occurred
            "last_seen": max(r["timestamp"] for r in group),
            "hash": compute_rule_hash(group[0])
        }
        
        rules.append(rule)
    
    # Sort by support (most common first)
    rules.sort(key=lambda r: r["support"], reverse=True)
    
    # Create rules index
    rules_index = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": str(provenance_file),
        "total_provenance_entries": len(entries),
        "total_rules": len(rules),
        "rules": rules
    }
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(rules_index, f, indent=2)
    
    print(f"\nMaterialized {len(rules)} rules to: {output_file}")
    print(f"Top 5 rules by support:")
    for i, rule in enumerate(rules[:5], 1):
        print(f"  {i}. {rule['id']}: support={rule['support']}, confidence={rule['confidence']:.2f}")
        print(f"     Conditions: {', '.join(rule['if_fragments'][:3])}")

def main():
    parser = argparse.ArgumentParser(description="Materialize provenance into rules index")
    parser.add_argument("--in", dest="input_file", required=True, help="Input provenance NDJSON file")
    parser.add_argument("--out", dest="output_file", required=True, help="Output rules JSON file")
    args = parser.parse_args()
    
    materialize_rules(args.input_file, args.output_file)

if __name__ == "__main__":
    main()

