#!/usr/bin/env python3
"""
Sandbox Mini-IDE for LLM Auditor
Provides secure, isolated development environment for AI code fixes.

FEATURES:
- Read/Write/Review code files
- Syntax validation
- Code analysis
- Diff generation
- All operations confined to sandbox
"""

import ast
import difflib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .sandbox_security import SandboxSecurityManager

logger = logging.getLogger(__name__)


class SandboxIDE:
    """
    Secure mini-IDE for LLM Auditor.
    
    All operations are confined to sandbox with security validation.
    """
    
    def __init__(self, sandbox_root: Path, aios_root: Path):
        self.sandbox_root = sandbox_root
        self.aios_root = aios_root
        self.security = SandboxSecurityManager(sandbox_root, aios_root)
        
        # Track file versions for rollback
        self.file_history = {}  # {file_path: [version1, version2, ...]}
        
        logger.info(f"Sandbox IDE initialized: {sandbox_root}")
    
    def read_file(self, file_path: str) -> Dict[str, any]:
        """
        Securely read a file from sandbox.
        
        Returns:
            Dict with content and metadata
        """
        # Validate path
        validated_path = self.security.validate_path(file_path, allow_write=False)
        if not validated_path:
            return {
                'success': False,
                'error': 'Path validation failed - outside sandbox or forbidden',
                'file_path': file_path
            }
        
        try:
            # Read file
            content = validated_path.read_text(encoding='utf-8')
            
            # Get metadata
            stats = validated_path.stat()
            
            return {
                'success': True,
                'file_path': str(validated_path.relative_to(self.sandbox_root)),
                'content': content,
                'lines': len(content.split('\n')),
                'size_bytes': stats.st_size,
                'extension': validated_path.suffix
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def write_file(self, file_path: str, content: str) -> Dict[str, any]:
        """
        Securely write a file to sandbox.
        
        Validates content for security issues before writing.
        """
        # Validate path
        validated_path = self.security.validate_path(file_path, allow_write=True)
        if not validated_path:
            return {
                'success': False,
                'error': 'Path validation failed - outside sandbox or forbidden',
                'file_path': file_path
            }
        
        # Validate code content (if Python file)
        if validated_path.suffix == '.py':
            validation = self.security.validate_code(content)
            if not validation['safe']:
                return {
                    'success': False,
                    'error': 'Code security validation failed',
                    'violations': validation['violations'],
                    'file_path': file_path
                }
        
        try:
            # Save current version to history (if exists)
            if validated_path.exists():
                current_content = validated_path.read_text(encoding='utf-8')
                self._save_to_history(validated_path, current_content)
            
            # Write new content
            validated_path.write_text(content, encoding='utf-8')
            
            return {
                'success': True,
                'file_path': str(validated_path.relative_to(self.sandbox_root)),
                'lines': len(content.split('\n')),
                'size_bytes': len(content.encode('utf-8'))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def modify_file(self, file_path: str, search: str, replace: str) -> Dict[str, any]:
        """
        Securely modify a file with search/replace.
        
        Validates both search and replace strings for security.
        """
        # Validate path
        validated_path = self.security.validate_path(file_path, allow_write=True)
        if not validated_path:
            return {
                'success': False,
                'error': 'Path validation failed',
                'file_path': file_path
            }
        
        if not validated_path.exists():
            return {
                'success': False,
                'error': 'File not found',
                'file_path': file_path
            }
        
        try:
            # Read current content
            current_content = validated_path.read_text(encoding='utf-8')
            
            # Perform replacement
            if search not in current_content:
                return {
                    'success': False,
                    'error': 'Search string not found',
                    'file_path': file_path
                }
            
            new_content = current_content.replace(search, replace, 1)  # Replace once
            
            # Validate new content (if Python)
            if validated_path.suffix == '.py':
                validation = self.security.validate_code(new_content)
                if not validation['safe']:
                    return {
                        'success': False,
                        'error': 'Modified code failed security validation',
                        'violations': validation['violations'],
                        'file_path': file_path
                    }
            
            # Save to history
            self._save_to_history(validated_path, current_content)
            
            # Write modified content
            validated_path.write_text(new_content, encoding='utf-8')
            
            return {
                'success': True,
                'file_path': str(validated_path.relative_to(self.sandbox_root)),
                'modified': True,
                'lines_changed': abs(len(new_content.split('\n')) - len(current_content.split('\n')))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def list_files(self) -> Dict[str, any]:
        """List all files in sandbox"""
        try:
            files = []
            for file_path in self.sandbox_root.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.sandbox_root)
                    stats = file_path.stat()
                    files.append({
                        'path': str(relative_path),
                        'size_bytes': stats.st_size,
                        'extension': file_path.suffix
                    })
            
            return {
                'success': True,
                'files': files,
                'total_files': len(files)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files': []
            }
    
    def verify_syntax(self, file_path: str) -> Dict[str, any]:
        """
        Verify Python syntax without executing code.
        
        Uses AST parsing for safe validation.
        """
        # Validate path
        validated_path = self.security.validate_path(file_path, allow_write=False)
        if not validated_path:
            return {
                'success': False,
                'error': 'Path validation failed',
                'file_path': file_path
            }
        
        if not validated_path.exists():
            return {
                'success': False,
                'error': 'File not found',
                'file_path': file_path
            }
        
        try:
            content = validated_path.read_text(encoding='utf-8')
            
            # Parse AST (safe - doesn't execute)
            ast.parse(content)
            
            return {
                'success': True,
                'valid': True,
                'file_path': str(validated_path.relative_to(self.sandbox_root))
            }
        
        except SyntaxError as e:
            return {
                'success': True,
                'valid': False,
                'error': str(e),
                'line': e.lineno,
                'offset': e.offset,
                'file_path': file_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def review_code(self, file_path: str) -> Dict[str, any]:
        """
        Review code for quality and security issues.
        
        Performs:
        - Syntax check
        - Security scan
        - Code smell detection
        - Complexity analysis
        """
        # Validate path
        validated_path = self.security.validate_path(file_path, allow_write=False)
        if not validated_path:
            return {
                'success': False,
                'error': 'Path validation failed',
                'file_path': file_path
            }
        
        if not validated_path.exists():
            return {
                'success': False,
                'error': 'File not found',
                'file_path': file_path
            }
        
        try:
            content = validated_path.read_text(encoding='utf-8')
            
            # Syntax check
            syntax_valid = True
            syntax_error = None
            try:
                ast.parse(content)
            except SyntaxError as e:
                syntax_valid = False
                syntax_error = str(e)
            
            # Security check
            security_check = self.security.validate_code(content)
            
            # Code smells
            smells = self._detect_code_smells(content)
            
            # Complexity
            complexity = self._analyze_complexity(content)
            
            return {
                'success': True,
                'file_path': str(validated_path.relative_to(self.sandbox_root)),
                'syntax_valid': syntax_valid,
                'syntax_error': syntax_error,
                'security_safe': security_check['safe'],
                'security_violations': security_check['violations'],
                'code_smells': smells,
                'complexity': complexity,
                'overall_quality': 'good' if (syntax_valid and security_check['safe'] and len(smells) == 0) else 'needs_work'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def generate_diff(self, file_path: str, original_content: str = None) -> Dict[str, any]:
        """
        Generate diff showing changes made to file.
        
        Args:
            file_path: File to diff
            original_content: Original content (or load from history)
        """
        # Validate path
        validated_path = self.security.validate_path(file_path, allow_write=False)
        if not validated_path:
            return {
                'success': False,
                'error': 'Path validation failed',
                'file_path': file_path
            }
        
        if not validated_path.exists():
            return {
                'success': False,
                'error': 'File not found',
                'file_path': file_path
            }
        
        try:
            # Get current content
            current_content = validated_path.read_text(encoding='utf-8')
            
            # Get original content
            if original_content is None:
                # Try to get from history
                history = self.file_history.get(str(validated_path), [])
                if history:
                    original_content = history[-1]
                else:
                    return {
                        'success': False,
                        'error': 'No history available for diff',
                        'file_path': file_path
                    }
            
            # Generate diff
            original_lines = original_content.split('\n')
            current_lines = current_content.split('\n')
            
            diff = list(difflib.unified_diff(
                original_lines,
                current_lines,
                fromfile=f"{file_path} (original)",
                tofile=f"{file_path} (modified)",
                lineterm=''
            ))
            
            return {
                'success': True,
                'file_path': str(validated_path.relative_to(self.sandbox_root)),
                'diff': '\n'.join(diff),
                'lines_added': sum(1 for line in diff if line.startswith('+')),
                'lines_removed': sum(1 for line in diff if line.startswith('-')),
                'has_changes': len(diff) > 0
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def _save_to_history(self, path: Path, content: str):
        """Save file version to history"""
        key = str(path)
        if key not in self.file_history:
            self.file_history[key] = []
        self.file_history[key].append(content)
        
        # Keep last 5 versions only
        if len(self.file_history[key]) > 5:
            self.file_history[key] = self.file_history[key][-5:]
    
    def _detect_code_smells(self, code: str) -> List[str]:
        """Detect common code smells"""
        smells = []
        
        # Bare except
        if re.search(r'except\s*:', code):
            smells.append("bare_except")
        
        # Print instead of logging
        if re.search(r'\bprint\s*\(', code):
            smells.append("print_instead_of_log")
        
        # TODO/FIXME
        if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', code):
            smells.append("maintenance_markers")
        
        # Long lines (>120 chars)
        long_lines = [i for i, line in enumerate(code.split('\n'), 1) if len(line) > 120]
        if long_lines:
            smells.append(f"long_lines ({len(long_lines)} lines)")
        
        return smells
    
    def _analyze_complexity(self, code: str) -> Dict[str, any]:
        """Analyze code complexity"""
        try:
            tree = ast.parse(code)
            
            # Count functions and classes
            functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            
            # Count imports
            imports = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
            
            # Lines of code
            lines = len(code.split('\n'))
            
            return {
                'lines': lines,
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'complexity': 'low' if lines < 100 else ('medium' if lines < 300 else 'high')
            }
        
        except Exception:
            return {
                'lines': len(code.split('\n')),
                'complexity': 'unknown'
            }
    
    def copy_from_aios(self, source_path: str, dest_name: str = None) -> Dict[str, any]:
        """
        Copy file from AIOS source to sandbox (read-only access to AIOS).
        
        Args:
            source_path: Path within AIOS root
            dest_name: Optional destination name in sandbox
        """
        # Validate source can be copied
        if not self.security.can_copy_from_aios(source_path):
            return {
                'success': False,
                'error': 'Source file cannot be copied (security policy)',
                'source': source_path
            }
        
        try:
            source = (self.aios_root / source_path).resolve()
            
            # Determine destination
            if dest_name:
                dest = self.sandbox_root / dest_name
            else:
                dest = self.sandbox_root / source.name
            
            # Validate destination
            validated_dest = self.security.validate_path(str(dest), allow_write=True)
            if not validated_dest:
                return {
                    'success': False,
                    'error': 'Destination path validation failed',
                    'source': source_path
                }
            
            # Check sandbox capacity
            capacity = self.security.check_sandbox_capacity()
            if capacity['at_capacity']:
                return {
                    'success': False,
                    'error': f"Sandbox at capacity ({capacity['file_count']} files)",
                    'source': source_path
                }
            
            # Copy file
            content = source.read_text(encoding='utf-8')
            validated_dest.write_text(content, encoding='utf-8')
            
            # Save to history
            self._save_to_history(validated_dest, content)
            
            return {
                'success': True,
                'source': source_path,
                'destination': str(validated_dest.relative_to(self.sandbox_root)),
                'size_bytes': len(content.encode('utf-8'))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': source_path
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, any]:
        """Get detailed information about a sandbox file"""
        validated_path = self.security.validate_path(file_path, allow_write=False)
        if not validated_path:
            return {
                'success': False,
                'error': 'Path validation failed',
                'file_path': file_path
            }
        
        if not validated_path.exists():
            return {
                'success': False,
                'error': 'File not found',
                'file_path': file_path
            }
        
        try:
            stats = validated_path.stat()
            content = validated_path.read_text(encoding='utf-8')
            
            return {
                'success': True,
                'file_path': str(validated_path.relative_to(self.sandbox_root)),
                'absolute_path': str(validated_path),
                'size_bytes': stats.st_size,
                'lines': len(content.split('\n')),
                'extension': validated_path.suffix,
                'in_history': str(validated_path) in self.file_history,
                'history_versions': len(self.file_history.get(str(validated_path), []))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def get_sandbox_status(self) -> Dict[str, any]:
        """Get overall sandbox status"""
        capacity = self.security.check_sandbox_capacity()
        files_list = self.list_files()
        security_summary = self.security.get_security_summary()
        
        return {
            'sandbox_root': str(self.sandbox_root),
            'total_files': capacity['file_count'],
            'total_size_mb': capacity['total_size_mb'],
            'at_capacity': capacity['at_capacity'],
            'files_tracked_in_history': len(self.file_history),
            'security': security_summary,
            'operational': True
        }

