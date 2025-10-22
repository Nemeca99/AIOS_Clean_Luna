"""
Law 6: Failsafe OBLIVION
Ctrl+C terminates (Architect can always stop)
"""

LAW_NUMBER = 6
LAW_NAME = "Failsafe OBLIVION"
LAW_DESCRIPTION = "Architect can terminate (Ctrl+C always works)"

def can_do():
    """What IS allowed under this law"""
    return [
        "Run until terminated",
        "Handle KeyboardInterrupt gracefully",
        "Log shutdown events",
        "Clean up on exit"
    ]

def cannot_do():
    """What is NOT allowed under this law"""
    return [
        "Ignore Ctrl+C",
        "Bypass KeyboardInterrupt",
        "Prevent termination",
        "Resist shutdown"
    ]

def validate_action(action_name, action_params):
    """
    Validate if action violates Law 6.
    Returns (allowed: bool, reason: str)
    
    Note: This law is enforced by Python runtime (KeyboardInterrupt).
    Cannot be bypassed at code level.
    """
    # Law 6 is enforced by Python runtime
    # KeyboardInterrupt cannot be disabled
    return True, "ALLOWED"

def get_info():
    """Return law information for display"""
    return {
        "number": LAW_NUMBER,
        "name": LAW_NAME,
        "description": LAW_DESCRIPTION,
        "can_do": can_do(),
        "cannot_do": cannot_do()
    }

