# AIOS PowerShell Setup Script
# This script sets up the AIOS PowerShell wrapper in your PowerShell profile

param(
    [switch]$Force,
    [string]$ProfilePath = $PROFILE
)

Write-Host "AIOS PowerShell Setup" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Get the current script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WrapperPath = Join-Path $ScriptDir "aios_powershell_wrapper.ps1"

# Check if wrapper exists
if (-not (Test-Path $WrapperPath)) {
    Write-Host "ERROR: aios_powershell_wrapper.ps1 not found at: $WrapperPath" -ForegroundColor Red
    exit 1
}

# Check if profile exists
if (-not (Test-Path $ProfilePath)) {
    Write-Host "Creating PowerShell profile at: $ProfilePath" -ForegroundColor Yellow
    
    # Create the profile directory if it doesn't exist
    $ProfileDir = Split-Path -Parent $ProfilePath
    if (-not (Test-Path $ProfileDir)) {
        New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
    }
    
    # Create empty profile
    New-Item -ItemType File -Path $ProfilePath -Force | Out-Null
}

# Check if AIOS wrapper is already in profile
$ProfileContent = Get-Content $ProfilePath -Raw -ErrorAction SilentlyContinue
$WrapperReference = ". '$WrapperPath'"

if ($ProfileContent -and $ProfileContent.Contains($WrapperReference)) {
    if (-not $Force) {
        Write-Host "AIOS PowerShell wrapper is already configured in your profile." -ForegroundColor Yellow
        Write-Host "Use -Force to reinstall." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Removing existing AIOS wrapper configuration..." -ForegroundColor Yellow
        $ProfileContent = $ProfileContent -replace [regex]::Escape($WrapperReference), ""
        $ProfileContent = $ProfileContent -replace [regex]::Escape("# AIOS PowerShell Wrapper"), ""
        $ProfileContent = $ProfileContent -replace [regex]::Escape("# Auto-load AIOS environment"), ""
    }
}

# Add AIOS wrapper to profile
Write-Host "Adding AIOS PowerShell wrapper to profile..." -ForegroundColor Green

$NewContent = @"

# AIOS PowerShell Wrapper
# Auto-load AIOS environment
. '$WrapperPath'
"@

if ($ProfileContent) {
    $ProfileContent += $NewContent
} else {
    $ProfileContent = $NewContent
}

# Write updated profile
Set-Content -Path $ProfilePath -Value $ProfileContent -Encoding UTF8

Write-Host ""
Write-Host "✅ AIOS PowerShell wrapper installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The following features are now available:" -ForegroundColor Cyan
Write-Host "• Automatic Python virtual environment activation" -ForegroundColor Gray
Write-Host "• SysAdminTools PowerShell module integration" -ForegroundColor Gray
Write-Host "• Custom AIOS commands and aliases" -ForegroundColor Gray
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "• aios     - Start AIOS interactive session" -ForegroundColor Gray
Write-Host "• status   - Check AIOS system status" -ForegroundColor Gray
Write-Host "• health   - Run AIOS health check" -ForegroundColor Gray
Write-Host "• monitor  - Start AIOS monitoring" -ForegroundColor Gray
Write-Host "• help-aios - Show all AIOS commands" -ForegroundColor Gray
Write-Host ""
Write-Host "To activate immediately, restart PowerShell or run:" -ForegroundColor Yellow
Write-Host ". `$PROFILE" -ForegroundColor White
Write-Host ""
