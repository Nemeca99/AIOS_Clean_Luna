#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
import datetime

d = st.date_input("When's your birthday", datetime.date(2020, 8, 11))
st.write("Your birthday is:", d)
