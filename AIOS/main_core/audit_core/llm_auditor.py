#!/usr/bin/env python3
"""
LLM Auditor - AI-Powered Code Fixer
Uses qwen2.5-coder-3b-instruct via LM Studio for intelligent code fixes.

RULES:
- Can ONLY modify existing files (never create new ones)
- Works in sandbox (copies files, modifies, system replaces)
- Uses tools to edit code
- If new files needed → documents it (doesn't create)
- Backup core restores on failure
"""

import requests
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .sandbox_ide import SandboxIDE
from .sandbox_security import SandboxSecurityManager

logger = logging.getLogger(__name__)


class LLMAuditor:
    """
    LLM-powered code auditor and fixer.
    
    Model: qwen2.5-coder-3b-instruct (LM Studio)
    Role: Analyzes code, generates fixes
    Constraints: Modify only, no new files
    """
    
    def __init__(self, 
                 lm_studio_url: str = "http://localhost:1234",
                 model: str = "qwen2.5-coder-3b-instruct",
                 rag_core = None,
                 sandbox_root: Path = None,
                 aios_root: Path = None):
        self.api_url = f"{lm_studio_url}/v1/chat/completions"
        self.model = model
        self.rag_core = rag_core  # RAG Core for context embedding
        
        # Initialize sandbox IDE (secure environment)
        if sandbox_root is None:
            sandbox_root = Path(__file__).parent / "sandbox" / "pending_fixes"
        if aios_root is None:
            aios_root = Path(__file__).parent.parent.parent
        
        self.sandbox_ide = SandboxIDE(sandbox_root, aios_root)
        self.security = self.sandbox_ide.security
        
        logger.info(f"LLM Auditor: Secure sandbox initialized at {sandbox_root}")
        
        # Define tools
        self.tools = self._define_tools()
        
        # Initialize RAG if not provided
        if self.rag_core is None:
            try:
                from rag_core.rag_core import RAGCore
                self.rag_core = RAGCore()
                logger.info("LLM Auditor: RAG Core integrated for context embedding")
            except Exception as e:
                logger.warning(f"LLM Auditor: RAG Core not available: {e}")
                self.rag_core = None
    
    def _define_tools(self) -> List[Dict]:
        """Define secure mini-IDE tools for the LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a file from the sandbox (secure, path-validated)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file in sandbox (relative path only)"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file in sandbox (security-validated)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file in sandbox"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write (will be security-scanned)"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "modify_file",
                    "description": "Modify an existing file (search and replace). Cannot create new files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to modify"
                            },
                            "search": {
                                "type": "string",
                                "description": "Text to find (must be exact match)"
                            },
                            "replace": {
                                "type": "string",
                                "description": "Text to replace with"
                            }
                        },
                        "required": ["file_path", "search", "replace"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "document_new_file_need",
                    "description": "Document that a new file is needed (cannot create it). System will log requirement.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path where file is needed"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Why this file is needed"
                            },
                            "suggested_content": {
                                "type": "string",
                                "description": "Suggested file content"
                            }
                        },
                        "required": ["file_path", "reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List all files in sandbox",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "review_code",
                    "description": "Review code for quality, security, and best practices",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to review"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_diff",
                    "description": "Generate diff showing changes made to file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to diff"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "copy_from_aios",
                    "description": "Copy file from AIOS source to sandbox (read-only access to AIOS)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_path": {
                                "type": "string",
                                "description": "Path within AIOS (e.g., 'carma_core/carma_core.py')"
                            },
                            "dest_name": {
                                "type": "string",
                                "description": "Optional destination name in sandbox"
                            }
                        },
                        "required": ["source_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_syntax",
                    "description": "Verify Python syntax of file without executing it",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to verify"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            }
        ]
    
    def analyze_and_fix(self, 
                       issue: Dict,
                       sandbox_path: Path) -> Dict:
        """
        Ask LLM to analyze issue and generate fix.
        
        Args:
            issue: Issue details from audit
            sandbox_path: Path to sandbox with file copy
        
        Returns:
            Dict with fix result
        """
        core_name = issue.get('core_name')
        issue_type = issue.get('issue_type')
        file_path = issue.get('file_path')
        
        # Build prompt for LLM
        prompt = self._build_fix_prompt(issue, sandbox_path)
        
        # Call LLM with tools
        response = self._call_llm_with_tools(prompt)
        
        return response
    
    def _get_relevant_context(self, issue: Dict) -> str:
        """Get relevant context from manual using RAG embedder"""
        if not self.rag_core or not self.rag_core.oracle_available:
            return ""
        
        try:
            # Build search query from issue
            core_name = issue.get('core_name', '')
            issue_type = issue.get('issue_type', '')
            
            search_query = f"{core_name} {issue_type} best practices"
            
            # Search manual for relevant guidelines
            results = self.rag_core.search_manual(search_query, core_name, top_k=3)
            
            if not results:
                return ""
            
            # Format context for LLM
            context_parts = []
            for result in results:
                title = result.get('title', '')
                content = result.get('content', '')
                anchor = result.get('anchor', '')
                
                if content:
                    # Extract first 300 chars as context
                    snippet = content[:300].strip()
                    context_parts.append(f"[{anchor}] {title}:\n{snippet}\n")
            
            return "\n".join(context_parts) if context_parts else ""
        
        except Exception as e:
            logger.warning(f"Could not retrieve RAG context: {e}")
            return ""
    
    def _build_fix_prompt(self, issue: Dict, sandbox_path: Path) -> str:
        """Build prompt for LLM auditor with RAG context."""
        # Get relevant context from manual
        context = self._get_relevant_context(issue)
        
        base_prompt = f"""You are a code auditor AI for AIOS. Your job is to fix code issues.

STRICT RULES:
1. You can ONLY modify existing files (use modify_file tool)
2. You CANNOT create new files (use document_new_file_need to log the need)
3. Always verify syntax after modifications (use verify_syntax tool)
4. Make minimal changes - only fix the specific issue
5. Read the file first (use read_file tool)"""
        
        # Add context if available
        if context:
            base_prompt += f"""

RELEVANT GUIDELINES FROM MANUAL:
{context}

Follow these guidelines when fixing the issue."""
        
        base_prompt += f"""

CURRENT ISSUE:
- Core: {issue.get('core_name')}
- Type: {issue.get('issue_type')}
- File: {issue.get('file_path')}
- Details: {issue.get('details', 'No details')}

SANDBOX:
- Location: {sandbox_path}
- Files: {[f.name for f in sandbox_path.iterdir() if f.is_file()]}

YOUR TASK:
1. Read the problematic file
2. Identify the exact issue
3. Generate a minimal fix
4. Verify syntax
5. Explain what you fixed

Start by reading the file with read_file tool.
"""
        return base_prompt
    
    def _call_llm_with_tools(self, prompt: str) -> Dict:
        """
        Call LM Studio API with tool support.
        
        Args:
            prompt: System prompt for the LLM
        
        Returns:
            LLM response with tool calls
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a code auditor AI. You can only modify existing files, never create new ones. Use tools carefully."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "tools": self.tools,
                "temperature": 0.1,  # Low temperature for precise fixes
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data,
                    'tool_calls': data.get('choices', [{}])[0].get('message', {}).get('tool_calls', [])
                }
            else:
                logger.error(f"LLM API error: {response.status_code}")
                return {'success': False, 'error': f'API error: {response.status_code}'}
        
        except requests.exceptions.ConnectionError:
            logger.warning("LM Studio not running. Start LM Studio with qwen2.5-coder-3b model.")
            return {'success': False, 'error': 'LM Studio not available'}
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_tool_call(self, 
                         tool_name: str,
                         arguments: Dict,
                         sandbox_path: Path) -> Dict:
        """
        Execute a tool call from the LLM with full security validation.
        
        All operations are:
        - Path-validated (no escaping sandbox)
        - Security-scanned (no injections, eval, exec, subprocess)
        - Logged for audit trail
        - Executed via secure IDE
        """
        # Sanitize tool call
        sanitized_args = self.security.sanitize_tool_call(tool_name, arguments)
        if sanitized_args is None:
            logger.warning(f"SECURITY: Tool call rejected - {tool_name}")
            return {
                "success": False,
                "error": f"Tool call rejected by security policy: {tool_name}",
                "security_violation": True
            }
        
        # Log tool execution
        logger.info(f"Tool call: {tool_name} with args: {list(sanitized_args.keys())}")
        
        # Execute via secure IDE
        if tool_name == "read_file":
            return self.sandbox_ide.read_file(sanitized_args.get('file_path', ''))
        
        elif tool_name == "write_file":
            return self.sandbox_ide.write_file(
                sanitized_args.get('file_path', ''),
                sanitized_args.get('content', '')
            )
        
        elif tool_name == "modify_file":
            return self.sandbox_ide.modify_file(
                sanitized_args.get('file_path', ''),
                sanitized_args.get('search', ''),
                sanitized_args.get('replace', '')
            )
        
        elif tool_name == "list_files":
            return self.sandbox_ide.list_files()
        
        elif tool_name == "review_code":
            return self.sandbox_ide.review_code(sanitized_args.get('file_path', ''))
        
        elif tool_name == "generate_diff":
            return self.sandbox_ide.generate_diff(sanitized_args.get('file_path', ''))
        
        elif tool_name == "copy_from_aios":
            return self.sandbox_ide.copy_from_aios(
                sanitized_args.get('source_path', ''),
                sanitized_args.get('dest_name')
            )
        
        elif tool_name == "verify_syntax":
            return self.sandbox_ide.verify_syntax(sanitized_args.get('file_path', ''))
        
        elif tool_name == "document_new_file_need":
            return self._tool_document_new_file(sanitized_args, sandbox_path)
        
        else:
            logger.warning(f"Unknown tool requested: {tool_name}")
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
    
    def _tool_read_file(self, args: Dict, sandbox: Path) -> Dict:
        """Tool: Read file from sandbox."""
        file_path = sandbox / args['file_path']
        
        if not file_path.exists():
            return {'success': False, 'error': 'File not found in sandbox'}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            return {'success': True, 'content': content}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_modify_file(self, args: Dict, sandbox: Path) -> Dict:
        """Tool: Modify file (search and replace)."""
        file_path = sandbox / args['file_path']
        
        if not file_path.exists():
            return {'success': False, 'error': 'File not found. Cannot create new files.'}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Search and replace
            search = args['search']
            replace = args['replace']
            
            if search not in content:
                return {'success': False, 'error': 'Search text not found in file'}
            
            new_content = content.replace(search, replace, 1)  # Replace first occurrence
            
            # Write back to sandbox file
            file_path.write_text(new_content, encoding='utf-8')
            
            return {'success': True, 'message': f'Modified {file_path.name}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_document_new_file(self, args: Dict, sandbox: Path) -> Dict:
        """Tool: Document need for new file (doesn't create it)."""
        needs_file = sandbox / "new_files_needed.json"
        
        # Load existing needs
        if needs_file.exists():
            with open(needs_file) as f:
                needs = json.load(f)
        else:
            needs = {'new_files': []}
        
        # Add this need
        needs['new_files'].append({
            'file_path': args['file_path'],
            'reason': args['reason'],
            'suggested_content': args.get('suggested_content', ''),
            'documented_at': str(Path.cwd())
        })
        
        # Save
        with open(needs_file, 'w') as f:
            json.dump(needs, f, indent=2)
        
        return {'success': True, 'message': f'Documented need for {args["file_path"]}'}
    
    def _tool_verify_syntax(self, args: Dict, sandbox: Path) -> Dict:
        """Tool: Verify Python syntax."""
        file_path = sandbox / args['file_path']
        
        if not file_path.exists():
            return {'success': False, 'error': 'File not found'}
        
        try:
            import ast
            content = file_path.read_text(encoding='utf-8')
            ast.parse(content)
            return {'success': True, 'message': 'Syntax valid'}
        except SyntaxError as e:
            return {'success': False, 'error': f'Syntax error: {e}'}

