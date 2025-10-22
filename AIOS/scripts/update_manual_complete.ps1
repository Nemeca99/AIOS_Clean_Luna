#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete Manual Update Workflow
.DESCRIPTION
    Updates AIOS_MANUAL.md, regenerates TOC, rebuilds RAG database with embeddings
    This is the ONE script to run after editing the manual.
#>

param(
    [switch]$SkipTOC,
    [switch]$SkipEmbeddings,
    [switch]$Verbose
)

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "AIOS MANUAL UPDATE WORKFLOW" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$startTime = Get-Date

# Step 1: Verify manual exists
Write-Host "`n[1/4] Verifying AIOS_MANUAL.md..." -ForegroundColor Yellow
if (-not (Test-Path "AIOS_MANUAL.md")) {
    Write-Host "   ERROR: AIOS_MANUAL.md not found!" -ForegroundColor Red
    exit 1
}
$manualSize = (Get-Item "AIOS_MANUAL.md").Length / 1MB
$manualLines = (Get-Content "AIOS_MANUAL.md").Count
Write-Host "   Manual found: $([math]::Round($manualSize, 2)) MB, $manualLines lines" -ForegroundColor Green

# Step 2: Regenerate TOC
if (-not $SkipTOC) {
    Write-Host "`n[2/4] Regenerating MANUAL_TOC.md..." -ForegroundColor Yellow
    
    # Run TOC generator
    py -c @"
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Read manual
with open('AIOS_MANUAL.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Generate TOC
toc_lines = []
toc_lines.append('# AIOS Manual - Table of Contents\n')
toc_lines.append('\n')
toc_lines.append('**Note:** Use line numbers for navigation. Canonical PDF is 660 pages (Letter, 1\" margins).\n')
toc_lines.append('\n')
toc_lines.append('| Line | Section | Topic |\n')
toc_lines.append('|------|---------|-------|\n')

section_num = ''
for i, line in enumerate(lines, 1):
    line = line.rstrip()
    if line.startswith('# ') and not line.startswith('# AIOS'):
        # Main heading
        title = line[2:].split('{')[0].strip()
        section_num = title.split()[0] if title[0].isdigit() else ''
        toc_lines.append(f'| {i} | {section_num} | **{title}** |\n')
    elif line.startswith('## '):
        # Second level heading
        title = line[3:].split('{')[0].strip()
        section_num = title.split()[0] if title[0].isdigit() else ''
        toc_lines.append(f'| {i} | {section_num} | {title} |\n')
    elif line.startswith('### '):
        # Third level heading
        title = line[4:].split('{')[0].strip()
        section_num = title.split()[0] if title[0].isdigit() else ''
        toc_lines.append(f'| {i} | {section_num} | {title} |\n')

# Write TOC
with open('MANUAL_TOC.md', 'w', encoding='utf-8') as f:
    f.writelines(toc_lines)

print(f'   TOC generated: {len(toc_lines)} entries')
"@
    
    if ($LASTEXITCODE -eq 0) {
        $tocLines = (Get-Content "MANUAL_TOC.md").Count
        Write-Host "   TOC updated: $tocLines lines" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: TOC generation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[2/4] Skipping TOC regeneration (--SkipTOC)" -ForegroundColor Gray
}

# Step 3: Update manual metadata
Write-Host "`n[3/4] Updating manual metadata..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
Write-Host "   Timestamp: $timestamp" -ForegroundColor Green
Write-Host "   Lines: $manualLines" -ForegroundColor Green

# Step 4: Rebuild RAG database
if (-not $SkipEmbeddings) {
    Write-Host "`n[4/4] Rebuilding RAG database with embeddings..." -ForegroundColor Yellow
    Write-Host "   This will take ~10-20 seconds for embedding generation..." -ForegroundColor Gray
    
    $embedStart = Get-Date
    py scripts/build_oracle_with_embeddings.py
    $embedEnd = Get-Date
    $embedDuration = ($embedEnd - $embedStart).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   RAG database rebuilt in $([math]::Round($embedDuration, 1))s" -ForegroundColor Green
        
        # Check index file
        if (Test-Path "rag_core/manual_oracle/oracle_index.json") {
            $indexSize = (Get-Item "rag_core/manual_oracle/oracle_index.json").Length / 1KB
            Write-Host "   Index size: $([math]::Round($indexSize, 0)) KB" -ForegroundColor Green
        }
    } else {
        Write-Host "   WARNING: RAG database rebuild had issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[4/4] Skipping RAG database rebuild (--SkipEmbeddings)" -ForegroundColor Gray
}

# Summary
$totalDuration = (Get-Date) - $startTime
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "UPDATE COMPLETE!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "  Manual: $manualLines lines ($([math]::Round($manualSize, 2)) MB)" -ForegroundColor White
if (-not $SkipTOC) {
    Write-Host "  TOC: Updated" -ForegroundColor White
}
if (-not $SkipEmbeddings) {
    Write-Host "  RAG Database: Rebuilt with embeddings" -ForegroundColor White
}
Write-Host "  Total time: $([math]::Round($totalDuration.TotalSeconds, 1))s" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  - Test search: py main.py --rag search 'your query'" -ForegroundColor Gray
Write-Host "  - Run audit: py main.py --audit --v3" -ForegroundColor Gray
Write-Host "  - Commit changes: git add AIOS_MANUAL.md MANUAL_TOC.md rag_core/" -ForegroundColor Gray
Write-Host ""

