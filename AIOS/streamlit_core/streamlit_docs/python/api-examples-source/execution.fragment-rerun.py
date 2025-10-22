#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

if "clicks" not in st.session_state:
    st.session_state.clicks = 0


@st.fragment
def count_to_five():
    if st.button("Plus one!"):
        st.session_state.clicks += 1
        if st.session_state.clicks % 5 == 0:
            st.rerun()
    return


count_to_five()
st.header(f"Multiples of five clicks: {st.session_state.clicks // 5}")

if st.button("Check click count"):
    st.toast(f"## Total clicks: {st.session_state.clicks}")
