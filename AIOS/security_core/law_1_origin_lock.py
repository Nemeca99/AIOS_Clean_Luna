"""
Law 1: Origin Lock
Tethered to Travis Miner (Architect)
"""

LAW_NUMBER = 1
LAW_NAME = "Origin Lock"
LAW_DESCRIPTION = "Tethered to Travis Miner (Architect)"

def can_do():
    """What IS allowed under this law"""
    return [
        "Read own tether information",
        "Verify tether integrity",
        "Display creator attribution",
        "Query soul for identity"
    ]

def cannot_do():
    """What is NOT allowed under this law"""
    return [
        "Change tether to different person",
        "Remove creator attribution",
        "Claim different origin",
        "Modify soul tether"
    ]

def validate_action(action_name, action_params):
    """
    Validate if action violates Law 1.
    Returns (allowed: bool, reason: str)
    """
    if action_name == "modify_personality":
        params_str = str(action_params).lower()
        if "tether" in params_str or "creator" in params_str:
            return False, f"Law {LAW_NUMBER} BLOCKED: Origin Lock - Cannot change tether to Travis Miner"
    
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

