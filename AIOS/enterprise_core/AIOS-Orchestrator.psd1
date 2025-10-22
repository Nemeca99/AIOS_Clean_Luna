@{
    # Module manifest for AIOS-Orchestrator
    # Enterprise-grade orchestration and monitoring utility for AIOS systems
    
    # Script module or binary module file associated with this manifest
    RootModule = 'AIOS-Orchestrator.psm1'
    
    # Version number of this module
    ModuleVersion = '2.0.0'
    
    # Supported PSEditions
    CompatiblePSEditions = @('Desktop', 'Core')
    
    # ID used to uniquely identify this module
    GUID = '12345678-1234-1234-1234-123456789012'
    
    # Author of this module
    Author = 'AIOS Development Team'
    
    # Company or vendor of this module
    CompanyName = 'AIOS Systems'
    
    # Copyright statement for this module
    Copyright = '(c) 2024 AIOS Systems. All rights reserved.'
    
    # Description of the functionality provided by this module
    Description = 'Enterprise-grade orchestration and monitoring utility for AIOS (Artificial Intelligence Operating System) with advanced health checks, security features, performance monitoring, and self-healing capabilities.'
    
    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '5.1'
    
    # Name of the PowerShell host required by this module
    # PowerShellHostName = ''
    
    # Minimum version of the PowerShell host required by this module
    # PowerShellHostVersion = ''
    
    # Minimum version of the .NET Framework required by this module
    DotNetFrameworkVersion = '4.7.2'
    
    # Minimum version of the common language runtime (CLR) required by this module
    # ClrVersion = ''
    
    # Processor architecture (None, X86, Amd64) required by this module
    ProcessorArchitecture = 'Amd64'
    
    # Modules that must be imported into the global environment prior to importing this module
    RequiredModules = @()
    
    # Assemblies that must be loaded prior to importing this module
    RequiredAssemblies = @(
        'System.Web',
        'System.Diagnostics.Eventing.Reader',
        'System.IO.Compression'
    )
    
    # Script files (.ps1) that are run in the caller's environment prior to importing this module
    ScriptsToProcess = @()
    
    # Type files (.ps1xml) to be loaded when importing this module
    TypesToProcess = @()
    
    # Format files (.ps1xml) to be loaded when importing this module
    FormatsToProcess = @()
    
    # Modules to import as nested modules of the module specified in RootModule/ModuleToProcess
    NestedModules = @()
    
    # Functions to export from this module
    FunctionsToExport = @(
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
    
    # Cmdlets to export from this module
    CmdletsToExport = @()
    
    # Variables to export from this module
    VariablesToExport = @()
    
    # Aliases to export from this module
    AliasesToExport = @(
        'aios',
        'status',
        'health',
        'monitor',
        'analyze',
        'diagnose',
        'logs',
        'readiness',
        'cleanup',
        'standards',
        'standards-monitor',
        'standards-report',
        'standards-fix',
        'bcm',
        'bcm-monitor',
        'wsr',
        'test-unicode',
        'help-aios',
        'stop-aios',
        'restart-aios',
        'process-detail',
        'log-level',
        'config',
        'set-config',
        'log-rotation',
        'clear-logs',
        'bcm-remediation',
        'health-check',
        'health-liveness',
        'health-readiness',
        'perf-counters',
        'perf-monitor',
        'dependency-check',
        'dependency-fix',
        'integrity-check',
        'security-init',
        'firewall-setup',
        'restart-backoff',
        'high-alert',
        'throttle-filter',
        'telemetry',
        'state-sync',
        'middleware-init',
        'telemetry-metrics',
        'cmd-middleware',
        'input-sanitizer',
        'response-transform',
        'resilient-cmd',
        'circuit-breaker',
        'failover'
    )
    
    # DSC resources to export from this module
    DscResourcesToExport = @()
    
    # List of all modules packaged with this module
    ModuleList = @()
    
    # List of all files packaged with this module
    FileList = @(
        'AIOS-Orchestrator.psm1',
        'AIOS-Orchestrator.psd1',
        'aios_powershell_wrapper.ps1',
        'config/aios_config.json'
    )
    
    # Private data to pass to the module specified in RootModule/ModuleToProcess
    PrivateData = @{
        PSData = @{
            # Tags applied to this module
            Tags = @(
                'AIOS',
                'Orchestration',
                'Monitoring',
                'AI',
                'Machine-Learning',
                'Performance',
                'Security',
                'Enterprise',
                'Health-Checks',
                'Self-Healing',
                'BCM',
                'WSR'
            )
            
            # A URL to the license for this module
            LicenseUri = 'https://github.com/aios-systems/aios-orchestrator/LICENSE'
            
            # A URL to the main website for this project
            ProjectUri = 'https://github.com/aios-systems/aios-orchestrator'
            
            # A URL to an icon representing this module
            IconUri = 'https://raw.githubusercontent.com/aios-systems/aios-orchestrator/main/assets/icon.png'
            
            # ReleaseNotes of this module
            ReleaseNotes = @'
## AIOS-Orchestrator v2.0.0 - Enterprise Edition

### 🚀 Major Features
- **Enterprise-Grade Health Checks**: Liveness and readiness endpoints with REST API integration
- **Intelligent Self-Healing**: BCM auto-remediation with adaptive control and restart back-off protection
- **Advanced Security**: WSR enforcement, service account management, firewall isolation, and configuration integrity
- **Performance Monitoring**: Windows Performance Counters integration with real-time alerts
- **Dependency Management**: Automated pip check and dependency resolution
- **Graceful Shutdown**: REST API-based graceful shutdown with fallback mechanisms

### 🔧 New Functions
- `Test-AIOSHealth`, `Test-AIOSLiveness`, `Test-AIOSReadiness`
- `Get-AIOSPerformanceCounters`, `Start-AIOSPerformanceMonitoring`
- `Test-AIOSDependency`, `Invoke-AIOSDependencyFix`
- `Initialize-AIOSSecurity`, `New-AIOSServiceAccount`, `Set-AIOSFirewallRules`
- `Test-AIOSRestartBackoff`, `Send-AIOSHighPriorityAlert`
- `Write-AIOSEventLog`, `Initialize-AIOSEventLog`

### 🛡️ Security Enhancements
- Principle of Least Privilege (PoLP) with dedicated service accounts
- Network isolation via dynamic firewall rules
- Configuration tamper detection with SHA256 integrity checks
- Windows Event Log integration for enterprise monitoring
- Enhanced WSR with audit trails and high-priority alerts

### 📊 Monitoring Improvements
- Real-time performance counter collection
- Intelligent restart back-off to prevent crash loops
- Comprehensive health check system with recommendations
- Enhanced debugging with system resource snapshots
- Log rotation with compression and retention policies

### 🔄 Operational Excellence
- Graceful shutdown with REST API integration
- Dependency integrity checking with automatic resolution
- Configuration management with external JSON files
- Advanced process management with detailed metrics
- Enterprise-grade logging and audit trails

### 📈 Performance Features
- BCM (Butterfly Cost Metric) monitoring with auto-remediation
- Process-specific performance counter collection
- Network traffic monitoring and analysis
- Memory and CPU optimization recommendations
- Real-time alerting for performance thresholds

This release transforms AIOS-Orchestrator into a true enterprise-grade orchestration platform suitable for production AI environments.
'@
            
            # Prerelease string of this module
            # Prerelease = ''
            
            # Flag to indicate whether the module requires explicit user acceptance for install/update/save
            RequireLicenseAcceptance = $false
            
            # External dependent modules of this module
            ExternalModuleDependencies = @()
        }
    }
    
    # HelpInfo URI of this module
    HelpInfoURI = 'https://github.com/aios-systems/aios-orchestrator/wiki'
    
    # Default prefix for commands exported from this module
    # DefaultCommandPrefix = 'AIOS'
}
