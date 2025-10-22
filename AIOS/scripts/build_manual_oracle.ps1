# Build Manual Oracle Database
# Creates the bulletproof manual lookup system for audit citations

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Determine repo root
$scriptDir = Split-Path -Parent $PSCommandPath
$repo = Resolve-Path (Join-Path $scriptDir '..')
Set-Location $repo

Write-Host "Building Manual Oracle Database..." -ForegroundColor Green

# Activate virtual environment (try .venv first, then venv)
$venvDirs = @(".venv", "venv")
$venvActivated = $false

foreach ($venvDir in $venvDirs) {
    $venvScript = Join-Path $repo "$venvDir\Scripts\Activate.ps1"
    if (Test-Path $venvScript) {
        & $venvScript
        Write-Host "Virtual environment activated: $venvDir" -ForegroundColor Yellow
        $venvActivated = $true
        break
    }
}

if (-not $venvActivated) {
    Write-Warning "No virtual environment found (.venv or venv)"
}

# Check if manual files exist
$manualPath = Join-Path $repo "AIOS_MANUAL.md"
$tocPath = Join-Path $repo "MANUAL_TOC.md"

if (-not (Test-Path $manualPath)) {
    throw "Manual not found: $manualPath"
}
if (-not (Test-Path $tocPath)) {
    throw "TOC not found: $tocPath"
}

Write-Host "Manual files found:" -ForegroundColor Yellow
Write-Host "  Manual: $manualPath" -ForegroundColor Gray
Write-Host "  TOC: $tocPath" -ForegroundColor Gray

# Build the oracle database
try {
    Write-Host "Initializing Manual Oracle..." -ForegroundColor Yellow
    
    $pythonCode = @"
import sys
sys.path.append('.')

from rag_core.manual_oracle import ManualOracle

# Initialize oracle (this will build the index)
oracle = ManualOracle('.')

# Get statistics
stats = oracle.get_oracle_stats()
print(f"Oracle built successfully!")
print(f"  Sections indexed: {stats['total_sections']}")
print(f"  Manual path: {stats['manual_path']}")
print(f"  TOC path: {stats['toc_path']}")
print(f"  Memory mapped: {stats['memory_mapped']}")
print(f"  Embedder available: {stats['embedder_available']}")
print(f"  Integrity verified: {stats['integrity_verified']}")

# Test a few lookups
print("\nTesting oracle lookups...")

# Test subsystem lookup
luna_sections = oracle.get_subsystem_sections('luna_core')
print(f"  Luna sections found: {len(luna_sections)}")

if luna_sections:
    print(f"  Sample Luna section: {luna_sections[0]['title']}")

# Test search
search_results = oracle.search_sections('timeout requests', 'luna_core', top_k=3)
print(f"  Search results for 'timeout requests': {len(search_results)}")

if search_results:
    print(f"  Top result: {search_results[0]['title']} (score: {search_results[0]['search_score']:.3f})")

# Test citation generation
test_finding = {
    'file_path': 'luna_core/test.py',
    'issue_type': 'requests_no_timeout',
    'verdict': 'FAIL',
    'issue_id': 'NET_TIMEOUT_REQUIRED'
}

citation = oracle.generate_audit_citation(test_finding, 'luna_core')
print(f"\nTest citation generated:")
print(f"  Citations: {citation['citations']}")
print(f"  Proof commands: {citation['proof_commands']}")
print(f"  Manual hash: {citation['manual_sha256'][:16]}...")

oracle.close()
print("\nOracle database built successfully!")
"@

    # Run the Python code
    py -c $pythonCode
    
    if ($LASTEXITCODE -ne 0) {
        throw "Oracle build failed with exit code $LASTEXITCODE"
    }
    
    Write-Host "`nManual Oracle Database built successfully!" -ForegroundColor Green
    Write-Host "Oracle index saved to: rag_core\manual_oracle\oracle_index.json" -ForegroundColor Gray
    
} catch {
    Write-Error "Failed to build oracle database: $_"
    exit 1
}

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Oracle is ready for audit system integration" -ForegroundColor Gray
Write-Host "2. Run audit system to test oracle lookups" -ForegroundColor Gray
Write-Host "3. Oracle provides bulletproof citations for all findings" -ForegroundColor Gray
