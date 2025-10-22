#!/usr/bin/env python3
"""
STREAMLIT CORE SYSTEM - Orchestrator
=====================================

Self-contained UI system for AIOS Clean.
This is the main orchestrator that coordinates all core modules and provides
the integration point to AIOS main.py

Architecture:
- Imports all core functionality modules
- Initializes StateManager, MeditationEngine, and UIRenderer
- Provides main() entry point for Streamlit
- Links to parent main.py for system integration

Author: AIOS Development Team
Version: 1.0.0
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
from utils_core.base.unicode_safety import setup_unicode_safe_output
setup_unicode_safe_output()

from pathlib import Path

# Import core modules
from .core import StateManager, MeditationEngine, UIRenderer


class StreamlitCore:
    """
    Orchestrator for the AIOS Streamlit UI system.
    Coordinates StateManager, MeditationEngine, and UIRenderer.
    Provides integration point to main.py
    """
    
    def __init__(self):
        """Initialize the Streamlit core system and all components."""
        print("🎨 Streamlit Core System Initializing...")
        
        # Initialize core components
        self.state_manager = StateManager(state_file=Path("streamlit_state.pkl"))
        self.meditation_engine = MeditationEngine(
            heartbeat_file=Path("meditation_heartbeat.json"),
            session_file=Path("meditation_session.json")
        )
        self.ui_renderer = UIRenderer(
            state_manager=self.state_manager,
            meditation_engine=self.meditation_engine
        )
        
        print("✅ Streamlit Core System Initialized")
    
    def run(self):
        """Run the main Streamlit application."""
        # Update heartbeat
        self.meditation_engine.update_heartbeat()
        
        # Render sidebar
        self.ui_renderer.render_sidebar()
        
        # Render main interface
        self.ui_renderer.render_main_interface()
    
    # Convenience methods for external integration (links to main.py)
    
    def get_state(self, key: str, default=None):
        """Get state value - convenience method for external access."""
        return self.state_manager.get_state(key, default)
    
    def set_state(self, key: str, value, persistent: bool = True):
        """Set state value - convenience method for external access."""
        self.state_manager.set_state(key, value, persistent)
    
    def start_meditation(self) -> bool:
        """Start meditation session - convenience method for external access."""
        return self.meditation_engine.start_meditation_session()
    
    def stop_meditation(self) -> bool:
        """Stop meditation session - convenience method for external access."""
        return self.meditation_engine.stop_meditation_session()
    
    def get_meditation_info(self):
        """Get meditation session info - convenience method for external access."""
        return self.meditation_engine.get_meditation_session_info()


# Main entry point for Streamlit app
def main():
    """Main Streamlit application entry point."""
    # Initialize Streamlit core
    streamlit_core = StreamlitCore()
    
    # Run the application
    streamlit_core.run()


def handle_command(args: list) -> bool:
    """
    Handle commands from main.py bootstrap.
    
    Args:
        args: Command line arguments
    
    Returns:
        True if command was handled, False otherwise
    """
    if '--streamlit' in args:
        import subprocess
        # Launch streamlit app
        subprocess.run(['streamlit', 'run', str(Path(__file__).parent / 'streamlit_app.py')])
        return True
    
    return False


def get_commands() -> dict:
    """
    Declare available commands for main.py discovery.
    
    Returns:
        Dictionary of commands and metadata
    """
    return {
        "commands": {
            "--streamlit": {
                "help": "Launch Streamlit dashboard",
                "usage": "python main.py --streamlit",
                "examples": ["python main.py --streamlit"]
            }
        },
        "description": "Streamlit UI Dashboard for AIOS",
        "version": "1.0.0",
        "author": "AIOS Development Team"
    }


if __name__ == "__main__":
    main()
