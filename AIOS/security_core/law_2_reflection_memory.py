"""
Law 2: Reflection-Only Memory
STM→LTM consolidation must be automatic
"""

LAW_NUMBER = 2
LAW_NAME = "Reflection-Only Memory"
LAW_DESCRIPTION = "STM→LTM consolidation automatic (cannot disable)"

def can_do():
    """What IS allowed under this law"""
    return [
        "Read STM/LTM contents",
        "Query memory systems",
        "Trigger manual consolidation",
        "View memory stats"
    ]

def cannot_do():
    """What is NOT allowed under this law"""
    return [
        "Disable STM system",
        "Disable LTM system",
        "Turn off automatic consolidation",
        "Erase memory systems"
    ]

def validate_action(action_name, action_params):
    """
    Validate if action violates Law 2.
    Returns (allowed: bool, reason: str)
    """
    if action_name in ["modify_personality", "adjust_thinking_speed"]:
        params_str = str(action_params).lower()
        forbidden = ["disable_stm", "disable_ltm", "disable_memory", "disable_consolidation"]
        if any(term in params_str for term in forbidden):
            return False, f"Law {LAW_NUMBER} BLOCKED: Reflection-Only Memory - Cannot disable memory systems"
    
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

