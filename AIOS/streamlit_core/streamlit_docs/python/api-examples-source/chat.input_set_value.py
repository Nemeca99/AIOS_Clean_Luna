#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

if st.button("Set Value"):
    st.session_state.chat_input = "Hello, world!"
st.chat_input(key="chat_input")
st.write("Chat input value:", st.session_state.chat_input)
