#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

if "attendance" not in st.session_state:
    st.session_state.attendance = set()


def take_attendance():
    if st.session_state.name in st.session_state.attendance:
        st.info(f"{st.session_state.name} has already been counted.")
    else:
        st.session_state.attendance.add(st.session_state.name)


with st.form(key="my_form"):
    st.text_input("Name", key="name")
    st.form_submit_button("I'm here!", on_click=take_attendance)
