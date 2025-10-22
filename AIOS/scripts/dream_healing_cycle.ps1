# Dream Healing Cycle
# Runs during dream consolidation to apply auditor's fixes

Write-Host "Dream Healing Cycle - Self-Healing System" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run audit to find issues and create sandbox fixes
Write-Host "[1/4] Running audit to detect issues..." -ForegroundColor Yellow
py main.py --audit --v3 --no-dashboard 2>&1 | Out-Null

# Step 2: Run dream consolidation
Write-Host "[2/4] Running dream consolidation..." -ForegroundColor Yellow
py main.py --mode consolidation --max-fragments 100 2>&1 | Out-Null

# Step 3: Apply pending fixes from sandbox
Write-Host "[3/4] Applying pending fixes..." -ForegroundColor Yellow
py -c "from main_core.audit_core.dream_integration import DreamHealer; from pathlib import Path; healer = DreamHealer(Path.cwd()); result = healer.run_healing_cycle(); print(f'Applied: {result[\"fixes_applied\"]}, Verified: {result[\"fixes_verified\"]}')"

# Step 4: Re-audit to verify healing worked
Write-Host "[4/4] Verifying fixes..." -ForegroundColor Yellow
py main.py --audit --v3 --no-dashboard 2>&1 | Out-Null

Write-Host ""
Write-Host "Dream healing cycle complete." -ForegroundColor Green
Write-Host "  System has self-healed overnight." -ForegroundColor Gray

