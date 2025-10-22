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


@st.fragment
def my_fragment1():
    st.button("rerun fragment 1")
    time.sleep(3)
    st.write("fragment 1 done!")


@st.fragment
def my_fragment2():
    if st.button("rerun fragment 2"):
        st.write("ran fragment 2")
    st.write("fragment 2 done!")


@st.fragment
def my_fragment3():
    st.button("rerun fragment 3")
    st.write("fragment 3 done!")


with st.container(border=True):
    my_fragment1()
with st.container(border=True):
    my_fragment2()
with st.container(border=True):
    my_fragment3()
