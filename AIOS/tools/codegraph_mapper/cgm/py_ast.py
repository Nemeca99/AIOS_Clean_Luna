"""
Python AST parser for CodeGraph Mapper
Safe parsing with encoding detection and fallback
"""

import ast
import tokenize
from pathlib import Path
from typing import Optional, Tuple


def read_py_text(path: Path) -> Tuple[str, str]:
    """
    Read Python file with encoding detection
    Returns: (text, encoding)
    """
    with open(path, 'rb') as rb:
        try:
            # Detect encoding from Python file header
            encoding, _ = tokenize.detect_encoding(rb.readline)
            rb.seek(0)
            text = rb.read().decode(encoding, errors="replace")
            return text, encoding
        except Exception:
            # Fallback to UTF-8 with replacement
            rb.seek(0)
            text = rb.read().decode('utf-8', errors="replace")
            return text, "utf-8"


def parse_python_ast(path: Path, logger) -> Optional[ast.AST]:
    """
    Parse Python file into AST
    Returns: AST tree or None on failure
    """
    try:
        text, encoding = read_py_text(path)
        
        # Check if encoding fallback happened (contains replacement char)
        if '�' in text:
            logger.warn("decode_fallback", 
                       path=str(path), 
                       encoding=encoding,
                       replaced=text.count('�'))
        
        # Parse with AST
        tree = ast.parse(text, filename=str(path), mode="exec", type_comments=True)
        return tree
        
    except SyntaxError as e:
        logger.warn("parse_syntax_error", 
                   path=str(path), 
                   line=e.lineno, 
                   msg=str(e))
        return None
    except Exception as e:
        logger.warn("parse_failed", 
                   path=str(path), 
                   reason=str(e))
        return None


def module_name_for(path: Path, root: Path) -> str:
    """
    Convert file path to Python module name
    Examples:
        L:\AIOS\luna_core\personality.py -> luna_core.personality
        L:\AIOS\luna_core\__init__.py -> luna_core
    """
    try:
        rel = path.relative_to(root)
        rel_str = str(rel).replace('\\', '/')
        
        # Handle __init__.py specially
        if rel_str.endswith('__init__.py'):
            rel_str = rel_str[:-12]  # Remove __init__.py
        elif rel_str.endswith('.py'):
            rel_str = rel_str[:-3]  # Remove .py
        
        # Convert slashes to dots
        module_name = rel_str.replace('/', '.').strip('.')
        return module_name
    
    except ValueError:
        # Path not relative to root
        return path.stem


def get_docstring(node: ast.AST) -> Optional[str]:
    """Extract first line of docstring from AST node"""
    docstring = ast.get_docstring(node)
    if docstring:
        # Return first line only
        return docstring.split('\n')[0].strip()
    return None

