#!/usr/bin/env python3
"""
UI Renderer for Streamlit Core
===============================

Handles all user interface rendering for the AIOS Streamlit UI system.
Renders sidebar, main interface, and all sub-components.

Key Features:
- Sidebar with system controls and state management
- Main interface with tabbed layout
- Chat interface for Luna
- Learning interface with meditation controls
- Analytics dashboard
- Settings configuration

Author: AIOS Development Team
Version: 1.0.0
"""

import streamlit as st

# Import from core modules
from .state_manager import StateManager
from .meditation_engine import MeditationEngine


class UIRenderer:
    """
    Renders the user interface for the AIOS Streamlit system.
    Coordinates between StateManager and MeditationEngine for UI updates.
    """
    
    def __init__(self, state_manager: StateManager, meditation_engine: MeditationEngine):
        """
        Initialize the UI renderer.
        
        Args:
            state_manager: StateManager instance for state operations
            meditation_engine: MeditationEngine instance for meditation features
        """
        self.state_manager = state_manager
        self.meditation_engine = meditation_engine
        
        print("🎨 UI Renderer Initialized")
    
    def render_sidebar(self):
        """Render the sidebar with persistent state management."""
        st.sidebar.title("🔧 System Controls")
        
        # Persistent State Management
        st.sidebar.subheader("💾 Persistent State")
        
        if st.sidebar.button("🗑️ Clear All State", type="secondary"):
            self.state_manager.clear_persistent_state()
            st.sidebar.success("State cleared!")
            st.rerun()
        
        # State Information
        state_info = self.state_manager.get_state_info()
        st.sidebar.write(f"**State Keys:** {state_info['num_keys']}")
        
        if state_info['num_keys'] > 0:
            st.sidebar.write(f"**State Size:** {state_info['size_kb']:.1f} KB")
        
        # Meditation Session Info
        session_info = self.meditation_engine.get_meditation_session_info()
        if session_info['active']:
            st.sidebar.subheader("🧘 Meditation Session")
            st.sidebar.write(f"**Status:** Active")
            st.sidebar.write(f"**Meditations:** {session_info['total_meditations']}")
            st.sidebar.write(f"**Karma:** {session_info['karma_gained']:.1f}")
        else:
            st.sidebar.subheader("🧘 Meditation Session")
            st.sidebar.write("**Status:** Inactive")
    
    def render_main_interface(self):
        """Render the main interface."""
        st.title("🌙 AIOS Clean - Luna Learning System")
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "🧠 Learning", "📊 Analytics", "🗺️ CodeGraph", "🔧 Settings"])
        
        with tab1:
            self._render_chat_interface()
        
        with tab2:
            self._render_learning_interface()
        
        with tab3:
            self._render_analytics_interface()
        
        with tab4:
            self._render_codegraph_viewer()

        with tab5:
            self._render_settings_interface()
    
    def _render_chat_interface(self):
        """Render the chat interface (wired to LM Studio via model_config)."""
        import time, requests, json
        from ..model_config import get_main_model
        
        st.header("💬 Chat with Luna")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Sidebar metrics
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("Messages", f"{len(st.session_state.chat_history)}")
        with mcol2:
            st.metric("Model", get_main_model())
        with mcol3:
            st.metric("Endpoint", "localhost:1234")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input box
        if prompt := st.chat_input("Ask Luna anything..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Call LM Studio (read-only; Streamlit core stays within its core)
            with st.chat_message("assistant"):
                t0 = time.perf_counter()
                try:
                    resp = requests.post(
                        "http://localhost:1234/v1/chat/completions",
                        json={
                            "model": get_main_model(),
                            "messages": [
                                {"role": "system", "content": "You are Luna. Be concise, helpful, and kind."},
                                *st.session_state.chat_history[-10:]  # last 10 messages
                            ],
                            "temperature": 0.7,
                            "max_tokens": 256
                        }, timeout=20
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data['choices'][0]['message']['content']
                    else:
                        content = f"[Error {resp.status_code}] {resp.text[:200]}"
                except Exception as e:
                    content = f"[Connection error] {e}"
                dt = time.perf_counter() - t0
                
                # Render and record
                st.markdown(content)
                st.caption(f"Response time: {dt:.2f}s • Model: {get_main_model()}")
                st.session_state.chat_history.append({"role": "assistant", "content": content})
    
    def _render_learning_interface(self):
        """Render the learning interface."""
        st.header("🧠 Luna Learning System")
        
        # Meditation Engine
        st.subheader("🧘 Meditation Engine")
        
        meditation_confirm = self.state_manager.get_state('meditation_confirm', False)
        
        if not meditation_confirm:
            st.info("Click below to start Luna's autonomous self-reflection mode")
            
            if st.button("🌙 Enter Meditation Mode (Self-Query Loop)", type="primary"):
                self.state_manager.set_state('meditation_confirm', True)
                st.rerun()
        else:
            st.warning("⚠️ Meditation mode requires confirmation")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ YES, Start Autonomous Reflection", type="primary"):
                    # Start meditation process
                    self.meditation_engine.start_meditation_session()
                    st.success("🧘 Meditation mode started!")
                    self.meditation_engine.update_heartbeat()
                    self.state_manager.set_state('meditation_confirm', False)
            
            with col2:
                if st.button("❌ Cancel", type="secondary"):
                    self.state_manager.set_state('meditation_confirm', False)
                    st.rerun()
        
        # Meditation Dashboard
        session_info = self.meditation_engine.get_meditation_session_info()
        if session_info['active']:
            st.subheader("📊 Meditation Dashboard")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Session Duration", f"{session_info['total_meditations']} cycles")
            with col2:
                st.metric("Karma Gained", f"{session_info['karma_gained']:.1f}")
            with col3:
                st.metric("Current State", session_info['current_state'])
            
            # Stop button
            if st.button("🛑 Stop Meditation", type="secondary"):
                self.meditation_engine.stop_meditation_session()
                st.success("Meditation session stopped")
                st.rerun()
    
    def _render_analytics_interface(self):
        """Render the analytics interface."""
        st.header("📊 System Analytics")
        
        # Placeholder for analytics
        st.info("Analytics interface coming soon...")
        st.write("This tab will display:")
        st.write("- System performance metrics")
        st.write("- Luna learning progress")
        st.write("- Meditation session history")
        st.write("- Karma accumulation trends")
    
    def _render_settings_interface(self):
        """Render the settings interface."""
        st.header("🔧 System Settings")
        
        # System configuration options
        st.subheader("System Configuration")
        
        # Model configuration display
        st.write("**Model Configuration:**")
        st.info("Model configuration is managed through config/model_config.json")
        
        # State management options
        st.subheader("State Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Persistent State:**")
            state_info = self.state_manager.get_state_info()
            st.write(f"- Keys: {state_info['num_keys']}")
            st.write(f"- Size: {state_info['size_kb']:.1f} KB")
            st.write(f"- File exists: {state_info['file_exists']}")
        
        with col2:
            st.write("**Meditation Engine:**")
            session_info = self.meditation_engine.get_meditation_session_info()
            st.write(f"- Active: {session_info['active']}")
            st.write(f"- Total sessions: {session_info['total_meditations']}")
            st.write(f"- Karma: {session_info['karma_gained']:.1f}")
        
        # Advanced settings
        st.subheader("Advanced Settings")
        st.info("Advanced settings interface coming soon...")

    # --- CodeGraph Viewer (Streamlit Core sub-node) ---
    def _render_codegraph_viewer(self):
        """Render the CodeGraph Mapper viewer.
        NOTE: This sub-node only reads artifacts from L:\\AIOS\\_maps and does
        not import from other cores or tool folders, respecting core boundaries.
        """
        import json
        from pathlib import Path
        import pandas as pd

        st.header("🗺️ AIOS CodeGraph Viewer")
        st.caption("Read-only view of repository structure generated by CodeGraph Mapper")

        maps_root = Path("L:/AIOS/_maps")
        if not maps_root.exists():
            st.warning("No maps found at L:/AIOS/_maps. Run the mapper first.")
            return

        # List runs (timestamped folders)
        runs = sorted([p for p in maps_root.iterdir() if p.is_dir()], reverse=True)
        run_labels = [p.name for p in runs]
        if not run_labels:
            st.info("No runs available yet.")
            return

        sel_idx = st.selectbox("Select run", options=list(range(len(run_labels))), format_func=lambda i: run_labels[i])
        run_dir = runs[sel_idx]

        graph_dir = run_dir / "graph"
        prov_path = run_dir / "provenance.json"

        # Load core artifacts lazily
        @st.cache_data(show_spinner=False)
        def load_json(path: Path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                return None

        provenance = load_json(prov_path) or {}
        nodes = load_json(graph_dir / "nodes.json") or []
        edges = load_json(graph_dir / "edges.json") or []

        # Metrics
        cols = st.columns(5)
        with cols[0]:
            st.metric("Nodes", f"{len(nodes):,}")
        with cols[1]:
            st.metric("Edges", f"{len(edges):,}")
        with cols[2]:
            st.metric("Modules", f"{sum(1 for n in nodes if n.get('kind')=='module'):,}")
        with cols[3]:
            st.metric("Files", f"{sum(1 for n in nodes if n.get('kind')=='file'):,}")
        with cols[4]:
            st.metric("Run ID", provenance.get("run_id", run_dir.name))

        st.divider()

        # Quick query tools (read-only, within this core)
        st.subheader("🔍 Quick Queries")
        colq1, colq2 = st.columns(2)

        # Imports from a module
        with colq1:
            src_mod = st.text_input("Module → show what it imports", value="main")
            if st.button("Show Imports", key="show_imports"):
                data = [
                    (e["src"].split(":",1)[1], e["dst"].split(":",1)[1], e["type"]) for e in edges
                    if e.get("type") in ("import","from_import") and e.get("src")==f"module:{src_mod}"
                ]
                if data:
                    df = pd.DataFrame(data, columns=["src","dst","type"])
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No imports found for that module.")

        # Reverse imports to a module
        with colq2:
            dst_mod = st.text_input("Module ← show who imports it", value="main_core.orchestration")
            if st.button("Show Importers", key="show_importers"):
                data = [
                    (e["src"].split(":",1)[1], e["dst"].split(":",1)[1], e["type"]) for e in edges
                    if e.get("type") in ("import","from_import") and e.get("dst")==f"module:{dst_mod}"
                ]
                if data:
                    df = pd.DataFrame(data, columns=["src","dst","type"])
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No importers found for that module.")

        st.subheader("🧭 Path Finder (module → module)")
        path_col1, path_col2 = st.columns([2,2])
        with path_col1:
            start_mod = st.text_input("Start module", value="main")
        with path_col2:
            goal_mod = st.text_input("Goal module", value="main_core.orchestration")

        if st.button("Find Path", type="primary"):
            # Build adjacency within this function to avoid cross-core imports
            from collections import defaultdict, deque
            g = defaultdict(set)
            for e in edges:
                if e.get("type") in ("import","from_import") and str(e.get("src","")) .startswith("module:") and str(e.get("dst","")) .startswith("module:"):
                    s = e["src"].split(":",1)[1]; d = e["dst"].split(":",1)[1]
                    g[s].add(d)
            q = deque([start_mod]); prev={start_mod: None}
            while q:
                u=q.popleft()
                if u==goal_mod: break
                for v in g.get(u,()):
                    if v not in prev:
                        prev[v]=u; q.append(v)
            if goal_mod not in prev:
                st.warning("No path found.")
            else:
                path=[]; cur=goal_mod
                while cur is not None:
                    path.append(cur); cur=prev[cur]
                st.success(" → ".join(reversed(path)))

