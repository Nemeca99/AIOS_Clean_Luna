#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import pandas as pd
import streamlit as st

uploaded_files = st.file_uploader(
    "Upload data", accept_multiple_files=True, type="csv"
)

for uploaded_file in uploaded_files:
    df = pd.read_csv(uploaded_file)
    st.write(df)
