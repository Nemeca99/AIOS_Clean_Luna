#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

st.metric(label="Gas price", value=4, delta=-0.5, delta_color="inverse")
st.metric(label="Active developers", value=123, delta=123, delta_color="off")
