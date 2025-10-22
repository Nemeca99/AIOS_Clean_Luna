"""
Markdown report generator
Creates human-readable summary of code graph
"""

from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict


class MarkdownReporter:
    """Generates Markdown summary report"""
    
    def __init__(self, out_dir: Path, logger):
        self.out_dir = out_dir
        self.logger = logger
        self.reports_dir = out_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, graph_data: Dict, file_inventory: Dict, 
                provenance: Dict) -> Path:
        """
        Generate summary.md
        Returns: path to report
        """
        output_path = self.reports_dir / "summary.md"
        
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        stats = graph_data['stats']
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# AIOS CodeGraph Summary\n\n")
            f.write(f"**Generated:** {provenance['timestamps']['start']}\n")
            f.write(f"**Run ID:** {provenance['run_id']}\n")
            f.write(f"**Tool Version:** {provenance['version']}\n\n")
            
            f.write("---\n\n")
            
            # Totals
            f.write("## Overall Statistics\n\n")
            f.write(f"- **Total Files:** {stats.get('files', len(file_inventory))}\n")
            f.write(f"- **Python Files:** {stats['py_files']}\n")
            f.write(f"- **Modules:** {stats['modules']}\n")
            f.write(f"- **Total Nodes:** {stats['nodes']}\n")
            f.write(f"- **Total Edges:** {stats['edges']}\n")
            f.write(f"- **Parse Failures:** {stats.get('parse_failures', 0)}\n\n")
            
            # Top imported modules
            f.write("## Top 20 Most Imported Modules\n\n")
            import_counts = Counter()
            for edge in edges:
                if edge['type'] in ['import', 'from_import']:
                    dst = edge['dst'].split(':')[1] if ':' in edge['dst'] else edge['dst']
                    import_counts[dst] += 1
            
            f.write("| Rank | Module | Import Count |\n")
            f.write("|------|--------|-------------|\n")
            for i, (mod, count) in enumerate(import_counts.most_common(20), 1):
                f.write(f"| {i} | `{mod}` | {count} |\n")
            f.write("\n")
            
            # Orphans (modules with no connections)
            f.write("## Orphan Modules\n\n")
            orphans = self._find_orphans(nodes, edges)
            if orphans:
                f.write(f"Found {len(orphans)} modules with no imports (in or out):\n\n")
                for mod in sorted(orphans)[:20]:
                    f.write(f"- `{mod}`\n")
                if len(orphans) > 20:
                    f.write(f"\n... and {len(orphans) - 20} more\n")
            else:
                f.write("No orphan modules found.\n")
            f.write("\n")
            
            # Hotspots (highest degree modules)
            f.write("## Hotspot Modules (Highest Degree)\n\n")
            hotspots = self._find_hotspots(nodes, edges, top_n=20)
            f.write("| Rank | Module | In-Degree | Out-Degree | Total |\n")
            f.write("|------|--------|-----------|------------|-------|\n")
            for i, (mod, in_deg, out_deg) in enumerate(hotspots, 1):
                f.write(f"| {i} | `{mod}` | {in_deg} | {out_deg} | {in_deg + out_deg} |\n")
            f.write("\n")
            
            # Largest files
            f.write("## Largest Python Files\n\n")
            py_files_by_size = [(path, meta) for path, meta in file_inventory.items() 
                               if meta['mime'] == 'text/x-python']
            py_files_by_size.sort(key=lambda x: x[1]['size'], reverse=True)
            
            f.write("| Rank | File | Size (KB) |\n")
            f.write("|------|------|----------|\n")
            for i, (path, meta) in enumerate(py_files_by_size[:20], 1):
                size_kb = meta['size'] / 1024
                rel_path = Path(path).relative_to(provenance['params']['root'])
                f.write(f"| {i} | `{rel_path}` | {size_kb:.1f} |\n")
            f.write("\n")
            
            # Integrity metrics
            f.write("## Integrity Metrics\n\n")
            unresolved_count = sum(1 for e in edges if e.get('meta', {}).get('unresolved'))
            total_imports = sum(1 for e in edges if e['type'] in ['import', 'from_import'])
            resolved_pct = 100 * (total_imports - unresolved_count) / total_imports if total_imports > 0 else 100
            
            f.write(f"- **Total Imports:** {total_imports}\n")
            f.write(f"- **Unresolved Imports:** {unresolved_count}\n")
            f.write(f"- **Resolution Rate:** {resolved_pct:.1f}%\n\n")
            
            # Artifacts reference
            f.write("---\n\n")
            f.write("## Generated Artifacts\n\n")
            f.write("- `graph/code_graph.json` - Complete graph (nodes + edges)\n")
            f.write("- `graph/nodes.json` - All nodes\n")
            f.write("- `graph/edges.json` - All edges\n")
            f.write("- `graph/symbol_index.json` - Symbol lookup index\n")
            f.write("- `graph/call_index.json` - Call graph per file\n")
            f.write("- `graph/file_index.json` - File inventory\n")
            f.write("- `graph/import_matrix.csv` - Module import matrix\n")
            f.write("- `graph/edges.csv` - Edge list\n")
            f.write("- `graph/code_graph.dot` - Graphviz DOT\n")
            f.write("- `graph/code_graph.mmd` - Mermaid diagram\n")
            f.write("- `provenance.json` - Run metadata\n\n")
        
        self.logger.info("emit_markdown", file="summary.md")
        return output_path
    
    def _find_orphans(self, nodes: List, edges: List) -> List[str]:
        """Find modules with zero in-degree and zero out-degree"""
        module_nodes = {n['qualname'] for n in nodes if n['kind'] == 'module' and 'qualname' in n}
        connected_modules = set()
        
        for edge in edges:
            if edge['type'] in ['import', 'from_import']:
                src = edge['src'].split(':')[1] if ':' in edge['src'] else edge['src']
                dst = edge['dst'].split(':')[1] if ':' in edge['dst'] else edge['dst']
                connected_modules.add(src)
                connected_modules.add(dst)
        
        return list(module_nodes - connected_modules)
    
    def _find_hotspots(self, nodes: List, edges: List, top_n: int = 20) -> List[tuple]:
        """Find modules with highest degree (in + out)"""
        in_degree = Counter()
        out_degree = Counter()
        
        for edge in edges:
            if edge['type'] in ['import', 'from_import']:
                src = edge['src'].split(':')[1] if ':' in edge['src'] else edge['src']
                dst = edge['dst'].split(':')[1] if ':' in edge['dst'] else edge['dst']
                out_degree[src] += 1
                in_degree[dst] += 1
        
        # Calculate total degree
        all_modules = set(in_degree.keys()) | set(out_degree.keys())
        degrees = [(mod, in_degree[mod], out_degree[mod]) for mod in all_modules]
        degrees.sort(key=lambda x: x[1] + x[2], reverse=True)
        
        return degrees[:top_n]

