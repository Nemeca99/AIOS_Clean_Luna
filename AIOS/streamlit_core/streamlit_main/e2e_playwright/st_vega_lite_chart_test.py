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


import pytest
from playwright.sync_api import Page, expect

from e2e_playwright.conftest import ImageCompareFunction, wait_for_app_run
from e2e_playwright.shared.app_utils import check_top_level_class, get_button

VEGA_LITE_CHART_COUNT = 12


def test_vega_lite_chart(app: Page):
    """Tests that it displays charts on the DOM."""
    vega_lite_charts = app.get_by_test_id("stVegaLiteChart")
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)

    for idx in range(VEGA_LITE_CHART_COUNT):
        chart = vega_lite_charts.nth(idx)
        vega_display = chart.locator("[role='graphics-document']").nth(0)
        expect(vega_display).to_be_visible()
        expect(vega_display.locator("svg")).to_have_class("marks")


@pytest.mark.skip_browser("firefox")
def test_vega_lite_chart_displays_interactive_charts(
    themed_app: Page, assert_snapshot: ImageCompareFunction
):
    """Tests that it displays interactive charts on the DOM."""
    vega_lite_charts = themed_app.get_by_test_id("stVegaLiteChart")
    # expect statement here so that snapshots are taken properly
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)
    expect(vega_lite_charts.nth(1)).to_be_visible()
    assert_snapshot(
        vega_lite_charts.nth(1),
        name="st_vega_lite_chart-interactive",
    )


@pytest.mark.skip_browser("firefox")
def test_vega_lite_chart_same_plot_different_ways(
    themed_app: Page, assert_snapshot: ImageCompareFunction
):
    """Tests that it displays the same plot in different ways."""
    vega_lite_charts = themed_app.get_by_test_id("stVegaLiteChart")
    # expect statement here so that snapshots are taken properly
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)

    for idx in range(2, 6):
        assert_snapshot(vega_lite_charts.nth(idx), name=f"st_vega_lite_chart-{idx}")


@pytest.mark.skip_browser("firefox")
def test_vega_lite_chart_streamlit_theme(
    themed_app: Page, assert_snapshot: ImageCompareFunction
):
    """Tests that st.vega_lite_chart supports the Streamlit theme."""
    vega_lite_charts = themed_app.get_by_test_id("stVegaLiteChart")
    # expect statement here so that snapshots are taken properly
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)

    for idx in range(6, 8):
        assert_snapshot(
            vega_lite_charts.nth(idx), name=f"st_vega_lite_chart-theming_{idx}"
        )


@pytest.mark.skip_browser("firefox")
def test_vega_lite_chart_default_theme(
    themed_app: Page, assert_snapshot: ImageCompareFunction
):
    """Tests that st.vega_lite_chart supports the default theme."""
    vega_lite_charts = themed_app.get_by_test_id("stVegaLiteChart")
    # expect statement here so that snapshots are taken properly
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)

    assert_snapshot(vega_lite_charts.nth(8), name="st_vega_lite_chart-default_theming")


@pytest.mark.skip_browser("firefox")
def test_vega_lite_chart_user_supplied_colors(
    themed_app: Page, assert_snapshot: ImageCompareFunction
):
    """Tests that st.vega_lite_chart respects user configuration."""
    vega_lite_charts = themed_app.get_by_test_id("stVegaLiteChart")
    # expect statement here so that snapshots are taken properly
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)

    assert_snapshot(
        vega_lite_charts.nth(9),
        name="st_vega_lite_chart-user_supplied_colors",
    )


@pytest.mark.skip_browser("firefox")
def test_empty_vega_lite_chart(app: Page, assert_snapshot: ImageCompareFunction):
    vega_lite_charts = app.get_by_test_id("stVegaLiteChart")
    # expect statement here so that snapshots are taken properly
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)

    assert_snapshot(
        vega_lite_charts.nth(10),
        name="st_vega_lite_chart-empty",
    )


def test_check_top_level_class(app: Page):
    """Check that the top level class is correctly set."""
    check_top_level_class(app, "stVegaLiteChart")


@pytest.mark.skip_browser("firefox")
def test_vega_lite_chart_updates_with_slightly_different_data(
    app: Page, assert_snapshot: ImageCompareFunction
):
    """Tests that it displays interactive charts on the DOM."""
    vega_lite_charts = app.get_by_test_id("stVegaLiteChart")
    # expect statement here so that snapshots are taken properly
    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)
    expect(vega_lite_charts.nth(11)).to_be_visible()
    assert_snapshot(
        vega_lite_charts.nth(11),
        name="st_vega_lite_chart-before_update",
    )

    get_button(app, "change").click()
    wait_for_app_run(app)

    expect(vega_lite_charts).to_have_count(VEGA_LITE_CHART_COUNT)
    expect(vega_lite_charts.nth(11)).to_be_visible()
    assert_snapshot(
        vega_lite_charts.nth(11),
        name="st_vega_lite_chart-after_update",
    )
