#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

AIOS PowerShell Bridge Module
Seamless integration between Python and PowerShell for advanced system monitoring
"""

import subprocess
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile
import threading
import time
from datetime import datetime

class PowerShellBridge:
    """Advanced PowerShell integration for AIOS system monitoring"""
    
    def __init__(self, aios_root: str = None, execution_policy: str = "Bypass"):
        self.aios_root = aios_root or os.getcwd()
        self.execution_policy = execution_policy
        self.powershell_wrapper = os.path.join(self.aios_root, "aios_powershell_wrapper.ps1")
        self.logger = self._setup_logger()
        
        # Ensure PowerShell wrapper exists
        if not os.path.exists(self.powershell_wrapper):
            raise FileNotFoundError(f"PowerShell wrapper not found: {self.powershell_wrapper}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for PowerShell bridge"""
        logger = logging.getLogger("PowerShellBridge")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def execute_powershell_command(self, command: str, capture_output: bool = True, 
                                 timeout: int = 30) -> Dict[str, Any]:
        """Execute a PowerShell command and return structured results"""
        try:
            self.logger.debug(f"Executing PowerShell command: {command}")
            
            result = subprocess.run(
                ['powershell', f'-ExecutionPolicy', self.execution_policy, '-Command', command],
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=self.aios_root
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_powershell_function(self, function_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific PowerShell function from the wrapper"""
        param_string = ""
        if parameters:
            param_parts = []
            for key, value in parameters.items():
                if isinstance(value, str):
                    param_parts.append(f'-{key} "{value}"')
                elif isinstance(value, bool) and value:
                    param_parts.append(f'-{key}')
                else:
                    param_parts.append(f'-{key} {value}')
            param_string = " " + " ".join(param_parts)
        
        command = f'& "{self.powershell_wrapper}"{param_string}; {function_name}'
        return self.execute_powershell_command(command)
    
    def start_monitoring(self, real_time: bool = True, admin_mode: bool = False) -> Dict[str, Any]:
        """Start the AIOS backend monitoring system"""
        params = {}
        if real_time:
            params['RealTimeMode'] = True
        if admin_mode:
            params['FullSystemAccess'] = True
        
        return self.execute_powershell_function('Start-AIOSBackendMonitor', params)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        result = self.execute_powershell_function('Get-AIOSStatus')
        
        if result['success']:
            # Parse the status output
            status_data = self._parse_status_output(result['stdout'])
            result['parsed_data'] = status_data
        
        return result
    
    def run_code_analysis(self, file_path: str = None, full_scan: bool = True) -> Dict[str, Any]:
        """Run comprehensive code analysis"""
        params = {}
        if file_path:
            params['FilePath'] = file_path
        if full_scan:
            params['FullScan'] = True
        
        result = self.execute_powershell_function('Invoke-AIOSCodeAnalysis', params)
        
        if result['success']:
            # Parse analysis results
            analysis_data = self._parse_analysis_output(result['stdout'])
            result['parsed_data'] = analysis_data
        
        return result
    
    def run_system_diagnostics(self, full_system_scan: bool = True, security_scan: bool = True) -> Dict[str, Any]:
        """Run comprehensive system diagnostics"""
        params = {}
        if full_system_scan:
            params['FullSystemScan'] = True
        if security_scan:
            params['SecurityScan'] = True
        
        result = self.execute_powershell_function('Invoke-AIOSSystemDiagnostics', params)
        
        if result['success']:
            # Parse diagnostics output
            diagnostics_data = self._parse_diagnostics_output(result['stdout'])
            result['parsed_data'] = diagnostics_data
        
        return result
    
    def get_logs(self, lines: int = 50, filter_type: str = "ALL", log_type: str = "monitor") -> Dict[str, Any]:
        """Retrieve AIOS logs"""
        params = {
            'Lines': lines,
            'Filter': filter_type,
            'LogType': log_type
        }
        
        result = self.execute_powershell_function('Get-AIOSLogs', params)
        
        if result['success']:
            logs_data = self._parse_logs_output(result['stdout'])
            result['parsed_data'] = logs_data
        
        return result
    
    def create_backup(self, backup_location: str = None) -> Dict[str, Any]:
        """Create system backup"""
        params = {}
        if backup_location:
            params['BackupLocation'] = backup_location
        
        result = self.execute_powershell_function('Backup-AIOSData', params)
        return result
    
    def restart_services(self) -> Dict[str, Any]:
        """Restart AIOS services"""
        return self.execute_powershell_function('Restart-AIOSService')
    
    def update_components(self) -> Dict[str, Any]:
        """Update AIOS components"""
        return self.execute_powershell_function('Update-AIOSComponents')
    
    def _parse_status_output(self, output: str) -> Dict[str, Any]:
        """Parse status command output"""
        status_data = {
            'components': {},
            'overall_status': 'unknown'
        }
        
        lines = output.split('\n')
        for line in lines:
            if ':' in line and ('Found' in line or 'Missing' in line):
                parts = line.split(':')
                if len(parts) == 2:
                    component = parts[0].strip()
                    status = parts[1].strip()
                    status_data['components'][component] = status
        
        return status_data
    
    def _parse_analysis_output(self, output: str) -> Dict[str, Any]:
        """Parse code analysis output"""
        analysis_data = {
            'files_analyzed': 0,
            'issues_found': 0,
            'severity_breakdown': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'issues': []
        }
        
        # Parse the analysis results (simplified)
        if 'files with issues' in output:
            try:
                issues_count = int(output.split('Found ')[1].split(' files')[0])
                analysis_data['issues_found'] = issues_count
            except (ValueError, IndexError) as e:
                # Output format not as expected - skip parsing
                print(f"Warning: Could not parse issues count: {e}")
        
        return analysis_data
    
    def _parse_diagnostics_output(self, output: str) -> Dict[str, Any]:
        """Parse diagnostics output"""
        diagnostics_data = {
            'system_info': {},
            'aios_health': {},
            'security_status': {},
            'performance_metrics': {}
        }
        
        # Parse diagnostics results (simplified)
        if 'System diagnostics complete' in output:
            diagnostics_data['status'] = 'completed'
        
        return diagnostics_data
    
    def _parse_logs_output(self, output: str) -> Dict[str, Any]:
        """Parse logs output"""
        logs_data = {
            'entries': [],
            'total_count': 0,
            'log_types': set()
        }
        
        lines = output.split('\n')
        for line in lines:
            if line.strip() and '[' in line and ']' in line:
                logs_data['entries'].append(line.strip())
                logs_data['total_count'] += 1
        
        return logs_data
    
    def start_continuous_monitoring(self, interval: int = 60, callback: callable = None) -> threading.Thread:
        """Start continuous monitoring in a separate thread"""
        def monitor_loop():
            while True:
                try:
                    # Get system status
                    status_result = self.get_system_status()
                    
                    # Get performance metrics
                    perf_result = self.execute_powershell_command(
                        "Get-Counter '\\Processor(_Total)\\% Processor Time', '\\Memory\\Available MBytes'"
                    )
                    
                    # Prepare monitoring data
                    monitoring_data = {
                        'timestamp': datetime.now().isoformat(),
                        'status': status_result,
                        'performance': perf_result
                    }
                    
                    # Call callback if provided
                    if callback:
                        callback(monitoring_data)
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in continuous monitoring: {e}")
                    time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def create_powershell_module(self, module_name: str = "AIOSTools") -> str:
        """Create a PowerShell module for advanced AIOS management"""
        module_content = f'''
# {module_name} PowerShell Module
# Advanced AIOS system management functions

function Test-AIOSProjectReadiness {{
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        
        [Parameter(Mandatory=$false)]
        [switch]$CheckDependencies,
        
        [Parameter(Mandatory=$false)]
        [switch]$CheckSecurity
    )
    
    Write-Verbose "Starting AIOS project readiness check..."
    
    $readiness = @{{
        ProjectPath = $ProjectPath
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        Checks = @{{}}
        OverallStatus = "Unknown"
    }}
    
    # Check core files
    $coreFiles = @("main.py", "requirements.txt", "aios_powershell_wrapper.ps1")
    foreach ($file in $coreFiles) {{
        $fullPath = Join-Path $ProjectPath $file
        $exists = Test-Path $fullPath
        $readiness.Checks["CoreFile_$file"] = @{{
            Path = $fullPath
            Exists = $exists
            Status = if ($exists) {{ "OK" }} else {{ "MISSING" }}
        }}
    }}
    
    # Check core directories
    $coreDirs = @("luna_core", "carma_core", "enterprise_core", "support_core", "config", "Data")
    foreach ($dir in $coreDirs) {{
        $fullPath = Join-Path $ProjectPath $dir
        $exists = Test-Path $fullPath
        $readiness.Checks["CoreDir_$dir"] = @{{
            Path = $fullPath
            Exists = $exists
            Status = if ($exists) {{ "OK" }} else {{ "MISSING" }}
        }}
    }}
    
    # Check Python environment
    $venvPath = Join-Path $ProjectPath "venv"
    $pythonExists = Test-Path (Join-Path $venvPath "Scripts\\python.exe")
    $readiness.Checks["PythonEnvironment"] = @{{
        Path = $venvPath
        Exists = $pythonExists
        Status = if ($pythonExists) {{ "OK" }} else {{ "MISSING" }}
    }}
    
    # Check dependencies if requested
    if ($CheckDependencies) {{
        $reqFile = Join-Path $ProjectPath "requirements.txt"
        if (Test-Path $reqFile) {{
            $readiness.Checks["Dependencies"] = @{{
                RequirementsFile = $reqFile
                Status = "FOUND"
            }}
        }} else {{
            $readiness.Checks["Dependencies"] = @{{
                RequirementsFile = $reqFile
                Status = "MISSING"
            }}
        }}
    }}
    
    # Security check if requested
    if ($CheckSecurity) {{
        $suspiciousPatterns = @("*.tmp", "*.temp", "*.exe.tmp")
        $suspiciousFiles = @()
        
        foreach ($pattern in $suspiciousPatterns) {{
            $files = Get-ChildItem -Path $ProjectPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
            if ($files) {{
                $suspiciousFiles += $files.FullName
            }}
        }}
        
        $readiness.Checks["Security"] = @{{
            SuspiciousFiles = $suspiciousFiles
            Status = if ($suspiciousFiles.Count -eq 0) {{ "CLEAN" }} else {{ "SUSPICIOUS" }}
        }}
    }}
    
    # Calculate overall status
    $failedChecks = ($readiness.Checks.Values | Where-Object {{ $_.Status -ne "OK" -and $_.Status -ne "FOUND" -and $_.Status -ne "CLEAN" }}).Count
    $totalChecks = $readiness.Checks.Count
    
    if ($failedChecks -eq 0) {{
        $readiness.OverallStatus = "READY"
    }} elseif ($failedChecks -le ($totalChecks * 0.3)) {{
        $readiness.OverallStatus = "WARNING"
    }} else {{
        $readiness.OverallStatus = "CRITICAL"
    }}
    
    return $readiness
}}

function Invoke-AIOSProjectCleanup {{
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath
    )
    
    if ($PSCmdlet.ShouldProcess("Clean up AIOS project at '$ProjectPath'")) {{
        Write-Verbose "Starting AIOS project cleanup..."
        
        $cleanupResults = @{{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            ProjectPath = $ProjectPath
            CleanedItems = @()
            Errors = @()
        }}
        
        # Clean temporary files
        $tempPatterns = @("*.pyc", "__pycache__", "*.tmp", "*.temp", ".pytest_cache")
        
        foreach ($pattern in $tempPatterns) {{
            try {{
                $items = Get-ChildItem -Path $ProjectPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
                foreach ($item in $items) {{
                    if ($item.PSIsContainer) {{
                        Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    }} else {{
                        Remove-Item -Path $item.FullName -Force -ErrorAction SilentlyContinue
                    }}
                    $cleanupResults.CleanedItems += $item.FullName
                }}
            }} catch {{
                $cleanupResults.Errors += "Failed to clean $pattern : $($_.Exception.Message)"
            }}
        }}
        
        # Clean old log files (older than 7 days)
        $logDir = Join-Path $ProjectPath "log"
        if (Test-Path $logDir) {{
            try {{
                $oldLogs = Get-ChildItem -Path $logDir -Recurse -File | Where-Object {{ $_.LastWriteTime -lt (Get-Date).AddDays(-7) }}
                foreach ($log in $oldLogs) {{
                    Remove-Item -Path $log.FullName -Force -ErrorAction SilentlyContinue
                    $cleanupResults.CleanedItems += $log.FullName
                }}
            }} catch {{
                $cleanupResults.Errors += "Failed to clean old logs: $($_.Exception.Message)"
            }}
        }}
        
        return $cleanupResults
    }}
}}

Export-ModuleMember -Function Test-AIOSProjectReadiness, Invoke-AIOSProjectCleanup
'''
        
        # Save module to AIOS root
        module_path = os.path.join(self.aios_root, f"{module_name}.psm1")
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(module_content)
        
        self.logger.info(f"Created PowerShell module: {module_path}")
        return module_path
    
    def get_project_readiness(self, check_dependencies: bool = True, check_security: bool = True) -> Dict[str, Any]:
        """Check AIOS project readiness using PowerShell module"""
        # First create the module if it doesn't exist
        module_path = os.path.join(self.aios_root, "AIOSTools.psm1")
        if not os.path.exists(module_path):
            self.create_powershell_module()
        
        # Execute the readiness check
        params = {
            'ProjectPath': self.aios_root
        }
        if check_dependencies:
            params['CheckDependencies'] = True
        if check_security:
            params['CheckSecurity'] = True
        
        command = f'Import-Module "{module_path}" ; Test-AIOSProjectReadiness -ProjectPath "{self.aios_root}" -CheckDependencies -CheckSecurity -Verbose'
        result = self.execute_powershell_command(command)
        
        if result['success']:
            # Parse the readiness output
            readiness_data = self._parse_readiness_output(result['stdout'])
            result['parsed_data'] = readiness_data
        
        return result
    
    def _parse_readiness_output(self, output: str) -> Dict[str, Any]:
        """Parse project readiness output"""
        readiness_data = {
            'timestamp': None,
            'project_path': None,
            'overall_status': 'unknown',
            'checks': {},
            'summary': {}
        }
        
        # Parse the output (simplified parsing)
        lines = output.split('\n')
        for line in lines:
            if 'OverallStatus' in line:
                try:
                    status = line.split(':')[1].strip()
                    readiness_data['overall_status'] = status
                except (ValueError, IndexError) as e:
                    # Line format not as expected - skip
                    print(f"Warning: Could not parse status line: {e}")
        
        return readiness_data


def create_powershell_integration_example():
    """Example of how to use the PowerShell bridge"""
    
    # Initialize the bridge
    bridge = PowerShellBridge()
    
    # Example 1: Get system status
    print("=== AIOS System Status ===")
    status_result = bridge.get_system_status()
    if status_result['success']:
        print("✅ System status retrieved successfully")
        if 'parsed_data' in status_result:
            print(f"Components checked: {len(status_result['parsed_data']['components'])}")
    else:
        print(f"❌ Failed to get system status: {status_result['stderr']}")
    
    # Example 2: Run code analysis
    print("\n=== Code Analysis ===")
    analysis_result = bridge.run_code_analysis()
    if analysis_result['success']:
        print("✅ Code analysis completed")
        if 'parsed_data' in analysis_result:
            print(f"Issues found: {analysis_result['parsed_data']['issues_found']}")
    else:
        print(f"❌ Code analysis failed: {analysis_result['stderr']}")
    
    # Example 3: Start monitoring
    print("\n=== Starting Monitoring ===")
    monitor_result = bridge.start_monitoring(real_time=True, admin_mode=True)
    if monitor_result['success']:
        print("✅ Monitoring started successfully")
    else:
        print(f"❌ Failed to start monitoring: {monitor_result['stderr']}")
    
    # Example 4: Continuous monitoring with callback
    def monitoring_callback(data):
        print(f"📊 Monitoring update: {data['timestamp']}")
        if data['status']['success']:
            print("  System status: OK")
        if data['performance']['success']:
            print("  Performance data: Available")
    
    print("\n=== Starting Continuous Monitoring ===")
    monitor_thread = bridge.start_continuous_monitoring(interval=30, callback=monitoring_callback)
    print("✅ Continuous monitoring started (30-second intervals)")
    
    return bridge


if __name__ == "__main__":
    # Run the integration example
    bridge = create_powershell_integration_example()
    
    # Keep the script running to see continuous monitoring
    try:
        print("\n🔄 Continuous monitoring active. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user.")
