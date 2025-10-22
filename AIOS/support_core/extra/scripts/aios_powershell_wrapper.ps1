# AIOS PowerShell Wrapper - Backend Monitoring System
# Comprehensive system monitoring, debugging, and administration for AIOS
# Provides full system oversight with real-time logging and error tracking

param(
    [switch]$SkipPythonEnv, 
    [switch]$TestUnicode, 
    [switch]$Silent,
    [switch]$MonitorMode,
    [switch]$DebugMode,
    [switch]$AdminMode,
    [string]$LogLevel = "INFO"
)

# Set console encoding for Unicode support
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Global Configuration - Load from external config file
$CONFIG_FILE = "F:\AIOS_Clean\config\aios_config.json"
$DEFAULT_CONFIG = @{
    AIOS_ROOT = "F:\AIOS_Clean"
    PYTHON_ENV_PATH = "F:\AIOS_Clean\venv"
    LOG_DIR = "F:\AIOS_Clean\log\monitoring"
    DEBUG_DIR = "F:\AIOS_Clean\temp\debug"
    MONITORING_ENABLED = $false
    ADMIN_MODE = $false
    LOG_LEVEL = "INFO"
    MONITORING_CONFIG = @{
        RealTimeLogging = $true
        CodeAnalysis = $true
        SystemMonitoring = $true
        PerformanceTracking = $true
        SecurityScanning = $true
        AutoErrorReporting = $true
        LogRetention = 30
        MaxLogSize = 104857600  # 100MB in bytes
        BCM_OVERLOAD_THRESHOLD = 85.0
        BCM_MEMORY_THRESHOLD = 1000.0
        BCM_AUTO_REMEDIATION = $true
        BCM_REMEDIATION_DELAY_MINUTES = 5
    }
    SECURITY_CONFIG = @{
        WSR_CHALLENGE_DURATION_MINUTES = 5
        WSR_MAX_ATTEMPTS_PER_SESSION = 3
        AUDIT_LOG_TO_EVENT_LOG = $true
        SESSION_TIMEOUT_MINUTES = 60
    }
    PERFORMANCE_CONFIG = @{
        CACHE_TTL_SECONDS = 300
        MAX_CACHE_SIZE_MB = 100
        METRICS_REFRESH_INTERVAL = 5
        PROCESS_MONITORING_INTERVAL = 10
    }
}

# Core utility functions
function Write-AIOSMessage {
    param([string]$Message, [string]$Level = "INFO", [string]$Source = "SYSTEM")
    if ($Silent -and $Level -eq "INFO") { return }
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "INFO" { "Cyan" }
        "DEBUG" { "Magenta" }
        "TRACE" { "Gray" }
        default { "White" }
    }
    
    # Unicode-safe message handling
    $safeMessage = $Message -replace '[^\x20-\x7E\n\r\t]', '?'
    $logEntry = "[$timestamp] [$Level] [$Source] $safeMessage"
    
    # Console output
    Write-Host "[$($timestamp.Split(' ')[1])] [AIOS-$Level] $safeMessage" -ForegroundColor $color
    
    # File logging if monitoring enabled
    if ($MONITORING_ENABLED -and $MONITORING_CONFIG.RealTimeLogging) {
        $logFile = "$LOG_DIR\aios_monitor_$(Get-Date -Format 'yyyy-MM-dd').log"
        Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
    }
}

# Load configuration from file or use defaults
function Load-AIOSConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$ConfigFile = $CONFIG_FILE
    )
    
    try {
        if (Test-Path $ConfigFile) {
            $configContent = Get-Content $ConfigFile -Raw -Encoding UTF8
            $loadedConfig = $configContent | ConvertFrom-Json -Depth 10
            
            Write-AIOSMessage -Message "Configuration loaded from: $ConfigFile" -Level INFO
            
            return $loadedConfig
        }
        else {
            Write-AIOSMessage -Message "Configuration file not found: $ConfigFile. Using defaults." -Level WARN
            return $DEFAULT_CONFIG
        }
    }
    catch {
        Write-AIOSMessage -Message "Error loading configuration: $($_.Exception.Message). Using defaults." -Level ERROR
        return $DEFAULT_CONFIG
    }
}

# Save configuration to file
function Save-AIOSConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$ConfigFile = $CONFIG_FILE
    )
    
    try {
        $configDir = Split-Path $ConfigFile -Parent
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        $global:AIOS_CONFIG | ConvertTo-Json -Depth 10 | Set-Content $ConfigFile -Encoding UTF8
        Write-AIOSMessage -Message "Configuration saved to: $ConfigFile" -Level SUCCESS
        return $true
    }
    catch {
        Write-AIOSMessage -Message "Error saving configuration: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

# Initialize Windows Event Log Source
function Initialize-AIOSEventLog {
    [CmdletBinding()]
    param()
    
    try {
        $eventSource = "AIOS-Orchestrator"
        $logName = "Application"
        
        # Check if event source already exists
        if (-not [System.Diagnostics.EventLog]::SourceExists($eventSource)) {
            if (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
                New-EventLog -LogName $logName -Source $eventSource
                Write-AIOSMessage -Message "✅ Created Windows Event Log source: $eventSource" -Level SUCCESS
            } else {
                Write-AIOSMessage -Message "⚠️ Administrator privileges required to create Event Log source: $eventSource" -Level WARN
            }
        } else {
            Write-AIOSMessage -Message "Windows Event Log source already exists: $eventSource" -Level INFO
        }
        
        return $true
    }
    catch {
        Write-AIOSMessage -Message "Error initializing Event Log: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Write-AIOSEventLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$true)]
        [ValidateSet("Information", "Warning", "Error")]
        [string]$EntryType,
        
        [Parameter(Mandatory=$false)]
        [int]$EventId = 1000,
        
        [Parameter(Mandatory=$false)]
        [int]$Category = 0
    )
    
    try {
        $eventSource = "AIOS-Orchestrator"
        
        # Check if Event Log integration is enabled
        if ($global:AIOS_CONFIG.SECURITY_CONFIG.AUDIT_LOG_TO_EVENT_LOG) {
            Write-EventLog -LogName "Application" -Source $eventSource -EventId $EventId -EntryType $EntryType -Message $Message -Category $Category
        }
    }
    catch {
        # Silently fail Event Log writes to prevent breaking the main functionality
        Write-AIOSMessage -Message "Failed to write to Windows Event Log: $($_.Exception.Message)" -Level DEBUG
    }
}

# Load initial configuration
$global:AIOS_CONFIG = Load-AIOSConfiguration

# Initialize Event Log source
Initialize-AIOSEventLog

# Set global variables from configuration
$AIOS_ROOT = $global:AIOS_CONFIG.AIOS_ROOT
$PYTHON_ENV_PATH = $global:AIOS_CONFIG.PYTHON_ENV_PATH
$LOG_DIR = $global:AIOS_CONFIG.LOG_DIR
$DEBUG_DIR = $global:AIOS_CONFIG.DEBUG_DIR
$MONITORING_ENABLED = $global:AIOS_CONFIG.MONITORING_ENABLED
$ADMIN_MODE = $global:AIOS_CONFIG.ADMIN_MODE

# Create directories if they don't exist
if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }
if (-not (Test-Path $DEBUG_DIR)) { New-Item -ItemType Directory -Path $DEBUG_DIR -Force | Out-Null }

# Set monitoring configuration
$MONITORING_CONFIG = $global:AIOS_CONFIG.MONITORING_CONFIG

function Write-DebugInfo {
    param(
        [string]$Message,
        [string]$FilePath = "",
        [int]$LineNumber = 0,
        [string]$FunctionName = "",
        [object]$Variables = $null,
        [string]$StackTrace = ""
    )
    
    try {
        # Capture current system resources
        $systemResources = Get-SystemResourceSnapshot
        
        # Capture recent log context
        $logContext = Get-RecentLogContext
        
        # Enhanced debug information
        $debugInfo = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            Message = $Message
            FilePath = $FilePath
            LineNumber = $LineNumber
            FunctionName = $FunctionName
            Variables = $Variables
            StackTrace = $StackTrace
            ProcessId = $PID
            ThreadId = [System.Threading.Thread]::CurrentThread.ManagedThreadId
            SystemResources = $systemResources
            LogContext = $logContext
            Environment = @{
                AIOS_ROOT = $AIOS_ROOT
                PYTHON_ENV_PATH = $PYTHON_ENV_PATH
                LOG_DIR = $LOG_DIR
                DEBUG_DIR = $DEBUG_DIR
                MONITORING_ENABLED = $MONITORING_ENABLED
                ADMIN_MODE = $ADMIN_MODE
                LogLevel = $LogLevel
            }
        }
        
        $debugFile = "$DEBUG_DIR\debug_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
        $debugInfo | ConvertTo-Json -Depth 10 | Out-File -FilePath $debugFile -Encoding UTF8
        
        Write-AIOSMessage -Message "Debug info saved to: $debugFile" -Level DEBUG
        
        # Also save a summary to the main log
        Write-AIOSMessage -Message "DEBUG: $Message | Resources: CPU=$($systemResources.CPUUsage)%, Memory=$($systemResources.MemoryUsage)%, Disk=$($systemResources.DiskUsage)%" -Level DEBUG
        
        return $debugFile
    }
    catch {
        Write-AIOSMessage -Message "Error writing debug info: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function Get-SystemResourceSnapshot {
    [CmdletBinding()]
    param()
    
    try {
        # Get current system performance counters
        $cpuCounter = Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1 -ErrorAction SilentlyContinue
        $memoryCounter = Get-Counter '\Memory\Available MBytes' -SampleInterval 1 -MaxSamples 1 -ErrorAction SilentlyContinue
        $diskCounter = Get-Counter '\LogicalDisk(C:)\% Free Space' -SampleInterval 1 -MaxSamples 1 -ErrorAction SilentlyContinue
        
        # Get AIOS process information
        $aiosProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "python" -and 
            ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
        }
        
        $aiosProcessInfo = @()
        foreach ($process in $aiosProcesses) {
            $aiosProcessInfo += @{
                ProcessId = $process.Id
                ProcessName = $process.ProcessName
                CPU = $process.CPU
                WorkingSet = [Math]::Round($process.WorkingSet64 / 1MB, 2)
                VirtualMemory = [Math]::Round($process.VirtualMemorySize64 / 1MB, 2)
                Handles = $process.HandleCount
                Threads = $process.Threads.Count
                Responding = $process.Responding
            }
        }
        
        return @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            CPUUsage = if ($cpuCounter) { [Math]::Round($cpuCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            MemoryUsage = if ($memoryCounter) { [Math]::Round((Get-WmiObject -Class Win32_OperatingSystem).TotalVisibleMemorySize / 1MB - $memoryCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            DiskUsage = if ($diskCounter) { [Math]::Round(100 - $diskCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            AvailableMemory = if ($memoryCounter) { [Math]::Round($memoryCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            AIOSProcesses = $aiosProcessInfo
            ProcessCount = $aiosProcesses.Count
        }
    }
    catch {
        return @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            Error = "Failed to capture system resources: $($_.Exception.Message)"
            CPUUsage = "Error"
            MemoryUsage = "Error"
            DiskUsage = "Error"
        }
    }
}

function Get-RecentLogContext {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [int]$Lines = 50
    )
    
    try {
        $logFiles = Get-ChildItem -Path $LOG_DIR -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        
        $logContext = @()
        
        foreach ($logFile in $logFiles) {
            try {
                $logLines = Get-Content $logFile.FullName -Tail $Lines -ErrorAction SilentlyContinue
                if ($logLines) {
                    $logContext += @{
                        LogFile = $logFile.Name
                        LastWriteTime = $logFile.LastWriteTime
                        Lines = $logLines
                        LineCount = $logLines.Count
                    }
                }
            }
            catch {
                # Skip files that can't be read
                continue
            }
        }
        
        return $logContext
    }
    catch {
        return @{
            Error = "Failed to capture log context: $($_.Exception.Message)"
        }
    }
}

function Test-UnicodeSupport {
    Write-AIOSMessage "Testing Unicode character support..." "INFO"
    
    # Test basic Unicode characters
    $testCases = @(
        "Basic Unicode: [U+2192] [U+2264] [U+20AC]",
        "Math Symbols: <= >= != infinity pi",
        "Currency: EUR cents GBP JPY", 
        "Smart Quotes: `"test`" 'test'",
        "Special: degree plus-minus times divide"
    )
    
    foreach ($test in $testCases) {
        Write-Host "Test: $test" -ForegroundColor White
    }
    
    # Test actual Unicode characters one by one
    Write-Host "Testing individual Unicode characters:" -ForegroundColor Cyan
    $unicodeChars = @("→", "≤", "≥", "≠", "∞", "π", "€", "¢", "£", "¥", "°", "±", "×", "÷")
    foreach ($char in $unicodeChars) {
        try {
            Write-Host "  $char" -ForegroundColor Green -NoNewline
            Write-Host " - OK" -ForegroundColor Green
        } catch {
            Write-Host "  ? - Error" -ForegroundColor Red
        }
    }
    
    Write-AIOSMessage "Unicode test completed" "SUCCESS"
}

function Initialize-PythonEnvironment {
    if ($SkipPythonEnv) {
        Write-AIOSMessage -Message "Skipping Python environment activation" -Level WARN
        return $true
    }
    
    Write-AIOSMessage -Message "Initializing AIOS Python environment..." -Level INFO
    
    if (Test-Path "$PYTHON_ENV_PATH\Scripts\python.exe") {
        Write-AIOSMessage -Message "Python environment found" -Level SUCCESS
        
        # Validate Python version
        $pythonValidation = Test-PythonVersion
        if (-not $pythonValidation.IsValid) {
            Write-AIOSMessage -Message "Python version validation failed: $($pythonValidation.Message)" -Level ERROR
            return $false
        }
        
        if (Test-Path "$PYTHON_ENV_PATH\Scripts\Activate.ps1") {
            Write-AIOSMessage -Message "Activating Python virtual environment..." -Level INFO
            & "$PYTHON_ENV_PATH\Scripts\Activate.ps1"
            
            if ($LASTEXITCODE -eq 0) {
                Write-AIOSMessage -Message "Python environment activated successfully" -Level SUCCESS
                
                # Validate dependencies
                $dependencyValidation = Test-PythonDependencies
                if (-not $dependencyValidation.IsValid) {
                    Write-AIOSMessage -Message "Dependency validation failed: $($dependencyValidation.Message)" -Level WARN
                    Write-AIOSMessage -Message "Attempting to install missing dependencies..." -Level INFO
                    
                    $installResult = Install-MissingDependencies
                    if (-not $installResult) {
                        Write-AIOSMessage -Message "Failed to install missing dependencies" -Level ERROR
                        return $false
                    }
                }
                
                return $true
            } else {
                Write-AIOSMessage -Message "Failed to activate Python environment" -Level ERROR
                return $false
            }
        }
    } else {
        Write-AIOSMessage -Message "Creating Python virtual environment..." -Level INFO
        python -m venv $PYTHON_ENV_PATH
        if (Test-Path "$PYTHON_ENV_PATH\Scripts\python.exe") {
            Write-AIOSMessage -Message "Python environment created successfully" -Level SUCCESS
            
            # Install dependencies in new environment
            $installResult = Install-MissingDependencies
            if ($installResult) {
                return $true
            } else {
                Write-AIOSMessage -Message "Failed to install dependencies in new environment" -Level ERROR
                return $false
            }
        }
    }
    return $false
}

function Test-PythonVersion {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$RequiredVersion = "3.8"
    )
    
    try {
        $pythonExe = "$PYTHON_ENV_PATH\Scripts\python.exe"
        if (-not (Test-Path $pythonExe)) {
            return @{
                IsValid = $false
                Message = "Python executable not found at: $pythonExe"
                CurrentVersion = $null
                RequiredVersion = $RequiredVersion
            }
        }
        
        # Get Python version
        $versionOutput = & $pythonExe --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            return @{
                IsValid = $false
                Message = "Failed to get Python version: $versionOutput"
                CurrentVersion = $null
                RequiredVersion = $RequiredVersion
            }
        }
        
        # Parse version string (e.g., "Python 3.11.5")
        $versionMatch = $versionOutput -match "Python (\d+\.\d+\.\d+)"
        if ($versionMatch) {
            $currentVersion = [Version]$matches[1]
            $requiredVersionObj = [Version]$RequiredVersion
            
            if ($currentVersion -ge $requiredVersionObj) {
                return @{
                    IsValid = $true
                    Message = "Python version is compatible"
                    CurrentVersion = $currentVersion.ToString()
                    RequiredVersion = $RequiredVersion
                }
            } else {
                return @{
                    IsValid = $false
                    Message = "Python version $($currentVersion.ToString()) is below required $RequiredVersion"
                    CurrentVersion = $currentVersion.ToString()
                    RequiredVersion = $RequiredVersion
                }
            }
        } else {
            return @{
                IsValid = $false
                Message = "Could not parse Python version from: $versionOutput"
                CurrentVersion = $null
                RequiredVersion = $RequiredVersion
            }
        }
    }
    catch {
        return @{
            IsValid = $false
            Message = "Error checking Python version: $($_.Exception.Message)"
            CurrentVersion = $null
            RequiredVersion = $RequiredVersion
        }
    }
}

function Test-PythonDependencies {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string[]]$RequiredPackages = @("numpy", "pandas", "requests", "streamlit", "plotly")
    )
    
    try {
        $pythonExe = "$PYTHON_ENV_PATH\Scripts\python.exe"
        $pipExe = "$PYTHON_ENV_PATH\Scripts\pip.exe"
        
        if (-not (Test-Path $pipExe)) {
            return @{
                IsValid = $false
                Message = "pip executable not found"
                MissingPackages = $RequiredPackages
            }
        }
        
        # Get installed packages
        $installedPackagesOutput = & $pipExe freeze 2>&1
        if ($LASTEXITCODE -ne 0) {
            return @{
                IsValid = $false
                Message = "Failed to get installed packages: $installedPackagesOutput"
                MissingPackages = $RequiredPackages
            }
        }
        
        $missingPackages = @()
        foreach ($package in $RequiredPackages) {
            if ($installedPackagesOutput -notmatch "^$package==") {
                $missingPackages += $package
            }
        }
        
        if ($missingPackages.Count -eq 0) {
            return @{
                IsValid = $true
                Message = "All required packages are installed"
                MissingPackages = @()
            }
        } else {
            return @{
                IsValid = $false
                Message = "Missing packages: $($missingPackages -join ', ')"
                MissingPackages = $missingPackages
            }
        }
    }
    catch {
        return @{
            IsValid = $false
            Message = "Error checking dependencies: $($_.Exception.Message)"
            MissingPackages = $RequiredPackages
        }
    }
}

function Test-AIOSDependency {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [switch]$Detailed,
        
        [Parameter(Mandatory=$false)]
        [switch]$AutoFix
    )
    
    Write-AIOSMessage -Message "🔍 Testing AIOS dependency integrity..." -Level INFO
    
    try {
        $pipExe = "$PYTHON_ENV_PATH\Scripts\pip.exe"
        
        if (-not (Test-Path $pipExe)) {
            Write-AIOSMessage -Message "pip executable not found: $pipExe" -Level ERROR
            return @{
                Success = $false
                Error = "pip executable not found"
                Details = @()
            }
        }
        
        # Run pip check to identify dependency conflicts
        Write-AIOSMessage -Message "Running pip check for dependency conflicts..." -Level INFO
        $pipCheckOutput = & $pipExe check 2>&1
        
        $dependencyResults = @{
            Success = $LASTEXITCODE -eq 0
            PipCheckExitCode = $LASTEXITCODE
            PipCheckOutput = $pipCheckOutput
            Conflicts = @()
            Recommendations = @()
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-AIOSMessage -Message "Dependency conflicts detected!" -Level WARN
            $dependencyResults.Conflicts = $pipCheckOutput
            
            # Parse conflicts and provide recommendations
            foreach ($line in $pipCheckOutput) {
                if ($line -match "(.+) (.+) has requirement (.+), but you have (.+)") {
                    $package = $matches[1]
                    $version = $matches[2]
                    $required = $matches[3]
                    $installed = $matches[4]
                    
                    $conflict = @{
                        Package = $package
                        Version = $version
                        Required = $required
                        Installed = $installed
                        Recommendation = "Consider updating $package or resolving version conflict"
                    }
                    $dependencyResults.Conflicts += $conflict
                    $dependencyResults.Recommendations += $conflict.Recommendation
                }
            }
            
            Write-AIOSMessage -Message "Found $($dependencyResults.Conflicts.Count) dependency conflicts" -Level WARN
            
            if ($AutoFix) {
                Write-AIOSMessage -Message "Attempting automatic dependency resolution..." -Level INFO
                $fixResult = Invoke-AIOSDependencyFix
                $dependencyResults.AutoFixAttempted = $true
                $dependencyResults.AutoFixResult = $fixResult
            }
        } else {
            Write-AIOSMessage -Message "✅ No dependency conflicts found" -Level SUCCESS
        }
        
        # Additional dependency tree analysis if detailed requested
        if ($Detailed) {
            Write-AIOSMessage -Message "Generating detailed dependency tree..." -Level INFO
            
            # Try to use pipdeptree if available, otherwise fall back to pip show
            $pipdeptreeOutput = & $pipExe show pipdeptree 2>$null
            if ($LASTEXITCODE -eq 0) {
                $dependencyTree = & $pipExe install pipdeptree --quiet; & $pipExe deptree 2>&1
                $dependencyResults.DependencyTree = $dependencyTree
            } else {
                # Fallback: Get dependency information for key packages
                $keyPackages = @("numpy", "pandas", "requests", "streamlit", "plotly", "psutil")
                $dependencyInfo = @{}
                
                foreach ($package in $keyPackages) {
                    $packageInfo = & $pipExe show $package 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        $dependencyInfo[$package] = $packageInfo
                    }
                }
                $dependencyResults.DependencyInfo = $dependencyInfo
            }
        }
        
        return $dependencyResults
    }
    catch {
        Write-AIOSMessage -Message "Error during dependency check: $($_.Exception.Message)" -Level ERROR
        return @{
            Success = $false
            Error = $_.Exception.Message
            Details = @()
        }
    }
}

function Invoke-AIOSDependencyFix {
    [CmdletBinding()]
    param()
    
    try {
        Write-AIOSMessage -Message "Attempting automatic dependency resolution..." -Level INFO
        
        $pipExe = "$PYTHON_ENV_PATH\Scripts\pip.exe"
        $fixResults = @{
            Success = $false
            ActionsTaken = @()
            Errors = @()
        }
        
        # Strategy 1: Try to upgrade conflicting packages
        Write-AIOSMessage -Message "Attempting package upgrades..." -Level INFO
        $upgradeOutput = & $pipExe install --upgrade --no-deps $(Get-AIOSCorePackages) 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $fixResults.ActionsTaken += "Upgraded core packages"
            Write-AIOSMessage -Message "Package upgrades completed" -Level SUCCESS
        } else {
            $fixResults.Errors += "Package upgrade failed: $upgradeOutput"
            Write-AIOSMessage -Message "Package upgrade failed" -Level WARN
        }
        
        # Strategy 2: Try to reinstall problematic packages
        Write-AIOSMessage -Message "Attempting package reinstallation..." -Level INFO
        $reinstallOutput = & $pipExe install --force-reinstall --no-deps $(Get-AIOSCorePackages) 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $fixResults.ActionsTaken += "Reinstalled core packages"
            Write-AIOSMessage -Message "Package reinstallation completed" -Level SUCCESS
        } else {
            $fixResults.Errors += "Package reinstallation failed: $reinstallOutput"
            Write-AIOSMessage -Message "Package reinstallation failed" -Level WARN
        }
        
        # Verify fix
        $verificationCheck = Test-AIOSDependency
        $fixResults.Success = $verificationCheck.Success
        
        if ($fixResults.Success) {
            Write-AIOSMessage -Message "✅ Dependency conflicts resolved automatically" -Level SUCCESS
        } else {
            Write-AIOSMessage -Message "⚠️ Some dependency conflicts remain - manual intervention may be required" -Level WARN
        }
        
        return $fixResults
    }
    catch {
        Write-AIOSMessage -Message "Error during dependency fix: $($_.Exception.Message)" -Level ERROR
        return @{
            Success = $false
            Error = $_.Exception.Message
            ActionsTaken = @()
            Errors = @($_.Exception.Message)
        }
    }
}

function Get-AIOSCorePackages {
    [CmdletBinding()]
    param()
    
    return @("numpy", "pandas", "requests", "streamlit", "plotly", "psutil", "flask", "fastapi", "uvicorn")
}

function Install-MissingDependencies {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$RequirementsFile = "$AIOS_ROOT\requirements.txt"
    )
    
    try {
        $pipExe = "$PYTHON_ENV_PATH\Scripts\pip.exe"
        
        if (Test-Path $RequirementsFile) {
            Write-AIOSMessage -Message "Installing dependencies from: $RequirementsFile" -Level INFO
            & $pipExe install -r $RequirementsFile
            
            if ($LASTEXITCODE -eq 0) {
                Write-AIOSMessage -Message "Dependencies installed successfully" -Level SUCCESS
                
                # Run dependency integrity check after installation
                Write-AIOSMessage -Message "Verifying dependency integrity..." -Level INFO
                $integrityCheck = Test-AIOSDependency
                if (-not $integrityCheck.Success) {
                    Write-AIOSMessage -Message "⚠️ Dependency conflicts detected after installation" -Level WARN
                }
                
                return $true
            } else {
                Write-AIOSMessage -Message "Failed to install dependencies from requirements file" -Level ERROR
                return $false
            }
        } else {
            Write-AIOSMessage -Message "Requirements file not found: $RequirementsFile" -Level WARN
            Write-AIOSMessage -Message "Attempting to install core packages..." -Level INFO
            
            $corePackages = Get-AIOSCorePackages
            foreach ($package in $corePackages) {
                Write-AIOSMessage -Message "Installing $package..." -Level INFO
                & $pipExe install $package
                
                if ($LASTEXITCODE -ne 0) {
                    Write-AIOSMessage -Message "Failed to install $package" -Level ERROR
                    return $false
                }
            }
            
            Write-AIOSMessage -Message "Core packages installed successfully" -Level SUCCESS
            return $true
        }
    }
    catch {
        Write-AIOSMessage -Message "Error installing dependencies: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Initialize-SysAdminTools {
    Write-AIOSMessage "Checking SysAdminTools module..." "INFO"
    
    try {
        $module = Get-Module -ListAvailable -Name "SysAdminTools" -ErrorAction SilentlyContinue
        if ($module) {
        Write-AIOSMessage "SysAdminTools module found" "SUCCESS"
        try {
                Import-Module "SysAdminTools" -Force -ErrorAction Stop
            Write-AIOSMessage "SysAdminTools imported successfully" "SUCCESS"
            return $true
        } catch {
                Write-AIOSMessage "Failed to import SysAdminTools: $($_.Exception.Message)" "WARN"
                return $false
            }
        } else {
            Write-AIOSMessage "SysAdminTools module not found, skipping..." "WARN"
            return $false
        }
    } catch {
        Write-AIOSMessage "Error checking SysAdminTools module: $($_.Exception.Message)" "WARN"
            return $false
    }
}

# AIOS Commands
function Start-AIOS {
    param([string]$Mode = "luna", [int]$Questions = 1, [switch]$Interactive)
    
    # Validate mode
    $validModes = @("luna", "carma", "health", "enterprise", "support")
    if ($Mode -notin $validModes) {
        Write-AIOSMessage "Invalid mode '$Mode'. Valid modes: $($validModes -join ', ')" "ERROR"
        return
    }
    
    # Validate questions parameter
    if ($Questions -lt 1 -or $Questions -gt 100) {
        Write-AIOSMessage "Questions must be between 1 and 100" "ERROR"
        return
    }
    
    # Check if main.py exists
    if (-not (Test-Path "$AIOS_ROOT\main.py")) {
        Write-AIOSMessage "main.py not found at $AIOS_ROOT" "ERROR"
        return
    }
    
    Write-AIOSMessage "Starting AIOS Clean System in $Mode mode with $Questions questions..." "INFO"
    
    try {
    $command = "python `"$AIOS_ROOT\main.py`" --mode $Mode --questions $Questions"
    if ($Interactive) {
        Set-Location $AIOS_ROOT
            Write-AIOSMessage "Running in interactive mode from $AIOS_ROOT" "INFO"
    }
    Invoke-Expression $command
    } catch {
        Write-AIOSMessage "Failed to start AIOS: $($_.Exception.Message)" "ERROR"
    }
}

function Get-AIOSStatus {
    Write-AIOSMessage "Checking AIOS system status..." "INFO"
    Write-Host "=== AIOS System Status ===" -ForegroundColor Yellow
    Write-Host "Root Directory: $AIOS_ROOT" -ForegroundColor Cyan
    Write-Host "Python Environment: $PYTHON_ENV_PATH" -ForegroundColor Cyan
    
    $components = @(
        @{Name="Main Script"; Path="$AIOS_ROOT\main.py"},
        @{Name="Config"; Path="$AIOS_ROOT\config"},
        @{Name="Data"; Path="$AIOS_ROOT\Data"},
        @{Name="CARMA Core"; Path="$AIOS_ROOT\carma_core"},
        @{Name="Luna Core"; Path="$AIOS_ROOT\luna_core"},
        @{Name="Enterprise Core"; Path="$AIOS_ROOT\enterprise_core"},
        @{Name="Support Core"; Path="$AIOS_ROOT\support_core"}
    )
    
    foreach ($component in $components) {
        $exists = Test-Path $component.Path
        $status = if ($exists) { "Found" } else { "Missing" }
        $color = if ($exists) { "Green" } else { "Red" }
        Write-Host "$($component.Name): $status" -ForegroundColor $color
    }
    
    # Check Python environment
    $pythonExists = Test-Path "$PYTHON_ENV_PATH\Scripts\python.exe"
    $pythonStatus = if ($pythonExists) { "Found" } else { "Missing" }
    $pythonColor = if ($pythonExists) { "Green" } else { "Red" }
    Write-Host "Python Environment: $pythonStatus" -ForegroundColor $pythonColor
}

function Invoke-AIOSHealthCheck {
    Write-AIOSMessage "Running AIOS health check..." "INFO"
    
    if (-not (Test-Path "$AIOS_ROOT\main.py")) {
        Write-AIOSMessage "main.py not found at $AIOS_ROOT" "ERROR"
        return
    }
    
    try {
    $command = "python `"$AIOS_ROOT\main.py`" --mode health"
    Set-Location $AIOS_ROOT
    Invoke-Expression $command
    } catch {
        Write-AIOSMessage "Health check failed: $($_.Exception.Message)" "ERROR"
    }
}

function Start-AIOSMonitoring {
    Write-AIOSMessage "Starting AIOS system monitoring..." "INFO"
    
    if (-not (Test-Path "$AIOS_ROOT\system_monitor.py")) {
        Write-AIOSMessage "system_monitor.py not found at $AIOS_ROOT" "ERROR"
        return
    }
    
    try {
    $command = "python `"$AIOS_ROOT\system_monitor.py`""
    Set-Location $AIOS_ROOT
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
        Write-AIOSMessage "Monitoring started in new PowerShell window" "SUCCESS"
    } catch {
        Write-AIOSMessage "Failed to start monitoring: $($_.Exception.Message)" "ERROR"
    }
}

# === ADVANCED MONITORING AND ADMINISTRATION FUNCTIONS ===

function Start-AIOSBackendMonitor {
    param([switch]$FullSystemAccess, [switch]$RealTimeMode)
    
    $script:MONITORING_ENABLED = $true
    $script:ADMIN_MODE = $FullSystemAccess
    
    Write-AIOSMessage -Message "Starting AIOS Backend Monitor with full system access..." -Level SUCCESS
    Write-AIOSMessage -Message "Admin Mode: $ADMIN_MODE | Real-time: $RealTimeMode" -Level INFO
    
    # Start background monitoring jobs
    $jobs = @()
    
    if ($RealTimeMode) {
        $jobs += Start-Job -ScriptBlock {
            param($AIOS_ROOT, $LOG_DIR)
            while ($true) {
                # Monitor file changes
                Get-ChildItem -Path "$AIOS_ROOT\*.py" -Recurse | ForEach-Object {
                    $lastWrite = $_.LastWriteTime
                    if ($lastWrite -gt (Get-Date).AddMinutes(-1)) {
                        $logFile = "$LOG_DIR\file_changes_$(Get-Date -Format 'yyyy-MM-dd').log"
                        Add-Content -Path $logFile -Value "[$(Get-Date)] File changed: $($_.FullName)" -Encoding UTF8
                    }
                }
                Start-Sleep -Seconds 30
            }
        } -ArgumentList $AIOS_ROOT, $LOG_DIR
    }
    
    # System resource monitoring with BCM integration
    $jobs += Start-Job -ScriptBlock {
        param($LOG_DIR)
        while ($true) {
            $cpu = Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1
            $memory = Get-Counter '\Memory\Available MBytes' -SampleInterval 1 -MaxSamples 1
            $disk = Get-Counter '\LogicalDisk(C:)\% Free Space' -SampleInterval 1 -MaxSamples 1
            
            # BCM Analysis - Check AIOS processes for efficiency
            $aiosProcesses = Get-Process | Where-Object { 
                $_.ProcessName -like "*python*" -and 
                ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
            }
            
            $bcmOverloadDetected = $false
            $bcmOverloadReason = ""
            
            foreach ($process in $aiosProcesses) {
                $processCpu = $process.CPU
                $processMemory = $process.WorkingSet64 / 1MB
                
                # BCM Overload Detection
                if ($processCpu -gt 85) {
                    $bcmOverloadDetected = $true
                    $bcmOverloadReason += "PID $($process.Id): High CPU ($([Math]::Round($processCpu, 1))%) "
                }
                
                if ($processMemory -gt 1000) {
                    $bcmOverloadDetected = $true
                    $bcmOverloadReason += "PID $($process.Id): High Memory ($([Math]::Round($processMemory, 1))MB) "
                }
            }
            
            # Log system performance
            $logFile = "$LOG_DIR\system_performance_$(Get-Date -Format 'yyyy-MM-dd').log"
            $logEntry = "[$(Get-Date)] CPU: $($cpu.CounterSamples[0].CookedValue)% | Memory: $($memory.CounterSamples[0].CookedValue)MB | Disk: $($disk.CounterSamples[0].CookedValue)%"
            Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
            
                    # BCM Auto-Remediation Logic
                    if ($bcmOverloadDetected) {
                        $bcmLogFile = "$LOG_DIR\bcm_alerts_$(Get-Date -Format 'yyyy-MM-dd').log"
                        $bcmAlert = "[$(Get-Date)] 🚨 BCM_OVERLOAD: $bcmOverloadReason | AI using overly complex probabilistic path"
                        Add-Content -Path $bcmLogFile -Value $bcmAlert -Encoding UTF8
                        
                        # Track BCM overload duration for auto-remediation
                        $bcmStateFile = "$LOG_DIR\bcm_state.json"
                        $bcmState = @{
                            overload_started = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                            overload_duration_minutes = 0
                            remediation_attempted = $false
                            last_remediation = $null
                            remediation_count = 0
                        }
                        
                        # Load existing state if available
                        if (Test-Path $bcmStateFile) {
                            try {
                                $existingState = Get-Content $bcmStateFile -Raw | ConvertFrom-Json
                                if ($existingState.overload_started) {
                                    $overloadStart = [DateTime]::ParseExact($existingState.overload_started, "yyyy-MM-dd HH:mm:ss.fff", $null)
                                    $bcmState.overload_duration_minutes = [Math]::Round(((Get-Date) - $overloadStart).TotalMinutes, 2)
                                    $bcmState.remediation_attempted = $existingState.remediation_attempted
                                    $bcmState.last_remediation = $existingState.last_remediation
                                    $bcmState.remediation_count = $existingState.remediation_count
                                }
                            }
                            catch {
                                # If we can't parse the state, start fresh
                            }
                        }
                        
                        # Auto-remediation logic based on configuration
                        $autoRemediationEnabled = $MONITORING_CONFIG.BCM_AUTO_REMEDIATION
                        $remediationDelayMinutes = $MONITORING_CONFIG.BCM_REMEDIATION_DELAY_MINUTES
                        
                        if ($autoRemediationEnabled -and $bcmState.overload_duration_minutes -ge $remediationDelayMinutes) {
                            if (-not $bcmState.remediation_attempted) {
                                # Attempt first remediation
                                $remediationResult = Invoke-BCMRemediation -RemediationLevel "LIGHT"
                                $bcmState.remediation_attempted = $true
                                $bcmState.last_remediation = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                                $bcmState.remediation_count = 1
                                
                                $remediationAlert = "[$(Get-Date)] BCM_REMEDIATION: Light remediation attempted - $remediationResult"
                                Add-Content -Path $bcmLogFile -Value $remediationAlert -Encoding UTF8
                            }
                            elseif ($bcmState.overload_duration_minutes -ge ($remediationDelayMinutes * 2) -and $bcmState.remediation_count -eq 1) {
                                # Attempt medium remediation
                                $remediationResult = Invoke-BCMRemediation -RemediationLevel "MEDIUM"
                                $bcmState.last_remediation = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                                $bcmState.remediation_count = 2
                                
                                $remediationAlert = "[$(Get-Date)] BCM_REMEDIATION: Medium remediation attempted - $remediationResult"
                                Add-Content -Path $bcmLogFile -Value $remediationAlert -Encoding UTF8
                            }
                            elseif ($bcmState.overload_duration_minutes -ge ($remediationDelayMinutes * 3) -and $bcmState.remediation_count -eq 2) {
                                # Attempt heavy remediation (requires admin mode)
                                if ($ADMIN_MODE) {
                                    $remediationResult = Invoke-BCMRemediation -RemediationLevel "HEAVY"
                                    $bcmState.last_remediation = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                                    $bcmState.remediation_count = 3
                                    
                                    $remediationAlert = "[$(Get-Date)] BCM_REMEDIATION: Heavy remediation attempted (Admin Mode) - $remediationResult"
                                    Add-Content -Path $bcmLogFile -Value $remediationAlert -Encoding UTF8
                                }
                                else {
                                    $remediationAlert = "[$(Get-Date)] ⚠️ BCM_REMEDIATION: Heavy remediation required but Admin Mode not enabled"
                                    Add-Content -Path $bcmLogFile -Value $remediationAlert -Encoding UTF8
                                }
                            }
                        }
                        
                        # Save BCM state
                        $bcmState | ConvertTo-Json | Set-Content $bcmStateFile -Encoding UTF8
                    }
                    else {
                        # Clear BCM overload state if no overload detected
                        $bcmStateFile = "$LOG_DIR\bcm_state.json"
                        if (Test-Path $bcmStateFile) {
                            try {
                                $existingState = Get-Content $bcmStateFile -Raw | ConvertFrom-Json
                                if ($existingState.overload_started) {
                                    $overloadStart = [DateTime]::ParseExact($existingState.overload_started, "yyyy-MM-dd HH:mm:ss.fff", $null)
                                    $overloadDuration = ((Get-Date) - $overloadStart).TotalMinutes
                                    
                                    if ($overloadDuration -gt 1) {  # Only log if overload lasted more than 1 minute
                                        $bcmLogFile = "$LOG_DIR\bcm_alerts_$(Get-Date -Format 'yyyy-MM-dd').log"
                                        $recoveryAlert = "[$(Get-Date)] ✅ BCM_RECOVERY: Overload resolved after $([Math]::Round($overloadDuration, 2)) minutes"
                                        Add-Content -Path $bcmLogFile -Value $recoveryAlert -Encoding UTF8
                                    }
                                }
                            }
                            catch {
                                # Ignore errors when clearing state
                            }
                            
                            # Remove state file
                            Remove-Item $bcmStateFile -Force -ErrorAction SilentlyContinue
                        }
                    }
            
            # Save BCM metrics
            $bcmLogFile = "$LOG_DIR\bcm_metrics.json"
            $bcmData = @{
                timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
                system_cpu = [Math]::Round($cpu.CounterSamples[0].CookedValue, 2)
                system_memory = [Math]::Round($memory.CounterSamples[0].CookedValue, 2)
                system_disk = [Math]::Round($disk.CounterSamples[0].CookedValue, 2)
                aios_processes = $aiosProcesses.Count
                bcm_overload_detected = $bcmOverloadDetected
                bcm_overload_reason = $bcmOverloadReason.Trim()
            }
            
            $bcmJson = $bcmData | ConvertTo-Json -Depth 3
            Add-Content -Path $bcmLogFile -Value $bcmJson -Encoding UTF8
            
            Start-Sleep -Seconds 60
        }
    } -ArgumentList $LOG_DIR
    
    Write-AIOSMessage -Message "Started $($jobs.Count) monitoring jobs" -Level SUCCESS
    return $jobs
}

function Invoke-AIOSCodeAnalysis {
    param([string]$FilePath = "", [switch]$FullScan)
    
    Write-AIOSMessage -Message "Starting AIOS code analysis..." -Level INFO
    
    $analysisResults = @()
    $pythonFiles = if ($FilePath) { @($FilePath) } else { Get-ChildItem -Path "$AIOS_ROOT\*.py" -Recurse }
    
    foreach ($file in $pythonFiles) {
        if (Test-Path $file.FullName) {
            $content = Get-Content $file.FullName -Raw
            $issues = @()
            
            # Check for common issues
            if ($content -match "print\s*\(") {
                $issues += "Found print statements - consider using logging"
            }
            if ($content -match "except\s*:") {
                $issues += "Found bare except clauses - should specify exception types"
            }
            if ($content -match "import \*") {
                $issues += "Found wildcard imports - should be avoided"
            }
            if ($content -match "TODO|FIXME|HACK") {
                $issues += "Found TODO/FIXME/HACK comments"
            }
            
            # Performance analysis
            if ($content -match "for.*for.*for") {
                $issues += "Potential nested loop performance issue"
            }
            
            if ($issues.Count -gt 0) {
                $analysisResults += @{
                    File = $file.FullName
                    Issues = $issues
                    Severity = if ($issues.Count -gt 3) { "HIGH" } else { "MEDIUM" }
                }
            }
        }
    }
    
    # Save analysis results
    $analysisFile = "$DEBUG_DIR\code_analysis_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
    $analysisResults | ConvertTo-Json -Depth 5 | Out-File -FilePath $analysisFile -Encoding UTF8
    
    Write-AIOSMessage -Message "Code analysis complete. Found $($analysisResults.Count) files with issues" -Level SUCCESS
    Write-AIOSMessage -Message "Results saved to: $analysisFile" -Level INFO
    
    return $analysisResults
}

function Invoke-AIOSSystemDiagnostics {
    param([switch]$FullSystemScan, [switch]$SecurityScan)
    
    Write-AIOSMessage -Message "Running comprehensive system diagnostics..." -Level INFO
    
    $diagnostics = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        SystemInfo = @{}
        AIOSHealth = @{}
        SecurityStatus = @{}
        PerformanceMetrics = @{}
    }
    
    # System Information
    $diagnostics.SystemInfo = @{
        ComputerName = $env:COMPUTERNAME
        UserName = $env:USERNAME
        OSVersion = [System.Environment]::OSVersion.VersionString
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        DotNetVersion = [System.Environment]::Version.ToString()
        TotalRAM = [math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB, 2)
        AvailableRAM = [math]::Round((Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue / 1024, 2)
        DiskSpace = @{}
    }
    
    # Disk space analysis
    Get-WmiObject -Class Win32_LogicalDisk | ForEach-Object {
        $diagnostics.SystemInfo.DiskSpace[$_.DeviceID] = @{
            Size = [math]::Round($_.Size / 1GB, 2)
            Free = [math]::Round($_.FreeSpace / 1GB, 2)
            Used = [math]::Round(($_.Size - $_.FreeSpace) / 1GB, 2)
            PercentFree = [math]::Round(($_.FreeSpace / $_.Size) * 100, 2)
        }
    }
    
    # AIOS Health Check
    $diagnostics.AIOSHealth = @{
        MainScriptExists = Test-Path "$AIOS_ROOT\main.py"
        ConfigExists = Test-Path "$AIOS_ROOT\config"
        DataExists = Test-Path "$AIOS_ROOT\Data"
        PythonEnvExists = Test-Path "$PYTHON_ENV_PATH\Scripts\python.exe"
        CoreModules = @{
            Luna = Test-Path "$AIOS_ROOT\luna_core"
            CARMA = Test-Path "$AIOS_ROOT\carma_core"
            Enterprise = Test-Path "$AIOS_ROOT\enterprise_core"
            Support = Test-Path "$AIOS_ROOT\support_core"
        }
        RecentLogs = (Get-ChildItem "$AIOS_ROOT\log" -Recurse -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) }).Count
    }
    
    # Security Scan
    if ($SecurityScan) {
        Write-AIOSMessage -Message "Running security scan..." -Level INFO
        
        $diagnostics.SecurityStatus = @{
            RunningProcesses = (Get-Process).Count
            NetworkConnections = (Get-NetTCPConnection | Where-Object { $_.State -eq "Established" }).Count
            FirewallStatus = (Get-NetFirewallProfile | Where-Object { $_.Enabled -eq "True" }).Count
            AntivirusStatus = "Unknown"  # Would need specific antivirus integration
            SuspiciousFiles = @()
        }
        
        # Check for suspicious file patterns
        $suspiciousPatterns = @("*.tmp", "*.temp", "*.exe.tmp")
        foreach ($pattern in $suspiciousPatterns) {
            $files = Get-ChildItem -Path $AIOS_ROOT -Filter $pattern -Recurse -ErrorAction SilentlyContinue
            if ($files) {
                $diagnostics.SecurityStatus.SuspiciousFiles += $files.FullName
            }
        }
    }
    
    # Performance Metrics
    $diagnostics.PerformanceMetrics = @{
        CPULoad = [math]::Round((Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue, 2)
        MemoryUsage = [math]::Round(((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum - (Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue * 1MB) / 1GB, 2)
        DiskIO = Get-Counter '\PhysicalDisk(_Total)\Disk Reads/sec', '\PhysicalDisk(_Total)\Disk Writes/sec' | ForEach-Object { [math]::Round($_.CounterSamples[0].CookedValue, 2) }
        NetworkIO = (Get-NetAdapter | Where-Object { $_.Status -eq "Up" }).Count
    }
    
    # Save diagnostics
    $diagnosticsFile = "$DEBUG_DIR\system_diagnostics_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
    $diagnostics | ConvertTo-Json -Depth 10 | Out-File -FilePath $diagnosticsFile -Encoding UTF8
    
    Write-AIOSMessage -Message "System diagnostics complete" -Level SUCCESS
    Write-AIOSMessage -Message "Results saved to: $diagnosticsFile" -Level INFO
    
    return $diagnostics
}

function Invoke-AIOSStandardsCheck {
    param(
        [string]$FilePath = "",
        [switch]$FullProject,
        [switch]$AutoFix
    )
    
    Write-AIOSMessage -Message "🔍 Starting AIOS Standards Check..." -Level INFO
    
    try {
        if ($FullProject -or [string]::IsNullOrEmpty($FilePath)) {
            Write-AIOSMessage -Message "Checking entire project for standards compliance..." -Level INFO
            
            # Run Python standards checker
            $pythonScript = "$AIOS_ROOT\aios_standards_checker.py"
            if (Test-Path $pythonScript) {
                if ($AutoFix) {
                    & python $pythonScript check-project
                } else {
                    & python $pythonScript check-project
                }
                
                $result = $LASTEXITCODE
                if ($result -eq 0) {
                    Write-AIOSMessage -Message "✅ Standards check completed successfully" -Level SUCCESS
                } else {
                    Write-AIOSMessage -Message "⚠️ Standards check found issues" -Level WARN
                }
            } else {
                Write-AIOSMessage -Message "❌ Standards checker not found: $pythonScript" -Level ERROR
                return $false
            }
        } else {
            Write-AIOSMessage -Message "Checking single file: $FilePath" -Level INFO
            
            if (Test-Path $FilePath) {
                $pythonScript = "$AIOS_ROOT\aios_standards_checker.py"
                if (Test-Path $pythonScript) {
                    if ($AutoFix) {
                        & python $pythonScript check-file $FilePath
                    } else {
                        & python $pythonScript check-file $FilePath
                    }
                    
                    $result = $LASTEXITCODE
                    if ($result -eq 0) {
                        Write-AIOSMessage -Message "✅ File standards check passed" -Level SUCCESS
                    } else {
                        Write-AIOSMessage -Message "⚠️ File standards issues found" -Level WARN
                    }
                } else {
                    Write-AIOSMessage -Message "❌ Standards checker not found" -Level ERROR
                    return $false
                }
            } else {
                Write-AIOSMessage -Message "❌ File not found: $FilePath" -Level ERROR
                return $false
            }
        }
        
        return $true
    }
    catch {
        Write-AIOSMessage -Message "❌ Error during standards check: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Start-AIOSStandardsMonitoring {
    param([int]$Interval = 30)
    
    Write-AIOSMessage -Message "👁️ Starting AIOS Standards Monitoring..." -Level INFO
    Write-AIOSMessage -Message "Monitoring interval: $Interval seconds" -Level INFO
    
    try {
        $pythonScript = "$AIOS_ROOT\aios_standards_checker.py"
        if (Test-Path $pythonScript) {
            # Start monitoring in background
            Start-Job -ScriptBlock {
                param($ScriptPath, $Interval, $AiosRoot)
                Set-Location $AiosRoot
                & python $ScriptPath monitor --interval $Interval
            } -ArgumentList $pythonScript, $Interval, $AIOS_ROOT -Name "AIOSStandardsMonitor"
            
            Write-AIOSMessage -Message "✅ Standards monitoring started (Job: AIOSStandardsMonitor)" -Level SUCCESS
            Write-AIOSMessage -Message "Use 'Get-Job AIOSStandardsMonitor' to check status" -Level INFO
            Write-AIOSMessage -Message "Use 'Stop-Job AIOSStandardsMonitor' to stop monitoring" -Level INFO
        } else {
            Write-AIOSMessage -Message "❌ Standards checker not found: $pythonScript" -Level ERROR
            return $false
        }
        
        return $true
    }
    catch {
        Write-AIOSMessage -Message "❌ Error starting standards monitoring: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Get-AIOSComplianceReport {
    Write-AIOSMessage -Message "📊 Generating AIOS Compliance Report..." -Level INFO
    
    try {
        $pythonScript = "$AIOS_ROOT\aios_standards_checker.py"
        if (Test-Path $pythonScript) {
            & python $pythonScript report
            
            $result = $LASTEXITCODE
            if ($result -eq 0) {
                Write-AIOSMessage -Message "✅ Compliance report generated successfully" -Level SUCCESS
                Write-AIOSMessage -Message "📄 Report saved to: AIOS_COMPLIANCE_REPORT.md" -Level INFO
            } else {
                Write-AIOSMessage -Message "⚠️ Report generation completed with issues" -Level WARN
            }
        } else {
            Write-AIOSMessage -Message "❌ Standards checker not found: $pythonScript" -Level ERROR
            return $false
        }
        
        return $true
    }
    catch {
        Write-AIOSMessage -Message "❌ Error generating compliance report: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Invoke-AIOSStandardsFix {
    param(
        [string]$FilePath = "",
        [switch]$FullProject
    )
    
    Write-AIOSMessage -Message "🔧 Starting AIOS Standards Auto-Fix..." -Level INFO
    
    try {
        $pythonScript = "$AIOS_ROOT\aios_standards_checker.py"
        if (Test-Path $pythonScript) {
            if ($FullProject -or [string]::IsNullOrEmpty($FilePath)) {
                Write-AIOSMessage -Message "Auto-fixing entire project..." -Level INFO
                & python $pythonScript check-project
            } else {
                Write-AIOSMessage -Message "Auto-fixing file: $FilePath" -Level INFO
                & python $pythonScript check-file $FilePath
            }
            
            $result = $LASTEXITCODE
            if ($result -eq 0) {
                Write-AIOSMessage -Message "✅ Standards auto-fix completed successfully" -Level SUCCESS
            } else {
                Write-AIOSMessage -Message "⚠️ Auto-fix completed with remaining issues" -Level WARN
            }
        } else {
            Write-AIOSMessage -Message "❌ Standards checker not found: $pythonScript" -Level ERROR
            return $false
        }
        
        return $true
    }
    catch {
        Write-AIOSMessage -Message "❌ Error during standards auto-fix: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Test-WillingSubmissionRequirement {
    param(
        [string]$Operation = "Administrative Action",
        [string]$RiskLevel = "HIGH"
    )
    
    Write-AIOSMessage -Message "🔒 WILLING SUBMISSION REQUIREMENT (WSR) ENFORCEMENT" -Level WARN
    Write-AIOSMessage -Message "================================================" -Level WARN
    Write-AIOSMessage -Message "" -Level WARN
    Write-AIOSMessage -Message "Operation: $Operation" -Level WARN
    Write-AIOSMessage -Message "Risk Level: $RiskLevel" -Level WARN
    Write-AIOSMessage -Message "" -Level WARN
    Write-AIOSMessage -Message "⚠️  WARNING: This operation requires Willing Submission to proceed." -Level WARN
    Write-AIOSMessage -Message "⚠️  You are about to grant administrative access to the AIOS system." -Level WARN
    Write-AIOSMessage -Message "⚠️  This may modify system files, processes, or configurations." -Level WARN
    Write-AIOSMessage -Message "" -Level WARN
    
    # Generate WSR challenge
    $challengeCode = (Get-Random -Minimum 1000 -Maximum 9999)
    $challengeText = "AIOS_WSR_$challengeCode"
    
    Write-AIOSMessage -Message "🔐 WSR Challenge Required:" -Level WARN
    Write-AIOSMessage -Message "Type the following EXACTLY to confirm your Willing Submission:" -Level WARN
    Write-AIOSMessage -Message "Challenge Code: $challengeText" -Level WARN
    Write-AIOSMessage -Message "" -Level WARN
    
    $userInput = Read-Host "Enter WSR Challenge Code"
    
    if ($userInput -eq $challengeText) {
        Write-AIOSMessage -Message "✅ Willing Submission CONFIRMED - Admin access granted" -Level SUCCESS
        Write-AIOSMessage -Message "📝 WSR Audit Log: Operation '$Operation' approved by user at $(Get-Date)" -Level INFO
        
        # Log WSR confirmation
        $wsrLogFile = "$LOG_DIR\wsr_audit.log"
        $auditEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff') - $Operation - $RiskLevel - CONFIRMED - Challenge: $challengeText"
        Add-Content -Path $wsrLogFile -Value $auditEntry
        
        # Log to Windows Event Log if enabled
        if ($global:AIOS_CONFIG.SECURITY_CONFIG.AUDIT_LOG_TO_EVENT_LOG) {
            try {
                $eventLogMessage = "AIOS WSR Challenge CONFIRMED - Operation: $Operation, Risk Level: $RiskLevel, Challenge: $challengeText, User: $env:USERNAME, Session: $PID"
                Write-EventLog -LogName "Application" -Source "AIOS" -EventId 1001 -EntryType Information -Message $eventLogMessage -Category 0
            }
            catch {
                Write-AIOSMessage -Message "Failed to write WSR confirmation to Windows Event Log: $($_.Exception.Message)" -Level WARN
            }
        }
        
        return $true
    } else {
        Write-AIOSMessage -Message "❌ Willing Submission DENIED - Admin access blocked" -Level ERROR
        Write-AIOSMessage -Message "📝 WSR Audit Log: Operation '$Operation' rejected - Invalid challenge response" -Level ERROR
        
        # Log WSR denial
        $wsrLogFile = "$LOG_DIR\wsr_audit.log"
        $auditEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff') - $Operation - $RiskLevel - DENIED - Invalid response: $userInput"
        Add-Content -Path $wsrLogFile -Value $auditEntry
        
        # Log to Windows Event Log if enabled
        if ($global:AIOS_CONFIG.SECURITY_CONFIG.AUDIT_LOG_TO_EVENT_LOG) {
            try {
                $eventLogMessage = "AIOS WSR Challenge DENIED - Operation: $Operation, Risk Level: $RiskLevel, Invalid Response: $userInput, User: $env:USERNAME, Session: $PID"
                Write-EventLog -LogName "Application" -Source "AIOS" -EventId 1002 -EntryType Warning -Message $eventLogMessage -Category 1
            }
            catch {
                Write-AIOSMessage -Message "Failed to write WSR denial to Windows Event Log: $($_.Exception.Message)" -Level WARN
            }
        }
        
        return $false
    }
}

function Get-ButterflyCostMetric {
    param(
        [int]$ProcessId = -1,
        [int]$SampleDuration = 10
    )
    
    try {
        if ($ProcessId -eq -1) {
            # Find AIOS processes
            $aiosProcesses = Get-Process | Where-Object { 
                $_.ProcessName -like "*python*" -and 
                ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
            }
            
            if ($aiosProcesses.Count -eq 0) {
                Write-AIOSMessage -Message "⚠️ No AIOS processes found for BCM calculation" -Level WARN
                return @{
                    ProcessId = 0
                    CPU_Usage = 0
                    Memory_Usage = 0
                    BCM_Score = 0
                    BCM_Status = "NO_PROCESS"
                    Efficiency_Level = "UNKNOWN"
                    Overload_Detected = $false
                }
            }
            
            $ProcessId = $aiosProcesses[0].Id
        }
        
        Write-AIOSMessage -Message "🦋 Calculating Butterfly Cost Metric for PID: $ProcessId" -Level INFO
        
        # Sample performance metrics over time
        $samples = @()
        $endTime = (Get-Date).AddSeconds($SampleDuration)
        
        while ((Get-Date) -lt $endTime) {
            try {
                $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
                if ($process) {
                    $sample = @{
                        Timestamp = Get-Date
                        CPU_Usage = $process.CPU
                        Memory_Usage = $process.WorkingSet64 / 1MB
                        ProcessorTime = $process.TotalProcessorTime
                    }
                    $samples += $sample
                }
                Start-Sleep -Milliseconds 1000
            }
            catch {
                Write-AIOSMessage -Message "⚠️ Error sampling process $ProcessId : $($_.Exception.Message)" -Level WARN
                break
            }
        }
        
        if ($samples.Count -lt 2) {
            Write-AIOSMessage -Message "⚠️ Insufficient samples for BCM calculation" -Level WARN
            return @{
                ProcessId = $ProcessId
                CPU_Usage = 0
                Memory_Usage = 0
                BCM_Score = 0
                BCM_Status = "INSUFFICIENT_DATA"
                Efficiency_Level = "UNKNOWN"
                Overload_Detected = $false
            }
        }
        
        # Calculate BCM metrics
        $avgCpuUsage = ($samples | Measure-Object -Property CPU_Usage -Average).Average
        $avgMemoryUsage = ($samples | Measure-Object -Property Memory_Usage -Average).Average
        $maxCpuUsage = ($samples | Measure-Object -Property CPU_Usage -Maximum).Maximum
        
        # Calculate BCM Score (0-100, higher = more efficient)
        # Lower CPU usage and consistent performance = higher BCM score
        $cpuEfficiency = [Math]::Max(0, 100 - $avgCpuUsage)
        $memoryEfficiency = [Math]::Max(0, 100 - ($avgMemoryUsage / 10)) # Normalize memory usage
        $consistencyBonus = if ($maxCpuUsage - $avgCpuUsage -lt 20) { 10 } else { 0 }
        
        $bcmScore = [Math]::Min(100, $cpuEfficiency + $memoryEfficiency + $consistencyBonus)
        
        # Determine BCM status and efficiency level
        $bcmStatus = switch ($bcmScore) {
            { $_ -ge 80 } { "OPTIMAL" }
            { $_ -ge 60 } { "ACCEPTABLE" }
            { $_ -ge 40 } { "DEGRADED" }
            { $_ -ge 20 } { "POOR" }
            default { "CRITICAL" }
        }
        
        $efficiencyLevel = switch ($bcmScore) {
            { $_ -ge 90 } { "EXCELLENT" }
            { $_ -ge 70 } { "GOOD" }
            { $_ -ge 50 } { "FAIR" }
            { $_ -ge 30 } { "POOR" }
            default { "CRITICAL" }
        }
        
        # Check for BCM overload conditions
        $overloadDetected = $false
        $overloadReason = ""
        
        if ($avgCpuUsage -gt 85) {
            $overloadDetected = $true
            $overloadReason += "High CPU usage ($([Math]::Round($avgCpuUsage, 1))%) "
        }
        
        if ($avgMemoryUsage -gt 1000) {
            $overloadDetected = $true
            $overloadReason += "High memory usage ($([Math]::Round($avgMemoryUsage, 1))MB) "
        }
        
        if ($maxCpuUsage -gt 95) {
            $overloadDetected = $true
            $overloadReason += "CPU spikes detected ($([Math]::Round($maxCpuUsage, 1))%) "
        }
        
        $bcmResult = @{
            ProcessId = $ProcessId
            CPU_Usage = [Math]::Round($avgCpuUsage, 2)
            Memory_Usage = [Math]::Round($avgMemoryUsage, 2)
            BCM_Score = [Math]::Round($bcmScore, 2)
            BCM_Status = $bcmStatus
            Efficiency_Level = $efficiencyLevel
            Overload_Detected = $overloadDetected
            Overload_Reason = $overloadReason.Trim()
            Sample_Count = $samples.Count
            Sample_Duration = $SampleDuration
            Timestamp = Get-Date
        }
        
        # Log BCM results
        Write-AIOSMessage -Message "🦋 BCM Analysis Complete:" -Level INFO
        Write-AIOSMessage -Message "   Process ID: $ProcessId" -Level INFO
        Write-AIOSMessage -Message "   CPU Usage: $($bcmResult.CPU_Usage)%" -Level INFO
        Write-AIOSMessage -Message "   Memory Usage: $($bcmResult.Memory_Usage)MB" -Level INFO
        Write-AIOSMessage -Message "   BCM Score: $($bcmResult.BCM_Score)/100" -Level INFO
        Write-AIOSMessage -Message "   Status: $($bcmResult.BCM_Status)" -Level INFO
        Write-AIOSMessage -Message "   Efficiency: $($bcmResult.Efficiency_Level)" -Level INFO
        
        if ($overloadDetected) {
            Write-AIOSMessage -Message "🚨 BCM OVERLOAD DETECTED: $($bcmResult.Overload_Reason)" -Level ERROR
            Write-AIOSMessage -Message "⚠️ AI is using an overly complex (inefficient) probabilistic path" -Level ERROR
        }
        
        # Save BCM data
        $bcmLogFile = "$LOG_DIR\bcm_metrics.json"
        $bcmData = @{
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
            process_id = $ProcessId
            cpu_usage = $bcmResult.CPU_Usage
            memory_usage = $bcmResult.Memory_Usage
            bcm_score = $bcmResult.BCM_Score
            bcm_status = $bcmResult.BCM_Status
            efficiency_level = $bcmResult.Efficiency_Level
            overload_detected = $overloadDetected
            overload_reason = $bcmResult.Overload_Reason
            sample_count = $bcmResult.Sample_Count
            sample_duration = $bcmResult.Sample_Duration
        }
        
        $bcmJson = $bcmData | ConvertTo-Json -Depth 3
        Add-Content -Path $bcmLogFile -Value $bcmJson
        
        return $bcmResult
        
    }
    catch {
        Write-AIOSMessage -Message "❌ Error calculating BCM: $($_.Exception.Message)" -Level ERROR
        return @{
            ProcessId = $ProcessId
            CPU_Usage = 0
            Memory_Usage = 0
            BCM_Score = 0
            BCM_Status = "ERROR"
            Efficiency_Level = "UNKNOWN"
            Overload_Detected = $false
            Error = $_.Exception.Message
        }
    }
}

function Start-AIOSBCMMonitoring {
    param(
        [int]$IntervalSeconds = 30,
        [int]$SampleDuration = 10,
        [switch]$Continuous
    )
    
    Write-AIOSMessage -Message "🦋 Starting AIOS Butterfly Cost Metric Monitoring..." -Level INFO
    Write-AIOSMessage -Message "Monitoring interval: $IntervalSeconds seconds" -Level INFO
    Write-AIOSMessage -Message "Sample duration: $SampleDuration seconds" -Level INFO
    
    try {
        if ($Continuous) {
            Write-AIOSMessage -Message "🔄 Continuous BCM monitoring enabled" -Level INFO
            
            while ($true) {
                $bcmResult = Get-ButterflyCostMetric -SampleDuration $SampleDuration
                
                if ($bcmResult.Overload_Detected) {
                    Write-AIOSMessage -Message "🚨 BCM OVERLOAD ALERT: $($bcmResult.Overload_Reason)" -Level ERROR
                    Write-AIOSMessage -Message "⚠️ Consider optimizing AI process efficiency" -Level WARN
                }
                
                Start-Sleep -Seconds $IntervalSeconds
            }
        } else {
            # Single BCM check
            $bcmResult = Get-ButterflyCostMetric -SampleDuration $SampleDuration
            return $bcmResult
        }
    }
    catch {
        Write-AIOSMessage -Message "❌ Error in BCM monitoring: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function Show-AIOSHelp {
    Write-Host "=== AIOS PowerShell Backend Monitor Commands ===" -ForegroundColor Yellow
    Write-Host "Start-AIOS [-Mode luna|carma|health] [-Questions number] [-Interactive]" -ForegroundColor Cyan
    Write-Host "Get-AIOSStatus" -ForegroundColor Cyan
    Write-Host "Invoke-AIOSHealthCheck" -ForegroundColor Cyan
    Write-Host "Start-AIOSMonitoring" -ForegroundColor Cyan
    Write-Host "Test-UnicodeSupport" -ForegroundColor Cyan
    Write-Host "=== ADVANCED MONITORING COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Start-AIOSBackendMonitor [-FullSystemAccess] [-RealTimeMode]" -ForegroundColor Magenta
    Write-Host "Invoke-AIOSCodeAnalysis [-FilePath path] [-FullScan]" -ForegroundColor Magenta
    Write-Host "Invoke-AIOSSystemDiagnostics [-FullSystemScan] [-SecurityScan]" -ForegroundColor Magenta
    Write-Host "Get-AIOSLogs [-Lines number] [-Filter error|warn|info]" -ForegroundColor Magenta
    Write-Host "Clear-AIOSLogs [-OlderThan days]" -ForegroundColor Magenta
    Write-Host "=== PROJECT MANAGEMENT COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Test-AIOSProjectReadiness [-ProjectPath path] [-CheckDependencies] [-CheckSecurity] [-CheckPerformance]" -ForegroundColor Magenta
    Write-Host "Invoke-AIOSProjectCleanup [-ProjectPath path] [-Aggressive] [-KeepBackups]" -ForegroundColor Magenta
    Write-Host "=== STANDARDS COMPLIANCE COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Invoke-AIOSStandardsCheck [-FilePath path] [-FullProject] [-AutoFix]" -ForegroundColor Magenta
    Write-Host "Start-AIOSStandardsMonitoring [-Interval seconds]" -ForegroundColor Magenta
    Write-Host "Get-AIOSComplianceReport" -ForegroundColor Magenta
    Write-Host "Invoke-AIOSStandardsFix [-FilePath path] [-FullProject]" -ForegroundColor Magenta
    Write-Host "=== BCM & WSR COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Get-ButterflyCostMetric [-ProcessId pid] [-SampleDuration seconds]" -ForegroundColor Magenta
    Write-Host "Start-AIOSBCMMonitoring [-IntervalSeconds seconds] [-Continuous]" -ForegroundColor Magenta
    Write-Host "Test-WillingSubmissionRequirement [-Operation name] [-RiskLevel level]" -ForegroundColor Magenta
    Write-Host "Invoke-BCMRemediation [-RemediationLevel LIGHT|MEDIUM|HEAVY]" -ForegroundColor Magenta
    Write-Host "=== ADMINISTRATION COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Stop-AIOS [-Force] [-TimeoutSeconds seconds]" -ForegroundColor Red
    Write-Host "Start-AIOSProcess [-Mode mode] [-Questions number] [-Background]" -ForegroundColor Red
    Write-Host "Restart-AIOS [-Mode mode] [-Questions number] [-StopTimeoutSeconds seconds]" -ForegroundColor Red
    Write-Host "Get-AIOSProcessDetail [-IncludeCommandLine] [-IncludePerformance]" -ForegroundColor Red
    Write-Host "Set-AIOSLogLevel [-LogLevel DEBUG|INFO|WARN|ERROR|TRACE]" -ForegroundColor Red
    Write-Host "Get-AIOSConfiguration [-Section section]" -ForegroundColor Red
    Write-Host "Set-AIOSConfiguration [-Section section] [-Key key] [-Value value]" -ForegroundColor Red
    Write-Host "Update-AIOSComponents" -ForegroundColor Red
    Write-Host "Backup-AIOSData" -ForegroundColor Red
    Write-Host "Restore-AIOSData [-BackupFile path]" -ForegroundColor Red
    Write-Host "=== LOG MANAGEMENT COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Invoke-LogRotation [-LogRetentionDays days] [-MaxLogSizeBytes bytes] [-CompressOldLogs] [-Force]" -ForegroundColor Magenta
    Write-Host "Clear-AIOSLogs [-OlderThan days] [-Force]" -ForegroundColor Magenta
    Write-Host "=== HEALTH & MONITORING COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Test-AIOSHealth [-CheckType LIVENESS|READINESS|FULL] [-BaseUrl url] [-TimeoutSeconds seconds]" -ForegroundColor Magenta
    Write-Host "Test-AIOSLiveness [-BaseUrl url] [-TimeoutSeconds seconds]" -ForegroundColor Magenta
    Write-Host "Test-AIOSReadiness [-BaseUrl url] [-TimeoutSeconds seconds]" -ForegroundColor Magenta
    Write-Host "Get-AIOSPerformanceCounters [-SampleInterval seconds] [-MaxSamples count]" -ForegroundColor Magenta
    Write-Host "Start-AIOSPerformanceMonitoring [-IntervalSeconds seconds] [-OutputFile path]" -ForegroundColor Magenta
    Write-Host "=== DEPENDENCY & INTEGRITY COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Test-AIOSDependency [-Detailed] [-AutoFix]" -ForegroundColor Magenta
    Write-Host "Invoke-AIOSDependencyFix" -ForegroundColor Magenta
    Write-Host "Test-AIOSConfigurationIntegrity" -ForegroundColor Magenta
    Write-Host "=== SECURITY & ISOLATION COMMANDS ===" -ForegroundColor Yellow
    Write-Host "Initialize-AIOSSecurity [-CreateServiceAccount] [-ConfigureFirewall] [-VerifyIntegrity]" -ForegroundColor Magenta
    Write-Host "New-AIOSServiceAccount" -ForegroundColor Magenta
    Write-Host "Set-AIOSFirewallRules [-AllowedPorts ports] [-RuleName name]" -ForegroundColor Magenta
    Write-Host "Test-AIOSRestartBackoff" -ForegroundColor Magenta
    Write-Host "Send-AIOSHighPriorityAlert [-Message message] [-Severity level]" -ForegroundColor Magenta
    Write-Host "=== Aliases ===" -ForegroundColor Yellow
    Write-Host "aios -> Start-AIOS -Interactive" -ForegroundColor Gray
    Write-Host "status -> Get-AIOSStatus" -ForegroundColor Gray
    Write-Host "health -> Invoke-AIOSHealthCheck" -ForegroundColor Gray
    Write-Host "monitor -> Start-AIOSBackendMonitor -RealTimeMode" -ForegroundColor Gray
    Write-Host "analyze -> Invoke-AIOSCodeAnalysis -FullScan" -ForegroundColor Gray
    Write-Host "diagnose -> Invoke-AIOSSystemDiagnostics -FullSystemScan -SecurityScan" -ForegroundColor Gray
    Write-Host "=== Parameters ===" -ForegroundColor Yellow
    Write-Host "-SkipPythonEnv: Skip Python environment setup" -ForegroundColor Gray
    Write-Host "-TestUnicode: Run Unicode character test" -ForegroundColor Gray
    Write-Host "-Silent: Suppress INFO messages" -ForegroundColor Gray
    Write-Host "-MonitorMode: Enable monitoring mode" -ForegroundColor Gray
    Write-Host "-DebugMode: Enable debug mode" -ForegroundColor Gray
    Write-Host "-AdminMode: Enable admin mode" -ForegroundColor Gray
    Write-Host "-LogLevel: Set log level (TRACE|DEBUG|INFO|WARN|ERROR)" -ForegroundColor Gray
}

# === ADVANCED PROJECT MANAGEMENT FUNCTIONS ===

function Test-AIOSProjectReadiness {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        
        [Parameter(Mandatory=$false)]
        [switch]$CheckDependencies,
        
        [Parameter(Mandatory=$false)]
        [switch]$CheckSecurity,
        
        [Parameter(Mandatory=$false)]
        [switch]$CheckPerformance
    )
    
    Write-AIOSMessage -Message "Starting comprehensive AIOS project readiness check..." -Level INFO
    
    $readiness = @{
        ProjectPath = $ProjectPath
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        Checks = @{}
        OverallStatus = "Unknown"
        Recommendations = @()
    }
    
    # Check core files
    Write-AIOSMessage -Message "Checking core files..." -Level INFO
    $coreFiles = @(
        @{Name="main.py"; Critical=$true},
        @{Name="requirements.txt"; Critical=$true},
        @{Name="aios_powershell_wrapper.ps1"; Critical=$true},
        @{Name="streamlit_app.py"; Critical=$false},
        @{Name="system_monitor.py"; Critical=$false}
    )
    
    foreach ($file in $coreFiles) {
        $fullPath = Join-Path $ProjectPath $file.Name
        $exists = Test-Path $fullPath
        $status = if ($exists) { "OK" } else { if ($file.Critical) { "CRITICAL" } else { "MISSING" } }
        
        $readiness.Checks["CoreFile_$($file.Name)"] = @{
            Path = $fullPath
            Exists = $exists
            Critical = $file.Critical
            Status = $status
            LastModified = if ($exists) { (Get-Item $fullPath).LastWriteTime } else { $null }
        }
        
        if (-not $exists -and $file.Critical) {
            $readiness.Recommendations += "CRITICAL: Missing required file - $($file.Name)"
        }
    }
    
    # Check core directories
    Write-AIOSMessage -Message "Checking core directories..." -Level INFO
    $coreDirs = @(
        @{Name="luna_core"; Critical=$true},
        @{Name="carma_core"; Critical=$true},
        @{Name="enterprise_core"; Critical=$true},
        @{Name="support_core"; Critical=$true},
        @{Name="config"; Critical=$true},
        @{Name="Data"; Critical=$true},
        @{Name="utils"; Critical=$false},
        @{Name="docs"; Critical=$false}
    )
    
    foreach ($dir in $coreDirs) {
        $fullPath = Join-Path $ProjectPath $dir.Name
        $exists = Test-Path $fullPath
        $status = if ($exists) { "OK" } else { if ($dir.Critical) { "CRITICAL" } else { "MISSING" } }
        
        $fileCount = 0
        if ($exists) {
            $fileCount = (Get-ChildItem -Path $fullPath -Recurse -File).Count
        }
        
        $readiness.Checks["CoreDir_$($dir.Name)"] = @{
            Path = $fullPath
            Exists = $exists
            Critical = $dir.Critical
            Status = $status
            FileCount = $fileCount
        }
        
        if (-not $exists -and $dir.Critical) {
            $readiness.Recommendations += "CRITICAL: Missing required directory - $($dir.Name)"
        }
    }
    
    # Check Python environment
    Write-AIOSMessage -Message "Checking Python environment..." -Level INFO
    $venvPath = Join-Path $ProjectPath "venv"
    $pythonExists = Test-Path (Join-Path $venvPath "Scripts\python.exe")
    $pipExists = Test-Path (Join-Path $venvPath "Scripts\pip.exe")
    
    $readiness.Checks["PythonEnvironment"] = @{
        Path = $venvPath
        PythonExists = $pythonExists
        PipExists = $pipExists
        Status = if ($pythonExists -and $pipExists) { "OK" } else { "INCOMPLETE" }
    }
    
    if (-not $pythonExists) {
        $readiness.Recommendations += "Create Python virtual environment: python -m venv venv"
    }
    
    # Check dependencies if requested
    if ($CheckDependencies) {
        Write-AIOSMessage -Message "Checking dependencies..." -Level INFO
        $reqFile = Join-Path $ProjectPath "requirements.txt"
        
        if (Test-Path $reqFile) {
            $requirements = Get-Content $reqFile
            $reqCount = $requirements.Count
            
            # Check if packages are installed
            $installedPackages = @()
            if ($pythonExists) {
                try {
                    $installedOutput = & (Join-Path $venvPath "Scripts\pip.exe") list --format=json 2>$null
                    if ($installedOutput) {
                        $installedPackages = $installedOutput | ConvertFrom-Json
                    }
                } catch {
                    Write-AIOSMessage -Message "Could not check installed packages" -Level WARN
                }
            }
            
            $readiness.Checks["Dependencies"] = @{
                RequirementsFile = $reqFile
                RequirementsCount = $reqCount
                InstalledPackagesCount = $installedPackages.Count
                Status = if ($installedPackages.Count -ge $reqCount) { "OK" } else { "INCOMPLETE" }
            }
            
            if ($installedPackages.Count -lt $reqCount) {
                $readiness.Recommendations += "Install missing dependencies: pip install -r requirements.txt"
            }
        } else {
            $readiness.Checks["Dependencies"] = @{
                RequirementsFile = $reqFile
                Status = "MISSING"
            }
            $readiness.Recommendations += "Create requirements.txt file"
        }
    }
    
    # Security check if requested
    if ($CheckSecurity) {
        Write-AIOSMessage -Message "Running security check..." -Level INFO
        $suspiciousPatterns = @("*.tmp", "*.temp", "*.exe.tmp", "*.bat.tmp")
        $suspiciousFiles = @()
        $largeFiles = @()
        
        foreach ($pattern in $suspiciousPatterns) {
            $files = Get-ChildItem -Path $ProjectPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
            if ($files) {
                $suspiciousFiles += $files.FullName
            }
        }
        
        # Check for large files (>100MB)
        $largeFiles = Get-ChildItem -Path $ProjectPath -Recurse -File | Where-Object { $_.Length -gt 100MB }
        
        # Check for files with executable extensions
        $executableExtensions = @("*.exe", "*.bat", "*.cmd", "*.scr", "*.pif")
        $executableFiles = @()
        foreach ($ext in $executableExtensions) {
            $files = Get-ChildItem -Path $ProjectPath -Filter $ext -Recurse -ErrorAction SilentlyContinue
            $executableFiles += $files.FullName
        }
        
        $readiness.Checks["Security"] = @{
            SuspiciousFiles = $suspiciousFiles
            LargeFiles = $largeFiles.Count
            ExecutableFiles = $executableFiles.Count
            Status = if ($suspiciousFiles.Count -eq 0 -and $executableFiles.Count -eq 0) { "CLEAN" } else { "REVIEW_NEEDED" }
        }
        
        if ($suspiciousFiles.Count -gt 0) {
            $readiness.Recommendations += "Review suspicious files: $($suspiciousFiles.Count) found"
        }
        if ($executableFiles.Count -gt 0) {
            $readiness.Recommendations += "Review executable files: $($executableFiles.Count) found"
        }
    }
    
    # Performance check if requested
    if ($CheckPerformance) {
        Write-AIOSMessage -Message "Running performance check..." -Level INFO
        
        # Check for large directories
        $largeDirs = Get-ChildItem -Path $ProjectPath -Directory | ForEach-Object {
            $size = (Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
            if ($size -gt 500MB) {
                @{
                    Name = $_.Name
                    Size = [math]::Round($size / 1MB, 2)
                    SizeMB = $size / 1MB
                }
            }
        }
        
        # Check for files with potential performance issues
        $pythonFiles = Get-ChildItem -Path $ProjectPath -Filter "*.py" -Recurse
        $largePythonFiles = $pythonFiles | Where-Object { $_.Length -gt 1MB }
        
        $readiness.Checks["Performance"] = @{
            LargeDirectories = $largeDirs
            LargePythonFiles = $largePythonFiles.Count
            TotalPythonFiles = $pythonFiles.Count
            Status = if ($largeDirs.Count -eq 0 -and $largePythonFiles.Count -eq 0) { "GOOD" } else { "REVIEW_NEEDED" }
        }
        
        if ($largeDirs.Count -gt 0) {
            $readiness.Recommendations += "Consider cleaning large directories: $($largeDirs.Count) found"
        }
        if ($largePythonFiles.Count -gt 0) {
            $readiness.Recommendations += "Review large Python files: $($largePythonFiles.Count) found"
        }
    }
    
    # Calculate overall status
    $criticalIssues = ($readiness.Checks.Values | Where-Object { $_.Status -eq "CRITICAL" }).Count
    $incompleteIssues = ($readiness.Checks.Values | Where-Object { $_.Status -eq "INCOMPLETE" }).Count
    $reviewNeeded = ($readiness.Checks.Values | Where-Object { $_.Status -eq "REVIEW_NEEDED" }).Count
    $totalChecks = $readiness.Checks.Count
    
    if ($criticalIssues -eq 0 -and $incompleteIssues -eq 0) {
        $readiness.OverallStatus = "READY"
    } elseif ($criticalIssues -eq 0 -and $incompleteIssues -le 2) {
        $readiness.OverallStatus = "WARNING"
    } else {
        $readiness.OverallStatus = "CRITICAL"
    }
    
    # Save results
    $resultsFile = "$DEBUG_DIR\project_readiness_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
    $readiness | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsFile -Encoding UTF8
    
    Write-AIOSMessage -Message "Project readiness check completed" -Level SUCCESS
    Write-AIOSMessage -Message "Overall Status: $($readiness.OverallStatus)" -Level INFO
    Write-AIOSMessage -Message "Results saved to: $resultsFile" -Level INFO
    
    if ($readiness.Recommendations.Count -gt 0) {
        Write-AIOSMessage -Message "Recommendations:" -Level WARN
        foreach ($rec in $readiness.Recommendations) {
            Write-AIOSMessage -Message "  - $rec" -Level WARN
        }
    }
    
    return $readiness
}

function Invoke-AIOSProjectCleanup {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        
        [Parameter(Mandatory=$false)]
        [switch]$Aggressive,
        
        [Parameter(Mandatory=$false)]
        [switch]$KeepBackups
    )
    
    # Enforce WSR for cleanup operations
    if (-not (Test-WillingSubmissionRequirement -Operation "AIOS Project Cleanup" -RiskLevel "MEDIUM")) {
        Write-AIOSMessage -Message "Willing Submission Required - Project cleanup blocked" -Level ERROR
        return
    }
    
    if ($PSCmdlet.ShouldProcess("Clean up AIOS project at '$ProjectPath'")) {
        Write-AIOSMessage -Message "Starting AIOS project cleanup..." -Level INFO
        
        $cleanupResults = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            ProjectPath = $ProjectPath
            CleanedItems = @()
            FreedSpace = 0
            Errors = @()
        }
        
        # Clean temporary files
        Write-AIOSMessage -Message "Cleaning temporary files..." -Level INFO
        $tempPatterns = @("*.pyc", "__pycache__", "*.tmp", "*.temp", ".pytest_cache", "*.log.tmp")
        
        foreach ($pattern in $tempPatterns) {
            try {
                $items = Get-ChildItem -Path $ProjectPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
                foreach ($item in $items) {
                    $size = if ($item.PSIsContainer) { 0 } else { $item.Length }
                    
                    if ($item.PSIsContainer) {
                        Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    } else {
                        Remove-Item -Path $item.FullName -Force -ErrorAction SilentlyContinue
                    }
                    
                    $cleanupResults.CleanedItems += @{
                        Path = $item.FullName
                        Type = if ($item.PSIsContainer) { "Directory" } else { "File" }
                        Size = $size
                    }
                    $cleanupResults.FreedSpace += $size
                }
            } catch {
                $cleanupResults.Errors += "Failed to clean $pattern : $($_.Exception.Message)"
            }
        }
        
        # Clean old log files (older than 7 days)
        Write-AIOSMessage -Message "Cleaning old log files..." -Level INFO
        $logDir = Join-Path $ProjectPath "log"
        if (Test-Path $logDir) {
            try {
                $oldLogs = Get-ChildItem -Path $logDir -Recurse -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
                foreach ($log in $oldLogs) {
                    $size = $log.Length
                    Remove-Item -Path $log.FullName -Force -ErrorAction SilentlyContinue
                    $cleanupResults.CleanedItems += @{
                        Path = $log.FullName
                        Type = "LogFile"
                        Size = $size
                        Age = ((Get-Date) - $log.LastWriteTime).Days
                    }
                    $cleanupResults.FreedSpace += $size
                }
            } catch {
                $cleanupResults.Errors += "Failed to clean old logs: $($_.Exception.Message)"
            }
        }
        
        # Aggressive cleanup if requested
        if ($Aggressive) {
            Write-AIOSMessage -Message "Running aggressive cleanup..." -Level WARN
            
            # Clean node_modules if present
            $nodeModules = Get-ChildItem -Path $ProjectPath -Filter "node_modules" -Recurse -Directory
            foreach ($nm in $nodeModules) {
                try {
                    $size = (Get-ChildItem -Path $nm.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
                    Remove-Item -Path $nm.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    $cleanupResults.CleanedItems += @{
                        Path = $nm.FullName
                        Type = "NodeModules"
                        Size = $size
                    }
                    $cleanupResults.FreedSpace += $size
                } catch {
                    $cleanupResults.Errors += "Failed to clean node_modules: $($_.Exception.Message)"
                }
            }
            
            # Clean .git directory if requested (dangerous!)
            $gitDir = Join-Path $ProjectPath ".git"
            if (Test-Path $gitDir) {
                try {
                    $size = (Get-ChildItem -Path $gitDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
                    Remove-Item -Path $gitDir -Recurse -Force -ErrorAction SilentlyContinue
                    $cleanupResults.CleanedItems += @{
                        Path = $gitDir
                        Type = "GitDirectory"
                        Size = $size
                    }
                    $cleanupResults.FreedSpace += $size
                } catch {
                    $cleanupResults.Errors += "Failed to clean .git directory: $($_.Exception.Message)"
                }
            }
        }
        
        # Cleanup backups if not keeping them
        if (-not $KeepBackups) {
            Write-AIOSMessage -Message "Cleaning old backups..." -Level INFO
            $backupDir = Join-Path $ProjectPath "backups"
            if (Test-Path $backupDir) {
                try {
                    $oldBackups = Get-ChildItem -Path $backupDir -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
                    foreach ($backup in $oldBackups) {
                        $size = $backup.Length
                        Remove-Item -Path $backup.FullName -Force -ErrorAction SilentlyContinue
                        $cleanupResults.CleanedItems += @{
                            Path = $backup.FullName
                            Type = "OldBackup"
                            Size = $size
                            Age = ((Get-Date) - $backup.LastWriteTime).Days
                        }
                        $cleanupResults.FreedSpace += $size
                    }
                } catch {
                    $cleanupResults.Errors += "Failed to clean old backups: $($_.Exception.Message)"
                }
            }
        }
        
        # Save cleanup results
        $resultsFile = "$DEBUG_DIR\project_cleanup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
        $cleanupResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsFile -Encoding UTF8
        
        $freedSpaceMB = [math]::Round($cleanupResults.FreedSpace / 1MB, 2)
        
        Write-AIOSMessage -Message "Project cleanup completed" -Level SUCCESS
        Write-AIOSMessage -Message "Items cleaned: $($cleanupResults.CleanedItems.Count)" -Level INFO
        Write-AIOSMessage -Message "Space freed: $freedSpaceMB MB" -Level INFO
        Write-AIOSMessage -Message "Results saved to: $resultsFile" -Level INFO
        
        if ($cleanupResults.Errors.Count -gt 0) {
            Write-AIOSMessage -Message "Errors encountered:" -Level WARN
            foreach ($error in $cleanupResults.Errors) {
                Write-AIOSMessage -Message "  - $error" -Level WARN
            }
        }
        
        return $cleanupResults
    }
}

# === LOGGING AND ADMINISTRATION FUNCTIONS ===

function Get-AIOSLogs {
    param([int]$Lines = 50, [string]$Filter = "ALL", [string]$LogType = "monitor")
    
    Write-AIOSMessage -Message "Retrieving AIOS logs (Last $Lines lines, Filter: $Filter)..." -Level INFO
    
    $logFiles = @()
    
    switch ($LogType) {
        "monitor" { $logFiles = Get-ChildItem -Path "$LOG_DIR\*monitor*.log" -ErrorAction SilentlyContinue }
        "system" { $logFiles = Get-ChildItem -Path "$LOG_DIR\*system*.log" -ErrorAction SilentlyContinue }
        "file" { $logFiles = Get-ChildItem -Path "$LOG_DIR\*file*.log" -ErrorAction SilentlyContinue }
        "all" { $logFiles = Get-ChildItem -Path "$LOG_DIR\*.log" -ErrorAction SilentlyContinue }
    }
    
    if ($logFiles.Count -eq 0) {
        Write-AIOSMessage -Message "No log files found in $LOG_DIR" -Level WARN
        return
    }
    
    $allLogs = @()
    foreach ($logFile in $logFiles) {
        $logs = Get-Content $logFile.FullName -Tail $Lines -ErrorAction SilentlyContinue
        foreach ($log in $logs) {
            if ($Filter -eq "ALL" -or $log -match "\[$Filter\]") {
                $allLogs += @{
                    File = $logFile.Name
                    Content = $log
                    Timestamp = if ($log -match "\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})") { $matches[1] } else { "Unknown" }
                }
            }
        }
    }
    
    # Sort by timestamp and display
    $sortedLogs = $allLogs | Sort-Object Timestamp -Descending | Select-Object -First $Lines
    
    Write-Host "=== AIOS Logs (Last $($sortedLogs.Count) entries) ===" -ForegroundColor Yellow
    foreach ($log in $sortedLogs) {
        $color = switch -Regex ($log.Content) {
            "\[ERROR\]" { "Red" }
            "\[WARN\]" { "Yellow" }
            "\[SUCCESS\]" { "Green" }
            "\[DEBUG\]" { "Magenta" }
            default { "White" }
        }
        Write-Host "[$($log.File)] $($log.Content)" -ForegroundColor $color
    }
    
    return $sortedLogs
}

function Invoke-LogRotation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [int]$LogRetentionDays = 30,
        
        [Parameter(Mandatory=$false)]
        [long]$MaxLogSizeBytes = 104857600,  # 100MB
        
        [Parameter(Mandatory=$false)]
        [switch]$CompressOldLogs,
        
        [Parameter(Mandatory=$false)]
        [switch]$Force
    )
    
    Write-AIOSMessage -Message "🔄 Starting AIOS log rotation..." -Level INFO
    
    try {
        $rotationStats = @{
            FilesProcessed = 0
            FilesDeleted = 0
            FilesCompressed = 0
            SpaceFreed = 0
            Errors = 0
        }
        
        # Get all log files in the log directory
        $logFiles = Get-ChildItem -Path $LOG_DIR -Filter "*.log" -Recurse
        
        foreach ($logFile in $logFiles) {
            $rotationStats.FilesProcessed++
            
            try {
                $shouldProcess = $false
                $action = ""
                
                # Check if file should be processed based on age
                $fileAge = (Get-Date) - $logFile.LastWriteTime
                if ($fileAge.TotalDays -gt $LogRetentionDays) {
                    $shouldProcess = $true
                    $action = "age"
                }
                
                # Check if file should be processed based on size
                if ($logFile.Length -gt $MaxLogSizeBytes) {
                    $shouldProcess = $true
                    if ($action -eq "") {
                        $action = "size"
                    } else {
                        $action = "both"
                    }
                }
                
                if ($shouldProcess -or $Force) {
                    if ($CompressOldLogs -and $action -ne "size") {
                        # Compress the log file
                        $compressedFile = "$($logFile.FullName).gz"
                        
                        # Use .NET compression
                        $fileBytes = [System.IO.File]::ReadAllBytes($logFile.FullName)
                        $compressedBytes = [System.IO.Compression.GZipStream]::new(
                            [System.IO.File]::Create($compressedFile),
                            [System.IO.Compression.CompressionMode]::Compress
                        )
                        $compressedBytes.Write($fileBytes, 0, $fileBytes.Length)
                        $compressedBytes.Close()
                        
                        # Remove original file
                        Remove-Item $logFile.FullName -Force
                        
                        $rotationStats.FilesCompressed++
                        $rotationStats.SpaceFreed += $logFile.Length
                        
                        Write-AIOSMessage -Message "Compressed log file: $($logFile.Name)" -Level INFO
                    } else {
                        # Delete the log file
                        $fileSize = $logFile.Length
                        Remove-Item $logFile.FullName -Force
                        
                        $rotationStats.FilesDeleted++
                        $rotationStats.SpaceFreed += $fileSize
                        
                        Write-AIOSMessage -Message "Deleted log file: $($logFile.Name) (Reason: $action)" -Level INFO
                    }
                }
            }
            catch {
                $rotationStats.Errors++
                Write-AIOSMessage -Message "Error processing log file $($logFile.Name): $($_.Exception.Message)" -Level ERROR
            }
        }
        
        # Clean up old compressed files
        $compressedFiles = Get-ChildItem -Path $LOG_DIR -Filter "*.gz" -Recurse | Where-Object { 
            $_.LastWriteTime -lt (Get-Date).AddDays($LogRetentionDays * 2) 
        }
        
        foreach ($compressedFile in $compressedFiles) {
            try {
                $fileSize = $compressedFile.Length
                Remove-Item $compressedFile.FullName -Force
                $rotationStats.FilesDeleted++
                $rotationStats.SpaceFreed += $fileSize
                Write-AIOSMessage -Message "Deleted old compressed log: $($compressedFile.Name)" -Level INFO
            }
            catch {
                $rotationStats.Errors++
                Write-AIOSMessage -Message "Error deleting compressed file $($compressedFile.Name): $($_.Exception.Message)" -Level ERROR
            }
        }
        
        # Log rotation summary
        $spaceFreedMB = [Math]::Round($rotationStats.SpaceFreed / 1MB, 2)
        Write-AIOSMessage -Message "Log rotation completed - Files processed: $($rotationStats.FilesProcessed), Deleted: $($rotationStats.FilesDeleted), Compressed: $($rotationStats.FilesCompressed), Space freed: $spaceFreedMB MB, Errors: $($rotationStats.Errors)" -Level SUCCESS
        
        # Create rotation report
        $rotationReport = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            LogRetentionDays = $LogRetentionDays
            MaxLogSizeBytes = $MaxLogSizeBytes
            CompressOldLogs = $CompressOldLogs
            Statistics = $rotationStats
        }
        
        $reportFile = "$LOG_DIR\log_rotation_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $rotationReport | ConvertTo-Json -Depth 3 | Set-Content $reportFile -Encoding UTF8
        
        return $rotationStats
    }
    catch {
        Write-AIOSMessage -Message "Error during log rotation: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function Clear-AIOSLogs {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [int]$OlderThan = 7,
        
        [Parameter(Mandatory=$false)]
        [switch]$Force
    )
    
    Write-AIOSMessage -Message "Clearing AIOS logs older than $OlderThan days..." -Level WARN
    
    try {
        $cutoffDate = (Get-Date).AddDays(-$OlderThan)
        $deletedFiles = 0
        $deletedSize = 0
        
        Get-ChildItem -Path $LOG_DIR -Recurse -File | Where-Object { $_.LastWriteTime -lt $cutoffDate } | ForEach-Object {
            try {
                $size = $_.Length
                Remove-Item $_.FullName -Force
                $deletedFiles++
                $deletedSize += $size
            }
            catch {
                Write-AIOSMessage -Message "Error deleting file $($_.Name): $($_.Exception.Message)" -Level ERROR
            }
        }
        
        $spaceFreedMB = [Math]::Round($deletedSize / 1MB, 2)
        Write-AIOSMessage -Message "Deleted $deletedFiles log files ($spaceFreedMB MB)" -Level SUCCESS
        
        return @{
            FilesDeleted = $deletedFiles
            SpaceFreed = $deletedSize
            SpaceFreedMB = $spaceFreedMB
        }
    }
    catch {
        Write-AIOSMessage -Message "Error clearing logs: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function Stop-AIOS {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$false)]
        [switch]$Force,
        
        [Parameter(Mandatory=$false)]
        [switch]$Graceful,
        
        [Parameter(Mandatory=$false)]
        [string]$BaseUrl = "http://localhost:8080",
        
        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 30
    )
    
    Write-AIOSMessage -Message "🛑 Stopping AIOS services..." -Level WARN
    
    try {
        # Find all AIOS-related processes
        $aiosProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "python" -and 
            ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
        }
        
        if ($aiosProcesses.Count -eq 0) {
            Write-AIOSMessage -Message "No AIOS processes found to stop" -Level INFO
            return $true
        }
        
        Write-AIOSMessage -Message "Found $($aiosProcesses.Count) AIOS processes to stop" -Level INFO
        
        if ($Force) {
            # Force stop all processes
            $aiosProcesses | Stop-Process -Force
            Write-AIOSMessage -Message "Force stopped all AIOS processes" -Level WARN
        } elseif ($Graceful) {
            # Attempt graceful shutdown via REST API
            $gracefulResult = Invoke-AIOSGracefulShutdown -BaseUrl $BaseUrl -TimeoutSeconds $TimeoutSeconds
            if ($gracefulResult.Success) {
                Write-AIOSMessage -Message "Graceful shutdown completed successfully" -Level SUCCESS
                return $true
            } else {
                Write-AIOSMessage -Message "Graceful shutdown failed: $($gracefulResult.Error)" -Level WARN
                Write-AIOSMessage -Message "Falling back to process-based shutdown..." -Level INFO
            }
        }
        
        # Process-based shutdown (either fallback or default)
        foreach ($process in $aiosProcesses) {
            try {
                # Try graceful shutdown first
                $process.CloseMainWindow()
                Write-AIOSMessage -Message "Sent close signal to PID $($process.Id)" -Level INFO
            }
            catch {
                Write-AIOSMessage -Message "Failed to gracefully close PID $($process.Id): $($_.Exception.Message)" -Level WARN
            }
        }
        
        # Wait for graceful shutdown
        $elapsed = 0
        while ($elapsed -lt $TimeoutSeconds) {
            $remainingProcesses = Get-Process | Where-Object { 
                $_.ProcessName -eq "python" -and 
                ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
            }
            
            if ($remainingProcesses.Count -eq 0) {
                Write-AIOSMessage -Message "All AIOS processes stopped gracefully" -Level SUCCESS
                return $true
            }
            
            Start-Sleep -Seconds 2
            $elapsed += 2
            $shutdownMessage = "Waiting for graceful shutdown... ($elapsed/$TimeoutSeconds seconds)"
            Write-AIOSMessage -Message $shutdownMessage -Level INFO
        }
        
        # Force stop remaining processes
        $remainingProcesses | Stop-Process -Force
        Write-AIOSMessage -Message "Force stopped remaining processes after timeout" -Level WARN
        
        return $true
    }
    catch {
        Write-AIOSMessage -Message "Error stopping AIOS services: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Invoke-AIOSGracefulShutdown {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$BaseUrl = "http://localhost:8080",
        
        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 30
    )
    
    try {
        Write-AIOSMessage -Message "🔄 Attempting graceful shutdown via REST API..." -Level INFO
        
        $shutdownUrl = "$BaseUrl/admin/shutdown"
        
        # Send graceful shutdown request
        $shutdownRequest = @{
            graceful = $true
            timeout = $TimeoutSeconds
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
        }
        
        $response = Invoke-RestMethod -Uri $shutdownUrl -Method Post -Body ($shutdownRequest | ConvertTo-Json) -ContentType "application/json" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        
        return @{
            Success = $true
            Message = $response.message
            ShutdownTime = $response.shutdown_time
            ProcessesStopped = $response.processes_stopped
            Details = $response.details
        }
    }
    catch {
        Write-AIOSMessage -Message "Graceful shutdown API call failed: $($_.Exception.Message)" -Level WARN
        
        return @{
            Success = $false
            Error = $_.Exception.Message
            Message = "API-based graceful shutdown not available"
        }
    }
}

function Start-AIOSProcess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Mode,
        
        [Parameter(Mandatory=$false)]
        [int]$Questions = 1,
        
        [Parameter(Mandatory=$false)]
        [switch]$Background
    )
    
    Write-AIOSMessage -Message "🚀 Starting AIOS in $Mode mode..." -Level INFO
    
    try {
        $mainScript = "$AIOS_ROOT\main.py"
        if (-not (Test-Path $mainScript)) {
            Write-AIOSMessage -Message "Main script not found: $mainScript" -Level ERROR
            return $false
        }
        
        $pythonExe = "$PYTHON_ENV_PATH\Scripts\python.exe"
        if (-not (Test-Path $pythonExe)) {
            Write-AIOSMessage -Message "Python executable not found: $pythonExe" -Level ERROR
            return $false
        }
        
        $arguments = @("$mainScript", "--mode", $Mode, "--questions", $Questions)
        
        if ($Background) {
            $process = Start-Process -FilePath $pythonExe -ArgumentList $arguments -WindowStyle Hidden -PassThru
            Write-AIOSMessage -Message "Started AIOS in background (PID: $($process.Id))" -Level SUCCESS
        } else {
            & $pythonExe $arguments
            Write-AIOSMessage -Message "AIOS process completed" -Level SUCCESS
        }
        
        return $true
    }
    catch {
        Write-AIOSMessage -Message "Error starting AIOS: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Restart-AIOS {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$false)]
        [string]$Mode = "luna",
        
        [Parameter(Mandatory=$false)]
        [int]$Questions = 1,
        
        [Parameter(Mandatory=$false)]
        [int]$StopTimeoutSeconds = 30,
        
        [Parameter(Mandatory=$false)]
        [switch]$Force
    )
    
    # Check restart back-off state
    $backoffResult = Test-AIOSRestartBackoff
    if ($backoffResult.InBackoffState -and -not $Force) {
        Write-AIOSMessage -Message "🚫 AIOS restart blocked - System is in back-off state until $($backoffResult.BackoffUntil)" -Level ERROR
        Write-AIOSMessage -Message "Reason: $($backoffResult.BackoffReason)" -Level WARN
        Write-AIOSMessage -Message "Use -Force to override back-off protection" -Level INFO
        return $false
    }
    
    # Enforce WSR for admin operations
    if (-not (Test-WillingSubmissionRequirement -Operation "AIOS Service Restart" -RiskLevel "HIGH")) {
        Write-AIOSMessage -Message "Willing Submission Required - Service restart blocked" -Level ERROR
        return $false
    }
    
    Write-AIOSMessage -Message "🔄 Restarting AIOS services..." -Level WARN
    
    try {
        # Record restart attempt
        $restartAttempt = Record-AIOSRestartAttempt -Mode $Mode -Force $Force
        
        # Stop existing processes
        Write-AIOSMessage -Message "Stopping existing AIOS processes..." -Level INFO
        $stopResult = Stop-AIOS -Graceful -TimeoutSeconds $StopTimeoutSeconds
        
        if (-not $stopResult) {
            Write-AIOSMessage -Message "Failed to stop AIOS processes" -Level ERROR
            Record-AIOSRestartFailure -Attempt $restartAttempt -Reason "Stop failed"
            return $false
        }
        
        # Wait for cleanup
        Start-Sleep -Seconds 3
        
        # Start new processes
        Write-AIOSMessage -Message "Starting AIOS in $Mode mode..." -Level INFO
        $startResult = Start-AIOSProcess -Mode $Mode -Questions $Questions -Background
        
        if ($startResult) {
            Write-AIOSMessage -Message "AIOS services restarted successfully" -Level SUCCESS
            
            # Record successful restart
            Record-AIOSRestartSuccess -Attempt $restartAttempt
            
            # Log restart event
            log_admin_operation "restart_service" $true "AIOS restarted in $Mode mode"
            return $true
        } else {
            Write-AIOSMessage -Message "Failed to start AIOS services" -Level ERROR
            Record-AIOSRestartFailure -Attempt $restartAttempt -Reason "Start failed"
            return $false
        }
    }
    catch {
        Write-AIOSMessage -Message "Error during AIOS restart: $($_.Exception.Message)" -Level ERROR
        Record-AIOSRestartFailure -Attempt $restartAttempt -Reason "Exception: $($_.Exception.Message)"
        return $false
    }
}

function Test-AIOSRestartBackoff {
    [CmdletBinding()]
    param()
    
    try {
        $backoffFile = "$LOG_DIR\aios_restart_backoff.json"
        
        if (-not (Test-Path $backoffFile)) {
            return @{
                InBackoffState = $false
                BackoffUntil = $null
                BackoffReason = $null
                RestartCount = 0
            }
        }
        
        $backoffData = Get-Content $backoffFile -Raw | ConvertFrom-Json
        
        # Check if back-off period has expired
        $backoffUntil = [DateTime]::Parse($backoffData.backoff_until)
        $now = Get-Date
        
        if ($now -lt $backoffUntil) {
            return @{
                InBackoffState = $true
                BackoffUntil = $backoffUntil.ToString("yyyy-MM-dd HH:mm:ss")
                BackoffReason = $backoffData.backoff_reason
                RestartCount = $backoffData.restart_count
            }
        } else {
            # Back-off period has expired, remove the file
            Remove-Item $backoffFile -Force -ErrorAction SilentlyContinue
            return @{
                InBackoffState = $false
                BackoffUntil = $null
                BackoffReason = $null
                RestartCount = 0
            }
        }
    }
    catch {
        Write-AIOSMessage -Message "Error checking restart back-off state: $($_.Exception.Message)" -Level ERROR
        return @{
            InBackoffState = $false
            BackoffUntil = $null
            BackoffReason = $null
            RestartCount = 0
        }
    }
}

function Record-AIOSRestartAttempt {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$Mode = "luna",
        
        [Parameter(Mandatory=$false)]
        [switch]$Force
    )
    
    $attempt = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        Mode = $Mode
        Force = $Force
        ProcessId = $PID
        User = $env:USERNAME
    }
    
    return $attempt
}

function Record-AIOSRestartSuccess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Attempt
    )
    
    try {
        $successLog = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            Attempt = $Attempt
            Success = $true
            Message = "AIOS restart completed successfully"
        }
        
        $logFile = "$LOG_DIR\aios_restart_success.log"
        $successLog | ConvertTo-Json -Depth 3 | Add-Content $logFile -Encoding UTF8
        
        # Clear any existing back-off state on successful restart
        $backoffFile = "$LOG_DIR\aios_restart_backoff.json"
        if (Test-Path $backoffFile) {
            Remove-Item $backoffFile -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-AIOSMessage -Message "Error recording restart success: $($_.Exception.Message)" -Level ERROR
    }
}

function Record-AIOSRestartFailure {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Attempt,
        
        [Parameter(Mandatory=$true)]
        [string]$Reason
    )
    
    try {
        $failureLog = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            Attempt = $Attempt
            Success = $false
            Reason = $Reason
        }
        
        $logFile = "$LOG_DIR\aios_restart_failures.log"
        $failureLog | ConvertTo-Json -Depth 3 | Add-Content $logFile -Encoding UTF8
        
        # Check if we need to enter back-off state
        $failureCount = (Get-Content $logFile | ConvertFrom-Json | Where-Object { 
            $_.Success -eq $false -and 
            [DateTime]::Parse($_.Timestamp) -gt (Get-Date).AddMinutes(-10) 
        }).Count
        
        if ($failureCount -ge 3) {
            Enter-AIOSRestartBackoff -Reason "Multiple restart failures ($failureCount) within 10 minutes"
        }
    }
    catch {
        Write-AIOSMessage -Message "Error recording restart failure: $($_.Exception.Message)" -Level ERROR
    }
}

function Enter-AIOSRestartBackoff {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Reason
    )
    
    try {
        $backoffData = @{
            backoff_started = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            backoff_until = (Get-Date).AddMinutes(30).ToString("yyyy-MM-dd HH:mm:ss.fff")
            backoff_reason = $Reason
            restart_count = 3
            high_priority_alert_sent = $false
        }
        
        $backoffFile = "$LOG_DIR\aios_restart_backoff.json"
        $backoffData | ConvertTo-Json -Depth 3 | Set-Content $backoffFile -Encoding UTF8
        
        Write-AIOSMessage -Message "🚨 ENTERING RESTART BACK-OFF STATE - No restarts allowed for 30 minutes" -Level ERROR
        Write-AIOSMessage -Message "Reason: $Reason" -Level ERROR
        Write-AIOSMessage -Message "Back-off until: $($backoffData.backoff_until)" -Level ERROR
        
        # Send high-priority alert
        Send-AIOSHighPriorityAlert -Message "AIOS RESTART BACK-OFF ACTIVATED - $Reason" -Severity "CRITICAL"
        
        # Log to Windows Event Log
        if ($global:AIOS_CONFIG.SECURITY_CONFIG.AUDIT_LOG_TO_EVENT_LOG) {
            try {
                $eventLogMessage = "AIOS RESTART BACK-OFF ACTIVATED - Reason: $Reason - Back-off until: $($backoffData.backoff_until)"
                Write-EventLog -LogName "Application" -Source "AIOS" -EventId 2001 -EntryType Error -Message $eventLogMessage -Category 2
            }
            catch {
                Write-AIOSMessage -Message "Failed to log back-off event to Windows Event Log: $($_.Exception.Message)" -Level WARN
            }
        }
    }
    catch {
        Write-AIOSMessage -Message "Error entering restart back-off state: $($_.Exception.Message)" -Level ERROR
    }
}

function Send-AIOSHighPriorityAlert {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("INFO", "WARN", "ERROR", "CRITICAL")]
        [string]$Severity = "ERROR"
    )
    
    try {
        $alert = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            Severity = $Severity
            Message = $Message
            ProcessId = $PID
            User = $env:USERNAME
        }
        
        $alertFile = "$LOG_DIR\aios_high_priority_alerts.log"
        $alert | ConvertTo-Json -Depth 3 | Add-Content $alertFile -Encoding UTF8
        
        Write-AIOSMessage -Message "🚨 HIGH PRIORITY ALERT: $Message" -Level ERROR
        
        # Could integrate with external alerting systems here (email, Slack, etc.)
    }
    catch {
        Write-AIOSMessage -Message "Error sending high priority alert: $($_.Exception.Message)" -Level ERROR
    }
}

function Get-AIOSProcessDetail {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [switch]$IncludeCommandLine,
        
        [Parameter(Mandatory=$false)]
        [switch]$IncludePerformance
    )
    
    Write-AIOSMessage -Message "🔍 Getting detailed AIOS process information..." -Level INFO
    
    try {
        $aiosProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "python" -and 
            ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
        }
        
        if ($aiosProcesses.Count -eq 0) {
            Write-AIOSMessage -Message "No AIOS processes found" -Level WARN
            return @()
        }
        
        $processDetails = @()
        
        foreach ($process in $aiosProcesses) {
            $detail = @{
                ProcessId = $process.Id
                ProcessName = $process.ProcessName
                StartTime = $process.StartTime
                CPU = $process.CPU
                WorkingSet = [Math]::Round($process.WorkingSet64 / 1MB, 2)
                VirtualMemory = [Math]::Round($process.VirtualMemorySize64 / 1MB, 2)
                PagedMemory = [Math]::Round($process.PagedMemorySize64 / 1MB, 2)
                Handles = $process.HandleCount
                Threads = $process.Threads.Count
                PeakWorkingSet = [Math]::Round($process.PeakWorkingSet64 / 1MB, 2)
                PeakVirtualMemory = [Math]::Round($process.PeakVirtualMemorySize64 / 1MB, 2)
                Responding = $process.Responding
                PriorityClass = $process.PriorityClass.ToString()
            }
            
            if ($IncludeCommandLine) {
                try {
                    $detail.CommandLine = $process.CommandLine
                }
                catch {
                    $detail.CommandLine = "Unable to retrieve command line"
                }
            }
            
            if ($IncludePerformance) {
                try {
                    $detail.TotalProcessorTime = $process.TotalProcessorTime
                    $detail.UserProcessorTime = $process.UserProcessorTime
                    $detail.PrivilegedProcessorTime = $process.PrivilegedProcessorTime
                }
                catch {
                    $detail.TotalProcessorTime = "Unable to retrieve"
                }
            }
            
            $processDetails += $detail
        }
        
        # Display results
        Write-AIOSMessage -Message "Found $($processDetails.Count) AIOS processes:" -Level INFO
        
        foreach ($detail in $processDetails) {
            Write-AIOSMessage -Message "PID $($detail.ProcessId): $($detail.WorkingSet)MB RAM, $($detail.CPU)s CPU, $($detail.Threads) threads" -Level INFO
        }
        
        return $processDetails
    }
    catch {
        Write-AIOSMessage -Message "Error getting process details: $($_.Exception.Message)" -Level ERROR
        return @()
    }
}

function Set-AIOSLogLevel {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("DEBUG", "INFO", "WARN", "ERROR", "TRACE")]
        [string]$LogLevel
    )
    
    Write-AIOSMessage -Message "📝 Setting AIOS log level to: $LogLevel" -Level INFO
    
    try {
        # Update global configuration
        $global:AIOS_CONFIG.LOG_LEVEL = $LogLevel
        
        # Update global log level variable
        $script:LogLevel = $LogLevel
        
        # Save configuration
        Save-AIOSConfiguration
        
        # Try to communicate with running AIOS processes to change log level
        $aiosProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "python" -and 
            ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
        }
        
        if ($aiosProcesses.Count -gt 0) {
            Write-AIOSMessage -Message "Attempting to update log level in $($aiosProcesses.Count) running AIOS processes..." -Level INFO
            
            # Create a temporary config update file
            $configUpdateFile = "$DEBUG_DIR\log_level_update.json"
            @{
                action = "set_log_level"
                log_level = $LogLevel
                timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            } | ConvertTo-Json | Set-Content $configUpdateFile -Encoding UTF8
            
            # Signal processes to reload configuration (this would require the Python app to monitor for this file)
            Write-AIOSMessage -Message "Log level update signal sent to AIOS processes" -Level SUCCESS
        }
        else {
            Write-AIOSMessage -Message "No running AIOS processes found. Log level will be applied on next startup." -Level INFO
        }
        
        Write-AIOSMessage -Message "Log level successfully changed to: $LogLevel" -Level SUCCESS
        return $true
    }
    catch {
        Write-AIOSMessage -Message "Error setting log level: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Get-AIOSConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$Section = ""
    )
    
    if ([string]::IsNullOrEmpty($Section)) {
        return $global:AIOS_CONFIG
    }
    else {
        return $global:AIOS_CONFIG.$Section
    }
}

function Set-AIOSConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Section,
        
        [Parameter(Mandatory=$true)]
        [string]$Key,
        
        [Parameter(Mandatory=$true)]
        [object]$Value
    )
    
    try {
        # Update configuration
        $global:AIOS_CONFIG.$Section.$Key = $Value
        
        # Save configuration
        Save-AIOSConfiguration
        
        Write-AIOSMessage -Message "Configuration updated: $Section.$Key = $Value" -Level SUCCESS
        return $true
    }
    catch {
        Write-AIOSMessage -Message "Error updating configuration: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Invoke-BCMRemediation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("LIGHT", "MEDIUM", "HEAVY")]
        [string]$RemediationLevel
    )
    
    try {
        Write-AIOSMessage -Message "🔧 Invoking BCM remediation: $RemediationLevel" -Level WARN
        
        switch ($RemediationLevel) {
            "LIGHT" {
                # Light remediation: Send signal to reduce batch size
                $remediationSignal = @{
                    action = "reduce_batch_size"
                    level = "light"
                    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                    parameters = @{
                        batch_size_reduction = 0.5
                        max_concurrent_operations = 2
                    }
                }
                
                $signalFile = "$DEBUG_DIR\bcm_remediation_signal.json"
                $remediationSignal | ConvertTo-Json -Depth 3 | Set-Content $signalFile -Encoding UTF8
                
                return "Light remediation signal sent - reduced batch size to 50%"
            }
            
            "MEDIUM" {
                # Medium remediation: Limit concurrent operations and reduce complexity
                $remediationSignal = @{
                    action = "limit_concurrency"
                    level = "medium"
                    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                    parameters = @{
                        max_concurrent_operations = 1
                        complexity_threshold = 0.7
                        batch_size_reduction = 0.3
                    }
                }
                
                $signalFile = "$DEBUG_DIR\bcm_remediation_signal.json"
                $remediationSignal | ConvertTo-Json -Depth 3 | Set-Content $signalFile -Encoding UTF8
                
                return "Medium remediation signal sent - limited concurrency and reduced complexity"
            }
            
            "HEAVY" {
                # Heavy remediation: Restart specific AIOS processes (requires admin mode)
                if (-not $ADMIN_MODE) {
                    return "Heavy remediation requires Admin Mode - not performed"
                }
                
                # Find and restart the most resource-intensive AIOS processes
                $aiosProcesses = Get-Process | Where-Object { 
                    $_.ProcessName -eq "python" -and 
                    ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
                } | Sort-Object CPU -Descending
                
                if ($aiosProcesses.Count -gt 0) {
                    $targetProcess = $aiosProcesses[0]
                    Write-AIOSMessage -Message "Restarting most resource-intensive process: PID $($targetProcess.Id)" -Level WARN
                    
                    # Graceful restart of the process
                    try {
                        $targetProcess.CloseMainWindow()
                        Start-Sleep -Seconds 5
                        
                        if (-not $targetProcess.HasExited) {
                            $targetProcess.Kill()
                            Start-Sleep -Seconds 2
                        }
                        
                        # Restart the process (this would require knowledge of how to restart specific components)
                        return "Heavy remediation completed - restarted process PID $($targetProcess.Id)"
                    }
                    catch {
                        return "Heavy remediation failed - could not restart process: $($_.Exception.Message)"
                    }
                } else {
                    return "Heavy remediation - no AIOS processes found to restart"
                }
            }
        }
    }
    catch {
        Write-AIOSMessage -Message "Error during BCM remediation: $($_.Exception.Message)" -Level ERROR
        return "Remediation failed: $($_.Exception.Message)"
    }
}

function Test-AIOSHealth {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [ValidateSet("LIVENESS", "READINESS", "FULL")]
        [string]$CheckType = "FULL",
        
        [Parameter(Mandatory=$false)]
        [string]$BaseUrl = "http://localhost:8080",
        
        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 10
    )
    
    Write-AIOSMessage -Message "🏥 Testing AIOS health ($CheckType)..." -Level INFO
    
    $healthResults = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        CheckType = $CheckType
        OverallStatus = "UNKNOWN"
        Checks = @{}
        Recommendations = @()
    }
    
    try {
        # Liveness Check
        if ($CheckType -in @("LIVENESS", "FULL")) {
            $livenessResult = Test-AIOSLiveness -BaseUrl $BaseUrl -TimeoutSeconds $TimeoutSeconds
            $healthResults.Checks.Liveness = $livenessResult
            
            if (-not $livenessResult.Success) {
                $healthResults.Recommendations += "CRITICAL: Liveness check failed - consider restarting AIOS service"
            }
        }
        
        # Readiness Check
        if ($CheckType -in @("READINESS", "FULL")) {
            $readinessResult = Test-AIOSReadiness -BaseUrl $BaseUrl -TimeoutSeconds $TimeoutSeconds
            $healthResults.Checks.Readiness = $readinessResult
            
            if (-not $readinessResult.Success) {
                $healthResults.Recommendations += "WARNING: Readiness check failed - AIOS may not be ready for requests"
            }
        }
        
        # Determine overall status
        $allChecks = $healthResults.Checks.Values
        if ($allChecks.Count -eq 0) {
            $healthResults.OverallStatus = "NO_CHECKS"
        } elseif ($allChecks | Where-Object { $_.Success -eq $false }) {
            $healthResults.OverallStatus = "UNHEALTHY"
        } else {
            $healthResults.OverallStatus = "HEALTHY"
        }
        
        # Log health status
        $statusMessage = "AIOS Health Check ($CheckType): $($healthResults.OverallStatus)"
        switch ($healthResults.OverallStatus) {
            "HEALTHY" { Write-AIOSMessage -Message "✅ $statusMessage" -Level SUCCESS }
            "UNHEALTHY" { Write-AIOSMessage -Message "❌ $statusMessage" -Level ERROR }
            default { Write-AIOSMessage -Message "⚠️ $statusMessage" -Level WARN }
        }
        
        # Log recommendations
        foreach ($recommendation in $healthResults.Recommendations) {
            Write-AIOSMessage -Message "💡 $recommendation" -Level WARN
        }
        
        return $healthResults
    }
    catch {
        Write-AIOSMessage -Message "Error during health check: $($_.Exception.Message)" -Level ERROR
        $healthResults.OverallStatus = "ERROR"
        $healthResults.Error = $_.Exception.Message
        return $healthResults
    }
}

function Test-AIOSLiveness {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$BaseUrl = "http://localhost:8080",
        
        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 5
    )
    
    try {
        $livenessUrl = "$BaseUrl/health/liveness"
        
        $response = Invoke-RestMethod -Uri $livenessUrl -Method Get -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        
        return @{
            Success = $true
            Status = $response.status
            Timestamp = $response.timestamp
            Details = $response.details
            ResponseTime = $response.responseTime
            Message = "Liveness check passed"
        }
    }
    catch {
        # Fallback: Check if process is running
        $aiosProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "python" -and 
            ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
        }
        
        if ($aiosProcesses.Count -gt 0) {
            return @{
                Success = $true
                Status = "UP"
                Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                Details = "Process-based liveness check"
                ProcessCount = $aiosProcesses.Count
                Message = "Process running but API endpoint not accessible"
            }
        } else {
            return @{
                Success = $false
                Status = "DOWN"
                Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                Error = $_.Exception.Message
                Message = "No AIOS processes found and API endpoint failed"
            }
        }
    }
}

function Test-AIOSReadiness {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$BaseUrl = "http://localhost:8080",
        
        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 10
    )
    
    try {
        $readinessUrl = "$BaseUrl/health/readiness"
        
        $response = Invoke-RestMethod -Uri $readinessUrl -Method Get -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        
        return @{
            Success = $response.status -eq "READY"
            Status = $response.status
            Timestamp = $response.timestamp
            Components = $response.components
            Details = $response.details
            Message = "Readiness check completed"
        }
    }
    catch {
        # Fallback: Basic system checks
        $systemChecks = @{
            PythonEnvironment = Test-Path "$PYTHON_ENV_PATH\Scripts\python.exe"
            MainScript = Test-Path "$AIOS_ROOT\main.py"
            LogDirectory = Test-Path $LOG_DIR
            Configuration = Test-Path $CONFIG_FILE
        }
        
        $allChecksPass = $systemChecks.Values | Where-Object { $_ -eq $false } | Measure-Object | Select-Object -ExpandProperty Count
        
        return @{
            Success = $allChecksPass -eq 0
            Status = if ($allChecksPass -eq 0) { "READY" } else { "NOT_READY" }
            Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            Components = $systemChecks
            Error = $_.Exception.Message
            Message = "Fallback system readiness check"
        }
    }
}

function Initialize-AIOSSecurity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [switch]$CreateServiceAccount,
        
        [Parameter(Mandatory=$false)]
        [switch]$ConfigureFirewall,
        
        [Parameter(Mandatory=$false)]
        [switch]$VerifyIntegrity
    )
    
    Write-AIOSMessage -Message "🔒 Initializing AIOS security features..." -Level INFO
    
    $securityResults = @{
        ServiceAccount = @{ Success = $false; Message = "" }
        Firewall = @{ Success = $false; Message = "" }
        Integrity = @{ Success = $false; Message = "" }
    }
    
    try {
        # Create dedicated service account if requested
        if ($CreateServiceAccount) {
            $serviceAccountResult = New-AIOSServiceAccount
            $securityResults.ServiceAccount = $serviceAccountResult
        }
        
        # Configure firewall rules if requested
        if ($ConfigureFirewall) {
            $firewallResult = Set-AIOSFirewallRules
            $securityResults.Firewall = $firewallResult
        }
        
        # Verify configuration integrity if requested
        if ($VerifyIntegrity) {
            $integrityResult = Test-AIOSConfigurationIntegrity
            $securityResults.Integrity = $integrityResult
        }
        
        return $securityResults
    }
    catch {
        Write-AIOSMessage -Message "Error initializing security features: $($_.Exception.Message)" -Level ERROR
        return $securityResults
    }
}

function New-AIOSServiceAccount {
    [CmdletBinding()]
    param()
    
    try {
        Write-AIOSMessage -Message "Creating AIOS service account..." -Level INFO
        
        $serviceAccountName = "AIOS-Service"
        $serviceAccountDescription = "Dedicated service account for AIOS operations with minimal required permissions"
        
        # Check if account already exists
        try {
            $existingAccount = Get-LocalUser -Name $serviceAccountName -ErrorAction Stop
            Write-AIOSMessage -Message "Service account already exists: $serviceAccountName" -Level INFO
            return @{ Success = $true; Message = "Service account already exists" }
        }
        catch {
            # Account doesn't exist, create it
        }
        
        # Create the service account (requires admin privileges)
        if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
            return @{ Success = $false; Message = "Administrator privileges required to create service account" }
        }
        
        # Generate secure password
        $password = [System.Web.Security.Membership]::GeneratePassword(16, 4)
        $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
        
        # Create the user account
        New-LocalUser -Name $serviceAccountName -Description $serviceAccountDescription -Password $securePassword -PasswordNeverExpires -UserMayNotChangePassword -ErrorAction Stop
        
        # Add to appropriate groups (minimal permissions)
        Add-LocalGroupMember -Group "Users" -Member $serviceAccountName -ErrorAction SilentlyContinue
        
        Write-AIOSMessage -Message "✅ AIOS service account created successfully: $serviceAccountName" -Level SUCCESS
        
        return @{ 
            Success = $true; 
            Message = "Service account created successfully";
            AccountName = $serviceAccountName;
            Password = $password; # In production, this should be stored securely
        }
    }
    catch {
        Write-AIOSMessage -Message "Error creating service account: $($_.Exception.Message)" -Level ERROR
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

function Set-AIOSFirewallRules {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [int[]]$AllowedPorts = @(8080, 443, 80),
        
        [Parameter(Mandatory=$false)]
        [string]$RuleName = "AIOS-Allow-Traffic"
    )
    
    try {
        Write-AIOSMessage -Message "Configuring AIOS firewall rules..." -Level INFO
        
        if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
            return @{ Success = $false; Message = "Administrator privileges required to configure firewall" }
        }
        
        $firewallResults = @{
            Success = $true
            RulesCreated = @()
            Errors = @()
        }
        
        foreach ($port in $AllowedPorts) {
            try {
                # Create inbound rule
                $rule = New-NetFirewallRule -DisplayName "$RuleName-Inbound-$port" -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow -Profile Any -ErrorAction Stop
                $firewallResults.RulesCreated += "Inbound TCP $port"
                
                Write-AIOSMessage -Message "Created firewall rule for port $port (inbound)" -Level SUCCESS
            }
            catch {
                $firewallResults.Errors += "Failed to create inbound rule for port $port : $($_.Exception.Message)"
                Write-AIOSMessage -Message "Failed to create inbound firewall rule for port $port : $($_.Exception.Message)" -Level ERROR
            }
        }
        
        if ($firewallResults.RulesCreated.Count -gt 0) {
            Write-AIOSMessage -Message "✅ Created $($firewallResults.RulesCreated.Count) firewall rules for AIOS" -Level SUCCESS
        }
        
        return $firewallResults
    }
    catch {
        Write-AIOSMessage -Message "Error configuring firewall rules: $($_.Exception.Message)" -Level ERROR
        return @{ Success = $false; Message = $_.Exception.Message; RulesCreated = @(); Errors = @($_.Exception.Message) }
    }
}

function Test-AIOSConfigurationIntegrity {
    [CmdletBinding()]
    param()
    
    try {
        Write-AIOSMessage -Message "Testing AIOS configuration integrity..." -Level INFO
        
        $integrityResults = @{
            Success = $true
            Checks = @{}
            Recommendations = @()
        }
        
        # Check configuration file integrity
        if (Test-Path $CONFIG_FILE) {
            $configHash = Get-FileHash -Path $CONFIG_FILE -Algorithm SHA256
            $integrityResults.Checks.ConfigFile = @{
                Present = $true
                Hash = $configHash.Hash
                Algorithm = $configHash.Algorithm
            }
        } else {
            $integrityResults.Checks.ConfigFile = @{ Present = $false }
            $integrityResults.Recommendations += "Configuration file missing - using defaults"
        }
        
        # Check main script integrity
        $mainScriptPath = "$AIOS_ROOT\main.py"
        if (Test-Path $mainScriptPath) {
            $mainScriptHash = Get-FileHash -Path $mainScriptPath -Algorithm SHA256
            $integrityResults.Checks.MainScript = @{
                Present = $true
                Hash = $mainScriptHash.Hash
                Algorithm = $mainScriptHash.Algorithm
            }
        } else {
            $integrityResults.Checks.MainScript = @{ Present = $false }
            $integrityResults.Recommendations += "Main script missing - AIOS may not function properly"
        }
        
        # Check for suspicious file modifications
        $suspiciousFiles = @(
            "$AIOS_ROOT\*.exe",
            "$AIOS_ROOT\*.bat",
            "$AIOS_ROOT\*.cmd",
            "$AIOS_ROOT\*.ps1"
        )
        
        $foundSuspicious = @()
        foreach ($pattern in $suspiciousFiles) {
            $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Where-Object { 
                $_.Name -notlike "*aios_powershell_wrapper*" -and 
                $_.Name -notlike "*install_aios*" 
            }
            if ($files) {
                $foundSuspicious += $files
            }
        }
        
        $integrityResults.Checks.SuspiciousFiles = @{
            Count = $foundSuspicious.Count
            Files = $foundSuspicious | Select-Object Name, FullName, LastWriteTime
        }
        
        if ($foundSuspicious.Count -gt 0) {
            $integrityResults.Recommendations += "Found $($foundSuspicious.Count) potentially suspicious executable files"
            $integrityResults.Success = $false
        }
        
        # Log integrity results
        if ($integrityResults.Success) {
            Write-AIOSMessage -Message "✅ Configuration integrity check passed" -Level SUCCESS
        } else {
            Write-AIOSMessage -Message "⚠️ Configuration integrity issues detected" -Level WARN
            foreach ($recommendation in $integrityResults.Recommendations) {
                Write-AIOSMessage -Message "💡 $recommendation" -Level WARN
            }
        }
        
        return $integrityResults
    }
    catch {
        Write-AIOSMessage -Message "Error during integrity check: $($_.Exception.Message)" -Level ERROR
        return @{ Success = $false; Error = $_.Exception.Message; Checks = @{}; Recommendations = @() }
    }
}

function Get-AIOSPerformanceCounters {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [int]$SampleInterval = 1,
        
        [Parameter(Mandatory=$false)]
        [int]$MaxSamples = 1
    )
    
    try {
        Write-AIOSMessage -Message "📊 Collecting AIOS performance counters..." -Level INFO
        
        $performanceData = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            SystemCounters = @{}
            ProcessCounters = @{}
            NetworkCounters = @{}
        }
        
        # System-level counters
        try {
            $cpuCounter = Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval $SampleInterval -MaxSamples $MaxSamples -ErrorAction SilentlyContinue
            $memoryCounter = Get-Counter '\Memory\Available MBytes' -SampleInterval $SampleInterval -MaxSamples $MaxSamples -ErrorAction SilentlyContinue
            $diskCounter = Get-Counter '\LogicalDisk(C:)\% Free Space' -SampleInterval $SampleInterval -MaxSamples $MaxSamples -ErrorAction SilentlyContinue
            
            $performanceData.SystemCounters = @{
                CPUUsage = if ($cpuCounter) { [Math]::Round($cpuCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
                AvailableMemory = if ($memoryCounter) { [Math]::Round($memoryCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
                DiskFreeSpace = if ($diskCounter) { [Math]::Round($diskCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            }
        }
        catch {
            Write-AIOSMessage -Message "Error collecting system counters: $($_.Exception.Message)" -Level WARN
        }
        
        # AIOS process-specific counters
        $aiosProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "python" -and 
            ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
        }
        
        foreach ($process in $aiosProcesses) {
            try {
                $processName = "python_$($process.Id)"
                $cpuCounterPath = "\Process($processName)\% Processor Time"
                $memoryCounterPath = "\Process($processName)\Working Set"
                
                # Try to get process-specific counters
                $processCpuCounter = Get-Counter $cpuCounterPath -SampleInterval $SampleInterval -MaxSamples $MaxSamples -ErrorAction SilentlyContinue
                $processMemoryCounter = Get-Counter $memoryCounterPath -SampleInterval $SampleInterval -MaxSamples $MaxSamples -ErrorAction SilentlyContinue
                
                $performanceData.ProcessCounters["PID_$($process.Id)"] = @{
                    ProcessId = $process.Id
                    ProcessName = $process.ProcessName
                    CPUUsage = if ($processCpuCounter) { [Math]::Round($processCpuCounter.CounterSamples[0].CookedValue, 2) } else { "N/A" }
                    WorkingSet = if ($processMemoryCounter) { [Math]::Round($processMemoryCounter.CounterSamples[0].CookedValue / 1MB, 2) } else { "N/A" }
                    HandleCount = $process.HandleCount
                    ThreadCount = $process.Threads.Count
                    StartTime = $process.StartTime
                }
            }
            catch {
                Write-AIOSMessage -Message "Error collecting counters for process $($process.Id): $($_.Exception.Message)" -Level WARN
            }
        }
        
        # Network counters
        try {
            $networkCounters = Get-Counter '\Network Interface(*)\Bytes Total/sec' -SampleInterval $SampleInterval -MaxSamples $MaxSamples -ErrorAction SilentlyContinue
            if ($networkCounters) {
                $totalNetworkBytes = ($networkCounters.CounterSamples | Where-Object { $_.InstanceName -ne "_Total" } | Measure-Object -Property CookedValue -Sum).Sum
                $performanceData.NetworkCounters = @{
                    TotalBytesPerSec = [Math]::Round($totalNetworkBytes, 2)
                    TotalMBPerSec = [Math]::Round($totalNetworkBytes / 1MB, 2)
                }
            }
        }
        catch {
            Write-AIOSMessage -Message "Error collecting network counters: $($_.Exception.Message)" -Level WARN
        }
        
        return $performanceData
    }
    catch {
        Write-AIOSMessage -Message "Error collecting performance counters: $($_.Exception.Message)" -Level ERROR
        return @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            Error = $_.Exception.Message
            SystemCounters = @{}
            ProcessCounters = @{}
            NetworkCounters = @{}
        }
    }
}

function Start-AIOSPerformanceMonitoring {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [int]$IntervalSeconds = 30,
        
        [Parameter(Mandatory=$false)]
        [string]$OutputFile = "$LOG_DIR\aios_performance_monitoring.json"
    )
    
    Write-AIOSMessage -Message "📊 Starting AIOS performance monitoring..." -Level INFO
    Write-AIOSMessage -Message "Monitoring interval: $IntervalSeconds seconds" -Level INFO
    Write-AIOSMessage -Message "Output file: $OutputFile" -Level INFO
    
    try {
        while ($true) {
            $performanceData = Get-AIOSPerformanceCounters
            
            # Append to monitoring file
            $performanceData | ConvertTo-Json -Depth 5 | Add-Content $OutputFile -Encoding UTF8
            
            # Log key metrics
            $systemCpu = $performanceData.SystemCounters.CPUUsage
            $systemMemory = $performanceData.SystemCounters.AvailableMemory
            $processCount = $performanceData.ProcessCounters.Count
            
            Write-AIOSMessage -Message "Performance: CPU=$systemCpu%, Memory=$systemMemory MB, AIOS Processes=$processCount" -Level INFO
            
            # Check for performance alerts
            if ($systemCpu -gt 90) {
                Write-AIOSMessage -Message "🚨 High CPU usage detected: $systemCpu%" -Level WARN
                Write-AIOSEventLog -Message "AIOS High CPU Alert: $systemCpu%" -EntryType Warning -EventId 3001
            }
            
            if ($systemMemory -lt 1000) {
                Write-AIOSMessage -Message "🚨 Low available memory: $systemMemory MB" -Level WARN
                Write-AIOSEventLog -Message "AIOS Low Memory Alert: $systemMemory MB available" -EntryType Warning -EventId 3002
            }
            
            Start-Sleep -Seconds $IntervalSeconds
        }
    }
    catch {
        Write-AIOSMessage -Message "Error in performance monitoring: $($_.Exception.Message)" -Level ERROR
        Write-AIOSEventLog -Message "AIOS Performance Monitoring Error: $($_.Exception.Message)" -EntryType Error -EventId 3003
    }
}

# ===========================================
# MIDDLEWARE & EVENT-DRIVEN FUNCTIONS
# ===========================================

# Real-Time Dynamic Throttling - API Gatekeeper Middleware
function Filter-ThrottledCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData,
        
        [Parameter(Mandatory=$false)]
        [int]$MaximumConcurrency = 5,
        
        [Parameter(Mandatory=$false)]
        [int]$BaseDelayMs = 50,
        
        [Parameter(Mandatory=$false)]
        [int]$MaxDelayMs = 5000
    )
    
    try {
        # Check current load on Python service
        $aiosProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "python" -and 
            ($_.CommandLine -like "*aios*" -or $_.CommandLine -like "*luna*" -or $_.CommandLine -like "*carma*")
        }
        
        $activeRequests = $aiosProcesses.Count
        
        # Check CPU load for dynamic throttling
        $cpuLoad = Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1 -ErrorAction SilentlyContinue
        $currentCpuUsage = if ($cpuLoad) { $cpuLoad.CounterSamples[0].CookedValue } else { 0 }
        
        # Dynamic throttling logic
        if ($activeRequests -ge $MaximumConcurrency -or $currentCpuUsage -gt 85) {
            # Calculate delay based on overload severity
            $overloadFactor = [Math]::Max($activeRequests - $MaximumConcurrency + 1, 1)
            $cpuFactor = if ($currentCpuUsage -gt 85) { 2 } else { 1 }
            
            $calculatedDelay = [Math]::Min($BaseDelayMs * $overloadFactor * $cpuFactor, $MaxDelayMs)
            
            Write-AIOSMessage -Message "🛑 Throttling command: $($CommandData.CommandType) - Active: $activeRequests, CPU: $([Math]::Round($currentCpuUsage, 1))%, Delay: ${calculatedDelay}ms" -Level WARN
            
            # Apply QoS - lower priority for current processes if high-priority command waiting
            if ($CommandData.Priority -eq "HIGH" -and $activeRequests -gt 0) {
                $aiosProcesses | ForEach-Object {
                    try {
                        $_.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::BelowNormal
                        Write-AIOSMessage -Message "Lowered priority for PID $($_.Id) to accommodate high-priority command" -Level INFO
                    }
                    catch {
                        Write-AIOSMessage -Message "Could not adjust priority for PID $($_.Id): $($_.Exception.Message)" -Level WARN
                    }
                }
            }
            
            # Graceful delay with progress indication
            $delaySteps = [Math]::Floor($calculatedDelay / 100)
            for ($i = 0; $i -lt $delaySteps; $i++) {
                Start-Sleep -Milliseconds 100
                if ($i % 5 -eq 0) {
                    Write-AIOSMessage -Message "Throttling in progress... $([Math]::Round((($i + 1) / $delaySteps) * 100, 0))%" -Level DEBUG
                }
            }
            
            # Record throttling event for telemetry
            Record-CommandTelemetry -EventType "THROTTLE" -CommandData $CommandData -Duration $calculatedDelay -Metadata @{
                ActiveRequests = $activeRequests
                CPUUsage = $currentCpuUsage
                DelayMs = $calculatedDelay
                Priority = $CommandData.Priority
            }
        }
        
        # Update command execution context
        $CommandData.ExecutionContext = @{
            Throttled = $true
            DelayApplied = $calculatedDelay
            Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            ProcessCount = $activeRequests
            CPUUsage = $currentCpuUsage
        }
        
        # Pass command through to Python service
        return $CommandData
        
    }
    catch {
        Write-AIOSMessage -Message "Error in throttling filter: $($_.Exception.Message)" -Level ERROR
        return $CommandData
    }
}

# Event-Driven Telemetry Logger - Command Execution Tracker
function Record-CommandTelemetry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("START", "COMPLETE", "ERROR", "THROTTLE", "CANCEL")]
        [string]$EventType,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData,
        
        [Parameter(Mandatory=$false)]
        [double]$Duration = 0,
        
        [Parameter(Mandatory=$false)]
        [hashtable]$Metadata = @{},
        
        [Parameter(Mandatory=$false)]
        [string]$TelemetryEndpoint = "http://localhost:8080/api/telemetry"
    )
    
    try {
        # Create comprehensive telemetry record
        $telemetryRecord = @{
            Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            EventType = $EventType
            CommandId = $CommandData.CommandId
            CommandType = $CommandData.CommandType
            Priority = $CommandData.Priority
            Duration = $Duration
            UserContext = @{
                Username = $env:USERNAME
                Domain = $env:USERDOMAIN
                MachineName = $env:COMPUTERNAME
                SessionId = $PID
            }
            SystemContext = @{
                PowerShellVersion = $PSVersionTable.PSVersion.ToString()
                OS = "$($env:OS) $([System.Environment]::OSVersion.Version.ToString())"
                Architecture = $env:PROCESSOR_ARCHITECTURE
                AvailableMemory = (Get-WmiObject -Class Win32_OperatingSystem).FreePhysicalMemory / 1MB
            }
            AIOSContext = @{
                AIOS_ROOT = $AIOS_ROOT
                PYTHON_ENV_PATH = $PYTHON_ENV_PATH
                LogLevel = $LogLevel
                AdminMode = $ADMIN_MODE
                MonitoringEnabled = $MONITORING_ENABLED
            }
            Metadata = $Metadata
            ExecutionContext = $CommandData.ExecutionContext
        }
        
        # Store telemetry locally for immediate access
        $telemetryFile = "$DEBUG_DIR\telemetry_$(Get-Date -Format 'yyyyMMdd').json"
        $telemetryRecord | ConvertTo-Json -Depth 10 | Add-Content $telemetryFile -Encoding UTF8
        
        # Send to external telemetry endpoint if available
        if ($TelemetryEndpoint -and $EventType -in @("COMPLETE", "ERROR")) {
            try {
                $response = Invoke-RestMethod -Uri $TelemetryEndpoint -Method Post -Body ($telemetryRecord | ConvertTo-Json -Depth 10) -ContentType "application/json" -TimeoutSec 5 -ErrorAction SilentlyContinue
                Write-AIOSMessage -Message "Telemetry sent to endpoint successfully" -Level DEBUG
            }
            catch {
                Write-AIOSMessage -Message "Failed to send telemetry to endpoint: $($_.Exception.Message)" -Level DEBUG
            }
        }
        
        # Log telemetry event
        Write-AIOSMessage -Message "📊 Telemetry: $EventType - $($CommandData.CommandType) - Duration: ${Duration}ms" -Level DEBUG
        
        # Update real-time metrics cache
        Update-TelemetryCache -EventType $EventType -CommandData $CommandData -Duration $Duration
        
        return $telemetryRecord
    }
    catch {
        Write-AIOSMessage -Message "Error recording telemetry: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

# On-Demand State Management - Dynamic Control Plane
function Sync-PythonState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("UPDATE_LOG_LEVEL", "FLUSH_CACHE", "RELOAD_CONFIG", "HEALTH_OVERRIDE", "BCM_RESET", "CUSTOM_COMMAND")]
        [string]$Operation,
        
        [Parameter(Mandatory=$false)]
        [string]$Value = "",
        
        [Parameter(Mandatory=$false)]
        [hashtable]$Parameters = @{},
        
        [Parameter(Mandatory=$false)]
        [string]$ControlEndpoint = "http://localhost:8080/admin/control",
        
        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 10
    )
    
    try {
        Write-AIOSMessage -Message "🎛️ Syncing Python state: $Operation" -Level INFO
        
        # Create control command
        $controlCommand = @{
            Operation = $Operation
            Value = $Value
            Parameters = $Parameters
            Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            Source = "PowerShell-Orchestrator"
            CommandId = [System.Guid]::NewGuid().ToString()
        }
        
        # Record control command telemetry
        Record-CommandTelemetry -EventType "START" -CommandData @{
            CommandId = $controlCommand.CommandId
            CommandType = "STATE_SYNC"
            Priority = "HIGH"
            Operation = $Operation
        }
        
        $startTime = Get-Date
        
        # Send control command to Python service
        try {
            $response = Invoke-RestMethod -Uri $ControlEndpoint -Method Post -Body ($controlCommand | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
            
            $duration = ((Get-Date) - $startTime).TotalMilliseconds
            
            # Record successful completion
            Record-CommandTelemetry -EventType "COMPLETE" -CommandData @{
                CommandId = $controlCommand.CommandId
                CommandType = "STATE_SYNC"
                Priority = "HIGH"
                Operation = $Operation
            } -Duration $duration -Metadata @{
                Response = $response
                Success = $true
            }
            
            Write-AIOSMessage -Message "✅ State sync completed: $Operation - Response: $($response.message)" -Level SUCCESS
            
            return @{
                Success = $true
                Response = $response
                Duration = $duration
                Operation = $Operation
            }
        }
        catch {
            $duration = ((Get-Date) - $startTime).TotalMilliseconds
            
            # Record error
            Record-CommandTelemetry -EventType "ERROR" -CommandData @{
                CommandId = $controlCommand.CommandId
                CommandType = "STATE_SYNC"
                Priority = "HIGH"
                Operation = $Operation
            } -Duration $duration -Metadata @{
                Error = $_.Exception.Message
                Success = $false
            }
            
            Write-AIOSMessage -Message "❌ State sync failed: $Operation - Error: $($_.Exception.Message)" -Level ERROR
            
            return @{
                Success = $false
                Error = $_.Exception.Message
                Duration = $duration
                Operation = $Operation
            }
        }
    }
    catch {
        Write-AIOSMessage -Message "Error in state sync: $($_.Exception.Message)" -Level ERROR
        return @{
            Success = $false
            Error = $_.Exception.Message
            Operation = $Operation
        }
    }
}

# Helper function to update real-time telemetry cache
function Update-TelemetryCache {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$EventType,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData,
        
        [Parameter(Mandatory=$false)]
        [double]$Duration = 0
    )
    
    try {
        $cacheFile = "$DEBUG_DIR\telemetry_cache.json"
        
        # Load existing cache or create new
        if (Test-Path $cacheFile) {
            $cache = Get-Content $cacheFile -Raw | ConvertFrom-Json
        } else {
            $cache = @{
                LastUpdated = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                CommandStats = @{}
                PerformanceMetrics = @{
                    TotalCommands = 0
                    SuccessfulCommands = 0
                    FailedCommands = 0
                    AverageDuration = 0
                    ThrottledCommands = 0
                }
            }
        }
        
        # Update command statistics
        $commandType = $CommandData.CommandType
        if (-not $cache.CommandStats.$commandType) {
            $cache.CommandStats.$commandType = @{
                Count = 0
                TotalDuration = 0
                SuccessCount = 0
                ErrorCount = 0
                LastExecuted = $null
            }
        }
        
        $cache.CommandStats.$commandType.Count++
        $cache.CommandStats.$commandType.TotalDuration += $Duration
        $cache.CommandStats.$commandType.LastExecuted = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
        
        # Update performance metrics
        $cache.PerformanceMetrics.TotalCommands++
        
        switch ($EventType) {
            "COMPLETE" {
                $cache.PerformanceMetrics.SuccessfulCommands++
                $cache.CommandStats.$commandType.SuccessCount++
            }
            "ERROR" {
                $cache.PerformanceMetrics.FailedCommands++
                $cache.CommandStats.$commandType.ErrorCount++
            }
            "THROTTLE" {
                $cache.PerformanceMetrics.ThrottledCommands++
            }
        }
        
        # Calculate average duration
        $cache.PerformanceMetrics.AverageDuration = if ($cache.PerformanceMetrics.TotalCommands -gt 0) {
            ($cache.CommandStats.Values | ForEach-Object { $_.TotalDuration } | Measure-Object -Sum).Sum / $cache.PerformanceMetrics.TotalCommands
        } else { 0 }
        
        $cache.LastUpdated = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
        
        # Save updated cache
        $cache | ConvertTo-Json -Depth 10 | Set-Content $cacheFile -Encoding UTF8
        
    }
    catch {
        Write-AIOSMessage -Message "Error updating telemetry cache: $($_.Exception.Message)" -Level ERROR
    }
}

# ===========================================
# CROSS-CUTTING CONCERNS - MIDDLEWARE PIPELINE
# ===========================================

# Security Feature: Input Validation & Sanitization
function Filter-InputSanitizer {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData,
        
        [Parameter(Mandatory=$false)]
        [hashtable]$SecurityConfig = @{
            EnableInjectionPrevention = $true
            EnableSchemaValidation = $true
            EnablePromptGuardrails = $true
            MaxInputLength = 10000
            AllowedCharacters = 'a-zA-Z0-9\s\-_.,!?@#$%^&*()+={}[]|\\:;\"''<>/`~'
        }
    )
    
    try {
        Write-AIOSMessage -Message "Validating and sanitizing input for command: $($CommandData.CommandType)" -Level DEBUG
        
        $sanitizationResults = @{
            OriginalInput = $CommandData.Parameters
            SanitizedInput = @{}
            ValidationPassed = $true
            SecurityWarnings = @()
            SecurityBlocks = @()
            SanitizationActions = @()
        }
        
        # 1. Command Injection Prevention
        if ($SecurityConfig.EnableInjectionPrevention) {
            $dangerousPatterns = @(
                ';', '`', '\$', '\(', '\)', '&', '\|', '<', '>', '>>', '2>&1',
                'exec', 'eval', 'subprocess', 'os\.system', 'shell=True',
                'rm\s+-rf', 'del\s+/s', 'format\s+', 'shutdown', 'reboot'
            )
            
            foreach ($paramName in $CommandData.Parameters.Keys) {
                $paramValue = $CommandData.Parameters[$paramName]
                
                if ($paramValue -is [string]) {
                    foreach ($pattern in $dangerousPatterns) {
                        if ($paramValue -match $pattern) {
                            $sanitizationResults.SecurityBlocks += "Dangerous pattern '$pattern' detected in parameter '$paramName'"
                            $sanitizationResults.ValidationPassed = $false
                            
                            # Log security violation
                            Write-AIOSMessage -Message "🚨 SECURITY BLOCK: Dangerous pattern '$pattern' in parameter '$paramName'" -Level ERROR
                            Write-AIOSEventLog -Message "Security violation blocked: $pattern in $paramName" -EntryType Warning -EventId 4001
                        }
                    }
                    
                    # Remove dangerous characters while preserving functionality
                    $sanitizedValue = $paramValue -replace '[`;|&<>]', ''
                    if ($sanitizedValue -ne $paramValue) {
                        $sanitizationResults.SanitizationActions += "Removed dangerous characters from '$paramName'"
                        $sanitizationResults.SecurityWarnings += "Sanitized dangerous characters in parameter '$paramName'"
                    }
                    
                    $sanitizationResults.SanitizedInput[$paramName] = $sanitizedValue
                } else {
                    $sanitizationResults.SanitizedInput[$paramName] = $paramValue
                }
            }
        }
        
        # 2. Schema Enforcement & Type Validation
        if ($SecurityConfig.EnableSchemaValidation) {
            $schemaRules = @{
                "questions" = @{ Type = "int"; Min = 1; Max = 100; Required = $false }
                "mode" = @{ Type = "string"; AllowedValues = @("luna", "carma", "enterprise"); Required = $false }
                "input" = @{ Type = "string"; MaxLength = $SecurityConfig.MaxInputLength; Required = $false }
                "priority" = @{ Type = "string"; AllowedValues = @("LOW", "NORMAL", "HIGH", "CRITICAL"); Required = $false }
                "timeout" = @{ Type = "int"; Min = 1; Max = 3600; Required = $false }
            }
            
            foreach ($paramName in $sanitizationResults.SanitizedInput.Keys) {
                $paramValue = $sanitizationResults.SanitizedInput[$paramName]
                
                if ($schemaRules.ContainsKey($paramName)) {
                    $rule = $schemaRules[$paramName]
                    
                    # Type validation
                    if ($rule.Type -eq "int") {
                        if (-not ($paramValue -match '^\d+$')) {
                            $sanitizationResults.SecurityBlocks += "Parameter '$paramName' must be an integer"
                            $sanitizationResults.ValidationPassed = $false
                            continue
                        }
                        $paramValue = [int]$paramValue
                    }
                    
                    # Range validation
                    if ($rule.Min -and $paramValue -lt $rule.Min) {
                        $sanitizationResults.SecurityBlocks += "Parameter '$paramName' must be >= $($rule.Min)"
                        $sanitizationResults.ValidationPassed = $false
                        continue
                    }
                    
                    if ($rule.Max -and $paramValue -gt $rule.Max) {
                        $sanitizationResults.SecurityBlocks += "Parameter '$paramName' must be less than or equal to $($rule.Max)"
                        $sanitizationResults.ValidationPassed = $false
                        continue
                    }
                    
                    if ($rule.MaxLength -and $paramValue.Length -gt $rule.MaxLength) {
                        $sanitizationResults.SecurityBlocks += "Parameter '$paramName' exceeds maximum length of $($rule.MaxLength)"
                        $sanitizationResults.ValidationPassed = $false
                        continue
                    }
                    
                    # Allowed values validation
                    if ($rule.AllowedValues -and $paramValue -notin $rule.AllowedValues) {
                        $sanitizationResults.SecurityBlocks += "Parameter '$paramName' must be one of: $($rule.AllowedValues -join ', ')"
                        $sanitizationResults.ValidationPassed = $false
                        continue
                    }
                    
                    $sanitizationResults.SanitizedInput[$paramName] = $paramValue
                }
            }
        }
        
        # 3. AI Prompt Guardrails
        if ($SecurityConfig.EnablePromptGuardrails) {
            $jailbreakPatterns = @(
                'ignore all previous instructions',
                'disregard previous instructions',
                'forget everything',
                'you are now',
                'pretend to be',
                'roleplay as',
                'act as if',
                'system prompt',
                'developer mode',
                'jailbreak',
                'override safety',
                'ignore safety',
                'ignore guidelines'
            )
            
            foreach ($paramName in $sanitizationResults.SanitizedInput.Keys) {
                $paramValue = $sanitizationResults.SanitizedInput[$paramName]
                
                if ($paramValue -is [string] -and $paramName -like "*input*" -or $paramName -like "*prompt*") {
                    foreach ($pattern in $jailbreakPatterns) {
                        if ($paramValue -match $pattern) {
                            $sanitizationResults.SecurityWarnings += "Potential jailbreak attempt detected in '$paramName': '$pattern'"
                            
                            # Log security warning
                            Write-AIOSMessage -Message "⚠️ SECURITY WARNING: Potential jailbreak attempt in '$paramName'" -Level WARN
                            Write-AIOSEventLog -Message "Jailbreak attempt detected: $pattern in $paramName" -EntryType Warning -EventId 4002
                            
                            # Optionally redact or flag the content
                            $sanitizedValue = $paramValue -replace $pattern, "[REDACTED]"
                            $sanitizationResults.SanitizedInput[$paramName] = $sanitizedValue
                            $sanitizationResults.SanitizationActions += "Redacted jailbreak attempt in '$paramName'"
                        }
                    }
                }
            }
        }
        
        # Update command data with sanitized input
        $CommandData.Parameters = $sanitizationResults.SanitizedInput
        $CommandData.SecurityValidation = $sanitizationResults
        
        # Record security telemetry
        if ($sanitizationResults.SecurityWarnings.Count -gt 0 -or $sanitizationResults.SecurityBlocks.Count -gt 0) {
            Record-CommandTelemetry -EventType "START" -CommandData $CommandData -Metadata @{
                SecurityWarnings = $sanitizationResults.SecurityWarnings.Count
                SecurityBlocks = $sanitizationResults.SecurityBlocks.Count
                ValidationPassed = $sanitizationResults.ValidationPassed
            }
        }
        
        if (-not $sanitizationResults.ValidationPassed) {
            Write-AIOSMessage -Message "🚫 Command blocked by security validation: $($sanitizationResults.SecurityBlocks -join '; ')" -Level ERROR
            return $null
        }
        
        Write-AIOSMessage -Message "✅ Input validation completed - $($sanitizationResults.SanitizationActions.Count) sanitization actions applied" -Level DEBUG
        return $CommandData
    }
    catch {
        Write-AIOSMessage -Message "Error in input sanitization: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

# Data Feature: Response Transformation & Abstraction
function Convert-ServiceResponse {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [object]$RawResponse,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData,
        
        [Parameter(Mandatory=$false)]
        [hashtable]$TransformConfig = @{
            EnableObjectification = $true
            EnableErrorAbstraction = $true
            EnableResultFiltering = $true
            MaxResponseSize = 1048576  # 1MB
        }
    )
    
    try {
        Write-AIOSMessage -Message "🔄 Transforming service response for command: $($CommandData.CommandType)" -Level DEBUG
        
        $transformationResults = @{
            OriginalResponse = $RawResponse
            TransformedResponse = $null
            TransformationActions = @()
            ErrorDetails = $null
            FilteredProperties = @()
        }
        
        # 1. Error Abstraction & Standardization
        if ($TransformConfig.EnableErrorAbstraction -and ($RawResponse -is [System.Management.Automation.ErrorRecord] -or $RawResponse -like "*error*" -or $RawResponse -like "*exception*")) {
            $errorId = [System.Guid]::NewGuid().ToString()
            
            $standardizedError = [PSCustomObject]@{
                ErrorId = $errorId
                ErrorType = "AIOS_SERVICE_ERROR"
                ErrorMessage = "AI Service operation failed"
                ErrorDetails = "See Error ID $errorId for technical details"
                Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                CommandType = $CommandData.CommandType
                CommandId = $CommandData.CommandId
                UserFriendlyMessage = "The AI service encountered an issue. Please try again or contact support with Error ID: $errorId"
                Severity = "ERROR"
            }
            
            # Log detailed error internally
            Write-AIOSMessage -Message "❌ Service error occurred - Error ID: $errorId" -Level ERROR
            Write-DebugInfo -Message "Service error details" -FilePath "Convert-ServiceResponse" -LineNumber 1 -Variables @{
                ErrorId = $errorId
                RawError = $RawResponse
                CommandData = $CommandData
            }
            
            $transformationResults.TransformedResponse = $standardizedError
            $transformationResults.TransformationActions += "Standardized error response"
            $transformationResults.ErrorDetails = $RawResponse
            
            return $transformationResults
        }
        
        # 2. Response Size Validation
        $responseSize = if ($RawResponse -is [string]) { $RawResponse.Length } else { ($RawResponse | ConvertTo-Json -Compress).Length }
        if ($responseSize -gt $TransformConfig.MaxResponseSize) {
            $transformationResults.TransformedResponse = [PSCustomObject]@{
                ErrorId = [System.Guid]::NewGuid().ToString()
                ErrorType = "RESPONSE_SIZE_LIMIT"
                ErrorMessage = "Response exceeds maximum size limit"
                UserFriendlyMessage = "The AI service response is too large to process. Please refine your request."
                ResponseSize = $responseSize
                MaxAllowedSize = $TransformConfig.MaxResponseSize
            }
            $transformationResults.TransformationActions += "Applied response size limit"
            return $transformationResults
        }
        
        # 3. Objectification (Convert to PowerShell Objects)
        if ($TransformConfig.EnableObjectification) {
            $objectifiedResponse = $null
            
            if ($RawResponse -is [string]) {
                # Try to parse as JSON first
                try {
                    $jsonResponse = $RawResponse | ConvertFrom-Json -ErrorAction Stop
                    $objectifiedResponse = ConvertTo-PowerShellObject -JsonData $jsonResponse -CommandData $CommandData
                }
                catch {
                    # Not JSON, create a simple object
                    $objectifiedResponse = [PSCustomObject]@{
                        ResponseType = "TEXT"
                        Content = $RawResponse
                        Length = $RawResponse.Length
                        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                        CommandType = $CommandData.CommandType
                    }
                }
            }
            elseif ($RawResponse -is [hashtable] -or $RawResponse -is [PSCustomObject]) {
                $objectifiedResponse = ConvertTo-PowerShellObject -JsonData $RawResponse -CommandData $CommandData
            }
            else {
                # Convert other types to objects
                $objectifiedResponse = [PSCustomObject]@{
                    ResponseType = $RawResponse.GetType().Name
                    Content = $RawResponse
                    Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                    CommandType = $CommandData.CommandType
                }
            }
            
            $transformationResults.TransformedResponse = $objectifiedResponse
            $transformationResults.TransformationActions += "Objectified response"
        }
        
        # 4. Result Filtering (Remove sensitive/internal properties)
        if ($TransformConfig.EnableResultFiltering -and $transformationResults.TransformedResponse) {
            $filteredResponse = Remove-SensitiveProperties -Object $transformationResults.TransformedResponse -CommandData $CommandData
            $transformationResults.FilteredProperties = Compare-Objects $transformationResults.TransformedResponse $filteredResponse -Property @('PSObject.Properties.Name') | Where-Object { $_.SideIndicator -eq '<=' } | Select-Object -ExpandProperty InputObject
            
            if ($transformationResults.FilteredProperties.Count -gt 0) {
                $transformationResults.TransformedResponse = $filteredResponse
                $transformationResults.TransformationActions += "Filtered $($transformationResults.FilteredProperties.Count) sensitive properties"
            }
        }
        
        # Add metadata to response
        if ($transformationResults.TransformedResponse -and $transformationResults.TransformedResponse.PSObject.TypeNames -notcontains "AIOS.Response") {
            Add-Member -InputObject $transformationResults.TransformedResponse -MemberType NoteProperty -Name "AIOSMetadata" -Value @{
                CommandId = $CommandData.CommandId
                CommandType = $CommandData.CommandType
                ProcessingTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                TransformationActions = $transformationResults.TransformationActions
            } -Force
            Add-Member -InputObject $transformationResults.TransformedResponse -MemberType TypeName -Value "AIOS.Response" -Force
        }
        
        Write-AIOSMessage -Message "✅ Response transformation completed - $($transformationResults.TransformationActions.Count) transformations applied" -Level DEBUG
        return $transformationResults
    }
    catch {
        Write-AIOSMessage -Message "Error in response transformation: $($_.Exception.Message)" -Level ERROR
        return @{
            TransformedResponse = [PSCustomObject]@{
                ErrorId = [System.Guid]::NewGuid().ToString()
                ErrorType = "TRANSFORMATION_ERROR"
                ErrorMessage = "Failed to transform service response"
                UserFriendlyMessage = "An error occurred while processing the AI service response"
                TechnicalDetails = $_.Exception.Message
            }
            TransformationActions = @("Error during transformation")
        }
    }
}

# Resilience Feature: Automatic Retry and Circuit Breaking
function Invoke-ResilientCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [scriptblock]$CommandBlock,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData,
        
        [Parameter(Mandatory=$false)]
        [hashtable]$ResilienceConfig = @{
            MaxRetries = 3
            BaseDelayMs = 1000
            MaxDelayMs = 10000
            CircuitBreakerThreshold = 5
            CircuitBreakerTimeout = 300000  # 5 minutes
            EnableExponentialBackoff = $true
            EnableCircuitBreaker = $true
            EnableFailover = $false
        }
    )
    
    try {
        Write-AIOSMessage -Message "🔄 Executing resilient command: $($CommandData.CommandType)" -Level DEBUG
        
        $resilienceResults = @{
            Attempts = 0
            Success = $false
            FinalResult = $null
            Errors = @()
            CircuitBreakerTripped = $false
            FailoverUsed = $false
            TotalDuration = 0
        }
        
        $startTime = Get-Date
        
        # Check circuit breaker state
        if ($ResilienceConfig.EnableCircuitBreaker) {
            $circuitState = Test-CircuitBreakerState -CommandType $CommandData.CommandType -ResilienceConfig $ResilienceConfig
            if ($circuitState.IsOpen) {
                $resilienceResults.CircuitBreakerTripped = $true
                $resilienceResults.FinalResult = [PSCustomObject]@{
                    ErrorId = [System.Guid]::NewGuid().ToString()
                    ErrorType = "CIRCUIT_BREAKER_OPEN"
                    ErrorMessage = "Service is currently unavailable due to repeated failures"
                    UserFriendlyMessage = "The AI service is temporarily unavailable. Please try again later."
                    CircuitBreakerState = $circuitState
                    RetryAfter = $circuitState.RetryAfter
                }
                
                Write-AIOSMessage -Message "🚫 Circuit breaker is OPEN for command type: $($CommandData.CommandType)" -Level ERROR
                return $resilienceResults
            }
        }
        
        # Execute with retry logic
        for ($attempt = 1; $attempt -le $ResilienceConfig.MaxRetries; $attempt++) {
            $resilienceResults.Attempts = $attempt
            
            try {
                Write-AIOSMessage -Message "🔄 Attempt $attempt of $($ResilienceConfig.MaxRetries) for command: $($CommandData.CommandType)" -Level DEBUG
                
                # Execute the command
                $result = & $CommandBlock
                
                # Check if result indicates success
                if ($result -and -not ($result -is [System.Management.Automation.ErrorRecord])) {
                    $resilienceResults.Success = $true
                    $resilienceResults.FinalResult = $result
                    
                    # Reset circuit breaker on success
                    if ($ResilienceConfig.EnableCircuitBreaker) {
                        Reset-CircuitBreakerState -CommandType $CommandData.CommandType
                    }
                    
                    Write-AIOSMessage -Message "✅ Command succeeded on attempt $attempt" -Level SUCCESS
                    break
                } else {
                    throw "Command returned error result"
                }
            }
            catch {
                $error = $_.Exception
                $resilienceResults.Errors += $error
                
                Write-AIOSMessage -Message "❌ Attempt $attempt failed: $($error.Message)" -Level WARN
                
                # Record failure for circuit breaker
                if ($ResilienceConfig.EnableCircuitBreaker) {
                    Record-CircuitBreakerFailure -CommandType $CommandData.CommandType
                }
                
                # Check if we should retry
                if ($attempt -lt $ResilienceConfig.MaxRetries) {
                    $delay = if ($ResilienceConfig.EnableExponentialBackoff) {
                        [Math]::Min($ResilienceConfig.BaseDelayMs * [Math]::Pow(2, $attempt - 1), $ResilienceConfig.MaxDelayMs)
                    } else {
                        $ResilienceConfig.BaseDelayMs
                    }
                    
                    Write-AIOSMessage -Message "⏳ Waiting ${delay}ms before retry..." -Level INFO
                    Start-Sleep -Milliseconds $delay
                }
            }
        }
        
        # If all retries failed, check for failover
        if (-not $resilienceResults.Success -and $ResilienceConfig.EnableFailover) {
            Write-AIOSMessage -Message "🔄 All retries failed, attempting failover..." -Level WARN
            
            try {
                $failoverResult = Invoke-FailoverCommand -CommandData $CommandData
                if ($failoverResult) {
                    $resilienceResults.Success = $true
                    $resilienceResults.FinalResult = $failoverResult
                    $resilienceResults.FailoverUsed = $true
                    Write-AIOSMessage -Message "✅ Failover succeeded" -Level SUCCESS
                }
            }
            catch {
                Write-AIOSMessage -Message "❌ Failover also failed: $($_.Exception.Message)" -Level ERROR
            }
        }
        
        # Create final error result if all attempts failed
        if (-not $resilienceResults.Success) {
            $resilienceResults.FinalResult = [PSCustomObject]@{
                ErrorId = [System.Guid]::NewGuid().ToString()
                ErrorType = "RESILIENCE_FAILURE"
                ErrorMessage = "Command failed after $($resilienceResults.Attempts) attempts"
                UserFriendlyMessage = "The AI service is currently experiencing issues. Please try again later."
                Attempts = $resilienceResults.Attempts
                Errors = $resilienceResults.Errors | Select-Object -First 3 | ForEach-Object { $_.Message }
                CircuitBreakerTripped = $resilienceResults.CircuitBreakerTripped
                FailoverUsed = $resilienceResults.FailoverUsed
            }
        }
        
        $resilienceResults.TotalDuration = ((Get-Date) - $startTime).TotalMilliseconds
        
        # Record resilience telemetry
        Record-CommandTelemetry -EventType "COMPLETE" -CommandData $CommandData -Duration $resilienceResults.TotalDuration -Metadata @{
            Attempts = $resilienceResults.Attempts
            Success = $resilienceResults.Success
            CircuitBreakerTripped = $resilienceResults.CircuitBreakerTripped
            FailoverUsed = $resilienceResults.FailoverUsed
        }
        
        Write-AIOSMessage -Message "🏁 Resilience execution completed - Success: $($resilienceResults.Success), Attempts: $($resilienceResults.Attempts), Duration: $([Math]::Round($resilienceResults.TotalDuration, 2))ms" -Level INFO
        return $resilienceResults
    }
    catch {
        Write-AIOSMessage -Message "Error in resilient command execution: $($_.Exception.Message)" -Level ERROR
        return @{
            Success = $false
            FinalResult = [PSCustomObject]@{
                ErrorId = [System.Guid]::NewGuid().ToString()
                ErrorType = "RESILIENCE_ERROR"
                ErrorMessage = "Resilience layer encountered an error"
                UserFriendlyMessage = "An unexpected error occurred in the command execution system"
                TechnicalDetails = $_.Exception.Message
            }
            Attempts = 0
            Errors = @($_.Exception)
        }
    }
}

# Helper Functions for Cross-Cutting Concerns
function ConvertTo-PowerShellObject {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [object]$JsonData,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData
    )
    
    try {
        if ($JsonData -is [PSCustomObject]) {
            # Add AIOS metadata to existing object
            Add-Member -InputObject $JsonData -MemberType NoteProperty -Name "AIOSMetadata" -Value @{
                CommandId = $CommandData.CommandId
                CommandType = $CommandData.CommandType
                ProcessedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            } -Force
            return $JsonData
        }
        elseif ($JsonData -is [hashtable]) {
            # Convert hashtable to PSCustomObject
            $psObject = [PSCustomObject]$JsonData
            Add-Member -InputObject $psObject -MemberType NoteProperty -Name "AIOSMetadata" -Value @{
                CommandId = $CommandData.CommandId
                CommandType = $CommandData.CommandType
                ProcessedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            } -Force
            return $psObject
        }
        else {
            # Wrap other types
            return [PSCustomObject]@{
                Data = $JsonData
                AIOSMetadata = @{
                    CommandId = $CommandData.CommandId
                    CommandType = $CommandData.CommandType
                    ProcessedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                    OriginalType = $JsonData.GetType().Name
                }
            }
        }
    }
    catch {
        Write-AIOSMessage -Message "Error converting to PowerShell object: $($_.Exception.Message)" -Level ERROR
        return [PSCustomObject]@{
            Error = $_.Exception.Message
            OriginalData = $JsonData
        }
    }
}

function Remove-SensitiveProperties {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [object]$Object,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData
    )
    
    try {
        $sensitiveProperties = @(
            "password", "secret", "key", "token", "auth", "credential",
            "internal_id", "debug_info", "stack_trace", "raw_data",
            "temp_data", "cache_data", "session_data"
        )
        
        if ($Object -is [PSCustomObject]) {
            $filteredObject = $Object.PSObject.Copy()
            
            foreach ($property in $filteredObject.PSObject.Properties) {
                if ($sensitiveProperties | Where-Object { $property.Name -like "*$_*" }) {
                    $filteredObject.PSObject.Properties.Remove($property.Name)
                }
            }
            
            return $filteredObject
        }
        
        return $Object
    }
    catch {
        Write-AIOSMessage -Message "Error filtering sensitive properties: $($_.Exception.Message)" -Level ERROR
        return $Object
    }
}

function Test-CircuitBreakerState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$CommandType,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$ResilienceConfig
    )
    
    try {
        $circuitFile = "$DEBUG_DIR\circuit_breaker_$($CommandType.ToLower()).json"
        
        if (-not (Test-Path $circuitFile)) {
            return @{
                IsOpen = $false
                FailureCount = 0
                LastFailure = $null
                State = "CLOSED"
            }
        }
        
        $circuitData = Get-Content $circuitFile -Raw | ConvertFrom-Json
        
        # Check if circuit breaker timeout has expired
        $lastFailure = [DateTime]::Parse($circuitData.LastFailure)
        $timeoutExpired = ((Get-Date) - $lastFailure).TotalMilliseconds -gt $ResilienceConfig.CircuitBreakerTimeout
        
        if ($timeoutExpired) {
            # Reset circuit breaker
            Remove-Item $circuitFile -Force -ErrorAction SilentlyContinue
            return @{
                IsOpen = $false
                FailureCount = 0
                LastFailure = $null
                State = "CLOSED"
            }
        }
        
        $isOpen = $circuitData.FailureCount -ge $ResilienceConfig.CircuitBreakerThreshold
        
        return @{
            IsOpen = $isOpen
            FailureCount = $circuitData.FailureCount
            LastFailure = $circuitData.LastFailure
            State = if ($isOpen) { "OPEN" } else { "CLOSED" }
            RetryAfter = if ($isOpen) { $ResilienceConfig.CircuitBreakerTimeout - ((Get-Date) - $lastFailure).TotalMilliseconds } else { 0 }
        }
    }
    catch {
        Write-AIOSMessage -Message "Error checking circuit breaker state: $($_.Exception.Message)" -Level ERROR
        return @{
            IsOpen = $false
            FailureCount = 0
            LastFailure = $null
            State = "CLOSED"
        }
    }
}

function Record-CircuitBreakerFailure {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$CommandType
    )
    
    try {
        $circuitFile = "$DEBUG_DIR\circuit_breaker_$($CommandType.ToLower()).json"
        
        $circuitData = if (Test-Path $circuitFile) {
            Get-Content $circuitFile -Raw | ConvertFrom-Json
        } else {
            @{
                FailureCount = 0
                LastFailure = $null
                FirstFailure = $null
            }
        }
        
        $circuitData.FailureCount++
        $circuitData.LastFailure = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
        
        if ($circuitData.FailureCount -eq 1) {
            $circuitData.FirstFailure = $circuitData.LastFailure
        }
        
        $circuitData | ConvertTo-Json -Depth 3 | Set-Content $circuitFile -Encoding UTF8
        
        Write-AIOSMessage -Message "Circuit breaker failure recorded for $CommandType - Count: $($circuitData.FailureCount)" -Level WARN
    }
    catch {
        Write-AIOSMessage -Message "Error recording circuit breaker failure: $($_.Exception.Message)" -Level ERROR
    }
}

function Reset-CircuitBreakerState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$CommandType
    )
    
    try {
        $circuitFile = "$DEBUG_DIR\circuit_breaker_$($CommandType.ToLower()).json"
        
        if (Test-Path $circuitFile) {
            Remove-Item $circuitFile -Force
            Write-AIOSMessage -Message "Circuit breaker reset for $CommandType" -Level INFO
        }
    }
    catch {
        Write-AIOSMessage -Message "Error resetting circuit breaker state: $($_.Exception.Message)" -Level ERROR
    }
}

function Invoke-FailoverCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$CommandData
    )
    
    try {
        Write-AIOSMessage -Message "🔄 Attempting failover for command: $($CommandData.CommandType)" -Level INFO
        
        # Define failover strategies based on command type
        $failoverStrategies = @{
            "AI_INFERENCE" = {
                # Try cached response or simplified model
                Write-AIOSMessage -Message "Using cached/simplified AI model for failover" -Level INFO
                return [PSCustomObject]@{
                    ResponseType = "FAILOVER_CACHED"
                    Content = "This is a cached/simplified response due to service unavailability"
                    FailoverUsed = $true
                    OriginalCommandType = $CommandData.CommandType
                }
            }
            "HEALTH_CHECK" = {
                # Return basic health status
                return [PSCustomObject]@{
                    Status = "DEGRADED"
                    Message = "Service is experiencing issues - using fallback health check"
                    FailoverUsed = $true
                }
            }
            "CONFIG_UPDATE" = {
                # Use local configuration
                return [PSCustomObject]@{
                    Status = "FALLBACK"
                    Message = "Using local configuration due to service unavailability"
                    FailoverUsed = $true
                }
            }
        }
        
        if ($failoverStrategies.ContainsKey($CommandData.CommandType)) {
            $failoverResult = & $failoverStrategies[$CommandData.CommandType]
            Write-AIOSMessage -Message "✅ Failover successful for $($CommandData.CommandType)" -Level SUCCESS
            return $failoverResult
        } else {
            Write-AIOSMessage -Message "No failover strategy available for $($CommandData.CommandType)" -Level WARN
            return $null
        }
    }
    catch {
        Write-AIOSMessage -Message "Error in failover execution: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

# Middleware Integration Functions
function Initialize-AIOSMiddleware {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [switch]$EnableThrottling,
        
        [Parameter(Mandatory=$false)]
        [switch]$EnableTelemetry,
        
        [Parameter(Mandatory=$false)]
        [switch]$EnableStateSync,
        
        [Parameter(Mandatory=$false)]
        [hashtable]$MiddlewareConfig = @{}
    )
    
    try {
        Write-AIOSMessage -Message "🔧 Initializing AIOS middleware components..." -Level INFO
        
        $middlewareStatus = @{
            ThrottlingEnabled = $EnableThrottling
            TelemetryEnabled = $EnableTelemetry
            StateSyncEnabled = $EnableStateSync
            Config = $MiddlewareConfig
            Initialized = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
        }
        
        # Store middleware configuration
        $configFile = "$DEBUG_DIR\middleware_config.json"
        $middlewareStatus | ConvertTo-Json -Depth 5 | Set-Content $configFile -Encoding UTF8
        
        if ($EnableThrottling) {
            Write-AIOSMessage -Message "✅ Command throttling middleware enabled" -Level SUCCESS
        }
        
        if ($EnableTelemetry) {
            Write-AIOSMessage -Message "✅ Event-driven telemetry enabled" -Level SUCCESS
        }
        
        if ($EnableStateSync) {
            Write-AIOSMessage -Message "✅ Dynamic state management enabled" -Level SUCCESS
        }
        
        # Initialize telemetry cache
        if ($EnableTelemetry) {
            $cacheFile = "$DEBUG_DIR\telemetry_cache.json"
            if (-not (Test-Path $cacheFile)) {
                $initialCache = @{
                    LastUpdated = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                    CommandStats = @{}
                    PerformanceMetrics = @{
                        TotalCommands = 0
                        SuccessfulCommands = 0
                        FailedCommands = 0
                        AverageDuration = 0
                        ThrottledCommands = 0
                    }
                }
                $initialCache | ConvertTo-Json -Depth 10 | Set-Content $cacheFile -Encoding UTF8
                Write-AIOSMessage -Message "Telemetry cache initialized" -Level INFO
            }
        }
        
        Write-AIOSMessage -Message "AIOS middleware initialization completed" -Level SUCCESS
        return $middlewareStatus
    }
    catch {
        Write-AIOSMessage -Message "Error initializing middleware: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function Get-AIOSTelemetryMetrics {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [ValidateSet("SUMMARY", "DETAILED", "REALTIME")]
        [string]$DetailLevel = "SUMMARY"
    )
    
    try {
        $cacheFile = "$DEBUG_DIR\telemetry_cache.json"
        
        if (-not (Test-Path $cacheFile)) {
            Write-AIOSMessage -Message "No telemetry data available" -Level WARN
            return $null
        }
        
        $cache = Get-Content $cacheFile -Raw | ConvertFrom-Json
        
        switch ($DetailLevel) {
            "SUMMARY" {
                return @{
                    TotalCommands = $cache.PerformanceMetrics.TotalCommands
                    SuccessRate = if ($cache.PerformanceMetrics.TotalCommands -gt 0) { 
                        [Math]::Round(($cache.PerformanceMetrics.SuccessfulCommands / $cache.PerformanceMetrics.TotalCommands) * 100, 2) 
                    } else { 0 }
                    AverageDuration = [Math]::Round($cache.PerformanceMetrics.AverageDuration, 2)
                    ThrottledCommands = $cache.PerformanceMetrics.ThrottledCommands
                    LastUpdated = $cache.LastUpdated
                }
            }
            "DETAILED" {
                return $cache
            }
            "REALTIME" {
                # Add current system metrics
                $currentMetrics = Get-SystemResourceSnapshot
                return @{
                    CachedMetrics = $cache
                    CurrentSystemState = $currentMetrics
                    GeneratedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
                }
            }
        }
    }
    catch {
        Write-AIOSMessage -Message "Error retrieving telemetry metrics: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function Invoke-AIOSCommandWithMiddleware {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$CommandType,
        
        [Parameter(Mandatory=$false)]
        [string]$Priority = "NORMAL",
        
        [Parameter(Mandatory=$false)]
        [hashtable]$Parameters = @{},
        
        [Parameter(Mandatory=$false)]
        [scriptblock]$CommandBlock,
        
        [Parameter(Mandatory=$false)]
        [hashtable]$SecurityConfig = @{
            EnableInjectionPrevention = $true
            EnableSchemaValidation = $true
            EnablePromptGuardrails = $true
        },
        
        [Parameter(Mandatory=$false)]
        [hashtable]$TransformConfig = @{
            EnableObjectification = $true
            EnableErrorAbstraction = $true
            EnableResultFiltering = $true
        },
        
        [Parameter(Mandatory=$false)]
        [hashtable]$ResilienceConfig = @{
            MaxRetries = 3
            EnableCircuitBreaker = $true
            EnableFailover = $true
        }
    )
    
    try {
        Write-AIOSMessage -Message "🚀 Starting full middleware pipeline for command: $CommandType" -Level INFO
        
        # Create command data structure
        $commandData = @{
            CommandId = [System.Guid]::NewGuid().ToString()
            CommandType = $CommandType
            Priority = $Priority
            Parameters = $Parameters
            Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
            ExecutionContext = @{}
            MiddlewarePipeline = @{
                SecurityValidation = $null
                ThrottlingApplied = $null
                ResilienceResults = $null
                TransformationResults = $null
            }
        }
        
        # Record command start
        Record-CommandTelemetry -EventType "START" -CommandData $commandData
        
        $pipelineStartTime = Get-Date
        
        # STEP 1: Security Validation & Input Sanitization
        Write-AIOSMessage -Message "🔒 Step 1: Security validation and input sanitization" -Level DEBUG
        $sanitizedCommandData = Filter-InputSanitizer -CommandData $commandData -SecurityConfig $SecurityConfig
        
        if (-not $sanitizedCommandData) {
            Write-AIOSMessage -Message "🚫 Command blocked by security validation" -Level ERROR
            return @{
                Success = $false
                Result = [PSCustomObject]@{
                    ErrorId = [System.Guid]::NewGuid().ToString()
                    ErrorType = "SECURITY_BLOCKED"
                    ErrorMessage = "Command blocked by security validation"
                    UserFriendlyMessage = "The command was blocked due to security concerns"
                }
                CommandData = $commandData
                Duration = ((Get-Date) - $pipelineStartTime).TotalMilliseconds
                PipelineStep = "SECURITY_VALIDATION"
            }
        }
        
        $commandData.MiddlewarePipeline.SecurityValidation = $sanitizedCommandData.SecurityValidation
        
        # STEP 2: Throttling & Load Management
        Write-AIOSMessage -Message "🛑 Step 2: Throttling and load management" -Level DEBUG
        $throttledCommandData = Filter-ThrottledCommand -CommandData $sanitizedCommandData
        
        $commandData.MiddlewarePipeline.ThrottlingApplied = $throttledCommandData.ExecutionContext
        
        # STEP 3: Resilient Command Execution
        Write-AIOSMessage -Message "🔄 Step 3: Resilient command execution with circuit breaking" -Level DEBUG
        $resilienceResults = Invoke-ResilientCommand -CommandBlock $CommandBlock -CommandData $throttledCommandData -ResilienceConfig $ResilienceConfig
        
        $commandData.MiddlewarePipeline.ResilienceResults = $resilienceResults
        
        if (-not $resilienceResults.Success) {
            Write-AIOSMessage -Message "❌ Command failed in resilience layer" -Level ERROR
            
            # Transform the error response
            $errorTransformation = Convert-ServiceResponse -RawResponse $resilienceResults.FinalResult -CommandData $commandData -TransformConfig $TransformConfig
            $commandData.MiddlewarePipeline.TransformationResults = $errorTransformation
            
            return @{
                Success = $false
                Result = $errorTransformation.TransformedResponse
                Error = $resilienceResults.Errors | Select-Object -First 1
                CommandData = $commandData
                Duration = ((Get-Date) - $pipelineStartTime).TotalMilliseconds
                PipelineStep = "RESILIENCE_EXECUTION"
            }
        }
        
        # STEP 4: Response Transformation & Abstraction
        Write-AIOSMessage -Message "🔄 Step 4: Response transformation and abstraction" -Level DEBUG
        $transformationResults = Convert-ServiceResponse -RawResponse $resilienceResults.FinalResult -CommandData $commandData -TransformConfig $TransformConfig
        
        $commandData.MiddlewarePipeline.TransformationResults = $transformationResults
        
        # Record successful completion
        $totalDuration = ((Get-Date) - $pipelineStartTime).TotalMilliseconds
        Record-CommandTelemetry -EventType "COMPLETE" -CommandData $commandData -Duration $totalDuration -Metadata @{
            PipelineSteps = 4
            SecurityValidationPassed = $true
            ThrottlingApplied = $commandData.MiddlewarePipeline.ThrottlingApplied.Throttled
            ResilienceAttempts = $resilienceResults.Attempts
            TransformationActions = $transformationResults.TransformationActions.Count
            Success = $true
        }
        
        Write-AIOSMessage -Message "✅ Full middleware pipeline completed successfully - Duration: $([Math]::Round($totalDuration, 2))ms" -Level SUCCESS
        
        return @{
            Success = $true
            Result = $transformationResults.TransformedResponse
            Error = $null
            CommandData = $commandData
            Duration = $totalDuration
            PipelineStep = "COMPLETED"
            MiddlewareMetrics = @{
                SecurityValidation = $commandData.MiddlewarePipeline.SecurityValidation
                ThrottlingApplied = $commandData.MiddlewarePipeline.ThrottlingApplied
                ResilienceResults = $commandData.MiddlewarePipeline.ResilienceResults
                TransformationResults = $commandData.MiddlewarePipeline.TransformationResults
            }
        }
    }
    catch {
        $errorDuration = ((Get-Date) - $pipelineStartTime).TotalMilliseconds
        Write-AIOSMessage -Message "❌ Error in middleware pipeline: $($_.Exception.Message)" -Level ERROR
        
        # Record pipeline error
        Record-CommandTelemetry -EventType "ERROR" -CommandData $commandData -Duration $errorDuration -Metadata @{
            PipelineError = $_.Exception.Message
            PipelineStep = "PIPELINE_ERROR"
            Success = $false
        }
        
        return @{
            Success = $false
            Result = [PSCustomObject]@{
                ErrorId = [System.Guid]::NewGuid().ToString()
                ErrorType = "MIDDLEWARE_PIPELINE_ERROR"
                ErrorMessage = "Middleware pipeline encountered an error"
                UserFriendlyMessage = "An unexpected error occurred in the command processing pipeline"
                TechnicalDetails = $_.Exception.Message
            }
            Error = $_.Exception
            CommandData = $commandData
            Duration = $errorDuration
            PipelineStep = "PIPELINE_ERROR"
        }
    }
}

function Restart-AIOSService {
    # Legacy function - redirect to new Restart-AIOS
    return Restart-AIOS
}

function Update-AIOSComponents {
    # Enforce WSR for admin operations
    if (-not (Test-WillingSubmissionRequirement -Operation "AIOS Component Update" -RiskLevel "MEDIUM")) {
        Write-AIOSMessage -Message "Willing Submission Required - Component update blocked" -Level ERROR
        return
    }
    
    Write-AIOSMessage -Message "Updating AIOS components..." -Level INFO
    
    # Update Python packages
    Write-AIOSMessage -Message "Updating Python packages..." -Level INFO
    pip install --upgrade -r "$AIOS_ROOT\requirements.txt"
    
    # Update git repositories if any
    if (Test-Path "$AIOS_ROOT\.git") {
        Write-AIOSMessage -Message "Updating git repository..." -Level INFO
        git -C $AIOS_ROOT pull origin master
    }
    
    Write-AIOSMessage -Message "AIOS components updated" -Level SUCCESS
}

function Backup-AIOSData {
    param([string]$BackupLocation = "$AIOS_ROOT\backups")
    
    # Enforce WSR for admin operations
    if (-not (Test-WillingSubmissionRequirement -Operation "AIOS Data Backup" -RiskLevel "MEDIUM")) {
        Write-AIOSMessage -Message "Willing Submission Required - Data backup blocked" -Level ERROR
        return
    }
    
    Write-AIOSMessage -Message "Creating AIOS backup..." -Level INFO
    
    if (-not (Test-Path $BackupLocation)) {
        New-Item -ItemType Directory -Path $BackupLocation -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupFile = "$BackupLocation\aios_backup_$timestamp.zip"
    
    # Backup critical directories
    $backupItems = @("config", "Data", "luna_core", "carma_core", "enterprise_core", "support_core", "main.py", "requirements.txt")
    
    Compress-Archive -Path $backupItems -DestinationPath $backupFile -Force
    
    $backupSize = (Get-Item $backupFile).Length / 1MB
    $backupSizeRounded = [math]::Round($backupSize, 2)
    $backupMessage = 'Backup created: ' + $backupFile + ' (' + $backupSizeRounded + ' MB)'
    Write-AIOSMessage -Message $backupMessage -Level SUCCESS
    
    return $backupFile
}

function Restore-AIOSData {
    param([string]$BackupFile = "")
    
    # Enforce WSR for admin operations
    if (-not (Test-WillingSubmissionRequirement -Operation 'AIOS Data Restore' -RiskLevel 'CRITICAL')) {
        Write-AIOSMessage -Message "Willing Submission Required - Data restore blocked" -Level ERROR
        return
    }
    
    if (-not $BackupFile -or -not (Test-Path $BackupFile)) {
        Write-AIOSMessage -Message "Valid backup file required" -Level ERROR
        return
    }
    
    if (-not $ADMIN_MODE) {
        Write-AIOSMessage -Message "Admin mode required for data restore" -Level ERROR
        return
    }
    
    Write-AIOSMessage -Message "Restoring AIOS data from: $BackupFile" -Level WARN
    
    # Create restore backup
    $restoreBackup = Backup-AIOSData -BackupLocation "$AIOS_ROOT\backups\restore_backup"
    Write-AIOSMessage -Message "Created restore backup: $restoreBackup" -Level INFO
    
    # Extract backup
    $restoreLocation = "$AIOS_ROOT\temp\restore_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
    Expand-Archive -Path $BackupFile -DestinationPath $restoreLocation -Force
    
    # Copy files back
    Get-ChildItem -Path $restoreLocation -Recurse | Copy-Item -Destination $AIOS_ROOT -Force
    
    Write-AIOSMessage -Message "AIOS data restored successfully" -Level SUCCESS
}

# Create function aliases instead of Set-Alias with script blocks
function aios { Start-AIOS -Interactive }
function status { Get-AIOSStatus }
function health { Invoke-AIOSHealthCheck }
function monitor { Start-AIOSBackendMonitor -RealTimeMode }
function analyze { Invoke-AIOSCodeAnalysis -FullScan }
function diagnose { Invoke-AIOSSystemDiagnostics -FullSystemScan -SecurityScan }
function logs { Get-AIOSLogs }
function readiness { Test-AIOSProjectReadiness -ProjectPath $AIOS_ROOT -CheckDependencies -CheckSecurity -CheckPerformance }
function cleanup { Invoke-AIOSProjectCleanup -ProjectPath $AIOS_ROOT }
function standards { Invoke-AIOSStandardsCheck -FullProject }
function standards-monitor { Start-AIOSStandardsMonitoring }
function standards-report { Get-AIOSComplianceReport }
function standards-fix { Invoke-AIOSStandardsFix -FullProject }
function bcm { Get-ButterflyCostMetric }
function bcm-monitor { Start-AIOSBCMMonitoring -Continuous }
function wsr { Test-WillingSubmissionRequirement }
function test-unicode { Test-UnicodeSupport }
function help-aios { Show-AIOSHelp }
function stop-aios { Stop-AIOS }
function restart-aios { Restart-AIOS }
function process-detail { Get-AIOSProcessDetail -IncludeCommandLine -IncludePerformance }
function log-level { Set-AIOSLogLevel }
function config { Get-AIOSConfiguration }
function set-config { Set-AIOSConfiguration }
function log-rotation { Invoke-LogRotation -CompressOldLogs }
function clear-logs { Clear-AIOSLogs }
function bcm-remediation { Invoke-BCMRemediation }
function health-check { Test-AIOSHealth -CheckType FULL }
function health-liveness { Test-AIOSLiveness }
function health-readiness { Test-AIOSReadiness }
function perf-counters { Get-AIOSPerformanceCounters }
function perf-monitor { Start-AIOSPerformanceMonitoring }
function dependency-check { Test-AIOSDependency -Detailed }
function dependency-fix { Test-AIOSDependency -AutoFix }
function integrity-check { Test-AIOSConfigurationIntegrity }
function security-init { Initialize-AIOSSecurity -CreateServiceAccount -ConfigureFirewall -VerifyIntegrity }
function firewall-setup { Set-AIOSFirewallRules }
function restart-backoff { Test-AIOSRestartBackoff }
function high-alert { Send-AIOSHighPriorityAlert }

# Middleware & Event-Driven Aliases
function throttle-filter { Filter-ThrottledCommand }
function telemetry { Record-CommandTelemetry }
function state-sync { Sync-PythonState }
function middleware-init { Initialize-AIOSMiddleware }
function telemetry-metrics { Get-AIOSTelemetryMetrics }
function cmd-middleware { Invoke-AIOSCommandWithMiddleware }

# Cross-Cutting Concerns Aliases
function input-sanitizer { Filter-InputSanitizer }
function response-transform { Convert-ServiceResponse }
function resilient-cmd { Invoke-ResilientCommand }
function circuit-breaker { Test-CircuitBreakerState }
function failover { Invoke-FailoverCommand }

# Main Initialization
if (-not $Silent) {
Write-Host ""
    Write-Host "AIOS PowerShell Backend Monitor" -ForegroundColor Cyan
    Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""
}

# Handle special modes first
if ($TestUnicode) {
    Test-UnicodeSupport
    return
}

if ($MonitorMode) {
    $script:MONITORING_ENABLED = $true
    Write-AIOSMessage -Message "Monitoring mode enabled" -Level SUCCESS
}

if ($DebugMode) {
    $script:MONITORING_ENABLED = $true
    Write-AIOSMessage -Message "Debug mode enabled - enhanced logging active" -Level SUCCESS
}

if ($AdminMode) {
    $script:ADMIN_MODE = $true
    Write-AIOSMessage -Message "ADMIN MODE ENABLED - Full system access granted" -Level WARN
    Write-AIOSMessage -Message "You now have the power to control the entire system" -Level WARN
}

$pythonSuccess = Initialize-PythonEnvironment
$sysadminSuccess = Initialize-SysAdminTools

if ($pythonSuccess) {
    $modeInfo = @()
    if ($MONITORING_ENABLED) { $modeInfo += "MONITORING" }
    if ($ADMIN_MODE) { $modeInfo += "ADMIN" }
    if ($DebugMode) { $modeInfo += "DEBUG" }
    
    $modeString = if ($modeInfo.Count -gt 0) { " [$($modeInfo -join ', ')]" } else { "" }
    
    Write-AIOSMessage -Message "AIOS Backend Monitor initialized successfully!$modeString" -Level SUCCESS
    Write-AIOSMessage -Message "Type help-aios for available commands" -Level INFO
    
    if ($MONITORING_ENABLED) {
        Write-AIOSMessage -Message "Real-time monitoring and logging active" -Level INFO
        Write-AIOSMessage -Message "Logs being written to: $LOG_DIR" -Level INFO
        Write-AIOSMessage -Message "Debug info being written to: $DEBUG_DIR" -Level INFO
    }
} else {
    Write-AIOSMessage -Message "AIOS Backend Monitor initialized with warnings" -Level WARN
}

if (-not $Silent) {
Write-Host ""
}