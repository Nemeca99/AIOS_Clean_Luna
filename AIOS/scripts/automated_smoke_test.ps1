#!/usr/bin/env pwsh
# AIOS V5.1 Automated Smoke Test
# Actually sends prompts and checks logs

Write-Host "="*60 -ForegroundColor Cyan
Write-Host "AIOS V5.1 Automated Smoke Test" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Torpor prompts (low activity)
Write-Host "`n[TEST 1] TORPOR (Low Activity)" -ForegroundColor Yellow
$torpor = @("ping", "what time is it", "define entropy in one line")

foreach ($prompt in $torpor) {
    Write-Host "  -> $prompt" -ForegroundColor Gray
    py main.py --luna --chat "$prompt" 2>&1 | Out-Null
    Start-Sleep -Milliseconds 500
}

Write-Host "  Waiting 35 seconds for heartbeat..." -ForegroundColor Gray
Start-Sleep -Seconds 35

# Thrash prompts (high activity)
Write-Host "`n[TEST 2] THRASH (High Activity)" -ForegroundColor Yellow
$thrash = @(
    "why does heat cause expansion?",
    "how does heat lead to expansion?",
    "what is expansion in thermodynamics?"
)

for ($i = 0; $i -lt 3; $i++) {
    foreach ($prompt in $thrash) {
        Write-Host "  -> $prompt" -ForegroundColor Gray
        py main.py --luna --chat "$prompt" 2>&1 | Out-Null
        Start-Sleep -Milliseconds 500
    }
}

Write-Host "  Waiting 35 seconds for hot heartbeat..." -ForegroundColor Gray
Start-Sleep -Seconds 35

# Check logs
Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "LOG ANALYSIS" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Find latest drift log
$driftLogs = Get-ChildItem "consciousness_core/drift_logs/*.jsonl" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime
if ($driftLogs) {
    $latest = $driftLogs | Select-Object -Last 1
    Write-Host "`n[DRIFT LOG] $($latest.Name)" -ForegroundColor Yellow
    
    $entries = Get-Content $latest | ForEach-Object { $_ | ConvertFrom-Json }
    $withPulse = $entries | Where-Object { $_.metadata.pulse_bpm -ne $null }
    
    if ($withPulse) {
        Write-Host "  Found $($withPulse.Count) entries with pulse metrics" -ForegroundColor Green
        
        $lastPulse = $withPulse | Select-Object -Last 1
        Write-Host "`n  Latest pulse metrics:" -ForegroundColor Yellow
        Write-Host "    pulse_bpm: $($lastPulse.metadata.pulse_bpm)"
        Write-Host "    pulse_hvv: $($lastPulse.metadata.pulse_hvv)"
        Write-Host "    pulse_ones: $($lastPulse.metadata.pulse_ones)"
        Write-Host "    pulse_ticks: $($lastPulse.metadata.pulse_ticks)"
        
        if ($lastPulse.metadata.pulse_units) {
            Write-Host "    pulse_units: $($lastPulse.metadata.pulse_units | ConvertTo-Json -Compress)"
        }
        
        # Check for hot activity
        if ($lastPulse.metadata.pulse_bpm -ge 0.02) {
            Write-Host "`n  [OK] HOT ACTIVITY DETECTED (pulse_bpm >= 0.02)" -ForegroundColor Green
        } else {
            Write-Host "`n  [INFO] Low activity (pulse_bpm < 0.02)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [WARN] No pulse metrics in drift log" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[WARN] No drift logs found" -ForegroundColor Yellow
}

# Check drift summary
if (Test-Path "consciousness_core/drift_logs/drift_summary.json") {
    $summary = Get-Content "consciousness_core/drift_logs/drift_summary.json" | ConvertFrom-Json
    Write-Host "`n[DRIFT SUMMARY]" -ForegroundColor Yellow
    Write-Host "  Status: $($summary.status)"
    Write-Host "  Interactions: $($summary.interactions)"
}

Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "SMOKE TEST COMPLETE" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n[VERDICT]" -ForegroundColor Yellow
if ($withPulse -and $withPulse.Count -gt 0) {
    Write-Host "  System is breathing. Pulse metrics flowing." -ForegroundColor Green
} else {
    Write-Host "  Pulse metrics not detected. Check config or logs." -ForegroundColor Red
}

