#!/usr/bin/env python3
"""
Hybrid Luna Core - Python-Rust bridge for Luna personality system
"""

from pathlib import Path
from utils_core.bridges.rust_bridge import RustBridge, MultiLanguageCore
from .core.luna_core import LunaSystem

class HybridLunaCore(MultiLanguageCore):
    """
    Hybrid Luna Core that combines Python and Rust implementations.
    """
    
    def __init__(self, custom_params=None, custom_config=None):
        """
        Initialize the Hybrid Luna Core.
        
        Args:
            custom_params: Custom parameters for Luna system
            custom_config: Custom configuration for Luna system
        """
        print("🌙 Initializing Hybrid Luna Core...")
        
        # Initialize Python implementation
        python_luna = LunaSystem(custom_params=custom_params, custom_config=custom_config)
        
        # Wire shared DriftMonitor + ExperienceState for runtime plumbing
        # This overrides the default one created in response_generator.__init__
        try:
            from consciousness_core.drift_monitor import DriftMonitor
            from luna_core.core.luna_lingua_calc import ExperienceState
            
            # Create shared session objects
            if not hasattr(self.__class__, "_shared_drift"):
                self.__class__._shared_drift = DriftMonitor()
                self.__class__._shared_exp = ExperienceState()
                print("   [HYBRID] Created shared DriftMonitor + ExperienceState")
            
            # Wire into response generator (replaces default instance)
            python_luna.response_generator.drift_monitor = self.__class__._shared_drift
            python_luna.response_generator.exp_state = self.__class__._shared_exp
            print("   [HYBRID] Wired shared session objects to response_generator")
        except Exception as e:
            print(f"   Warning: Could not wire drift/exp_state: {e}")
            import traceback
            traceback.print_exc()
        
        # No Rust bridge for Luna (Python only - no Rust module exists)
        rust_bridge = None
        # try:
        #     rust_path = Path(__file__).parent / "rust_luna"
        #     if rust_path.exists():
        #         print(f"🔍 DEBUG: Creating RustBridge for Luna at {rust_path}")
        #         rust_bridge = RustBridge("luna", str(rust_path))
        #         print(f"🔍 DEBUG: RustBridge created, is_available: {rust_bridge.is_available()}")
        #         
        #         # Try to compile and load Rust module
        #         print(f"🔍 DEBUG: Attempting to compile Rust module...")
        #         if rust_bridge.compile_rust_module():
        #             print(f"🔍 DEBUG: Compilation successful, loading module...")
        #             rust_bridge.load_rust_module()
        #             print(f"🔍 DEBUG: Module loaded, final is_available: {rust_bridge.is_available()}")
        #         else:
        #             print(f"🔍 DEBUG: Compilation failed")
        #     else:
        #         print(f"🔍 DEBUG: Rust path does not exist: {rust_path}")
        # except Exception as e:
        #     print(f"⚠️ Rust Luna initialization failed: {e}")
        #     print("   Falling back to Python implementation")
        #     import traceback
        #     traceback.print_exc()
        
        # Initialize multi-language core
        super().__init__("luna", python_luna, rust_bridge)
        
        # Expose key attributes for compatibility
        self.python_impl = python_luna
        # Sync with Python implementation's interaction count
        self.total_interactions = getattr(python_luna, 'total_interactions', 0)
        self.total_responses = getattr(python_luna, 'total_responses', 0)
        
        print(f"🚀 Hybrid Luna Core Initialized")
        print(f"   Current implementation: {self.current_implementation.upper()}")
    
    def generate_response(self, question: str, trait: str = "general", carma_result: dict = None, session_memory: list = None) -> str:
        """
        Generate Luna's response using hybrid implementation.
        
        Args:
            question: The question to respond to
            trait: Personality trait to use
            carma_result: CARMA system result
            session_memory: Session memory context
            
        Returns:
            Luna's response string
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustLunaCore")
                if rust_class:
                    rust_instance = rust_class()
                    karma_score = 0.5  # Default karma score
                    if carma_result:
                        karma_score = carma_result.get('karma_score', 0.5)
                    
                    response = rust_instance.generate_response(question, trait, karma_score)
                    return response.response
            except Exception as e:
                print(f"⚠️ Rust Luna response generation failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        try:
            print(f"   DEBUG: Calling python_impl.process_question with question: {type(question)}, trait: {type(trait)}")
            response, metadata = self.python_impl.process_question(question, trait, session_memory)
            print(f"   DEBUG: Got response: {type(response)}, metadata: {type(metadata)}")
            return response
        except Exception as e:
            print(f"⚠️ Python Luna response generation failed: {e}")
            return "I'm sorry, I encountered an error processing your message."
    
    def run_learning_session(self, questions: list) -> dict:
        """
        Run a learning session using hybrid implementation.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Learning session results
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustLunaCore")
                if rust_class:
                    rust_instance = rust_class()
                    
                    # Extract questions and traits
                    question_texts = [q.get('question', '') for q in questions]
                    traits = [q.get('trait', 'general') for q in questions]
                    
                    result = rust_instance.run_learning_session(question_texts, traits)
                    
                    # Convert to Python dict format
                    return {
                        'total_questions': result.total_questions,
                        'total_responses': result.total_responses,
                        'average_karma': result.average_karma,
                        'session_duration': result.session_duration,
                        'responses': [{
                            'response': r.response,
                            'trait': r.personality_trait,
                            'karma_score': r.karma_score,
                            'timestamp': r.timestamp
                        } for r in result.responses]
                    }
            except Exception as e:
                print(f"⚠️ Rust Luna learning session failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return self.python_impl.run_learning_session(questions)
    
    def get_personality_traits(self) -> dict:
        """
        Get current personality trait scores.
        
        Returns:
            Dictionary of trait scores
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustLunaCore")
                if rust_class:
                    rust_instance = rust_class()
                    return rust_instance.get_personality_traits()
            except Exception as e:
                print(f"⚠️ Rust Luna personality traits failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        if hasattr(self.python_impl, 'get_personality_traits'):
            return self.python_impl.get_personality_traits()
        return {}
    
    def get_stats(self) -> dict:
        """
        Get Luna system statistics.
        
        Returns:
            Dictionary of system stats
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustLunaCore")
                if rust_class:
                    rust_instance = rust_class()
                    return rust_instance.get_stats()
            except Exception as e:
                print(f"⚠️ Rust Luna stats failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return {
            'total_interactions': getattr(self.python_impl, 'total_interactions', 0),
            'total_responses': getattr(self.python_impl, 'total_responses', 0),
            'implementation': self.current_implementation
        }
    
    def calculate_karma_score(self, question: str, trait: str = "general") -> float:
        """
        Calculate karma score for a question using hybrid implementation.
        
        Args:
            question: The question to analyze
            trait: Personality trait
            
        Returns:
            Karma score (0.0 to 1.0)
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustLunaCore")
                if rust_class:
                    rust_instance = rust_class()
                    return rust_instance.calculate_karma_score(question, trait)
            except Exception as e:
                print(f"⚠️ Rust Luna karma calculation failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return 0.5  # Default karma score
    
    def analyze_emotional_tone(self, text: str) -> str:
        """
        Analyze emotional tone of text using hybrid implementation.
        
        Args:
            text: Text to analyze
            
        Returns:
            Emotional tone ("positive", "negative", "neutral")
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustLunaCore")
                if rust_class:
                    rust_instance = rust_class()
                    return rust_instance.analyze_emotional_tone(text)
            except Exception as e:
                print(f"⚠️ Rust Luna emotional analysis failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return "neutral"  # Default emotional tone
    
    def classify_question_type(self, question: str) -> str:
        """
        Classify question type using hybrid implementation.
        
        Args:
            question: Question to classify
            
        Returns:
            Question type classification
        """
        if self.current_implementation == "rust" and self.rust_bridge and self.rust_bridge.is_available():
            try:
                # Use Rust implementation
                rust_class = self.rust_bridge.get_rust_class("RustLunaCore")
                if rust_class:
                    rust_instance = rust_class()
                    return rust_instance.classify_question_type(question)
            except Exception as e:
                print(f"⚠️ Rust Luna question classification failed: {e}")
                print("   Falling back to Python implementation")
        
        # Fall back to Python implementation
        return "simple"  # Default question type
    
    def get_system_stats(self) -> dict:
        """
        Get system statistics (alias for get_stats for compatibility).
        
        Returns:
            Dictionary of system stats
        """
        return self.get_stats()
    
    def get_hybrid_status(self) -> dict:
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
            'custom_params': getattr(self, 'custom_params', None),
            'total_interactions': self.total_interactions,
            'total_responses': self.total_responses
        }
