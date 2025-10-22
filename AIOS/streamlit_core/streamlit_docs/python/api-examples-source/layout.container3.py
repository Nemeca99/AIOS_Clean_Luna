#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

row1 = st.columns(3)
row2 = st.columns(3)

for col in row1 + row2:
    tile = col.container(border=True, height=120)
    tile.title(":balloon:")
