#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

col1, col2 = st.columns([1, 2])
col1.title("Sum:")

with st.form("addition"):
    a = st.number_input("a")
    b = st.number_input("b")
    submit = st.form_submit_button("add")

if submit:
    col2.title(f"{a+b:.2f}")
