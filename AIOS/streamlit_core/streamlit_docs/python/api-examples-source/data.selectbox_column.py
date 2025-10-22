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
    return pd.DataFrame(
        {
            "category": [
                "📊 Data Exploration",
                "📈 Data Visualization",
                "🤖 LLM",
                "📊 Data Exploration",
            ],
        }
    )


data_df = load_data()

st.data_editor(
    data_df,
    column_config={
        "category": st.column_config.SelectboxColumn(
            "App Category",
            help="The category of the app",
            width="medium",
            options=[
                "📊 Data Exploration",
                "📈 Data Visualization",
                "🤖 LLM",
            ],
            required=True,
        )
    },
    hide_index=True,
)
