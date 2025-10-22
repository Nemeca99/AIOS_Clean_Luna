#!/usr/bin/env pwsh
# AIOS V5.1 Smoke Test Helper
# Sets dev overrides and tails relevant logs for manual smoke testing

Write-Host "="*60 -ForegroundColor Cyan
Write-Host "AIOS V5.1 Manual Smoke Test Helper" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Check if in AIOS_Clean directory
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: Run from AIOS_Clean root directory" -ForegroundColor Red
    exit 1
}

Write-Host "`n[SETUP] Creating dev config overrides..." -ForegroundColor Yellow

# Create dev config override
$devConfig = @"
{
  "heartbeat_window_seconds": 30,
  "pulse_metrics_enabled": true,
  "pulse_bpm_hot_threshold": 0.02,
  "log_level": "INFO"
}
"@

$devConfig | Out-File -FilePath "data_core/config/dev_smoke_config.json" -Encoding UTF8

Write-Host "[OK] Dev config: 30s heartbeat, pulse enabled, 0.02 hot threshold" -ForegroundColor Green

Write-Host "`n[INSTRUCTIONS] Manual Smoke Test Protocol" -ForegroundColor Yellow
Write-Host "="*60

Write-Host "`n1. TORPOR (Low Activity):"
Write-Host "   Type: ping"
Write-Host "   Type: what time is it"
Write-Host "   Type: define entropy (one line)"
Write-Host "   Wait: 30-40 seconds for first heartbeat"

Write-Host "`n2. THRASH (High Activity):"
Write-Host "   Type: why does heat cause expansion?"
Write-Host "   Type: how does heat lead to expansion?"
Write-Host "   Type: what is expansion in thermodynamics?"
Write-Host "   Repeat: 2-3 times"
Write-Host "   Wait: 30-40 seconds for hot heartbeat"

Write-Host "`n3. CHECK LOGS:"
Write-Host "   Heartbeat pulse:"
Write-Host '   > Select-String -Path "consciousness_core/drift_logs/*.jsonl" -Pattern "pulse_bpm|pulse_hvv" | Select-Object -Last 5'
Write-Host "`n   Latest drift entry:"
Write-Host '   > Get-Content (Get-ChildItem consciousness_core/drift_logs\*.jsonl | Sort-Object LastWriteTime | Select-Object -Last 1) -Tail 1 | ConvertFrom-Json'

Write-Host "`n="*60
Write-Host "[READY] Starting AIOS with dev config..." -ForegroundColor Green
Write-Host "="*60

Write-Host "`nPress Ctrl+C to stop and check logs`n"

# Run AIOS (user will interact manually)
py .\main.py --log-level=INFO

Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "SMOKE TEST COMPLETE" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n[POST-TEST] Quick log checks:"

# Show last heartbeat
Write-Host "`nLast heartbeat entries:" -ForegroundColor Yellow
Select-String -Path "consciousness_core/drift_logs/*.jsonl" -Pattern "pulse_bpm" | Select-Object -Last 3

# Show drift summary
if (Test-Path "consciousness_core/drift_logs/drift_summary.json") {
    Write-Host "`nDrift summary:" -ForegroundColor Yellow
    Get-Content "consciousness_core/drift_logs/drift_summary.json" | ConvertFrom-Json | Format-List
}

Write-Host "`n[CLEANUP] Removing dev config override..."
Remove-Item "data_core/config/dev_smoke_config.json" -ErrorAction SilentlyContinue

Write-Host "`n[DONE] Review logs above for pulse_bpm, pulse_hvv, and consolidation triggers" -ForegroundColor Green

