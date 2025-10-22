#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

VIDEO_URL = "https://static.streamlit.io/examples/star.mp4"

st.video(VIDEO_URL)

st.write(
    """
    #### Video credit:

    Creator: User _fxxu_ from _Pixabay_.

    License: Free for commercial use. No attribution required.
    https://pixabay.com/en/service/license/

    URL:
    https://pixabay.com/en/videos/star-long-exposure-starry-sky-sky-6962/

"""
)
