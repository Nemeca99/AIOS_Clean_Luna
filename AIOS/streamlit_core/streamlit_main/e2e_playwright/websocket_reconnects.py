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


import time

import streamlit as st

# st.session_state can only be accessed while running with streamlit
if "counter" not in st.session_state:
    st.session_state.counter = 0
    st.session_state.slow_operations_attempted = 0

if st.button("click me!"):
    st.session_state.counter += 1

if st.checkbox("do something slow"):
    st.session_state.slow_operations_attempted += 1
    time.sleep(5)

st.write(f"count: {st.session_state.counter}")
st.write(f"slow operations attempted: {st.session_state.slow_operations_attempted}")

if f := st.file_uploader("Upload a file"):
    st.text(f.read())

if img := st.camera_input("Take a picture"):
    st.image(img)
