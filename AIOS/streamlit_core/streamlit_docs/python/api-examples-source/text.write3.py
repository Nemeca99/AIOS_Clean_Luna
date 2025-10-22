#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    data_frame = pd.DataFrame(
        {"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]}
    )
    return data_frame


data_frame = load_data()
st.write("1 + 1 = ", 2)
st.write("Below is a DataFrame:", data_frame, "Above is a dataframe.")
