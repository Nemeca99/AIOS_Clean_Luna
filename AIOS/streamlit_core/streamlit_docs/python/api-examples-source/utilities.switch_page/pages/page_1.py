#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

if st.button("Home"):
    st.switch_page("your_app.py")
if st.button("Page 1"):
    st.switch_page("pages/page_1.py")
if st.button("Page 2"):
    st.switch_page("pages/page_2.py")
