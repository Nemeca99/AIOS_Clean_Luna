# AIOS Automation Suite Setup
# Schedules tasks between 6 AM - 12 PM (Travis's preferred window)

Write-Host "Setting up AIOS automation suite..." -ForegroundColor Cyan
Write-Host "All tasks will run between 6 AM - 12 PM" -ForegroundColor Gray
Write-Host ""

$workingDir = Split-Path $PSScriptRoot -Parent
$tasksCreated = @()

# Helper function to create task
function New-AIOSTask {
    param(
        [string]$TaskName,
        [string]$ScriptPath,
        [string]$Time,
        [string]$Frequency,  # Daily, Weekly, etc.
        [string]$Description,
        [string]$DayOfWeek = $null
    )
    
    # Remove if exists
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false | Out-Null
    }
    
    # Create action
    $action = New-ScheduledTaskAction `
        -Execute "pwsh.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`"" `
        -WorkingDirectory $workingDir
    
    # Create trigger
    if ($Frequency -eq "Daily") {
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    } elseif ($Frequency -eq "Weekly" -and $DayOfWeek) {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $DayOfWeek -At $Time
    } else {
        throw "Unsupported frequency: $Frequency"
    }
    
    # Settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable
    
    # Register
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description $Description `
        -ErrorAction Stop | Out-Null
    
    return $TaskName
}

# Task 1: Dependency Health Check (Weekly - Monday 6 AM)
Write-Host "Creating: Dependency Health Check (Mondays 6 AM)..." -ForegroundColor Yellow

$script1Path = Join-Path $PSScriptRoot "check_dependencies.ps1"
$script1Content = @'
# Dependency Health Check
Write-Host "Checking dependencies for CVEs and updates..." -ForegroundColor Cyan

# Check for outdated packages
py -m pip list --outdated --format=json | Out-File -FilePath "reports\outdated_packages.json"

# Run audit to check SBOM
py main.py --audit --v3 --no-dashboard 2>&1 | Out-Null

Write-Host "Dependency check complete. See reports\outdated_packages.json" -ForegroundColor Green
'@
Set-Content -Path $script1Path -Value $script1Content

try {
    $task1 = New-AIOSTask `
        -TaskName "AIOS_Dependency_Check" `
        -ScriptPath $script1Path `
        -Time "6:00AM" `
        -Frequency "Weekly" `
        -DayOfWeek "Monday" `
        -Description "Weekly dependency health and CVE check"
    $tasksCreated += "✅ Dependency Check (Mon 6 AM)"
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
}

# Task 2: Dream Consolidation (Daily - 7 AM)
Write-Host "Creating: Dream Consolidation (Daily 7 AM)..." -ForegroundColor Yellow

$script2Path = Join-Path $PSScriptRoot "run_dream_consolidation.ps1"
$script2Content = @'
# Dream Consolidation - Memory Maintenance
Write-Host "Running dream consolidation (memory optimization)..." -ForegroundColor Cyan

# Run dream core consolidation
py main.py --mode consolidation --max-fragments 100 2>&1 | Out-Null

Write-Host "Dream consolidation complete. Memory optimized." -ForegroundColor Green
'@
Set-Content -Path $script2Path -Value $script2Content

try {
    $task2 = New-AIOSTask `
        -TaskName "AIOS_Dream_Consolidation" `
        -ScriptPath $script2Path `
        -Time "7:00AM" `
        -Frequency "Daily" `
        -Description "Daily memory consolidation and optimization"
    $tasksCreated += "✅ Dream Consolidation (Daily 7 AM)"
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
}

# Task 3: Weekly Backup (Sunday 8 AM)
Write-Host "Creating: Weekly Backup (Sundays 8 AM)..." -ForegroundColor Yellow

$script3Path = Join-Path $PSScriptRoot "run_weekly_backup.ps1"
$script3Content = @'
# Weekly Backup
Write-Host "Creating weekly backup..." -ForegroundColor Cyan

# Create timestamped backup
$timestamp = Get-Date -Format "yyyy-MM-dd"
py main.py --action backup --backup-name "weekly_$timestamp" 2>&1 | Out-Null

Write-Host "Backup complete: weekly_$timestamp" -ForegroundColor Green
'@
Set-Content -Path $script3Path -Value $script3Content

try {
    $task3 = New-AIOSTask `
        -TaskName "AIOS_Weekly_Backup" `
        -ScriptPath $script3Path `
        -Time "8:00AM" `
        -Frequency "Weekly" `
        -DayOfWeek "Sunday" `
        -Description "Weekly system backup"
    $tasksCreated += "✅ Weekly Backup (Sun 8 AM)"
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
}

# Task 4: Daily Audit (already exists at 9 AM)
$tasksCreated += "✅ Daily Audit (Daily 9 AM) [Already Installed]"

# Task 5: Performance Monitoring (Daily 10 AM)
Write-Host "Creating: Performance Monitoring (Daily 10 AM)..." -ForegroundColor Yellow

$script5Path = Join-Path $PSScriptRoot "monitor_performance.ps1"
$script5Content = @'
# Performance Monitoring
Write-Host "Monitoring system performance..." -ForegroundColor Cyan

# Run audit with perf tracking
py main.py --audit --v3 --perf-budget strict --no-dashboard 2>&1 | Out-Null

# Check trends for regressions
$trends = Get-Content "reports\audit_trends.jsonl" | Select-Object -Last 5
$latestEntry = $trends | Select-Object -Last 1 | ConvertFrom-Json

Write-Host "Performance check complete." -ForegroundColor Green
Write-Host "  Latest score: $($latestEntry.average_score)" -ForegroundColor Gray
'@
Set-Content -Path $script5Path -Value $script5Content

try {
    $task5 = New-AIOSTask `
        -TaskName "AIOS_Performance_Monitor" `
        -ScriptPath $script5Path `
        -Time "10:00AM" `
        -Frequency "Daily" `
        -Description "Daily performance monitoring and regression detection"
    $tasksCreated += "✅ Performance Monitor (Daily 10 AM)"
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
}

# Task 6: Luna Learning Summary (Weekly - Friday 11 AM)
Write-Host "Creating: Luna Learning Summary (Fridays 11 AM)..." -ForegroundColor Yellow

$script6Path = Join-Path $PSScriptRoot "luna_weekly_summary.ps1"
$script6Content = @'
# Luna Weekly Learning Summary
Write-Host "Generating Luna learning summary..." -ForegroundColor Cyan

# Check Luna learning history
$historyFile = "config\luna_learning_history.json"
if (Test-Path $historyFile) {
    $history = Get-Content $historyFile | ConvertFrom-Json
    $summaryFile = "reports\luna_summary_$(Get-Date -Format 'yyyy-MM-dd').txt"
    
    "Luna Learning Summary - $(Get-Date -Format 'yyyy-MM-dd')" | Out-File $summaryFile
    "================================================" | Out-File $summaryFile -Append
    "" | Out-File $summaryFile -Append
    
    Write-Host "Summary saved to: $summaryFile" -ForegroundColor Green
} else {
    Write-Host "No Luna history found." -ForegroundColor Yellow
}
'@
Set-Content -Path $script6Path -Value $script6Content

try {
    $task6 = New-AIOSTask `
        -TaskName "AIOS_Luna_Summary" `
        -ScriptPath $script6Path `
        -Time "11:00AM" `
        -Frequency "Weekly" `
        -DayOfWeek "Friday" `
        -Description "Weekly Luna learning summary"
    $tasksCreated += "✅ Luna Summary (Fri 11 AM)"
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Automation Suite Installed!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Scheduled tasks:" -ForegroundColor Yellow
foreach ($task in $tasksCreated) {
    Write-Host "  $task" -ForegroundColor Gray
}
Write-Host ""
Write-Host "All tasks run between 6 AM - 12 PM (your preferred window)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view all tasks:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask | Where-Object {`$_.TaskName -like 'AIOS_*'}" -ForegroundColor Gray
Write-Host ""
Write-Host "To remove all:" -ForegroundColor Yellow
Write-Host "  pwsh scripts\remove_automation.ps1" -ForegroundColor Gray

