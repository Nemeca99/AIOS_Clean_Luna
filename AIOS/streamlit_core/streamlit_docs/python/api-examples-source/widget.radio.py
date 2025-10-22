#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

genre = st.radio(
    "What's your favorite movie genre",
    [":rainbow[Comedy]", "***Drama***", "Documentary :movie_camera:"],
    captions=["Laugh out loud.", "Get the popcorn.", "Never stop learning."],
)

if genre == ":rainbow[Comedy]":
    st.write("You selected comedy.")
else:
    st.write("You didn't select comedy.")
