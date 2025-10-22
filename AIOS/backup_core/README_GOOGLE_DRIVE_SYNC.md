# Google Drive Sync for AIOS Backup

**Alternative to GitHub backup - simple folder sync**

## Setup (One-Time)

### 1. Get Google Drive API Credentials

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Desktop app**
6. Download the JSON credentials file
7. Save as: `backup_core/config/gdrive_credentials.json`

### 2. Authenticate

```powershell
python -m backup_core.google_drive_sync --auth
```

This will:
- Open browser for Google login
- Request Drive access permission
- Save token to `backup_core/config/gdrive_token.pickle`

**You only need to do this once.** Token will auto-refresh.

---

## Usage

### Quick Sync to Your Folder

```powershell
# Using your folder URL
python -m backup_core.google_drive_sync --sync "https://drive.google.com/drive/folders/1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF?usp=sharing"

# Or using folder ID directly
python -m backup_core.google_drive_sync --sync "1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF"
```

### Custom Backup Name

```powershell
python -m backup_core.google_drive_sync --sync "YOUR_FOLDER_ID" --name "AIOS_Backup_v5.1.1"
```

---

## What Gets Synced

**Included:**
- All `*_core` directories (luna, carma, dream, data, rag, etc.)
- `scripts/` directory
- `tests/` directory
- Root files: main.py, README.md, AIOS_MANUAL.md, requirements.txt, etc.

**Excluded (Smart Defaults):**
- `*.pyc`, `__pycache__`, `.venv`, `venv`
- `.git`, `.pytest_cache`, `.hypothesis`
- `*.faiss`, `*.db`, `*.sqlite`, `*.log` (data files)
- `archive_dev_core`, `streamlit_core` (large/vendor)
- Compiled binaries (`*.pyd`, `*.dll`, `*.so`)

**File Size Limit:** 100 MB per file (skips large files automatically)

---

## From Python Code

```python
from backup_core.google_drive_sync import GoogleDriveSync

# Initialize
sync = GoogleDriveSync()

# Authenticate
if sync.authenticate():
    # Sync to your folder
    result = sync.sync_workspace(
        target_folder_id="1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF",
        backup_name="AIOS_Clean_Backup"
    )
    
    print(f"Uploaded: {result['stats']['uploaded']} files")
    print(f"Folder: {result['folder_id']}")
```

---

## Sync State

After each sync, state is saved to:
`backup_core/config/gdrive_sync_state.json`

```json
{
  "backup_folder_id": "...",
  "backup_name": "AIOS_Clean_2025-10-17",
  "timestamp": "2025-10-17T18:50:00",
  "stats": {
    "uploaded": 145,
    "skipped": 89,
    "failed": 0,
    "total_bytes": 12345678,
    "cores_synced": ["luna_core", "carma_core", ...]
  }
}
```

---

## Comparison to GitHub Backup

| Feature | GitHub | Google Drive |
|---------|--------|--------------|
| Version Control | ✅ Full git history | ❌ Simple folder sync |
| File Size Limits | 100 MB | 15 GB (free tier) |
| Setup Complexity | Medium (SSH keys) | Easy (OAuth2 browser) |
| Sharing | Public/Private repos | Shared links |
| Cost | Free (public) / $4/mo (private) | Free (15 GB) / $1.99/mo (100 GB) |
| Best For | Code versioning | Quick backups, sharing |

---

## Security Notes

- **Token File:** `gdrive_token.pickle` contains OAuth2 access token
  - Add to `.gitignore`: `backup_core/config/gdrive_token.pickle`
  - Never commit this file!

- **Credentials File:** `gdrive_credentials.json` contains OAuth2 client ID/secret
  - Add to `.gitignore`: `backup_core/config/gdrive_credentials.json`
  - This is your API key - keep private!

- **Shared Links:** Anyone with the link can view (not edit)
  - Don't share private data via public links
  - Use Google Drive access controls for sensitive data

---

## Troubleshooting

### "Credentials file not found"
Save your OAuth2 credentials JSON as `backup_core/config/gdrive_credentials.json`

### "Authentication failed"
1. Delete `backup_core/config/gdrive_token.pickle`
2. Run `--auth` again
3. Make sure you allow Drive access in the browser popup

### "Quota exceeded"
Google Drive free tier: 15 GB total
- Check your Drive storage
- Increase `exclude_patterns` to skip more files
- Lower `max_size_mb` limit

### "Upload timeouts"
Large files may timeout. Increase timeout or exclude:
```python
sync.sync_workspace(folder_id, exclude_patterns=['*.faiss', '*.db', 'large_files/'])
```

---

## Your Folder

**URL:** https://drive.google.com/drive/folders/1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF?usp=sharing  
**Folder ID:** `1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF`  
**Access:** Anyone with link (view only)

**Quick Sync:**
```powershell
python -m backup_core.google_drive_sync --sync "1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF"
```

---

**Travis Miner | AIOS_clean**  
**Version:** 5.1.1  
**Date:** October 17, 2025

