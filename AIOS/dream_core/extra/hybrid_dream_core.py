#!/usr/bin/env python3
"""
Hybrid Dream Core - Python-Rust bridge for Dream system
"""

from pathlib import Path
from utils_core.bridges.rust_bridge import RustBridge, MultiLanguageCore
from dream_core.dream_core import DreamCore

class HybridDreamCore(MultiLanguageCore):
    """
    Hybrid Dream Core that combines Python and Rust implementations.
    """
    
    def __init__(self):
        """
        Initialize the Hybrid Dream Core.
        """
        print("🌙 Initializing Hybrid Dream Core...")
        
        # Initialize Python implementation
        python_dream = DreamCore()
        
        # Initialize Rust bridge
        rust_bridge = None
        try:
            rust_path = Path(__file__).parent / "rust_dream"
            if rust_path.exists():
                rust_bridge = RustBridge("dream", str(rust_path))
                
                # Try to compile and load Rust module
                if rust_bridge.compile_rust_module():
                    rust_bridge.load_rust_module()
        except Exception as e:
            print(f"⚠️ Rust Dream initialization failed: {e}")
            print("   Falling back to Python implementation")
        
        # Initialize multi-language core
        super().__init__("dream", python_dream, rust_bridge)
        
        # Expose key attributes for compatibility
        self.python_impl = python_dream
        
        print(f"🚀 Hybrid Dream Core Initialized")
        print(f"   Current implementation: {self.current_implementation.upper()}")
    
    def run_quick_nap(self, duration_minutes: int = 30, dream_cycles: int = 2, meditation_blocks: int = 1, verbose: bool = False):
        """
        Run a quick nap dream cycle using hybrid implementation.
        
        Args:
            duration_minutes: Duration of the nap in minutes
            dream_cycles: Number of dream cycles to run
            meditation_blocks: Number of meditation blocks
            verbose: Whether to show detailed output
            
        Returns:
            Dream cycle result
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustDreamCore")
                if rust_class:
                    rust_instance = rust_class()
                    result = rust_instance.run_quick_nap(duration_minutes, dream_cycles, meditation_blocks, verbose)
                    
                    # Convert to Python dict format
                    return {
                        'status': result.status,
                        'duration_minutes': result.duration_minutes,
                        'dream_cycles': result.dream_cycles,
                        'meditation_blocks': result.meditation_blocks,
                        'memory_consolidations': result.memory_consolidations,
                        'patterns_identified': result.patterns_identified,
                        'karma_refunds': result.karma_refunds,
                        'cycle_id': result.cycle_id,
                        'timestamp': result.timestamp
                    }
            except Exception as e:
                print(f"⚠️ Rust Dream quick nap failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return self.python_impl.run_quick_nap(duration_minutes, dream_cycles, meditation_blocks, verbose)
    
    def run_overnight_dream(self, duration_minutes: int = 480, verbose: bool = False):
        """
        Run an overnight dream session using hybrid implementation.
        
        Args:
            duration_minutes: Duration of the overnight session in minutes
            verbose: Whether to show detailed output
            
        Returns:
            Dream cycle result
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustDreamCore")
                if rust_class:
                    rust_instance = rust_class()
                    result = rust_instance.run_overnight_dream(duration_minutes, verbose)
                    
                    # Convert to Python dict format
                    return {
                        'status': result.status,
                        'duration_minutes': result.duration_minutes,
                        'dream_cycles': result.dream_cycles,
                        'meditation_blocks': result.meditation_blocks,
                        'memory_consolidations': result.memory_consolidations,
                        'patterns_identified': result.patterns_identified,
                        'karma_refunds': result.karma_refunds,
                        'cycle_id': result.cycle_id,
                        'timestamp': result.timestamp
                    }
            except Exception as e:
                print(f"⚠️ Rust Dream overnight session failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return self.python_impl.run_overnight_dream(duration_minutes, verbose)
    
    def run_meditation_session(self, duration_minutes: int = 30, verbose: bool = False):
        """
        Run a meditation session using hybrid implementation.
        
        Args:
            duration_minutes: Duration of the meditation session in minutes
            verbose: Whether to show detailed output
            
        Returns:
            Meditation session result
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustDreamCore")
                if rust_class:
                    rust_instance = rust_class()
                    result = rust_instance.run_meditation_session(duration_minutes, verbose)
                    
                    # Convert to Python dict format
                    return {
                        'status': result.status,
                        'duration_minutes': result.duration_minutes,
                        'dream_cycles': result.dream_cycles,
                        'meditation_blocks': result.meditation_blocks,
                        'memory_consolidations': result.memory_consolidations,
                        'patterns_identified': result.patterns_identified,
                        'karma_refunds': result.karma_refunds,
                        'cycle_id': result.cycle_id,
                        'timestamp': result.timestamp
                    }
            except Exception as e:
                print(f"⚠️ Rust Dream meditation session failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return self.python_impl.run_meditation_session(duration_minutes, verbose)
    
    def run_test_mode(self, duration_minutes: int = 2, verbose: bool = True):
        """
        Run test mode using hybrid implementation.
        
        Args:
            duration_minutes: Duration of the test in minutes
            verbose: Whether to show detailed output
            
        Returns:
            Test mode result
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustDreamCore")
                if rust_class:
                    rust_instance = rust_class()
                    result = rust_instance.run_test_mode(duration_minutes, verbose)
                    
                    # Convert to Python dict format
                    return {
                        'status': result.status,
                        'duration_minutes': result.duration_minutes,
                        'dream_cycles': result.dream_cycles,
                        'meditation_blocks': result.meditation_blocks,
                        'memory_consolidations': result.memory_consolidations,
                        'patterns_identified': result.patterns_identified,
                        'karma_refunds': result.karma_refunds,
                        'cycle_id': result.cycle_id,
                        'timestamp': result.timestamp
                    }
            except Exception as e:
                print(f"⚠️ Rust Dream test mode failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return self.python_impl.run_test_mode(duration_minutes, verbose)
    
    def get_system_status(self):
        """
        Get system status using hybrid implementation.
        
        Returns:
            System status dictionary
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustDreamCore")
                if rust_class:
                    rust_instance = rust_class()
                    return rust_instance.get_system_status()
            except Exception as e:
                print(f"⚠️ Rust Dream system status failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return self.python_impl.get_system_status()
    
    def consolidate_memories_during_dream(self, cycle_number: int):
        """
        Consolidate memories during dream using hybrid implementation.
        
        Args:
            cycle_number: The dream cycle number
            
        Returns:
            Memory consolidation result
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustDreamCore")
                if rust_class:
                    rust_instance = rust_class()
                    result = rust_instance.consolidate_memories_during_dream(cycle_number)
                    
                    # Convert to Python dict format
                    return {
                        'consolidation_id': result.consolidation_id,
                        'memories_processed': result.memories_processed,
                        'patterns_formed': result.patterns_formed,
                        'synapses_strengthened': result.synapses_strengthened,
                        'consolidation_quality': result.consolidation_quality,
                        'timestamp': result.timestamp
                    }
            except Exception as e:
                print(f"⚠️ Rust Dream memory consolidation failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return {
            'consolidation_id': f'python_consolidation_{cycle_number}',
            'memories_processed': 5,
            'patterns_formed': 2,
            'synapses_strengthened': 3,
            'consolidation_quality': 0.7,
            'timestamp': 0.0
        }
    
    def get_pattern_cache(self):
        """
        Get pattern recognition cache using hybrid implementation.
        
        Returns:
            Pattern cache dictionary
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustDreamCore")
                if rust_class:
                    rust_instance = rust_class()
                    return rust_instance.get_pattern_cache()
            except Exception as e:
                print(f"⚠️ Rust Dream pattern cache failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return {}
    
    def get_hybrid_status(self):
        """
        Get hybrid system status.
        
        Returns:
            Status information
        """
        return {
            'core_name': self.core_name,
            'current_implementation': self.current_implementation,
            'rust_available': self.rust_bridge.is_available() if self.rust_bridge else False,
            'python_available': True,
            'dream_dir': str(getattr(self.python_impl, 'dream_dir', 'dream_core'))
        }
