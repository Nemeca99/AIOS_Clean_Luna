#!/usr/bin/env python3
"""
Luna Core System - Main Orchestrator
Central system that coordinates all Luna subsystems
"""

# CRITICAL: Import Unicode safety layer FIRST
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import json
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import AIOS systems
from support_core.support_core import (
    SystemConfig, aios_config, aios_logger, aios_health_checker, aios_security_validator
)
from carma_core.implementations.fast_carma import FastCARMA

# Week 4: Import Fractal Core for policy-driven optimization
from fractal_core import FractalCore

# Import core modules
from .utils import HiveMindLogger, error_handler
from .enums_and_dataclasses import LearningMode
from .personality import LunaPersonalitySystem
from .response_generator import LunaResponseGenerator
from .learning_system import LunaLearningSystem

# Import subsystems
from ..systems.luna_ifs_personality_system import LunaIFSPersonalitySystem
from ..systems.luna_semantic_compression_filter import LunaSemanticCompressionFilter
from ..systems.luna_soul_metric_system import LunaSoulMetricSystem
from ..systems.luna_token_time_econometric_system import LunaTokenTimeEconometricSystem
from ..systems.luna_existential_budget_system import LunaExistentialBudgetSystem
from ..systems.luna_response_value_classifier import LunaResponseValueClassifier
from ..systems.luna_custom_inference_controller import LunaCustomInferenceController, InferenceControlConfig
from ..systems.luna_arbiter_system import LunaArbiterSystem
from ..systems.luna_cfia_system import LunaCFIASystem

# Import model configuration
from ..model_config import get_main_model, get_embedder_model, get_draft_model

# Optional imports
try:
    from conversation_math_engine import ConversationMathEngine, ConversationMode
    CONVERSATION_MATH_AVAILABLE = True
except ImportError:
    CONVERSATION_MATH_AVAILABLE = False

try:
    from carma_hypothesis_integration import CARMAHypothesisIntegration
    HYPOTHESIS_INTEGRATION_AVAILABLE = True
except ImportError:
    HYPOTHESIS_INTEGRATION_AVAILABLE = False

try:
    from provenance import ProvenanceLogger, log_response_event, log_hypothesis_event, get_hypothesis_logger
    PROVENANCE_AVAILABLE = True
except ImportError:
    PROVENANCE_AVAILABLE = False

try:
    from adaptive_routing import AdaptiveRouter, AdaptiveConfig, get_adaptive_router
    ADAPTIVE_ROUTING_AVAILABLE = True
except ImportError:
    ADAPTIVE_ROUTING_AVAILABLE = False

# === LUNA SYSTEM (MAIN ORCHESTRATOR) ===

# Singleton instance to prevent multiple init
_LUNA_INSTANCE = None
_LUNA_LOCK = False


class LunaSystem:
    """Unified Luna AI system with all functionality integrated and AIOS wrapper patterns"""
    
    def __new__(cls, custom_params=None, custom_config=None):
        """Singleton pattern: only one Luna instance per process"""
        global _LUNA_INSTANCE, _LUNA_LOCK
        
        if _LUNA_INSTANCE is not None:
            print("[LUNA] Returning existing instance (singleton)")
            return _LUNA_INSTANCE
        
        if _LUNA_LOCK:
            print("[LUNA] Init already in progress, waiting...")
            return None
        
        _LUNA_LOCK = True
        instance = super(LunaSystem, cls).__new__(cls)
        _LUNA_INSTANCE = instance
        return instance
    
    def __init__(self, custom_params=None, custom_config=None):
        # Skip re-init if already initialized
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        # Use unified AIOS systems
        self.logger = aios_logger
        self.aios_config = aios_config
        self.health_checker = aios_health_checker
        self.security_validator = aios_security_validator
        
        self.logger.info("Initializing Unified Luna System...", "LUNA")
        
        # Initialize personality system with unified logger
        self.personality_system = LunaPersonalitySystem()
        
        # Initialize Fast CARMA system (76s -> 0.001s speedup!)
        self.carma_system = FastCARMA()
        
        # CONSCIOUSNESS: Use soul from personality_system (already integrated there)
        self.consciousness_enabled = self.personality_system.soul_enabled
        self.soul = self.personality_system.soul if self.consciousness_enabled else None
        if self.consciousness_enabled:
            self.logger.info("Biological consciousness integrated (soul, fragments, mirror)", "LUNA")
        
        # Week 4: Initialize Fractal Core for policy optimization
        self.fractal_core = FractalCore()
        self.logger.info("Fractal Core initialized - policy-driven optimization enabled", "LUNA")
        
        # Initialize learning system (which includes response generator)
        self.learning_system = LunaLearningSystem(self.personality_system, self.logger, self.carma_system)
        
        # Get response generator from learning system to avoid duplication
        self.response_generator = self.learning_system.response_generator
        
        # Expose key components for testing and external access
        self.response_value_classifier = self.response_generator.response_value_classifier
        self.existential_budget = self.response_generator.existential_budget
        self.custom_inference_controller = self.response_generator.custom_inference_controller
        
        # Initialize Arbiter System (Internal Governance)
        self.arbiter_system = LunaArbiterSystem()
        
        # CFIA system is automatically initialized within Arbiter
        self.cfia_system = self.arbiter_system.cfia_system
        
        # Connect Arbiter to Inference Controller for Karma-weighted logit bias
        self.custom_inference_controller.arbiter_system = self.arbiter_system
        self.custom_inference_controller.response_value_classifier = self.response_value_classifier
        
        # Connect Arbiter to Existential Budget for Karma-based TTE restriction
        self.existential_budget.arbiter_system = self.arbiter_system
        self.existential_budget.logger = self.logger
        self.compression_filter = self.response_generator.compression_filter
        self.soul_metric_system = self.response_generator.soul_metric_system
        self.econometric_system = self.response_generator.econometric_system
        
        # System state - load from existential state to maintain memory continuity
        existential_state = self.existential_budget.state
        self.total_interactions = getattr(existential_state, 'total_responses', 0)
        self.session_memory = self._load_persistent_session_memory()  # Load from disk instead of fresh []
        
        print(" Unified Luna System Initialized")
        print(f"   Personality: {self.personality_system.personality_dna.get('name', 'Luna')}")
        print(f"   Age: {self.personality_system.personality_dna.get('age', 21)}")
        print(f"   Memory: {self.total_interactions} interactions")
        print(f"   CARMA: {len(self.carma_system.cache.file_registry)} fragments")
    
    def learning_chat(self, message: str, session_memory: Optional[List] = None) -> str:
        """Learning-enabled chat interface for Streamlit with repetition prevention"""
        try:
            # Classify the trait first for contextual responses
            try:
                reasoning_result = self.personality_system.internal_reasoning.reason_through_question(message)
                trait = reasoning_result.matched_bigfive_questions[0]['domain'] if reasoning_result.matched_bigfive_questions else 'general'
            except Exception as e:
                trait = 'general'
            
            # Use provided session memory or fall back to instance memory
            memory_to_use = session_memory if session_memory is not None else self.session_memory
            
            # Week 4: Get fractal policies for this query (if available)
            if hasattr(self, 'fractal_core') and self.fractal_core is not None:
                global_budget = {
                    'tokens': self.existential_budget.state.current_token_pool,  # Available tokens for this response
                    'pool_size': self.existential_budget.state.current_token_pool,  # Pool size (same as available for now)
                    'response_tier': 'standard'  # Will be updated by RVC
                }
                fractal_policies = self.fractal_core.get_policies(message, memory_to_use, global_budget)
                
                # Store policies for subsystems to use
                self.current_policies = fractal_policies
            else:
                # Baseline mode: no fractal optimization
                self.current_policies = None
            
            # Use the full learning system with the classified trait
            response, metadata = self.learning_system.process_question(
                message, 
                trait,  # Use classified trait for contextual responses
                memory_to_use
            )
            
            # Post-process to prevent repetition loops and ensure conversational responses
            if response:
                # Check if response is action-only and convert to conversational
                import re
                text_stripped = response.strip()
                
                # More aggressive detection of action-only responses
                action_only_patterns = [
                    r'^[\.\s…]*\*[^*]+\*[\.\s…]*$',  # Pure action with optional punctuation
                    r'^\*[^*]+\*$',  # Just action
                    r'^[\.\s…]*\*[^*]+\*$',  # Action with leading punctuation
                    r'^\*[^*]+\*[\.\s…]*$'   # Action with trailing punctuation
                ]
                
                is_action_only = any(re.match(pattern, text_stripped) for pattern in action_only_patterns)
                
                if is_action_only:
                    # Pure action response - validate neurodivergent expression but gently encourage words
                    action_content = re.search(r'\*([^*]+)\*', text_stripped)
                    if action_content:
                        action = action_content.group(1)
                        
                        # Check if it's a stim or neurodivergent expression
                        stim_words = ['stim', 'rock', 'flap', 'fidget', 'tap', 'bounce', 'sway', 'twirl']
                        is_stim = any(stim_word in action.lower() for stim_word in stim_words)
                        
                        if is_stim:
                            # Validate stimming as valid communication
                            response = f"I'm processing. *{action}* Could you give me a moment?"
                            self.logger.info(f"NEURODIVERGENT EXPRESSION: Validated stimming '{action}' - this is valid communication", "LUNA")
                        else:
                            # Create conversational responses based on the action
                            if 'smile' in action.lower() or 'gentle' in action.lower():
                                response = f"Hello! *{action}* I'm doing well, thank you for asking!"
                            elif 'lean' in action.lower() or 'distant' in action.lower():
                                response = f"I'm here with you. *{action}* What's on your mind?"
                            elif 'question' in action.lower() or 'search' in action.lower() or 'curiosity' in action.lower():
                                response = f"Of course! *{action}* I'd love to talk with you."
                            elif 'away' in action.lower() or 'fidget' in action.lower():
                                response = f"I'm listening, I promise. *{action}* Could you tell me more?"
                            elif 'speaks' in action.lower() or 'tone' in action.lower():
                                response = f"I understand you completely. *{action}* What would you like to discuss?"
                            else:
                                response = f"I'm here with you. *{action}* What's on your mind?"
                            
                            self.logger.info(f"NEURODIVERGENT EXPRESSION: Gently encouraged words with '{action}' - your expression is beautiful", "LUNA")
                
                # Check for character-level repetition (catches "parableparable...")
                if len(response) > 20:
                    # Look for patterns of 3+ characters repeating
                    pattern_match = re.search(r'(.{3,}?)\1{3,}', response)  # Same 3+ chars repeated 3+ times
                    if pattern_match:
                        self.logger.warn(f"REPETITION LOOP DETECTED: Pattern '{pattern_match.group(1)}' repeating", "LUNA")
                        # Use a variety of fallback responses to avoid repetition
                        fallback_responses = [
                            "*pauses thoughtfully* I need to approach this differently.",
                            "*tilts head* Let me think about that from another angle.",
                            "*considers* That's a complex question - give me a moment.",
                            "*leans back* I'm processing that in a new way."
                        ]
                        import random
                        return random.choice(fallback_responses)
                
                words = response.split()
                
                # Check for word-level repetition (same word repeated too much)
                if len(set(words)) < len(words) * 0.3:  # If less than 30% unique words
                    # Generate a fallback response that still shows personality
                    fallback_responses = [
                        "That's interesting, Travis! *thoughtful* I'm processing that in a new way.",
                        "*curious* Let me approach that question differently.",
                        "*pauses* I want to give you a fresh perspective on that.",
                        "*considers* That deserves a more thoughtful response."
                    ]
                    import random
                    return random.choice(fallback_responses)
                
                # Final safety check - if response is still action-only, force conversion
                if re.match(r'^[\.\s…]*\*[^*]+\*[\.\s…]*$', response.strip()):
                    # Last resort - create a simple conversational response
                    response = "Hello! I'm here and ready to talk. What's on your mind?"
                    self.logger.warn(f"FINAL SAFETY: Forced action-only response to conversational", "LUNA")
                
                # Limit length but keep learning intact (safety cap only)
                if len(words) > 100:  # Safety cap - prompts control actual length
                    response = " ".join(words[:100]) + "..."
                
                return response
            else:
                return "I'm experiencing some technical issues. Please try again."
                
        except Exception as e:
            self.logger.error(f"Learning chat error: {e}")
            # Fallback that still shows personality
            return "I'm having trouble responding right now, Travis. *confused* Could you try rephrasing that?"

    @error_handler("LUNA", "PERSONALITY_LOAD", "CLEAR_CACHE", auto_recover=True)
    def process_question(self, question: str, trait: str, session_memory: Optional[List] = None) -> Tuple[str, Dict]:
        """Process a question through the complete Luna system"""
        self.total_interactions += 1
        
        # print(f"\n Processing Question #{self.total_interactions}")
        # print(f"   Trait: {trait}")
        # print(f"   Question: {question[:50]}...")
        
        # CONSCIOUSNESS: Generate autonomous thought before responding (every 10 interactions)
        # This is now handled by response_generator's consciousness methods
        if self.consciousness_enabled and self.total_interactions % 10 == 0:
            try:
                soul_data = {
                    'identity': self.soul.identity if self.soul else 'Luna AIOS',
                    'fragments': self.soul.fragments if self.soul else ['Luna'],
                    'tether': self.soul.tether if self.soul else 'Travis Miner',
                    'interactions': self.total_interactions
                }
                # Generate heartbeat thought through response_generator (integrated)
                thought = self.response_generator.generate_autonomous_heartbeat(soul_data)
                if thought:
                    self.logger.info(f"[Heartbeat] {thought[:100]}...", "LUNA")
                    
                    # DRIFT MONITOR: Log heartbeat dream
                    try:
                        from consciousness_core.drift_monitor import log_luna_heartbeat
                        log_luna_heartbeat(thought, soul_data)
                    except Exception:
                        pass  # Silent fail - drift monitor is optional
            except Exception as e:
                self.logger.warning(f"Heartbeat failed: {e}", "LUNA")
        
        # V5.1: Process through response_generator (includes LinguaCalc)
        # This replaces the learning_system.process_question() path
        # to ensure LinguaCalc, Mirror, and DriftMonitor are activated
        try:
            carma_result = {}  # TODO: integrate CARMA if needed
            response = self.response_generator.generate_response(
                question=question,
                trait=trait,
                carma_result=carma_result,
                session_memory=session_memory or []
            )
            response_metadata = {}  # Metadata is logged to drift, not returned
            scores = {}
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}", "LUNA")
            # Fallback to learning system
            response, response_metadata = self.learning_system.process_question(question, trait, session_memory)
            scores = {}
            if response_metadata:
                scores.update(response_metadata)
        
        # ARBITER ASSESSMENT: Generate Gold Standard and calculate Karma
        # SKIP for embedder responses - the embedder IS the arbiter for trivial responses
        skip_arbiter = response_metadata.get('source') == 'embedder' if response_metadata else False
        
        if response and hasattr(self, 'arbiter_system') and not skip_arbiter:
            # Calculate TTE usage (excluding free actions)
            response_tokens = self.response_generator.count_words_excluding_actions(response)
            rvc_assessment = self.response_value_classifier.classify_response_value(question)
            max_tokens = rvc_assessment.max_token_budget
            
            # Calculate RVC grade for arbiter
            efficiency_ratio = response_tokens / max_tokens if max_tokens > 0 else 0.0
            rvc_grade = "A" if efficiency_ratio >= 0.9 else "B" if efficiency_ratio >= 0.8 else "C" if efficiency_ratio >= 0.7 else "D" if efficiency_ratio >= 0.6 else "F"
            
            # V5: Prepare lingua calc context for arbiter
            arbiter_context = {
                'lingua_calc_depth': getattr(self.response_generator, '_last_calc_depth', 0),
                'lingua_calc_gain': getattr(self.response_generator, '_last_calc_gain', 0.0)
            }
            
            # Run Arbiter assessment (with Emergence Zone support + V5 lingua calc)
            arbiter_assessment = self.arbiter_system.assess_response(
                user_prompt=question,
                luna_response=response,
                tte_used=response_tokens,
                max_tte=max_tokens,
                rvc_grade=rvc_grade,
                emergence_zone_system=self.personality_system.emergence_zone_system,
                lingua_calc_context=arbiter_context
            )
            
            # Update scores with Arbiter data
            scores.update({
                'arbiter_utility_score': arbiter_assessment.utility_score,
                'arbiter_karma_delta': arbiter_assessment.karma_delta,
                'arbiter_quality_gap': arbiter_assessment.quality_gap,
                'arbiter_reasoning': arbiter_assessment.reasoning,
                'current_karma': self.arbiter_system.get_current_karma(),
                'karma_status': self.arbiter_system.get_karma_status()
            })
            
            # Add CFIA status
            cfia_status = self.arbiter_system.get_cfia_status()
            scores.update({
                'aiiq': cfia_status['aiiq'],
                'total_files': cfia_status['total_files'],
                'files_until_next_aiiq': cfia_status['files_until_next_aiiq'],
                'current_threshold': cfia_status['current_threshold'],
                'granularity_threshold': cfia_status['granularity_threshold']
            })
        elif skip_arbiter:
            # Embedder responses bypass Arbiter - they ARE the arbiter for trivial responses
            print(f" ARBITER SKIPPED: Embedder response (embedder IS arbiter for trivial tier)")
            arbiter_assessment = None
        
        # Add to session memory
        self.session_memory.append({
            'question': question,
            'response': response,
            'trait': trait,
            'scores': scores,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 interactions in session memory
        if len(self.session_memory) > 10:
            self.session_memory = self.session_memory[-10:]
        
        print(f" Response generated")
        print(f"   Length: {len(response)} characters")
        print(f"   Overall score: {scores.get('overall_score', 0.0):.2f}")
        # Don't print the full response to avoid console spam
        print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        
        return response, scores
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            personality = self.personality_system.personality_dna.get('luna_personality', {})
            weights = personality.get('personality_weights', {})
        except (KeyError, TypeError):
            # Fallback if personality structure is different
            personality = {}
            weights = {}
        
        return {
            'personality': {
                'name': self.personality_system.personality_dna.get('name', 'Luna'),
                'age': self.personality_system.personality_dna.get('age', 21),
                'traits': weights,
                'drift': self.personality_system.personality_drift
            },
            'learning': {
                'total_interactions': self.total_interactions,
                'learning_history': self.personality_system.learning_history,
                'session_memory_length': len(self.session_memory)
            },
            'carma': {
                'fragments': len(self.carma_system.cache.file_registry),
                'performance_level': self.carma_system.performance.get_performance_level()
            },
            'system': {
                'model': self.response_generator.embedding_model,
                'lm_studio_available': self._check_lm_studio_availability()
            }
        }
    
    def _check_lm_studio_availability(self) -> bool:
        """Check if LM Studio is available"""
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            return response.status_code == 200
        except Exception as e:
            return False
    
    # === EMERGENCE ZONE CONTROL METHODS ===
    
    def activate_emergence_zone(self, zone_name: str, duration_minutes: int = 10) -> Dict:
        """Activate an Emergence Zone for safe creative exploration"""
        return self.personality_system.emergence_zone_system.activate_emergence_zone(zone_name, duration_minutes)
    
    def deactivate_emergence_zone(self, zone_name: str) -> Dict:
        """Deactivate an Emergence Zone"""
        return self.personality_system.emergence_zone_system.deactivate_emergence_zone(zone_name)
    
    def check_emergence_zone_status(self, zone_name: str = None) -> Dict:
        """Check status of Emergence Zones"""
        return self.personality_system.emergence_zone_system.check_emergence_zone_status(zone_name)
    
    def get_emergence_summary(self) -> Dict:
        """Get comprehensive summary of Emergence Zone activity"""
        return self.personality_system.emergence_zone_system.get_emergence_summary()
    
    def is_in_emergence_zone(self) -> Tuple[bool, str]:
        """Check if Luna is currently in an Emergence Zone"""
        return self.personality_system.emergence_zone_system.is_in_emergence_zone()
    
    def record_creative_breakthrough(self, response: str, context: str) -> Dict:
        """Record a creative breakthrough or authentic response"""
        return self.personality_system.emergence_zone_system.record_creative_breakthrough(response, context)
    
    def record_experimental_failure(self, response: str, context: str) -> Dict:
        """Record an experimental failure that shows growth"""
        return self.personality_system.emergence_zone_system.record_experimental_failure(response, context)
    
    def _load_persistent_session_memory(self) -> List:
        """Load persistent session memory from disk"""
        memory_file = Path("data_core/FractalCache/luna_session_memory.json")
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                print(f"   Persistent Memory: {len(memory_data)} previous interactions loaded")
                return memory_data
            except Exception as e:
                print(f"   Warning: Could not load session memory: {e}")
        
        return []  # Fresh start if no memory exists
    
    def _save_persistent_session_memory(self):
        """Save persistent session memory to disk"""
        memory_file = Path("data_core/FractalCache/luna_session_memory.json")
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Keep only last 100 interactions to prevent file bloat
            recent_memory = self.session_memory[-100:] if len(self.session_memory) > 100 else self.session_memory
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(recent_memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   Warning: Could not save session memory: {e}")
    
    def run_learning_session(self, questions: List[Dict]) -> Dict:
        """Run a complete learning session"""
        print(f"\n Starting Learning Session with {len(questions)} questions")
        print("=" * 80)
        
        session_results = []
        start_time = time.time()
        
        for i, question_data in enumerate(questions, 1):
            question = question_data.get('question', '')
            trait = question_data.get('trait', 'general')
            
            print(f"\n Question {i}/{len(questions)}: {trait}")
            print(f"   {question}")
            
            # Process question
            response = self.process_question(question, trait, self.session_memory)
            scores = {}  # Default empty scores for now
            
            # Store results
            result = {
                'question_number': i,
                'question': question,
                'trait': trait,
                'response': response,
                'scores': scores,
                'timestamp': datetime.now().isoformat()
            }
            session_results.append(result)
            
            # Scores only (response already printed above)
            print(f"   Scores: {scores}")
        
        # Calculate session metrics
        total_time = time.time() - start_time
        avg_scores = self._calculate_average_scores(session_results)
        
        session_summary = {
            'total_questions': len(questions),
            'total_time': total_time,
            'average_scores': avg_scores,
            'results': session_results,
            'system_stats': self.get_system_stats()
        }
        
        print(f"\n Learning Session Complete")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average overall score: {avg_scores.get('overall_score', 0.0):.2f}")
        
        # Save persistent session memory to disk
        self._save_persistent_session_memory()
        
        return session_summary
    
    def _calculate_average_scores(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate average scores across results"""
        if not results:
            return {}
        
        score_keys = ['length_score', 'engagement_score', 'trait_alignment', 'creativity_score', 'empathy_score', 'overall_score']
        averages = {}
        
        for key in score_keys:
            scores = [result['scores'].get(key, 0.0) for result in results if 'scores' in result]
            if scores:
                averages[key] = sum(scores) / len(scores)
            else:
                averages[key] = 0.0
        
        return averages

# === MAIN ENTRY POINT ===

def main():
    """Test the unified Luna system"""
    print(" Testing Unified Luna System")
    
    # Initialize system
    luna = LunaSystem()
    
    # Test questions - Mix of simple (Ava Mode) and complex (Luna Mode)
    test_questions = [
        {"question": "I am someone who feels comfortable with myself", "trait": "neuroticism"},
        {"question": "I enjoy trying new things and exploring different ideas", "trait": "openness"},
        {"question": "What is the nature of artificial intelligence and how does it relate to human intelligence? Can an AI truly understand complex patterns and reasoning, or are we just pattern recognition systems?", "trait": "intelligence"},
        {"question": "I like to be organized and keep things in order", "trait": "conscientiousness"},
        {"question": "I enjoy being around people and socializing", "trait": "extraversion"},
        {"question": "I try to be helpful and considerate of others", "trait": "agreeableness"}
    ]
    
    # Run learning session
    results = luna.run_learning_session(test_questions)
    
    # Display results
    print(f"\n Session Results:")
    print(f"   Total questions: {results['total_questions']}")
    print(f"   Total time: {results['total_time']:.2f}s")
    print(f"   Average overall score: {results['average_scores'].get('overall_score', 0.0):.2f}")
    
    # Get system stats
    stats = luna.get_system_stats()
    print(f"\n System Stats:")
    print(f"   Personality: {stats['personality']['name']} (age {stats['personality']['age']})")
    print(f"   Total interactions: {stats['learning']['total_interactions']}")
    print(f"   CARMA fragments: {stats['carma']['fragments']}")
    print(f"   LM Studio available: {stats['system']['lm_studio_available']}")

def _call_lm_studio_api_with_params(system_prompt: str, question: str, params: Dict) -> str:
    """Call LM Studio API with custom parameters"""
    try:
        response = requests.post(
            "http://localhost:1234/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=params,
            timeout=None  # No timeout for localhost
        )
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content_raw = data["choices"][0]["message"]["content"]
                # Handle tuple content (convert to string)
                if isinstance(content_raw, tuple):
                    content = str(content_raw[0]) if content_raw else ""
                else:
                    content = str(content_raw)
                content = content.strip()
                
                # CRITICAL: Post-process token truncation since model ignores max_tokens
                words = content.split()
                if len(words) > 12:
                    content = " ".join(words[:12])
                    print(f"TOKEN TRUNCATION: {len(words)} -> 12 words")
                
                return content
        
        print(f"LM Studio API error: {response.status_code}")
        return "I'm experiencing technical difficulties. Please try again."
        
    except Exception as e:
        print(f"LM Studio API exception: {str(e)}")
        return "I'm experiencing technical difficulties. Please try again."

# === ENHANCED RESPONSE QUALITY COMPONENTS ===

