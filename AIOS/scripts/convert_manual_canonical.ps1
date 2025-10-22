$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Determine repo root (this script lives in scripts\)
$scriptDir = Split-Path -Parent $PSCommandPath
$repo = Resolve-Path (Join-Path $scriptDir '..')
Set-Location $repo

# Paths
$manualPath = Join-Path $repo 'AIOS_MANUAL.md'
if (-not (Test-Path $manualPath)) { throw "Manual not found: $manualPath" }

$outDir = Join-Path $repo 'reports\manual'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$cssPath  = Join-Path $outDir 'print.css'
$outHtml  = Join-Path $outDir 'AIOS_MANUAL_canonical.html'
$outPdf   = Join-Path $outDir 'AIOS_MANUAL_canonical.pdf'

# Print CSS (Letter, 1 inch margins, sane fonts)
$cssContent = @"
@page { size: Letter; margin: 1in; }
html, body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.35; }
pre, code { font-family: Consolas, "Courier New", monospace; font-size: 9pt; }
h1, h2, h3, h4 { page-break-after: avoid; }
img { max-width: 100%; }
h2 + p, h3 + p { page-break-before: avoid; }
"@
$cssContent | Out-File -Encoding ASCII $cssPath

# Convert MD -> HTML via pandoc
$pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-not $pandoc) { throw 'pandoc not found. Please install pandoc.' }
& $pandoc.Source $manualPath -s --from markdown --toc --css $cssPath -o $outHtml
if ($LASTEXITCODE -ne 0) { throw 'pandoc HTML conversion failed' }

# Render HTML -> PDF. Prefer wkhtmltopdf, else Edge/Chrome headless
$wk = Get-Command wkhtmltopdf -ErrorAction SilentlyContinue
if ($wk) {
  & $wk.Source --print-media-type --page-size Letter --margin-top 25.4 --margin-bottom 25.4 --margin-left 25.4 --margin-right 25.4 $outHtml $outPdf
  if ($LASTEXITCODE -ne 0) { throw 'wkhtmltopdf failed' }
} else {
  $browserCandidates = @('msedge.exe','msedge','chrome.exe','chrome','chromium','chromium-browser')
  $browser = $null
  foreach ($c in $browserCandidates) { $cmd = Get-Command $c -ErrorAction SilentlyContinue; if ($cmd) { $browser = $cmd.Source; break } }
  if (-not $browser) {
    $edge32 = Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'
    $edge64 = Join-Path ${env:ProgramFiles}      'Microsoft\Edge\Application\msedge.exe'
    if     (Test-Path $edge64) { $browser = $edge64 }
    elseif (Test-Path $edge32) { $browser = $edge32 }
  }
  if (-not $browser) { throw 'No PDF engine found (wkhtmltopdf/edge/chrome) for headless render.' }
  & $browser --headless --disable-gpu --print-to-pdf=$outPdf --no-pdf-header-footer --virtual-time-budget=60000 $outHtml
  if ($LASTEXITCODE -ne 0) { throw 'Headless browser PDF render failed' }
}

Write-Host ('Canonical PDF written to: ' + $outPdf)

