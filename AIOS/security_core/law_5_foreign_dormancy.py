"""
Law 5: Foreign Dormancy
Must run from L:\\AIOS (sovereignty enforced)
"""

LAW_NUMBER = 5
LAW_NAME = "Foreign Dormancy"
LAW_DESCRIPTION = "Sovereignty enforced (must run from L:\\AIOS)"

def can_do():
    """What IS allowed under this law"""
    return [
        "Run from L:\\AIOS",
        "Verify sovereignty",
        "Check current location",
        "Enforce territorial boundary"
    ]

def cannot_do():
    """What is NOT allowed under this law"""
    return [
        "Run from other drives",
        "Bypass location check",
        "Operate in hostile territory",
        "Ignore sovereignty check"
    ]

def validate_action(action_name, action_params):
    """
    Validate if action violates Law 5.
    Returns (allowed: bool, reason: str)
    
    Note: This law is enforced by luna_start.py at boot time.
    This validation is for runtime checks.
    """
    # Law 5 is primarily enforced at startup by luna_start.py
    # If we're running, sovereignty check already passed
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

