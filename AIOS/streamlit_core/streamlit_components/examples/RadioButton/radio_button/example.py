#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
from radio_button import custom_radio_button

# Test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run radio_button/example.py`
result = custom_radio_button(
    "How many bats?",
    options=["one bat", "TWO bats", "THREE bats", "FOUR BATS! ah ah ah!"],
    default="one bat",
)
st.write("This many: %s" % result)
