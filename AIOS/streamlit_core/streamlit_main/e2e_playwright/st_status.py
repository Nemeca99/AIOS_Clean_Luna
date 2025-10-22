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
from streamlit.runtime.scriptrunner import get_script_run_ctx

ctx = get_script_run_ctx()
if ctx is None:
    import sys

    # This script is not compatible with running it in "bare" mode (e.g. `python script.py`)
    # The reason is that the mutable container is not correctly returned if
    # the runtime doesn't exist.
    print("This test script does not support bare script execution.")
    sys.exit(0)


running_status = st.status("Running status", expanded=False)
running_status.write("Doing some work...")

with st.status("Completed status", expanded=False, state="complete"):
    st.write("Hello world")

with st.status("Error status", expanded=False, state="error"):
    st.error("Oh no, something went wrong!")

with st.status("Expanded", state="complete", expanded=True):
    st.write("Hello world")

with st.status("About to change label...", state="complete") as status:
    st.write("Hello world")
    status.update(label="Changed label")

status = st.status("Without context manager", state="complete")
status.write("Hello world")
status.update(state="error", expanded=True)

with st.status("Collapse via update...", state="complete", expanded=True) as status:
    st.write("Hello world")
    status.update(label="Collapsed", expanded=False)

st.status("Empty state...", state="complete")

try:
    with st.status("Uncaught exception"):
        st.write("Hello world")
        raise Exception("Error!")
except Exception:
    pass

with st.status("Fixed width status", state="complete", width=200):
    st.write("Hello World")

with st.status("Stretch width status", state="complete", width="stretch"):
    st.write("Hello World")
