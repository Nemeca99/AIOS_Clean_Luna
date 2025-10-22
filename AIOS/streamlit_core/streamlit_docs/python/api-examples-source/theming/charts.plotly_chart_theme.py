#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import plotly.express as px
import streamlit as st


@st.cache_data
def get_chart(use_container_width: bool):
    df = px.data.gapminder()

    fig = px.scatter(
        df.query("year==2007"),
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=60,
    )

    tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
    with tab1:
        st.plotly_chart(fig, use_container_width=use_container_width, theme="streamlit")
    with tab2:
        st.plotly_chart(fig, use_container_width=use_container_width, theme=None)


try:
    get_chart(use_container_width=True)
except Exception as e:
    st.exception(e)
