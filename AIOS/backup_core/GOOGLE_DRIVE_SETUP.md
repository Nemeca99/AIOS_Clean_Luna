# Google Drive Sync - Quick Setup Guide

**For Travis: Sync AIOS_Clean to your Google Drive folder**

---

## Option 1: Simple Setup (Recommended for You)

Since you already have a Google Drive folder with shared access, the easiest approach is:

### Use Google Drive Desktop App (No Code Needed)

1. **Install Google Drive for Desktop** (if not already)
   - Download: https://www.google.com/drive/download/
   
2. **Create sync folder**
   ```powershell
   # Create a folder in your Google Drive
   # It will automatically sync to: C:\Users\YOUR_USERNAME\Google Drive\
   ```

3. **Copy AIOS_Clean**
   ```powershell
   # Simply copy your AIOS_Clean to the Google Drive folder
   xcopy /E /I F:\AIOS_Clean "C:\Users\nemec\Google Drive\AIOS_Clean"
   ```

**Done!** Google Drive handles the sync automatically.

---

## Option 2: API-Based Sync (Automated, Requires Setup)

For automated syncs via Python scripts.

### Step 1: Get OAuth2 Credentials (One-Time)

1. Go to https://console.cloud.google.com/
2. Create new project: "AIOS Backup"
3. Enable **Google Drive API**:
   - Go to "APIs & Services" → "Enable APIs and Services"
   - Search "Google Drive API" → Click "Enable"
4. Create credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: **Desktop app**
   - Name: "AIOS Backup Client"
   - Click "Create"
5. Download JSON:
   - Click download button (⬇️) next to your client
   - Save as: `F:\AIOS_Clean\backup_core\config\gdrive_credentials.json`

### Step 2: Authenticate (Browser Popup)

```powershell
python -m backup_core.google_drive_sync --auth
```

This will:
- Open browser automatically
- Ask you to sign in with Google
- Request permission to access Drive
- Save token to `backup_core/config/gdrive_token.pickle`

**You only do this once.** Token auto-refreshes.

### Step 3: Sync to Your Folder

```powershell
# Your folder ID: 1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF
python -m backup_core.google_drive_sync --sync "1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF"
```

This will:
- Create a timestamped backup folder in your Drive folder
- Upload all `*_core` directories
- Upload scripts, tests, root files
- Skip large/temp files (*.faiss, *.db, .venv, etc.)
- Show progress and summary

---

## Option 3: Use Rclone (CLI Tool)

**Fastest for large syncs, no coding needed:**

1. **Install rclone:**
   ```powershell
   winget install Rclone.Rclone
   ```

2. **Configure rclone for Google Drive:**
   ```powershell
   rclone config
   # Follow prompts to add Google Drive remote
   ```

3. **Sync AIOS_Clean:**
   ```powershell
   rclone sync F:\AIOS_Clean "gdrive:AIOS_Clean" --exclude ".venv/**" --exclude "*.pyc" --exclude "__pycache__/**" --progress
   ```

---

## Which Option for You?

**Recommended:** **Option 1 (Google Drive Desktop)**
- ✅ Zero setup (you probably already have it)
- ✅ Auto-syncs in background
- ✅ Works with your existing shared folder
- ✅ No API credentials needed

**Option 2 (Python API):**
- Use if you want automated backups via scripts
- Good for scheduled backups
- Requires OAuth2 setup (10 minutes)

**Option 3 (Rclone):**
- Best for one-time large syncs
- Faster than API
- Good CLI control

---

## For Python API Setup (Option 2 Details)

### Quick Start

```powershell
# 1. Get your credentials JSON from Google Cloud Console
# 2. Save as: backup_core/config/gdrive_credentials.json

# 3. Authenticate (browser popup)
python -m backup_core.google_drive_sync --auth

# 4. Sync to your folder
python -m backup_core.google_drive_sync --sync "1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF"
```

### What Gets Uploaded

**Cores:** luna_core, carma_core, dream_core, data_core, rag_core, consciousness_core, etc.  
**Scripts:** scripts/ directory  
**Tests:** tests/ directory  
**Root Files:** main.py, README.md, AIOS_MANUAL.md, requirements.txt, etc.

**Excluded:** .venv, *.pyc, __pycache__, *.faiss, *.db, *.log, archive_dev_core, streamlit_core

### Sync Result

```
Uploaded: 145 files
Skipped: 89 files
Failed: 0 files
Total size: 15.2 MB
Cores synced: 12

Backup folder ID: abc123...
Share link: https://drive.google.com/drive/folders/abc123...
```

---

## Security Notes

**DO NOT COMMIT:**
- `backup_core/config/gdrive_token.pickle` (your access token)
- `backup_core/config/gdrive_credentials.json` (your OAuth2 client secret)

Add to `.gitignore`:
```
backup_core/config/gdrive_*.json
backup_core/config/gdrive_*.pickle
```

---

## Travis's Folder

**URL:** https://drive.google.com/drive/folders/1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF?usp=sharing  
**Folder ID:** `1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF`  
**Access:** Anyone with link (view only)

**Sync Command:**
```powershell
python -m backup_core.google_drive_sync --sync "1vlF1xmstfdcc8ZhKts2hAiZqXaGvzjyF"
```

---

**Which should you use?**

For you, Travis: **Just use Google Drive Desktop app**. Drag and drop AIOS_Clean into your Google Drive folder. Done. No API, no OAuth2, no complexity.

The Python API is there if you want automated scheduled backups later.

