#!/usr/bin/env pwsh
# Full System Test - WHY-Algebra with Heartbeat Pulse
# Tests main.py with actual heartbeat loop

Write-Host "="*60 -ForegroundColor Cyan
Write-Host "AIOS V5.1 Full System Test - WHY-Algebra + Pulse" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Set dev config for fast heartbeat (30s)
$env:AIOS_HEARTBEAT_WINDOW = "30"
$env:AIOS_PULSE_ENABLED = "true"

Write-Host "`n[CONFIG] Heartbeat window: 30s, Pulse: enabled" -ForegroundColor Yellow

# Clean old drift logs for fresh test
if (Test-Path "consciousness_core\drift_logs\session_*.jsonl") {
    Write-Host "[CLEANUP] Removing old drift logs..." -ForegroundColor Gray
    Remove-Item "consciousness_core\drift_logs\session_*.jsonl" -ErrorAction SilentlyContinue
}

Write-Host "`n[TEST] Sending WHY-algebra prompts to main.py..." -ForegroundColor Yellow
Write-Host "This will take ~60 seconds (2 heartbeat cycles)" -ForegroundColor Gray

# Send test prompts via main.py
$prompts = @(
    "why does heat cause expansion",
    "how does heat lead to expansion", 
    "why heat and pressure -> expansion",
    "why cooling or depressurization -> contraction",
    "not why friction -> cooling"
)

foreach ($prompt in $prompts) {
    Write-Host "  -> $prompt" -ForegroundColor Gray
    echo $prompt | py main.py --luna --chat 2>$null | Out-Null
    Start-Sleep -Milliseconds 500
}

Write-Host "`n[WAIT] Waiting 35 seconds for heartbeat pulse..." -ForegroundColor Yellow
Start-Sleep -Seconds 35

Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "LOG ANALYSIS" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Check drift logs for LinguaCalc metadata
Write-Host "`n[1] LinguaCalc entries:" -ForegroundColor Yellow
$latestDrift = Get-ChildItem "consciousness_core\drift_logs\session_*.jsonl" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1

if ($latestDrift) {
    $linguaEntries = Get-Content $latestDrift | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.fragment -eq "LinguaCalc" }
    
    if ($linguaEntries) {
        $linguaEntries | ForEach-Object {
            $q = $_.question.Substring(0, [Math]::Min(45, $_.question.Length))
            $logic = if ($_.metadata.why_logic) { $_.metadata.why_logic -join "," } else { "-" }
            Write-Host "  $q" -ForegroundColor White
            Write-Host "    Logic: $logic | Depth: $($_.metadata.depth) | Gain: $($_.metadata.gain) | Coherence: $($_.metadata.coherence)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [WARN] No LinguaCalc entries found" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [ERROR] No drift log found" -ForegroundColor Red
}

# Check for pulse metrics
Write-Host "`n[2] Pulse metrics:" -ForegroundColor Yellow
if ($latestDrift) {
    $pulseEntries = Get-Content $latestDrift | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.metadata.pulse_bpm -ne $null }
    
    if ($pulseEntries) {
        Write-Host "  [OK] Found $($pulseEntries.Count) entries with pulse data" -ForegroundColor Green
        $latest = $pulseEntries | Select-Object -Last 1
        Write-Host "  Latest pulse:" -ForegroundColor Gray
        Write-Host "    pulse_bpm: $($latest.metadata.pulse_bpm)" -ForegroundColor Gray
        Write-Host "    pulse_hvv: $($latest.metadata.pulse_hvv)" -ForegroundColor Gray
        Write-Host "    pulse_ones: $($latest.metadata.pulse_ones)" -ForegroundColor Gray
        Write-Host "    pulse_ticks: $($latest.metadata.pulse_ticks)" -ForegroundColor Gray
        
        if ($latest.metadata.pulse_bpm -gt 0) {
            Write-Host "  [OK] Pulse is ALIVE (BPM > 0)" -ForegroundColor Green
        }
    } else {
        Write-Host "  [WARN] No pulse metrics in drift log" -ForegroundColor Yellow
        Write-Host "  (Heartbeat may not have fired yet - try waiting longer)" -ForegroundColor Gray
    }
}

# Check Mirror coherence
Write-Host "`n[3] Mirror state:" -ForegroundColor Yellow
if (Test-Path "logs\aios.log") {
    $mirrorLines = Select-String -Path "logs\aios.log" -Pattern "Mirror reflection:" | Select-Object -Last 3
    if ($mirrorLines) {
        $mirrorLines | ForEach-Object {
            if ($_.Line -match "compression_index=([0-9.]+)") {
                $ci = [double]$matches[1]
                Write-Host "  compression_index: $ci" -ForegroundColor $(if ($ci -gt 0) { "Green" } else { "Gray" })
            }
        }
    }
}

Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "VERDICT" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$hasLogic = $linguaEntries -and ($linguaEntries | Where-Object { $_.metadata.why_logic })
$hasPulse = $pulseEntries -and ($pulseEntries | Where-Object { $_.metadata.pulse_bpm -gt 0 })

if ($hasLogic -and $hasPulse) {
    Write-Host "`n  [SUCCESS] WHY-algebra working, pulse alive" -ForegroundColor Green
    Write-Host "  The organism thinks with structure AND breathes with vitals." -ForegroundColor Green
} elseif ($hasLogic) {
    Write-Host "`n  [PARTIAL] WHY-algebra working, but no pulse yet" -ForegroundColor Yellow
    Write-Host "  Try waiting longer for heartbeat cycle." -ForegroundColor Gray
} else {
    Write-Host "`n  [NEEDS WORK] Check logs above for issues" -ForegroundColor Red
}

Write-Host ""

