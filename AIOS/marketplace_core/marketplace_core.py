#!/usr/bin/env python3
"""
Marketplace Core - Discover and Install Cores

The ecosystem distribution hub for AIOS.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class MarketplaceCore:
    """Marketplace for discovering and installing cores."""
    
    def __init__(self):
        self.name = "marketplace_core"
        self.version = "1.0.0"
        self.catalog_file = Path(__file__).parent / "config" / "catalog.json"
        self.installed_file = Path(__file__).parent / "config" / "installed.json"
        self.catalog = self._load_catalog()
        self.installed = self._load_installed()
        
        Path(__file__).parent.joinpath("config").mkdir(exist_ok=True)
    
    def _load_catalog(self) -> Dict[str, Any]:
        """Load marketplace catalog."""
        # In real implementation, this would fetch from online registry
        # For now, return demo catalog
        demo_catalog = {
            "cores": {
                "music_core": {
                    "name": "music_core",
                    "display_name": "Music Core",
                    "description": "AI-controlled music playback and library management",
                    "version": "1.0.0",
                    "author": "AIOS Community",
                    "rating": 4.8,
                    "downloads": 12000,
                    "price": "FREE",
                    "license": "MIT",
                    "repository": "https://github.com/aios-community/music_core",
                    "install_method": "git",
                    "capabilities": ["play_music", "mood_detection", "learning"],
                    "requires_privacy": "semi-auto"
                },
                "game_core": {
                    "name": "game_core",
                    "display_name": "Game Core",
                    "description": "Gaming analytics and personalized coaching",
                    "version": "1.0.0",
                    "author": "AIOS Community",
                    "rating": 4.9,
                    "downloads": 3000,
                    "price": "FREE",
                    "license": "MIT",
                    "repository": "https://github.com/aios-community/game_core",
                    "install_method": "git",
                    "capabilities": ["gameplay_tracking", "coaching"],
                    "requires_privacy": "full-auto"
                },
                "pro_automation_core": {
                    "name": "pro_automation_core",
                    "display_name": "Pro Automation Core",
                    "description": "Industrial automation with voice control and safety",
                    "version": "2.5.0",
                    "author": "IndustrialAI Corp",
                    "rating": 5.0,
                    "downloads": 500,
                    "price": "$499/year",
                    "license": "Commercial",
                    "repository": "https://marketplace.aios.ai/pro_automation_core",
                    "install_method": "marketplace",
                    "capabilities": ["robot_control", "safety_monitoring", "voice_commands"],
                    "requires_privacy": "full-auto"
                },
                "calendar_core": {
                    "name": "calendar_core",
                    "display_name": "Calendar Core",
                    "description": "Schedule management and smart reminders",
                    "version": "1.5.0",
                    "author": "ProductivityTeam",
                    "rating": 4.6,
                    "downloads": 8000,
                    "price": "FREE",
                    "license": "Apache 2.0",
                    "repository": "https://github.com/aios-community/calendar_core",
                    "install_method": "git",
                    "capabilities": ["scheduling", "reminders", "calendar_sync"]
                }
            }
        }
        
        return demo_catalog
    
    def _load_installed(self) -> List[str]:
        """Load list of installed cores."""
        if not self.installed_file.exists():
            return []
        
        try:
            with open(self.installed_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def list_available(self, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict]:
        """List available cores from marketplace."""
        cores = list(self.catalog['cores'].values())
        
        if search:
            search_lower = search.lower()
            cores = [c for c in cores if search_lower in c['name'].lower() or 
                    search_lower in c['description'].lower()]
        
        return cores
    
    def show_core_details(self, core_name: str):
        """Show detailed information about a core."""
        core = self.catalog['cores'].get(core_name)
        
        if not core:
            print(f"\n⚠️  Core '{core_name}' not found in marketplace\n")
            return
        
        print(f"\n📦 {core['display_name']} v{core['version']}")
        print("=" * 60)
        print(f"\n{core['description']}")
        print(f"\nAuthor: {core['author']}")
        print(f"Rating: {'⭐' * int(core['rating'])} {core['rating']}/5")
        print(f"Downloads: {core['downloads']:,}")
        print(f"Price: {core['price']}")
        print(f"License: {core['license']}")
        print(f"\nCapabilities:")
        for cap in core.get('capabilities', []):
            print(f"  ✓ {cap}")
        print(f"\nRepository: {core['repository']}")
        print()


# === PLUGIN INTERFACE ===

def get_commands():
    """Declare marketplace commands."""
    return {
        "commands": {
            "--marketplace": {
                "help": "Browse and install cores from ecosystem",
                "usage": "python main.py --marketplace [list|search|install|info]",
                "examples": [
                    "python main.py --marketplace list",
                    "python main.py --marketplace search music",
                    "python main.py --marketplace info music_core"
                ]
            },
            "--list": {
                "help": "List available cores",
                "usage": "python main.py --marketplace list"
            },
            "--search": {
                "help": "Search marketplace",
                "usage": "python main.py --marketplace search <term>"
            },
            "--info": {
                "help": "Show core details",
                "usage": "python main.py --marketplace info <core_name>"
            }
        },
        "description": "Marketplace Core - Discover & install cores from ecosystem",
        "version": "1.0.0",
        "author": "AIOS System"
    }


def handle_command(args: List[str]) -> bool:
    """Handle marketplace commands."""
    
    if '--marketplace' not in args:
        return False
    
    try:
        marketplace = MarketplaceCore()
        
        # Check what marketplace command
        has_subcommand = any(cmd in args for cmd in ['--list', '--search', '--info', '--install'])
        
        if not has_subcommand:
            # Show marketplace help
            print("\n🛒 AIOS Marketplace")
            print("\nCommands:")
            print("  --marketplace list              List all available cores")
            print("  --marketplace search <term>     Search for cores")
            print("  --marketplace info <core>       Show core details")
            print("\nExamples:")
            print("  python main.py --marketplace list")
            print("  python main.py --marketplace search automation")
            print("  python main.py --marketplace info music_core\n")
            return True
        
        if '--list' in args:
            # List all available cores
            cores = marketplace.list_available()
            print(f"\n🛒 AIOS Marketplace - {len(cores)} cores available\n")
            
            for core in cores:
                price_color = "FREE" if core['price'] == "FREE" else core['price']
                print(f"📦 {core['display_name']} v{core['version']}")
                print(f"   {core['description']}")
                print(f"   ⭐ {core['rating']}/5 | {core['downloads']:,} downloads | {price_color}")
                print()
        
        elif '--search' in args:
            # Search marketplace
            idx = args.index('--search')
            if idx + 1 < len(args):
                search_term = args[idx + 1]
                cores = marketplace.list_available(search=search_term)
                
                if cores:
                    print(f"\n🔍 Found {len(cores)} cores matching '{search_term}':\n")
                    for core in cores:
                        print(f"📦 {core['name']} - {core['description']}")
                        print(f"   {core['price']} | ⭐ {core['rating']}/5\n")
                else:
                    print(f"\n⚠️  No cores found matching '{search_term}'\n")
            else:
                print("\n⚠️  Please provide search term\n")
        
        elif '--info' in args:
            # Show core details
            idx = args.index('--info')
            if idx + 1 < len(args):
                core_name = args[idx + 1]
                marketplace.show_core_details(core_name)
            else:
                print("\n⚠️  Please provide core name\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Marketplace error: {e}")
        return True


if __name__ == "__main__":
    """Allow standalone execution."""
    import sys
    result = handle_command(sys.argv)
    if not result:
        print("Usage: python -m marketplace_core --marketplace list")

