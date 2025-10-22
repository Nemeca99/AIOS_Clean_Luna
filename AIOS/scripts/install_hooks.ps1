# Install Git Hooks for AIOS
# Sets up pre-commit audit hooks

Write-Host "Installing AIOS Git Hooks..." -ForegroundColor Cyan

# Get git directory
$gitDir = git rev-parse --git-dir 2>$null

if (-not $gitDir) {
    Write-Host "Error: Not a git repository" -ForegroundColor Red
    exit 1
}

$hooksDir = Join-Path $gitDir "hooks"

# Ensure hooks directory exists
if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir | Out-Null
}

# Copy pre-commit hook
$sourceHook = ".githooks\pre-commit.ps1"
$targetHook = Join-Path $hooksDir "pre-commit"

if (Test-Path $sourceHook) {
    # Create wrapper that calls PowerShell script
    $wrapperContent = @"
#!/bin/sh
# AIOS Pre-Commit Hook Wrapper
# Calls PowerShell version for Windows compatibility

pwsh.exe -ExecutionPolicy Bypass -File .githooks/pre-commit.ps1
exit `$?
"@
    
    Set-Content -Path $targetHook -Value $wrapperContent -NoNewline
    
    # On Windows, make sure we have the .ps1 version
    Write-Host "Installed pre-commit hook" -ForegroundColor Green
    Write-Host "  Location: $targetHook" -ForegroundColor Gray
    Write-Host "  Calls: .githooks/pre-commit.ps1" -ForegroundColor Gray
} else {
    Write-Host "Error: .githooks/pre-commit.ps1 not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Git hooks installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Pre-commit hook will:" -ForegroundColor Yellow
Write-Host "  - Audit changed cores before commit" -ForegroundColor Gray
Write-Host "  - Prevent commits that break quality" -ForegroundColor Gray
Write-Host "  - Provide fast feedback (only changed files)" -ForegroundColor Gray
Write-Host ""
Write-Host "To bypass (not recommended): git commit --no-verify" -ForegroundColor Gray

