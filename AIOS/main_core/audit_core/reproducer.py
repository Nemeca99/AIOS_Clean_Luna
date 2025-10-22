#!/usr/bin/env python3
"""
Reproducer Bundle Generator
Creates ZIP with everything needed to reproduce a failing audit locally.
"""

import json
import zipfile
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class ReproducerBundler:
    """
    Generate reproducer bundles on audit failures.
    
    Bundle includes:
    - audit_report.json
    - policy.yaml
    - allowlist.json
    - requirements.txt
    - environment.txt
    - reproduce.py script
    """
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
    
    def create_bundle(self, 
                     audit_report: Dict,
                     output_dir: Path = None) -> Path:
        """
        Create reproducer bundle ZIP.
        
        Args:
            audit_report: Full audit report dict
            output_dir: Where to save bundle (default: reports/)
        
        Returns:
            Path to created ZIP file
        """
        if output_dir is None:
            output_dir = self.root / "reports"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_name = f"reproducer_{timestamp}.zip"
        bundle_path = output_dir / bundle_name
        
        logger.info(f"Creating reproducer bundle: {bundle_name}")
        
        with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. Audit report
            report_json = json.dumps(audit_report, indent=2)
            zf.writestr('audit_report.json', report_json)
            
            # 2. Policy
            policy_path = self.root / "main_core" / "audit_core" / "config" / "policy.yaml"
            if policy_path.exists():
                zf.write(policy_path, 'policy.yaml')
            
            # 3. Allowlist
            allowlist_path = self.root / "main_core" / "audit_core" / "config" / "allowlist.json"
            if allowlist_path.exists():
                zf.write(allowlist_path, 'allowlist.json')
            
            # 4. Requirements
            req_path = self.root / "requirements.txt"
            if req_path.exists():
                zf.write(req_path, 'requirements.txt')
            
            # 5. Environment info
            env_info = self._collect_environment_info()
            zf.writestr('environment.txt', env_info)
            
            # 6. Reproduce script
            reproduce_script = self._generate_reproduce_script(audit_report)
            zf.writestr('reproduce.py', reproduce_script)
            
            # 7. README
            readme = self._generate_readme(audit_report)
            zf.writestr('README.md', readme)
        
        logger.info(f"Bundle created: {bundle_path}")
        return bundle_path
    
    def _collect_environment_info(self) -> str:
        """Collect environment information."""
        info = []
        
        # Python version
        try:
            result = subprocess.run(
                ['python', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            info.append(f"Python: {result.stdout.strip()}")
        except:
            info.append("Python: unknown")
        
        # Git commit
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            info.append(f"Commit: {result.stdout.strip()}")
        except:
            info.append("Commit: unknown")
        
        # Git branch
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            info.append(f"Branch: {result.stdout.strip()}")
        except:
            info.append("Branch: unknown")
        
        # OS
        import platform
        info.append(f"OS: {platform.system()} {platform.release()}")
        info.append(f"Platform: {platform.platform()}")
        
        # Timestamp
        info.append(f"Captured: {datetime.now().isoformat()}")
        
        return '\n'.join(info)
    
    def _generate_reproduce_script(self, audit_report: Dict) -> str:
        """Generate reproduce.py script."""
        script = '''#!/usr/bin/env python3
"""
Reproducer Script - Reproduce audit failure locally.

Usage:
    python reproduce.py                    # Reproduce full audit
    python reproduce.py --core CORE_NAME   # Reproduce specific core
"""

import sys
import json
import subprocess
from pathlib import Path

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Reproduce audit failure')
    parser.add_argument('--core', help='Specific core to audit')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("REPRODUCER - Audit Failure Reproduction")
    print("=" * 60)
    
    # Load report
    with open('audit_report.json') as f:
        report = json.load(f)
    
    print(f"\\nOriginal audit:")
    print(f"  Average Score: {report.get('average_score', 'N/A')}")
    print(f"  Production Ready: {report.get('production_ready', 'N/A')}")
    print(f"  Critical Cores: {report.get('critical_count', 'N/A')}")
    
    # Environment check
    print("\\nEnvironment info:")
    with open('environment.txt') as f:
        for line in f:
            print(f"  {line.strip()}")
    
    print("\\n" + "=" * 60)
    print("To reproduce this audit:")
    print("  1. Ensure you're on the same commit")
    print("  2. Install requirements: pip install -r requirements.txt")
    print("  3. Run audit:")
    
    if args.core:
        print(f"     py main.py --audit --core {args.core}")
    else:
        print("     py main.py --audit")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
'''
        return script
    
    def _generate_readme(self, audit_report: Dict) -> str:
        """Generate README for bundle."""
        readme = f'''# Audit Failure Reproducer Bundle

**Generated**: {datetime.now().isoformat()}
**Average Score**: {audit_report.get('average_score', 'N/A')}
**Production Ready**: {audit_report.get('production_ready', 'N/A')}

## Contents

- `audit_report.json` - Full audit report
- `policy.yaml` - Policy configuration
- `allowlist.json` - Suppression allowlist
- `requirements.txt` - Python dependencies
- `environment.txt` - Environment information
- `reproduce.py` - Reproduction script
- `README.md` - This file

## Usage

### Quick Start

```bash
# Extract bundle
unzip reproducer_*.zip
cd reproducer_*

# View report
python reproduce.py

# Install dependencies
pip install -r requirements.txt

# Reproduce full audit
py main.py --audit

# Reproduce specific core
py main.py --audit --core carma_core
```

### Environment

See `environment.txt` for:
- Python version
- Git commit/branch
- OS platform
- Capture timestamp

### Failed Cores

'''
        
        # Add failed cores info
        cores = audit_report.get('cores', [])
        failed = [c for c in cores if c.get('status') in ['CRITICAL', 'WARNING']]
        
        if failed:
            readme += "The following cores had issues:\n\n"
            for core in failed:
                readme += f"- **{core.get('core_name')}**: {core.get('status')} (score: {core.get('score')})\n"
        else:
            readme += "No cores failed (but overall production gate failed).\n"
        
        readme += '''
## Troubleshooting

If reproduction fails:
1. Check you're on the exact commit (see environment.txt)
2. Ensure all dependencies match (pip list vs requirements.txt)
3. Verify environment variables match
4. Check for local modifications (git status)

## Support

For questions, see: docs/audit/
'''
        
        return readme

