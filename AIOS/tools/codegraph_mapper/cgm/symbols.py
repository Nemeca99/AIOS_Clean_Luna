"""
Symbol index builder
Extracts classes, functions, and constants from Python AST
"""

import ast
from typing import List, Dict, Optional


class SymbolExtractor:
    """Extracts symbols (classes, functions, constants) from AST"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def extract_symbols(self, tree: ast.AST, module_qual: str, file_path: str) -> List[Dict]:
        """
        Extract all symbols from top-level AST
        Returns: list of {kind, qual, name, span, doc, decorators}
        """
        symbols = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols.append(self._extract_class(node, module_qual, file_path))
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(self._extract_function(node, module_qual, file_path))
            
            elif isinstance(node, ast.Assign):
                # Extract ALL_CAPS constants
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        symbols.append(self._extract_const(target, node, module_qual, file_path))
        
        return symbols
    
    def _extract_class(self, node: ast.ClassDef, module_qual: str, file_path: str) -> Dict:
        """Extract class symbol"""
        qualname = f"{module_qual}.{node.name}"
        
        return {
            "kind": "class",
            "name": node.name,
            "qualname": qualname,
            "file": file_path,
            "span": {
                "start": {"line": node.lineno, "col": node.col_offset},
                "end": {"line": node.end_lineno or node.lineno, "col": node.end_col_offset or 0}
            },
            "doc": self._get_docstring(node),
            "decorators": [self._decorator_name(d) for d in node.decorator_list],
            "bases": [self._expr_to_str(b) for b in node.bases]
        }
    
    def _extract_function(self, node: ast.FunctionDef, module_qual: str, file_path: str) -> Dict:
        """Extract function symbol"""
        qualname = f"{module_qual}.{node.name}"
        
        return {
            "kind": "function",
            "name": node.name,
            "qualname": qualname,
            "file": file_path,
            "span": {
                "start": {"line": node.lineno, "col": node.col_offset},
                "end": {"line": node.end_lineno or node.lineno, "col": node.end_col_offset or 0}
            },
            "doc": self._get_docstring(node),
            "decorators": [self._decorator_name(d) for d in node.decorator_list],
            "async": isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _extract_const(self, target: ast.Name, node: ast.Assign, module_qual: str, file_path: str) -> Dict:
        """Extract constant symbol"""
        qualname = f"{module_qual}.{target.id}"
        
        return {
            "kind": "const",
            "name": target.id,
            "qualname": qualname,
            "file": file_path,
            "span": {
                "start": {"line": node.lineno, "col": node.col_offset},
                "end": {"line": node.end_lineno or node.lineno, "col": node.end_col_offset or 0}
            },
            "doc": None
        }
    
    def _get_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract first line of docstring"""
        docstring = ast.get_docstring(node)
        if docstring:
            return docstring.split('\n')[0].strip()
        return None
    
    def _decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name as string"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return self._expr_to_str(decorator)
        elif isinstance(decorator, ast.Call):
            return self._expr_to_str(decorator.func)
        return str(type(decorator).__name__)
    
    def _expr_to_str(self, expr: ast.expr) -> str:
        """Convert AST expression to string (best effort)"""
        if isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.Attribute):
            value_str = self._expr_to_str(expr.value)
            return f"{value_str}.{expr.attr}"
        elif isinstance(expr, ast.Constant):
            return str(expr.value)
        return "<?>"

