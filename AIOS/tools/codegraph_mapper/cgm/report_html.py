"""
HTML report generator with interactive visualization
Self-contained, no external CDN dependencies
"""

from pathlib import Path
from typing import Dict, List
from collections import Counter


class HTMLReporter:
    """Generates interactive HTML summary"""
    
    def __init__(self, out_dir: Path, logger):
        self.out_dir = out_dir
        self.logger = logger
        self.reports_dir = out_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, graph_data: Dict, file_inventory: Dict, 
                provenance: Dict) -> Path:
        """
        Generate summary.html with embedded charts
        Returns: path to report
        """
        output_path = self.reports_dir / "summary.html"
        
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        stats = graph_data['stats']
        
        # Calculate metrics
        import_counts = Counter()
        for edge in edges:
            if edge['type'] in ['import', 'from_import']:
                dst = edge['dst'].split(':')[1] if ':' in edge['dst'] else edge['dst']
                import_counts[dst] += 1
        
        top_imports = import_counts.most_common(20)
        
        html = self._build_html(stats, top_imports, provenance)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        self.logger.info("emit_html", file="summary.html")
        return output_path
    
    def _build_html(self, stats: Dict, top_imports: List, provenance: Dict) -> str:
        """Build complete HTML document"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIOS CodeGraph Summary</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ margin: 0 0 10px 0; color: #333; }}
        .meta {{ color: #666; font-size: 14px; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #2563eb; }}
        .stat-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{ margin-top: 0; color: #333; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
        .bar {{
            height: 20px;
            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
            border-radius: 4px;
            margin-top: 4px;
        }}
        .collapsible {{ cursor: pointer; user-select: none; }}
        .collapsible:hover {{ background: #f9fafb; }}
        .content {{ display: none; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ AIOS CodeGraph Summary</h1>
        <div class="meta">
            Run ID: <code>{provenance['run_id']}</code> |
            Generated: {provenance['timestamps']['start']} |
            Duration: {(provenance['timestamps'].get('duration_ms') or 0) / 1000:.1f}s
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{stats.get('files', 0):,}</div>
            <div class="stat-label">Total Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['py_files']:,}</div>
            <div class="stat-label">Python Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['modules']:,}</div>
            <div class="stat-label">Modules</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['nodes']:,}</div>
            <div class="stat-label">Total Nodes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['edges']:,}</div>
            <div class="stat-label">Total Edges</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Top 20 Most Imported Modules</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Module</th>
                    <th>Import Count</th>
                    <th>Visual</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_import_table_rows(top_imports)}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>📁 Quick Links to Artifacts</h2>
        <ul>
            <li><a href="../graph/code_graph.json">Complete Graph (JSON)</a></li>
            <li><a href="../graph/symbol_index.json">Symbol Index</a></li>
            <li><a href="../graph/import_matrix.csv">Import Matrix (CSV)</a></li>
            <li><a href="../graph/code_graph.mmd">Mermaid Diagram</a></li>
            <li><a href="../provenance.json">Provenance Metadata</a></li>
        </ul>
    </div>
    
    <script>
        // Collapsible sections
        document.querySelectorAll('.collapsible').forEach(elem => {{
            elem.addEventListener('click', function() {{
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                if (content.style.display === 'block') {{
                    content.style.display = 'none';
                }} else {{
                    content.style.display = 'block';
                }}
            }});
        }});
    </script>
</body>
</html>"""
    
    def _generate_import_table_rows(self, top_imports: List) -> str:
        """Generate HTML table rows for top imports"""
        if not top_imports:
            return "<tr><td colspan='4'>No imports found</td></tr>"
        
        max_count = top_imports[0][1] if top_imports and len(top_imports) > 0 else 1
        if max_count == 0:
            max_count = 1
        
        rows = []
        
        for i, (mod, count) in enumerate(top_imports, 1):
            bar_width = (count / max_count) * 100 if max_count > 0 else 0
            rows.append(f"""
                <tr>
                    <td>{i}</td>
                    <td><code>{mod}</code></td>
                    <td>{count}</td>
                    <td><div class="bar" style="width: {bar_width}%;"></div></td>
                </tr>""")
        
        return ''.join(rows)

