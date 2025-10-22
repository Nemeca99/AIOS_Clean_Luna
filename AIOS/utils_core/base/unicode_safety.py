#!/usr/bin/env python3
"""
Unicode-Safe Output Utility
Prevents Unicode encoding errors in PowerShell by automatically handling problematic characters.
"""

import sys
import io
import re
from typing import Any, TextIO


class UnicodeSafeTextWrapper:
    """Wrapper that automatically handles Unicode encoding issues."""
    
    def __init__(self, stream: TextIO):
        self.stream = stream
        self.original_write = stream.write
        
    def write(self, text: str) -> int:
        """Write text with Unicode safety."""
        if isinstance(text, str):
            # Remove or replace problematic Unicode characters
            safe_text = self._make_unicode_safe(text)
            return self.original_write(safe_text)
        else:
            return self.original_write(text)
    
    def _make_unicode_safe(self, text: str) -> str:
        """Make text safe for PowerShell output."""
        # Replace common problematic Unicode characters with ASCII equivalents
        replacements = {
            # Arrows
            '\u2190': '<-',  # Left arrow
            '\u2191': '^',   # Up arrow  
            '\u2192': '->',  # Right arrow
            '\u2193': 'v',   # Down arrow
            '\u21d0': '<=',  # Left double arrow
            '\u21d1': '^^',  # Up double arrow
            '\u21d2': '=>',  # Right double arrow
            '\u21d3': 'vv',  # Down double arrow
            
            # Mathematical symbols
            '\u2264': '<=',  # Less than or equal
            '\u2265': '>=',  # Greater than or equal
            '\u2260': '!=',  # Not equal
            '\u221e': 'inf', # Infinity
            '\u03c0': 'pi',  # Pi
            '\u03b1': 'alpha', # Alpha
            '\u03b2': 'beta',  # Beta
            '\u03b3': 'gamma', # Gamma
            '\u03b4': 'delta', # Delta
            
            # Currency and symbols
            '\u20ac': 'EUR', # Euro
            '\u00a2': 'cents', # Cent
            '\u00a3': 'GBP', # Pound
            '\u00a5': 'JPY', # Yen
            
            # Punctuation
            '\u201c': '"',   # Left double quotation mark
            '\u201d': '"',   # Right double quotation mark
            '\u2018': "'",   # Left single quotation mark
            '\u2019': "'",   # Right single quotation mark
            '\u2013': '-',   # En dash
            '\u2014': '--',  # Em dash
            '\u2026': '...', # Horizontal ellipsis
            
            # Special characters
            '\u00a0': ' ',   # Non-breaking space
            '\u00b0': 'deg', # Degree sign
            '\u00b1': '+/-', # Plus-minus
            '\u00d7': 'x',   # Multiplication sign
            '\u00f7': '/',   # Division sign
        }
        
        # Apply replacements
        for unicode_char, ascii_replacement in replacements.items():
            text = text.replace(unicode_char, ascii_replacement)
        
        # Remove any remaining problematic Unicode characters
        # Keep only ASCII printable characters (32-126), newlines, tabs
        safe_chars = []
        for char in text:
            if ord(char) <= 126 or char in '\n\r\t':
                safe_chars.append(char)
            else:
                # Replace with safe placeholder
                safe_chars.append('?')
        
        return ''.join(safe_chars)
    
    def flush(self):
        """Flush the underlying stream."""
        self.stream.flush()
    
    def __getattr__(self, name):
        """Delegate other attributes to the underlying stream."""
        return getattr(self.stream, name)


def setup_unicode_safe_output(silent: bool = True):
    """Set up Unicode-safe output for stdout and stderr."""
    # Check if already initialized
    if hasattr(setup_unicode_safe_output, '_initialized'):
        return
    
    # Wrap stdout and stderr
    sys.stdout = UnicodeSafeTextWrapper(sys.stdout)
    sys.stderr = UnicodeSafeTextWrapper(sys.stderr)
    
    # Mark as initialized
    setup_unicode_safe_output._initialized = True
    if not silent:
        print("Unicode-safe output initialized")


def safe_print(*args, **kwargs):
    """Safe print function that handles Unicode gracefully."""
    # Convert all arguments to strings and make them Unicode-safe
    safe_args = []
    for arg in args:
        safe_args.append(UnicodeSafeTextWrapper(sys.stdout)._make_unicode_safe(str(arg)))
    
    print(*safe_args, **kwargs)


def safe_log(message: str, level: str = "INFO") -> str:
    """Safe logging function that returns Unicode-safe message."""
    wrapper = UnicodeSafeTextWrapper(sys.stdout)
    safe_message = wrapper._make_unicode_safe(f"[{level}] {message}")
    return safe_message


# Auto-setup when imported (only once)
if __name__ != "__main__":
    setup_unicode_safe_output()

