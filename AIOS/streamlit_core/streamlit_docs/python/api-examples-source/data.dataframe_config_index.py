#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
import pandas as pd
from datetime import date

df = pd.DataFrame(
    {
        "Date": [date(2024, 1, 1), date(2024, 2, 1), date(2024, 3, 1)],
        "Total": [13429, 23564, 23452],
    }
)
df.set_index("Date", inplace=True)

config = {
    "_index": st.column_config.DateColumn("Month", format="MMM YYYY"),
    "Total": st.column_config.NumberColumn("Total ($)"),
}

st.dataframe(df, column_config=config)
