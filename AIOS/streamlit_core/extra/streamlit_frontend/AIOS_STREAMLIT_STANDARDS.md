# AIOS Streamlit Frontend Standards
===================================

This document defines the comprehensive file standards and best practices for the AIOS Streamlit frontend, ensuring internal consistency, modularity, and adherence to AIOS Clean principles.

## 📋 Table of Contents

1. [File Structure Standards](#file-structure-standards)
2. [Python File Standards](#python-file-standards)
3. [Component Standards](#component-standards)
4. [Configuration Standards](#configuration-standards)
5. [Security Standards](#security-standards)
6. [Performance Standards](#performance-standards)
7. [Documentation Standards](#documentation-standards)
8. [Testing Standards](#testing-standards)
9. [Integration Standards](#integration-standards)

---

## 🏗️ File Structure Standards

### Required Directory Structure
```
streamlit_frontend/
├── pages/                          # Streamlit page files
│   ├── 1_🏠_Dashboard.py
│   ├── 2_🧠_Luna.py
│   ├── 3_🔧_CARMA.py
│   ├── 4_📊_Monitoring.py
│   ├── 5_🏢_Enterprise.py
│   └── 6_⚙️_Settings.py
├── components/                     # Custom UI components
│   ├── __init__.py
│   └── aios_components/
│       ├── __init__.py
│       ├── node_health_display.py
│       ├── cognitive_flow_map.py
│       ├── performance_metrics.py
│       ├── wsr_challenge.py
│       └── bcm_monitor.py
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── aios_integration.py
│   └── ui_components.py
├── config/                         # Configuration files
│   ├── __init__.py
│   ├── streamlit_config.py
│   └── ui_config.py
├── assets/                         # Static assets
│   ├── images/
│   ├── icons/
│   └── styles/
├── tests/                          # Test files
│   ├── __init__.py
│   ├── test_components.py
│   ├── test_integration.py
│   └── test_config.py
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── AIOS_STREAMLIT_STANDARDS.md     # This file
└── .streamlit/                     # Streamlit configuration
    └── config.toml
```

### Naming Conventions
- **Page files**: `{number}_{emoji}_{Name}.py` (e.g., `1_🏠_Dashboard.py`)
- **Component files**: `snake_case.py` (e.g., `node_health_display.py`)
- **Config files**: `{module}_config.py` (e.g., `streamlit_config.py`)
- **Test files**: `test_{module}.py` (e.g., `test_components.py`)

---

## 🐍 Python File Standards

### File Header Template
```python
"""
{Module Name} - {Brief Description}
==================================

{Detailed description of the module's purpose and functionality}

Key Features:
- Feature 1
- Feature 2
- Feature 3

Author: AIOS Development Team
Version: 1.0.0
Last Updated: {Date}
"""

# Standard library imports
import os
import sys
from typing import Dict, List, Any, Optional

# Third-party imports
import streamlit as st
import pandas as pd

# Local imports
from utils.aios_integration import get_aios_connector
from config.ui_config import get_ui_config
```

### Import Standards
1. **Standard library imports** (alphabetical)
2. **Third-party imports** (alphabetical)
3. **Local imports** (alphabetical)
4. **One import per line**
5. **Use `from` imports for specific functions when appropriate**

### Function Standards
```python
def function_name(param1: str, param2: int = 10) -> bool:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
        ConnectionError: When unable to connect to backend
    
    Example:
        >>> result = function_name("test", 20)
        >>> print(result)
        True
    """
    # Implementation here
    return True
```

### Class Standards
```python
class ComponentName:
    """
    Brief description of the class.
    
    This class provides [functionality description] for the AIOS frontend.
    
    Attributes:
        attribute1: Description of attribute1
        attribute2: Description of attribute2
    
    Example:
        >>> component = ComponentName()
        >>> component.render()
    """
    
    def __init__(self, param1: str = "default"):
        """Initialize the component."""
        self.param1 = param1
        self._private_attribute = None
    
    def public_method(self) -> None:
        """Public method description."""
        pass
    
    def _private_method(self) -> None:
        """Private method description."""
        pass
```

---

## 🧩 Component Standards

### Component Structure
Every custom component must follow this structure:

```python
class ComponentName:
    """Component description."""
    
    def __init__(self, title: str = "Default Title"):
        """Initialize component with required parameters."""
        self.title = title
        self.data = {}
        self._initialize_component()
    
    def _initialize_component(self):
        """Initialize component-specific data structures."""
        pass
    
    def add_data(self, data: Dict[str, Any]):
        """Add data to the component."""
        pass
    
    def render(self):
        """Render the component in Streamlit."""
        pass
    
    def _render_header(self):
        """Render component header."""
        pass
    
    def _render_content(self):
        """Render component content."""
        pass
    
    def _render_footer(self):
        """Render component footer."""
        pass
```

### Component Requirements
1. **Single Responsibility**: Each component should have one clear purpose
2. **Configurable**: Components should accept configuration parameters
3. **Reusable**: Components should be usable across different pages
4. **Testable**: Components should be easily testable
5. **Documented**: All public methods must have docstrings

### Streamlit Integration
```python
# Use @st.cache_data for expensive computations
@st.cache_data(ttl=300)  # Cache for 5 minutes
def expensive_computation(data):
    return processed_data

# Use @st.cache_resource for objects that should be cached
@st.cache_resource
def get_expensive_object():
    return ExpensiveObject()

# Use st.session_state for component state
def render_component():
    if 'component_state' not in st.session_state:
        st.session_state.component_state = {}
```

---

## ⚙️ Configuration Standards

### Configuration File Structure
```python
"""
Configuration Module - {Purpose}
===============================

{Description of configuration purpose}
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Configuration enums
class ConfigEnum(Enum):
    VALUE1 = "value1"
    VALUE2 = "value2"

# Configuration data classes
@dataclass
class ConfigClass:
    attribute1: str = "default"
    attribute2: int = 10

# Main configuration class
class MainConfig:
    def __init__(self):
        self.config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "setting1": "value1",
            "setting2": 10
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
```

### Configuration Requirements
1. **Type Hints**: All configuration values must have type hints
2. **Default Values**: All settings must have sensible defaults
3. **Validation**: Configuration values must be validated
4. **Documentation**: Each configuration option must be documented
5. **Environment Support**: Support for environment variable overrides

---

## 🔒 Security Standards

### Authentication Requirements
```python
# All admin operations must check authentication
def admin_operation():
    if not check_authentication():
        st.error("Authentication required")
        return
    
    if not check_permissions("admin"):
        st.error("Admin permissions required")
        return
    
    # Proceed with admin operation
    pass

# WSR challenges for sensitive operations
def sensitive_operation():
    if not validate_wsr_challenge():
        st.error("WSR challenge required")
        return
    
    # Proceed with sensitive operation
    pass
```

### Security Best Practices
1. **Input Validation**: All user inputs must be validated
2. **Output Sanitization**: All outputs must be sanitized
3. **Session Management**: Proper session timeout and cleanup
4. **Audit Logging**: All security events must be logged
5. **Error Handling**: No sensitive information in error messages

---

## ⚡ Performance Standards

### Caching Strategy
```python
# Use appropriate caching decorators
@st.cache_data(ttl=300)  # For data that changes infrequently
def get_static_data():
    return data

@st.cache_resource  # For objects that are expensive to create
def get_expensive_object():
    return ExpensiveObject()

# Use session state for component state
def render_component():
    if 'component_data' not in st.session_state:
        st.session_state.component_data = load_data()
```

### Performance Requirements
1. **Response Time**: Page loads must complete within 3 seconds
2. **Memory Usage**: Components must not exceed 100MB memory
3. **Caching**: Appropriate use of Streamlit caching
4. **Lazy Loading**: Load data only when needed
5. **Error Handling**: Graceful degradation on errors

---

## 📚 Documentation Standards

### README Requirements
Every module must have a comprehensive README.md with:
1. **Purpose**: What the module does
2. **Installation**: How to install dependencies
3. **Usage**: How to use the module
4. **Configuration**: Available configuration options
5. **Examples**: Code examples
6. **API Reference**: Function and class documentation

### Code Documentation
1. **Module Docstrings**: Every module must have a docstring
2. **Class Docstrings**: Every class must have a docstring
3. **Function Docstrings**: Every public function must have a docstring
4. **Inline Comments**: Complex logic must be commented
5. **Type Hints**: All function parameters and returns must be typed

---

## 🧪 Testing Standards

### Test File Structure
```python
"""
Test Module - {Component Name}
=============================

Tests for {component description}
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch

from components.aios_components.component_name import ComponentName

class TestComponentName:
    """Test cases for ComponentName."""
    
    def test_initialization(self):
        """Test component initialization."""
        component = ComponentName("Test Title")
        assert component.title == "Test Title"
    
    def test_add_data(self):
        """Test adding data to component."""
        component = ComponentName()
        test_data = {"key": "value"}
        component.add_data(test_data)
        assert component.data == test_data
    
    @patch('streamlit.markdown')
    def test_render(self, mock_markdown):
        """Test component rendering."""
        component = ComponentName()
        component.render()
        mock_markdown.assert_called()
```

### Testing Requirements
1. **Unit Tests**: Every function must have unit tests
2. **Integration Tests**: Components must have integration tests
3. **Coverage**: Minimum 80% code coverage
4. **Mocking**: External dependencies must be mocked
5. **CI/CD**: Tests must run in CI/CD pipeline

---

## 🔗 Integration Standards

### Backend Integration
```python
# Use the AIOS integration module for all backend communication
from utils.aios_integration import get_aios_connector

def get_backend_data():
    connector = get_aios_connector()
    response = connector.get_system_status()
    
    if response.success:
        return response.data
    else:
        st.error(f"Backend error: {response.message}")
        return None
```

### Integration Requirements
1. **Error Handling**: All backend calls must handle errors gracefully
2. **Timeout Handling**: All calls must have appropriate timeouts
3. **Retry Logic**: Failed calls should be retried with exponential backoff
4. **Logging**: All integration calls must be logged
5. **Validation**: All data from backend must be validated

---

## ✅ Compliance Checklist

### File Standards Compliance
- [ ] File header follows template
- [ ] Imports are properly organized
- [ ] Functions have proper docstrings
- [ ] Classes have proper docstrings
- [ ] Type hints are used throughout
- [ ] Code follows PEP 8 style guide

### Component Standards Compliance
- [ ] Component follows structure template
- [ ] Component is configurable
- [ ] Component is reusable
- [ ] Component is testable
- [ ] Component is documented
- [ ] Component uses appropriate caching

### Security Standards Compliance
- [ ] Authentication checks in place
- [ ] Permission checks in place
- [ ] WSR challenges for sensitive operations
- [ ] Input validation implemented
- [ ] Output sanitization implemented
- [ ] Audit logging implemented

### Performance Standards Compliance
- [ ] Appropriate caching used
- [ ] Response time under 3 seconds
- [ ] Memory usage under 100MB
- [ ] Lazy loading implemented
- [ ] Error handling graceful

### Documentation Standards Compliance
- [ ] README.md is comprehensive
- [ ] Module docstring present
- [ ] Class docstrings present
- [ ] Function docstrings present
- [ ] Inline comments for complex logic
- [ ] Type hints throughout

### Testing Standards Compliance
- [ ] Unit tests for all functions
- [ ] Integration tests for components
- [ ] 80% code coverage achieved
- [ ] External dependencies mocked
- [ ] Tests run in CI/CD

---

## 📝 Auto-Checking Implementation

### Standards Checker
A Python script `check_streamlit_standards.py` should be created to automatically verify compliance:

```python
#!/usr/bin/env python3
"""
AIOS Streamlit Standards Checker
===============================

Automatically checks Streamlit frontend files for compliance with AIOS standards.
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

def check_file_standards(file_path: Path) -> Dict[str, Any]:
    """Check a single file for standards compliance."""
    results = {
        "file": str(file_path),
        "compliant": True,
        "issues": []
    }
    
    # Check file header
    # Check imports organization
    # Check function docstrings
    # Check class docstrings
    # Check type hints
    # Check naming conventions
    
    return results

def main():
    """Main checker function."""
    streamlit_dir = Path("streamlit_frontend")
    results = []
    
    for py_file in streamlit_dir.rglob("*.py"):
        if py_file.name != "__init__.py":
            results.append(check_file_standards(py_file))
    
    # Report results
    pass

if __name__ == "__main__":
    main()
```

---

## 🚀 Getting Started

### Quick Setup
1. **Install Dependencies**:
   ```bash
   cd streamlit_frontend
   pip install -r requirements.txt
   ```

2. **Run Standards Check**:
   ```bash
   python check_streamlit_standards.py
   ```

3. **Start Development**:
   ```bash
   streamlit run pages/1_🏠_Dashboard.py
   ```

### Development Workflow
1. **Create/Edit Files** following standards
2. **Run Standards Check** before committing
3. **Run Tests** to ensure functionality
4. **Update Documentation** as needed
5. **Submit for Review**

---

## 📞 Support

For questions about these standards or to request changes:
- **Documentation**: See inline code comments
- **Issues**: Create GitHub issues for problems
- **Suggestions**: Submit pull requests for improvements

---

**Last Updated**: 2025-09-28  
**Version**: 1.0.0  
**Maintained by**: AIOS Development Team
