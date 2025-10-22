# AIOS Learning System V2 - PowerShell Version
# Designed to work with PowerShell environment

Write-Host "AIOS Learning System V2 - Brilliant-Style Learning Platform" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""

Write-Host "This system offers two powerful learning modes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "MANUAL MODE - Interactive Learning" -ForegroundColor Cyan
Write-Host "   - Learn step-by-step with AI personality" -ForegroundColor White
Write-Host "   - AI adapts to your pace and style" -ForegroundColor White
Write-Host "   - Perfect for: New subjects, skill building" -ForegroundColor White
Write-Host "   - Database built through interaction" -ForegroundColor White
Write-Host ""
Write-Host "AUTO MODE - Data Processing" -ForegroundColor Cyan
Write-Host "   - Feed AI your data and let it learn" -ForegroundColor White
Write-Host "   - Processes files, documents, code" -ForegroundColor White
Write-Host "   - Perfect for: Research, knowledge extraction" -ForegroundColor White
Write-Host "   - Database built automatically" -ForegroundColor White
Write-Host ""

# Change to AIOS directory
Set-Location "F:\AIOS_Clean"

Write-Host "Starting AIOS Learning System..." -ForegroundColor Yellow
Write-Host ""

# Check if we can run Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Run the learning system
Write-Host "Launching AIOS Learning System..." -ForegroundColor Yellow
Write-Host ""

# Try to run the interactive system
try {
    python aios_learning_launcher.py
} catch {
    Write-Host "Interactive mode failed, running demo instead..." -ForegroundColor Yellow
    python aios_learning_demo_v2.py
}

Write-Host ""
Write-Host "AIOS Learning System session ended." -ForegroundColor Green
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
