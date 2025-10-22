"""
Mermaid diagram emitter for code graph
Generates package-level flowchart
"""

from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class MermaidEmitter:
    """Emits graph as Mermaid diagram"""
    
    def __init__(self, out_dir: Path, logger):
        self.out_dir = out_dir
        self.logger = logger
        self.graph_dir = out_dir / "graph"
        self.graph_dir.mkdir(parents=True, exist_ok=True)
    
    def emit(self, graph_data: Dict, max_packages: int = 100) -> Path:
        """
        Emit Mermaid flowchart (package-level with clusters)
        Returns: path to .mmd file
        """
        output_path = self.graph_dir / "code_graph.mmd"
        
        # Extract packages and their relationships
        packages = set()
        for node in graph_data['nodes']:
            if node['kind'] == 'module' and 'qualname' in node:
                qual = node['qualname']
                # Get top-level package
                top_pkg = qual.split('.')[0] if '.' in qual else qual
                packages.add(top_pkg)
        
        # Build package import relationships
        pkg_imports = defaultdict(set)
        for edge in graph_data['edges']:
            if edge['type'] in ['import', 'from_import']:
                src_pkg = self._extract_top_package(edge['src'])
                dst_pkg = self._extract_top_package(edge['dst'])
                if src_pkg and dst_pkg and src_pkg != dst_pkg:
                    pkg_imports[src_pkg].add(dst_pkg)
        
        # Check size
        if len(packages) > max_packages:
            self.logger.warn("mermaid_large", 
                           packages=len(packages), 
                           max=max_packages,
                           msg="Emitting top packages only")
            packages = set(list(sorted(packages))[:max_packages])
        
        # Write Mermaid
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('graph TD\n')
            f.write('  %% AIOS CodeGraph - Package Level\n\n')
            
            # Define nodes
            for pkg in sorted(packages):
                pkg_id = self._mermaid_id(pkg)
                f.write(f'  {pkg_id}["{pkg}"]\n')
            
            f.write('\n')
            
            # Define edges
            for src_pkg in sorted(pkg_imports.keys()):
                if src_pkg not in packages:
                    continue
                
                src_id = self._mermaid_id(src_pkg)
                for dst_pkg in sorted(pkg_imports[src_pkg]):
                    if dst_pkg not in packages:
                        continue
                    
                    dst_id = self._mermaid_id(dst_pkg)
                    f.write(f'  {src_id} --> {dst_id}\n')
            
            f.write('\n  %% Style\n')
            f.write('  classDef core fill:#e1f5ff,stroke:#333,stroke-width:2px\n')
        
        self.logger.info("emit_mermaid", file="code_graph.mmd", packages=len(packages))
        return output_path
    
    def _extract_top_package(self, node_id: str) -> str:
        """Extract top-level package from node ID"""
        if ':' not in node_id:
            return ""
        
        qual = node_id.split(':')[1]
        return qual.split('.')[0]
    
    def _mermaid_id(self, pkg_name: str) -> str:
        """Convert package name to valid Mermaid ID"""
        return pkg_name.replace('.', '_').replace('-', '_')

