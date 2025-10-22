#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

uploaded_files = st.file_uploader(
    "Upload images", accept_multiple_files="directory", type=["jpg", "png"]
)
for uploaded_file in uploaded_files:
    st.image(uploaded_file)
