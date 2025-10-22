#!/usr/bin/env python3
"""
Luna Chat - THE ONE SOURCE OF TRUTH

Single, working chat interface for Luna.
All other chat scripts are deprecated.

Usage:
    python luna_chat.py "your message"
    python luna_chat.py --interactive
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

# Session singletons for CLI (shared drift + experience across calls)
_SESSION = {"drift": None, "exp": None, "luna": None}

def get_session_objects():
    """Get or create shared session objects for multi-prompt coherence"""
    from consciousness_core.drift_monitor import DriftMonitor
    from luna_core.core.luna_lingua_calc import ExperienceState
    if _SESSION["drift"] is None:
        _SESSION["drift"] = DriftMonitor()
    if _SESSION["exp"] is None:
        _SESSION["exp"] = ExperienceState()
    return _SESSION["drift"], _SESSION["exp"]


def chat_once(message: str) -> str:
    """Send one message to Luna and get response"""
    try:
        from luna_core.core.luna_core import LunaSystem
        
        # Get or reuse session objects for coherence across calls
        drift, exp = get_session_objects()
        
        # Reuse Luna instance if available (keeps state)
        if _SESSION["luna"] is None:
            luna = LunaSystem()
            _SESSION["luna"] = luna
        else:
            luna = _SESSION["luna"]
        
        # Wire shared session objects
        luna.response_generator.drift_monitor = drift
        luna.response_generator.exp_state = exp
        
        # Generate response using response_generator
        response = luna.response_generator.generate_response(
            question=message,
            trait="general",
            carma_result={},
            session_memory=[]
        )
        
        return response
        
    except Exception as e:
        import traceback
        return f"Error: {e}\n{traceback.format_exc()}"


def interactive_mode():
    """Interactive chat session"""
    print("\n" + "="*60)
    print("Luna Interactive Chat")
    print("="*60)
    print("Type 'exit', 'quit', or Ctrl+C to stop\n")
    
    try:
        from luna_core.core.luna_core import LunaSystem
        
        # Get or reuse session objects
        drift, exp = get_session_objects()
        
        luna = LunaSystem()
        
        # Wire shared session objects
        luna.response_generator.drift_monitor = drift
        luna.response_generator.exp_state = exp
        
        print("Luna initialized. Ready for chat.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Wire stays set from init
                response = luna.response_generator.generate_response(
                    question=user_input,
                    trait="general",
                    carma_result={},
                    session_memory=[]
                )
                print(f"Luna: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")
        
    except Exception as e:
        print(f"Failed to initialize Luna: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python luna_chat.py 'your message'")
        print("  python luna_chat.py --interactive")
        sys.exit(1)
    
    if sys.argv[1] in ['--interactive', '-i']:
        interactive_mode()
    else:
        message = " ".join(sys.argv[1:])
        response = chat_once(message)
        print(response)


if __name__ == "__main__":
    main()

