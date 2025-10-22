#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import graphviz as graphviz
import streamlit as st


@st.cache_data
def load_graph():
    # Create a graphlib graph object
    graph = graphviz.Digraph()
    graph.edge("run", "intr")
    graph.edge("intr", "runbl")
    graph.edge("runbl", "run")
    graph.edge("run", "kernel")
    graph.edge("kernel", "zombie")
    graph.edge("kernel", "sleep")
    graph.edge("kernel", "runmem")
    graph.edge("sleep", "swap")
    graph.edge("swap", "runswap")
    graph.edge("runswap", "new")
    graph.edge("runswap", "runmem")
    graph.edge("new", "runmem")
    graph.edge("sleep", "runmem")
    return graph


graph = load_graph()

st.graphviz_chart(graph)
