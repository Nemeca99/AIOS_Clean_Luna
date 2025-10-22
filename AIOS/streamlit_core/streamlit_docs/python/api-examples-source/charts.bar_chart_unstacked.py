#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
from vega_datasets import data

source = data.barley()

st.bar_chart(source, x="year", y="yield", color="site", stack=False)
