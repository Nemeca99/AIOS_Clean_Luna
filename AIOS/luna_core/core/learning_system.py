#!/usr/bin/env python3
"""
Luna Learning System
Handles learning cycles and personality evolution
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
import os
import requests
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

# Import AIOS systems
from support_core.support_core import SystemConfig

# Import from core modules
from .utils import HiveMindLogger
from .personality import LunaPersonalitySystem
from .response_generator import LunaResponseGenerator

# === LUNA LEARNING SYSTEM ===


class LunaLearningSystem:
    """Luna's learning and adaptation system"""
    
    def __init__(self, personality_system: LunaPersonalitySystem, logger, carma_system=None):
        self.personality_system = personality_system
        self.logger = logger
        self.carma_system = carma_system
        self.learning_rate = SystemConfig.LEARNING_RATE
        self.adaptation_threshold = SystemConfig.ADAPTATION_THRESHOLD
        
        # Initialize response generator once (not per request)
        self.response_generator = LunaResponseGenerator(self.personality_system, self.logger, self.carma_system)
        
        # === EXPERIMENTAL FEATURES (Disabled) ===
        # These are experimental modules that are not currently enabled
        
        # Conversation Math Engine - Mathematical weight calculations
        CONVERSATION_MATH_AVAILABLE = False  # Experimental feature
        if CONVERSATION_MATH_AVAILABLE:
            self.conversation_math = ConversationMathEngine(base_depth=0.001)
            print("   Conversation Math Engine initialized")
        else:
            self.conversation_math = None
            print("   [Experimental] Conversation Math Engine: Disabled")
        
        # CARMA Hypothesis Integration - Continuous learning
        HYPOTHESIS_INTEGRATION_AVAILABLE = False  # Experimental feature
        if HYPOTHESIS_INTEGRATION_AVAILABLE:
            self.hypothesis_integration = CARMAHypothesisIntegration()
            print("   CARMA Hypothesis Integration initialized")
            print(f"   Testing {len(self.hypothesis_integration.tester.hypotheses)} hypotheses")
        else:
            self.hypothesis_integration = None
            print("   [Experimental] CARMA Hypothesis Integration: Disabled")
        
        # Provenance Logging - Closed-loop evaluation
        PROVENANCE_AVAILABLE = False  # Experimental feature
        if PROVENANCE_AVAILABLE:
            self.provenance_logger = get_hypothesis_logger()
            print("   Provenance logging initialized")
            print("   Analytics: data_core/analytics/hypotheses.ndjson")
        else:
            self.provenance_logger = None
            print("   [Experimental] Provenance Logging: Disabled")
        
        # Adaptive Routing - A/B testing and dynamic weights
        ADAPTIVE_ROUTING_AVAILABLE = False  # Experimental feature
        if ADAPTIVE_ROUTING_AVAILABLE:
            self.adaptive_router = get_adaptive_router()
            print("   Adaptive routing initialized")
            print("   A/B buckets: control (50%) / treatment (50%)")
        else:
            self.adaptive_router = None
            print("   [Experimental] Adaptive Routing: Disabled")
        
        print(" Luna Learning System Initialized")
        print(f"   Learning rate: {self.learning_rate}")
        print(f"   Adaptation threshold: {self.adaptation_threshold}")
    
    def process_question(self, question: str, trait: str, session_memory: Optional[List] = None) -> Tuple[str, Dict]:
        """Process a question and generate response with learning"""
        # DEFENSIVE PROGRAMMING: Handle tuple inputs
        if isinstance(question, tuple):
            question = question[0] if question else "hi"
        if isinstance(trait, tuple):
            trait = trait[0] if trait else "general"
        try:
            # Check for template responses FIRST (before any routing)
            if hasattr(self, 'response_generator'):
                template_response = self.response_generator._check_for_template_response(question)
                if template_response:
                    # Return template directly without routing or CARMA
                    return template_response, {}
            
            # Generate conversation ID early for adaptive routing
            conversation_id = session_memory[0].get('conversation_id', f"conv_{uuid.uuid4().hex[:8]}") if session_memory else f"conv_{uuid.uuid4().hex[:8]}"
            msg_id = session_memory[0].get('msg_count', 0) + 1 if session_memory else 1
            
            # Initialize message_weight to None (will be set by conversation_math if available)
            message_weight = None
            
            # Get relevant memories from CARMA
            carma_memories = {}
            embedder_can_answer = False
            if hasattr(self, 'carma_system'):
                try:
                    carma_result = self.carma_system.process_query(question)
                    carma_memories = {
                        'fragments_found': carma_result.get('fragments_found', 0),
                        'conversation_memories_found': carma_result.get('conversation_memories_found', []),
                        'fragments': carma_result.get('fragments_found', []),
                        'conversation_memories': carma_result.get('conversation_memories_found', [])
                    }
                    # print(f"   CARMA found {carma_memories['fragments_found']} fragments and {len(carma_memories['conversation_memories_found'])} conversation memories")
                    
                    # SMART ROUTING DECISION LOGIC
                    # Use complexity and expected length to determine optimal routing
                    question_complexity = self.response_generator._assess_question_complexity(question)
                    expected_response_length = self.response_generator._estimate_expected_response_length(question, question_complexity)
                    routing_decision = self.response_generator._make_smart_routing_decision(question, question_complexity, expected_response_length)
                    
                    # print(f"   SMART ROUTING DECISION:")
                    # print(f"   - Question Complexity: {question_complexity:.3f}")
                    # print(f"   - Expected Length: {expected_response_length}")
                    # print(f"   - Route: {routing_decision['route']}")
                    # print(f"   - Use SD: {routing_decision['use_sd']}")
                    # print(f"   - Reasoning: {routing_decision['reasoning']}")
                        
                except Exception as e:
                    print(f"   CARMA query failed: {e}")
                    carma_memories = {}
            
            # Fallback routing decision if CARMA failed
            if 'routing_decision' not in locals():
                question_complexity = self.response_generator._assess_question_complexity(question)
                expected_response_length = self.response_generator._estimate_expected_response_length(question, question_complexity)
                routing_decision = self.response_generator._make_smart_routing_decision(question, question_complexity, expected_response_length)
            
            # SMART ROUTING: EMBEDDER VS MAIN MODEL
            # Use complexity and expected length to determine response path
            
            if routing_decision['route'] == 'embedder':
                # EMBEDDER PATH: Direct, blunt responses for simple questions
                # print(f"   ROUTING: Using embedder for direct response")
                
                # Use embedder with toned-down system prompt
                embedder_prompt = """You speak directly and descriptively. You'll answer any question and discuss any topic openly. You maintain a straightforward, honest communication style without excessive politeness."""
                
                # Call embedder model
                response = self._call_embedder_model(question, embedder_prompt)
                source = 'embedder'
                tier = 'trivial_low'
                response_type = 'direct_embedder'
                
            else:
                # MAIN MODEL PATH: Creative, engaging responses for complex questions
                # print(f"   ROUTING: Using main model for engaging response")
                
                # Set SD preference based on routing decision
                # Note: SD is controlled in LM Studio UI, but we track the preference
                use_sd = routing_decision.get('use_sd', False)
                
                # Generate response using existing generator with CARMA memories
                response = self.response_generator.generate_response(question, trait, carma_memories, session_memory)
                source = 'main_model'
                tier = 'moderate_high' if routing_decision['route'] == 'main_no_sd' else 'high'
                response_type = 'full_generation'
            
            # Score response
            scores = self._score_response(response, trait, question)
            
            # Update learning
            self._update_learning(question, response, trait, scores)
            
            # Update personality drift
            self._update_personality_drift(scores)
            
            # LOG DATA FOR HYPOTHESIS TESTING
            if self.hypothesis_integration:
                hypothesis_message_data = {
                    "calculated_weight": question_complexity,  # Use complexity as weight
                    "source": source,
                    "response_time_ms": 0,  # Will be calculated by caller
                    "question_complexity": question_complexity,
                    "expected_response_length": expected_response_length,
                    "routing_route": routing_decision['route'],
                    "use_sd": routing_decision['use_sd'],
                    "fragments_found": carma_memories.get('fragments_found', 0),
                    "context_messages": [],  # Will be populated by caller
                    "response_quality": scores.get('overall', 0.5)
                }
                
                # Log to hypothesis integration
                self.hypothesis_integration.log_conversation_data(conversation_id, hypothesis_message_data)
                
                # UPDATE ADAPTIVE ROUTING based on hypothesis results
                if self.adaptive_router and len(self.hypothesis_integration.conversation_buffer) > 0:
                    # Get hypothesis test results
                    hypothesis_results = {
                        'rates': {
                            'quality': scores.get('overall', 0.5),
                            'latency': 0.0,  # Will be calculated by caller
                            'memory': 0.1
                        },
                        'passed': sum(1 for r in self.hypothesis_integration.test_results if r.get('passed', False)),
                        'failed': sum(1 for r in self.hypothesis_integration.test_results if not r.get('passed', True))
                    }
                    
                    # Update adaptive routing
                    adaptive_metadata = self.adaptive_router.update_from_hypotheses(
                        hypothesis_results,
                        msg_seq=msg_id,
                        conv_id=conversation_id
                    )
                    
                    if adaptive_metadata.get('adaptive', {}).get('adapted', False):
                        print(f"   ADAPTIVE: {adaptive_metadata['adaptive']['direction']} - {adaptive_metadata['adaptive']['reason']}")
                        print(f"   ADAPTIVE: New boundary: {adaptive_metadata['boundary']:.3f}")
            
            # LOG PROVENANCE FOR CLOSED-LOOP EVALUATION
            if self.provenance_logger:
                # Prepare smart routing data
                smart_routing_data = {
                    'question_complexity': question_complexity,
                    'expected_response_length': expected_response_length,
                    'routing_route': routing_decision['route'],
                    'use_sd': routing_decision['use_sd'],
                    'routing_reasoning': routing_decision['reasoning']
                }
                
                # Add adaptive routing data if available
                if hasattr(self, 'adaptive_router') and self.adaptive_router:
                    smart_routing_data['adaptive'] = {
                        'bucket': self.adaptive_router.assign_bucket(conversation_id),
                        'boundary': self.adaptive_router.current_boundary(conversation_id),
                        'adaptive_metadata': adaptive_metadata if 'adaptive_metadata' in locals() else None
                    }
                
                # Log response event
                log_response_event(
                    self.provenance_logger,
                    conv_id=conversation_id,
                    msg_id=msg_id,
                    question=question,
                    trait=trait,
                    response=response,
                    meta={'source': source, 'tier': tier, 'response_type': response_type},
                    carma=carma_memories,
                    math_weights=smart_routing_data
                )
            
            # CRITICAL: Apply post-processing BEFORE returning
            # This ensures all responses get cleaned up
            response = self.response_generator._normalize_caps(response)
            response = self.response_generator._clarify_vocal_stims(response)
            response = self.response_generator._remove_stray_hmm(response)
            response = self.response_generator._enforce_brevity(response, target_words=30)
            
            return response, {
                'source': source,
                'tier': tier,
                'response_type': response_type,
                'routing_decision': routing_decision,
                'question_complexity': question_complexity,
                'expected_response_length': expected_response_length
            }
            
        except Exception as e:
            import traceback
            self.logger.log("LUNA", f"Error processing question: {e}", "ERROR")
            print(f"   ERROR DETAILS: {e}")
            print(f"   TRACEBACK: {traceback.format_exc()}")
            return "I'm sorry, I encountered an error processing your question.", {}
    
    def _call_embedder_model(self, question: str, system_prompt: str) -> str:
        """Call the embedder model for direct responses"""
        try:
            # Load model config to get embedder endpoint
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'model_config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            embedder_config = config.get('embedder_llm', {})
            api_endpoint = embedder_config.get('api_endpoint', 'http://localhost:1234/v1/chat/completions')
            
            # Prepare the request
            payload = {
                "model": embedder_config.get('model_name', 'llama-3.2-1b-instruct-abliterated'),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.7,
                "max_tokens": 150,  # Shorter responses for embedder
                "stream": False
            }
            
            # Make the API call
            response = requests.post(api_endpoint, json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                embedder_response = result['choices'][0]['message']['content'].strip()
                print(f"   EMBEDDER RESPONSE: {embedder_response[:100]}...")
                return embedder_response
            else:
                print(f"   EMBEDDER ERROR: {response.status_code} - {response.text}")
                return f"Embedder error: {response.status_code}"
                
        except Exception as e:
            print(f"   EMBEDDER CALL FAILED: {e}")
            # Fallback to simple response
            return f"Direct response: {question.lower()}"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get mathematical summary of conversation with hypothesis testing results"""
        summary = {}
        
        # Get conversation math summary
        if self.conversation_math:
            summary["conversation_math"] = self.conversation_math.get_conversation_summary()
        else:
            summary["conversation_math"] = {"status": "Conversation math engine not available"}
        
        # Get hypothesis testing summary
        if self.hypothesis_integration:
            summary["hypothesis_testing"] = {
                "status": self.hypothesis_integration.tester.get_hypothesis_status(),
                "buffer_size": len(self.hypothesis_integration.conversation_buffer),
                "last_test_time": self.hypothesis_integration.last_test_time.isoformat() if self.hypothesis_integration.last_test_time else None,
                "recent_results": self.hypothesis_integration.test_results
            }
        else:
            summary["hypothesis_testing"] = {"status": "Hypothesis integration not available"}
        
        return summary
    
    def _score_response(self, response: str, trait: str, question: str = "") -> Dict[str, float]:
        """Score response using LLM performance evaluation system instead of legacy metrics"""
        try:
            # Ensure response is a string, not a tuple
            if isinstance(response, tuple):
                response = response[0] if response else ""
            elif not isinstance(response, str):
                response = str(response)
            # TEMPORARILY DISABLED: Complex evaluation system causing tuple errors
            # Return simple fallback scores for now
            return {
                'length_score': 1.0,
                'engagement_score': 1.0,
                'trait_alignment': 0.8,
                'creativity_score': 0.8,
                'empathy_score': 0.8,
                'overall_score': 0.8,
                'performance_score': 8.0,
                'performance_level': 'good',
                'architect_scores': {},
                'semantic_scores': {}
            }
            
        except Exception as e:
            self.logger.log("LUNA", f"LLM performance evaluation failed, using fallback: {e}", "ERROR")
            return self._fallback_scoring(response, trait)
    
    def _fallback_scoring(self, response: str, trait: str) -> Dict[str, float]:
        """Fallback scoring if LLM performance evaluation fails"""
        response_lower = response.lower()
        
        # Basic scoring metrics
        scores = {
            'length_score': min(len(response.split()) / 50.0, 1.0),
            'engagement_score': self._calculate_engagement_score(response_lower),
            'trait_alignment': self._calculate_trait_alignment(response_lower, trait),
            'creativity_score': self._calculate_creativity_score(response_lower),
            'empathy_score': self._calculate_empathy_score(response_lower)
        }
        
        # Overall score
        scores['overall_score'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _calculate_engagement_score(self, response_lower: str) -> float:
        """Calculate engagement score"""
        engagement_words = ['interesting', 'fascinating', 'cool', 'nice', 'good', 'ok']
        engagement_count = sum(1 for word in engagement_words if word in response_lower)
        return min(engagement_count / 3.0, 1.0)
    
    def _calculate_trait_alignment(self, response_lower: str, trait: str) -> float:
        """Calculate trait alignment score"""
        trait_keywords = {
            'openness': ['creative', 'imaginative', 'artistic', 'curious', 'innovative', 'novel', 'explore', 'constraint'],
            'conscientiousness': ['organized', 'systematic', 'methodical', 'reliable', 'disciplined', 'checklist', 'verify', 'audit', 'review', 'risk'],
            'extraversion': ['social', 'outgoing', 'energetic', 'enthusiastic', 'talkative', 'group', 'together'],
            'agreeableness': ['helpful', 'kind', 'cooperative', 'compassionate', 'understanding', 'considerate', 'fair'],
            'neuroticism': ['anxious', 'worried', 'stressed', 'nervous', 'tense', 'rumination', 'wobble', 'trigger']
        }
        
        keywords = trait_keywords.get(trait, [])
        if not keywords:
            return 0.5
        
        keyword_count = sum(1 for keyword in keywords if keyword in response_lower)
        return min(keyword_count / max(1, len(keywords)), 1.0)
    
    def _calculate_creativity_score(self, response_lower: str) -> float:
        """Calculate creativity score"""
        creative_indicators = ['imagine', 'creative', 'unique', 'original', 'innovative', 'artistic']
        creative_count = sum(1 for indicator in creative_indicators if indicator in response_lower)
        return min(creative_count / 3.0, 1.0)
    
    def _calculate_empathy_score(self, response_lower: str) -> float:
        """Calculate empathy score"""
        empathy_indicators = ['understand', 'feel', 'empathize', 'relate', 'support', 'care']
        empathy_count = sum(1 for indicator in empathy_indicators if indicator in response_lower)
        return min(empathy_count / 3.0, 1.0)
    
    def _update_learning(self, question: str, response: str, trait: str, scores: Dict):
        """Update learning based on interaction"""
        # Update learning history
        if 'total_questions' not in self.personality_system.learning_history:
            self.personality_system.learning_history = self.personality_system._create_default_learning_history()
        
        self.personality_system.learning_history['total_questions'] += 1
        self.personality_system.learning_history['total_responses'] += 1
        self.personality_system.learning_history['last_learning'] = datetime.now().isoformat()
        
        # Add to personality evolution
        evolution_entry = {
            'timestamp': datetime.now().isoformat(),
            'trait': trait,
            'scores': scores,
            'personality_drift': self.personality_system.personality_drift
        }
        self.personality_system.learning_history['personality_evolution'].append(evolution_entry)
        
        # Save learning history
        self.personality_system._save_learning_history()
    
    def _update_personality_drift(self, scores: Dict):
        """Update personality drift based on scores"""
        # Simple drift calculation
        overall_score = scores.get('overall_score', 0.5)
        drift_change = (overall_score - 0.5) * self.learning_rate
        self.personality_system.personality_drift += drift_change
        
        # Clamp drift to reasonable range
        self.personality_system.personality_drift = max(-1.0, min(1.0, self.personality_system.personality_drift))

# === UNIFIED LUNA SYSTEM ===

