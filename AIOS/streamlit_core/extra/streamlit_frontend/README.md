# AIOS Streamlit Frontend
=========================

A comprehensive, Python-native frontend for the Advanced Intelligence Operating System (AIOS), built with Streamlit for rapid development and maximum integration with the AIOS backend.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AIOS backend running
- PowerShell (for backend integration)

### Installation
```bash
# Clone the repository
cd streamlit_frontend

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run pages/1_🏠_Dashboard.py
```

## 📋 Features

### 🏠 Dashboard
- Real-time system status overview
- Performance metrics visualization
- Quick access to all subsystems
- Administrative operations with WSR challenges

### 🧠 Luna Interface
- Interactive AI conversation interface
- Real-time chat with Luna core
- Conversation history and management
- Advanced prompt engineering tools

### 🔧 CARMA Console
- Node health monitoring
- Interactive network visualization
- Performance optimization tools
- Real-time system diagnostics

### 📊 Monitoring Dashboard
- Comprehensive system monitoring
- Performance trend analysis
- Alert management
- Historical data visualization

### 🏢 Enterprise Features
- User management and authentication
- Audit logging and compliance
- Role-based access control
- System administration tools

### ⚙️ Settings & Configuration
- System configuration management
- Theme and UI customization
- Security settings
- Integration configuration

## 🏗️ Architecture

### Component Structure
```
streamlit_frontend/
├── pages/                    # Streamlit page files
├── components/               # Custom UI components
│   └── aios_components/     # AIOS-specific components
├── utils/                   # Utility modules
├── config/                  # Configuration files
├── assets/                  # Static assets
└── tests/                   # Test files
```

### Key Components

#### NodeHealthDisplay
Advanced visualization for CARMA node health status with real-time updates and interactive controls.

#### BCMMonitor
Butterfly Cost Metric monitoring with efficiency tracking and overload detection.

#### WSRChallenge
Willing Submission Requirement component for secure administrative operations.

#### PerformanceMetrics
Real-time system performance monitoring with comprehensive metrics visualization.

#### CognitiveFlowMap
Interactive visualization of AI decision flows and cognitive processes.

## 🔧 Configuration

### Streamlit Configuration
The frontend uses a comprehensive configuration system:

```python
from config.streamlit_config import get_streamlit_config

config = get_streamlit_config()
app_title = config.get("app_title", "AIOS Control Center")
```

### UI Configuration
Customizable UI themes and layouts:

```python
from config.ui_config import get_ui_config, render_metric_card

ui_config = get_ui_config()
render_metric_card("CPU Usage", "45.2%")
```

### Security Configuration
Built-in authentication and authorization:

```python
from config.streamlit_config import get_auth_config

auth_config = get_auth_config()
is_authenticated = auth_config.verify_password(username, password)
```

## 🔗 Backend Integration

### AIOS Integration Module
The frontend communicates with the AIOS backend through a dedicated integration module:

```python
from utils.aios_integration import get_aios_connector

connector = get_aios_connector()
status = connector.get_backend_status()
```

### Supported Operations
- System status monitoring
- Performance metrics collection
- Administrative operations (with WSR)
- BCM monitoring
- User authentication
- Audit logging

## 🔒 Security Features

### Authentication
- Multi-user support with role-based permissions
- Session management with timeout
- Failed login attempt tracking
- Password security policies

### WSR (Willing Submission Requirement)
- Challenge-response authentication for admin operations
- Time-limited challenge windows
- Comprehensive audit logging
- Session-based validation

### Audit Logging
- All administrative operations logged
- User action tracking
- Security event monitoring
- Compliance reporting

## 📊 Performance Optimization

### Caching Strategy
```python
# Data caching for expensive operations
@st.cache_data(ttl=300)  # 5-minute cache
def get_system_metrics():
    return expensive_computation()

# Resource caching for objects
@st.cache_resource
def get_aios_connector():
    return AIOSBackendConnector()
```

### Session State Management
```python
# Efficient state management
if 'system_data' not in st.session_state:
    st.session_state.system_data = load_data()

# Component state isolation
component_state = st.session_state.get('component_state', {})
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_components.py

# Run with coverage
pytest --cov=components tests/
```

### Test Structure
- Unit tests for all components
- Integration tests for backend communication
- UI tests for user interactions
- Performance tests for optimization

## 📚 Development

### Code Standards
The project follows comprehensive AIOS file standards:

- **File Structure**: Standardized directory layout
- **Python Standards**: PEP 8 compliance with type hints
- **Component Standards**: Reusable, testable components
- **Documentation**: Comprehensive docstrings and comments
- **Security**: Authentication and authorization requirements

See `AIOS_STREAMLIT_STANDARDS.md` for complete details.

### Adding New Components
1. Create component file in `components/aios_components/`
2. Follow component structure template
3. Add comprehensive tests
4. Update documentation
5. Run standards checker

### Adding New Pages
1. Create page file in `pages/` directory
2. Follow naming convention: `{number}_{emoji}_{Name}.py`
3. Implement page structure template
4. Add navigation integration
5. Test functionality

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Configure environment variables
export AIOS_BACKEND_URL="https://your-backend.com"
export STREAMLIT_SERVER_PORT=8501

# Run with production settings
streamlit run pages/1_🏠_Dashboard.py --server.port 8501
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "pages/1_🏠_Dashboard.py", "--server.port", "8501"]
```

## 🔧 Troubleshooting

### Common Issues

#### Backend Connection Failed
```python
# Check backend status
from utils.aios_integration import get_aios_status
status = get_aios_status()
if not status.success:
    print(f"Backend error: {status.message}")
```

#### Authentication Issues
```python
# Verify authentication configuration
from config.streamlit_config import get_auth_config
auth_config = get_auth_config()
print("Users:", list(auth_config.users.keys()))
```

#### Performance Issues
```python
# Check caching configuration
from config.streamlit_config import get_streamlit_config
config = get_streamlit_config()
cache_ttl = config.get("cache_ttl_seconds", 300)
```

### Debug Mode
Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

### Documentation
- **Standards**: `AIOS_STREAMLIT_STANDARDS.md`
- **API Reference**: Inline code documentation
- **Examples**: Sample components and pages

### Getting Help
- **Issues**: Create GitHub issues for bugs
- **Features**: Submit pull requests for enhancements
- **Questions**: Check inline documentation first

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Follow AIOS file standards
4. Add comprehensive tests
5. Update documentation
6. Submit pull request

### Code Review Process
- Standards compliance check
- Test coverage verification
- Security review
- Performance assessment
- Documentation review

## 📄 License

This project is part of the AIOS ecosystem and follows the same licensing terms.

---

**Version**: 1.0.0  
**Last Updated**: 2025-09-28  
**Maintained by**: AIOS Development Team