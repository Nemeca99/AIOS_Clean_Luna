# Performance Monitoring
Write-Host "Monitoring system performance..." -ForegroundColor Cyan

# Run audit with perf tracking
py main.py --audit --v3 --perf-budget strict --no-dashboard 2>&1 | Out-Null

# Check trends for regressions
$trends = Get-Content "reports\audit_trends.jsonl" | Select-Object -Last 5
$latestEntry = $trends | Select-Object -Last 1 | ConvertFrom-Json

Write-Host "Performance check complete." -ForegroundColor Green
Write-Host "  Latest score: $($latestEntry.average_score)" -ForegroundColor Gray
