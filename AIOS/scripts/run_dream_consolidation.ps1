# Dream Consolidation - Memory Maintenance
Write-Host "Running dream consolidation (memory optimization)..." -ForegroundColor Cyan

# Run dream core consolidation
py main.py --mode consolidation --max-fragments 100 2>&1 | Out-Null

Write-Host "Dream consolidation complete. Memory optimized." -ForegroundColor Green
