#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
from numpy.random import default_rng as rng

df = rng(0).standard_normal((10, 1))

tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])

tab1.subheader("A tab with a chart")
tab1.line_chart(df)

tab2.subheader("A tab with the data")
tab2.write(df)
