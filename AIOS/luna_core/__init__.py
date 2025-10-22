#!/usr/bin/env python3
"""
Luna Core Package
================

Complete Luna AI personality system with all functionality integrated.

This package contains:
- LunaSystem: Main Luna AI system
- All Luna subsystems and utilities
- Configuration files
- Learning and memory systems
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

# Import main system from core
from .core.luna_core import LunaSystem
from .core.personality import LunaPersonalitySystem
from .core.response_generator import LunaResponseGenerator
from .core.learning_system import LunaLearningSystem

# Import subsystems from systems/
from .systems.luna_arbiter_system import LunaArbiterSystem
from .systems.luna_cfia_system import LunaCFIASystem
from .systems.luna_custom_inference_controller import LunaCustomInferenceController
from .systems.luna_existential_budget_system import LunaExistentialBudgetSystem
from .systems.luna_ifs_personality_system import LunaIFSPersonalitySystem
from .systems.luna_response_value_classifier import LunaResponseValueClassifier
from .systems.luna_semantic_compression_filter import LunaSemanticCompressionFilter
from .systems.luna_soul_metric_system import LunaSoulMetricSystem
from .systems.luna_token_time_econometric_system import LunaTokenTimeEconometricSystem
# Soft-quarantined (unused - External Auditor sweep 2025-10-16):
# from .systems.llm_performance_evaluator import LLMPerformanceEvaluationSystem

__all__ = [
    'LunaSystem',
    'LunaPersonalitySystem', 
    'LunaResponseGenerator',
    'LunaLearningSystem',
    'LunaArbiterSystem',
    'LunaCFIASystem',
    'LunaCustomInferenceController',
    'LunaExistentialBudgetSystem',
    'LunaIFSPersonalitySystem',
    'LunaResponseValueClassifier',
    'LunaSemanticCompressionFilter',
    'LunaSoulMetricSystem',
    'LunaTokenTimeEconometricSystem',
    # 'LLMPerformanceEvaluationSystem',  # Soft-quarantined (unused)
    'get_commands',
    'handle_command'
]


# === PLUGIN INTERFACE ===

def get_commands():
    """
    Declare Luna Core commands for AIOS integration.
    This lets main.py know what Luna can do!
    """
    return {
        "commands": {
            "--luna": {
                "help": "Access Luna AI personality system",
                "usage": "python main.py --luna [--chat|--message|--learn] <text>",
                "examples": [
                    "python main.py --luna --chat 'hello'",
                    "python main.py --luna --message 'tell me about yourself'"
                ]
            },
            "--chat": {
                "help": "Chat with Luna (use with --luna)",
                "usage": "python main.py --luna --chat 'your message'",
                "examples": ["python main.py --luna --chat 'hello Luna'"]
            },
            "--message": {
                "help": "Send message to Luna (use with --luna)",
                "usage": "python main.py --luna --message 'your message'",
                "examples": ["python main.py --luna --message 'hi'"]
            }
        },
        "description": "Luna Core - AI Personality System with learning & memory",
        "version": "2.0.0",
        "author": "AIOS Team",
        "can_run_standalone": True
    }


def handle_command(args):
    """
    Handle Luna commands - works as AIOS plugin OR standalone.
    
    This is called by main.py when --luna is detected.
    Can also be run directly: python -m luna_core --chat "hello"
    """
    # Check if this is for Luna
    if '--luna' not in args:
        return False  # Not for us
    
    try:
        # Check if main.py provided a shared hybrid core
        luna = getattr(__import__('luna_core'), '_shared_hybrid', None)
        
        if luna is None:
            # Import the hybrid Luna system
            from .hybrid_luna_core import HybridLunaCore
            
            # Initialize Luna
            luna = HybridLunaCore()
        
        # Determine what action to take
        if '--chat' in args:
            # Get message (join all args after --chat)
            chat_idx = args.index('--chat')
            if chat_idx + 1 < len(args):
                # Join all remaining args as the message
                message = " ".join(args[chat_idx + 1:])
                
                # Generate response
                response = luna.generate_response(message)
                print(f"\n🌙 Luna: {response}\n")
            else:
                print("⚠️  Please provide a message after --chat")
                print("   Example: python main.py --luna --chat 'hello'")
        
        elif '--message' in args:
            # Similar to chat
            msg_idx = args.index('--message')
            if msg_idx + 1 < len(args):
                # Join all remaining args as the message
                message = " ".join(args[msg_idx + 1:])
                response = luna.generate_response(message)
                print(f"\n🌙 Luna: {response}\n")
            else:
                print("⚠️  Please provide a message")
        
        else:
            # Show Luna help
            print("\n🌙 Luna AI Personality System")
            print("\nCommands:")
            print("  --luna --chat 'message'      Chat with Luna")
            print("  --luna --message 'text'      Send a message")
            print("\nExamples:")
            print("  python main.py --luna --chat 'hello'")
            print("  python main.py --luna --message 'tell me about yourself'\n")
        
        return True  # We handled it
        
    except Exception as e:
        print(f"❌ Luna Core error: {e}")
        if '--debug' in args:
            import traceback
            traceback.print_exc()
        return True  # We tried to handle it


# === STANDALONE EXECUTION ===

if __name__ == "__main__":
    """
    Allow running luna_core standalone.
    Example: python -m luna_core --chat "hello"
    """
    import sys
    result = handle_command(sys.argv)
    if not result:
        print("Usage: python -m luna_core --luna --chat 'your message'")
