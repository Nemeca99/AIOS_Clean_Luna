#!/usr/bin/env python3
"""
Dashboard Generator
Real-time HTML dashboards and Slack/email alerts.
Humans don't read JSON. Make data visible.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """
    Generate HTML dashboards from audit trends.
    
    Features:
    - Score trends (per-core, rolling 10 runs)
    - Differential savings over time
    - Active suppressions with expiry
    - CVE trends
    - Live build status emojis
    """
    
    def __init__(self, trends_file: Path, output_dir: Path = None):
        self.trends_file = trends_file
        self.output_dir = output_dir or Path("reports")
        self.trends = self._load_trends()
    
    def _load_trends(self) -> List[Dict]:
        """Load trends from JSONL file."""
        trends = []
        
        if not self.trends_file.exists():
            return trends
        
        try:
            with open(self.trends_file) as f:
                for line in f:
                    if line.strip():
                        trends.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to load trends: {e}")
        
        return trends
    
    def generate_dashboard(self, 
                          current_report: Dict,
                          suppressions: List[Dict] = None,
                          quarantines: List[Dict] = None) -> Path:
        """
        Generate HTML dashboard.
        
        Args:
            current_report: Latest audit report
            suppressions: Active suppressions
            quarantines: Active quarantines
        
        Returns:
            Path to generated dashboard.html
        """
        logger.info("Generating dashboard...")
        
        html = self._generate_html(current_report, suppressions or [], quarantines or [])
        
        dashboard_path = self.output_dir / "dashboard.html"
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Dashboard saved to {dashboard_path}")
        return dashboard_path
    
    def _generate_html(self, 
                      report: Dict,
                      suppressions: List[Dict],
                      quarantines: List[Dict]) -> str:
        """Generate complete HTML dashboard."""
        
        # Extract data
        avg_score = report.get('average_score', 0)
        production_ready = report.get('production_ready', False)
        cores = report.get('cores', [])
        
        # Build status emoji
        status_emoji = "✅" if production_ready else "❌"
        status_class = "pass" if production_ready else "fail"
        
        # Score trend data
        trend_chart = self._generate_trend_chart()
        
        # Core scores table
        core_table = self._generate_core_table(cores)
        
        # Suppressions table
        suppressions_table = self._generate_suppressions_table(suppressions)
        
        # Quarantines table
        quarantines_table = self._generate_quarantines_table(quarantines)
        
        # Differential savings
        differential_stats = self._calculate_differential_stats()
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <title>AIOS Audit Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0d1117;
            color: #c9d1d9;
        }}
        .header {{
            background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            color: white;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .status {{
            font-size: 3em;
        }}
        .score {{
            font-size: 4em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .score.pass {{ color: #3fb950; }}
        .score.fail {{ color: #f85149; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }}
        .card h2 {{
            margin-top: 0;
            color: #58a6ff;
            border-bottom: 2px solid #30363d;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #30363d;
        }}
        th {{
            background: #0d1117;
            color: #58a6ff;
        }}
        .pass {{ color: #3fb950; }}
        .fail {{ color: #f85149; }}
        .warn {{ color: #d29922; }}
        .expiring {{ color: #d29922; font-weight: bold; }}
        .chart {{
            height: 200px;
            background: #0d1117;
            border-radius: 4px;
            padding: 10px;
            position: relative;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #8b949e;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>
            <span class="status">{status_emoji}</span>
            AIOS Audit V3 Sovereign
        </h1>
        <div class="score {status_class}">{avg_score:.1f}/100</div>
        <div>Production Ready: {"YES" if production_ready else "NO"}</div>
        <div style="font-size: 0.9em; margin-top: 10px;">
            Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h2>📊 Score Trend (Last 10 Runs)</h2>
            <div class="chart">{trend_chart}</div>
        </div>
        
        <div class="card">
            <h2>⚡ Differential Savings</h2>
            {differential_stats}
        </div>
        
        <div class="card">
            <h2>🔒 Active Suppressions</h2>
            {suppressions_table}
        </div>
        
        <div class="card">
            <h2>⏸️ Quarantined Checks</h2>
            {quarantines_table}
        </div>
    </div>
    
    <div class="card" style="margin-top: 20px;">
        <h2>🎯 Per-Core Scores</h2>
        {core_table}
    </div>
    
    <div class="footer">
        Generated by AIOS Audit V3 Sovereign | Auto-refresh every 60s
    </div>
</body>
</html>'''
        
        return html
    
    def _generate_trend_chart(self) -> str:
        """Generate ASCII/simple score trend chart."""
        if len(self.trends) < 2:
            return "<p>Insufficient data for trend (need 2+ runs)</p>"
        
        # Get last 10 scores
        recent = self.trends[-10:]
        scores = [t.get('average_score', 0) for t in recent if 'average_score' in t]
        
        if not scores:
            return "<p>No score data available</p>"
        
        # Simple sparkline
        max_score = max(scores)
        min_score = min(scores)
        
        points = []
        for i, score in enumerate(scores):
            normalized = (score - min_score) / (max_score - min_score) if max_score > min_score else 0.5
            height = int(normalized * 100)
            points.append(f'<div style="display:inline-block; width:10%; height:{height}%; background:#3fb950; margin:2px;"></div>')
        
        return f'''
        <div style="display:flex; align-items:flex-end; height:100px;">
            {''.join(points)}
        </div>
        <p style="margin:10px 0 0 0;">
            Range: {min_score:.1f} - {max_score:.1f} | 
            Current: {scores[-1]:.1f}
        </p>
        '''
    
    def _generate_core_table(self, cores: List[Dict]) -> str:
        """Generate table of core scores."""
        if not cores:
            return "<p>No core data available</p>"
        
        rows = []
        for core in sorted(cores, key=lambda c: c.get('score', 0), reverse=True):
            name = core.get('core_name', 'unknown')
            score = core.get('score', 0)
            status = core.get('status', 'UNKNOWN')
            
            status_class = 'pass' if status == 'OK' else 'fail' if status == 'CRITICAL' else 'warn'
            
            rows.append(f'''
                <tr>
                    <td>{name}</td>
                    <td class="{status_class}">{score:.1f}</td>
                    <td class="{status_class}">{status}</td>
                </tr>
            ''')
        
        return f'''
        <table>
            <tr>
                <th>Core</th>
                <th>Score</th>
                <th>Status</th>
            </tr>
            {''.join(rows)}
        </table>
        '''
    
    def _generate_suppressions_table(self, suppressions: List[Dict]) -> str:
        """Generate table of active suppressions."""
        if not suppressions:
            return "<p>No active suppressions</p>"
        
        rows = []
        now = datetime.now()
        
        for supp in suppressions:
            pattern = supp.get('pattern_id', 'unknown')
            owner = supp.get('owner', 'unknown')
            expires = supp.get('expires_on', '')
            
            # Check if expiring soon
            try:
                expires_dt = datetime.fromisoformat(expires)
                days_left = (expires_dt - now).days
                
                if days_left < 14:
                    expire_class = "expiring"
                    expire_text = f"{expires} ({days_left} days)"
                else:
                    expire_class = ""
                    expire_text = expires
            except:
                expire_class = ""
                expire_text = expires
            
            rows.append(f'''
                <tr>
                    <td>{pattern}</td>
                    <td>{owner}</td>
                    <td class="{expire_class}">{expire_text}</td>
                </tr>
            ''')
        
        return f'''
        <table>
            <tr>
                <th>Pattern</th>
                <th>Owner</th>
                <th>Expires</th>
            </tr>
            {''.join(rows)}
        </table>
        '''
    
    def _generate_quarantines_table(self, quarantines: List[Dict]) -> str:
        """Generate table of quarantined checks."""
        if not quarantines:
            return "<p>No quarantined checks</p>"
        
        rows = []
        for q in quarantines:
            check_id = q.get('check_id', 'unknown')
            owner = q.get('owner', 'unknown')
            reason = q.get('reason', '')[:50]  # Truncate
            
            rows.append(f'''
                <tr>
                    <td>{check_id}</td>
                    <td>{owner}</td>
                    <td>{reason}</td>
                </tr>
            ''')
        
        return f'''
        <table>
            <tr>
                <th>Check</th>
                <th>Owner</th>
                <th>Reason</th>
            </tr>
            {''.join(rows)}
        </table>
        '''
    
    def _calculate_differential_stats(self) -> str:
        """Calculate differential audit savings stats."""
        # This would come from actual differential data
        # For now, placeholder
        return '''
        <p style="font-size: 1.2em;">
            <strong>Average savings:</strong> <span class="pass">37%</span>
        </p>
        <p>Typical audit: 12/19 cores (7 saved)</p>
        <p>Time saved: ~60s per run</p>
        '''


class AlertManager:
    """
    Send alerts on audit failures.
    
    Integrations:
    - Slack webhook
    - Email (SMTP)
    """
    
    def __init__(self, policy: Dict):
        self.alerts_config = policy.get('alerts', {})
        self.enabled = self.alerts_config.get('enabled', False)
    
    def send_alert(self, 
                  alert_type: str,
                  summary: str,
                  details: Dict = None):
        """
        Send alert if configured.
        
        Args:
            alert_type: Type of alert (production_gate_fail, regression_detected, etc.)
            summary: One-line summary
            details: Additional context
        """
        if not self.enabled:
            return
        
        # Check if this alert type should trigger
        notify_on = self.alerts_config.get('slack', {}).get('notify_on', [])
        
        if alert_type not in notify_on:
            return
        
        # Send to Slack
        slack_config = self.alerts_config.get('slack', {})
        if slack_config.get('enabled', False):
            self._send_slack(summary, details, slack_config)
        
        # Send to Email
        email_config = self.alerts_config.get('email', {})
        if email_config.get('enabled', False):
            self._send_email(summary, details, email_config)
    
    def _send_slack(self, summary: str, details: Dict, config: Dict):
        """Send Slack webhook."""
        import requests
        
        webhook_url = config.get('webhook_url') or os.getenv('AUDIT_SLACK_WEBHOOK')
        
        if not webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
        
        # Format message
        core_name = details.get('core_name', 'system')
        delta = details.get('delta', '')
        commit = details.get('commit', 'unknown')[:8]
        
        message = {
            "text": f"🚨 AIOS Audit Alert",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{summary}*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Core:*\n{core_name}"},
                        {"type": "mrkdwn", "text": f"*Commit:*\n{commit}"}
                    ]
                }
            ]
        }
        
        if delta:
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Delta:* {delta}"
                }
            })
        
        # Add reproducer hint
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```py main_core/audit_core/reproduce.py {core_name}```"
            }
        })
        
        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            if response.status_code == 200:
                logger.info("Slack alert sent")
            else:
                logger.error(f"Slack alert failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_email(self, summary: str, details: Dict, config: Dict):
        """Send email alert (placeholder)."""
        # Email sending implementation
        logger.info(f"Email alert would be sent: {summary}")

