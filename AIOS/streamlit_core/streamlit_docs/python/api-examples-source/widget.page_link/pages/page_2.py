#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

st.page_link("your_app.py", label="Home", icon="🏠")
st.page_link("pages/page_1.py", label="Page 1", icon="1️⃣")
st.page_link("pages/page_2.py", label="Page 2", icon="2️⃣", disabled=True)
st.page_link("http://www.google.com", label="Google", icon="🌎")
