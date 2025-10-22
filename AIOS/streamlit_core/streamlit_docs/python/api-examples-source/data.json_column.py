#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import pandas as pd
import streamlit as st

data_df = pd.DataFrame(
    {
        "json": [
            {"foo": "bar", "bar": "baz"},
            {"foo": "baz", "bar": "qux"},
            {"foo": "qux", "bar": "foo"},
            None,
        ],
    }
)

st.dataframe(
    data_df,
    column_config={
        "json": st.column_config.JsonColumn(
            "JSON Data",
            help="JSON strings or objects",
            width="large",
        ),
    },
    hide_index=True,
)
