#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

st.header("Chart elements")
chart_data = st.session_state.chart_data
map_data = st.session_state.map_data

st.subheader("Area chart")
st.area_chart(chart_data)
st.subheader("Bar chart")
st.bar_chart(chart_data)
st.subheader("Line chart")
st.line_chart(chart_data)
st.subheader("Scatter chart")
st.scatter_chart(chart_data)
st.subheader("Map")
st.map(map_data, color=st.get_option("theme.chartCategoricalColors")[0])
