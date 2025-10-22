#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
import time


@st.fragment
def release_the_balloons():
    st.button("Release the balloons", help="Fragment rerun")
    st.balloons()


with st.spinner("Inflating balloons..."):
    time.sleep(5)
release_the_balloons()
st.button("Inflate more balloons", help="Full rerun")
