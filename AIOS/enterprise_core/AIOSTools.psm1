
# AIOSTools PowerShell Module
# Advanced AIOS system management functions

function Test-AIOSProjectReadiness {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        
        [Parameter(Mandatory=$false)]
        [switch]$CheckDependencies,
        
        [Parameter(Mandatory=$false)]
        [switch]$CheckSecurity
    )
    
    Write-Verbose "Starting AIOS project readiness check..."
    
    $readiness = @{
        ProjectPath = $ProjectPath
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        Checks = @{}
        OverallStatus = "Unknown"
    }
    
    # Check core files
    $coreFiles = @("main.py", "requirements.txt", "aios_powershell_wrapper.ps1")
    foreach ($file in $coreFiles) {
        $fullPath = Join-Path $ProjectPath $file
        $exists = Test-Path $fullPath
        $readiness.Checks["CoreFile_$file"] = @{
            Path = $fullPath
            Exists = $exists
            Status = if ($exists) { "OK" } else { "MISSING" }
        }
    }
    
    # Check core directories
    $coreDirs = @("luna_core", "carma_core", "enterprise_core", "support_core", "config", "Data")
    foreach ($dir in $coreDirs) {
        $fullPath = Join-Path $ProjectPath $dir
        $exists = Test-Path $fullPath
        $readiness.Checks["CoreDir_$dir"] = @{
            Path = $fullPath
            Exists = $exists
            Status = if ($exists) { "OK" } else { "MISSING" }
        }
    }
    
    # Check Python environment
    $venvPath = Join-Path $ProjectPath "venv"
    $pythonExists = Test-Path (Join-Path $venvPath "Scripts\python.exe")
    $readiness.Checks["PythonEnvironment"] = @{
        Path = $venvPath
        Exists = $pythonExists
        Status = if ($pythonExists) { "OK" } else { "MISSING" }
    }
    
    # Check dependencies if requested
    if ($CheckDependencies) {
        $reqFile = Join-Path $ProjectPath "requirements.txt"
        if (Test-Path $reqFile) {
            $readiness.Checks["Dependencies"] = @{
                RequirementsFile = $reqFile
                Status = "FOUND"
            }
        } else {
            $readiness.Checks["Dependencies"] = @{
                RequirementsFile = $reqFile
                Status = "MISSING"
            }
        }
    }
    
    # Security check if requested
    if ($CheckSecurity) {
        $suspiciousPatterns = @("*.tmp", "*.temp", "*.exe.tmp")
        $suspiciousFiles = @()
        
        foreach ($pattern in $suspiciousPatterns) {
            $files = Get-ChildItem -Path $ProjectPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
            if ($files) {
                $suspiciousFiles += $files.FullName
            }
        }
        
        $readiness.Checks["Security"] = @{
            SuspiciousFiles = $suspiciousFiles
            Status = if ($suspiciousFiles.Count -eq 0) { "CLEAN" } else { "SUSPICIOUS" }
        }
    }
    
    # Calculate overall status
    $failedChecks = ($readiness.Checks.Values | Where-Object { $_.Status -ne "OK" -and $_.Status -ne "FOUND" -and $_.Status -ne "CLEAN" }).Count
    $totalChecks = $readiness.Checks.Count
    
    if ($failedChecks -eq 0) {
        $readiness.OverallStatus = "READY"
    } elseif ($failedChecks -le ($totalChecks * 0.3)) {
        $readiness.OverallStatus = "WARNING"
    } else {
        $readiness.OverallStatus = "CRITICAL"
    }
    
    return $readiness
}

function Invoke-AIOSProjectCleanup {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath
    )
    
    if ($PSCmdlet.ShouldProcess("Clean up AIOS project at '$ProjectPath'")) {
        Write-Verbose "Starting AIOS project cleanup..."
        
        $cleanupResults = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            ProjectPath = $ProjectPath
            CleanedItems = @()
            Errors = @()
        }
        
        # Clean temporary files
        $tempPatterns = @("*.pyc", "__pycache__", "*.tmp", "*.temp", ".pytest_cache")
        
        foreach ($pattern in $tempPatterns) {
            try {
                $items = Get-ChildItem -Path $ProjectPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
                foreach ($item in $items) {
                    if ($item.PSIsContainer) {
                        Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    } else {
                        Remove-Item -Path $item.FullName -Force -ErrorAction SilentlyContinue
                    }
                    $cleanupResults.CleanedItems += $item.FullName
                }
            } catch {
                $cleanupResults.Errors += "Failed to clean $pattern : $($_.Exception.Message)"
            }
        }
        
        # Clean old log files (older than 7 days)
        $logDir = Join-Path $ProjectPath "log"
        if (Test-Path $logDir) {
            try {
                $oldLogs = Get-ChildItem -Path $logDir -Recurse -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
                foreach ($log in $oldLogs) {
                    Remove-Item -Path $log.FullName -Force -ErrorAction SilentlyContinue
                    $cleanupResults.CleanedItems += $log.FullName
                }
            } catch {
                $cleanupResults.Errors += "Failed to clean old logs: $($_.Exception.Message)"
            }
        }
        
        return $cleanupResults
    }
}

Export-ModuleMember -Function Test-AIOSProjectReadiness, Invoke-AIOSProjectCleanup
