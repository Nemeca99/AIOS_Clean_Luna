#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

option = st.selectbox(
    "Default email",
    ["foo@example.com", "bar@example.com", "baz@example.com"],
    index=None,
    placeholder="Select a saved email or enter a new one",
    accept_new_options=True,
)

st.write("You selected:", option)
