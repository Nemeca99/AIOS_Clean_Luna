#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

popover = st.popover("Filter items")
red = popover.checkbox("Show red items.", True)
blue = popover.checkbox("Show blue items.", True)

if red:
    st.write(":red[This is a red item.]")
if blue:
    st.write(":blue[This is a blue item.]")
