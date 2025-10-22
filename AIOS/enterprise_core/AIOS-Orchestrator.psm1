# AIOS-Orchestrator PowerShell Module
# Enterprise-grade orchestration and monitoring utility for AIOS systems
# Version: 2.0.0
# Author: AIOS Development Team

# Module metadata
$ModuleVersion = "2.0.0"
$ModuleGuid = "12345678-1234-1234-1234-123456789012"

# Export all public functions
Export-ModuleMember -Function @(
    # Core AIOS Functions
    'Start-AIOS',
    'Stop-AIOS',
    'Start-AIOSProcess',
    'Restart-AIOS',
    'Get-AIOSStatus',
    'Invoke-AIOSHealthCheck',
    'Start-AIOSMonitoring',
    
    # Health & Monitoring
    'Test-AIOSHealth',
    'Test-AIOSLiveness',
    'Test-AIOSReadiness',
    'Get-AIOSPerformanceCounters',
    'Start-AIOSPerformanceMonitoring',
    
    # Process Management
    'Get-AIOSProcessDetail',
    'Get-AIOSLogs',
    'Clear-AIOSLogs',
    
    # Configuration Management
    'Load-AIOSConfiguration',
    'Save-AIOSConfiguration',
    'Get-AIOSConfiguration',
    'Set-AIOSConfiguration',
    'Set-AIOSLogLevel',
    
    # Dependency Management
    'Test-AIOSDependency',
    'Invoke-AIOSDependencyFix',
    'Install-MissingDependencies',
    'Test-PythonVersion',
    'Test-PythonDependencies',
    
    # Security & Isolation
    'Initialize-AIOSSecurity',
    'New-AIOSServiceAccount',
    'Set-AIOSFirewallRules',
    'Test-AIOSConfigurationIntegrity',
    'Test-WillingSubmissionRequirement',
    
    # BCM & Performance
    'Get-ButterflyCostMetric',
    'Start-AIOSBCMMonitoring',
    'Invoke-BCMRemediation',
    'Get-SystemResourceSnapshot',
    
    # Log Management
    'Invoke-LogRotation',
    'Write-AIOSMessage',
    'Write-DebugInfo',
    'Get-RecentLogContext',
    
    # Standards & Compliance
    'Invoke-AIOSStandardsCheck',
    'Start-AIOSStandardsMonitoring',
    'Get-AIOSComplianceReport',
    'Invoke-AIOSStandardsFix',
    
    # System Diagnostics
    'Invoke-AIOSSystemDiagnostics',
    'Invoke-AIOSCodeAnalysis',
    'Test-AIOSProjectReadiness',
    'Invoke-AIOSProjectCleanup',
    
    # Administration
    'Update-AIOSComponents',
    'Backup-AIOSData',
    'Restore-AIOSData',
    'Test-AIOSRestartBackoff',
    'Record-AIOSRestartAttempt',
    'Record-AIOSRestartSuccess',
    'Record-AIOSRestartFailure',
    'Enter-AIOSRestartBackoff',
    'Send-AIOSHighPriorityAlert',
    
    # Enterprise Integration
    'Write-AIOSEventLog',
    'Initialize-AIOSEventLog',
    'Invoke-AIOSGracefulShutdown',
    
    # Middleware & Event-Driven Functions
    'Filter-ThrottledCommand',
    'Record-CommandTelemetry',
    'Sync-PythonState',
    'Update-TelemetryCache',
    'Initialize-AIOSMiddleware',
    'Get-AIOSTelemetryMetrics',
    'Invoke-AIOSCommandWithMiddleware',
    
    # Cross-Cutting Concerns
    'Filter-InputSanitizer',
    'Convert-ServiceResponse',
    'Invoke-ResilientCommand',
    'ConvertTo-PowerShellObject',
    'Remove-SensitiveProperties',
    'Test-CircuitBreakerState',
    'Record-CircuitBreakerFailure',
    'Reset-CircuitBreakerState',
    'Invoke-FailoverCommand',
    
    # Utility Functions
    'Test-UnicodeSupport',
    'Initialize-SysAdminTools',
    'Initialize-PythonEnvironment',
    'Show-AIOSHelp'
)

# Module-level variables
$script:ModuleRoot = $PSScriptRoot
$script:ModuleVersion = $ModuleVersion

# Initialize module on import
function Initialize-Module {
    [CmdletBinding()]
    param()
    
    try {
        # Set up module paths
        $script:AIOS_ROOT = "F:\AIOS_Clean"
        $script:CONFIG_FILE = "$script:AIOS_ROOT\config\aios_config.json"
        
        # Load configuration
        if (Test-Path $script:CONFIG_FILE) {
            $script:AIOS_CONFIG = Get-Content $script:CONFIG_FILE -Raw | ConvertFrom-Json -Depth 10
        } else {
            # Use default configuration
            $script:AIOS_CONFIG = @{
                AIOS_ROOT = $script:AIOS_ROOT
                PYTHON_ENV_PATH = "$script:AIOS_ROOT\venv"
                LOG_DIR = "$script:AIOS_ROOT\log\monitoring"
                DEBUG_DIR = "$script:AIOS_ROOT\temp\debug"
                MONITORING_ENABLED = $false
                ADMIN_MODE = $false
                LOG_LEVEL = "INFO"
            }
        }
        
        # Initialize Event Log
        Initialize-AIOSEventLog
        
        Write-Verbose "AIOS-Orchestrator module initialized successfully (v$ModuleVersion)"
    }
    catch {
        Write-Warning "Failed to initialize AIOS-Orchestrator module: $($_.Exception.Message)"
    }
}

# Initialize module when imported
Initialize-Module

# Module cleanup function
function Cleanup-Module {
    [CmdletBinding()]
    param()
    
    try {
        Write-Verbose "Cleaning up AIOS-Orchestrator module"
        # Add any cleanup logic here
    }
    catch {
        Write-Warning "Error during module cleanup: $($_.Exception.Message)"
    }
}

# Register cleanup on module removal
$MyInvocation.MyCommand.ScriptBlock.Module.OnRemove = { Cleanup-Module }
