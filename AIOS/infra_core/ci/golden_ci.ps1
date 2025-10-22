# Golden Test CI Gate (PowerShell version for Windows)
# Fails build on regression

param(
    [string]$Set = "data_core\goldens\sample_set.json",
    [string]$Baseline = "data_core\goldens\baseline_new.json",
    [double]$Threshold = 0.25
)

$ErrorActionPreference = "Stop"

Write-Host "======================================================================"
Write-Host "GOLDEN TEST CI GATE"
Write-Host "======================================================================"

# Check if baseline exists
if (!(Test-Path $Baseline)) {
    Write-Host "[golden] no baseline; recording initial baseline"
    py tools\golden_runner.py record --set $Set --out $Baseline
    Write-Host "✅ Baseline recorded"
    exit 0
}

# Run comparison
Write-Host ""
Write-Host "📊 Running golden test comparison..."
Write-Host "   Baseline: $Baseline"
Write-Host "   Golden Set: $Set"
Write-Host ""

py tools\golden_runner.py compare --set $Set --baseline $Baseline --threshold $Threshold

# Exit code from compare determines CI status
# 0 = PASS, 1 = FAIL
exit $LASTEXITCODE





