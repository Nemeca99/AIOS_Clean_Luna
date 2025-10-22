#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import pandas as pd
import streamlit as st
from numpy.random import default_rng as rng

df = pd.DataFrame(
    {
        "col1": list(range(20)) * 3,
        "col2": rng(0).standard_normal(60),
        "col3": ["a"] * 20 + ["b"] * 20 + ["c"] * 20,
    }
)

st.bar_chart(df, x="col1", y="col2", color="col3")
