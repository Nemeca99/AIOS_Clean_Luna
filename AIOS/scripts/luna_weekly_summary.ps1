# Luna Weekly Learning Summary
Write-Host "Generating Luna learning summary..." -ForegroundColor Cyan

# Check Luna learning history
$historyFile = "config\luna_learning_history.json"
if (Test-Path $historyFile) {
    $history = Get-Content $historyFile | ConvertFrom-Json
    $summaryFile = "reports\luna_summary_$(Get-Date -Format 'yyyy-MM-dd').txt"
    
    "Luna Learning Summary - $(Get-Date -Format 'yyyy-MM-dd')" | Out-File $summaryFile
    "================================================" | Out-File $summaryFile -Append
    "" | Out-File $summaryFile -Append
    
    Write-Host "Summary saved to: $summaryFile" -ForegroundColor Green
} else {
    Write-Host "No Luna history found." -ForegroundColor Yellow
}
