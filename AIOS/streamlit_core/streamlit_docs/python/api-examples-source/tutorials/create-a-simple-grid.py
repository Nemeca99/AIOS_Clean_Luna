#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
from random import randint, choices


def create_grid(row_count, col_count, height):
    grid = []
    for row_num in range(row_count):
        row = st.columns(col_count)
        grid.append([col.container(border=True, height=height) for col in row])
    return grid


def pick_flowers(n):
    flowers = [
        ":tulip:",
        ":cherry_blossom:",
        ":rose:" ":hibiscus:",
        ":sunflower:",
        ":blossom:",
    ]
    return choices(flowers, k=n)


grid = create_grid(3, 5, 120)
for tile in [tile for row in grid for tile in row]:
    bouquet = "".join(pick_flowers(randint(2, 12)))
    tile.title(bouquet)
