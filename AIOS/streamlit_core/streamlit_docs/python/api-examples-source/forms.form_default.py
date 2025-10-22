#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

with st.form("my_form"):
    st.write("Inside the form")
    my_number = st.slider("Pick a number", 1, 10)
    my_color = st.selectbox(
        "Pick a color", ["red", "orange", "green", "blue", "violet"]
    )
    st.form_submit_button("Submit my picks")

# This is outside the form
st.write(my_number)
st.write(my_color)
