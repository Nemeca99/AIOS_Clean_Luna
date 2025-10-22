"""
AIOS Quality Dashboard
======================

Visualizes hypothesis pass rate, latency trends, routing boundary drift, 
A/B buckets, and per-message drilldowns.

This dashboard uses the core.dashboard_analytics module for all data processing
and focuses purely on UI presentation.

Author: AIOS Development Team
Version: 1.0.0
"""
from __future__ import annotations
import time
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Import analytics engine
from core.dashboard_analytics import DashboardAnalytics

# Initialize dashboard analytics
ROOT = Path(__file__).resolve().parents[1]
analytics = DashboardAnalytics(root_path=ROOT)

st.set_page_config(page_title="AIOS Quality Dashboard", layout="wide")
st.title("AIOS Quality Dashboard")


@st.cache_data(ttl=10)
def load_data():
    """Load all dashboard data (cached)."""
    rdf, hdf = analytics.load_frames()
    adaptive_state = analytics.load_adaptive_state()
    last_report, baseline = analytics.load_golden_reports()
    return rdf, hdf, adaptive_state, last_report, baseline


# Load data
rdf, hdf, adaptive_state, last_report, baseline = load_data()

# Sidebar filters
st.sidebar.header("Filters")
conv_ids = sorted([c for c in rdf.get("conv_id", pd.Series(dtype=str)).dropna().unique().tolist()]) if not rdf.empty else []
conv_sel = st.sidebar.multiselect("Conversation IDs", conv_ids, default=conv_ids[:5] if len(conv_ids) > 0 else [])
window = st.sidebar.selectbox("Aggregation window", ["None", "1m", "5m", "15m", "1h"], index=2)

# Auto-refresh
if st.sidebar.checkbox("Auto-refresh (10s)", value=False):
    time.sleep(10)
    st.rerun()

# Top summary metrics
col1, col2, col3, col4 = st.columns(4)

# Hypothesis pass rate
total_cases, total_pass, pass_rate = analytics.calculate_hypothesis_pass_rate(hdf)

# Routing metrics
routing_metrics = analytics.get_routing_metrics(adaptive_state)

col1.metric(
    "Hypothesis pass rate", 
    f"{pass_rate:.0%}" if pass_rate is not None else "n/a", 
    help="Percentage of hypothesis tests that passed"
)
col2.metric(
    "Control samples", 
    f"{routing_metrics['control_count']}", 
    help="Messages processed in control bucket"
)
col3.metric(
    "Treatment samples", 
    f"{routing_metrics['treatment_count']}", 
    help="Messages processed in treatment bucket"
)
col4.metric(
    "Treatment boundary", 
    f"{routing_metrics['treatment_boundary']:.3f}", 
    delta=f"{routing_metrics['treatment_boundary'] - 0.5:+.3f}" if routing_metrics['treatment_boundary'] != 0.5 else None,
    help="Current routing boundary for treatment bucket"
)

st.divider()

# Tabs
T1, T2, T3, T4, T5 = st.tabs([
    "Overview", "Hypotheses", "Routing", "Drill-down", "Settings"
])

with T1:
    st.subheader("Traffic split and sources")
    if rdf.empty:
        st.info("No response events yet. Run some questions through Luna to see data.")
    else:
        c1, c2 = st.columns(2)
        
        # Bucket distribution
        if routing_metrics['total_conversations'] > 0:
            bucket_data = analytics.prepare_bucket_distribution_data(routing_metrics)
            c1.plotly_chart(
                px.pie(bucket_data, names="bucket", values="count", title="A/B Bucket Distribution"), 
                use_container_width=True
            )
        else:
            c1.info("No A/B bucket data yet")
        
        # Source distribution
        source_data = analytics.prepare_source_distribution_data(rdf, conv_sel)
        if not source_data.empty:
            c2.plotly_chart(
                px.pie(source_data, names="source", values="count", 
                      title="Routing Source (main_model vs embedder)"), 
                use_container_width=True
            )
        else:
            c2.info("No routing source data in logs yet")

with T2:
    st.subheader("Hypothesis batches")
    if hdf.empty:
        st.info("No hypothesis batches logged yet. Hypothesis tests run periodically after messages accumulate.")
    else:
        # Basic table
        view_cols = analytics.get_hypothesis_view_columns()
        view = hdf[[c for c in view_cols if c in hdf.columns]].sort_values("ts", ascending=False)
        st.dataframe(view, use_container_width=True, height=300)
        
        # Trend: quality fail rate over time
        if "rates.quality" in hdf.columns:
            ht = hdf.dropna(subset=["rates.quality"]).copy()
            if not ht.empty:
                ht["timestamp"] = pd.to_datetime(ht.get("ts", pd.Timestamp.utcnow()))
                st.plotly_chart(
                    px.line(ht, x="timestamp", y="rates.quality", markers=True, 
                           title="Quality fail rate over time"),
                    use_container_width=True
                )

with T3:
    st.subheader("Boundary drift and adaptive signals")
    
    # SLO overlay section
    col_a, col_b = st.columns(2)
    
    # Get SLO status
    slo_status = analytics.get_slo_status(adaptive_state, last_report)
    
    # Boundary drift alert
    drift_status = slo_status['drift_status']
    boundary_offset = slo_status['drift_offset']
    
    col_a.metric(
        "Boundary drift",
        f"{boundary_offset:+.3f}",
        delta=drift_status,
        help="Treatment bucket boundary offset from baseline (0.5). SLO: ≤0.08"
    )
    
    if drift_status != "NORMAL":
        col_a.warning(f"⚠ Boundary drift {drift_status}: {abs(boundary_offset):.3f} (SLO: ≤0.08)")
    
    # Latency SLO
    p95 = slo_status['p95_latency']
    latency_status = slo_status['latency_status']
    
    col_b.metric(
        "P95 latency",
        f"{p95/1000:.1f}s",
        delta=f"{latency_status} (SLO: ≤20s)",
        help="95th percentile latency. SLO: ≤20,000ms"
    )
    
    if latency_status == "FAIL":
        col_b.error(f"❌ P95 latency exceeds SLO: {p95/1000:.1f}s > 20s")
    
    if rdf.empty:
        st.info("No response events yet.")
    else:
        dfv = rdf.copy()
        if conv_sel:
            dfv = dfv[dfv["conv_id"].isin(conv_sel)]
        
        # Extract boundary and weight
        boundary_col = "math_weights.adaptive.boundary" if "math_weights.adaptive.boundary" in dfv.columns else None
        weight_col = "math_weights.calculated_weight" if "math_weights.calculated_weight" in dfv.columns else None
        time_col = "ts" if "ts" in dfv.columns else None
        
        if boundary_col and time_col:
            dfb = dfv.dropna(subset=[boundary_col]).copy()
            if not dfb.empty:
                dfb["timestamp"] = pd.to_datetime(dfb[time_col])
                
                # Create chart with SLO lines
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dfb["timestamp"],
                    y=dfb[boundary_col],
                    mode='lines+markers',
                    name='Boundary'
                ))
                # Add SLO boundaries
                fig.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="Baseline (0.5)")
                fig.add_hline(y=0.58, line_dash="dot", line_color="red", annotation_text="SLO Max (+0.08)")
                fig.add_hline(y=0.42, line_dash="dot", line_color="red", annotation_text="SLO Min (-0.08)")
                fig.update_layout(title="Effective routing boundary over time (with SLO limits)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No boundary data in logs yet (adaptive routing may not have adjusted yet)")
        
        if weight_col and time_col:
            dfw = dfv.dropna(subset=[weight_col]).copy()
            if not dfw.empty:
                dfw["timestamp"] = pd.to_datetime(dfw[time_col])
                
                # Create chart with routing threshold
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dfw["timestamp"],
                    y=dfw[weight_col],
                    mode='markers',
                    name='Weight',
                    opacity=0.6
                ))
                fig.add_hline(y=0.5, line_dash="dash", line_color="blue", annotation_text="Routing threshold (0.5)")
                fig.update_layout(title="Calculated conversation weight over time")
                st.plotly_chart(fig, use_container_width=True)
        
        # Notes from adaptive
        if "math_weights.adaptive.adaptive_metadata" in dfv.columns:
            notes_df = dfv.dropna(subset=["math_weights.adaptive.adaptive_metadata"])
            if not notes_df.empty:
                st.write("Recent adaptive adjustments:")
                st.dataframe(
                    notes_df[["ts", "conv_id", "math_weights.adaptive.adaptive_metadata"]].tail(10),
                    use_container_width=True,
                    height=220
                )

with T4:
    st.subheader("Per-message events")
    if rdf.empty:
        st.info("No response events yet.")
    else:
        # Show available columns
        drilldown_cols = analytics.get_drilldown_columns()
        cols = [c for c in drilldown_cols if c in rdf.columns]
        
        if cols:
            view = rdf[cols].sort_values("ts", ascending=False) if "ts" in rdf.columns else rdf[cols]
            st.dataframe(view, use_container_width=True, height=450)
        else:
            st.warning("Response events found but no recognized columns. Check log format.")

with T5:
    st.subheader("Settings and diagnostics")
    st.write("**Paths:**")
    st.code(str(analytics.ndjson_path))
    st.code(str(analytics.adaptive_state_path))
    st.code(str(analytics.golden_last_path))
    st.code(str(analytics.golden_baseline_path))
    
    st.write("**Adaptive state (raw):**")
    st.json(adaptive_state or {})
    
    st.write("**Files status:**")
    st.write(f"- NDJSON events: {len(rdf)} response events, {len(hdf)} hypothesis batches")
    st.write(f"- Adaptive conversations tracked: {routing_metrics['total_conversations']}")
    st.write(f"- Control bucket samples: {routing_metrics['control_count']}")
    st.write(f"- Treatment bucket samples: {routing_metrics['treatment_count']}")

st.caption("Updates every ~10s with auto-refresh enabled. Adjust cache TTLs in code if needed.")
