#!/usr/bin/env python3
"""
Auto-Fixer - Generate fixes for common audit issues.
Works with SandboxManager to prepare fixes for dream_core.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class AutoFixer:
    """
    Generate fixes for common audit issues.
    
    Supported fixes:
    - Bare except → except Exception
    - Missing imports
    - Print → logger
    - Missing timeouts
    - Missing context managers
    """
    
    def __init__(self):
        self.fix_count = 0
    
    def can_auto_fix(self, issue_type: str) -> bool:
        """Check if issue type can be auto-fixed."""
        fixable = {
            'bare-except',
            'print-instead-of-log',
            'missing-import',
            'requests-no-timeout',
            'missing-context-manager'
        }
        
        return issue_type in fixable
    
    def generate_fix(self, 
                    issue_type: str,
                    file_content: str,
                    issue_details: Dict) -> Optional[Tuple[str, str]]:
        """
        Generate fix for an issue.
        
        Args:
            issue_type: Type of issue
            file_content: Current file content
            issue_details: Details about the issue
        
        Returns:
            (fixed_content, fix_description) or None if can't fix
        """
        if issue_type == 'bare-except':
            return self._fix_bare_except(file_content, issue_details)
        
        elif issue_type == 'print-instead-of-log':
            return self._fix_print_to_logger(file_content, issue_details)
        
        elif issue_type == 'missing-import':
            return self._fix_missing_import(file_content, issue_details)
        
        elif issue_type == 'requests-no-timeout':
            return self._fix_requests_timeout(file_content, issue_details)
        
        else:
            logger.debug(f"No auto-fix available for {issue_type}")
            return None
    
    def _fix_bare_except(self, content: str, details: Dict) -> Tuple[str, str]:
        """Fix bare except clauses."""
        # Replace 'except:' with 'except Exception as e:'
        fixed = re.sub(
            r'\bexcept\s*:',
            'except Exception as e:',
            content
        )
        
        description = "Replaced bare 'except:' with 'except Exception as e:'"
        return fixed, description
    
    def _fix_print_to_logger(self, content: str, details: Dict) -> Tuple[str, str]:
        """Fix print statements to use logger."""
        lines = content.split('\n')
        fixed_lines = []
        added_import = False
        
        for line in lines:
            # Check if line has print()
            if 'print(' in line and not line.strip().startswith('#'):
                # Convert print to logger.info
                # Simple conversion: print("text") → logger.info("text")
                fixed_line = line.replace('print(', 'logger.info(')
                fixed_lines.append(fixed_line)
                
                # Add logger import at top if not present
                if not added_import and 'import logging' not in content:
                    # We'll add it later
                    pass
            else:
                fixed_lines.append(line)
        
        # Add logging import if needed
        if 'import logging' not in content:
            # Find first import or add at top
            for i, line in enumerate(fixed_lines):
                if line.startswith('import ') or line.startswith('from '):
                    fixed_lines.insert(i, 'import logging')
                    fixed_lines.insert(i+1, 'logger = logging.getLogger(__name__)')
                    fixed_lines.insert(i+2, '')
                    break
        
        fixed = '\n'.join(fixed_lines)
        description = "Replaced print() with logger.info()"
        return fixed, description
    
    def _fix_missing_import(self, content: str, details: Dict) -> Tuple[str, str]:
        """Add missing import."""
        missing_module = details.get('module', '')
        
        if not missing_module:
            return None
        
        # Add import at top
        lines = content.split('\n')
        
        # Find first import line
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                lines.insert(i, f'import {missing_module}')
                break
        else:
            # No imports found, add at top (after docstring)
            insert_pos = 0
            if lines[0].strip().startswith('"""') or lines[0].strip().startswith("'''"):
                # Skip docstring
                for i in range(1, len(lines)):
                    if '"""' in lines[i] or "'''" in lines[i]:
                        insert_pos = i + 1
                        break
            
            lines.insert(insert_pos, f'import {missing_module}')
        
        fixed = '\n'.join(lines)
        description = f"Added missing import: {missing_module}"
        return fixed, description
    
    def _fix_requests_timeout(self, content: str, details: Dict) -> Tuple[str, str]:
        """Add timeout to requests calls."""
        # Find requests.get/post/etc without timeout
        pattern = r'(requests\.(get|post|put|delete|patch)\([^)]*)\)'
        
        def add_timeout(match):
            call = match.group(1)
            # Check if timeout already present
            if 'timeout=' in call:
                return match.group(0)
            
            # Add timeout
            return f"{call}, timeout=30)"
        
        fixed = re.sub(pattern, add_timeout, content)
        description = "Added timeout=30 to requests calls"
        return fixed, description

