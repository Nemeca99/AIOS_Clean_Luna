#!/usr/bin/env pwsh
# AIOS Google Drive Sync Script (Using rclone)
# Travis Miner | AIOS_clean

Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "AIOS → GOOGLE DRIVE SYNC (rclone)" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""

# Check if rclone is configured
$rconfigCheck = rclone config show AIOS_Cloean 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ rclone not configured (looking for 'AIOS_Cloean' remote)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run this ONCE to configure:" -ForegroundColor Yellow
    Write-Host "  rclone config" -ForegroundColor White
    Write-Host ""
    Write-Host "Follow these prompts:" -ForegroundColor Yellow
    Write-Host "  n) New remote" -ForegroundColor Gray
    Write-Host "  name> gdrive" -ForegroundColor Gray
    Write-Host "  Storage> drive (Google Drive)" -ForegroundColor Gray
    Write-Host "  client_id> (just press Enter)" -ForegroundColor Gray
    Write-Host "  client_secret> (just press Enter)" -ForegroundColor Gray
    Write-Host "  scope> 1 (Full access)" -ForegroundColor Gray
    Write-Host "  service_account_file> (just press Enter)" -ForegroundColor Gray
    Write-Host "  Edit advanced config> n" -ForegroundColor Gray
    Write-Host "  Use web browser> y" -ForegroundColor Gray
    Write-Host "  (Browser opens - sign in with Google)" -ForegroundColor Gray
    Write-Host "  Configure as team drive> n" -ForegroundColor Gray
    Write-Host "  Keep this remote> y" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "✅ rclone configured" -ForegroundColor Green
Write-Host ""

# Sync parameters  
$source = "F:\AIOS_Clean"
$dest = "AIOS_Cloean:AIOS_Clean"  # Using your configured remote name

# Exclusions (smart defaults)
$exclude = @(
    "--exclude", ".venv/**",
    "--exclude", "venv/**",
    "--exclude", "__pycache__/**",
    "--exclude", "*.pyc",
    "--exclude", ".git/**",
    "--exclude", ".pytest_cache/**",
    "--exclude", ".hypothesis/**",
    "--exclude", "*.faiss",
    "--exclude", "*.db",
    "--exclude", "*.sqlite",
    "--exclude", "*.log",
    "--exclude", "archive_dev_core/**",
    "--exclude", "streamlit_core/**",
    "--exclude", "*.pyd",
    "--exclude", "*.dll",
    "--exclude", "target/**",
    "--exclude", "build/**",
    "--exclude", "dist/**"
)

Write-Host "Syncing AIOS_Clean to Google Drive..." -ForegroundColor Yellow
Write-Host "  Source: $source" -ForegroundColor Gray
Write-Host "  Destination: $dest" -ForegroundColor Gray
Write-Host "  Rate limit: 10 TPS (prevents Google API quota errors)" -ForegroundColor Gray
Write-Host ""

# Sync with progress and rate limiting (hardcoded to avoid quota issues)
rclone sync $source $dest @exclude --progress --stats 10s --transfers 4 --tpslimit 10

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "="*70 -ForegroundColor Green
    Write-Host "SYNC COMPLETE!" -ForegroundColor Green
    Write-Host "="*70 -ForegroundColor Green
    Write-Host ""
    Write-Host "Your AIOS_Clean is now in Google Drive" -ForegroundColor Green
    Write-Host "Check: https://drive.google.com/drive/folders/1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Sync failed" -ForegroundColor Red
    Write-Host ""
}

