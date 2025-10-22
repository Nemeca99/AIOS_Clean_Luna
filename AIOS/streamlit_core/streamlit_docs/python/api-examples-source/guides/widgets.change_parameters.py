#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

cols = st.columns([2, 1, 2])
minimum = cols[0].number_input("Minimum", 1, 5)
maximum = cols[2].number_input("Maximum", 6, 10, 10)

st.slider("No default, no key", minimum, maximum)
st.slider("No default, with key", minimum, maximum, key="a")
st.slider("With default, no key", minimum, maximum, value=5)
st.slider("With default, with key", minimum, maximum, value=5, key="b")
