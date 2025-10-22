#!/usr/bin/env python3
"""
Dashboard Analytics for Streamlit Core
=======================================

Handles data loading, processing, and analytics for the AIOS Quality Dashboard.
Provides hypothesis tracking, routing metrics, and SLO monitoring.

Key Features:
- NDJSON hypothesis data loading
- Adaptive routing state analysis
- Golden report comparisons
- SLO status calculations
- Chart data preparation

Author: AIOS Development Team
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

import pandas as pd


class DashboardAnalytics:
    """
    Analytics engine for the AIOS Quality Dashboard.
    Loads and processes quality metrics, hypothesis tests, and routing data.
    """
    
    def __init__(self, root_path: Path = None):
        """
        Initialize dashboard analytics.
        
        Args:
            root_path: Root path for data files. Defaults to parent directory.
        """
        if root_path is None:
            root_path = Path(__file__).resolve().parents[2]
        
        self.root = root_path
        self.ndjson_path = self.root / "data_core/analytics/hypotheses.ndjson"
        self.adaptive_state_path = self.root / "data_core/analytics/adaptive_routing_state.json"
        self.golden_last_path = self.root / "data_core/goldens/last_report.json"
        self.golden_baseline_path = self.root / "data_core/goldens/baseline_new.json"
        
        print("📊 Dashboard Analytics Initialized")
        print(f"   Root: {self.root}")
    
    def read_ndjson(self, path: Path) -> List[dict]:
        """Read NDJSON file and return list of records."""
        if not path.exists():
            return []
        
        out = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    out.append(obj)
                except Exception:
                    # skip malformed line
                    continue
        return out
    
    def read_json(self, path: Path) -> dict:
        """Read JSON file and return dictionary."""
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    
    def load_frames(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and process hypothesis data into dataframes."""
        records = self.read_ndjson(self.ndjson_path)
        if not records:
            return pd.DataFrame(), pd.DataFrame()
        
        df = pd.DataFrame(records)

        # Response events (default kind)
        rdf = df[df.get("event_type", "response").fillna("response") == "response"].copy()
        
        # Flatten nested fields safely
        for col in ("meta", "carma", "math_weights", "routing", "adaptive"):
            if col in rdf.columns:
                try:
                    expanded = pd.json_normalize(rdf[col].dropna())
                    if not expanded.empty:
                        expanded.columns = [f"{col}.{c}" for c in expanded.columns]
                        rdf = pd.concat([rdf.drop(columns=[col], errors='ignore'), expanded], axis=1)
                except Exception as e:
                    pass  # Skip if normalization fails

        # Hypothesis batches
        hdf = df[df.get("event_type") == "hypothesis_batch"].copy()
        
        # Expand aggregate rates and basic counts
        if not hdf.empty and "results" in hdf.columns:
            hdf["rates.quality"] = hdf["results"].apply(
                lambda r: (r.get("rates") or {}).get("quality") if isinstance(r, dict) else None
            )
            hdf["rates.latency"] = hdf["results"].apply(
                lambda r: (r.get("rates") or {}).get("latency") if isinstance(r, dict) else None
            )
            hdf["rates.memory"] = hdf["results"].apply(
                lambda r: (r.get("rates") or {}).get("memory") if isinstance(r, dict) else None
            )
            hdf["passed"] = hdf["results"].apply(
                lambda r: r.get("passed") if isinstance(r, dict) else None
            )
            hdf["failed"] = hdf["results"].apply(
                lambda r: r.get("failed") if isinstance(r, dict) else None
            )
            hdf["total"] = hdf["results"].apply(
                lambda r: r.get("total") if isinstance(r, dict) else None
            )
            hdf["batch_id"] = hdf["results"].apply(
                lambda r: r.get("batch_id") if isinstance(r, dict) else None
            )
        
        return rdf, hdf
    
    def load_adaptive_state(self) -> dict:
        """Load adaptive routing state."""
        return self.read_json(self.adaptive_state_path)
    
    def load_golden_reports(self) -> Tuple[dict, dict]:
        """Load golden reports (last and baseline)."""
        return self.read_json(self.golden_last_path), self.read_json(self.golden_baseline_path)
    
    def calculate_hypothesis_pass_rate(self, hdf: pd.DataFrame) -> Tuple[int, int, float]:
        """
        Calculate hypothesis pass rate from hypothesis dataframe.
        
        Returns:
            Tuple of (total_cases, total_pass, pass_rate)
        """
        if hdf.empty or "total" not in hdf.columns or "passed" not in hdf.columns:
            return 0, 0, None
        
        total_cases = int(hdf["total"].dropna().sum())
        total_pass = int(hdf["passed"].dropna().sum())
        pass_rate = (total_pass / total_cases) if total_cases > 0 else None
        
        return total_cases, total_pass, pass_rate
    
    def get_routing_metrics(self, adaptive_state: dict) -> Dict[str, Any]:
        """
        Extract routing metrics from adaptive state.
        
        Returns:
            Dictionary with control_count, treatment_count, treatment_boundary
        """
        control_count = adaptive_state.get("buckets", {}).get("control", {}).get("sample_count", 0)
        treatment_count = adaptive_state.get("buckets", {}).get("treatment", {}).get("sample_count", 0)
        treatment_boundary = adaptive_state.get("buckets", {}).get("treatment", {}).get("boundary", 0.5)
        
        return {
            'control_count': control_count,
            'treatment_count': treatment_count,
            'treatment_boundary': treatment_boundary,
            'total_conversations': adaptive_state.get("total_conversations", 0)
        }
    
    def get_slo_status(self, adaptive_state: dict, last_report: dict) -> Dict[str, Any]:
        """
        Calculate SLO status for boundary drift and latency.
        
        Returns:
            Dictionary with drift_status, latency_status, and related metrics
        """
        status = {
            'drift_status': 'NORMAL',
            'drift_offset': 0.0,
            'latency_status': 'PASS',
            'p95_latency': 0.0,
            'slo_p95': 20000.0
        }
        
        # Boundary drift
        if adaptive_state.get("buckets"):
            treatment = adaptive_state["buckets"].get("treatment", {})
            boundary_offset = treatment.get("boundary_offset", 0.0)
            status['drift_offset'] = boundary_offset
            
            if abs(boundary_offset) <= 0.05:
                status['drift_status'] = 'NORMAL'
            elif abs(boundary_offset) <= 0.08:
                status['drift_status'] = 'WARNING'
            else:
                status['drift_status'] = 'CRITICAL'
        
        # Latency SLO
        if last_report.get("metrics"):
            p95 = last_report["metrics"].get("p95_ms", 0)
            status['p95_latency'] = p95
            status['latency_status'] = 'PASS' if p95 <= status['slo_p95'] else 'FAIL'
        
        return status
    
    def prepare_bucket_distribution_data(self, routing_metrics: Dict[str, Any]) -> pd.DataFrame:
        """Prepare data for bucket distribution pie chart."""
        return pd.DataFrame([
            {"bucket": "control", "count": routing_metrics['control_count']},
            {"bucket": "treatment", "count": routing_metrics['treatment_count']}
        ])
    
    def prepare_source_distribution_data(self, rdf: pd.DataFrame, 
                                         conv_filter: List[str] = None) -> pd.DataFrame:
        """Prepare data for source distribution pie chart."""
        if rdf.empty:
            return pd.DataFrame()
        
        dfv = rdf.copy()
        if conv_filter:
            dfv = dfv[dfv["conv_id"].isin(conv_filter)]
        
        source_col = "meta.source" if "meta.source" in dfv.columns else None
        
        if source_col and source_col in dfv.columns:
            vs = dfv[source_col].fillna("unknown").value_counts().reset_index()
            vs.columns = ["source", "count"]
            return vs
        
        return pd.DataFrame()
    
    def get_hypothesis_view_columns(self) -> List[str]:
        """Get columns for hypothesis batch view."""
        return [
            "ts", "conv_id", "msg_id", "passed", "failed", 
            "rates.quality", "rates.latency", "rates.memory", "batch_id"
        ]
    
    def get_drilldown_columns(self) -> List[str]:
        """Get columns for per-message drilldown view."""
        return [
            "ts", "conv_id", "msg_id", "question", "trait", "meta.source",
            "math_weights.adaptive.bucket", "math_weights.adaptive.boundary",
            "math_weights.calculated_weight", "math_weights.mode",
            "carma.fragments_found"
        ]

