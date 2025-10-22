#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

st.header("Full radius")
cols = st.columns(2)
with cols[0]:
    st.markdown("This is Markdown with `inline code`.")
    st.markdown("This is Markdown with a :primary-background[:primary[color badge]].")
    st.multiselect("Multiselect", ["A", "B", "C"], default=["A"], help="This is a tooltip.")
    st.button("Secondary button")
    st.segmented_control("Segmented control", ["Alpha", "Beta", "Gamma"])
with cols[1]:
    st.code("""import streamlit as st\n\nst.write("Hello World!")""")
    st.dataframe({"Column 1": [1, 2], "Column 2": [3, 4]})
    st.info("This is an info message.")

with st.sidebar:
    st.header("Zero radius")
    st.markdown("This is Markdown with `inline code`.")
    st.markdown("This is Markdown with a :primary-background[:primary[color badge]].")
    st.multiselect("Sidebar multiselect", ["A", "B", "C"], default=["A"], help="This is a tooltip.")
    st.button("Sidebar secondary button")
    st.segmented_control("Sidebar segmented control", ["One", "Two", "Three"])