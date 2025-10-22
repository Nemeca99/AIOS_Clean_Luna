"""
Import graph extraction from Python AST
"""

import ast
from typing import List, Tuple, Dict


class ImportExtractor:
    """Extracts import relationships from AST"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def extract_imports(self, tree: ast.AST, module_name: str) -> List[Dict]:
        """
        Extract all import statements from AST
        Returns: list of {type, target, names, line}
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "target": alias.name,
                        "alias": alias.asname,
                        "names": [],
                        "line": node.lineno
                    })
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                
                imports.append({
                    "type": "from_import",
                    "target": module,
                    "alias": None,
                    "names": names,
                    "line": node.lineno,
                    "level": node.level  # Relative import level
                })
        
        return imports
    
    def resolve_import_target(self, import_info: Dict, current_module: str, 
                            known_modules: set) -> Tuple[str, bool]:
        """
        Resolve import target to actual module name
        Returns: (resolved_name, is_resolved)
        """
        target = import_info['target']
        
        # Handle relative imports
        if import_info['type'] == 'from_import' and import_info.get('level', 0) > 0:
            # Relative import
            level = import_info['level']
            parts = current_module.split('.')
            
            if level >= len(parts):
                # Can't resolve - goes above root
                return target, False
            
            # Go up 'level' packages
            base_parts = parts[:-level] if level > 0 else parts
            if target:
                resolved = '.'.join(base_parts + [target])
            else:
                resolved = '.'.join(base_parts)
            
            # Check if resolved module exists
            is_resolved = resolved in known_modules
            return resolved, is_resolved
        
        # Absolute import - check if it's in known modules
        is_resolved = target in known_modules or any(target.startswith(m + '.') for m in known_modules)
        return target, is_resolved

