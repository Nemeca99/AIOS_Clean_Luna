#!/usr/bin/env python3
# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()


import streamlit as st
from streamlit import runtime

i1 = st.toggle("toggle 1 (True)", True)
st.write("toggle 1 - value:", i1)

i2 = st.toggle("toggle 2 (False)", False)
st.write("toggle 2 - value:", i2)

i3 = st.toggle(
    "toggle 3: This is a really really really really long label that should wrap "
    "eventually if we keep adding more text to it"
)
st.write("toggle 3 - value:", i3)

if runtime.exists():

    def on_change():
        st.session_state.toggle_clicked = True

    st.toggle("toggle 4 (with callback)", key="toggle4", on_change=on_change)
    st.write("toggle 4 - value:", st.session_state.toggle4)
    st.write("toggle 4 - clicked:", "toggle_clicked" in st.session_state)

i5 = st.toggle("toggle 5 (False, disabled)", disabled=True)
st.write("toggle 5 - value:", i5)

i6 = st.toggle("toggle 6 (True, disabled)", value=True, disabled=True)
st.write("toggle 6 - value:", i6)

i7 = st.toggle("toggle 7 (label hidden)", label_visibility="hidden", key="toggle_7")
st.write("toggle 7 - value:", i7)

i8 = st.toggle(
    "toggle 8 (label collapsed)", label_visibility="collapsed", key="toggle_8"
)
st.write("toggle 8 - value:", i8)

with st.expander("Grouped toggles", expanded=True):
    st.toggle("toggle group - 1")
    st.toggle("toggle group - 2")
    st.toggle("toggle group - 3")
    st.text("A non-toggle element")

st.toggle(
    "toggle 9 -> :material/check: :rainbow[Fancy] _**markdown** `label` _support_",
    key="toggle_9",
)

st.toggle("toggle with content width", width="content")
st.toggle("toggle with stretch width", width="stretch")
st.toggle("toggle with 150px width", width=150)

st.markdown("Dynamic toggle props:")

if st.toggle("Update toggle props"):
    state = st.toggle(
        "Updated dynamic toggle",
        value=False,
        width="stretch",
        help="updated help",
        key="dynamic_toggle_with_key",
        on_change=lambda a, param: print(
            f"Updated toggle - callback triggered: {a} {param}"
        ),
        args=("Updated toggle arg",),
        kwargs={"param": "updated kwarg param"},
    )
    st.write("Updated toggle state:", state)
else:
    state = st.toggle(
        "Initial dynamic toggle",
        value=True,
        width="content",
        help="initial help",
        key="dynamic_toggle_with_key",
        on_change=lambda a, param: print(
            f"Initial toggle - callback triggered: {a} {param}"
        ),
        args=("Initial toggle arg",),
        kwargs={"param": "initial kwarg param"},
    )
    st.write("Initial toggle state:", state)
