# AIOS Learning System Launcher for PowerShell 7+
# This script is optimized for PowerShell 7+ with better terminal support

param(
    [switch]$Interactive = $true,
    [string]$Subject = "",
    [string]$Difficulty = "beginner"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AIOS LEARNING SYSTEM - PowerShell 7+ Enhanced" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion
Write-Host "PowerShell Version: $($psVersion.ToString())" -ForegroundColor Green

if ($psVersion.Major -lt 7) {
    Write-Host "WARNING: This script is optimized for PowerShell 7+" -ForegroundColor Yellow
    Write-Host "Download PowerShell 7+ from: https://github.com/PowerShell/PowerShell/releases" -ForegroundColor Cyan
    Write-Host ""
}

# Change to the AIOS directory
Set-Location "F:\AIOS_Clean"

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python Version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python and ensure it's in your PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting AIOS Learning System..." -ForegroundColor Green
Write-Host ""

# Run the learning system with enhanced error handling
try {
    if ($Interactive) {
        Write-Host "Running in interactive mode..." -ForegroundColor Cyan
        python aios_complete_learning_system.py
    } else {
        Write-Host "Running in demo mode..." -ForegroundColor Cyan
        python aios_learning_demo_noninteractive.py
    }
} catch {
    Write-Host "Error running learning system: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Trying demo mode instead..." -ForegroundColor Yellow
    python aios_learning_demo_noninteractive.py
}

# Keep the window open
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AIOS Learning System Session Complete" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

