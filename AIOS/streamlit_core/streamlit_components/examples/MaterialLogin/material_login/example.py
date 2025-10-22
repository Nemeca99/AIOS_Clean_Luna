#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
from material_login import material_login

# Test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run material_login/example.py`

USERNAME = "a@a.com"
PASSWORD = "test"

logged_in_data = material_login("Insert your account")

st.write(logged_in_data)

if bool(logged_in_data) and logged_in_data['username'] == USERNAME and logged_in_data['password'] == PASSWORD:
    st.balloons()
