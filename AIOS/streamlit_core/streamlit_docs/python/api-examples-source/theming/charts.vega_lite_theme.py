#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
from vega_datasets import data


@st.cache_data
def get_chart(use_container_width: bool):
    source = data.cars()

    chart = {
        "mark": "point",
        "encoding": {
            "x": {
                "field": "Horsepower",
                "type": "quantitative",
            },
            "y": {
                "field": "Miles_per_Gallon",
                "type": "quantitative",
            },
            "color": {"field": "Origin", "type": "nominal"},
            "shape": {"field": "Origin", "type": "nominal"},
        },
    }

    tab1, tab2 = st.tabs(["Streamlit theme (default)", "Vega-Lite native theme"])

    with tab1:
        st.vega_lite_chart(
            source, chart, use_container_width=use_container_width, theme="streamlit"
        )
    with tab2:
        st.vega_lite_chart(
            source, chart, use_container_width=use_container_width, theme=None
        )


try:
    get_chart(use_container_width=True)
except Exception as e:
    st.exception(e)
