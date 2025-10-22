# AIOS FILE STANDARDS DOCUMENTATION

## 🎯 Core Principle
**All AIOS files must follow strict internal standards for consistency, modularity, and maintainability.**

## 📋 File Type Standards

### Python Files (.py)
- **Header**: Must start with `#!/usr/bin/env python3`
- **Unicode Safety**: Must import and setup Unicode safety layer
- **Line Length**: Maximum 88 characters (Black standard)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: No wildcard imports (`import *`)
- **Error Handling**: Must handle exceptions properly
- **Logging**: Use logging instead of print statements
- **Type Hints**: Required for all functions and methods
- **Docstrings**: Required for all classes and functions

**Required Import Pattern:**
```python
#!/usr/bin/env python3
"""
Module Name
Description
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

# Other imports...
```

### JSON Files (.json)
- **Format**: Must use JSON array format `[{}, {}, {}]`
- **Required Fields**: All objects must have `id` and `timestamp`
- **Encoding**: UTF-8
- **Indentation**: 2 spaces
- **Validation**: Must pass AIOS JSON standards validation

**Required Structure:**
```json
[
  {
    "id": "uuid-string",
    "timestamp": "2025-01-01T00:00:00.000Z",
    "data": "value"
  }
]
```

### PowerShell Files (.ps1, .psm1)
- **Header**: Must start with `# AIOS PowerShell`
- **Logging**: Must use `Write-AIOSMessage` instead of `Write-Host`
- **Parameters**: Must have parameter block
- **Functions**: Must be properly defined with braces
- **Encoding**: UTF-8 with BOM
- **Line Endings**: CRLF

**Required Header:**
```powershell
# AIOS PowerShell Backend Monitor
# Description
# Generated: 2025-01-01
# Author: AIOS System

param(
    [Parameter(Mandatory=$false)]
    [string]$Parameter1
)
```

### Markdown Files (.md)
- **Headers**: Must have main header and subsections
- **Structure**: Must follow AIOS documentation format
- **Security**: No JavaScript or external scripts
- **Line Length**: Maximum 100 characters

### Configuration Files (.cfg, .conf, .ini)
- **Security**: No plaintext passwords or secrets
- **Versioning**: Must include version and timestamp
- **Format**: Follow standard format conventions

## 🔧 Validation Rules

### Critical Issues (Must Fix)
- Missing Unicode safety imports (Python)
- Invalid JSON syntax
- Security risks (plaintext secrets)
- Syntax errors

### High Priority Issues
- Missing required headers
- Non-array JSON format
- Missing required fields
- Bare except clauses

### Medium Priority Issues
- Line length violations
- Forbidden patterns
- Missing docstrings
- Wildcard imports

### Low Priority Issues
- Style violations
- Minor formatting issues
- Optional pattern violations

## 🚀 Auto-Fix Capabilities

The system can automatically fix:
- Add missing Python shebang
- Add Unicode safety imports
- Fix file encoding to UTF-8
- Add missing JSON IDs
- Fix basic formatting issues

## 📊 Compliance Scoring

Files are scored on:
- **Critical Issues**: 0 points (must fix)
- **High Issues**: -20 points each
- **Medium Issues**: -10 points each
- **Low Issues**: -5 points each
- **Perfect Compliance**: 100 points

## 🛠️ Usage

### Command Line
```bash
# Validate single file
python utils/aios_file_standards.py validate file.py

# Validate entire project
python utils/aios_file_standards.py validate-project

# Auto-fix issues
python utils/aios_file_standards.py auto-fix file.py
```

### Python API
```python
from utils.aios_file_standards import AIOSFileValidator

validator = AIOSFileValidator()
result = validator.validate_file("file.py")
print(f"Compliance: {result.standards_compliance}%")

# Auto-fix issues
fixes = validator.auto_fix_file("file.py")
print(f"Applied fixes: {fixes}")
```

## 📈 Integration with CI/CD

The standards system integrates with:
- **Pre-commit hooks**: Automatic validation before commits
- **GitHub Actions**: Automated validation in CI pipeline
- **IDE plugins**: Real-time validation in development
- **Build system**: Validation as part of build process

## 🎯 Benefits

1. **Consistency**: All files follow the same standards
2. **Maintainability**: Easy to read and modify
3. **Security**: Prevents common security issues
4. **Quality**: Catches issues early
5. **Automation**: Reduces manual review time
6. **Modularity**: Ensures proper module structure

---
**This standard ensures all AIOS components maintain internal consistency and quality!** 🚀
