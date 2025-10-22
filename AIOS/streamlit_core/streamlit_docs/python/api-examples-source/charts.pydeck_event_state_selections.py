#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
import pydeck
import pandas as pd

capitals = pd.read_csv(
    "python/api-examples-source/data/capitals.csv",
    header=0,
    names=[
        "Capital",
        "State",
        "Abbreviation",
        "Latitude",
        "Longitude",
        "Population",
    ],
)
capitals["size"] = capitals.Population / 10

point_layer = pydeck.Layer(
    "ScatterplotLayer",
    data=capitals,
    id="capital-cities",
    get_position=["Longitude", "Latitude"],
    get_color="[255, 75, 75]",
    pickable=True,
    auto_highlight=True,
    get_radius="size",
)

view_state = pydeck.ViewState(
    latitude=40, longitude=-117, controller=True, zoom=2.4, pitch=30
)

chart = pydeck.Deck(
    point_layer,
    initial_view_state=view_state,
    tooltip={"text": "{Capital}, {Abbreviation}\nPopulation: {Population}"},
)

event = st.pydeck_chart(chart, on_select="rerun", selection_mode="multi-object")

event
