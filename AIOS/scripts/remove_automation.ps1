# Remove All AIOS Automation Tasks

Write-Host "Removing AIOS automation tasks..." -ForegroundColor Yellow
Write-Host ""

$tasks = Get-ScheduledTask | Where-Object {$_.TaskName -like 'AIOS_*'}

if ($tasks.Count -eq 0) {
    Write-Host "No AIOS tasks found." -ForegroundColor Gray
    exit 0
}

Write-Host "Found $($tasks.Count) AIOS tasks:" -ForegroundColor Cyan
foreach ($task in $tasks) {
    Write-Host "  - $($task.TaskName)" -ForegroundColor Gray
}

Write-Host ""
$confirm = Read-Host "Remove all AIOS tasks? (y/N)"

if ($confirm -eq 'y' -or $confirm -eq 'Y') {
    foreach ($task in $tasks) {
        Write-Host "Removing $($task.TaskName)..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false
    }
    
    Write-Host ""
    Write-Host "All AIOS automation tasks removed." -ForegroundColor Green
} else {
    Write-Host "Cancelled." -ForegroundColor Gray
}

