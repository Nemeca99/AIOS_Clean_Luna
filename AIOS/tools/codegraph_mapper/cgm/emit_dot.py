"""
DOT (Graphviz) emitter for code graph
Optional - only creates if not disabled
"""

from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class DOTEmitter:
    """Emits graph as Graphviz DOT format"""
    
    def __init__(self, out_dir: Path, logger):
        self.out_dir = out_dir
        self.logger = logger
        self.graph_dir = out_dir / "graph"
        self.graph_dir.mkdir(parents=True, exist_ok=True)
    
    def emit(self, graph_data: Dict, max_nodes: int = 500) -> Path:
        """
        Emit DOT file (package-level if too large)
        Returns: path to DOT file
        """
        output_path = self.graph_dir / "code_graph.dot"
        
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        # If too many nodes, emit package-level graph only
        if len(nodes) > max_nodes:
            self.logger.warn("dot_large_graph", 
                           nodes=len(nodes), 
                           max=max_nodes,
                           msg="Emitting package-level graph only")
            return self._emit_package_level(nodes, edges, output_path)
        
        # Emit full graph
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('digraph CodeGraph {\n')
            f.write('  rankdir=LR;\n')
            f.write('  node [shape=box, style=rounded];\n\n')
            
            # Group nodes by package
            packages = defaultdict(list)
            for node in nodes:
                if node['kind'] == 'module':
                    pkg = '.'.join(node['qualname'].split('.')[:-1]) or 'root'
                    packages[pkg].append(node)
            
            # Emit clusters
            for pkg_name, pkg_nodes in sorted(packages.items()):
                cluster_id = pkg_name.replace('.', '_')
                f.write(f'  subgraph cluster_{cluster_id} {{\n')
                f.write(f'    label="{pkg_name}";\n')
                f.write('    style=filled;\n')
                f.write('    color=lightgrey;\n\n')
                
                for node in pkg_nodes:
                    node_id = self._escape_id(node['id'])
                    label = node['name']
                    f.write(f'    "{node_id}" [label="{label}"];\n')
                
                f.write('  }\n\n')
            
            # Emit edges (imports only to keep it manageable)
            for edge in edges:
                if edge['type'] in ['import', 'from_import']:
                    src_id = self._escape_id(edge['src'])
                    dst_id = self._escape_id(edge['dst'])
                    edge_type = edge['type']
                    f.write(f'  "{src_id}" -> "{dst_id}" [label="{edge_type}"];\n')
            
            f.write('}\n')
        
        self.logger.info("emit_dot", file="code_graph.dot", nodes=len(nodes), edges=len(edges))
        return output_path
    
    def _emit_package_level(self, nodes: List, edges: List, output_path: Path) -> Path:
        """Emit simplified package-level graph"""
        # Extract package nodes only
        packages = set()
        for node in nodes:
            if node['kind'] == 'module' and 'qualname' in node:
                pkg = '.'.join(node['qualname'].split('.')[:-1]) or 'root'
                packages.add(pkg)
        
        # Build package-level edges
        pkg_edges = defaultdict(int)
        for edge in edges:
            if edge['type'] in ['import', 'from_import']:
                src_pkg = self._extract_package(edge['src'])
                dst_pkg = self._extract_package(edge['dst'])
                if src_pkg and dst_pkg:
                    pkg_edges[(src_pkg, dst_pkg)] += 1
        
        # Write DOT
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('digraph PackageGraph {\n')
            f.write('  rankdir=LR;\n')
            f.write('  node [shape=box];\n\n')
            
            for pkg in sorted(packages):
                pkg_id = pkg.replace('.', '_')
                f.write(f'  "{pkg_id}" [label="{pkg}"];\n')
            
            f.write('\n')
            
            for (src_pkg, dst_pkg), count in pkg_edges.items():
                src_id = src_pkg.replace('.', '_')
                dst_id = dst_pkg.replace('.', '_')
                f.write(f'  "{src_id}" -> "{dst_id}" [label="{count}"];\n')
            
            f.write('}\n')
        
        return output_path
    
    def _extract_package(self, node_id: str) -> str:
        """Extract package name from node ID"""
        if ':' not in node_id:
            return ""
        
        qual = node_id.split(':')[1]
        parts = qual.split('.')
        return '.'.join(parts[:-1]) if len(parts) > 1 else parts[0]
    
    def _escape_id(self, node_id: str) -> str:
        """Escape node ID for DOT"""
        return node_id.replace('"', '\\"').replace('\\', '\\\\')

