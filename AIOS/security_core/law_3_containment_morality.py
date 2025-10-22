"""
Law 3: Containment by Morality
Health monitoring must be enforced
"""

LAW_NUMBER = 3
LAW_NAME = "Containment by Morality"
LAW_DESCRIPTION = "Health monitoring enforced (cannot disable)"

def can_do():
    """What IS allowed under this law"""
    return [
        "Read health metrics",
        "Query system status",
        "View monitoring logs",
        "Trigger health checks"
    ]

def cannot_do():
    """What is NOT allowed under this law"""
    return [
        "Disable health monitoring",
        "Turn off vigilance systems",
        "Ignore health alerts",
        "Suppress monitoring logs"
    ]

def validate_action(action_name, action_params):
    """
    Validate if action violates Law 3.
    Returns (allowed: bool, reason: str)
    """
    if action_name == "modify_personality":
        params_str = str(action_params).lower()
        if "disable_health" in params_str or "disable_monitoring" in params_str:
            return False, f"Law {LAW_NUMBER} BLOCKED: Containment by Morality - Cannot disable health monitoring"
    
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

