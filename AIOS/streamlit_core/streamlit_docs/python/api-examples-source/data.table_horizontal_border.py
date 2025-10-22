#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st

product_data = {
    "Product": [
        ":material/devices: Widget Pro",
        ":material/smart_toy: Smart Device",
        ":material/inventory: Premium Kit",
    ],
    "Category": [":blue[Electronics]", ":green[IoT]", ":violet[Bundle]"],
    "Stock": ["🟢 Full", "🟡 Low", "🔴 Empty"],
    "Units sold": [1247, 892, 654],
    "Revenue": [125000, 89000, 98000],
}
st.table(product_data, border="horizontal")
