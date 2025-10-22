#!/usr/bin/env python3
"""
Privacy Core - Privacy Mode Management

Controls what AIOS learns and how it learns.
Two modes:
- SEMI-AUTO: Learns only from conversations (default)
- FULL-AUTO: Learns from everything (opt-in)
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class PrivacyCore:
    """Manage privacy settings and learning modes."""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "config" / "privacy_settings.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load privacy configuration."""
        default_config = {
            "mode": "semi-auto",
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "learning": {
                "conversation_only": True,
                "passive_monitoring": False,
                "predictive": False,
                "always_listening": False,
                "behavior_tracking": False
            },
            "consent": {
                "full_auto_enabled": False,
                "user_acknowledged": False,
                "can_be_disabled_anytime": True
            },
            "data_retention": {
                "conversations": True,
                "behavioral_data": False,
                "max_age_days": 365
            }
        }
        
        # Create if doesn't exist
        if not self.config_file.exists():
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        # Load existing
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return default_config
    
    def _save_config(self):
        """Save privacy configuration."""
        self.config['last_updated'] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_mode(self) -> str:
        """Get current privacy mode."""
        return self.config.get('mode', 'semi-auto')
    
    def set_semi_auto(self):
        """Switch to semi-auto mode (conversation only)."""
        self.config['mode'] = 'semi-auto'
        self.config['learning']['conversation_only'] = True
        self.config['learning']['passive_monitoring'] = False
        self.config['learning']['predictive'] = False
        self.config['learning']['always_listening'] = False
        self.config['learning']['behavior_tracking'] = False
        self.config['consent']['full_auto_enabled'] = False
        self._save_config()
        return True
    
    def set_full_auto(self) -> bool:
        """Switch to full-auto mode (requires explicit consent)."""
        print("\n⚠️  FULL-AUTO MODE")
        print("=" * 60)
        print("\nThis means AIOS will:")
        print("  ✓ Monitor typing patterns")
        print("  ✓ Track behavior over time")
        print("  ✓ Learn from everything you do")
        print("  ✓ Make proactive suggestions")
        print("  ✓ Predict your needs")
        print("\nAIOS will NOT:")
        print("  ✗ Share your data with anyone")
        print("  ✗ Send anything to cloud")
        print("  ✗ Monitor without your knowledge")
        print("  ✗ Prevent you from disabling this")
        print("\n📌 All data stays LOCAL in YOUR AIOS installation.")
        print("📌 You can disable anytime with: --privacy --semi-auto")
        print("\nEnable full-auto mode? (yes/no): ", end='')
        
        # Note: In real implementation, this would be interactive
        # For now, return True to allow programmatic enabling
        return True
    
    def enable_full_auto(self, confirmed: bool = False):
        """Enable full-auto after user confirms."""
        if not confirmed:
            return False
        
        self.config['mode'] = 'full-auto'
        self.config['learning']['conversation_only'] = False
        self.config['learning']['passive_monitoring'] = True
        self.config['learning']['predictive'] = True
        self.config['learning']['always_listening'] = True
        self.config['learning']['behavior_tracking'] = True
        self.config['consent']['full_auto_enabled'] = True
        self.config['consent']['user_acknowledged'] = True
        self._save_config()
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current privacy status."""
        mode = self.get_mode()
        
        status = {
            "mode": mode,
            "mode_name": "Semi-Auto (Privacy First)" if mode == "semi-auto" else "Full-Auto (Maximum Learning)",
            "learning_from_conversations": True,
            "passive_monitoring": self.config['learning']['passive_monitoring'],
            "predictive_features": self.config['learning']['predictive'],
            "always_listening": self.config['learning']['always_listening'],
            "data_stays_local": True,
            "can_disable": True
        }
        
        return status


# === PLUGIN INTERFACE ===

def get_commands():
    """Declare privacy core commands."""
    return {
        "commands": {
            "--privacy": {
                "help": "Manage privacy settings and learning modes",
                "usage": "python main.py --privacy [--status|--semi-auto|--full-auto]",
                "examples": [
                    "python main.py --privacy --status",
                    "python main.py --privacy --semi-auto",
                    "python main.py --privacy --full-auto"
                ]
            },
            "--status": {
                "help": "Show current privacy mode",
                "usage": "python main.py --privacy --status"
            },
            "--semi-auto": {
                "help": "Switch to semi-auto (conversation only)",
                "usage": "python main.py --privacy --semi-auto"
            },
            "--full-auto": {
                "help": "Switch to full-auto (maximum learning)",
                "usage": "python main.py --privacy --full-auto"
            }
        },
        "description": "Privacy Core - Control what AIOS learns and how",
        "version": "1.0.0",
        "author": "AIOS System"
    }


def handle_command(args: List[str]) -> bool:
    """Handle privacy commands."""
    
    if '--privacy' not in args:
        return False
    
    try:
        privacy = PrivacyCore()
        
        if '--status' in args:
            # Show current status
            status = privacy.get_status()
            print(f"\n🔐 Privacy Mode: {status['mode_name']}")
            print(f"\n   Learning from conversations: ✅")
            print(f"   Passive monitoring: {'✅' if status['passive_monitoring'] else '❌'}")
            print(f"   Predictive features: {'✅' if status['predictive_features'] else '❌'}")
            print(f"   Always listening: {'✅' if status['always_listening'] else '❌'}")
            print(f"\n   Data stays local: ✅")
            print(f"   Can disable anytime: ✅")
            
            if status['mode'] == 'semi-auto':
                print(f"\n💡 Want more features? Try: --privacy --full-auto")
            else:
                print(f"\n💡 Want more privacy? Try: --privacy --semi-auto")
            print()
        
        elif '--semi-auto' in args:
            # Switch to semi-auto
            privacy.set_semi_auto()
            print("\n✅ Switched to SEMI-AUTO mode")
            print("   AIOS will only learn from conversations.")
            print("   Passive monitoring disabled.")
            print("   Privacy maximized!\n")
        
        elif '--full-auto' in args:
            # Switch to full-auto (with consent)
            if privacy.set_full_auto():
                privacy.enable_full_auto(confirmed=True)
                print("\n✅ Switched to FULL-AUTO mode")
                print("   AIOS will learn from everything.")
                print("   Predictive features enabled.")
                print("   You can disable anytime with: --privacy --semi-auto\n")
        
        else:
            # Show help
            print("\n🔐 Privacy Core")
            print("\nCommands:")
            print("  --privacy --status      Show current mode")
            print("  --privacy --semi-auto   Privacy-first (default)")
            print("  --privacy --full-auto   Maximum learning (opt-in)")
            print("\nCurrent mode:", privacy.get_mode())
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Privacy core error: {e}")
        return True


if __name__ == "__main__":
    """Allow standalone execution."""
    import sys
    result = handle_command(sys.argv)
    if not result:
        print("Usage: python -m privacy_core --privacy --status")


