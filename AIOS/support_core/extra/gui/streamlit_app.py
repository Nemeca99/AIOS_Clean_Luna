#!/usr/bin/env python3
"""
AIOS Clean - Streamlit Web Interface
Web interface for the AIOS Clean system using the unified main.py as foundation.
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
import json
import re
import pickle
import time
from datetime import datetime
from main import AIOSClean

# Optional imports for analytics (gracefully handle if missing)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Persistent state management
STATE_FILE = Path("streamlit_state.pkl")

def load_persistent_state():
    """Load persistent state from file with memory leak protection."""
    if STATE_FILE.exists():
        try:
            # Check file size to prevent loading huge files
            file_size = STATE_FILE.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                print(f"Warning: State file too large ({file_size} bytes), clearing it")
                STATE_FILE.unlink()
                return {}
            
            with open(STATE_FILE, 'rb') as f:
                state = pickle.load(f)
                
            # Validate state is a dictionary and not too large
            if not isinstance(state, dict):
                print("Warning: Invalid state format, clearing")
                STATE_FILE.unlink()
                return {}
                
            # Limit number of keys to prevent memory bloat
            if len(state) > 1000:
                print(f"Warning: Too many state keys ({len(state)}), clearing old state")
                STATE_FILE.unlink()
                return {}
                
            return state
            
        except (pickle.PickleError, EOFError, OSError) as e:
            print(f"Error loading state: {e}, clearing corrupted file")
            try:
                STATE_FILE.unlink()
            except (FileNotFoundError, OSError) as e:
                # State file already doesn't exist - that's fine
                print(f"Note: State file removal skipped: {e}")
            return {}
    return {}

def save_persistent_state(state):
    """Save persistent state to file with memory leak protection."""
    try:
        # Validate state before saving
        if not isinstance(state, dict):
            print("Error: State must be a dictionary")
            return
            
        # Limit state size
        if len(state) > 1000:
            print("Error: Too many state keys, not saving")
            return
            
        # Create backup before overwriting
        if STATE_FILE.exists():
            backup_file = STATE_FILE.with_suffix('.bak')
            try:
                STATE_FILE.rename(backup_file)
            except (FileNotFoundError, OSError) as e:
                # State file doesn't exist to backup - that's fine
                print(f"Note: State backup skipped: {e}")
        
        # Write new state
        with open(STATE_FILE, 'wb') as f:
            pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        # Remove backup if successful
        backup_file = STATE_FILE.with_suffix('.bak')
        if backup_file.exists():
            backup_file.unlink()
            
    except Exception as e:
        print(f"Error saving state: {e}")
        # Restore backup if save failed
        backup_file = STATE_FILE.with_suffix('.bak')
        if backup_file.exists():
            try:
                backup_file.rename(STATE_FILE)
            except (FileNotFoundError, OSError) as e:
                # Backup file doesn't exist to restore - that's fine
                print(f"Note: State restoration from backup failed: {e}")

def get_state(key, default=None):
    """Get a state value, with persistent fallback and memory protection."""
    # Limit key length to prevent memory issues
    if not isinstance(key, str) or len(key) > 100:
        print(f"Warning: Invalid state key: {key}")
        return default
        
    if key not in st.session_state:
        persistent_state = load_persistent_state()
        if key in persistent_state:
            value = persistent_state[key]
            # Validate value size
            try:
                import sys
                value_size = sys.getsizeof(value)
                if value_size > 1024 * 1024:  # 1MB limit per value
                    print(f"Warning: State value too large ({value_size} bytes), using default")
                    st.session_state[key] = default
                    return default
            except Exception as e:
                # State loading failed - use default
                print(f"Warning: Could not load state for {key}: {e}")
            st.session_state[key] = value
        else:
            st.session_state[key] = default
    return st.session_state[key]

def set_state(key, value, persistent=True):
    """Set a state value with memory leak protection."""
    # Validate key
    if not isinstance(key, str) or len(key) > 100:
        print(f"Warning: Invalid state key: {key}")
        return
        
    # Validate value size
    try:
        import sys
        value_size = sys.getsizeof(value)
        if value_size > 1024 * 1024:  # 1MB limit per value
            print(f"Warning: State value too large ({value_size} bytes), not setting")
            return
    except Exception as e:
        # Size check failed - proceed anyway
        print(f"Warning: Could not check state size: {e}")
    
    st.session_state[key] = value
    if persistent:
        persistent_state = load_persistent_state()
        persistent_state[key] = value
        save_persistent_state(persistent_state)

def clear_persistent_state():
    """Clear all persistent state with cleanup."""
    try:
        # Clear session state
        st.session_state.clear()
        
        # Remove state file and backup
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        backup_file = STATE_FILE.with_suffix('.bak')
        if backup_file.exists():
            backup_file.unlink()
            
    except Exception as e:
        print(f"Error clearing state: {e}")

def cleanup_old_state_files():
    """Clean up old or corrupted state files."""
    try:
        # Clean up backup files older than 1 hour
        backup_file = STATE_FILE.with_suffix('.bak')
        if backup_file.exists():
            import time
            file_age = time.time() - backup_file.stat().st_mtime
            if file_age > 3600:  # 1 hour
                backup_file.unlink()
                
        # Clean up any temp files
        for temp_file in STATE_FILE.parent.glob(f"{STATE_FILE.stem}.*.tmp"):
            try:
                temp_file.unlink()
            except (FileNotFoundError, OSError) as e:
                # Temp file already removed - that's fine
                print(f"Note: Temp file cleanup skipped: {e}")
                
    except Exception as e:
        print(f"Error cleaning up state files: {e}")

# Page configuration
st.set_page_config(
    page_title="AIOS Clean",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for visual effects
st.markdown("""
<style>
    /* Dark Gothic Theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a1a 100%);
    }
    
    /* Animated gradient border for main container */
    .main .block-container {
        background: linear-gradient(145deg, rgba(20,20,30,0.9), rgba(30,20,40,0.9));
        border: 2px solid transparent;
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(138, 43, 226, 0.3);
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(138, 43, 226, 0.3); }
        50% { box-shadow: 0 0 40px rgba(138, 43, 226, 0.6); }
    }
    
    /* Luna's message glow effect */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: linear-gradient(135deg, rgba(75, 0, 130, 0.2), rgba(138, 43, 226, 0.2));
        border-left: 3px solid #8a2be2;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* User message styling */
    .stChatMessage[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, rgba(0, 100, 150, 0.2), rgba(0, 150, 200, 0.2));
        border-left: 3px solid #00bcd4;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Metrics with glow */
    .stMetric {
        background: rgba(138, 43, 226, 0.1);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(138, 43, 226, 0.3);
    }
    
    .stMetric:hover {
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.5);
        transition: all 0.3s ease;
    }
    
    /* Animated tab indicators */
    .stTabs [data-baseweb="tab"] {
        background: rgba(138, 43, 226, 0.1);
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(138, 43, 226, 0.3);
        transform: translateY(-2px);
    }
    
    /* Pulsing effect for "thinking" state */
    @keyframes pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* Button glow effects */
    .stButton>button {
        background: linear-gradient(135deg, #8a2be2, #4b0082);
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(138, 43, 226, 0.8);
        transform: scale(1.05);
    }
    
    /* Sidebar gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0a1a 0%, #0a0a1a 100%);
        border-right: 2px solid rgba(138, 43, 226, 0.3);
    }
    
    /* Expander glow on expand */
    .streamlit-expanderHeader {
        background: rgba(138, 43, 226, 0.1);
        border-radius: 5px;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(138, 43, 226, 0.2);
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.4);
    }
    
    /* Chart containers */
    .js-plotly-plot {
        border-radius: 10px;
        padding: 10px;
        background: rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'aios_system' not in st.session_state:
    st.session_state.aios_system = None
    st.session_state.initialized = False
    st.session_state.chat_history = []
    st.session_state.luna_stats = {
        'total_questions': 0,
        'total_karma': 0.0,
        'generation': 0,
        'bigfive_answered': 0
    }

# Cleanup old state files on startup
cleanup_old_state_files()

# Sidebar
st.sidebar.title(" AIOS Clean")
st.sidebar.markdown("AI Performance System")

# Initialize system button
if st.sidebar.button(" Initialize System", type="primary"):
    with st.spinner("Initializing AIOS Clean System..."):
        st.session_state.aios_system = AIOSClean()
        st.session_state.initialized = True
    st.success("System initialized successfully!")

# Persistent state management
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Persistent State")

# Show current persistent state (with memory protection)
try:
    persistent_state = load_persistent_state()
    if persistent_state:
        st.sidebar.info(f"📁 State file: `{STATE_FILE.name}`")
        
        # Safe display of state items (limit to prevent memory issues)
        display_items = {}
        count = 0
        for k, v in persistent_state.items():
            if count >= 3:  # Limit to 3 items
                break
            # Only show simple values to prevent memory leaks
            if isinstance(v, (str, int, float, bool, type(None))):
                display_items[k] = v
                count += 1
            elif isinstance(v, (list, dict)) and len(str(v)) < 100:
                display_items[k] = v
                count += 1
        
        if display_items:
            st.sidebar.json(display_items)
        else:
            st.sidebar.caption("State contains complex objects")
            
        if len(persistent_state) > 3:
            st.sidebar.caption(f"... and {len(persistent_state) - 3} more items")
    else:
        st.sidebar.info("📁 No persistent state saved")
except Exception as e:
    st.sidebar.error(f"Error loading state: {e}")
    st.sidebar.info("📁 State file may be corrupted")

# Clear state button
if st.sidebar.button("🗑️ Clear All State", type="secondary"):
    clear_persistent_state()
    st.sidebar.success("✅ All persistent state cleared!")
    st.rerun()

# Main interface
if st.session_state.initialized and st.session_state.aios_system:
    
    # System status
    st.title(" System Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = st.session_state.aios_system.get_quick_status()
        st.metric("System Status", status['status'].title())
    
    with col2:
        st.metric("CARMA Fragments", status['carma_fragments'])
    
    with col3:
        st.metric("Luna Interactions", status['luna_interactions'])
    
    with col4:
        st.metric("Support Fragments", status['support_fragments'])
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬 Chat with Luna",
        "🧠 Luna Learning", 
        "🗂️ CARMA",
        "📊 Analytics",
        "❤️ Health", 
        "🧪 Testing", 
        "⚙️ Settings"
    ])
    
    with tab1:
        st.header("💬 Chat with Luna")
        
        # Get current Luna stats
        try:
            luna_system = st.session_state.aios_system.luna_system
            current_karma = luna_system.arbiter_system.get_current_karma()
            current_gen = luna_system.cfia_system.state.aiiq
            bigfive_count = len(luna_system.personality_system.internal_reasoning.bigfive_answer_history)
            
            # Display stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Generation", f"Gen {current_gen}")
            with col2:
                st.metric("Karma", f"{current_karma:.1f}")
            with col3:
                st.metric("Files", luna_system.cfia_system.state.total_files)
            with col4:
                st.metric("Self-Knowledge", f"{bigfive_count}/15")
        except Exception as e:
            # Big Five metrics not available - skip display
            print(f"Note: Big Five metrics not available: {e}")
        
        # Chat interface
        st.markdown("---")
        
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("metadata"):
                    with st.expander("🧠 Luna's Thought Process"):
                        meta = message["metadata"]
                        st.write(f"**Trait Classification:** {meta.get('dominant_trait', 'N/A')}")
                        st.write(f"**Confidence:** {meta.get('confidence', 0):.1%}")
                        if meta.get('bigfive_reasoning'):
                            st.write("**Internal Reasoning:**")
                            for reasoning in meta['bigfive_reasoning']:
                                st.write(f"  💭 {reasoning}")
                        # Debug info
                        st.caption(f"Message #{i+1}")
        
        # Chat input
        user_input = st.chat_input("Ask Luna anything...")
        
        if user_input:
            # Check if we've already processed this input to prevent duplicates
            if 'last_processed_input' not in st.session_state or st.session_state.last_processed_input != user_input:
                st.session_state.last_processed_input = user_input
                
                # Also check if we've already added this user message to prevent duplicates
                if not (st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user" and st.session_state.chat_history[-1]["content"] == user_input):
                    # Add user message to chat
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                
                # Process through Luna
                with st.spinner("Luna is thinking..."):
                    try:
                        # Build session memory from chat history
                        session_memory = []
                        for i in range(0, len(st.session_state.chat_history)-1, 2):
                            if i+1 < len(st.session_state.chat_history):
                                user_msg = st.session_state.chat_history[i]
                                assistant_msg = st.session_state.chat_history[i+1]
                                if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                                    session_memory.append({
                                        "question": user_msg["content"],
                                        "response": assistant_msg["content"]
                                    })
                        
                        # Get Luna's response using learning chat (preserves personality and learning)
                        response = luna_system.learning_chat(user_input, session_memory)
                        
                        # Ensure we have a valid response
                        if not response or response.strip() == "":
                            response = "*tilts head* I'm having trouble responding right now."
                        
                        # Get trait classification from personality system
                        try:
                            reasoning_result = luna_system.personality_system.internal_reasoning.reason_through_question(user_input)
                            dominant_trait = reasoning_result.matched_bigfive_questions[0]['domain'] if reasoning_result.matched_bigfive_questions else 'general'
                            confidence = reasoning_result.matched_bigfive_questions[0]['similarity'] if reasoning_result.matched_bigfive_questions else 0.0
                        except Exception as e:
                            print(f"Trait classification error: {e}")
                            dominant_trait = 'general'
                            confidence = 0.0
                        
                        # Metadata for learning chat mode
                        metadata = {
                            'mode': 'learning_chat',
                            'response_length': len(response.split()) if response else 0,
                            'timestamp': datetime.now().isoformat(),
                            'learning_enabled': True,
                            'dominant_trait': dominant_trait,
                            'confidence': confidence
                        }
                        
                        # Get current karma
                        current_karma = luna_system.arbiter_system.get_current_karma()
                        
                        # Add Luna's response to chat
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "metadata": metadata
                        })
                        
                        # Update stats
                        st.session_state.luna_stats['total_questions'] += 1
                        st.session_state.luna_stats['total_karma'] = current_karma
                        st.session_state.luna_stats['generation'] = luna_system.cfia_system.state.aiiq
                        st.session_state.luna_stats['bigfive_answered'] = len(luna_system.personality_system.internal_reasoning.bigfive_answer_history)
                        
                    except Exception as e:
                        st.error(f"Error generating response: {e}")
                        # Add error message to chat history so user knows something went wrong
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"I encountered an error: {str(e)}",
                            "metadata": {"mode": "error", "timestamp": datetime.now().isoformat()}
                        })
            
            st.rerun()
    
    with tab2:
        st.header("🧠 Luna Learning Sessions")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            questions = st.slider("Number of Questions", 1, 120, 10)
            
            col_learn1, col_learn2 = st.columns(2)
            
            with col_learn1:
                if st.button("Run Luna Learning Session", type="primary"):
                    with st.spinner("Running Luna learning session..."):
                        results = st.session_state.aios_system.run_luna_learning(questions)
                    
                    st.success("Luna learning session completed!")
                    st.json(results)
            
            with col_learn2:
                # Use persistent state for meditation mode
                meditation_confirm = get_state('meditation_confirm', False)
                
                if not meditation_confirm:
                    st.warning("⚠️ **The Meditation Engine** - Autonomous Self-Reflection")
                    st.markdown("""
                    **This is the ultimate self-governance test:**
                    - Pure, self-directed introspection
                    - Controlled entirely by the Arbiter (logic center)
                    - Validates core philosophical architecture
                    - Tests efficiency, self-correction, conscientiousness
                    - System runs autonomously without external stimulus
                    """)
                    
                    if st.button("🧘 Enter Meditation Mode", type="secondary"):
                        import uuid
                        session_id = str(uuid.uuid4())
                        set_state('meditation_confirm', True)
                        set_state('meditation_session_id', session_id, persistent=False)  # Don't persist session ID
                        set_state('meditation_start_time', time.time())
                        st.success("✅ Meditation Mode Activated!")
                        st.info("Scroll down to see the instructions below.")
                        st.rerun()
                
                else:
                    st.success("🧘 **Meditation Engine Active** - Pure Self-Governance")
                    st.markdown("""
                    **The Meditation Engine is now running:**
                    - Self-query generation via Arbiter/Embedder
                    - Autonomous self-answer analysis
                    - Existential Budget validation in isolation
                    - Karma Pool growth through self-correction
                    """)
                    
                    st.code("python meditation_controller.py --heartbeat 5", language="bash")
                    st.caption("Or try the simple version (no browser detection):")
                    st.code("python simple_meditation.py --heartbeat 5", language="bash")
                    st.warning("⚠️ **Emergency Brake:** Press Ctrl+C to exit meditation mode")
                    
                    if st.button("🛑 Exit Meditation Mode", type="secondary"):
                        set_state('meditation_confirm', False)
                        st.success("✅ Meditation Mode Deactivated!")
                        st.rerun()
        
        with col2:
            st.info("""
            **Luna AI Features:**
            - Big Five personality assessment
            - Internal reasoning system
            - Self-knowledge building
            - Trait classification
            - Persistent memory
            """)
        
        # Check if meditation should still be running (browser-based detection)
        if get_state('meditation_confirm', False):
            # Check if this is a fresh page load (browser was closed/reopened)
            if 'meditation_session_id' not in st.session_state:
                # Browser was closed, stop meditation mode
                set_state('meditation_confirm', False)
                st.warning("🔄 Meditation mode stopped - browser session ended")
                st.rerun()
            
            # Update heartbeat file to show browser is still active
            try:
                heartbeat_data = {
                    'last_heartbeat': time.time(),
                    'meditation_count': get_state('meditation_count', 0),
                    'current_state': get_state('current_state', 'self_inquiry')
                }
                
                heartbeat_file = Path("meditation_heartbeat.json")
                with open(heartbeat_file, 'w') as f:
                    json.dump(heartbeat_data, f)
                    
            except Exception as e:
                print(f"Error updating heartbeat: {e}")
        
        # Show meditation instructions when active
        if get_state('meditation_confirm', False):
            st.markdown("---")
            st.header("🧘 Meditation Engine Instructions")
            
            col_inst1, col_inst2 = st.columns(2)
            
            with col_inst1:
                st.subheader("🚀 Quick Start")
                st.code("""
# Browser-Aware (stops when browser closes)
python meditation_controller.py --heartbeat 5

# Simple Version (no browser detection)
python simple_meditation.py --heartbeat 5

# Windows Batch
start_meditation.bat

# PowerShell  
./start_meditation.ps1
                """, language="bash")
            
            with col_inst2:
                st.subheader("📊 What You'll See")
                st.markdown("""
- **Meditation States**: Cycles through 5 states every 5 questions
- **Self-Queries**: Arbiter generates questions based on current state
- **Self-Reflection**: Luna answers using her learning system
- **Karma Tracking**: Real-time karma gain and efficiency scores
- **Progress Stats**: Total meditations, average efficiency, peak performance
                """)
            
            st.subheader("🎯 Meditation States")
            states = {
                "🧠 Self-Inquiry": "Who am I? What makes me unique?",
                "💎 Values Exploration": "What do I value? What matters to me?",
                "🔍 Behavior Analysis": "How do I typically respond? What patterns do I notice?",
                "🌱 Growth Reflection": "How have I changed? What insights surprise me?",
                "✨ Wisdom Integration": "What wisdom am I developing? How do I apply my knowledge?"
            }
            
            for state, description in states.items():
                st.markdown(f"**{state}**: {description}")
            
            st.info("💡 **Tip**: The Meditation Engine will run continuously until you press Ctrl+C or close the browser. Each meditation builds Luna's self-knowledge and validates her core philosophical architecture.")
            
            # Real-time meditation dashboard
            st.markdown("---")
            st.subheader("📊 Real-Time Meditation Dashboard")
            
            heartbeat_file = Path("meditation_heartbeat.json")
            session_file = Path("meditation_session.json")
            
            if heartbeat_file.exists() and session_file.exists():
                try:
                    # Load heartbeat data
                    with open(heartbeat_file, 'r') as f:
                        heartbeat_data = json.load(f)
                    
                    # Load session data
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    last_heartbeat = heartbeat_data.get('last_heartbeat', 0)
                    time_since_heartbeat = time.time() - last_heartbeat
                    
                    # Calculate session duration
                    session_start = session_data.get('start_time', time.time())
                    session_duration = time.time() - session_start
                    
                    # Format duration
                    hours = int(session_duration // 3600)
                    minutes = int((session_duration % 3600) // 60)
                    seconds = int(session_duration % 60)
                    
                    if hours > 0:
                        duration_str = f"{hours}h {minutes}m {seconds}s"
                    elif minutes > 0:
                        duration_str = f"{minutes}m {seconds}s"
                    else:
                        duration_str = f"{seconds}s"
                    
                    # Status indicator
                    if time_since_heartbeat < 30:
                        st.success("🟢 Meditation Controller: Active")
                    else:
                        st.warning("🟡 Meditation Controller: May have stopped")
                    
                    # Key metrics in columns
                    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
                    
                    meditation_count = heartbeat_data.get('meditation_count', 0)
                    current_state = heartbeat_data.get('current_state', 'unknown')
                    total_karma = heartbeat_data.get('total_karma', 0)
                    avg_efficiency = heartbeat_data.get('avg_efficiency', 0)
                    last_response_time = heartbeat_data.get('last_response_time', 0)
                    last_efficiency = heartbeat_data.get('last_efficiency', 0)
                    
                    with col_metric1:
                        st.metric(
                            label="🕐 Session Duration",
                            value=duration_str,
                            help="Total time meditation has been running"
                        )
                    
                    with col_metric2:
                        st.metric(
                            label="🧘 Total Meditations",
                            value=meditation_count,
                            help="Number of self-reflection questions processed"
                        )
                    
                    with col_metric3:
                        state_display = current_state.replace('_', ' ').title()
                        st.metric(
                            label="🎯 Current State",
                            value=state_display,
                            help="Current meditation state (changes every 5 questions)"
                        )
                    
                    with col_metric4:
                        if meditation_count > 0:
                            meditations_per_minute = meditation_count / (session_duration / 60)
                            st.metric(
                                label="⚡ Meditations/Min",
                                value=f"{meditations_per_minute:.1f}",
                                help="Rate of self-reflection questions per minute"
                            )
                        else:
                            st.metric(
                                label="⚡ Meditations/Min",
                                value="0.0",
                                help="Rate of self-reflection questions per minute"
                            )
                    
                    # Second row of metrics
                    col_metric5, col_metric6, col_metric7, col_metric8 = st.columns(4)
                    
                    with col_metric5:
                        st.metric(
                            label="💰 Total Karma",
                            value=f"{total_karma:.1f}",
                            help="Total karma gained from self-reflection"
                        )
                    
                    with col_metric6:
                        st.metric(
                            label="📊 Avg Efficiency",
                            value=f"{avg_efficiency:.1f} w/s",
                            help="Average words per second across all responses"
                        )
                    
                    with col_metric7:
                        st.metric(
                            label="⏱️ Last Response",
                            value=f"{last_response_time:.1f}s",
                            help="Processing time of the most recent response"
                        )
                    
                    with col_metric8:
                        st.metric(
                            label="🚀 Last Efficiency",
                            value=f"{last_efficiency:.1f} w/s",
                            help="Efficiency of the most recent response"
                        )
                    
                    # Detailed stats section
                    st.markdown("#### 📈 Detailed Statistics")
                    
                    col_detail1, col_detail2 = st.columns(2)
                    
                    with col_detail1:
                        st.markdown("**🔄 Meditation States Progress:**")
                        
                        # Show progress through meditation states
                        states = ["self_inquiry", "values_exploration", "behavior_analysis", "growth_reflection", "wisdom_integration"]
                        current_state_index = states.index(current_state) if current_state in states else 0
                        
                        for i, state in enumerate(states):
                            state_name = state.replace('_', ' ').title()
                            if i == current_state_index:
                                st.markdown(f"🟢 **{state_name}** (Current)")
                            elif i < current_state_index:
                                st.markdown(f"✅ {state_name} (Completed)")
                            else:
                                st.markdown(f"⏳ {state_name} (Pending)")
                        
                        # State progress within current state
                        state_progress = (meditation_count % 5) + 1
                        st.progress(state_progress / 5, text=f"Progress in current state: {state_progress}/5")
                    
                    with col_detail2:
                        st.markdown("**📊 Session Information:**")
                        
                        # Session details
                        session_id = session_data.get('session_id', 'Unknown')
                        st.markdown(f"**Session ID:** `{session_id}`")
                        
                        # Last activity
                        if time_since_heartbeat < 60:
                            st.markdown(f"**Last Activity:** {time_since_heartbeat:.1f} seconds ago")
                        else:
                            st.markdown(f"**Last Activity:** {time_since_heartbeat/60:.1f} minutes ago")
                        
                        # Estimated completion
                        if meditation_count > 0:
                            avg_time_per_meditation = session_duration / meditation_count
                            remaining_meditations = 25 - (meditation_count % 25)  # Assuming 25 meditations per full cycle
                            estimated_completion = remaining_meditations * avg_time_per_meditation
                            
                            if estimated_completion > 0:
                                completion_minutes = int(estimated_completion // 60)
                                completion_seconds = int(estimated_completion % 60)
                                
                                if completion_minutes > 0:
                                    completion_str = f"{completion_minutes}m {completion_seconds}s"
                                else:
                                    completion_str = f"{completion_seconds}s"
                                
                                st.markdown(f"**Est. Next State:** {completion_str}")
                        
                        # System status
                        st.markdown(f"**System Status:** {'Healthy' if time_since_heartbeat < 30 else 'Checking...'}")
                    
                    # Auto-refresh every 10 seconds when meditation is active
                    if time_since_heartbeat < 30:
                        time.sleep(10)
                        st.rerun()
                        
                except Exception as e:
                    st.error("🔴 Meditation Controller: Status unknown")
                    st.caption(f"Error reading status: {e}")
            else:
                st.info("⚪ Meditation Controller: Not running")
                st.caption("Start the controller script to begin meditation")
    
    with tab3:
        st.header("🗂️ CARMA Performance System")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            queries = st.text_area(
                "Enter CARMA Learning Queries (one per line):",
                value="I am learning about artificial intelligence\nThis is a test query\nMemory consolidation is important",
                height=100
            )
            
            if st.button("Run CARMA Learning Session", type="primary"):
                query_list = [q.strip() for q in queries.split('\n') if q.strip()]
                with st.spinner("Running CARMA learning session..."):
                    results = st.session_state.aios_system.run_carma_learning(query_list)
                
                st.success("CARMA learning session completed!")
                st.json(results)
        
        with col2:
            st.info("""
            **CARMA Features:**
            - Performance architecture
            - Memory consolidation
            - Synaptic tagging
            - Predictive coding
            """)
    
    with tab4:
        st.header("📊 Luna Analytics & Insights")
        
        # Get Luna system reference
        luna_system = st.session_state.aios_system.luna_system
        
        # Create sub-tabs for different analytics
        analytics_tab1, analytics_tab2, analytics_tab3, analytics_tab4 = st.tabs([
            "📈 Performance", "🧠 Memory", "🎭 Actions", "💰 Economy"
        ])
        
        with analytics_tab1:
            st.subheader("Performance Metrics")
            
            # Karma History Graph
            if not PLOTLY_AVAILABLE:
                st.warning("📦 Install plotly and pandas for visualizations: `pip install plotly pandas`")
            else:
                try:
                    # Get karma history from arbiter
                    current_karma = luna_system.arbiter_system.get_current_karma()
                    karma_history = [current_karma]  # Would track over time in production
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=karma_history,
                        mode='lines+markers',
                        name='Karma',
                        line=dict(color='#00ff00', width=2)
                    ))
                    fig.update_layout(
                        title="Luna's Karma (Life Force) Over Time",
                        yaxis_title="Karma",
                        xaxis_title="Interaction",
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.warning(f"Karma graph unavailable: {e}")
                
                # Trait Distribution from Chat History
                if st.session_state.chat_history:
                    trait_counts = {}
                    for msg in st.session_state.chat_history:
                        if msg.get("role") == "assistant" and msg.get("metadata"):
                            trait = msg["metadata"].get("dominant_trait", "unknown")
                            trait_counts[trait] = trait_counts.get(trait, 0) + 1
                    
                    if trait_counts:
                        df = pd.DataFrame(list(trait_counts.items()), columns=['Trait', 'Count'])
                        fig = px.pie(df, values='Count', names='Trait', 
                                    title='Conversation Trait Distribution',
                                    color_discrete_sequence=px.colors.qualitative.Set3)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Response Efficiency Timeline
                if st.session_state.chat_history:
                    response_lengths = []
                    for msg in st.session_state.chat_history:
                        if msg.get("role") == "assistant":
                            length = msg.get("metadata", {}).get("response_length", 0)
                            response_lengths.append(length)
                    
                    if response_lengths:
                        fig = go.Figure()
                        colors = ['green' if l <= 15 else 'yellow' if l <= 25 else 'red' for l in response_lengths]
                        fig.add_trace(go.Bar(
                            y=response_lengths,
                            marker_color=colors,
                            name='Response Length'
                        ))
                        fig.update_layout(
                            title="Response Length Over Conversation",
                            yaxis_title="Words",
                            xaxis_title="Response #",
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        with analytics_tab2:
            st.subheader("Memory & Learning")
            
            # Big Five Self-Knowledge Progress
            try:
                bigfive_answers = luna_system.personality_system.internal_reasoning.bigfive_answer_history
                st.metric("Self-Knowledge Questions Answered", f"{len(bigfive_answers)}/15")
                
                if bigfive_answers:
                    # Show trait distribution from self-reflection
                    # bigfive_answers is a dictionary, so we need to iterate over its values
                    trait_scores = {}
                    for answer_id, answer_data in bigfive_answers.items():
                        if isinstance(answer_data, dict):
                            # Check if it's the new format (with trait field)
                            if 'trait' in answer_data:
                                domain = answer_data.get('trait', 'unknown')
                                # Extract score from answer string if possible
                                answer_text = answer_data.get('answer', '')
                                score_match = re.search(r'Score: (\d+)/5', answer_text)
                                score = int(score_match.group(1)) if score_match else 3
                            else:
                                # Old format (with bigfive_question nested structure)
                                domain = answer_data.get('bigfive_question', {}).get('domain', 'unknown')
                                score = answer_data.get('answer_score', 3)
                            
                            if domain not in trait_scores:
                                trait_scores[domain] = []
                            trait_scores[domain].append(score)
                    
                    # Calculate averages
                    for trait in trait_scores:
                        avg = sum(trait_scores[trait]) / len(trait_scores[trait])
                        st.progress(avg / 5.0, text=f"{trait.capitalize()}: {avg:.1f}/5.0")
            except Exception as e:
                st.warning(f"Self-knowledge data unavailable: {e}")
            
            st.markdown("---")
            
            # Session Memory Viewer
            st.subheader("Current Session Memory")
            if st.session_state.chat_history:
                for i, msg in enumerate(st.session_state.chat_history[-10:], 1):
                    role_emoji = "👤" if msg["role"] == "user" else "🤖"
                    with st.expander(f"{role_emoji} Message {i}: {msg['content'][:50]}..."):
                        st.write(f"**Role:** {msg['role']}")
                        st.write(f"**Content:** {msg['content']}")
                        if msg.get("metadata"):
                            st.json(msg["metadata"])
            else:
                st.info("No messages yet - start a conversation!")
        
        with analytics_tab3:
            st.subheader("Action Usage Analysis")
            
            # Analyze action usage from responses
            if st.session_state.chat_history:
                action_freq = {}
                total_responses = 0
                action_only_count = 0
                
                for msg in st.session_state.chat_history:
                    if msg.get("role") == "assistant":
                        total_responses += 1
                        content = msg["content"]
                        actions = re.findall(r'\*([^*]+)\*', content)
                        
                        # Check if action-only
                        words_without_actions = re.sub(r'\*[^*]+\*', '', content).strip()
                        if not words_without_actions or re.match(r'^[\.\s…]+$', words_without_actions):
                            action_only_count += 1
                        
                        for action in actions:
                            action_key = action.split(',')[0].strip()  # Get first part of action
                            action_freq[action_key] = action_freq.get(action_key, 0) + 1
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Responses", total_responses)
                    st.metric("Action-Only Responses", action_only_count)
                    if total_responses > 0:
                        st.metric("Action-Only Rate", f"{action_only_count/total_responses*100:.1f}%")
                
                with col2:
                    st.subheader("Most Used Actions")
                    sorted_actions = sorted(action_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                    for action, count in sorted_actions:
                        st.write(f"**{action}**: {count} times")
            else:
                st.info("No conversation data yet")
        
        with analytics_tab4:
            st.subheader("Token Economy Dashboard")
            
            try:
                # Token pool status
                token_state = luna_system.existential_budget.state
                total_tokens = token_state.max_token_pool
                current_tokens = token_state.current_token_pool
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Token Pool", f"{current_tokens}/{total_tokens}")
                    progress = current_tokens / total_tokens if total_tokens > 0 else 0
                    st.progress(progress)
                
                with col2:
                    st.metric("Age", token_state.age)
                    karma_progress = (token_state.current_karma / token_state.karma_quota * 100) if token_state.karma_quota > 0 else 0
                    st.metric("Progress to Next Age", f"{karma_progress:.1f}%")
                
                with col3:
                    current_karma = luna_system.arbiter_system.get_current_karma()
                    st.metric("Current Karma", f"{current_karma:.1f}")
                    karma_status = luna_system.arbiter_system.get_karma_status()
                    st.write(f"**Status:** {karma_status}")
                
                # CFIA Status
                st.markdown("---")
                st.subheader("Intelligence Architecture (CFIA)")
                
                cfia_status = luna_system.arbiter_system.get_cfia_status()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("AIIQ/Generation", cfia_status['aiiq'])
                
                with col2:
                    st.metric("Total Files Processed", cfia_status['total_files'])
                
                with col3:
                    st.metric("Current Threshold", f"{cfia_status['current_threshold']:.1f} KB")
                
            except Exception as e:
                st.warning(f"Economy data unavailable: {e}")
    
    with tab5:
        st.header("❤️ System Health Check")
        
        if st.button("Run Health Check", type="primary"):
            with st.spinner("Running system health check..."):
                health_results = st.session_state.aios_system.run_system_health_check()
            
            st.success("Health check completed!")
            
            # Display health score
            health_score = health_results.get('health_score', 0)
            st.metric("Health Score", f"{health_score:.2f}/1.0")
            
            # Display detailed results
            st.json(health_results)
    
    with tab6:
        st.header("🧪 System Testing")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Run System Tests", type="primary"):
                with st.spinner("Running system tests..."):
                    test_results = st.session_state.aios_system.run_system_tests()
                
                st.success("System tests completed!")
                
                # Display test results
                success_rate = (test_results['passed'] / test_results['total'] * 100)
                st.metric("Success Rate", f"{success_rate:.1f}%")
                st.metric("Tests Passed", f"{test_results['passed']}/{test_results['total']}")
                
                # Display individual test results
                for test in test_results['tests']:
                    status_emoji = "" if test['status'] == 'passed' else ""
                    st.write(f"{status_emoji} {test['name']}: {test['message']}")
        
        with col2:
            st.info("""
            **Test Coverage:**
            - Import tests
            - System initialization
            - Basic functionality
            - Error handling
            """)
    
    with tab7:
        st.header("⚙️ System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("System Information")
            info = st.session_state.aios_system.get_system_info()
            st.json(info)
        
        with col2:
            st.subheader("Export Data")
            if st.button("Export System Data"):
                filename = st.session_state.aios_system.export_system_data()
                st.success(f"Data exported to: {filename}")
                st.download_button(
                    label="Download Export",
                    data=json.dumps(st.session_state.aios_system.get_system_status(), indent=2),
                    file_name=filename,
                    mime="application/json"
                )

else:
    # Welcome screen
    st.title(" Welcome to AIOS Clean")
    st.markdown("### AI Performance System")
    
    st.markdown("""
    **AIOS Clean** is a modular AI system featuring:
    
    - ** Luna AI** - Personality system with learning capabilities
    - ** CARMA** - Cached Aided Retrieval Mycelium Architecture
    - ** Enterprise** - API and business features
    - ** Support** - Utilities and operations
    
    Click the "Initialize System" button in the sidebar to get started!
    """)
    
    # System architecture diagram
    st.subheader("System Architecture")
    st.code("""
    main.py (Unified Entry Point)
    ├── carma_core/carma_core.py
    ├── luna_core/luna_core.py  
    ├── enterprise_core/enterprise_core.py
    └── support_core/support_core.py
    """, language="text")

# Footer
st.markdown("---")
st.markdown("**AIOS Clean v1.0.0** - AI Performance System")
