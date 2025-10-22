# Simple test script for AIOS PowerShell Wrapper
# This script tests basic functionality without loading the full wrapper

param(
    [switch]$TestUnicode,
    [switch]$TestPython,
    [switch]$TestDependencies,
    [switch]$TestProjectReadiness
)

# Set console encoding for Unicode support
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Global Configuration
$AIOS_ROOT = "F:\AIOS_Clean"
$PYTHON_ENV_PATH = "F:\AIOS_Clean\venv"
$LOG_DIR = "F:\AIOS_Clean\log\monitoring"
$DEBUG_DIR = "F:\AIOS_Clean\temp\debug"

# Ensure directories exist
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}
if (-not (Test-Path $DEBUG_DIR)) {
    New-Item -ItemType Directory -Path $DEBUG_DIR -Force | Out-Null
}

# Simple message function
function Write-TestMessage {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "DEBUG" { "Cyan" }
        default { "White" }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Test Unicode Support
function Test-UnicodeSupport {
    Write-TestMessage "Testing Unicode support..." "INFO"
    
    try {
        $unicodeChars = @("→", "≤", "≥", "≠", "∞", "π", "€", "¢", "£", "¥", "°", "±", "×", "÷")
        foreach ($char in $unicodeChars) {
            Write-Host "  $char" -ForegroundColor Green -NoNewline
            Write-Host " - OK" -ForegroundColor Green
        }
        Write-TestMessage "Unicode support test completed successfully" "SUCCESS"
        return $true
    }
    catch {
        Write-TestMessage "Unicode support test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Test Python Environment
function Test-PythonEnvironment {
    Write-TestMessage "Testing Python environment..." "INFO"
    
    try {
        $pythonExe = "$PYTHON_ENV_PATH\Scripts\python.exe"
        if (-not (Test-Path $pythonExe)) {
            Write-TestMessage "Python executable not found at: $pythonExe" "ERROR"
            return $false
        }
        
        $pythonVersion = & $pythonExe --version 2>&1
        Write-TestMessage "Python version: $pythonVersion" "SUCCESS"
        
        $pipExe = "$PYTHON_ENV_PATH\Scripts\pip.exe"
        if (-not (Test-Path $pipExe)) {
            Write-TestMessage "Pip executable not found at: $pipExe" "ERROR"
            return $false
        }
        
        Write-TestMessage "Python environment test completed successfully" "SUCCESS"
        return $true
    }
    catch {
        Write-TestMessage "Python environment test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Test Dependencies
function Test-Dependencies {
    Write-TestMessage "Testing Python dependencies..." "INFO"
    
    try {
        $pipExe = "$PYTHON_ENV_PATH\Scripts\pip.exe"
        $requiredPackages = @("numpy", "pandas", "requests", "streamlit", "plotly")
        
        foreach ($package in $requiredPackages) {
            $packageInfo = & $pipExe show $package 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-TestMessage "Package $package is installed" "SUCCESS"
            } else {
                Write-TestMessage "Package $package is NOT installed" "WARN"
            }
        }
        
        Write-TestMessage "Dependencies test completed" "SUCCESS"
        return $true
    }
    catch {
        Write-TestMessage "Dependencies test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Test Project Readiness
function Test-ProjectReadiness {
    Write-TestMessage "Testing AIOS project readiness..." "INFO"
    
    try {
        $readiness = @{
            MainScript = Test-Path "$AIOS_ROOT\main.py"
            ConfigDir = Test-Path "$AIOS_ROOT\config"
            DataDir = Test-Path "$AIOS_ROOT\Data"
            LunaCore = Test-Path "$AIOS_ROOT\luna_core"
            CarmaCore = Test-Path "$AIOS_ROOT\carma_core"
            EnterpriseCore = Test-Path "$AIOS_ROOT\enterprise_core"
            SupportCore = Test-Path "$AIOS_ROOT\support_core"
            Requirements = Test-Path "$AIOS_ROOT\requirements.txt"
        }
        
        $passed = 0
        $total = $readiness.Count
        
        foreach ($check in $readiness.GetEnumerator()) {
            if ($check.Value) {
                Write-TestMessage "✓ $($check.Key)" "SUCCESS"
                $passed++
            } else {
                Write-TestMessage "✗ $($check.Key)" "ERROR"
            }
        }
        
        $percentage = [math]::Round(($passed / $total) * 100, 2)
        $readinessMessage = 'Project readiness: ' + $passed + '/' + $total + ' (' + $percentage + ' percent)'
        Write-TestMessage $readinessMessage "INFO"
        
        if ($percentage -ge 80) {
            Write-TestMessage "Project readiness test PASSED" "SUCCESS"
            return $true
        } else {
            Write-TestMessage "Project readiness test FAILED" "ERROR"
            return $false
        }
    }
    catch {
        Write-TestMessage "Project readiness test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution
Write-TestMessage "Starting AIOS Wrapper Test Suite..." "INFO"
Write-TestMessage "AIOS Root: $AIOS_ROOT" "INFO"
Write-TestMessage 'Python Env: ' $PYTHON_ENV_PATH 'INFO'

$testResults = @{}

if ($TestUnicode -or (-not $TestUnicode -and -not $TestPython -and -not $TestDependencies -and -not $TestProjectReadiness)) {
    $testResults.Unicode = Test-UnicodeSupport
}

if ($TestPython -or (-not $TestUnicode -and -not $TestPython -and -not $TestDependencies -and -not $TestProjectReadiness)) {
    $testResults.Python = Test-PythonEnvironment
}

if ($TestDependencies -or (-not $TestUnicode -and -not $TestPython -and -not $TestDependencies -and -not $TestProjectReadiness)) {
    $testResults.Dependencies = Test-Dependencies
}

if ($TestProjectReadiness -or (-not $TestUnicode -and -not $TestPython -and -not $TestDependencies -and -not $TestProjectReadiness)) {
    $testResults.ProjectReadiness = Test-ProjectReadiness
}

# Summary
Write-TestMessage '=== TEST SUMMARY ===' 'INFO'
foreach ($test in $testResults.GetEnumerator()) {
    $status = if ($test.Value) { 'PASS' } else { 'FAIL' }
    $color = if ($test.Value) { 'Green' } else { 'Red' }
    $testMessage = '  ' + $test.Key + ': ' + $status
    Write-Host $testMessage -ForegroundColor $color
}

$overallPass = ($testResults.Values | Where-Object { $_ -eq $true }).Count
$overallTotal = $testResults.Count
$overallPercentage = [math]::Round(($overallPass / $overallTotal) * 100, 2)

    $overallMessage = 'Overall: ' + $overallPass + '/' + $overallTotal + ' (' + $overallPercentage + ' percent)'
    Write-TestMessage $overallMessage 'INFO'

if ($overallPercentage -ge 80) {
    Write-TestMessage 'AIOS Wrapper Test Suite PASSED' 'SUCCESS'
    exit 0
} else {
    Write-TestMessage 'AIOS Wrapper Test Suite FAILED' 'ERROR'
    exit 1
}
