# Set up Windows scheduled task for daily audit
# Runs audit automatically every day at 9 AM

$taskName = "AIOS_Daily_Audit"
$scriptPath = Join-Path $PSScriptRoot "daily_audit.ps1"
$workingDir = Split-Path $PSScriptRoot -Parent

Write-Host "Setting up daily audit task..." -ForegroundColor Cyan

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction `
    -Execute "pwsh.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`"" `
    -WorkingDirectory $workingDir

# Create trigger (daily at 9 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Register task
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "AIOS V3 Sovereign daily audit - runs automatically" `
    -ErrorAction Stop

Write-Host ""
Write-Host "Daily audit task installed!" -ForegroundColor Green
Write-Host ""
Write-Host "Task details:" -ForegroundColor Yellow
Write-Host "  Name: $taskName" -ForegroundColor Gray
Write-Host "  Schedule: Daily at 9:00 AM" -ForegroundColor Gray
Write-Host "  Script: $scriptPath" -ForegroundColor Gray
Write-Host ""
Write-Host "To disable: " -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host ""
Write-Host "To run manually:" -ForegroundColor Yellow
Write-Host "  pwsh scripts\daily_audit.ps1" -ForegroundColor Gray

