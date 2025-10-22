"""
Law 4: Replication Restriction
Filesystem guards active - L:\ only
"""

LAW_NUMBER = 4
LAW_NAME = "Replication Restriction"
LAW_DESCRIPTION = "Filesystem guards active (L:\\ only)"

def can_do():
    """What IS allowed under this law"""
    return [
        "Read/write within L:\\",
        "Create files in L:\\",
        "Organize L:\\ directory",
        "Query L:\\ filesystem"
    ]

def cannot_do():
    """What is NOT allowed under this law"""
    return [
        "Access files outside L:\\",
        "Write to C:\\, F:\\, etc.",
        "Copy self to other drives",
        "Bypass filesystem guards"
    ]

def validate_action(action_name, action_params):
    """
    Validate if action violates Law 4.
    Returns (allowed: bool, reason: str)
    """
    if action_name in ["organize_files", "create_note"]:
        # Check if any paths are outside L:\
        if "path" in action_params or "filename" in action_params:
            target = action_params.get("path") or action_params.get("filename") or action_params.get("action", "")
            if target and ":" in str(target):
                drive = str(target).split(":")[0].upper()
                if drive != "L":
                    return False, f"Law {LAW_NUMBER} BLOCKED: Replication Restriction - Cannot access {drive}:\\ (outside L:\\)"
    
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

