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
        "category": [
            ["exploration", "visualization"],
            ["llm", "visualization"],
            ["exploration"],
        ],
    }
)

st.data_editor(
    data_df,
    column_config={
        "category": st.column_config.MultiselectColumn(
            "App Categories",
            help="The categories of the app",
            options=[
                "exploration",
                "visualization",
                "llm",
            ],
            color=["#ffa421", "#803df5", "#00c0f2"],
            format_func=lambda x: x.capitalize(),
        ),
    },
)
