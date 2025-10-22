#!/usr/bin/env python3
"""
Game Core - Learn YOUR Gaming Patterns

This core tracks YOUR gameplay and helps YOU improve.
It compares YOU to YOUR past self, not to others!
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class GameCore:
    """Gaming analytics that learns YOUR patterns."""
    
    def __init__(self):
        self.name = "game_core"
        self.version = "1.0.0"
        self.config_dir = Path(__file__).parent / "config"
        self.sessions = self._load_sessions()
        
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_sessions(self) -> List[Dict[str, Any]]:
        """Load YOUR gameplay sessions."""
        sessions_file = Path(__file__).parent / "config" / "game_sessions.json"
        
        if not sessions_file.exists():
            return []
        
        try:
            with open(sessions_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_sessions(self):
        """Save YOUR gameplay sessions."""
        sessions_file = Path(__file__).parent / "config" / "game_sessions.json"
        with open(sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def start_session(self, game_name: str) -> str:
        """Start tracking a gameplay session."""
        session = {
            "session_id": f"session_{len(self.sessions) + 1}",
            "game": game_name,
            "start_time": datetime.now().isoformat(),
            "events": [],
            "stats": {}
        }
        
        self.sessions.append(session)
        self._save_sessions()
        
        return session['session_id']
    
    def log_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Log a gameplay event (deaths, wins, etc)."""
        for session in self.sessions:
            if session['session_id'] == session_id:
                event = {
                    "timestamp": datetime.now().isoformat(),
                    "type": event_type,
                    "data": data
                }
                session['events'].append(event)
                self._save_sessions()
                break
    
    def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """Analyze YOUR performance in a session."""
        session = next((s for s in self.sessions if s['session_id'] == session_id), None)
        
        if not session:
            return {"error": "Session not found"}
        
        # Count events
        deaths = [e for e in session['events'] if e['type'] == 'death']
        wins = [e for e in session['events'] if e['type'] == 'win']
        
        # Detect YOUR patterns
        patterns = {
            "total_deaths": len(deaths),
            "total_wins": len(wins),
            "death_locations": {},
            "common_mistakes": []
        }
        
        # Find where YOU die most
        for death in deaths:
            loc = death['data'].get('location', 'unknown')
            patterns['death_locations'][loc] = patterns['death_locations'].get(loc, 0) + 1
        
        return patterns
    
    def get_coaching(self, game_name: str) -> List[str]:
        """Get personalized coaching based on YOUR gameplay."""
        # Find YOUR sessions for this game
        game_sessions = [s for s in self.sessions if s['game'] == game_name]
        
        if not game_sessions:
            return ["Play some games so I can learn YOUR patterns and help YOU improve!"]
        
        coaching = []
        coaching.append(f"📊 I've tracked {len(game_sessions)} sessions of YOUR {game_name} gameplay:")
        
        # Analyze YOUR patterns
        total_deaths = sum(len([e for e in s['events'] if e['type'] == 'death']) for s in game_sessions)
        total_wins = sum(len([e for e in s['events'] if e['type'] == 'win']) for s in game_sessions)
        
        coaching.append(f"   YOUR stats: {total_wins} wins, {total_deaths} deaths")
        
        # Compare YOU to YOUR past
        if len(game_sessions) >= 2:
            first_session = game_sessions[0]
            recent_session = game_sessions[-1]
            
            first_deaths = len([e for e in first_session['events'] if e['type'] == 'death'])
            recent_deaths = len([e for e in recent_session['events'] if e['type'] == 'death'])
            
            if recent_deaths < first_deaths:
                improvement = ((first_deaths - recent_deaths) / first_deaths) * 100
                coaching.append(f"   ✅ YOU'VE improved {improvement:.0f}% since first session!")
            
            coaching.append(f"\n   Comparing YOU to YOUR past self:")
            coaching.append(f"   - YOUR first session: {first_deaths} deaths")
            coaching.append(f"   - YOUR recent session: {recent_deaths} deaths")
        
        return coaching


# === PLUGIN INTERFACE ===

def get_commands():
    """Declare game core commands."""
    return {
        "commands": {
            "--game": {
                "help": "Gaming analytics and coaching",
                "usage": "python main.py --game [--start|--analyze|--coach]",
                "examples": [
                    "python main.py --game --start 'Dark Souls'",
                    "python main.py --game --coach 'Dark Souls'"
                ]
            },
            "--start": {
                "help": "Start tracking gameplay session",
                "usage": "python main.py --game --start 'game name'",
                "requires_mode": "full-auto"
            },
            "--coach": {
                "help": "Get personalized coaching",
                "usage": "python main.py --game --coach 'game name'"
            }
        },
        "description": "Game Core - Learn YOUR gaming patterns & improve YOUR play",
        "version": "1.0.0",
        "author": "AIOS Community",
        "capabilities": ["gameplay_tracking", "performance_analysis", "personalized_coaching"],
        "ai_integration": {
            "llm_callable": True,
            "learns_patterns": True,
            "compares_to_self": True
        },
        "can_run_standalone": True
    }


def handle_command(args: List[str]) -> bool:
    """Handle game commands."""
    
    if '--game' not in args:
        return False
    
    try:
        game = GameCore()
        
        if '--start' in args:
            # Start session
            idx = args.index('--start')
            if idx + 1 < len(args):
                game_name = args[idx + 1]
                session_id = game.start_session(game_name)
                print(f"\n🎮 Started tracking: {game_name}")
                print(f"   Session ID: {session_id}")
                print(f"   (Game core will learn YOUR patterns as you play)\n")
            else:
                print("\n⚠️  Please provide game name\n")
        
        elif '--coach' in args:
            # Get coaching
            idx = args.index('--coach')
            if idx + 1 < len(args):
                game_name = args[idx + 1]
                coaching = game.get_coaching(game_name)
                print("\n🎮 Personalized Coaching:\n")
                for line in coaching:
                    print(f"   {line}")
                print()
            else:
                print("\n⚠️  Please provide game name\n")
        
        else:
            # Show help
            print("\n🎮 Game Core - YOUR Personal Gaming Coach")
            print("\nCommands:")
            print("  --game --start 'name'    Start tracking gameplay")
            print("  --game --coach 'name'    Get coaching for YOUR improvement")
            print("\nPrivacy:")
            print("  Tracking requires --privacy --full-auto mode")
            print("  Compares YOU to YOUR past self, not to others!")
            print("\nExamples:")
            print("  python main.py --game --start 'Dark Souls'")
            print("  python main.py --game --coach 'Dark Souls'\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Game core error: {e}")
        return True


if __name__ == "__main__":
    """Allow standalone execution."""
    import sys
    result = handle_command(sys.argv)
    if not result:
        print("Usage: python -m game_core --game --coach 'game name'")


