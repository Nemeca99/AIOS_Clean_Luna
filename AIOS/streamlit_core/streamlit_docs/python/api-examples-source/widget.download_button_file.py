#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

with open("python/api-examples-source/flower.png", "rb") as file:
    st.download_button(
        label="Download image",
        data=file,
        file_name="flower.png",
        mime="image/png",
    )
