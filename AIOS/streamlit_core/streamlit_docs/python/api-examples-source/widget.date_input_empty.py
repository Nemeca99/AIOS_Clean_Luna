#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import datetime
import streamlit as st

d = st.date_input("When's your birthday", value=None)
st.write("Your birthday is:", d)
