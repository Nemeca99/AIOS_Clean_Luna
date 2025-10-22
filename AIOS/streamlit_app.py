"""
AIOS - Adaptive Intelligence Operating System
Streamlit UI Entry Point

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import cores
try:
    from luna_core.core.luna_core import LunaSystem
    from carma_core.carma_core import CARMASystem
    from fractal_core.fractal_core import FractalCore
except ImportError as e:
    st.error(f"Failed to import AIOS cores: {e}")
    st.error("Run setup.ps1 to configure the system first.")
    st.stop()

# Page config
st.set_page_config(
    page_title="AIOS Luna",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "luna" not in st.session_state:
    try:
        st.session_state.luna = LunaSystem()
        st.session_state.messages = []
        st.session_state.initialized = True
    except Exception as e:
        st.error(f"Failed to initialize Luna: {e}")
        st.error("Check LM Studio is running on localhost:1234")
        st.session_state.initialized = False

# Sidebar configuration
with st.sidebar:
    st.title("🧠 AIOS Configuration")
    
    st.markdown("---")
    st.subheader("Personality Settings")
    
    trait = st.selectbox(
        "Primary Trait",
        ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"],
        index=0,
        help="Luna's personality dimension for this conversation"
    )
    
    st.markdown("---")
    st.subheader("System Status")
    
    if st.session_state.get("initialized"):
        st.success("Luna: Online")
        
        # Show system stats
        if hasattr(st.session_state.luna, 'existential_budget'):
            budget = st.session_state.luna.existential_budget
            st.metric("Generation", budget.state.age)
            st.metric("Karma", f"{budget.state.current_karma:.1f}/{budget.state.karma_quota:.0f}")
            st.metric("Token Pool", f"{budget.state.current_token_pool:,}")
    else:
        st.error("Luna: Offline")
    
    st.markdown("---")
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("Luna - Adaptive Intelligence")

if not st.session_state.get("initialized"):
    st.warning("System not initialized. Run setup.ps1 first.")
    st.code(".\setup.ps1", language="powershell")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask Luna anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get Luna response
    with st.chat_message("assistant"):
        with st.spinner("Luna thinking..."):
            try:
                # LunaSystem.learning_chat() determines trait internally
                response = st.session_state.luna.learning_chat(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
                st.error("Check that LM Studio is running and models are loaded.")

