# Convert AIOS Manual to PDF
# Gets the TRUE page count

Write-Host "Converting AIOS Manual to PDF..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Generate HTML with pandoc
Write-Host "[1/3] Converting markdown to HTML..." -ForegroundColor Yellow
pandoc AIOS_MANUAL.md -o AIOS_MANUAL.html --standalone --toc --metadata title="AIOS User Manual"

if ($LASTEXITCODE -eq 0) {
    $htmlSize = (Get-Item AIOS_MANUAL.html).Length / 1MB
    Write-Host "  ✅ HTML created ($([math]::Round($htmlSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "  ❌ HTML conversion failed" -ForegroundColor Red
    exit 1
}

# Step 2: Open in browser
Write-Host "[2/3] Opening in browser..." -ForegroundColor Yellow
start AIOS_MANUAL.html

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "TO GET TRUE PAGE COUNT:" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "In the browser window that just opened:" -ForegroundColor White
Write-Host "  1. Press Ctrl+P (Print)" -ForegroundColor Gray
Write-Host "  2. Choose 'Save as PDF' as destination" -ForegroundColor Gray
Write-Host "  3. Click 'Save'" -ForegroundColor Gray
Write-Host "  4. Check page count in saved PDF" -ForegroundColor Gray
Write-Host ""
Write-Host "The PDF page count = TRUE page count" -ForegroundColor Green
Write-Host ""
Write-Host "Save as: AIOS_MANUAL.pdf" -ForegroundColor Yellow

