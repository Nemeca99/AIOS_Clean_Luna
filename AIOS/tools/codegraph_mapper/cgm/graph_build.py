"""
Graph builder - assembles complete code graph from all extracted data
"""

from pathlib import Path
from typing import Dict, List
from .py_ast import parse_python_ast, module_name_for, get_docstring
from .imports import ImportExtractor
from .symbols import SymbolExtractor
from .callgraph import CallGraphExtractor
from .xref import XRefExtractor


class GraphBuilder:
    """Builds complete code graph from file inventory"""
    
    def __init__(self, root: Path, file_inventory: Dict, logger):
        self.root = root
        self.file_inventory = file_inventory
        self.logger = logger
        
        # Extractors
        self.import_extractor = ImportExtractor(logger)
        self.symbol_extractor = SymbolExtractor(logger)
        self.call_extractor = CallGraphExtractor(logger)
        self.xref_extractor = XRefExtractor(logger)
        
        # Output structures
        self.nodes = []
        self.edges = []
        self.symbol_index = {}
        self.call_index = {}
        self.modules = set()
        
        # Tracking
        self.py_files_processed = 0
        self.parse_failures = 0
    
    def build(self) -> Dict:
        """
        Build complete graph
        Returns: {nodes, edges, symbol_index, call_index, stats}
        """
        self.logger.info("graph_build_start")
        
        # First pass: collect all Python files and module names
        py_files = []
        for path, meta in self.file_inventory.items():
            if meta['mime'] == 'text/x-python':
                py_files.append(Path(path))
        
        # Build module name mapping
        module_map = {}
        for py_file in py_files:
            mod_name = module_name_for(py_file, self.root)
            self.modules.add(mod_name)
            module_map[str(py_file)] = mod_name
        
        # Second pass: parse AST and extract everything
        for py_file in py_files:
            self._process_python_file(py_file, module_map)
        
        # Third pass: build cross-file references
        self._build_xrefs()
        
        self.logger.info("graph_build_complete",
                        nodes=len(self.nodes),
                        edges=len(self.edges),
                        modules=len(self.modules),
                        py_files=self.py_files_processed,
                        parse_failures=self.parse_failures)
        
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "symbol_index": self.symbol_index,
            "call_index": self.call_index,
            "stats": {
                "nodes": len(self.nodes),
                "edges": len(self.edges),
                "modules": len(self.modules),
                "py_files": self.py_files_processed,
                "parse_failures": self.parse_failures
            }
        }
    
    def _process_python_file(self, py_file: Path, module_map: Dict):
        """Process single Python file"""
        tree = parse_python_ast(py_file, self.logger)
        if not tree:
            self.parse_failures += 1
            return
        
        self.py_files_processed += 1
        module_qual = module_map[str(py_file)]
        file_meta = self.file_inventory[str(py_file)]
        
        # Add file node
        self.nodes.append({
            "id": f"file:{py_file}",
            "kind": "file",
            "path": str(py_file),
            "name": py_file.name,
            "hash": file_meta['sha256'],
            "meta": file_meta
        })
        
        # Add module node
        self.nodes.append({
            "id": f"module:{module_qual}",
            "kind": "module",
            "path": str(py_file),
            "name": module_qual.split('.')[-1],
            "qualname": module_qual,
            "doc": get_docstring(tree),
            "hash": file_meta['sha256']
        })
        
        # Extract imports
        imports = self.import_extractor.extract_imports(tree, module_qual)
        for imp in imports:
            # Resolve import target
            target, is_resolved = self.import_extractor.resolve_import_target(
                imp, module_qual, self.modules
            )
            
            # Create edge
            edge = {
                "src": f"module:{module_qual}",
                "dst": f"module:{target}",
                "type": imp['type'],
                "meta": {
                    "names": imp['names'],
                    "unresolved": not is_resolved
                }
            }
            
            if imp['alias']:
                edge["meta"]["alias"] = imp['alias']
            
            self.edges.append(edge)
        
        # Extract symbols
        symbols = self.symbol_extractor.extract_symbols(tree, module_qual, str(py_file))
        for sym in symbols:
            # Add symbol node
            node = {
                "id": f"{sym['kind']}:{sym['qualname']}",
                "kind": sym['kind'],
                "path": str(py_file),
                "name": sym['name'],
                "qualname": sym['qualname'],
                "span": sym['span'],
                "doc": sym.get('doc')
            }
            
            if 'decorators' in sym:
                node['meta'] = {"decorators": sym['decorators']}
            
            self.nodes.append(node)
            
            # Index symbol
            self.symbol_index[sym['qualname']] = {
                "kind": sym['kind'],
                "file": str(py_file),
                "span": [sym['span']['start']['line'], sym['span']['end']['line']],
                "doc": sym.get('doc')
            }
        
        # Extract call graph
        calls = self.call_extractor.extract_calls(tree, module_qual)
        
        # Store in call index
        if str(py_file) not in self.call_index:
            self.call_index[str(py_file)] = {}
        
        for caller, callee in calls:
            if caller not in self.call_index[str(py_file)]:
                self.call_index[str(py_file)][caller] = []
            
            if callee not in self.call_index[str(py_file)][caller]:
                self.call_index[str(py_file)][caller].append(callee)
            
            # Add call edge
            self.edges.append({
                "src": f"function:{caller}",
                "dst": f"function:{callee}",
                "type": "call_intra",
                "meta": {}
            })
    
    def _build_xrefs(self):
        """Build cross-file reference hints (lightweight heuristic)"""
        # TODO: Implement if needed
        # This would require tracking which modules are imported where
        # and matching Name/Attribute nodes against symbol index
        pass

