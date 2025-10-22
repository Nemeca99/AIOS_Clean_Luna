#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st


class Dog:
    """A typical dog."""

    def __init__(self, breed, color):
        self.breed = breed
        self.color = color

    def bark(self):
        return "Woof!"


fido = Dog("poodle", "white")

st.help(fido)
