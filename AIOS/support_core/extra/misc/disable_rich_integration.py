#!/usr/bin/env python3
"""
Disable Rich shell integration to fix input() issues
"""

import os
import sys

# Disable Rich shell integration
os.environ["RICH_SHELL_INTEGRATION"] = "false"
os.environ["RICH_FORCE_TERMINAL"] = "false"

# Disable Rich's automatic console detection
os.environ["RICH_DISABLE_CONSOLE"] = "true"

print("Rich shell integration disabled")
print("Terminal should now support input() properly")
