#!/usr/bin/env python3
"""
AIOS Repository Housekeeping Utility
Ensures clean separation between production (user-facing) and dev files.

Usage:
    py scripts\housekeep_repo.py [--dry-run] [--verify]

Author: Travis Miner + Kia
Version: 1.0.0
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Root directory
ROOT = Path(__file__).parent.parent

# Dev archive directory
ARCHIVE = ROOT / "archive_dev_core"

# Patterns to archive
DEV_PATTERNS = {
    "session_docs": [
        "SESSION_*.md",
        "AIOS_V5_INTEGRATION_*.md",
        "AIOS_V5_CONSCIOUSNESS_*.md",
        "AIOS_V5_FUSION_*.md",
        "AIOS_V5_REAL_*.md",
    ],
    "completion_docs": [
        "*_COMPLETE.md",
        "*_INTEGRATION_*.md",
        "REPO_CLEANUP_*.md",
    ],
    "upload_guides": [
        "CANONICAL_DOCS_V5_READY_FOR_GPT.md",
        "UPLOAD_TO_EXTERNAL_AUDITOR_GPT.md",
    ],
    "workspace_files": [
        "*.code-workspace",
    ],
    "test_scripts": [
        "test_*.py",
        "demo_*.py",
    ],
    "old_versions": [
        "*_old.py",
        "*_backup.py",
        "*_v1.py",
        "*_v2.py",
    ],
}

# Files to keep (always protect)
KEEP_FILES = {
    # Core documentation
    "AIOS_MANUAL.md",
    "AIOS_EXECUTIVE_SUMMARY.md",
    "MANUAL_TOC.md",
    "SYSTEM_CARD.md",
    "README.md",
    "README_INSTALL.md",
    "CHANGELOG.md",
    "LICENSE",
    "STANDARDS_MANIFEST.md",
    
    # V5 final status (user-facing)
    "AIOS_V5_FINAL_STATUS.md",
    
    # Integration docs (user-facing)
    "LINGUA_CALC_INTEGRATION_COMPLETE.md",
    "AUDITOR_ARBITER_INTEGRATION_SUMMARY.md",
    
    # Validation reports
    "V1_TESTING_COMPLETE.md",
    "AIOS_ENGINEERING_VALIDATION.md",
    "AIOS_TECHNICAL_VALIDATION_REPORT.md",
    "VALIDATION_QUICK_REFERENCE.md",
    
    # Infrastructure
    "FUTURE_ENHANCEMENTS.md",
    "main.py",
    "streamlit_app.py",
    "setup.ps1",
    "requirements.txt",
    "requirements-production.txt",
    "requirements-dashboard.txt",
    "pytest.ini",
    "pyproject.toml",
}

# Root test files (exceptions - keep these)
KEEP_ROOT_TEST_FILES = {
    "test_compression_architecture_verification.py",
    "test_modular_integration_full.py",
}


def log(message: str, level: str = "INFO"):
    """Simple logging function."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level:5s} | {message}")


def is_git_tracked(file_path: Path) -> bool:
    """Check if a file is tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(file_path)],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def check_archive_gitignored() -> bool:
    """Verify archive_dev_core is properly gitignored."""
    try:
        # Check if archive_dev_core is in .gitignore
        gitignore = ROOT / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if "archive_dev_core" in content:
                log("archive_dev_core found in .gitignore", "OK")
                
                # Check if it's tracked in git
                result = subprocess.run(
                    ["git", "ls-files"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True
                )
                if "archive_dev_core" in result.stdout:
                    log("WARNING: archive_dev_core files still tracked in git!", "WARN")
                    return False
                else:
                    log("archive_dev_core not tracked in git", "OK")
                    return True
            else:
                log("archive_dev_core NOT in .gitignore", "WARN")
                return False
        else:
            log(".gitignore not found", "ERROR")
            return False
    except Exception as e:
        log(f"Error checking gitignore: {e}", "ERROR")
        return False


def scan_for_dev_files() -> Dict[str, List[Path]]:
    """Scan for files matching dev patterns."""
    matches = {}
    
    for category, patterns in DEV_PATTERNS.items():
        matches[category] = []
        
        for pattern in patterns:
            # Search in root
            for file in ROOT.glob(pattern):
                if file.is_file() and file.name not in KEEP_FILES:
                    matches[category].append(file)
            
            # Search in scripts/
            if category == "test_scripts":
                scripts_dir = ROOT / "scripts"
                if scripts_dir.exists():
                    for file in scripts_dir.glob(pattern):
                        # Keep utility scripts, archive test/demo scripts
                        if file.is_file() and (
                            file.name.startswith("test_") or 
                            file.name.startswith("demo_")
                        ):
                            matches[category].append(file)
    
    # Also check for root test files (except those to keep)
    for test_file in ROOT.glob("test_*.py"):
        if test_file.name not in KEEP_ROOT_TEST_FILES:
            if test_file not in matches.get("test_scripts", []):
                matches.setdefault("test_scripts", []).append(test_file)
    
    return matches


def move_to_archive(file_path: Path, dry_run: bool = False) -> bool:
    """Move a file to archive_dev_core, preserving directory structure."""
    try:
        # Calculate relative path from ROOT
        rel_path = file_path.relative_to(ROOT)
        
        # Destination in archive
        dest = ARCHIVE / rel_path
        
        # Create parent directories
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(dest))
            log(f"Moved: {rel_path} -> archive_dev_core/{rel_path}", "MOVE")
        else:
            log(f"Would move: {rel_path} -> archive_dev_core/{rel_path}", "DRY")
        
        return True
    except Exception as e:
        log(f"Failed to move {file_path}: {e}", "ERROR")
        return False


def generate_report(matches: Dict[str, List[Path]], dry_run: bool = False) -> Dict:
    """Generate housekeeping report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "archive_gitignored": check_archive_gitignored(),
        "categories": {},
        "total_files": 0,
    }
    
    for category, files in matches.items():
        report["categories"][category] = {
            "count": len(files),
            "files": [str(f.relative_to(ROOT)) for f in files]
        }
        report["total_files"] += len(files)
    
    return report


def main():
    """Main housekeeping routine."""
    dry_run = "--dry-run" in sys.argv
    verify_only = "--verify" in sys.argv
    
    log("=" * 60)
    log("AIOS Repository Housekeeping")
    log("=" * 60)
    
    if dry_run:
        log("DRY RUN MODE - No files will be moved", "INFO")
    
    # Phase 1: Verify archive is gitignored
    log("\nPhase 1: Verify .gitignore")
    archive_ok = check_archive_gitignored()
    
    if verify_only:
        if archive_ok:
            log("\nVerification PASSED", "OK")
            return 0
        else:
            log("\nVerification FAILED", "ERROR")
            return 1
    
    # Phase 2: Scan for dev files
    log("\nPhase 2: Scanning for dev files...")
    matches = scan_for_dev_files()
    
    # Phase 3: Generate report
    report = generate_report(matches, dry_run)
    
    log(f"\nFound {report['total_files']} files to archive:")
    for category, data in report["categories"].items():
        if data["count"] > 0:
            log(f"  {category}: {data['count']} files")
    
    if report["total_files"] == 0:
        log("\nRepository is clean - no files to archive", "OK")
        return 0
    
    # Phase 4: Move files (if not dry-run)
    if not dry_run:
        log("\nPhase 4: Moving files to archive...")
        moved_count = 0
        failed_count = 0
        
        for category, files in matches.items():
            for file in files:
                if move_to_archive(file, dry_run=False):
                    moved_count += 1
                else:
                    failed_count += 1
        
        log(f"\nMoved {moved_count} files successfully")
        if failed_count > 0:
            log(f"Failed to move {failed_count} files", "WARN")
    
    # Save report
    report_path = ARCHIVE / "housekeeping_reports" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    log(f"\nReport saved: {report_path.relative_to(ROOT)}")
    
    log("\n" + "=" * 60)
    log("Housekeeping complete")
    log("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

