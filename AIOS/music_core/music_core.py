#!/usr/bin/env python3
"""
Music Core - Give AI Music Capabilities

This core gives ANY LLM the ability to play and manage music.
It learns YOUR music preferences over time.
"""

import sys
import json
import random
# TODO: For deterministic behavior, add random.seed(CONSTANT) for testing
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class MusicCore:
    """Music playback and library management with AI learning."""
    
    def __init__(self):
        self.name = "music_core"
        self.version = "1.0.0"
        self.music_dir = Path(__file__).parent / "music_library"
        self.config_dir = Path(__file__).parent / "config"
        self.config = self._load_config()
        self.play_history = self._load_history()
        
        # Create directories if needed
        self.music_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load music configuration."""
        config_file = Path(__file__).parent / "config" / "music_config.json"
        
        default_config = {
            "library_path": str(Path(__file__).parent / "music_library"),
            "current_volume": 70,
            "shuffle": False,
            "repeat": False,
            "mood_mappings": {
                "sad": ["blues", "jazz", "acoustic"],
                "happy": ["pop", "dance", "upbeat"],
                "stressed": ["ambient", "classical", "nature"],
                "focused": ["instrumental", "lo-fi", "classical"],
                "energized": ["rock", "metal", "electronic"]
            }
        }
        
        if not config_file.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return default_config
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load play history for learning."""
        history_file = self.config_dir / "play_history.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_history(self):
        """Save play history."""
        history_file = self.config_dir / "play_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.play_history, f, indent=2)
    
    def scan_library(self) -> List[Dict[str, str]]:
        """Scan music library (simulated for now)."""
        # In real implementation, would scan actual music files
        # For demo, return simulated library
        return [
            {"artist": "Miles Davis", "album": "Kind of Blue", "genre": "jazz", "mood": "calm"},
            {"artist": "Metallica", "album": "Master of Puppets", "genre": "metal", "mood": "energized"},
            {"artist": "Beethoven", "album": "Symphony No. 9", "genre": "classical", "mood": "focused"},
            {"artist": "Coltrane", "album": "A Love Supreme", "genre": "jazz", "mood": "calm"},
            {"artist": "Tool", "album": "Lateralus", "genre": "rock", "mood": "energized"}
        ]
    
    def play_music(self, genre: Optional[str] = None, mood: Optional[str] = None, 
                   artist: Optional[str] = None) -> Dict[str, Any]:
        """
        Play music based on criteria.
        AI calls this function to play music!
        """
        library = self.scan_library()
        
        # Filter by criteria
        matches = library
        
        if genre:
            matches = [s for s in matches if genre.lower() in s['genre'].lower()]
        if mood:
            matches = [s for s in matches if mood.lower() in s['mood'].lower()]
        if artist:
            matches = [s for s in matches if artist.lower() in s['artist'].lower()]
        
        if not matches:
            return {"success": False, "message": "No matching music found"}
        
        # Pick one (in real implementation, would actually play)
        song = random.choice(matches)
        
        # Log to history for learning
        play_record = {
            "song": song,
            "timestamp": datetime.now().isoformat(),
            "genre": genre,
            "mood": mood,
            "artist": artist
        }
        self.play_history.append(play_record)
        self._save_history()
        
        return {
            "success": True,
            "playing": f"{song['artist']} - {song['album']}",
            "genre": song['genre'],
            "mood": song['mood']
        }
    
    def get_mood_suggestion(self, mood: str) -> Optional[str]:
        """Get genre suggestion for mood based on YOUR history."""
        # Check play history for this mood
        mood_plays = [p for p in self.play_history if p.get('mood') == mood]
        
        if mood_plays:
            # Use YOUR learned preference
            genres = [p['song']['genre'] for p in mood_plays]
            most_common = max(set(genres), key=genres.count)
            return most_common
        else:
            # Use default mood mapping
            return self.config['mood_mappings'].get(mood, ["random"])[0]
    
    def get_recommendations(self, context: str) -> List[str]:
        """Get music recommendations based on YOUR history."""
        if not self.play_history:
            return ["Play some music to help me learn your preferences!"]
        
        # Analyze YOUR play history
        recent = self.play_history[-10:]  # Last 10 plays
        genres = [p['song']['genre'] for p in recent]
        most_played = max(set(genres), key=genres.count)
        
        return [
            f"Based on YOUR recent listening, you seem to like {most_played}",
            f"Want me to play more {most_played}?"
        ]


# === PLUGIN INTERFACE ===

def get_commands():
    """Declare music core commands."""
    return {
        "commands": {
            "--music": {
                "help": "Music playback and library management",
                "usage": "python main.py --music [--play|--stop|--genre|--mood]",
                "examples": [
                    "python main.py --music --play --genre jazz",
                    "python main.py --music --play --mood calm",
                    "python main.py --music --suggest"
                ]
            },
            "--play": {
                "help": "Play music (use with --music)",
                "usage": "python main.py --music --play [--genre X] [--mood Y]"
            },
            "--suggest": {
                "help": "Get music suggestions (use with --music)",
                "usage": "python main.py --music --suggest"
            }
        },
        "description": "Music Core - AI-controlled music system with learning",
        "version": "1.0.0",
        "author": "AIOS Community",
        "capabilities": ["play_music", "mood_detection", "preference_learning"],
        "ai_integration": {
            "llm_callable": True,
            "learns_preferences": True,
            "mood_aware": True
        },
        "can_run_standalone": True
    }


def handle_command(args: List[str]) -> bool:
    """Handle music commands."""
    
    if '--music' not in args:
        return False
    
    try:
        music = MusicCore()
        
        if '--play' in args:
            # Extract parameters
            genre = None
            mood = None
            artist = None
            
            # Parse genre
            if '--genre' in args:
                idx = args.index('--genre')
                if idx + 1 < len(args):
                    genre = args[idx + 1]
            
            # Parse mood
            if '--mood' in args:
                idx = args.index('--mood')
                if idx + 1 < len(args):
                    mood = args[idx + 1]
            
            # Parse artist
            if '--artist' in args:
                idx = args.index('--artist')
                if idx + 1 < len(args):
                    artist = args[idx + 1]
            
            # Play music
            result = music.play_music(genre=genre, mood=mood, artist=artist)
            
            if result['success']:
                print(f"\n♪ Now playing: {result['playing']}")
                print(f"   Genre: {result['genre']}")
                print(f"   Mood: {result['mood']}")
                print(f"\n   (This is a simulation - real music_core would play actual audio)\n")
            else:
                print(f"\n⚠️  {result['message']}\n")
        
        elif '--suggest' in args:
            # Get recommendations
            suggestions = music.get_recommendations("general")
            print("\n🎵 Music Suggestions:\n")
            for suggestion in suggestions:
                print(f"   {suggestion}")
            print()
        
        elif '--library' in args:
            # Show library
            library = music.scan_library()
            print(f"\n🎵 Music Library ({len(library)} albums):\n")
            for item in library:
                print(f"   {item['artist']} - {item['album']} ({item['genre']})")
            print()
        
        else:
            # Show help
            print("\n🎵 Music Core")
            print("\nCommands:")
            print("  --music --play [options]    Play music")
            print("  --music --suggest           Get recommendations")
            print("  --music --library           Show your library")
            print("\nOptions for --play:")
            print("  --genre <genre>             Specific genre")
            print("  --mood <mood>               Match your mood")
            print("  --artist <artist>           Specific artist")
            print("\nExamples:")
            print("  python main.py --music --play --genre jazz")
            print("  python main.py --music --play --mood calm")
            print("  python main.py --music --play --artist 'Miles Davis'\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Music core error: {e}")
        if '--debug' in args:
            import traceback
            traceback.print_exc()
        return True


if __name__ == "__main__":
    """Allow standalone execution."""
    import sys
    result = handle_command(sys.argv)
    if not result:
        print("Usage: python -m music_core --music --play")


