#!/usr/bin/env python3
"""
Git Integration for Audit System
Tracks audit results with git metadata (commit hash, branch, author)
"""

import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class GitIntegration:
    """Integrate audit results with git metadata."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def get_git_metadata(self) -> Dict:
        """Get current git metadata."""
        metadata = {
            'commit_hash': self._run_git_command(['rev-parse', 'HEAD']),
            'branch': self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD']),
            'author': self._run_git_command(['config', 'user.name']),
            'email': self._run_git_command(['config', 'user.email']),
            'commit_message': self._run_git_command(['log', '-1', '--pretty=%B']),
            'is_dirty': self._is_working_tree_dirty(),
            'timestamp': datetime.now().isoformat()
        }
        
        return metadata
    
    def _run_git_command(self, args: list) -> Optional[str]:
        """Run a git command and return output."""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Git command failed: {e}")
        return None
    
    def _is_working_tree_dirty(self) -> bool:
        """Check if working tree has uncommitted changes."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def enrich_report(self, report: Dict) -> Dict:
        """Add git metadata to audit report."""
        git_metadata = self.get_git_metadata()
        report['git_metadata'] = git_metadata
        
        return report
    
    def save_trend_data(self, report: Dict, trend_file: Path = None):
        """Save audit result to trend tracking file."""
        if trend_file is None:
            trend_file = self.repo_path / "reports" / "audit_trends.jsonl"
        
        # Ensure directory exists
        trend_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract trend data
        trend_entry = {
            'timestamp': report.get('git_metadata', {}).get('timestamp', datetime.now().isoformat()),
            'commit_hash': report.get('git_metadata', {}).get('commit_hash', 'unknown'),
            'branch': report.get('git_metadata', {}).get('branch', 'unknown'),
            'average_score': report['summary']['average_score'],
            'production_ready': report['summary']['production_ready'],
            'critical_count': report['summary']['issue_counts']['critical'],
            'performance_count': report['summary']['issue_counts']['performance'],
            'safety_count': report['summary']['issue_counts']['safety']
        }
        
        # Append to JSONL file (newline-delimited JSON for time series)
        with open(trend_file, 'a') as f:
            f.write(json.dumps(trend_entry) + '\n')
        
        logger.info(f"Trend data saved to {trend_file}")
    
    def get_score_delta_from_last_commit(self, current_score: float) -> Optional[float]:
        """Get score change since last commit."""
        trend_file = self.repo_path / "reports" / "audit_trends.jsonl"
        
        if not trend_file.exists():
            return None
        
        try:
            # Read last line
            with open(trend_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) < 2:
                return None
            
            # Parse last entry
            last_entry = json.loads(lines[-2].strip())  # -2 because current is -1
            last_score = last_entry['average_score']
            
            return current_score - last_score
            
        except Exception as e:
            logger.debug(f"Failed to get score delta: {e}")
            return None


def run_meta_audit_as_check():
    """Run meta-audit and report results."""
    from pathlib import Path
    
    audit_path = Path(__file__).parent
    meta = MetaAudit(audit_path)
    
    passed, issues = meta.run_meta_audit()
    
    if not passed:
        print("\n⚠️  META-AUDIT WARNING: Audit system has issues")
        for issue in issues:
            print(f"   - {issue}")
        print("\n   The audit system itself needs attention!")
    
    return passed


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    audit_path = Path(__file__).parent
    meta = MetaAudit(audit_path)
    passed, issues = meta.run_meta_audit()
    
    print("\n" + "=" * 60)
    print("META-AUDIT RESULTS")
    print("=" * 60)
    
    if passed:
        print("\n✅ PASSED - Audit system is trustworthy")
    else:
        print(f"\n❌ FAILED - {len(issues)} issues found")
        for issue in issues:
            print(f"   - {issue}")
    
    sys.exit(0 if passed else 1)

