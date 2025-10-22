# Dependency Health Check
Write-Host "Checking dependencies for CVEs and updates..." -ForegroundColor Cyan

# Check for outdated packages
py -m pip list --outdated --format=json | Out-File -FilePath "reports\outdated_packages.json"

# Run audit to check SBOM
py main.py --audit --v3 --no-dashboard 2>&1 | Out-Null

Write-Host "Dependency check complete. See reports\outdated_packages.json" -ForegroundColor Green
