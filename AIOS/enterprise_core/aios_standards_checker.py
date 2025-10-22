#!/usr/bin/env python3
"""
AIOS STANDARDS CHECKER
Automated file standards checking and enforcement system
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils_core.validation.file_standards import AIOSStandardsManager, AIOSFileValidator, FileValidationResult, SeverityLevel

class AIOSStandardsChecker:
    """AIOS Standards Checking and Enforcement System"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.manager = AIOSStandardsManager(self.project_root)
        self.validator = AIOSFileValidator(self.project_root)
        self.check_results = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Standards configuration
        self.config = {
            "auto_fix_enabled": True,
            "check_interval": 30,  # seconds
            "strict_mode": True,
            "exclude_patterns": [
                "__pycache__",
                ".git",
                "venv",
                "node_modules",
                ".pytest_cache",
                "build",
                "dist"
            ],
            "critical_actions": {
                "block_commit": True,
                "auto_fix": True,
                "notify": True
            }
        }
    
    def check_single_file(self, file_path: str) -> Dict[str, Any]:
        """Check a single file against standards"""
        try:
            result = self.validator.validate_file(file_path)
            
            check_result = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "is_valid": result.is_valid,
                "compliance_score": result.standards_compliance,
                "total_issues": len(result.issues),
                "critical_issues": len([i for i in result.issues if i.severity == SeverityLevel.CRITICAL]),
                "high_issues": len([i for i in result.issues if i.severity == SeverityLevel.HIGH]),
                "medium_issues": len([i for i in result.issues if i.severity == SeverityLevel.MEDIUM]),
                "low_issues": len([i for i in result.issues if i.severity == SeverityLevel.LOW]),
                "auto_fixable": result.auto_fixable_issues,
                "manual_fix": result.manual_fix_required,
                "issues": [
                    {
                        "line": issue.line_number,
                        "column": issue.column,
                        "type": issue.issue_type,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "suggested_fix": issue.suggested_fix,
                        "auto_fixable": issue.auto_fixable
                    }
                    for issue in result.issues
                ]
            }
            
            # Auto-fix if enabled and issues are auto-fixable
            if self.config["auto_fix_enabled"] and result.auto_fixable_issues > 0:
                fixes = self.validator.auto_fix_file(file_path)
                check_result["auto_fixes_applied"] = fixes
                
                # Re-check after fixes
                if fixes:
                    updated_result = self.validator.validate_file(file_path)
                    check_result["post_fix_compliance"] = updated_result.standards_compliance
                    check_result["post_fix_valid"] = updated_result.is_valid
            
            return check_result
            
        except Exception as e:
            return {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "is_valid": False,
                "compliance_score": 0
            }
    
    def check_project(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Check entire project against standards"""
        if file_patterns is None:
            file_patterns = ['**/*.py', '**/*.json', '**/*.ps1', '**/*.psm1', '**/*.md']
        
        print(f"🔍 Checking AIOS project standards...")
        print(f"📁 Project root: {self.project_root}")
        
        all_files = []
        for pattern in file_patterns:
            for file_path in self.project_root.glob(pattern):
                # Skip excluded patterns
                if any(exclude in str(file_path) for exclude in self.config["exclude_patterns"]):
                    continue
                all_files.append(file_path)
        
        print(f"📋 Found {len(all_files)} files to check")
        
        results = {}
        total_issues = 0
        critical_issues = 0
        auto_fixes_applied = 0
        
        for file_path in all_files:
            print(f"  ✓ Checking {file_path.relative_to(self.project_root)}")
            result = self.check_single_file(str(file_path))
            results[str(file_path)] = result
            
            if "error" not in result:
                total_issues += result["total_issues"]
                critical_issues += result["critical_issues"]
                if "auto_fixes_applied" in result:
                    auto_fixes_applied += len(result["auto_fixes_applied"])
        
        # Generate summary
        valid_files = len([r for r in results.values() if r.get("is_valid", False)])
        total_files = len(results)
        avg_compliance = sum(r.get("compliance_score", 0) for r in results.values()) / total_files if total_files > 0 else 0
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": total_files - valid_files,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "auto_fixes_applied": auto_fixes_applied,
            "average_compliance": avg_compliance,
            "standards_met": critical_issues == 0 and avg_compliance >= 80,
            "results": results
        }
        
        # Save results
        results_file = self.project_root / "aios_standards_check.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📊 Standards Check Complete!")
        print(f"   Files checked: {total_files}")
        print(f"   Valid files: {valid_files}")
        print(f"   Average compliance: {avg_compliance:.1f}%")
        print(f"   Critical issues: {critical_issues}")
        print(f"   Auto-fixes applied: {auto_fixes_applied}")
        print(f"   Results saved to: {results_file}")
        
        if critical_issues > 0:
            print(f"\n🚨 CRITICAL ISSUES FOUND - Standards not met!")
            return summary
        
        if avg_compliance >= 80:
            print(f"\n✅ Standards compliance achieved!")
        else:
            print(f"\n⚠️ Standards compliance below threshold (80%)")
        
        return summary
    
    def check_file_on_change(self, file_path: str) -> Dict[str, Any]:
        """Check file when it changes (for real-time monitoring)"""
        print(f"🔄 Real-time check: {file_path}")
        result = self.check_single_file(file_path)
        
        # Log critical issues immediately
        if result.get("critical_issues", 0) > 0:
            print(f"🚨 CRITICAL ISSUES in {file_path}:")
            for issue in result.get("issues", []):
                if issue["severity"] == "critical":
                    print(f"   Line {issue['line']}: {issue['message']}")
        
        # Auto-fix if enabled
        if self.config["auto_fix_enabled"] and result.get("auto_fixable", 0) > 0:
            fixes = self.validator.auto_fix_file(file_path)
            if fixes:
                print(f"🔧 Auto-fixed {len(fixes)} issues in {file_path}")
        
        return result
    
    def start_monitoring(self, check_interval: int = None):
        """Start continuous monitoring of file changes"""
        if self.monitoring_active:
            print("⚠️ Monitoring already active")
            return
        
        self.monitoring_active = True
        check_interval = check_interval or self.config["check_interval"]
        
        print(f"👁️ Starting AIOS standards monitoring (interval: {check_interval}s)")
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    # Check for recently modified files
                    recent_files = []
                    for file_path in self.project_root.rglob("*"):
                        if file_path.is_file() and not any(exclude in str(file_path) for exclude in self.config["exclude_patterns"]):
                            if file_path.suffix in ['.py', '.json', '.ps1', '.psm1', '.md']:
                                # Check if modified in last interval
                                if time.time() - file_path.stat().st_mtime < check_interval:
                                    recent_files.append(str(file_path))
                    
                    # Check recent files
                    for file_path in recent_files:
                        self.check_file_on_change(file_path)
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"❌ Monitoring error: {e}")
                    time.sleep(5)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring_active:
            print("⚠️ Monitoring not active")
            return
        
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("⏹️ Standards monitoring stopped")
    
    def generate_compliance_report(self) -> str:
        """Generate human-readable compliance report"""
        results = self.check_project()
        
        report = f"""
# AIOS Standards Compliance Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Project:** {self.project_root.name}
**Total Files:** {results['total_files']}
**Valid Files:** {results['valid_files']}
**Average Compliance:** {results['average_compliance']:.1f}%

## Summary

- ✅ **Standards Met:** {'Yes' if results['standards_met'] else 'No'}
- 🚨 **Critical Issues:** {results['critical_issues']}
- 🔧 **Auto-fixes Applied:** {results['auto_fixes_applied']}
- 📊 **Overall Score:** {results['average_compliance']:.1f}/100

## File Details

"""
        
        # Group files by compliance level
        excellent = []
        good = []
        needs_work = []
        critical = []
        
        for file_path, result in results['results'].items():
            if 'error' in result:
                critical.append((file_path, result))
            elif result.get('critical_issues', 0) > 0:
                critical.append((file_path, result))
            elif result.get('compliance_score', 0) >= 90:
                excellent.append((file_path, result))
            elif result.get('compliance_score', 0) >= 70:
                good.append((file_path, result))
            else:
                needs_work.append((file_path, result))
        
        if excellent:
            report += "### ✅ Excellent Compliance (90%+)\n"
            for file_path, result in excellent:
                report += f"- `{Path(file_path).name}`: {result['compliance_score']:.1f}%\n"
        
        if good:
            report += "\n### ⚠️ Good Compliance (70-89%)\n"
            for file_path, result in good:
                report += f"- `{Path(file_path).name}`: {result['compliance_score']:.1f}%\n"
        
        if needs_work:
            report += "\n### 🔧 Needs Work (<70%)\n"
            for file_path, result in needs_work:
                report += f"- `{Path(file_path).name}`: {result['compliance_score']:.1f}%\n"
        
        if critical:
            report += "\n### 🚨 Critical Issues\n"
            for file_path, result in critical:
                if 'error' in result:
                    report += f"- `{Path(file_path).name}`: ERROR - {result['error']}\n"
                else:
                    report += f"- `{Path(file_path).name}`: {result['critical_issues']} critical issues\n"
        
        report += "\n## Recommendations\n\n"
        
        if results['critical_issues'] > 0:
            report += "- 🚨 **Fix critical issues immediately** - These prevent proper operation\n"
        
        if results['average_compliance'] < 80:
            report += "- 📈 **Improve overall compliance** - Target 80%+ for production\n"
        
        if results['auto_fixes_applied'] > 0:
            report += f"- 🔧 **Review auto-fixes** - {results['auto_fixes_applied']} fixes were applied automatically\n"
        
        report += "- 📚 **Review standards documentation** - See `AIOS_STANDARDS.md`\n"
        report += "- 🔄 **Run regular checks** - Use `aios_standards_checker.py check-project`\n"
        
        return report
    
    def save_compliance_report(self):
        """Save compliance report to file"""
        report = self.generate_compliance_report()
        report_file = self.project_root / "AIOS_COMPLIANCE_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Compliance report saved to: {report_file}")
    
    def get_project_health_score(self) -> Dict[str, Any]:
        """Get overall project health score"""
        results = self.check_project()
        
        # Calculate health score (0-100)
        base_score = results['average_compliance']
        
        # Penalties
        critical_penalty = results['critical_issues'] * 10
        invalid_files_penalty = (results['invalid_files'] / results['total_files']) * 20 if results['total_files'] > 0 else 0
        
        # Bonuses
        auto_fix_bonus = min(results['auto_fixes_applied'] * 2, 10)
        
        health_score = max(0, min(100, base_score - critical_penalty - invalid_files_penalty + auto_fix_bonus))
        
        # Determine health status
        if health_score >= 90:
            status = "excellent"
            emoji = "🟢"
        elif health_score >= 75:
            status = "good"
            emoji = "🟡"
        elif health_score >= 60:
            status = "fair"
            emoji = "🟠"
        else:
            status = "poor"
            emoji = "🔴"
        
        return {
            "health_score": health_score,
            "status": status,
            "emoji": emoji,
            "timestamp": datetime.now().isoformat(),
            "details": {
                "base_compliance": results['average_compliance'],
                "critical_penalty": critical_penalty,
                "invalid_files_penalty": invalid_files_penalty,
                "auto_fix_bonus": auto_fix_bonus
            }
        }

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIOS Standards Checker")
    parser.add_argument("command", choices=[
        "check-file", "check-project", "monitor", "report", "health", "generate-docs"
    ], help="Command to execute")
    parser.add_argument("file", nargs="?", help="File to check (for check-file command)")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    checker = AIOSStandardsChecker(args.project_root)
    
    if args.command == "check-file" and args.file:
        result = checker.check_single_file(args.file)
        print(f"File: {args.file}")
        print(f"Valid: {result.get('is_valid', False)}")
        print(f"Compliance: {result.get('compliance_score', 0):.1f}%")
        print(f"Issues: {result.get('total_issues', 0)}")
        
        if result.get('auto_fixes_applied'):
            print(f"Auto-fixes applied: {len(result['auto_fixes_applied'])}")
            for fix in result['auto_fixes_applied']:
                print(f"  - {fix}")
    
    elif args.command == "check-project":
        checker.check_project()
    
    elif args.command == "monitor":
        try:
            checker.start_monitoring(args.interval)
            print("Press Ctrl+C to stop monitoring...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            checker.stop_monitoring()
    
    elif args.command == "report":
        checker.save_compliance_report()
    
    elif args.command == "health":
        health = checker.get_project_health_score()
        print(f"{health['emoji']} Project Health: {health['health_score']:.1f}/100 ({health['status']})")
        print(f"Base compliance: {health['details']['base_compliance']:.1f}%")
        print(f"Critical penalty: -{health['details']['critical_penalty']:.1f}")
        print(f"Auto-fix bonus: +{health['details']['auto_fix_bonus']:.1f}")
    
    elif args.command == "generate-docs":
        checker.manager.save_standards_documentation()
        print("Standards documentation generated")

if __name__ == "__main__":
    main()
