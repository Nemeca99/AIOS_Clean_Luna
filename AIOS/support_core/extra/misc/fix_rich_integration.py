#!/usr/bin/env python3
"""
Fix Rich shell integration issue
This script disables Rich integration and tests input()
"""

import os
import sys

# Disable Rich shell integration completely
os.environ["RICH_SHELL_INTEGRATION"] = "false"
os.environ["RICH_FORCE_TERMINAL"] = "false"
os.environ["RICH_DISABLE_CONSOLE"] = "true"
os.environ["RICH_DISABLE_SHELL_INTEGRATION"] = "true"

print("Rich shell integration disabled")
print(f"stdin.isatty(): {sys.stdin.isatty()}")
print(f"stdout.isatty(): {sys.stdout.isatty()}")
print(f"stderr.isatty(): {sys.stderr.isatty()}")

print("\nTesting input()...")
try:
    user_input = input("Enter something: ")
    print(f"SUCCESS! You entered: {user_input}")
except EOFError as e:
    print(f"EOF Error: {e}")
    print("Rich integration still active - need to disable at shell level")
except Exception as e:
    print(f"Other error: {e}")

print("\nTo permanently fix this:")
print("1. Uninstall Rich: pip uninstall rich")
print("2. Or set environment variable: RICH_SHELL_INTEGRATION=false")
print("3. Or run: python -c \"import os; os.environ['RICH_SHELL_INTEGRATION']='false'\"")
