#!/usr/bin/env pwsh
# AIOS V5.1 REAL Smoke Test
# Tests the features, not the wallpaper

Write-Host "="*60 -ForegroundColor Cyan
Write-Host "AIOS V5.1 REAL Smoke Test - WHY-Algebra & Pulse" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Set dev config
$env:AIOS_HEARTBEAT_WINDOW = "30"
$env:AIOS_PULSE_ENABLED = "true"

Write-Host "`n[TEST 1] WHY operator - causal edge" -ForegroundColor Yellow
py luna_chat.py "why does heat cause expansion?" 2>$null | Select-String "Well,|Why|How|What|Interesting" | Select-Object -Last 1
Start-Sleep -Seconds 2

Write-Host "`n[TEST 2] HOW operator - mechanism chain" -ForegroundColor Yellow
py luna_chat.py "how does heat lead to expansion?" 2>$null | Select-String "Well,|Why|How|What|Interesting" | Select-Object -Last 1
Start-Sleep -Seconds 2

Write-Host "`n[TEST 3] WHY-AND - shared mechanism" -ForegroundColor Yellow
py luna_chat.py "why heat and pressure cause expansion" 2>$null | Select-String "Well,|Why|How|What|Interesting" | Select-Object -Last 1
Start-Sleep -Seconds 2

Write-Host "`n[TEST 4] WHY-OR - alternative causes" -ForegroundColor Yellow
py luna_chat.py "why cooling or depressurization causes contraction" 2>$null | Select-String "Well,|Why|How|What|Interesting" | Select-Object -Last 1
Start-Sleep -Seconds 2

Write-Host "`n[TEST 5] NOT-WHY - negation" -ForegroundColor Yellow
py luna_chat.py "not why friction causes cooling" 2>$null | Select-String "Well,|Why|How|What|Interesting" | Select-Object -Last 1

Write-Host "`n[WAITING] 35 seconds for heartbeat pulse..." -ForegroundColor Gray
Start-Sleep -Seconds 35

Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "LOG ANALYSIS" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Check for heartbeat pulse in logs
Write-Host "`n[1] Checking for HEARTBEAT pulse metrics..." -ForegroundColor Yellow
if (Test-Path "logs\aios.log") {
    $pulseLines = Select-String -Path "logs\aios.log" -Pattern "HEARTBEAT|pulse_bpm|pulse_hvv" | Select-Object -Last 5
    if ($pulseLines) {
        Write-Host "  FOUND pulse metrics:" -ForegroundColor Green
        $pulseLines | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    } else {
        Write-Host "  [WARN] No pulse metrics in aios.log" -ForegroundColor Yellow
    }
}

# Check drift log for LinguaCalc metadata
Write-Host "`n[2] Checking drift log for LinguaCalc metadata..." -ForegroundColor Yellow
$latestDrift = Get-ChildItem "consciousness_core\drift_logs\*.jsonl" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
if ($latestDrift) {
    $lastEntry = Get-Content $latestDrift -Tail 1 | ConvertFrom-Json
    
    Write-Host "  Session: $($latestDrift.Name)" -ForegroundColor Gray
    
    if ($lastEntry.metadata.lingua_calc_depth -ne $null) {
        Write-Host "  [OK] lingua_calc_depth: $($lastEntry.metadata.lingua_calc_depth)" -ForegroundColor Green
    }
    
    if ($lastEntry.metadata.lingua_calc_gain -ne $null) {
        Write-Host "  [OK] lingua_calc_gain: $($lastEntry.metadata.lingua_calc_gain)" -ForegroundColor Green
    }
    
    if ($lastEntry.metadata.pulse_bpm -ne $null) {
        Write-Host "  [OK] pulse_bpm: $($lastEntry.metadata.pulse_bpm)" -ForegroundColor Green
    }
    
    if ($lastEntry.metadata.pulse_hvv -ne $null) {
        Write-Host "  [OK] pulse_hvv: $($lastEntry.metadata.pulse_hvv)" -ForegroundColor Green
    }
}

# Check Mirror compression
Write-Host "`n[3] Checking for Mirror compression..." -ForegroundColor Yellow
if (Test-Path "logs\aios.log") {
    $mirrorLines = Select-String -Path "logs\aios.log" -Pattern "Mirror reflection:|compression_index" | Select-Object -Last 3
    if ($mirrorLines) {
        $mirrorLines | ForEach-Object { 
            $line = $_.Line
            if ($line -match "compression_index=([0-9.]+)") {
                $ci = [double]$matches[1]
                if ($ci -gt 0) {
                    Write-Host "  [OK] compression_index: $ci (nonzero!)" -ForegroundColor Green
                } else {
                    Write-Host "  [INFO] compression_index: $ci (still zero)" -ForegroundColor Gray
                }
            }
        }
    }
}

Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "VERDICT" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`nIf you see:"
Write-Host "  - pulse_bpm > 0: Heartbeat is alive" -ForegroundColor Gray
Write-Host "  - lingua_calc_depth > 0: LinguaCalc is firing" -ForegroundColor Gray
Write-Host "  - compression_index > 0: Mirror is compressing" -ForegroundColor Gray
Write-Host "`nIf you don't: The organism twitched but didn't think.`n" -ForegroundColor Gray

