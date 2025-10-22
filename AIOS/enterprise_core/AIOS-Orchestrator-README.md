# AIOS-Orchestrator v2.0.0 - Enterprise Edition

## 🚀 Overview

AIOS-Orchestrator is an enterprise-grade PowerShell module designed to provide comprehensive orchestration, monitoring, security, and administration capabilities for AIOS (Artificial Intelligence Operating System) environments. Built with production-grade reliability, it offers advanced health checks, self-healing capabilities, security isolation, and performance monitoring.

## ✨ Key Features

### 🏥 Health & Monitoring
- **Tiered Health Checks**: Liveness and readiness endpoints with REST API integration
- **Performance Monitoring**: Windows Performance Counters with real-time alerts
- **System Resource Tracking**: CPU, memory, disk, and network monitoring
- **Process Management**: Detailed AIOS process tracking and control

### 🛡️ Security & Isolation
- **Principle of Least Privilege**: Dedicated service account management
- **Network Isolation**: Dynamic firewall rule configuration
- **Configuration Integrity**: SHA256 hash verification for critical files
- **WSR Enforcement**: Willing Submission Requirement for administrative actions
- **Audit Logging**: Windows Event Log integration for enterprise monitoring

### 🔧 Self-Healing & Reliability
- **BCM Auto-Remediation**: Butterfly Cost Metric monitoring with adaptive control
- **Intelligent Restart Logic**: Back-off protection to prevent crash loops
- **Dependency Management**: Automated pip check and conflict resolution
- **Graceful Shutdown**: REST API-based shutdown with fallback mechanisms

### 📊 Operational Excellence
- **Configuration Management**: External JSON configuration with hot-reloading
- **Log Management**: Rotation, compression, and retention policies
- **Standards Compliance**: Automated code and configuration standards checking
- **Backup & Recovery**: Data backup and restore capabilities

## 🚀 Quick Start

### Installation

```powershell
# Import the module
Import-Module .\AIOS-Orchestrator.psm1

# Or install from PowerShell Gallery (when published)
Install-Module AIOS-Orchestrator -Scope CurrentUser
```

### Basic Usage

```powershell
# Start AIOS with monitoring
Start-AIOS -Mode "luna" -Questions 5 -EnableMonitoring

# Check system health
Test-AIOSHealth -CheckType FULL

# View real-time performance
Get-AIOSPerformanceCounters

# Monitor BCM (Butterfly Cost Metric)
Start-AIOSBCMMonitoring
```

## 📚 Core Functions

### Health & Monitoring

| Function | Description |
|----------|-------------|
| `Test-AIOSHealth` | Comprehensive health check with recommendations |
| `Test-AIOSLiveness` | Basic liveness check (is AIOS running?) |
| `Test-AIOSReadiness` | Readiness check (is AIOS ready for requests?) |
| `Get-AIOSPerformanceCounters` | Detailed performance metrics collection |
| `Start-AIOSPerformanceMonitoring` | Continuous performance monitoring |

### Process Management

| Function | Description |
|----------|-------------|
| `Start-AIOS` | Start AIOS with various modes and options |
| `Stop-AIOS` | Stop AIOS with graceful shutdown support |
| `Restart-AIOS` | Intelligent restart with back-off protection |
| `Get-AIOSProcessDetail` | Detailed process information and metrics |

### Configuration & Dependencies

| Function | Description |
|----------|-------------|
| `Load-AIOSConfiguration` | Load configuration from external JSON |
| `Set-AIOSLogLevel` | Dynamically change logging level |
| `Test-AIOSDependency` | Check Python package integrity |
| `Invoke-AIOSDependencyFix` | Automatically resolve dependency conflicts |

### Security & Isolation

| Function | Description |
|----------|-------------|
| `Initialize-AIOSSecurity` | Set up security features (firewall, service account) |
| `Test-WillingSubmissionRequirement` | Enforce WSR for administrative actions |
| `Test-AIOSConfigurationIntegrity` | Verify file integrity with cryptographic hashes |
| `New-AIOSServiceAccount` | Create dedicated service account |

### BCM & Performance

| Function | Description |
|----------|-------------|
| `Get-ButterflyCostMetric` | Calculate current BCM value |
| `Start-AIOSBCMMonitoring` | Monitor BCM with auto-remediation |
| `Invoke-BCMRemediation` | Apply BCM-based performance fixes |
| `Get-SystemResourceSnapshot` | Capture current system state |

### Logging & Debugging

| Function | Description |
|----------|-------------|
| `Write-AIOSMessage` | Structured logging with levels |
| `Write-DebugInfo` | Enhanced debugging with context |
| `Invoke-LogRotation` | Manage log files with retention policies |
| `Write-AIOSEventLog` | Enterprise logging to Windows Event Log |

## ⚙️ Configuration

### External Configuration File

The module uses `config/aios_config.json` for centralized configuration:

```json
{
  "AIOS_ROOT": "F:\\AIOS_Clean",
  "PYTHON_ENV_PATH": "F:\\AIOS_Clean\\venv",
  "LOG_DIR": "F:\\AIOS_Clean\\log\\monitoring",
  "DEBUG_DIR": "F:\\AIOS_Clean\\temp\\debug",
  "MONITORING_ENABLED": false,
  "ADMIN_MODE": false,
  "LOG_LEVEL": "INFO",
  "MONITORING_CONFIG": {
    "BCM_OVERLOAD_THRESHOLD": 85.0,
    "BCM_AUTO_REMEDIATION": true,
    "LogRetention": 30,
    "MaxLogSize": 104857600
  },
  "SECURITY_CONFIG": {
    "WSR_CHALLENGE_DURATION_MINUTES": 5,
    "AUDIT_LOG_TO_EVENT_LOG": true
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `$AIOS_ROOT` | Root directory of AIOS installation | `F:\AIOS_Clean` |
| `$PYTHON_ENV_PATH` | Python virtual environment path | `$AIOS_ROOT\venv` |
| `$LOG_DIR` | Log directory | `$AIOS_ROOT\log\monitoring` |
| `$DEBUG_DIR` | Debug output directory | `$AIOS_ROOT\temp\debug` |

## 🔒 Security Features

### Willing Submission Requirement (WSR)

WSR ensures administrative actions require explicit user confirmation:

```powershell
# This will prompt for WSR confirmation
Test-WillingSubmissionRequirement -Operation "AIOS Service Restart" -RiskLevel "HIGH"
```

### Service Account Management

Create a dedicated service account with minimal privileges:

```powershell
Initialize-AIOSSecurity -CreateServiceAccount -ConfigureFirewall -VerifyIntegrity
```

### Configuration Integrity

Verify critical files haven't been tampered with:

```powershell
Test-AIOSConfigurationIntegrity
```

## 📊 BCM (Butterfly Cost Metric)

BCM monitors AI efficiency and triggers auto-remediation:

```powershell
# Monitor BCM in real-time
Start-AIOSBCMMonitoring

# Check current BCM value
Get-ButterflyCostMetric

# Manual remediation if needed
Invoke-BCMRemediation -RemediationLevel "MEDIUM"
```

## 🏥 Health Checks

### Tiered Health System

1. **Liveness Check**: Is AIOS process running?
2. **Readiness Check**: Is AIOS ready to handle requests?
3. **Full Health Check**: Comprehensive system validation

```powershell
# Quick liveness check
Test-AIOSLiveness

# Comprehensive health assessment
$health = Test-AIOSHealth -CheckType FULL
Write-Host "Overall Status: $($health.OverallStatus)"
```

## 📈 Performance Monitoring

### Real-time Metrics

```powershell
# Start continuous monitoring
Start-AIOSPerformanceMonitoring -IntervalSeconds 30

# Get current performance snapshot
$perf = Get-AIOSPerformanceCounters
Write-Host "CPU: $($perf.SystemCounters.CPUUsage)%"
Write-Host "Memory: $($perf.SystemCounters.AvailableMemory) MB"
```

### Process-specific Monitoring

```powershell
# Detailed process information
$processes = Get-AIOSProcessDetail
foreach ($proc in $processes) {
    Write-Host "PID $($proc.Id): CPU=$($proc.CPU), Memory=$($proc.WorkingSet)MB"
}
```

## 🔄 Self-Healing Features

### Intelligent Restart Logic

The module includes back-off protection to prevent crash loops:

```powershell
# Restart with back-off protection
Restart-AIOS -Mode "luna" -Questions 5

# Check back-off status
$backoff = Test-AIOSRestartBackoff
if ($backoff.InBackoffState) {
    Write-Host "System in back-off until: $($backoff.BackoffUntil)"
}
```

### Dependency Management

```powershell
# Check for dependency conflicts
$depCheck = Test-AIOSDependency -Detailed

# Auto-fix if possible
if (-not $depCheck.Success) {
    Invoke-AIOSDependencyFix
}
```

## 📝 Logging & Debugging

### Structured Logging

```powershell
# Write structured log messages
Write-AIOSMessage -Message "AIOS started successfully" -Level SUCCESS

# Enhanced debugging with context
Write-DebugInfo -Message "Process initialization" -FilePath "main.py" -LineNumber 42
```

### Log Management

```powershell
# Rotate logs with compression
Invoke-LogRotation -LogRetentionDays 30 -CompressOldLogs

# Clear old logs
Clear-AIOSLogs -DaysToKeep 7
```

## 🚨 Enterprise Integration

### Windows Event Log

```powershell
# Initialize Event Log integration
Initialize-AIOSEventLog

# Write to Event Log
Write-AIOSEventLog -Message "AIOS system started" -EntryType Information
```

### High-Priority Alerts

```powershell
# Send high-priority alert
Send-AIOSHighPriorityAlert -Message "Critical system failure detected" -Severity "CRITICAL"
```

## 🛠️ Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure running as Administrator for security features
2. **Python Environment**: Verify Python virtual environment is properly configured
3. **Configuration**: Check `config/aios_config.json` for correct paths
4. **Dependencies**: Run `Test-AIOSDependency` to check for conflicts

### Debug Mode

```powershell
# Enable debug logging
Set-AIOSLogLevel -LogLevel DEBUG

# Get detailed system information
Invoke-AIOSSystemDiagnostics
```

## 📋 Aliases

The module provides convenient aliases for common operations:

| Alias | Function |
|-------|----------|
| `aios` | `Start-AIOS` |
| `status` | `Get-AIOSStatus` |
| `health` | `Test-AIOSHealth` |
| `monitor` | `Start-AIOSMonitoring` |
| `bcm` | `Get-ButterflyCostMetric` |
| `wsr` | `Test-WillingSubmissionRequirement` |
| `help-aios` | `Show-AIOSHelp` |

## 🔧 Advanced Usage

### Custom Monitoring

```powershell
# Start custom monitoring job
$monitorJob = Start-Job -ScriptBlock {
    Import-Module AIOS-Orchestrator
    Start-AIOSPerformanceMonitoring -IntervalSeconds 10
}

# Stop monitoring
Stop-Job $monitorJob
```

### Configuration Management

```powershell
# Load configuration
$config = Load-AIOSConfiguration

# Modify settings
$config.MONITORING_CONFIG.BCM_OVERLOAD_THRESHOLD = 90.0

# Save changes
Save-AIOSConfiguration -Config $config
```

## 📊 Performance Considerations

- **Memory Usage**: ~50MB base overhead for monitoring
- **CPU Impact**: <1% during normal operation, <5% during intensive monitoring
- **Disk I/O**: Minimal, primarily for log rotation and configuration
- **Network**: Only for REST API health checks and external monitoring

## 🚀 Future Roadmap

- **v2.1**: GraphQL API integration
- **v2.2**: Kubernetes orchestration support
- **v2.3**: Machine learning-based anomaly detection
- **v3.0**: Multi-node cluster management

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/aios-systems/aios-orchestrator/wiki)
- **Issues**: [GitHub Issues](https://github.com/aios-systems/aios-orchestrator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aios-systems/aios-orchestrator/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**AIOS-Orchestrator v2.0.0** - Enterprise-grade orchestration for AI systems 🚀
