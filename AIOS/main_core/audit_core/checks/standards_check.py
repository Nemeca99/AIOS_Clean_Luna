#!/usr/bin/env python3
"""
AIOS Architectural Standards Check
Enforces AIOS architectural standards across all cores.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from .base_check import BaseCheck, CheckResult


class StandardsCheck(BaseCheck):
    """
    Enforces AIOS architectural standards:
    1. *_core folder structure
    2. *_core.py main files with handle_command()
    3. File linking patterns
    4. JSON configuration standards
    5. Coding standards (imports, structure, etc.)
    """
    
    def __init__(self):
        super().__init__()
        self.name = "AIOS Standards Check"
        self.description = "Enforces architectural standards"
        self.repo_root = self._find_repo_root()
        self.standards_violations = []
        self.standards_checks = []
    
    def _find_repo_root(self) -> Path:
        """Find the AIOS_Clean repository root"""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "AIOS_MANUAL.md").exists() and (parent / "main.py").exists():
                return parent
        raise RuntimeError("Could not find AIOS_Clean repository root")
    
    def run(self, core_path: Path, core_name: str) -> CheckResult:
        """Run architectural standards check on a core"""
        violations = []
        checks = []
        
        # 1. Check folder structure
        folder_violations = self._check_folder_structure(core_path, core_name)
        violations.extend(folder_violations)
        
        # 2. Check main *_core.py file
        main_file_violations = self._check_main_core_file(core_path, core_name)
        violations.extend(main_file_violations)
        
        # 3. Check file linking patterns
        linking_violations = self._check_file_linking(core_path, core_name)
        violations.extend(linking_violations)
        
        # 4. Check JSON standards
        json_violations = self._check_json_standards(core_path, core_name)
        violations.extend(json_violations)
        
        # 5. Check coding standards
        coding_violations = self._check_coding_standards(core_path, core_name)
        violations.extend(coding_violations)
        
        # Calculate score
        critical_violations = len([v for v in violations if v.get('severity') == 'critical'])
        warning_violations = len([v for v in violations if v.get('severity') == 'warning'])
        
        # Score calculation (similar to other checks)
        score = 100
        score -= critical_violations * 25  # Critical violations are severe
        score -= warning_violations * 10   # Warnings are moderate
        score = max(0, score)
        
        # Determine severity
        if critical_violations > 0:
            severity = 'critical'
        elif warning_violations > 0:
            severity = 'safety'
        else:
            severity = 'performance'
        
        # Create issue messages
        issue_messages = []
        for violation in violations:
            issue_messages.append(f"[{violation.get('category', 'unknown')}] {violation['message']}")
        
        return CheckResult(
            check_name=self.name,
            severity=severity,
            passed=len(violations) == 0,
            issues=issue_messages,
            details={
                'core_name': core_name,
                'score': score,
                'total_violations': len(violations),
                'critical_violations': critical_violations,
                'warning_violations': warning_violations,
                'standards_compliance': {
                    'folder_structure': len([v for v in violations if 'folder' in v.get('category', '')]) == 0,
                    'main_file': len([v for v in violations if 'main_file' in v.get('category', '')]) == 0,
                    'file_linking': len([v for v in violations if 'linking' in v.get('category', '')]) == 0,
                    'json_standards': len([v for v in violations if 'json' in v.get('category', '')]) == 0,
                    'coding_standards': len([v for v in violations if 'coding' in v.get('category', '')]) == 0
                }
            }
        )
    
    def _check_folder_structure(self, core_path: Path, core_name: str) -> List[Dict[str, Any]]:
        """Check if core follows *_core folder structure standards"""
        violations = []
        
        # Check folder name pattern
        if not core_name.endswith('_core'):
            violations.append({
                'category': 'folder_structure',
                'severity': 'critical',
                'message': f"Folder name '{core_name}' does not follow *_core pattern",
                'file': str(core_path),
                'line': 0
            })
        
        # Check for required subdirectories
        required_dirs = ['config']
        optional_dirs = ['core', 'systems', 'utils', 'implementations', 'extra']
        
        for req_dir in required_dirs:
            dir_path = core_path / req_dir
            if not dir_path.exists():
                violations.append({
                    'category': 'folder_structure',
                    'severity': 'warning',
                    'message': f"Missing required directory: {req_dir}/",
                    'file': str(core_path),
                    'line': 0
                })
        
        # Check for unexpected directories (warn about non-standard ones)
        unexpected_dirs = []
        for item in core_path.iterdir():
            if item.is_dir() and item.name not in required_dirs + optional_dirs + ['__pycache__']:
                # Allow some common exceptions
                # - rust_* (Rust implementations)
                # - test_* (test directories)
                # - _* (internal/private directories)
                # - manual_oracle, *_documents, *_embeddings (data directories)
                exceptions = ['rust_', 'test_', '.', '__', '_', 'manual_oracle', 'documents', 'embeddings', 'cache', 'data']
                if not any(exc in item.name for exc in exceptions):
                    unexpected_dirs.append(item.name)
        
        if unexpected_dirs:
            violations.append({
                'category': 'folder_structure',
                'severity': 'warning',
                'message': f"Non-standard directories found: {', '.join(unexpected_dirs)}",
                'file': str(core_path),
                'line': 0
            })
        
        return violations
    
    def _check_main_core_file(self, core_path: Path, core_name: str) -> List[Dict[str, Any]]:
        """Check if main *_core.py file follows standards"""
        violations = []
        
        # Check for main *_core.py file
        main_file = core_path / f"{core_name}.py"
        if not main_file.exists():
            violations.append({
                'category': 'main_file',
                'severity': 'critical',
                'message': f"Missing main file: {core_name}.py",
                'file': str(core_path),
                'line': 0
            })
            return violations
        
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            violations.append({
                'category': 'main_file',
                'severity': 'critical',
                'message': f"Cannot read main file: {e}",
                'file': str(main_file),
                'line': 0
            })
            return violations
        
        # Check for required elements
        required_elements = [
            ('#!/usr/bin/env python3', 'shebang'),
            ('"""', 'docstring'),
            ('handle_command', 'handle_command_function'),
            ('import sys', 'sys_import'),
            ('from pathlib import Path', 'pathlib_import')
        ]
        
        for element, name in required_elements:
            if element not in content:
                violations.append({
                    'category': 'main_file',
                    'severity': 'critical' if name == 'handle_command_function' else 'warning',
                    'message': f"Missing {name}: {element}",
                    'file': str(main_file),
                    'line': 0
                })
        
        # Check for handle_command function signature
        handle_command_pattern = r'def handle_command\([^)]*\) -> (bool|None):'
        if not re.search(handle_command_pattern, content):
            violations.append({
                'category': 'main_file',
                'severity': 'critical',
                'message': "handle_command function missing or incorrect signature",
                'file': str(main_file),
                'line': 0
            })
        
        # Check for Unicode safety import
        if 'unicode_safe_output' not in content:
            violations.append({
                'category': 'main_file',
                'severity': 'warning',
                'message': "Missing unicode_safe_output import (recommended for Windows)",
                'file': str(main_file),
                'line': 0
            })
        
        return violations
    
    def _check_file_linking(self, core_path: Path, core_name: str) -> List[Dict[str, Any]]:
        """Check file linking patterns within the core"""
        violations = []
        
        # Check for __init__.py files
        init_file = core_path / "__init__.py"
        if not init_file.exists():
            violations.append({
                'category': 'file_linking',
                'severity': 'warning',
                'message': "Missing __init__.py file",
                'file': str(core_path),
                'line': 0
            })
        else:
            # Check __init__.py content
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    init_content = f.read()
                
                # Should expose handle_command
                if 'handle_command' not in init_content:
                    violations.append({
                        'category': 'file_linking',
                        'severity': 'warning',
                        'message': "__init__.py should expose handle_command",
                        'file': str(init_file),
                        'line': 0
                    })
            except Exception as e:
                violations.append({
                    'category': 'file_linking',
                    'severity': 'warning',
                    'message': f"Cannot read __init__.py: {e}",
                    'file': str(init_file),
                    'line': 0
                })
        
        # Check for circular imports (basic check)
        main_file = core_path / f"{core_name}.py"
        if main_file.exists():
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for imports from the same core
                self_imports = re.findall(rf'from {core_name}\.', content)
                if self_imports:
                    violations.append({
                        'category': 'file_linking',
                        'severity': 'warning',
                        'message': f"Potential circular import: {', '.join(self_imports)}",
                        'file': str(main_file),
                        'line': 0
                    })
            except Exception:
                pass  # Already handled in main file check
        
        return violations
    
    def _check_json_standards(self, core_path: Path, core_name: str) -> List[Dict[str, Any]]:
        """Check JSON configuration file standards"""
        violations = []
        
        config_dir = core_path / "config"
        if not config_dir.exists():
            return violations  # Already checked in folder structure
        
        # Check JSON files in config directory
        for json_file in config_dir.glob("*.json"):
            violations.extend(self._validate_json_file(json_file, core_name))
        
        return violations
    
    def _validate_json_file(self, json_file: Path, core_name: str) -> List[Dict[str, Any]]:
        """Validate a single JSON file"""
        violations = []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
        except json.JSONDecodeError as e:
            violations.append({
                'category': 'json_standards',
                'severity': 'critical',
                'message': f"Invalid JSON: {e}",
                'file': str(json_file),
                'line': 0
            })
            return violations
        except Exception as e:
            violations.append({
                'category': 'json_standards',
                'severity': 'critical',
                'message': f"Cannot read JSON file: {e}",
                'file': str(json_file),
                'line': 0
            })
            return violations
        
        # Check for standard JSON structure elements
        filename = json_file.name
        
        # Model config files should have specific structure
        if filename == "model_config.json":
            if 'model_config' not in data:
                violations.append({
                    'category': 'json_standards',
                    'severity': 'critical',
                    'message': "model_config.json missing 'model_config' root key",
                    'file': str(json_file),
                    'line': 0
                })
            else:
                model_config = data['model_config']
                required_keys = ['version', 'models']
                for key in required_keys:
                    if key not in model_config:
                        violations.append({
                            'category': 'json_standards',
                            'severity': 'warning',
                            'message': f"model_config.json missing '{key}' key",
                            'file': str(json_file),
                            'line': 0
                        })
        
        # AIOS config files should have specific structure
        elif filename == "aios_config.json":
            required_keys = ['AIOS_ROOT', 'PYTHON_ENV_PATH', 'MONITORING_ENABLED']
            for key in required_keys:
                if key not in data:
                    violations.append({
                        'category': 'json_standards',
                        'severity': 'warning',
                        'message': f"aios_config.json missing '{key}' key",
                        'file': str(json_file),
                        'line': 0
                    })
        
        # Check for version fields (recommended)
        if 'version' not in data and 'schema_version' not in data:
            violations.append({
                'category': 'json_standards',
                'severity': 'warning',
                'message': "JSON file missing version/schema_version field",
                'file': str(json_file),
                'line': 0
            })
        
        return violations
    
    def _check_coding_standards(self, core_path: Path, core_name: str) -> List[Dict[str, Any]]:
        """Check coding standards across Python files"""
        violations = []
        
        # Check all Python files in the core
        for py_file in core_path.rglob("*.py"):
            if py_file.name.startswith('test_') or py_file.name.endswith('_test.py'):
                continue  # Skip test files
            
            violations.extend(self._validate_python_file(py_file, core_name))
        
        return violations
    
    def _validate_python_file(self, py_file: Path, core_name: str) -> List[Dict[str, Any]]:
        """Validate a single Python file"""
        violations = []
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                content = ''.join(lines)
        except Exception as e:
            violations.append({
                'category': 'coding_standards',
                'severity': 'warning',
                'message': f"Cannot read Python file: {e}",
                'file': str(py_file),
                'line': 0
            })
            return violations
        
        # Check for shebang on main files
        if py_file.name.endswith(f"{core_name}.py") and not content.startswith('#!/usr/bin/env python3'):
            violations.append({
                'category': 'coding_standards',
                'severity': 'warning',
                'message': "Main core file should start with shebang",
                'file': str(py_file),
                'line': 1
            })
        
        # Check for docstring
        if not (content.startswith('"""') or content.startswith("'''")):
            violations.append({
                'category': 'coding_standards',
                'severity': 'warning',
                'message': "Python file should have module docstring",
                'file': str(py_file),
                'line': 1
            })
        
        # Check import organization
        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                import_lines.append((i, stripped))
            elif stripped and not stripped.startswith('#'):
                break  # End of imports
        
        # Check for standard library imports first
        stdlib_imports = []
        third_party_imports = []
        local_imports = []
        
        for line_num, import_line in import_lines:
            if import_line.startswith('from utils_core') or import_line.startswith('from support_core'):
                local_imports.append((line_num, import_line))
            elif any(module in import_line for module in ['sys', 'os', 'json', 'time', 'pathlib', 'typing']):
                stdlib_imports.append((line_num, import_line))
            else:
                third_party_imports.append((line_num, import_line))
        
        # Check import order
        if stdlib_imports and third_party_imports:
            last_stdlib = max(line_num for line_num, _ in stdlib_imports)
            first_third_party = min(line_num for line_num, _ in third_party_imports)
            if last_stdlib > first_third_party:
                violations.append({
                    'category': 'coding_standards',
                    'severity': 'warning',
                    'message': "Standard library imports should come before third-party imports",
                    'file': str(py_file),
                    'line': first_third_party
                })
        
        return violations
