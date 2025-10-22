#!/usr/bin/env python3
"""
Multi-Repo Manifest Support
Empire mode. Audit across multiple repositories.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class MultiRepoAuditor:
    """
    Audit multiple projects from a manifest file.
    
    Features:
    - audit_manifest.yaml configuration
    - Per-project gates
    - Global roll-up report
    - Parallel project auditing
    """
    
    def __init__(self, manifest_file: Path = None):
        if manifest_file is None:
            manifest_file = Path("audit_manifest.yaml")
        
        self.manifest_file = manifest_file
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load manifest from YAML file."""
        if not self.manifest_file.exists():
            logger.warning(f"Manifest file not found: {self.manifest_file}")
            return {'projects': []}
        
        try:
            with open(self.manifest_file) as f:
                manifest = yaml.safe_load(f)
            
            logger.info(f"Loaded manifest with {len(manifest.get('projects', []))} projects")
            return manifest
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            return {'projects': []}
    
    def get_projects(self) -> List[Dict]:
        """Get list of projects to audit."""
        return self.manifest.get('projects', [])
    
    def validate_manifest(self) -> tuple:
        """
        Validate manifest structure.
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        projects = self.manifest.get('projects', [])
        
        if not projects:
            errors.append("No projects defined in manifest")
        
        for i, project in enumerate(projects):
            # Required fields
            if 'name' not in project:
                errors.append(f"Project {i}: missing 'name' field")
            
            if 'path' not in project:
                errors.append(f"Project {i}: missing 'path' field")
            
            # Validate path exists
            if 'path' in project:
                project_path = Path(project['path'])
                if not project_path.exists():
                    errors.append(f"Project '{project.get('name')}': path not found: {project['path']}")
        
        return len(errors) == 0, errors
    
    def generate_rollup_report(self, project_results: List[Dict]) -> Dict:
        """
        Generate unified roll-up report across all projects.
        
        Args:
            project_results: List of per-project audit results
        
        Returns:
            Aggregated report dict
        """
        total_projects = len(project_results)
        passing_projects = sum(1 for r in project_results if r.get('production_ready', False))
        
        # Calculate aggregate score
        scores = [r.get('average_score', 0) for r in project_results]
        global_score = sum(scores) / len(scores) if scores else 0
        
        # Aggregate issues
        total_critical = sum(r.get('critical_count', 0) for r in project_results)
        total_cves = sum(r.get('cve_count', 0) for r in project_results)
        
        # Determine global gate
        global_production_ready = all(r.get('production_ready', False) for r in project_results)
        
        rollup = {
            'summary': {
                'total_projects': total_projects,
                'passing_projects': passing_projects,
                'global_score': round(global_score, 1),
                'global_production_ready': global_production_ready,
                'total_critical_issues': total_critical,
                'total_cves': total_cves
            },
            'projects': project_results
        }
        
        return rollup
    
    def format_rollup_summary(self, rollup: Dict) -> str:
        """Format roll-up summary for console output."""
        summary = rollup['summary']
        projects = rollup['projects']
        
        status = "✅ PASS" if summary['global_production_ready'] else "❌ FAIL"
        
        lines = [
            "\n" + "=" * 60,
            "MULTI-REPO ROLL-UP REPORT",
            "=" * 60,
            f"Status: {status}",
            f"Global Score: {summary['global_score']}/100",
            f"Projects: {summary['passing_projects']}/{summary['total_projects']} passing",
            ""
        ]
        
        # Per-project summary table
        lines.append("Per-Project Results:")
        lines.append("-" * 60)
        
        for project in projects:
            name = project.get('project_name', 'unknown')
            score = project.get('average_score', 0)
            ready = project.get('production_ready', False)
            status_emoji = "✅" if ready else "❌"
            
            lines.append(f"{status_emoji} {name:30} {score:5.1f}/100")
        
        lines.append("=" * 60)
        
        return '\n'.join(lines)


# Example manifest structure
EXAMPLE_MANIFEST = """
# audit_manifest.yaml
# Multi-repository audit configuration

projects:
  - name: aios_core
    path: ./main_core
    policy_override: null  # Use default policy
    
  - name: analytics_core
    path: ../aios_analytics
    policy_override: strict  # Stricter policy for analytics
    
  - name: integrations
    path: ../aios_integrations
    policy_override: null

# Global settings
parallel: true
fail_fast: false  # Continue even if one project fails
"""

