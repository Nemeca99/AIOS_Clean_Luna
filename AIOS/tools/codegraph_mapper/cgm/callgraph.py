"""
Intra-file call graph builder
Extracts function calls within the same file
"""

import ast
from typing import List, Tuple, Dict


class CallGraphExtractor:
    """Builds intra-file call graph from AST"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def extract_calls(self, tree: ast.AST, module_qual: str) -> List[Tuple[str, str]]:
        """
        Extract function calls within file
        Returns: list of (caller_qualname, callee_qualname) tuples
        """
        calls = []
        current_func_stack = []
        
        class CallVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Push current function onto stack
                qualname = f"{module_qual}.{node.name}"
                current_func_stack.append(qualname)
                self.generic_visit(node)
                current_func_stack.pop()
            
            visit_AsyncFunctionDef = visit_FunctionDef
            
            def visit_ClassDef(self, node):
                # Push class onto stack for method qualification
                class_qual = f"{module_qual}.{node.name}"
                
                # Visit methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_qual = f"{class_qual}.{item.name}"
                        current_func_stack.append(method_qual)
                        self.generic_visit(item)
                        current_func_stack.pop()
            
            def visit_Call(self, node):
                if current_func_stack:
                    caller = current_func_stack[-1]
                    callee = None
                    
                    # Try to extract callee name
                    if isinstance(node.func, ast.Name):
                        # Simple function call
                        callee = f"{module_qual}.{node.func.id}"
                    
                    elif isinstance(node.func, ast.Attribute):
                        # Method call or attribute access
                        if isinstance(node.func.value, ast.Name):
                            # obj.method() where obj is a variable
                            callee = f"{module_qual}.{node.func.attr}"
                        elif isinstance(node.func.value, ast.Attribute):
                            # nested.attr.method()
                            callee = f"{module_qual}.{node.func.attr}"
                    
                    if callee:
                        calls.append((caller, callee))
                
                self.generic_visit(node)
        
        visitor = CallVisitor()
        visitor.visit(tree)
        
        return calls

