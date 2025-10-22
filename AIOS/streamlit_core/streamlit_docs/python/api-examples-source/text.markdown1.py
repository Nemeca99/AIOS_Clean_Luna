#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

md = st.text_area(
    "Type in your markdown string (without outer quotes)",
    "Happy Streamlit-ing! :balloon:",
)

st.code(
    f"""
import streamlit as st
        
st.markdown('''{md}''')
"""
)

st.markdown(md)
