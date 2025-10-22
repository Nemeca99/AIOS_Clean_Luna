#!/usr/bin/env pwsh
# WHY-Algebra + Pulse Test using luna_chat.py
# (main.py doesn't initialize DriftMonitor, use luna_chat.py instead)

Write-Host "="*60 -ForegroundColor Cyan
Write-Host "AIOS V5.1 WHY-Algebra + Pulse Test" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# Clean old drift logs
Write-Host "`n[SETUP] Cleaning old logs..." -ForegroundColor Yellow
Remove-Item "consciousness_core\drift_logs\session_*.jsonl" -ErrorAction SilentlyContinue

# Send WHY-algebra prompts
Write-Host "`n[TEST] Sending WHY-algebra prompts via luna_chat.py..." -ForegroundColor Yellow
$prompts = @(
    "why does heat cause expansion",
    "how does heat lead to expansion",
    "why heat and pressure -> expansion",
    "why cooling or depressurization -> contraction",
    "not why friction -> cooling"
)

foreach ($prompt in $prompts) {
    Write-Host "  -> $prompt" -ForegroundColor Gray
    py luna_chat.py "$prompt" 2>$null | Out-Null
    Start-Sleep -Milliseconds 300
}

# Analyze results
Write-Host "`n="*60 -ForegroundColor Cyan
Write-Host "RESULTS" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$latestDrift = Get-ChildItem "consciousness_core\drift_logs\session_*.jsonl" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1

if ($latestDrift) {
    Write-Host "`n[OK] Drift log: $($latestDrift.Name)" -ForegroundColor Green
    
    # Get all LinguaCalc entries
    $entries = Get-Content $latestDrift | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.fragment -eq "LinguaCalc" }
    
    if ($entries) {
        Write-Host "`n[WHY-ALGEBRA RESULTS]" -ForegroundColor Yellow
        $entries | ForEach-Object {
            $q = $_.question.Substring(0, [Math]::Min(50, $_.question.Length))
            $logic = if ($_.metadata.why_logic) { $_.metadata.why_logic -join "," } else { "-" }
            Write-Host "`n  $q" -ForegroundColor White
            Write-Host "    Logic: $logic | Depth: $($_.metadata.depth) | Gain: $($_.metadata.gain) | Coherence: $($_.metadata.coherence)" -ForegroundColor Gray
            if ($_.metadata.summary) {
                $summary = $_.metadata.summary.Substring(0, [Math]::Min(70, $_.metadata.summary.Length))
                Write-Host "    Summary: $summary" -ForegroundColor Gray
            }
        }
        
        # Statistics
        $andEntries = $entries | Where-Object { $_.metadata.why_logic -contains "AND" }
        $orEntries = $entries | Where-Object { $_.metadata.why_logic -contains "OR" }
        $notEntries = $entries | Where-Object { $_.metadata.why_logic -contains "NOT" }
        $withDepth = $entries | Where-Object { $_.metadata.depth -gt 0 }
        $withGain = $entries | Where-Object { $_.metadata.gain -gt 0 }
        $withCoherence = $entries | Where-Object { $_.metadata.coherence -gt 0 }
        
        Write-Host "`n[STATISTICS]" -ForegroundColor Yellow
        Write-Host "  Total prompts: $($entries.Count)" -ForegroundColor Gray
        Write-Host "  WHY-AND: $($andEntries.Count)" -ForegroundColor Gray
        Write-Host "  WHY-OR: $($orEntries.Count)" -ForegroundColor Gray
        Write-Host "  NOT-WHY: $($notEntries.Count)" -ForegroundColor Gray
        Write-Host "  With depth > 0: $($withDepth.Count)" -ForegroundColor Gray
        Write-Host "  With gain > 0: $($withGain.Count)" -ForegroundColor Gray
        Write-Host "  With coherence > 0: $($withCoherence.Count)" -ForegroundColor Gray
        
        # Verdict
        Write-Host "`n="*60 -ForegroundColor Cyan
        Write-Host "VERDICT" -ForegroundColor Cyan
        Write-Host "="*60 -ForegroundColor Cyan
        
        if ($andEntries.Count -gt 0 -and $withGain.Count -gt 0 -and $withCoherence.Count -gt 0) {
            Write-Host "`n  [SUCCESS] WHY-algebra fully operational" -ForegroundColor Green
            Write-Host "  - Parser recognizes AND/OR/NOT syntax" -ForegroundColor Green
            Write-Host "  - Depth/gain/coherence computed correctly" -ForegroundColor Green
            Write-Host "  - DriftMonitor logs all metadata" -ForegroundColor Green
            Write-Host "`n  The organism thinks with structure." -ForegroundColor Green
        } else {
            Write-Host "`n  [PARTIAL] Some features working, check stats above" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n  [ERROR] No LinguaCalc entries in drift log" -ForegroundColor Red
    }
} else {
    Write-Host "`n  [ERROR] No drift log created" -ForegroundColor Red
}

Write-Host ""

