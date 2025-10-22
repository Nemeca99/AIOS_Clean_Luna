"""
CSV emitters for code graph
Writes import matrix and edge list
"""

import csv
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class CSVEmitter:
    """Emits graph data as CSV files"""
    
    def __init__(self, out_dir: Path, logger):
        self.out_dir = out_dir
        self.logger = logger
        self.graph_dir = out_dir / "graph"
        self.graph_dir.mkdir(parents=True, exist_ok=True)
    
    def emit_all(self, graph_data: Dict) -> List[Path]:
        """
        Emit all CSV artifacts
        Returns: list of written file paths
        """
        written = []
        
        # 1. Edges CSV
        edges_path = self.graph_dir / "edges.csv"
        with open(edges_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['src', 'dst', 'type', 'meta_json'])
            
            for edge in sorted(graph_data['edges'], key=lambda e: (e['src'], e['dst'])):
                import json
                meta_json = json.dumps(edge.get('meta', {}))
                writer.writerow([edge['src'], edge['dst'], edge['type'], meta_json])
        
        written.append(edges_path)
        self.logger.info("emit_csv", file="edges.csv", rows=len(graph_data['edges']))
        
        # 2. Import matrix
        matrix_path = self.graph_dir / "import_matrix.csv"
        self._emit_import_matrix(graph_data['edges'], matrix_path)
        written.append(matrix_path)
        
        return written
    
    def _emit_import_matrix(self, edges: List[Dict], output_path: Path):
        """
        Generate import matrix CSV
        Rows = modules, Columns = modules, Value = import count
        """
        # Build module import counts
        import_counts = defaultdict(lambda: defaultdict(int))
        modules = set()
        
        for edge in edges:
            if edge['type'] in ['import', 'from_import']:
                # Extract module names from node IDs
                src_mod = edge['src'].split(':')[1] if ':' in edge['src'] else edge['src']
                dst_mod = edge['dst'].split(':')[1] if ':' in edge['dst'] else edge['dst']
                
                modules.add(src_mod)
                modules.add(dst_mod)
                import_counts[src_mod][dst_mod] += 1
        
        # Sort modules for deterministic output
        sorted_modules = sorted(modules)
        
        # Write matrix
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Header row
            writer.writerow([''] + sorted_modules)
            
            # Data rows
            for src_mod in sorted_modules:
                row = [src_mod]
                for dst_mod in sorted_modules:
                    row.append(import_counts[src_mod][dst_mod])
                writer.writerow(row)
        
        self.logger.info("emit_csv", file="import_matrix.csv", modules=len(sorted_modules))

