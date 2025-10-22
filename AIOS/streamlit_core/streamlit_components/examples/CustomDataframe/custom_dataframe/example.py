#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
import pandas as pd
from custom_dataframe import custom_dataframe

# Test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run custom_dataframe/example.py`
raw_data = {
    "First Name": ["Jason", "Molly", "Tina", "Jake", "Amy"],
    "Last Name": ["Miller", "Jacobson", "Ali", "Milner", "Smith"],
    "Age": [42, 52, 36, 24, 73],
}

df = pd.DataFrame(raw_data, columns=["First Name", "Last Name", "Age"])
returned_df = custom_dataframe(df)

if not returned_df.empty:
    st.table(returned_df)
