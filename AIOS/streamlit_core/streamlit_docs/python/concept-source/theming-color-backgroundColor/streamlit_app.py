#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

st.markdown("This is `inline code` in Markdown.")
st.multiselect("Multiselect", ["A", "B", "C"])
st.dataframe({"Dataframe column 1": [1, 2], "Dataframe column 2": [3, 4]})
st.code("""import streamlit as st\n\nst.write("Hello World!")""")

with st.sidebar:
    st.markdown("This is `inline code` in Markdown.")
    st.text_input("Text input")
    st.number_input("Number input")
    st.divider()
    st.chat_input("Chat input", accept_file=True)
