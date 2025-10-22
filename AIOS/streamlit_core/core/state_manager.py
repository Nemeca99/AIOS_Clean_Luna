#!/usr/bin/env python3
"""
State Manager for Streamlit Core
=================================

Handles session state and persistent state management for the AIOS Streamlit UI.
Provides memory leak protection and efficient state storage/retrieval.

Key Features:
- Session state management via Streamlit
- Persistent state storage via pickle files
- Memory leak protection (size limits, validation)
- Backup and recovery for state files

Author: AIOS Development Team
Version: 1.0.0
"""

import sys
import pickle
import streamlit as st
from pathlib import Path
from typing import Dict, Any


class StateManager:
    """
    Manages session and persistent state for the Streamlit application.
    Handles state storage, retrieval, and memory protection.
    """
    
    def __init__(self, state_file: Path = None):
        """
        Initialize the state manager.
        
        Args:
            state_file: Path to persistent state file. Defaults to streamlit_state.pkl
        """
        if state_file is None:
            state_file = Path("streamlit_state.pkl")
        
        self.state_file = state_file
        print("📦 State Manager Initialized")
        print(f"   State File: {self.state_file}")
    
    def load_persistent_state(self) -> Dict[str, Any]:
        """Load persistent state from file with memory leak protection."""
        if not self.state_file.exists():
            return {}
        
        try:
            # Check file size to prevent loading huge files
            file_size = self.state_file.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                print(f"⚠️ State file too large ({file_size} bytes), clearing it")
                self.state_file.unlink()
                return {}

            with open(self.state_file, 'rb') as f:
                state = pickle.load(f)

            # Validate state is a dictionary and not too large
            if not isinstance(state, dict):
                print("⚠️ Invalid state format, clearing")
                self.state_file.unlink()
                return {}

            # Limit number of keys to prevent memory bloat
            if len(state) > 1000:
                print(f"⚠️ Too many state keys ({len(state)}), clearing old state")
                self.state_file.unlink()
                return {}

            return state

        except (pickle.PickleError, EOFError, OSError) as e:
            print(f"⚠️ Error loading state: {e}, clearing corrupted file")
            try:
                self.state_file.unlink()
            except Exception as e:
                pass
            return {}
    
    def save_persistent_state(self, state: Dict[str, Any]):
        """Save persistent state to file with memory leak protection."""
        try:
            # Validate state before saving
            if not isinstance(state, dict):
                print("⚠️ State must be a dictionary")
                return

            # Limit state size
            if len(state) > 1000:
                print("⚠️ Too many state keys, not saving")
                return

            # Create backup before overwriting
            if self.state_file.exists():
                backup_file = self.state_file.with_suffix('.bak')
                try:
                    self.state_file.rename(backup_file)
                except Exception as e:
                    pass

            # Write new state
            with open(self.state_file, 'wb') as f:
                pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Remove backup if successful
            backup_file = self.state_file.with_suffix('.bak')
            if backup_file.exists():
                backup_file.unlink()

        except Exception as e:
            print(f"⚠️ Error saving state: {e}")
            # Restore backup if save failed
            backup_file = self.state_file.with_suffix('.bak')
            if backup_file.exists():
                try:
                    backup_file.rename(self.state_file)
                except Exception as e:
                    pass
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value, with persistent fallback and memory protection."""
        # Limit key length to prevent memory issues
        if not isinstance(key, str) or len(key) > 100:
            print(f"⚠️ Invalid state key: {key}")
            return default

        if key not in st.session_state:
            persistent_state = self.load_persistent_state()
            if key in persistent_state:
                value = persistent_state[key]
                # Validate value size
                try:
                    value_size = sys.getsizeof(value)
                    if value_size > 1024 * 1024:  # 1MB limit per value
                        print(f"⚠️ State value too large ({value_size} bytes), using default")
                        st.session_state[key] = default
                        return default
                except Exception as e:
                    pass
                st.session_state[key] = value
            else:
                st.session_state[key] = default
        return st.session_state[key]
    
    def set_state(self, key: str, value: Any, persistent: bool = True):
        """Set a state value with memory leak protection."""
        # Validate key
        if not isinstance(key, str) or len(key) > 100:
            print(f"⚠️ Invalid state key: {key}")
            return

        # Validate value size
        try:
            value_size = sys.getsizeof(value)
            if value_size > 1024 * 1024:  # 1MB limit per value
                print(f"⚠️ State value too large ({value_size} bytes), not setting")
                return
        except Exception as e:
            pass

        st.session_state[key] = value
        if persistent:
            persistent_state = self.load_persistent_state()
            persistent_state[key] = value
            self.save_persistent_state(persistent_state)
    
    def clear_persistent_state(self):
        """Clear all persistent state with cleanup."""
        try:
            # Clear session state
            st.session_state.clear()

            # Remove state file and backup
            if self.state_file.exists():
                self.state_file.unlink()
            backup_file = self.state_file.with_suffix('.bak')
            if backup_file.exists():
                backup_file.unlink()

        except Exception as e:
            print(f"⚠️ Error clearing state: {e}")
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get information about current state."""
        persistent_state = self.load_persistent_state()
        state_size = 0
        
        if persistent_state:
            state_size = sum(sys.getsizeof(str(v)) for v in persistent_state.values()) / 1024
        
        return {
            'num_keys': len(persistent_state),
            'size_kb': state_size,
            'file_exists': self.state_file.exists()
        }

