"""
Cross-file reference hints
Lightweight heuristic for symbol usage across files
"""

import ast
from typing import List, Tuple, Set, Dict


class XRefExtractor:
    """Extracts cross-file reference hints"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def extract_xrefs(self, tree: ast.AST, module_qual: str, 
                     imported_modules: Set[str], 
                     all_symbols: Dict[str, Dict]) -> List[Tuple[str, str, str]]:
        """
        Extract cross-file symbol references
        Returns: list of (from_module, to_symbol_qualname, confidence) tuples
        """
        xrefs = []
        names_used = set()
        
        # Collect all Name and Attribute nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names_used.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Collect attribute access patterns
                attr_chain = self._get_attr_chain(node)
                if attr_chain:
                    names_used.add(attr_chain)
        
        # Match against known symbols
        for name in names_used:
            for symbol_qual, symbol_info in all_symbols.items():
                # Check if this symbol matches and is from an imported module
                symbol_module = '.'.join(symbol_qual.split('.')[:-1])
                symbol_name = symbol_qual.split('.')[-1]
                
                if symbol_name == name and symbol_module in imported_modules:
                    # Likely reference to this symbol
                    confidence = "med" if symbol_module in imported_modules else "low"
                    xrefs.append((module_qual, symbol_qual, confidence))
        
        return xrefs
    
    def _get_attr_chain(self, node: ast.Attribute) -> str:
        """Extract full attribute chain (e.g., obj.attr.method)"""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        
        return '.'.join(reversed(parts)) if parts else ""

