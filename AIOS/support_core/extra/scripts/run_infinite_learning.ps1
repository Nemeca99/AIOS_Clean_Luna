#!/usr/bin/env pwsh
# Luna Infinite Learning PowerShell Script

Write-Host "Starting Luna Infinite Learning Mode..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop at any time" -ForegroundColor Yellow
Write-Host ""

try {
    python luna_infinite_learning.py --delay 5
}
catch {
    Write-Host "Luna Infinite Learning stopped." -ForegroundColor Red
}

Write-Host ""
Write-Host "Luna Infinite Learning stopped." -ForegroundColor Green
Read-Host "Press Enter to exit"
