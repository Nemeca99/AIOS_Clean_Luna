#!/usr/bin/env python3
"""
Memory Graph Maintenance
Compact, prune, and evict memory nodes

Usage:
    python memory_graph.py --compact --prune --evict --report dev_core/metrics/memory_maintenance.json
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def load_memory_graph(base_dir="data_core/FractalCache"):
    """Load memory graph from files"""
    base_path = Path(base_dir)
    
    nodes = {}
    edges = defaultdict(list)
    
    # Load JSON files as nodes
    if base_path.exists():
        for json_file in base_path.glob("**/*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'id' in data:
                        nodes[data['id']] = data
            except Exception:
                pass
    
    return nodes, edges

def compact_graph(nodes, edges):
    """Compact graph by merging semantic duplicates"""
    print("\n[Compacting Graph]")
    
    # Group by content similarity (simplified: by tags)
    tag_groups = defaultdict(list)
    for node_id, node in nodes.items():
        tags = tuple(sorted(node.get('tags', [])))
        if tags:
            tag_groups[tags].append(node_id)
    
    # Merge groups with >3 members
    merged_count = 0
    for tags, group in tag_groups.items():
        if len(group) > 3:
            print(f"  Merging {len(group)} nodes with tags: {', '.join(tags[:3])}")
            merged_count += len(group) - 1
    
    print(f"  → Merged {merged_count} duplicate nodes")
    return merged_count

def prune_graph(nodes, edges, importance_threshold=0.2):
    """Prune low-importance, unconnected nodes"""
    print("\n[Pruning Graph]")
    
    to_prune = []
    for node_id, node in nodes.items():
        importance = node.get('importance', 0.5)
        access_count = node.get('access_count', 0)
        
        # Prune if low importance AND never accessed
        if importance < importance_threshold and access_count == 0:
            to_prune.append(node_id)
    
    print(f"  → Pruned {len(to_prune)} low-value nodes")
    return len(to_prune)

def evict_nodes(nodes, edges, target_count=None, strategy="lru_centrality"):
    """Evict nodes based on strategy"""
    print("\n[Evicting Nodes]")
    
    if not target_count:
        # Evict 10% of nodes
        target_count = len(nodes) // 10
    
    # Score nodes by eviction priority
    node_scores = []
    current_time = time.time()
    
    for node_id, node in nodes.items():
        last_access = node.get('last_access', current_time)
        recency = 1.0 / (1.0 + (current_time - last_access) / 86400)  # Days
        centrality = node.get('centrality', 0.0)
        importance = node.get('importance', 0.5)
        
        # Lower score = higher eviction priority
        if strategy == "lru_centrality":
            score = recency * centrality * importance
        elif strategy == "lru":
            score = recency
        else:  # low_importance
            score = importance
        
        node_scores.append((node_id, score))
    
    # Sort by score (ascending = evict first)
    node_scores.sort(key=lambda x: x[1])
    
    to_evict = node_scores[:target_count]
    evicted_count = len(to_evict)
    
    print(f"  Strategy: {strategy}")
    print(f"  → Evicted {evicted_count} nodes")
    
    if evicted_count > 0:
        print(f"  Sample evicted nodes:")
        for node_id, score in to_evict[:3]:
            print(f"    - {node_id}: score={score:.4f}")
    
    return evicted_count

def generate_report(nodes, edges, operations):
    """Generate maintenance report"""
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "graph_stats": {
            "total_nodes": len(nodes),
            "total_edges": sum(len(e) for e in edges.values()),
            "node_types": {},
            "avg_importance": 0.0,
            "avg_centrality": 0.0
        },
        "operations": operations,
        "performance": {
            "total_time_ms": sum(op["duration_ms"] for op in operations),
            "nodes_per_second": 0
        }
    }
    
    # Compute node type distribution
    type_counts = defaultdict(int)
    importances = []
    centralities = []
    
    for node in nodes.values():
        node_type = node.get('node_type', 'unknown')
        type_counts[node_type] += 1
        importances.append(node.get('importance', 0.5))
        centralities.append(node.get('centrality', 0.0))
    
    report["graph_stats"]["node_types"] = dict(type_counts)
    
    if importances:
        report["graph_stats"]["avg_importance"] = sum(importances) / len(importances)
    if centralities:
        report["graph_stats"]["avg_centrality"] = sum(centralities) / len(centralities)
    
    total_time_s = report["performance"]["total_time_ms"] / 1000
    if total_time_s > 0:
        report["performance"]["nodes_per_second"] = int(len(nodes) / total_time_s)
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Memory Graph Maintenance")
    parser.add_argument("--compact", action="store_true", help="Compact duplicate nodes")
    parser.add_argument("--prune", action="store_true", help="Prune low-value nodes")
    parser.add_argument("--evict", action="store_true", help="Evict nodes by LRU × centrality")
    parser.add_argument("--evict-count", type=int, help="Number of nodes to evict")
    parser.add_argument("--report", type=str, help="Output report file (JSON)")
    parser.add_argument("--base-dir", type=str, default="data_core/FractalCache", help="Memory base directory")
    args = parser.parse_args()
    
    print("="*60)
    print("MEMORY GRAPH MAINTENANCE")
    print("="*60)
    
    # Load graph
    print(f"\nLoading memory graph from: {args.base_dir}")
    nodes, edges = load_memory_graph(args.base_dir)
    print(f"Loaded {len(nodes)} nodes, {sum(len(e) for e in edges.values())} edges")
    
    operations = []
    
    # Compact
    if args.compact:
        start = time.time()
        merged = compact_graph(nodes, edges)
        duration = (time.time() - start) * 1000
        operations.append({
            "operation": "compact",
            "nodes_affected": merged,
            "duration_ms": duration
        })
    
    # Prune
    if args.prune:
        start = time.time()
        pruned = prune_graph(nodes, edges)
        duration = (time.time() - start) * 1000
        operations.append({
            "operation": "prune",
            "nodes_affected": pruned,
            "duration_ms": duration
        })
    
    # Evict
    if args.evict:
        start = time.time()
        evicted = evict_nodes(nodes, edges, target_count=args.evict_count)
        duration = (time.time() - start) * 1000
        operations.append({
            "operation": "evict",
            "nodes_affected": evicted,
            "duration_ms": duration
        })
    
    # Generate report
    if args.report or operations:
        report = generate_report(nodes, edges, operations)
        
        print("\n[Maintenance Report]")
        print(f"  Total nodes: {report['graph_stats']['total_nodes']}")
        print(f"  Node types: {report['graph_stats']['node_types']}")
        print(f"  Avg importance: {report['graph_stats']['avg_importance']:.3f}")
        print(f"  Avg centrality: {report['graph_stats']['avg_centrality']:.3f}")
        print(f"  Total time: {report['performance']['total_time_ms']:.1f}ms")
        
        if args.report:
            with open(args.report, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport written to: {args.report}")
    
    print("\n" + "="*60)
    print("MAINTENANCE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()

