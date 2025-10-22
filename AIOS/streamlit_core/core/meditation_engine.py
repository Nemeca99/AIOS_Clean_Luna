#!/usr/bin/env python3
"""
Meditation Engine for Streamlit Core
=====================================

Handles meditation mode, heartbeat tracking, and session management for Luna's
autonomous self-reflection system.

Key Features:
- Heartbeat tracking to monitor browser activity
- Meditation session management
- Session state persistence
- Karma and efficiency tracking

Author: AIOS Development Team
Version: 1.0.0
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class MeditationEngine:
    """
    Manages meditation mode and session tracking for Luna's autonomous reflection system.
    """
    
    def __init__(self, heartbeat_file: Path = None, session_file: Path = None):
        """
        Initialize the meditation engine.
        
        Args:
            heartbeat_file: Path to heartbeat tracking file
            session_file: Path to meditation session file
        """
        if heartbeat_file is None:
            heartbeat_file = Path("meditation_heartbeat.json")
        if session_file is None:
            session_file = Path("meditation_session.json")
        
        self.heartbeat_file = heartbeat_file
        self.session_file = session_file
        
        print("🧘 Meditation Engine Initialized")
        print(f"   Heartbeat File: {self.heartbeat_file}")
        print(f"   Session File: {self.session_file}")
    
    def update_heartbeat(self):
        """Update the heartbeat file to indicate browser is active."""
        try:
            heartbeat_data = {
                'last_heartbeat': datetime.now().timestamp(),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.heartbeat_file, 'w', encoding='utf-8') as f:
                json.dump(heartbeat_data, f)
                
        except Exception as e:
            print(f"⚠️ Error updating heartbeat: {e}")
    
    def check_browser_active(self, max_idle_seconds: int = 30) -> bool:
        """Check if browser is still active based on heartbeat."""
        if not self.heartbeat_file.exists():
            return True  # Allow if no heartbeat file exists yet

        try:
            with open(self.heartbeat_file, 'r', encoding='utf-8') as f:
                heartbeat_data = json.load(f)

            last_heartbeat = heartbeat_data.get('last_heartbeat', 0)
            time_since_heartbeat = datetime.now().timestamp() - last_heartbeat

            return time_since_heartbeat < max_idle_seconds

        except Exception as e:
            print(f"⚠️ Error checking heartbeat: {e}")
            return True  # Allow if we can't read the file
    
    def get_meditation_session_info(self) -> Dict[str, Any]:
        """Get current meditation session information."""
        if not self.session_file.exists():
            return {
                'active': False,
                'start_time': None,
                'total_meditations': 0,
                'current_state': 'idle',
                'karma_gained': 0.0,
                'efficiency_scores': []
            }
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            return {
                'active': session_data.get('active', False),
                'start_time': session_data.get('start_time'),
                'total_meditations': session_data.get('meditation_count', 0),
                'current_state': session_data.get('current_state', 'idle'),
                'karma_gained': session_data.get('karma_gained', 0.0),
                'efficiency_scores': session_data.get('efficiency_scores', [])
            }
            
        except Exception as e:
            print(f"⚠️ Error reading session file: {e}")
            return {
                'active': False,
                'start_time': None,
                'total_meditations': 0,
                'current_state': 'idle',
                'karma_gained': 0.0,
                'efficiency_scores': []
            }
    
    def start_meditation_session(self) -> bool:
        """Start a new meditation session."""
        try:
            session_data = {
                'active': True,
                'start_time': datetime.now().isoformat(),
                'meditation_count': 0,
                'current_state': 'initializing',
                'karma_gained': 0.0,
                'efficiency_scores': []
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f)
            
            print("🧘 Meditation session started")
            return True
            
        except Exception as e:
            print(f"❌ Error starting meditation session: {e}")
            return False
    
    def stop_meditation_session(self) -> bool:
        """Stop the current meditation session."""
        try:
            if not self.session_file.exists():
                return True
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            session_data['active'] = False
            session_data['current_state'] = 'stopped'
            session_data['end_time'] = datetime.now().isoformat()
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f)
            
            print("🛑 Meditation session stopped")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping meditation session: {e}")
            return False
    
    def update_meditation_progress(self, karma_delta: float = 0.0, 
                                   efficiency_score: float = None):
        """Update meditation session progress."""
        try:
            if not self.session_file.exists():
                return
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            session_data['meditation_count'] = session_data.get('meditation_count', 0) + 1
            session_data['karma_gained'] = session_data.get('karma_gained', 0.0) + karma_delta
            
            if efficiency_score is not None:
                scores = session_data.get('efficiency_scores', [])
                scores.append(efficiency_score)
                session_data['efficiency_scores'] = scores[-100:]  # Keep last 100 scores
            
            session_data['last_update'] = datetime.now().isoformat()
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f)
            
        except Exception as e:
            print(f"⚠️ Error updating meditation progress: {e}")

