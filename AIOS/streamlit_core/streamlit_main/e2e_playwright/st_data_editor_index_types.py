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


# ruff: noqa: ERA001
import random

import numpy as np

import streamlit as st
from shared.data_mocks import (
    BASE_TYPES_DF,
    DATETIME_TYPES_DF,
    NUMBER_TYPES_DF,
    SPECIAL_TYPES_DF,
)

np.random.seed(0)
random.seed(0)

st.set_page_config(layout="wide")

st.header("Index types")

st.subheader("String Index (pd.Index)")
st.data_editor(BASE_TYPES_DF.set_index("string"), width="stretch", num_rows="dynamic")

st.subheader("Float64 Index (pd.Float64Index)")
st.data_editor(
    NUMBER_TYPES_DF.set_index("float64"), width="stretch", num_rows="dynamic"
)

st.subheader("Int64 Index (pd.Int64Index)")
st.data_editor(NUMBER_TYPES_DF.set_index("int64"), width="stretch", num_rows="dynamic")

st.subheader("Uint64 Index (pd.UInt64Index)")
st.data_editor(NUMBER_TYPES_DF.set_index("uint64"), width="stretch", num_rows="dynamic")

st.subheader("Date Index (pd.Index)")
st.data_editor(DATETIME_TYPES_DF.set_index("date"), width="stretch", num_rows="dynamic")

st.subheader("Time Index (pd.Index)")
st.data_editor(DATETIME_TYPES_DF.set_index("time"), width="stretch", num_rows="dynamic")

st.subheader("Datetime Index (pd.DatetimeIndex)")
st.data_editor(
    DATETIME_TYPES_DF.set_index("datetime"),
    width="stretch",
    num_rows="dynamic",
)

st.subheader("Categorical Index (pd.CategoricalIndex)")
st.data_editor(
    SPECIAL_TYPES_DF.set_index("categorical"),
    width="stretch",
    num_rows="dynamic",
)

# List index isn't editable currently:
# st.subheader("List Index (pd.Index)")
# st.data_editor(
#     LIST_TYPES_DF.set_index("string_list"), width="stretch", num_rows="dynamic"
# )

# Interval type isn't editable currently:
# st.subheader("Interval Index (pd.IntervalIndex)")
# st.data_editor(INTERVAL_TYPES_DF.set_index("int64_both"), width="stretch")

# Multi index is not yet supported for editing:
# st.subheader("Multi Index (pd.MultiIndex)")
# st.data_editor(
#     BASE_TYPES_DF.set_index(["string", "int64"]),
#     width="stretch",
#     num_rows="dynamic",
# )

# Timedelta Index are currently not supported for editing:
# st.subheader("Timedelta Index (pd.TimedeltaIndex)")
# st.data_editor(
#     SPECIAL_TYPES_DF.set_index("timedelta"),
#     width="stretch",
#     num_rows="dynamic",
# )
