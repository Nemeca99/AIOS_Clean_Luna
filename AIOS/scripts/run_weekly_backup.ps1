# Weekly Backup
Write-Host "Creating weekly backup..." -ForegroundColor Cyan

# Create timestamped backup
$timestamp = Get-Date -Format "yyyy-MM-dd"
py main.py --action backup --backup-name "weekly_$timestamp" 2>&1 | Out-Null

Write-Host "Backup complete: weekly_$timestamp" -ForegroundColor Green
