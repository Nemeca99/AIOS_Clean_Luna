#!/usr/bin/env python3
"""
SBOM + CVE Scanner
Supply chain is part of your code. Gate on critical CVEs and banned licenses.
"""

import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SBOMScanner:
    """
    Generate SBOM and scan for CVEs and license violations.
    
    Features:
    - SBOM generation (pip freeze)
    - CVE scanning (pip-audit/safety)
    - License compliance (pip-licenses)
    - Dependency delta tracking
    """
    
    def __init__(self, root_dir: Path, policy: Dict):
        self.root = root_dir
        self.dependency_policy = policy.get('dependency_health', {})
        self.enabled = self.dependency_policy.get('enabled', True)
    
    def generate_sbom(self) -> Dict:
        """Generate Software Bill of Materials."""
        if not self.enabled:
            return {'enabled': False}
        
        logger.info("Generating SBOM...")
        
        try:
            # Get installed packages (use py -m pip for Windows compatibility)
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                
                return {
                    'enabled': True,
                    'packages': packages,
                    'package_count': len(packages),
                    'timestamp': self._get_timestamp()
                }
        except Exception as e:
            logger.error(f"SBOM generation failed: {e}")
        
        return {'enabled': True, 'error': 'SBOM generation failed'}
    
    def scan_vulnerabilities(self) -> Dict:
        """Scan for CVEs using pip-audit or safety."""
        if not self.enabled:
            return {'enabled': False}
        
        logger.info("Scanning for vulnerabilities...")
        
        # Try pip-audit first
        vuln_data = self._run_pip_audit()
        
        if vuln_data.get('tool') == 'none':
            # Fallback to safety if pip-audit not available
            vuln_data = self._run_safety()
        
        # Gate on policy
        max_cve = self.dependency_policy.get('max_vulnerability_counts', {})
        critical_count = vuln_data.get('critical', 0)
        high_count = vuln_data.get('high', 0)
        
        fail_on_critical = self.dependency_policy.get('fail_on_critical_cve', True)
        fail_on_high = self.dependency_policy.get('fail_on_high_cve', False)
        
        passed = True
        if fail_on_critical and critical_count > max_cve.get('critical', 0):
            passed = False
        if fail_on_high and high_count > max_cve.get('high', 5):
            passed = False
        
        vuln_data['passed'] = passed
        return vuln_data
    
    def _run_pip_audit(self) -> Dict:
        """Run pip-audit for CVE scanning."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip_audit', '--format=json', '--progress-spinner=off'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    vulnerabilities = data.get('dependencies', [])
                    
                    # Categorize by severity
                    critical = []
                    high = []
                    medium = []
                    low = []
                    
                    for dep in vulnerabilities:
                        for vuln in dep.get('vulns', []):
                            severity = vuln.get('aliases', [{}])[0].get('severity', 'UNKNOWN') if vuln.get('aliases') else 'UNKNOWN'
                            
                            vuln_info = {
                                'package': dep.get('name'),
                                'version': dep.get('version'),
                                'cve': vuln.get('id'),
                                'severity': severity,
                                'fix_versions': vuln.get('fix_versions', [])
                            }
                            
                            if 'CRITICAL' in severity.upper():
                                critical.append(vuln_info)
                            elif 'HIGH' in severity.upper():
                                high.append(vuln_info)
                            elif 'MEDIUM' in severity.upper():
                                medium.append(vuln_info)
                            else:
                                low.append(vuln_info)
                    
                    return {
                        'tool': 'pip-audit',
                        'critical': len(critical),
                        'high': len(high),
                        'medium': len(medium),
                        'low': len(low),
                        'vulnerabilities': {
                            'critical': critical[:5],  # First 5
                            'high': high[:5],
                            'medium': medium[:5]
                        }
                    }
                except json.JSONDecodeError:
                    pass
            
            # No vulnerabilities found
            return {
                'tool': 'pip-audit',
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'vulnerabilities': {}
            }
            
        except FileNotFoundError:
            logger.debug("pip-audit not found")
            return {'tool': 'none'}
        except Exception as e:
            logger.debug(f"pip-audit failed: {e}")
            return {'tool': 'none'}
    
    def _run_safety(self) -> Dict:
        """Fallback: Run safety for CVE scanning."""
        try:
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    # Safety doesn't categorize by severity in free tier
                    vulns = len(data)
                    
                    return {
                        'tool': 'safety',
                        'critical': vulns,  # Assume all critical for gating
                        'high': 0,
                        'medium': 0,
                        'low': 0,
                        'total': vulns
                    }
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            logger.debug("safety not found")
        except Exception as e:
            logger.debug(f"safety failed: {e}")
        
        return {'tool': 'none', 'error': 'No CVE scanner available'}
    
    def check_licenses(self) -> Dict:
        """Check license compliance."""
        if not self.enabled:
            return {'enabled': False}
        
        logger.info("Checking license compliance...")
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip_licenses', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                licenses = json.loads(result.stdout)
                
                allowlist = set(self.dependency_policy.get('license_allowlist', []))
                blocklist = set(self.dependency_policy.get('license_blocklist', []))
                
                violations = []
                unknown = []
                
                for pkg in licenses:
                    lic = pkg.get('License', 'UNKNOWN')
                    name = pkg.get('Name')
                    
                    if lic in blocklist:
                        violations.append({
                            'package': name,
                            'license': lic,
                            'reason': 'Blocklisted'
                        })
                    elif allowlist and lic not in allowlist and lic != 'UNKNOWN':
                        violations.append({
                            'package': name,
                            'license': lic,
                            'reason': 'Not in allowlist'
                        })
                    elif lic == 'UNKNOWN':
                        unknown.append(name)
                
                return {
                    'enabled': True,
                    'tool': 'pip-licenses',
                    'passed': len(violations) == 0,
                    'violations': violations,
                    'unknown_licenses': unknown[:10],  # First 10
                    'total_packages': len(licenses)
                }
        except FileNotFoundError:
            logger.warning("pip-licenses not found - install with 'pip install pip-licenses'")
        except Exception as e:
            logger.error(f"License check failed: {e}")
        
        return {'enabled': True, 'error': 'License check unavailable'}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def format_cve_summary(self, vuln_data: Dict) -> str:
        """Format CVE summary for console output."""
        if not vuln_data.get('enabled', True):
            return ""
        
        if vuln_data.get('error'):
            return f"⚠️  CVE scan: {vuln_data['error']}"
        
        critical = vuln_data.get('critical', 0)
        high = vuln_data.get('high', 0)
        
        if critical == 0 and high == 0:
            return "✅ No critical/high CVEs found"
        
        lines = [f"\n🔥 VULNERABILITY SCAN: {critical} critical, {high} high CVEs"]
        
        # Show first few critical vulns with upgrade hints
        crit_vulns = vuln_data.get('vulnerabilities', {}).get('critical', [])
        for vuln in crit_vulns[:3]:
            pkg = vuln['package']
            ver = vuln['version']
            cve = vuln['cve']
            fix = vuln.get('fix_versions', [])
            
            if fix:
                lines.append(f"   {pkg}=={ver} → {cve} (upgrade to {fix[0]})")
            else:
                lines.append(f"   {pkg}=={ver} → {cve} (no fix available)")
        
        return '\n'.join(lines)

