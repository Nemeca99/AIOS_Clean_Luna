#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
from menu import menu_with_redirect

st.set_option("client.showSidebarNavigation", False)

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["super-admin"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

st.title("This page is available to super-admins")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
