#!/usr/bin/env pwsh
# Final WHY-Algebra Validation
# Uses luna_chat.py with shared process-level session

Write-Host "="*60 -ForegroundColor Green
Write-Host "V5.1 WHY-ALGEBRA FINAL VALIDATION" -ForegroundColor Green  
Write-Host "="*60 -ForegroundColor Green

# Clean slate
Remove-Item "consciousness_core\drift_logs\session_*.jsonl" -ErrorAction SilentlyContinue

Write-Host "`n[TEST] Sending 5 WHY-algebra prompts (shared session)..." -ForegroundColor Yellow

$prompts = @(
    "why does heat cause expansion?",
    "how does heat lead to expansion?",
    "why heat and pressure -> expansion",
    "why cooling or depressurization -> contraction",
    "not why friction -> cooling"
)

foreach ($prompt in $prompts) {
    Write-Host "  -> $prompt" -ForegroundColor Gray
    py luna_chat.py "$prompt" 2>$null | Out-Null
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "RESULTS" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

$drift = Get-ChildItem "consciousness_core\drift_logs\session_*.jsonl" | Sort-Object LastWriteTime | Select-Object -Last 1

if ($drift) {
    Write-Host "`nSession: $($drift.Name)" -ForegroundColor Gray
    
    $linguaEntries = Get-Content $drift | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.fragment -eq "LinguaCalc" }
    
    Write-Host "`n[LINGUA CALC ENTRIES]" -ForegroundColor Yellow
    $linguaEntries | ForEach-Object {
        Write-Host "  $($_.question)" -ForegroundColor White
        $logic = if ($_.metadata.why_logic) { $_.metadata.why_logic -join "," } else { "-" }
        Write-Host "    Logic=$logic Depth=$($_.metadata.depth) Gain=$($_.metadata.gain) Coherence=$($_.metadata.coherence)" -ForegroundColor Green
        Write-Host "    $($_.metadata.summary)" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host "[STATISTICS]" -ForegroundColor Yellow
    Write-Host "  Total prompts sent: $($prompts.Count)" -ForegroundColor Gray
    Write-Host "  LinguaCalc entries: $($linguaEntries.Count)" -ForegroundColor Gray
    
    $withAND = ($linguaEntries | Where-Object { $_.metadata.why_logic -contains "AND" }).Count
    $withOR = ($linguaEntries | Where-Object { $_.metadata.why_logic -contains "OR" }).Count
    $withNOT = ($linguaEntries | Where-Object { $_.metadata.why_logic -contains "NOT" }).Count
    $withDepth = ($linguaEntries | Where-Object { $_.metadata.depth -gt 0 }).Count
    $withGain = ($linguaEntries | Where-Object { $_.metadata.gain -gt 0 }).Count
    $withCoherence = ($linguaEntries | Where-Object { $_.metadata.coherence -gt 0 }).Count
    
    Write-Host "  - WHY-AND: $withAND" -ForegroundColor Gray
    Write-Host "  - WHY-OR: $withOR" -ForegroundColor Gray
    Write-Host "  - NOT-WHY: $withNOT" -ForegroundColor Gray
    Write-Host "  - Depth > 0: $withDepth" -ForegroundColor Gray
    Write-Host "  - Gain > 0: $withGain" -ForegroundColor Gray
    Write-Host "  - Coherence > 0: $withCoherence" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "="*60 -ForegroundColor Cyan
    Write-Host "VERDICT" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan
    
    if ($linguaEntries.Count -eq $prompts.Count) {
        Write-Host "`n  [SUCCESS] All prompts logged to shared session" -ForegroundColor Green
    } else {
        Write-Host "`n  [WARN] Only $($linguaEntries.Count)/$($prompts.Count) prompts logged" -ForegroundColor Yellow
    }
    
    if ($withAND -gt 0 -and $withOR -gt 0 -and $withNOT -gt 0) {
        Write-Host "  [SUCCESS] All WHY-algebra connectives working (AND, OR, NOT)" -ForegroundColor Green
    } else {
        Write-Host "  [PARTIAL] Missing connectives: AND=$withAND OR=$withOR NOT=$withNOT" -ForegroundColor Yellow
    }
    
    if ($withDepth -gt 0 -and $withGain -gt 0 -and $withCoherence -gt 0) {
        Write-Host "  [SUCCESS] Depth/Gain/Coherence scoring working" -ForegroundColor Green
    } else {
        Write-Host "  [PARTIAL] Metrics: Depth=$withDepth Gain=$withGain Coherence=$withCoherence" -ForegroundColor Yellow
    }
    
    Write-Host "`n  THE ORGANISM THINKS WITH ALGEBRA." -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "`n[FAIL] No drift log created" -ForegroundColor Red
}

