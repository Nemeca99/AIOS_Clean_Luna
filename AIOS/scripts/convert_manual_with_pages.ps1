# Convert AIOS Manual to HTML with Print-CSS page counters

Write-Host "Converting manual with Print-CSS page counters..." -ForegroundColor Cyan

# CSS for print with page counters
$printCSS = @'
<style>
    /* Print-CSS for page counting */
    @page {
        size: A4;
        margin: 25mm 20mm 25mm 20mm;
        
        @bottom-right {
            content: 'Page ' counter(page) ' of ' counter(pages);
            font-size: 0.8em;
            color: #666;
        }
        
        @bottom-left {
            content: 'AIOS User Manual v2.2.0';
            font-size: 0.8em;
            color: #666;
        }
    }
    
    /* First page (title page) - no page number */
    @page:first {
        @bottom-right {
            content: none;
        }
        @bottom-left {
            content: none;
        }
    }
    
    /* General styling */
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        line-height: 1.6;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }
    
    h1 {
        color: #2c3e50;
        page-break-before: always;
        page-break-after: avoid;
    }
    
    h2, h3 {
        color: #34495e;
        page-break-after: avoid;
    }
    
    pre, code {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 3px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9em;
    }
    
    pre {
        padding: 10px;
        overflow-x: auto;
        page-break-inside: avoid;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        page-break-inside: avoid;
    }
    
    table, th, td {
        border: 1px solid #ddd;
    }
    
    th, td {
        padding: 8px;
        text-align: left;
    }
    
    /* Page breaks */
    .page-break {
        page-break-before: always;
    }
</style>
'@

# Convert with pandoc and inject CSS
Write-Host "Converting markdown to HTML..." -ForegroundColor Yellow
pandoc AIOS_MANUAL.md -o AIOS_MANUAL_temp.html --standalone --toc --metadata title="AIOS User Manual"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ HTML created" -ForegroundColor Green
    
    # Inject Print-CSS into head
    $html = Get-Content AIOS_MANUAL_temp.html -Raw
    $html = $html -replace '</head>', "$printCSS`n</head>"
    
    Set-Content -Path "AIOS_MANUAL_PRINTABLE.html" -Value $html -Encoding UTF8
    Remove-Item AIOS_MANUAL_temp.html
    
    $size = (Get-Item AIOS_MANUAL_PRINTABLE.html).Length / 1MB
    Write-Host "  ✅ Print-ready HTML created ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "TO GET TRUE PAGE COUNT:" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Opening AIOS_MANUAL_PRINTABLE.html..." -ForegroundColor White
    Write-Host ""
    Write-Host "In the browser:" -ForegroundColor White
    Write-Host "  1. Press Ctrl+P (Print)" -ForegroundColor Gray
    Write-Host "  2. Look at preview - you'll see page numbers at bottom" -ForegroundColor Gray
    Write-Host "  3. Check total pages (e.g., 'Page 1 of 547')" -ForegroundColor Gray
    Write-Host "  4. (Optional) Save as PDF" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Page counter format: 'Page X of Y' at bottom right" -ForegroundColor Green
    Write-Host ""
    
    # Open in browser
    start AIOS_MANUAL_PRINTABLE.html
    
} else {
    Write-Host "  ❌ Conversion failed" -ForegroundColor Red
}

