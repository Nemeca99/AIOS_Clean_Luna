"""
JSON emitters for code graph
Writes nodes, edges, unified graph, symbol index, call index
"""

import json
from pathlib import Path
from typing import Dict, List


class JSONEmitter:
    """Emits graph data as JSON files"""
    
    def __init__(self, out_dir: Path, logger):
        self.out_dir = out_dir
        self.logger = logger
        self.graph_dir = out_dir / "graph"
        self.graph_dir.mkdir(parents=True, exist_ok=True)
    
    def emit_all(self, graph_data: Dict, file_inventory: Dict) -> List[Path]:
        """
        Emit all JSON artifacts
        Returns: list of written file paths
        """
        written = []
        
        # Sort nodes and edges for deterministic output
        nodes = sorted(graph_data['nodes'], key=lambda n: n['id'])
        edges = sorted(graph_data['edges'], key=lambda e: (e['src'], e['dst'], e['type']))
        
        # 1. Unified graph
        unified_path = self.graph_dir / "code_graph.json"
        with open(unified_path, 'w', encoding='utf-8') as f:
            json.dump({
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                }
            }, f, indent=2)
        written.append(unified_path)
        self.logger.info("emit_json", file="code_graph.json", nodes=len(nodes), edges=len(edges))
        
        # 2. Nodes only
        nodes_path = self.graph_dir / "nodes.json"
        with open(nodes_path, 'w', encoding='utf-8') as f:
            json.dump(nodes, f, indent=2)
        written.append(nodes_path)
        
        # 3. Edges only
        edges_path = self.graph_dir / "edges.json"
        with open(edges_path, 'w', encoding='utf-8') as f:
            json.dump(edges, f, indent=2)
        written.append(edges_path)
        
        # 4. Symbol index
        symbol_path = self.graph_dir / "symbol_index.json"
        with open(symbol_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data['symbol_index'], f, indent=2)
        written.append(symbol_path)
        
        # 5. Call index
        call_path = self.graph_dir / "call_index.json"
        with open(call_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data['call_index'], f, indent=2)
        written.append(call_path)
        
        # 6. File index
        file_path = self.graph_dir / "file_index.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(file_inventory, f, indent=2)
        written.append(file_path)
        
        return written

