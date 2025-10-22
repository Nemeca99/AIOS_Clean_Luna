# AIOS Learning System Launcher
Write-Host "Starting AIOS Learning System..." -ForegroundColor Green
Write-Host ""
Write-Host "This will run the learning system in a proper interactive terminal." -ForegroundColor Yellow
Write-Host ""

# Change to the AIOS directory
Set-Location "F:\AIOS_Clean"

# Check if we're in PowerShell 7+ for better terminal support
if ($PSVersionTable.PSVersion.Major -ge 7) {
    Write-Host "Using PowerShell 7+ with enhanced terminal support" -ForegroundColor Green
} else {
    Write-Host "Using Windows PowerShell - consider upgrading to PowerShell 7+ for better terminal support" -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/PowerShell/PowerShell/releases" -ForegroundColor Cyan
}

# Run the learning system
python aios_complete_learning_system.py

# Keep the window open
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
