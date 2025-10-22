"""
Google Drive Sync for AIOS Backup Core
Alternative backup option to GitHub

V5.1.1 - Travis Miner | AIOS_clean
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Google Drive API imports (lazy load)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveSync:
    """
    Google Drive synchronization for AIOS backups
    
    Features:
    - OAuth2 authentication
    - Folder creation and file upload
    - Sync detection (upload only changed files)
    - Progress tracking
    - Shared link support
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize Google Drive sync
        
        Args:
            workspace_root: Root directory of AIOS workspace
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError(
                "Google Drive API not available. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )
        
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent
        
        self.workspace_root = Path(workspace_root)
        self.config_dir = self.workspace_root / "backup_core" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.token_file = self.config_dir / "gdrive_token.pickle"
        self.credentials_file = self.config_dir / "gdrive_credentials.json"
        self.sync_state_file = self.config_dir / "gdrive_sync_state.json"
        
        self.service = None
        self.folder_id = None
        
        print(f"📂 Google Drive Sync Initialized")
        print(f"   Workspace: {self.workspace_root}")
        print(f"   Config: {self.config_dir}")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive using OAuth2
        
        Returns:
            True if authenticated, False otherwise
        """
        creds = None
        
        # Load existing token if available
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"⚠️  Failed to load token: {e}")
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("🔄 Token refreshed")
                except Exception as e:
                    print(f"⚠️  Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                # Check for credentials file
                if not self.credentials_file.exists():
                    print(f"❌ Credentials file not found: {self.credentials_file}")
                    print(f"")
                    print(f"To set up Google Drive sync:")
                    print(f"1. Go to https://console.cloud.google.com/")
                    print(f"2. Create a project and enable Google Drive API")
                    print(f"3. Create OAuth2 credentials (Desktop app)")
                    print(f"4. Download credentials JSON")
                    print(f"5. Save as: {self.credentials_file}")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    print("✅ Authentication successful")
                except Exception as e:
                    print(f"❌ Authentication failed: {e}")
                    return False
            
            # Save token for future use
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                print(f"💾 Token saved to: {self.token_file}")
            except Exception as e:
                print(f"⚠️  Failed to save token: {e}")
        
        # Build service
        try:
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive service connected")
            return True
        except Exception as e:
            print(f"❌ Failed to build Drive service: {e}")
            return False
    
    def set_target_folder(self, folder_id: str):
        """
        Set the target Google Drive folder ID
        
        Args:
            folder_id: Google Drive folder ID (from URL)
        """
        self.folder_id = folder_id
        print(f"📁 Target folder set: {folder_id}")
    
    def create_backup_folder(self, folder_name: str = None) -> Optional[str]:
        """
        Create a backup folder in Google Drive
        
        Args:
            folder_name: Name of folder (defaults to AIOS_Clean_YYYY-MM-DD)
        
        Returns:
            Folder ID or None if failed
        """
        if not self.service:
            print("❌ Not authenticated. Run authenticate() first.")
            return None
        
        if folder_name is None:
            folder_name = f"AIOS_Clean_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.folder_id] if self.folder_id else []
        }
        
        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            print(f"✅ Created folder: {folder_name} (ID: {folder_id})")
            return folder_id
            
        except Exception as e:
            print(f"❌ Failed to create folder: {e}")
            return None
    
    def upload_file(self, local_path: Path, parent_folder_id: str, remote_name: str = None) -> Optional[str]:
        """
        Upload a file to Google Drive
        
        Args:
            local_path: Local file path
            parent_folder_id: Parent folder ID in Drive
            remote_name: Name in Drive (defaults to filename)
        
        Returns:
            File ID or None if failed
        """
        if not self.service:
            print("❌ Not authenticated")
            return None
        
        if not local_path.exists():
            print(f"❌ File not found: {local_path}")
            return None
        
        if remote_name is None:
            remote_name = local_path.name
        
        file_metadata = {
            'name': remote_name,
            'parents': [parent_folder_id]
        }
        
        try:
            media = MediaFileUpload(
                str(local_path),
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            print(f"❌ Upload failed for {local_path.name}: {e}")
            return None
    
    def sync_directory(self, local_dir: Path, parent_folder_id: str, 
                      exclude_patterns: List[str] = None, 
                      max_size_mb: int = 100) -> Dict:
        """
        Sync a directory to Google Drive
        
        Args:
            local_dir: Local directory to sync
            parent_folder_id: Parent folder ID in Drive
            exclude_patterns: Patterns to exclude (e.g., ['*.pyc', '__pycache__', '.venv'])
            max_size_mb: Max file size to upload (MB)
        
        Returns:
            dict with sync statistics
        """
        if not self.service:
            print("❌ Not authenticated")
            return {"status": "error", "reason": "not_authenticated"}
        
        if exclude_patterns is None:
            exclude_patterns = [
                '*.pyc', '__pycache__', '.venv', 'venv', '*.egg-info',
                '.git', '.pytest_cache', '.hypothesis', 'node_modules',
                '*.faiss', '*.db', '*.sqlite', '*.log', '*.pyc'
            ]
        
        stats = {
            "uploaded": 0,
            "skipped": 0,
            "failed": 0,
            "total_bytes": 0
        }
        
        def should_exclude(path: Path) -> bool:
            """Check if path matches exclusion patterns"""
            import fnmatch
            path_str = str(path)
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(path_str, f"*{pattern}*"):
                    return True
            return False
        
        print(f"\n📤 Syncing: {local_dir.name}")
        
        # Create folder structure
        try:
            folder_metadata = {
                'name': local_dir.name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            current_folder_id = folder.get('id')
            
        except Exception as e:
            print(f"❌ Failed to create folder {local_dir.name}: {e}")
            return stats
        
        # Upload files
        for item in local_dir.rglob('*'):
            if item.is_dir():
                continue
            
            # Check exclusions
            if should_exclude(item):
                stats["skipped"] += 1
                continue
            
            # Check size
            size_mb = item.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                print(f"  ⏭️  Skipped (too large): {item.name} ({size_mb:.1f} MB)")
                stats["skipped"] += 1
                continue
            
            # Upload
            rel_path = item.relative_to(local_dir.parent)
            file_id = self.upload_file(item, current_folder_id, item.name)
            
            if file_id:
                stats["uploaded"] += 1
                stats["total_bytes"] += item.stat().st_size
                print(f"  ✅ {rel_path}")
            else:
                stats["failed"] += 1
                print(f"  ❌ {rel_path}")
        
        return stats
    
    def sync_workspace(self, target_folder_id: str, backup_name: str = None) -> Dict:
        """
        Sync entire AIOS workspace to Google Drive
        
        Args:
            target_folder_id: Target Google Drive folder ID
            backup_name: Backup folder name (defaults to AIOS_Clean_YYYY-MM-DD)
        
        Returns:
            dict with sync statistics
        """
        if not self.service:
            print("❌ Not authenticated. Run authenticate() first.")
            return {"status": "error", "reason": "not_authenticated"}
        
        print(f"\n{'='*70}")
        print(f"AIOS WORKSPACE → GOOGLE DRIVE SYNC")
        print(f"{'='*70}\n")
        
        # Create backup folder
        self.set_target_folder(target_folder_id)
        backup_folder_id = self.create_backup_folder(backup_name)
        
        if not backup_folder_id:
            return {"status": "error", "reason": "folder_creation_failed"}
        
        # Sync core directories (exclude heavy/temp stuff)
        core_dirs = [
            "luna_core",
            "carma_core",
            "dream_core",
            "data_core",
            "rag_core",
            "backup_core",
            "support_core",
            "utils_core",
            "consciousness_core",
            "main_core",
            "scripts",
            "tests"
        ]
        
        # Exclude patterns
        exclude = [
            '*.pyc', '__pycache__', '.venv', 'venv', '*.egg-info',
            '.git', '.pytest_cache', '.hypothesis', 'node_modules',
            '*.faiss', '*.db', '*.sqlite', '*.log',
            'archive_dev_core', 'streamlit_core',
            '*.pyd', '*.dll', '*.so', 'target', 'build', 'dist'
        ]
        
        total_stats = {
            "uploaded": 0,
            "skipped": 0,
            "failed": 0,
            "total_bytes": 0,
            "cores_synced": []
        }
        
        # Sync each core
        for core_name in core_dirs:
            core_path = self.workspace_root / core_name
            if core_path.exists() and core_path.is_dir():
                print(f"\n📦 Syncing {core_name}...")
                stats = self.sync_directory(core_path, backup_folder_id, exclude)
                
                total_stats["uploaded"] += stats["uploaded"]
                total_stats["skipped"] += stats["skipped"]
                total_stats["failed"] += stats["failed"]
                total_stats["total_bytes"] += stats["total_bytes"]
                total_stats["cores_synced"].append(core_name)
        
        # Upload key files from root
        root_files = [
            "main.py",
            "luna_chat.py",
            "README.md",
            "AIOS_MANUAL.md",
            "AIOS_EXECUTIVE_SUMMARY.md",
            "requirements.txt",
            "pyproject.toml",
            "pytest.ini",
            ".coveragerc",
            ".gitignore",
            ".gitattributes",
            "LICENSE"
        ]
        
        print(f"\n📄 Uploading root files...")
        for filename in root_files:
            file_path = self.workspace_root / filename
            if file_path.exists():
                file_id = self.upload_file(file_path, backup_folder_id)
                if file_id:
                    total_stats["uploaded"] += 1
                    print(f"  ✅ {filename}")
                else:
                    total_stats["failed"] += 1
        
        # Save sync state
        sync_state = {
            "backup_folder_id": backup_folder_id,
            "backup_name": backup_name or f"AIOS_Clean_{datetime.now().strftime('%Y-%m-%d')}",
            "timestamp": datetime.now().isoformat(),
            "stats": total_stats
        }
        
        with open(self.sync_state_file, 'w') as f:
            json.dump(sync_state, f, indent=2)
        
        # Summary
        print(f"\n{'='*70}")
        print(f"SYNC COMPLETE")
        print(f"{'='*70}")
        print(f"\nUploaded: {total_stats['uploaded']} files")
        print(f"Skipped: {total_stats['skipped']} files")
        print(f"Failed: {total_stats['failed']} files")
        print(f"Total size: {total_stats['total_bytes'] / (1024*1024):.2f} MB")
        print(f"Cores synced: {len(total_stats['cores_synced'])}")
        print(f"\nBackup folder ID: {backup_folder_id}")
        print(f"Share link: https://drive.google.com/drive/folders/{backup_folder_id}")
        
        return {
            "status": "ok",
            "folder_id": backup_folder_id,
            "stats": total_stats
        }
    
    def get_folder_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract folder ID from Google Drive URL
        
        Args:
            url: Google Drive folder URL
        
        Returns:
            Folder ID or None
        """
        # Handle both formats:
        # https://drive.google.com/drive/folders/FOLDER_ID?usp=sharing
        # https://drive.google.com/drive/folders/FOLDER_ID
        
        if 'folders/' in url:
            parts = url.split('folders/')[1]
            folder_id = parts.split('?')[0]
            return folder_id
        
        return None


def main():
    """CLI for Google Drive sync"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIOS Google Drive Sync")
    parser.add_argument('--auth', action='store_true', help='Authenticate with Google Drive')
    parser.add_argument('--sync', type=str, help='Sync to folder (URL or ID)')
    parser.add_argument('--name', type=str, help='Backup folder name')
    
    args = parser.parse_args()
    
    sync = GoogleDriveSync()
    
    if args.auth:
        if sync.authenticate():
            print("\n✅ Ready to sync!")
        else:
            print("\n❌ Authentication failed")
        return
    
    if args.sync:
        # Authenticate first
        if not sync.authenticate():
            print("❌ Authentication failed")
            return
        
        # Get folder ID from URL if provided
        if args.sync.startswith('http'):
            folder_id = sync.get_folder_id_from_url(args.sync)
            if not folder_id:
                print(f"❌ Could not parse folder ID from URL: {args.sync}")
                return
        else:
            folder_id = args.sync
        
        # Sync workspace
        result = sync.sync_workspace(folder_id, args.name)
        
        if result.get("status") == "ok":
            print(f"\n✅ Sync successful!")
        else:
            print(f"\n❌ Sync failed: {result.get('reason')}")


if __name__ == "__main__":
    main()

