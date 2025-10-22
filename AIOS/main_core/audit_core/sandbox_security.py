#!/usr/bin/env python3
"""
Sandbox Security Manager
Enforces strict isolation and security for the LLM Auditor sandbox.

SECURITY PRINCIPLES:
1. Sandbox-only access (no escape to parent directories)
2. No command execution (no subprocess, eval, exec)
3. Path validation (prevent directory traversal)
4. File size limits (prevent resource exhaustion)
5. Whitelist-only operations (explicit allow, implicit deny)
6. Read-only access to AIOS source (can copy, not modify)
7. Write access only to sandbox
"""

import re
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class SecurityPolicy:
    """Security policy for sandbox operations"""
    
    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Maximum files in sandbox
    MAX_SANDBOX_FILES = 100
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.py', '.json', '.yaml', '.yml', '.txt', '.md'}
    
    # Forbidden patterns in code
    FORBIDDEN_PATTERNS = [
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'\b__import__\s*\(',
        r'\bsubprocess\.',
        r'\bos\.system\s*\(',
        r'\bos\.popen\s*\(',
        r'\bos\.spawn',
        r'\bshutil\.rmtree\s*\(',
        r'\bopen\s*\([^)]*["\']w["\']',  # Write to arbitrary paths
        r'\bPath\s*\(["\']\/[^"\']*["\']',  # Absolute paths
        r'\brequests\.(get|post|put|delete)\s*\(',  # Network access
        r'\bsocket\.',  # Socket access
        r'\b__file__\b',  # File system introspection
        r'\bglobals\s*\(',  # Global namespace access
        r'\blocals\s*\(',  # Local namespace access
        r'\bsetattr\s*\(',  # Dynamic attribute modification
        r'\bdelattr\s*\(',  # Attribute deletion
    ]
    
    # Allowed Python builtins (whitelist)
    ALLOWED_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter', 
        'float', 'format', 'int', 'isinstance', 'len', 'list', 'map',
        'max', 'min', 'range', 'reversed', 'round', 'set', 'sorted',
        'str', 'sum', 'tuple', 'type', 'zip',
        # String methods
        'join', 'split', 'strip', 'replace', 'startswith', 'endswith',
        # Safe operations
        're', 'json', 'pathlib.Path'
    }


class SandboxSecurityManager:
    """
    Enforces security boundaries for the LLM Auditor sandbox.
    
    THREAT MODEL:
    - Malicious LLM trying to escape sandbox
    - Code injection via tool parameters
    - Directory traversal attacks
    - Resource exhaustion
    - Network access attempts
    """
    
    def __init__(self, sandbox_root: Path, aios_root: Path):
        self.sandbox_root = sandbox_root.resolve()
        self.aios_root = aios_root.resolve()
        self.policy = SecurityPolicy()
        
        # Ensure sandbox exists
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Sandbox Security initialized: {self.sandbox_root}")
    
    def validate_path(self, path: str, allow_write: bool = False) -> Optional[Path]:
        """
        Validate path is within sandbox and safe.
        
        Args:
            path: Path to validate
            allow_write: If True, allows write operations
            
        Returns:
            Resolved Path if valid, None if rejected
        """
        try:
            # Convert to Path (don't resolve yet if doesn't exist)
            target = Path(path)
            
            # If relative, make relative to sandbox
            if not target.is_absolute():
                target = self.sandbox_root / target
            
            # Now resolve (works even if file doesn't exist)
            target = target.resolve()
            
            # Check if within sandbox
            if not self._is_in_sandbox(target):
                logger.warning(f"Path outside sandbox rejected: {path}")
                return None
            
            # Check for directory traversal
            if '..' in str(path) or '~' in str(path):
                logger.warning(f"Directory traversal rejected: {path}")
                return None
            
            # Check extension
            if target.suffix and target.suffix not in self.policy.ALLOWED_EXTENSIONS:
                logger.warning(f"Forbidden file extension rejected: {path}")
                return None
            
            # If write operation, check parent exists
            if allow_write and not target.parent.exists():
                logger.warning(f"Write to non-existent directory rejected: {path}")
                return None
            
            # Check file size limit
            if target.exists() and target.stat().st_size > self.policy.MAX_FILE_SIZE:
                logger.warning(f"File too large rejected: {path}")
                return None
            
            return target
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return None
    
    def _is_in_sandbox(self, path: Path) -> bool:
        """Check if path is within sandbox"""
        try:
            # Try to resolve relative to sandbox
            path.relative_to(self.sandbox_root)
            return True
        except ValueError:
            return False
    
    def validate_code(self, code: str) -> Dict[str, any]:
        """
        Validate code for security issues.
        
        Checks for:
        - Forbidden function calls (eval, exec, subprocess)
        - Network access attempts
        - File system escape attempts
        - Dangerous imports
        
        Returns:
            Dict with 'safe' boolean and 'violations' list
        """
        violations = []
        
        # Check forbidden patterns
        for pattern in self.policy.FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, code, re.MULTILINE | re.IGNORECASE)
            if matches:
                violations.append(f"Forbidden pattern: {pattern[:30]}... (found {len(matches)} times)")
        
        # Parse and check AST for dangerous operations
        try:
            tree = ast.parse(code)
            ast_violations = self._check_ast_security(tree)
            violations.extend(ast_violations)
        except SyntaxError as e:
            # Syntax errors are caught separately, not a security issue
            pass
        except Exception as e:
            violations.append(f"AST parsing error: {str(e)[:100]}")
        
        return {
            'safe': len(violations) == 0,
            'violations': violations,
            'code_length': len(code)
        }
    
    def _check_ast_security(self, tree: ast.AST) -> List[str]:
        """Check AST for security violations"""
        violations = []
        
        for node in ast.walk(tree):
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['subprocess', 'os', 'sys', 'socket', 'requests']:
                        violations.append(f"Dangerous import: {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module in ['subprocess', 'os', 'sys', 'socket', 'requests']:
                    violations.append(f"Dangerous import from: {node.module}")
            
            # Check for exec/eval
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', '__import__', 'compile']:
                        violations.append(f"Forbidden function call: {node.func.id}")
            
            # Check for file operations with absolute paths
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'open' or node.func.attr == 'write':
                        # Check for absolute path arguments
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                if arg.value.startswith('/') or ':' in arg.value:
                                    violations.append(f"Absolute path in file operation: {arg.value}")
        
        return violations
    
    def can_copy_from_aios(self, source_path: str) -> bool:
        """
        Check if file can be copied from AIOS source to sandbox.
        
        Rules:
        - Must be within AIOS root
        - Must be a Python file or config
        - Must not be in excluded directories
        """
        try:
            source = Path(source_path).resolve()
            
            # Must be within AIOS root
            try:
                source.relative_to(self.aios_root)
            except ValueError:
                logger.warning(f"Source outside AIOS root: {source_path}")
                return False
            
            # Check extension
            if source.suffix not in self.policy.ALLOWED_EXTENSIONS:
                logger.warning(f"Forbidden extension for copy: {source_path}")
                return False
            
            # Excluded directories
            excluded_dirs = {
                '__pycache__', '.git', '.venv', 'venv', 'node_modules',
                'reports', 'logs'
            }
            
            if any(excluded in source.parts for excluded in excluded_dirs):
                logger.warning(f"Excluded directory: {source_path}")
                return False
            
            # File must exist
            if not source.exists():
                logger.warning(f"Source file not found: {source_path}")
                return False
            
            # File size check
            if source.stat().st_size > self.policy.MAX_FILE_SIZE:
                logger.warning(f"Source file too large: {source_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Copy validation error: {e}")
            return False
    
    def check_sandbox_capacity(self) -> Dict[str, any]:
        """Check if sandbox has capacity for more files"""
        try:
            file_count = len(list(self.sandbox_root.rglob('*')))
            total_size = sum(f.stat().st_size for f in self.sandbox_root.rglob('*') if f.is_file())
            
            at_capacity = file_count >= self.policy.MAX_SANDBOX_FILES
            
            return {
                'file_count': file_count,
                'total_size_mb': total_size / (1024 * 1024),
                'at_capacity': at_capacity,
                'max_files': self.policy.MAX_SANDBOX_FILES
            }
        except Exception as e:
            logger.error(f"Capacity check error: {e}")
            return {
                'file_count': 0,
                'total_size_mb': 0,
                'at_capacity': True,
                'error': str(e)
            }
    
    def sanitize_tool_call(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """
        Sanitize tool call arguments to prevent injection.
        
        Returns:
            Sanitized arguments if safe, None if rejected
        """
        # Whitelist of allowed tools
        allowed_tools = {
            'read_file', 'write_file', 'modify_file', 
            'list_files', 'verify_syntax', 'review_code',
            'document_new_file_need'
        }
        
        if tool_name not in allowed_tools:
            logger.warning(f"Forbidden tool call: {tool_name}")
            return None
        
        sanitized = {}
        
        # Validate each argument
        for key, value in arguments.items():
            # String arguments - check for injection
            if isinstance(value, str):
                # Remove null bytes
                value = value.replace('\x00', '')
                
                # Check for command injection patterns
                injection_patterns = [
                    r';\s*\w+',  # Command chaining
                    r'\|\s*\w+',  # Pipe to command
                    r'`.*`',  # Backtick execution
                    r'\$\(',  # Command substitution
                    r'>\s*[\w/]',  # Output redirection
                ]
                
                for pattern in injection_patterns:
                    if re.search(pattern, value):
                        logger.warning(f"Injection pattern detected in {key}: {pattern}")
                        return None
                
                # Path arguments - validate
                if 'path' in key.lower() or 'file' in key.lower():
                    validated_path = self.validate_path(value, allow_write=(tool_name in ['write_file', 'modify_file']))
                    if not validated_path:
                        logger.warning(f"Invalid path in {key}: {value}")
                        return None
                    value = str(validated_path)
            
            sanitized[key] = value
        
        return sanitized
    
    def get_security_summary(self) -> Dict[str, any]:
        """Get summary of security status"""
        capacity = self.check_sandbox_capacity()
        
        return {
            'sandbox_root': str(self.sandbox_root),
            'aios_root': str(self.aios_root),
            'sandbox_files': capacity['file_count'],
            'sandbox_size_mb': capacity['total_size_mb'],
            'at_capacity': capacity['at_capacity'],
            'max_file_size_mb': self.policy.MAX_FILE_SIZE / (1024 * 1024),
            'max_files': self.policy.MAX_SANDBOX_FILES,
            'allowed_extensions': list(self.policy.ALLOWED_EXTENSIONS),
            'security_active': True
        }

