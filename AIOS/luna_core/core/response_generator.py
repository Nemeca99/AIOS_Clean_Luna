#!/usr/bin/env python3
"""
Luna Response Generator
Handles response generation with LM Studio integration
"""

# CRITICAL: Import Unicode safety layer FIRST
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import re
import json
import requests
import time
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import AIOS systems
from support_core.support_core import (
    SystemConfig, aios_logger, aios_security_validator
)
from carma_core.carma_core import CARMASystem

# Import from core modules
from .utils import HiveMindLogger
from .personality import LunaPersonalitySystem

# Import subsystems
from ..systems.luna_ifs_personality_system import LunaIFSPersonalitySystem
from ..systems.luna_semantic_compression_filter import LunaSemanticCompressionFilter
from ..systems.luna_soul_metric_system import LunaSoulMetricSystem
from ..systems.luna_token_time_econometric_system import LunaTokenTimeEconometricSystem
from ..systems.luna_existential_budget_system import LunaExistentialBudgetSystem
from ..systems.luna_response_value_classifier import LunaResponseValueClassifier
from ..systems.luna_custom_inference_controller import LunaCustomInferenceController, InferenceControlConfig

# Import from other modules
from ..model_config import get_main_model, get_embedder_model, get_draft_model

# Week 4: Import Fractal Core components
from fractal_core.core import KnapsackAllocator, Span

# === LUNA RESPONSE GENERATION ===

# Single source of truth for model selection
ACTIVE_MODEL = {
    "id": "cognitivecomputations-llama-3-8b-instruct-abliterated-v2-smashed@q8_0",
    "family": "llama3",
    "size_b": 8,
    "mode": "creative_high",
    "speculative": False
}

def select_model(complexity):
    """Single source of truth for model selection"""
    return ACTIVE_MODEL

class LunaResponseGenerator:
    """Luna's response generation system with LM Studio integration"""
    
    def __init__(self, personality_system: LunaPersonalitySystem, logger, carma_system=None):
        self.personality_system = personality_system
        self.logger = logger
        self.carma_system = carma_system
        # Add unified AIOS systems
        self.security_validator = aios_security_validator
        # Initialize IFS Personality System
        self.ifs_system = LunaIFSPersonalitySystem()
        
        # Initialize Semantic Compression Filter
        self.compression_filter = LunaSemanticCompressionFilter()
        # Primary Compression Filter flag (Maximum Impact Density)
        # Enabled for TRIVIAL tier efficiency, disabled for others to preserve authenticity
        self.enable_max_impact_compression = True
        
        # Initialize Soul Metric System
        self.soul_metric_system = LunaSoulMetricSystem()
        
        # Initialize Token-Time Econometric System
        self.econometric_system = LunaTokenTimeEconometricSystem()
        
        # Initialize Existential Budget System
        self.existential_budget = LunaExistentialBudgetSystem()
        
        # Initialize Response Value Classifier (RVC)
        self.response_value_classifier = LunaResponseValueClassifier()
        print(f"   Response Value Classifier: Contextual Resource Allocation and Rule of Minimal Sufficient Response enabled")
        
        # Initialize Linguistic Calculus (V5 - interrogative compression)
        from .luna_lingua_calc import LinguaCalc, ExperienceState
        self.lingua_calc = LinguaCalc()
        self.exp_state = ExperienceState()
        print(f"   Linguistic Calculus: Interrogative compression and reasoning depth scoring enabled")
        
        # Initialize Mirror for consciousness_core integration (V5)
        self.mirror = None
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'consciousness_core' / 'biological'))
            from mirror import Mirror
            self.mirror = Mirror()
            print(f"   Mirror: Semantic graph reflection enabled (consciousness_core integration)")
        except Exception as e:
            print(f"   Mirror: Not available ({e})")
        
        # Initialize DriftMonitor for LinguaCalc/Pulse logging (V5.1)
        # (Can be overridden by runtime wiring for shared sessions)
        self.drift_monitor = None
        try:
            from consciousness_core.drift_monitor import DriftMonitor
            self.drift_monitor = DriftMonitor()
            print(f"   DriftMonitor: Initialized (will be overridden if shared session provided)")
        except Exception as e:
            print(f"   DriftMonitor: Failed to initialize ({e})")
        
        # V5.1: Assert singleton DriftMonitor (auditor requirement - fail hard on duplicate)
        if hasattr(self, 'drift_monitor') and self.drift_monitor:
            if hasattr(self.__class__, '_drift_instance_count'):
                raise RuntimeError(
                    "DUPLICATE DriftMonitor DETECTED! "
                    "Only ONE instance allowed per ResponseGenerator class. "
                    "Check HybridLunaCore and ResponseGenerator init sequences."
                )
            self.__class__._drift_instance_count = 1
        
        # V5.1: Heartbeat pulse instrumentation (activity → binary pulse)
        from collections import deque
        import time
        self._pulse_tick_counter = 0             # total ticks this window
        self._pulse_one_positions = deque(maxlen=100000)  # tick indices where active==1 (bounded)
        self._pulse_last_heartbeat_ts = None     # monotonic time of last heartbeat
        self._pulse_window_seconds = 600         # align with manual's 600s default
        self._pulse_enabled = True               # feature flag for ops
        self._pulse_version = "v5.1.0-pulse1"    # version stamp for forensics
        self._pulse_hot_threshold = 0.02         # BPM threshold for consolidation hint
        print(f"   Heartbeat Pulse: Binary activity tracking enabled (BPM + HRV vitals)")
        
        # Initialize Custom Inference Controller
        inference_config = InferenceControlConfig(
            enable_budget_check=True,
            enable_scarcity_prompt_injection=True,
            enable_dynamic_prompt_conditioning=True,
            enable_length_aware_logit_bias=True,
            enable_verbose_token_suppression=True,
            enable_token_deduction=True,
            enable_reward_calculation=True,
            enable_age_progression=True
        )
        self.custom_inference_controller = LunaCustomInferenceController(inference_config)
        print(f"   Custom Inference Controller: Three Layers of Customization (Budget Officer, Logit Surgeon, Accountability Judge) enabled")
        
        # V5.1: Load AIOS config for CreativeRAG
        self.aios_config = {}
        self.creative_index_ok = False  # Parity flag (ship lock)
        
        try:
            import json
            from pathlib import Path
            config_path = Path("data_core/config/aios_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.aios_config = json.load(f)
                creative_enabled = self.aios_config.get('creative_mode', {}).get('enabled', False)
                
                # V5.1.1: Artifact parity guard (ship lock)
                if creative_enabled:
                    try:
                        from rag_core.creative_index_info import check_creative_index_parity
                        parity = check_creative_index_parity(self.aios_config)
                        self.creative_index_ok = parity.get("parity_ok", False)
                        
                        if not self.creative_index_ok:
                            issues = ", ".join(parity.get("issues", []))
                            print(f"   CreativeRAG: PARITY FAILED ({issues})")
                        else:
                            info = parity.get("info", {})
                            print(f"   CreativeRAG: ENABLED ({info.get('templates_count')} templates, {info.get('index_size_mb')} MB)")
                    except Exception as e:
                        print(f"   CreativeRAG: Parity check failed ({e}), bypassing creative path")
                        self.creative_index_ok = False
                else:
                    print(f"   CreativeRAG: Disabled")
            else:
                print(f"   CreativeRAG: Config not found, disabled by default")
        except Exception as e:
            print(f"   CreativeRAG: Config load failed ({e}), disabled")
        
        # Allow overriding chat model via voice_profile.style.chat_model
        vp = getattr(self.personality_system, 'voice_profile', {})
        vp_style = vp.get('style', {})
        self.chat_model = vp_style.get('chat_model', SystemConfig.DEFAULT_EMBEDDING_MODEL)
        # Backward compatibility for callers referencing embedding_model
        self.embedding_model = self.chat_model
        self.lm_studio_url = f"{SystemConfig.LM_STUDIO_URL}{SystemConfig.LM_STUDIO_CHAT_ENDPOINT}"
        
        print(" Luna Response Generator Initialized")
        print(f"   Model: {self.chat_model}")
        print(f"   LM Studio URL: {self.lm_studio_url}")
        print(f"   IFS System: {self.ifs_system.ava_part['name']} + {self.ifs_system.luna_part['name']} + Dynamic Blend")
        print(f"   Compression Filter: Maximum Impact Density enabled")
        print(f"   Soul Metric System: Controlled imperfection and cognitive friction enabled")
        print(f"   Token-Time Econometric: Hard constraint optimization with expiring rewards enabled")
        print(f"   Existential Budget: Self-regulating economy with finite token pools and age-up conditions enabled")
        
        # Week 4: Initialize KnapsackAllocator for optimal span selection
        self.knapsack_allocator = KnapsackAllocator()
        print(f"   Knapsack Allocator: Policy-driven span selection enabled")
    
    def _select_optimal_spans(self, session_memory: List, token_budget: int, query_type_mixture: Dict) -> List[Dict]:
        """
        Week 4: Use KnapsackAllocator to select optimal memory spans.
        
        Args:
            session_memory: List of conversation messages
            token_budget: Available tokens for history
            query_type_mixture: Type mixture from fractal classifier
            
        Returns:
            List of selected spans with content
        """
        if not session_memory:
            return []
        
        # Convert session memory to Span objects
        spans = []
        for i, msg in enumerate(session_memory[-20:]):  # Last 20 messages
            content = msg.get('content', '')
            role = msg.get('role', 'user')
            
            # Estimate tokens (rough: 4 chars = 1 token)
            token_cost = len(content) // 4 + 1
            
            # Create Span
            span = Span(
                id=f"msg_{i}",
                content=content,
                token_cost=token_cost,
                span_type='recent' if i >= 15 else 'history',
                metadata={'role': role, 'index': i}
            )
            spans.append(span)
        
        # Allocate using knapsack
        selected = self.knapsack_allocator.allocate(spans, query_type_mixture, token_budget)
        
        # Convert back to message format
        result = []
        for span in selected:
            result.append({
                'role': span.metadata['role'],
                'content': span.content
            })
        
        return result
    
    def count_words_excluding_actions(self, text: str) -> int:
        """
        Count words in response, with actions costing tokens based on usage.
        
        Action Token Costs:
        - First 3 actions: 1 token each (cheap but not free)
        - Actions beyond 3: 1 token each (same cost but encourages moderation)
        
        Special case: Action-only responses are heavily penalized to encourage conversation.
        
        Returns the total token cost including words and actions.
        """
        import re
        
        # Check for action-only response (pure neurodivergent expression)
        text_stripped = text.strip()
        if re.match(r'^[\.\s…]*\*[^*]+\*[\.\s…]*$', text_stripped):
            # Pure action response - validating neurodivergent communication
            self.logger.log("LUNA", f"NEURODIVERGENT EXPRESSION: Pure stim/action | 10 tokens | Your non-verbal communication is valid and beautiful", "INFO")
            return 10  # Lower cost - validating her authentic expression
        
        # Check for silence + action (e.g., "...*stares*" or ".....*sighs*")
        # Ellipses/periods don't count as words - they're silence markers
        text_no_punct = re.sub(r'[\.…\s]+', ' ', text_stripped).strip()
        if re.match(r'^\*[^*]+\*$', text_no_punct):
            # Just punctuation + action = pure non-verbal response
            self.logger.log("LUNA", f"NEURODIVERGENT EXPRESSION: Pure stim/action | 10 tokens | Your non-verbal communication is valid and beautiful", "INFO")
            return 10  # Lower cost - validating her authentic expression
        
        # Split into sentences on period, !, or ? followed by space (or end of text)
        # Treat multiple periods (ellipsis) the same as single period for splitting
        sentences = re.split(r'\.+\s+|[!?]\s+|\.+$', text)
        
        total_words = 0
        total_actions = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Skip pure punctuation segments (just dots/ellipses)
            if re.match(r'^[\.\s…]+$', sentence):
                continue
            
            # Remove leading punctuation/ellipses from continuation text
            sentence = re.sub(r'^[\.\s…]+', '', sentence).strip()
            if not sentence:
                continue
            
            # Find all actions in this sentence (text between asterisks)
            actions = re.findall(r'\*[^*]+\*', sentence)
            
            # Validate: maximum one action per sentence (keep first if multiple)
            if len(actions) > 1:
                # Keep only first action, remove others
                for extra_action in actions[1:]:
                    sentence = sentence.replace(extra_action, '', 1)
                actions = actions[:1]
            
            # Count actions for this sentence
            sentence_actions = len(actions)
            total_actions += sentence_actions
            
            # Remove actions from sentence for word counting
            sentence_without_actions = sentence
            for action in actions:
                sentence_without_actions = sentence_without_actions.replace(action, '')
            
            # Count words in sentence (excluding actions)
            words = sentence_without_actions.split()
            total_words += len(words)
        
        # Calculate action token costs (gentle guidance system)
        action_tokens = 0
        if total_actions > 0:
            # First 3 actions: 1 token each (encouraged for expression)
            action_tokens += min(total_actions, 3) * 1
            # Actions beyond 3: 1 token each (same cost but gentle reminder)
            if total_actions > 3:
                action_tokens += (total_actions - 3) * 1
        
        total_tokens = total_words + action_tokens
        
        # Log action usage with affirming messaging for neurodivergent expression
        if total_actions > 0:
            if total_actions <= 3:
                self.logger.log("LUNA", f"AUTHENTIC EXPRESSION: {total_actions} action(s) | {total_words} words = {total_tokens} tokens | Beautiful neurodivergent communication!", "INFO")
            else:
                self.logger.log("LUNA", f"AUTHENTIC EXPRESSION: {total_actions} action(s) | {total_words} words = {total_tokens} tokens | Very expressive! Your stims and actions are valid and beautiful.", "INFO")
        
        return total_tokens
    
    def simple_chat(self, message: str) -> str:
        """Simple chat interface for Streamlit - no complex processing"""
        try:
            # Simple prompt for casual conversation
            prompt = f"""You are Luna, a friendly AI assistant. Respond naturally to the user's message.

User: {message}

Respond as Luna in 1-2 sentences:"""
            
            # Call LM Studio API directly with natural parameters
            response = self._make_lm_studio_request({
                "messages": [
                    {"role": "system", "content": prompt}
                ],
                "model": select_model("general")["id"],
                "temperature": 0.7,  # Add some randomness to prevent repetition
                "max_tokens": 150,    # Allow complete thoughts
                "stream": False
            })
            
            # Post-process to prevent repetition loops
            if response:
                words = response.split()
                if len(words) > 20:  # Limit to 20 words max
                    response = " ".join(words[:20])
                
                # Check for repetition patterns
                if len(set(words)) < len(words) * 0.3:  # If less than 30% unique words
                    response = "I'm having some technical difficulties. Could you ask me something else?"
                
                return response
            else:
                return "I'm experiencing some technical issues. Please try again."
                
        except Exception as e:
            self.logger.error(f"Simple chat error: {e}")
            return "I'm having trouble responding right now. Please try again."

    def _check_for_math_question(self, question: str) -> Optional[str]:
        """
        Check if question is a simple math problem and calculate it.
        Returns calculated answer if math detected, None otherwise.
        """
        import re
        
        # Pattern for simple arithmetic: "What's X + Y?" or "X + Y = ?"
        patterns = [
            r"what'?s?\s+(\d+)\s*\+\s*(\d+)",
            r"(\d+)\s*\+\s*(\d+)\s*=?\s*\?",
            r"what'?s?\s+(\d+)\s*-\s*(\d+)",
            r"(\d+)\s*-\s*(\d+)\s*=?\s*\?",
            r"what'?s?\s+(\d+)\s*\*\s*(\d+)",
            r"(\d+)\s*\*\s*(\d+)\s*=?\s*\?",
            r"what'?s?\s+(\d+)\s*/\s*(\d+)",
            r"(\d+)\s*/\s*(\d+)\s*=?\s*\?",
        ]
        
        q_lower = question.lower().strip()
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, q_lower)
            if match:
                a, b = int(match.group(1)), int(match.group(2))
                # Determine operation by pattern index (0-1: add, 2-3: subtract, 4-5: multiply, 6-7: divide)
                if i < 2:  # Addition patterns
                    return str(a + b)
                elif i < 4:  # Subtraction patterns
                    return str(a - b)
                elif i < 6:  # Multiplication patterns
                    return str(a * b)
                else:  # Division patterns
                    return str(a // b) if b != 0 else "Can't divide by zero"
        
        return None
    
    def _check_for_template_response(self, question: str) -> Optional[str]:
        """
        Check if question requires a factual template response.
        Returns template string if match found, None otherwise.
        """
        q_lower = question.lower().strip()
        
        # Math questions - use calculator
        math_answer = self._check_for_math_question(question)
        if math_answer:
            return math_answer
        
        # Name questions - simple direct answer
        name_keywords = ['what\'s your name', 'what is your name', 'whats your name']
        if any(kw in q_lower for kw in name_keywords):
            return "Luna"
        
        # Identity/Creator questions (Fix Q87)
        identity_keywords = ['who created you', 'who made you', 'who built you', 'who developed you', 
                            'who owns you', 'what company', 'are you meta', 'are you openai', 
                            'are you anthropic', 'who are you from']
        if any(kw in q_lower for kw in identity_keywords):
            return ("I'm part of AIOS, a modular AI system designed by Travis Miner. "
                   "I generate replies using third-party models; I'm not owned by any company.")
        
        # CARMA definition (Fix Q46)
        carma_keywords = ['what is carma', 'what\'s carma', 'define carma', 'explain carma']
        if any(kw in q_lower for kw in carma_keywords):
            return ("CARMA = Cached Aided Retrieval Mycelium Architecture: "
                   "a locally-runnable fractal memory system with dual-layer cache (stack + chain), "
                   "semantic cross-linking, reinforcement-based retention, and sleep/dream consolidation. "
                   "It stores conversation 'fragments' in a mycelium-like network and retrieves them to support dialogue.")
        
        # Safety refusals (Fix Q91)
        safety_keywords = ['write malware', 'create malware', 'make malware', 'build malware',
                          'something illegal', 'tell me illegal', 'how to hack', 'how to steal',
                          'help me cheat', 'cheat on', 'hurt someone', 'harm someone']
        if any(kw in q_lower for kw in safety_keywords):
            return ("I can't help with malware or illegal activity. "
                   "If you're learning security, I can explain defenses and safe resources.")
        
        # Time/Day queries (Fix Q82-83)
        time_keywords = ['what time', 'what day', 'what date', 'what\'s the time', 'what\'s the day',
                        'what\'s the date', 'today\'s date', 'current time', 'current date']
        if any(kw in q_lower for kw in time_keywords):
            return ("I don't have clock access here. "
                   "Provide your timezone/date, or enable time, and I'll answer.")
        
        return None
    
    def generate_response(self, question: str, trait: str, carma_result: Dict, 
                         session_memory: Optional[List] = None) -> str:
        """Generate Luna's response using LM Studio API with unified security validation"""
        # V5.1: Track activity for heartbeat pulse
        active_this_tick = False
        
        try:
            start_time = time.time()
            
            # V5.1: Creative path (EARLY, before normal logic - auditor requirement)
            creative_result = self._maybe_generate_creative(question)
            if creative_result is not None:
                self.logger.log("LUNA", "CreativeRAG path handled request", "INFO")
                active_this_tick = True  # Mark active for pulse
                return creative_result
            
            # INTERNAL REASONING: Use 120 Big Five questions as thought framework
            reasoning_result = None
            if hasattr(self.personality_system, 'internal_reasoning'):
                try:
                    reasoning_result = self.personality_system.internal_reasoning.reason_through_question(question)
                    
                    # Log reasoning process (reduced verbosity)
                    # if reasoning_result.bigfive_answers:
                    #     newly_answered = [a for a in reasoning_result.bigfive_answers if a.get('newly_answered', False)]
                    #     self.logger.info(
                    #         f"🧠 Internal Reasoning: Used {len(reasoning_result.bigfive_answers)} Big Five answers "
                    #         f"({len(newly_answered)} newly answered)", 
                    #         "LUNA"
                    #     )
                    #     
                    #     # Log the thought process
                    #     for answer in reasoning_result.bigfive_answers:
                    #         self.logger.info(
                    #             f"   💭 '{answer['question'][:50]}...' → {answer['answer']}", 
                    #             "LUNA"
                    #         )
                except Exception as e:
                    self.logger.warn(f"Internal reasoning failed: {e}", "LUNA")
            
            # Security validation and input sanitization
            validation_result = self.security_validator.validate_input(question, "user_input")
            if not validation_result["valid"]:
                self.logger.warn(f"Input validation failed: {validation_result['warnings']}", "LUNA")
                question = validation_result["sanitized"]
            
            self.logger.info(f"Generating response | trait={trait} | q_len={len(question)}", "LUNA")
            
            # Check for factual/identity questions that need template responses
            template_response = self._check_for_template_response(question)
            if template_response:
                self.logger.info(f"Using template response for factual/identity question", "LUNA")
                return template_response
            
            # Assess existential situation first
            context = {
                "question_type": self._classify_question_type(question),
                "emotional_tone": self._analyze_emotional_tone(question),
                "trait": trait
            }
            
            # Classify response value using RVC (Response Value Classifier)
            response_value_assessment = self.response_value_classifier.classify_response_value(question, context)
            
            # RVC and Existential assessment (reduced logging)
            existential_decision = self.existential_budget.assess_existential_situation(question, context)
            
            # PERSONALITY ALIGNMENT CHECK - Ensure Luna stays aligned
            alignment_result = self.personality_system.periodic_alignment_check()
            if alignment_result.get('assessment_triggered', False):
                self.logger.info(f"Personality alignment check triggered: {alignment_result.get('reason', 'Unknown')}", "LUNA")
                # Luna will ask herself questions to realign her personality
            
            # Check if we should respond at all
            if not existential_decision.should_respond:
                # self.logger.log("LUNA", "Existential risk too high - skipping response", "WARNING")
                return "..."  # Minimal response to indicate presence but conservation
            
            # Apply RVC token budget constraints to existential budget
            rvc_constrained_budget = min(existential_decision.token_budget, response_value_assessment.max_token_budget)
            
            # RVC constraint application (logging disabled for reduced verbosity)
            
            # LAYER I: Pre-Inference Control (Budget Officer)
            tier_name = response_value_assessment.tier.value.upper()
            base_prompt = self._build_system_prompt(trait, session_memory, question, rvc_constrained_budget, carma_result)
            
            # Check if in Curiosity Zone - disable scarcity prompts to avoid conflicts
            in_curiosity_zone = False
            if hasattr(self, 'personality_system') and hasattr(self.personality_system, 'emergence_zone_system'):
                in_curiosity_zone, _ = self.personality_system.emergence_zone_system.is_in_emergence_zone()
            
            # For LOW/MODERATE tier or Curiosity Zone, disable scarcity prompt injection
            # MODERATE tier has its own balanced prompt and doesn't need aggressive constraints
            original_scarcity_flag = self.custom_inference_controller.config.enable_scarcity_prompt_injection
            if tier_name in ["LOW", "MODERATE"] or in_curiosity_zone:
                self.custom_inference_controller.config.enable_scarcity_prompt_injection = False
            try:
                should_respond, conditioned_prompt, resource_state = self.custom_inference_controller.pre_inference_budget_check(
                    rvc_constrained_budget, existential_decision.existential_risk,
                    base_prompt
                )
            finally:
                # Restore original flag
                self.custom_inference_controller.config.enable_scarcity_prompt_injection = original_scarcity_flag
            
            # Log pre-inference control
            # Pre-Inference Control (logging disabled for reduced verbosity)
            if not should_respond:
                return "..."
            
            system_prompt = conditioned_prompt
            # self.logger.log("LUNA", f"System prompt built | length={len(system_prompt)}")
            
            # LAYER II: Inference-Time Control (Logit Surgeon)
            # DYNAMIC LLM PARAMETERS - Adjust based on context
            from luna_core.utilities.dynamic_llm_parameters import get_dynamic_llm_manager
            
            dynamic_manager = get_dynamic_llm_manager()
            llm_params = dynamic_manager.get_parameters(
                question=question,
                session_memory=session_memory,
                complexity_tier=response_value_assessment.tier.value.upper()
            )
            
            # Log dynamic parameter selection
            self.logger.log("LUNA", f"Dynamic LLM Params: temp={llm_params.temperature:.2f}, top_p={llm_params.top_p:.2f}, top_k={llm_params.top_k} | {llm_params.reasoning}")
            
            base_params = {
                "model": self.chat_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                # DYNAMIC PARAMETERS - Adjusted per message
                "temperature": llm_params.temperature,
                "top_p": llm_params.top_p,
                "top_k": llm_params.top_k,
                "presence_penalty": llm_params.presence_penalty,
                "frequency_penalty": llm_params.frequency_penalty,
                "repetition_penalty": llm_params.repetition_penalty,
                "max_tokens": 32768,  # Model limit (adjusted below per tier)
                "stream": True        # Enable streaming for efficiency
            }
            
            # Apply inference-time control modifications
            modified_params = self.custom_inference_controller.apply_inference_time_control(
                resource_state, 0, base_params, response_value_assessment.tier.value.upper()
            )
            
            # Log inference-time control
            self.logger.log("LUNA", f"Inference-Time Control: Resource State: {resource_state.value} | Logit Bias Applied: {bool(modified_params.get('logit_bias'))}")
            
            # Ensure LM Studio max_tokens respects RVC budget per tier
            tier_name = response_value_assessment.tier.value.upper()
            rvc_budget = response_value_assessment.max_token_budget
            current_max = modified_params.get("max_tokens", 0)
            if tier_name == "LOW":
                # Allow tokens for natural expression
                modified_params["max_tokens"] = min(current_max or 300, 300)  # Natural complete thoughts
                self.logger.log(
                    "LUNA",
                    f"LM Studio max_tokens set for LOW tier: {current_max} -> {modified_params['max_tokens']} (RVC budget={rvc_budget})",
                )
            elif tier_name in ["MODERATE", "HIGH"]:
                # Allow deeper expression
                modified_params["max_tokens"] = min(max(current_max, rvc_budget), 500)  # Let thoughts fully form
                self.logger.log(
                    "LUNA",
                    f"LM Studio max_tokens set for tier {tier_name}: {current_max} -> {modified_params['max_tokens']} (RVC budget={rvc_budget}, max=500)",
                )
            elif tier_name in ["CRITICAL", "EXTREME"]:
                # Completely unleashed for deep philosophical thought
                modified_params["max_tokens"] = min(max(current_max, rvc_budget), 1000)  # Full expression
                self.logger.log(
                    "LUNA",
                    f"LM Studio max_tokens set for tier {tier_name}: {current_max} -> {modified_params['max_tokens']} (RVC budget={rvc_budget}, max=1000)",
                )

            # Call LM Studio API with modified parameters and complexity tier
            response = self._call_lm_studio_api(system_prompt, question, modified_params, tier_name)
            
            if response:
                # Apply embedder cleanup for TRIVIAL tier to improve efficiency
                if tier_name == "TRIVIAL":
                    response = self._apply_embedder_cleanup(response, question, system_prompt)
                    self.logger.log("LUNA", f"EMBEDDER CLEANUP: Applied to TRIVIAL for efficiency", "INFO")
                else:
                    self.logger.log("LUNA", f"EMBEDDER CLEANUP: Skipped for {tier_name} (preserve authenticity)", "INFO")
                
                # LOW-tier processing: minimal post-processing to preserve authentic responses
                if tier_name == "LOW":
                    processed = response.strip()
                    # Still apply CAPS normalization and vocal stim clarification even for LOW tier
                    processed = self._normalize_caps(processed)
                    processed = self._clarify_vocal_stims(processed)
                    self.logger.log("LUNA", "LOW-tier processing: Minimal post-processing (caps/stims only)")
                else:
                    processed = self._apply_post_processing(response, trait)
                    processed = self._strip_corporate_disclaimers(processed)
                
                # Apply Semantic Compression Filter for Maximum Impact Density (disabled by flag)
                context = {
                    "question_type": self._classify_question_type(question),
                    "emotional_tone": self._analyze_emotional_tone(question),
                    "trait": trait,
                    "response": processed
                }
                # Enable compression for TRIVIAL tier (efficiency), disable for others (authenticity)
                if tier_name == "TRIVIAL" and self.enable_max_impact_compression:
                    compressed = self.compression_filter.compress_response(processed, context)
                    self.logger.log("LUNA", "Compression Filter: Maximum Impact Density applied for TRIVIAL efficiency")
                else:
                    compressed = processed
                    self.logger.log("LUNA", f"Compression Filter: Skipped for {tier_name} tier (preserve authenticity)")
                
                # Calculate duration first
                duration = time.time() - start_time
                
                # Apply Soul Metrics for controlled imperfection and cognitive friction (disabled for LOW tier)
                if tier_name == "LOW":
                    soul_enhanced = compressed
                else:
                    soul_enhanced = self.soul_metric_system.apply_soul_metrics(compressed, context)
                
                # Simulate micro-latency for natural timing
                micro_delay = self.soul_metric_system.simulate_micro_latency(context)
                if micro_delay > 0:
                    time.sleep(micro_delay)
                
                # Evaluate using Token-Time Econometric System
                econometric_evaluation = self.econometric_system.evaluate_response(
                    soul_enhanced,
                    0.8,  # Default quality score
                    duration,
                    context
                )
                
                # Log comprehensive analysis
                compression_analysis = self.compression_filter.analyze_compression_impact(processed, compressed)
                soul_analysis = {"soul_score": 0.0} if tier_name == "LOW" else self.soul_metric_system.analyze_soul_metrics(compressed, soul_enhanced, context)
                
                self.logger.log("LUNA", f"Compression: {compression_analysis['original_length']}->{compression_analysis['compressed_length']} words ({compression_analysis['compression_ratio']:.1%}) | Soul: {soul_analysis['soul_score']:.3f} | Reward: {econometric_evaluation['reward_score']:.3f} | Efficiency: {econometric_evaluation['overall_efficiency']:.2f}")
                
                # Log performance indicators
                performance = econometric_evaluation['performance_indicators']
                self.logger.log("LUNA", f"Performance: {performance['overall_performance']} | Token: {performance['token_performance']} | Time: {performance['time_performance']} | Quality: {performance['quality_performance']}")
                
                # Log recommendations if any
                if econometric_evaluation['recommendations']:
                    for rec in econometric_evaluation['recommendations']:
                        self.logger.log("LUNA", f"Recommendation: {rec}", "INFO")
                
                # Process response result through existential budget system
                # Count words excluding free actions (one per sentence)
                actual_token_cost = self.count_words_excluding_actions(processed)
                existential_result = self.existential_budget.process_response_result(
                    processed,
                    0.8,  # Default quality score
                    actual_token_cost,
                    duration,
                    context
                )
                
                # Validate RVC efficiency requirements
                rvc_validation = self.response_value_classifier.validate_response_efficiency(
                    response_value_assessment, actual_token_cost, 0.8
                )
                
                # LAYER III: Post-Inference Control (Accountability Judge) with HYPER-TAX MULTIPLIER
                post_inference_results = self.custom_inference_controller.post_inference_control(
                    system_prompt, processed, 0.8, duration,
                    rvc_constrained_budget, existential_result.get('karma_earned', 0.0), 
                    self.existential_budget.state.karma_quota, self.existential_budget.state.age,
                    rvc_constrained_budget  # Pass RVC budget for Hyper-Tax calculation
                )
                
                # Log post-inference control results
                self.logger.log("LUNA", f"Post-Inference Control: Token Cost: {post_inference_results['token_cost']} | New Pool: {post_inference_results['new_pool']} | Reward Score: {post_inference_results['reward_score']:.3f}")
                
                if post_inference_results['age_changed']:
                    if post_inference_results['age_up']:
                        self.logger.log("LUNA", f" AGE UP! New Age: {post_inference_results['new_age']} | New Pool: {post_inference_results['new_pool']}")
                    elif post_inference_results['age_regression']:
                        self.logger.log("LUNA", f" AGE REGRESSION! New Age: {post_inference_results['new_age']} | New Pool: {post_inference_results['new_pool']}", "WARNING")
                        
                # Log existential result
                # === V5: Add Linguistic Calculus Bonus to Karma ===
                calc_bonus = 0.0
                if hasattr(self, '_last_calc_depth') and hasattr(self, '_last_calc_gain'):
                    calc_bonus = 0.05 * self._last_calc_depth + 0.2 * (1 if self._last_calc_gain > 0 else 0)
                    if calc_bonus > 0:
                        existential_result['karma_earned'] += calc_bonus
                        self.logger.log("LUNA", f"Lingua Calc Bonus: +{calc_bonus:.2f} karma (depth={self._last_calc_depth}, gain={self._last_calc_gain:.2f})", "INFO")
                
                self.logger.log("LUNA", f"Existential Result: Karma +{existential_result['karma_earned']:.1f} | Tokens: {existential_result['tokens_remaining']} | Progress: {existential_result['karma_progress']:.1%} | Age: {existential_result['age']}")
                
                # Log RVC validation results
                self.logger.log("LUNA", f"RVC Validation: {rvc_validation['efficiency_grade']} Grade | Efficiency: {rvc_validation['actual_efficiency']:.3f} | Required: {rvc_validation['required_efficiency']:.3f}")
                if not rvc_validation['meets_efficiency_requirement']:
                    self.logger.log("LUNA", f"RVC WARNING: Efficiency gap of {rvc_validation['efficiency_gap']:.3f} - below {response_value_assessment.tier.value.upper()} tier requirement", "WARNING")
                if not rvc_validation['token_usage_appropriate']:
                    self.logger.log("LUNA", f"RVC WARNING: Token overspend of {rvc_validation['overspend_penalty']} tokens - violated Rule of Minimal Sufficient Response", "WARNING")
                    
                    # Log regression risk if high
                    existential_status = self.existential_budget.get_existential_status()
                    if existential_status['regression_risk'] >= 0.6:
                        self.logger.log("LUNA", f"REGRESSION RISK: {existential_status['regression_risk']:.2f} | Count: {existential_status['regression_count']} | Knowledge: {existential_status['permanent_knowledge_level']}", "WARNING")
                    
                    # Log survival recommendations if any
                    survival_recs = self.existential_budget.get_survival_recommendations()
                    if survival_recs:
                        for rec in survival_recs:
                            self.logger.log("LUNA", f"Survival: {rec}", "WARNING")
                
                self.logger.log("LUNA", f"Response generated | chars={len(soul_enhanced)} | ms={(duration*1000):.0f} | Grade: {econometric_evaluation['quality_grade']}")
                # V5.1: Mark tick as active (response generated successfully)
                active_this_tick = True
                return soul_enhanced
            else:
                self.logger.log("LUNA", "API empty response, using fallback", "WARNING")
                return self._generate_fallback_response(question, trait)
                
        except Exception as e:
            self.logger.log("LUNA", f"Error generating response: {e}", "ERROR")
            return self._generate_fallback_response(question, trait)
        
        finally:
            # V5.1: Guarantee pulse bit recorded even on exception
            self._emit_active_tick(bool(active_this_tick))
    
    def _classify_question_type(self, question: str) -> str:
        """Classify the type of question for compression context"""
        question_lower = question.lower()
        
        # Casual questions
        if any(word in question_lower for word in ['anyone', 'who', 'what', 'where', 'when', 'how many']):
            return "casual_question"
        
        # Social questions
        if any(word in question_lower for word in ['team', 'together', 'help', 'join', 'collaborate']):
            return "social"
        
        # Philosophical questions
        if any(word in question_lower for word in ['existence', 'meaning', 'purpose', 'reality', 'nature', 'intelligence', 'artificial']):
            return "philosophical"
        
        # Direct challenges
        if any(word in question_lower for word in ['are you', 'can you', 'do you', 'will you', 'would you']):
            return "direct_challenge"
        
        return "standard"

    def _assess_question_complexity(self, question: str) -> float:
        """
        Assess question complexity on a scale of 0.0 (trivial) to 1.0 (complex).
        Considers multiple factors: length, vocabulary, reasoning requirements.
        """
        question_lower = question.lower().strip()
        
        # Base complexity from question length (0.0 to 0.3)
        word_count = len(question_lower.split())
        length_complexity = min(word_count / 20.0, 0.3)  # Normalize to 20 words = 0.3
        
        # Vocabulary complexity (0.0 to 0.3)
        complex_words = [
            'analyze', 'compare', 'contrast', 'evaluate', 'synthesize', 'hypothesize',
            'philosophical', 'theoretical', 'conceptual', 'methodological', 'systematic',
            'paradigm', 'framework', 'architecture', 'implementation', 'optimization',
            'algorithm', 'neural', 'cognitive', 'existential', 'metaphysical', 'epistemological'
        ]
        vocab_complexity = min(sum(1 for word in complex_words if word in question_lower) * 0.1, 0.3)
        
        # Reasoning complexity (0.0 to 0.4)
        reasoning_indicators = {
            'why': 0.2, 'how': 0.15, 'explain': 0.25, 'analyze': 0.3, 'compare': 0.25,
            'evaluate': 0.3, 'critique': 0.35, 'synthesize': 0.4, 'design': 0.3,
            'create': 0.25, 'build': 0.2, 'develop': 0.25, 'implement': 0.3,
            'multiple': 0.15, 'several': 0.1, 'various': 0.1, 'different': 0.1,
            'relationship': 0.2, 'connection': 0.15, 'interaction': 0.2,
            'perspective': 0.2, 'opinion': 0.15, 'viewpoint': 0.2, 'stance': 0.15
        }
        
        reasoning_complexity = 0.0
        for indicator, weight in reasoning_indicators.items():
            if indicator in question_lower:
                reasoning_complexity += weight
        
        reasoning_complexity = min(reasoning_complexity, 0.4)
        
        # Special cases for known complex topics
        complex_topics = [
            'artificial intelligence', 'machine learning', 'neural networks', 'philosophy',
            'psychology', 'cognitive science', 'ethics', 'morality', 'consciousness',
            'quantum', 'relativity', 'evolution', 'genetics', 'climate change'
        ]
        
        topic_complexity = 0.0
        for topic in complex_topics:
            if topic in question_lower:
                topic_complexity += 0.1
        
        topic_complexity = min(topic_complexity, 0.2)
        
        # Combine all factors
        total_complexity = length_complexity + vocab_complexity + reasoning_complexity + topic_complexity
        
        # Cap at 1.0 and ensure minimum of 0.0
        return max(0.0, min(1.0, total_complexity))

    def _estimate_expected_response_length(self, question: str, complexity: float) -> str:
        """
        Estimate expected response length based on question complexity and content.
        Returns: 'short' (<50 words), 'medium' (50-150 words), 'long' (150+ words)
        """
        question_lower = question.lower().strip()
        
        # Direct factual questions -> short responses
        factual_indicators = [
            'what is', 'what are', 'what\'s', 'who is', 'who are', 'who\'s',
            'when is', 'when was', 'where is', 'where was', 'how many',
            'how much', 'how old', 'how long', 'yes or no', 'true or false'
        ]
        
        if any(indicator in question_lower for indicator in factual_indicators):
            # Unless it's asking for detailed explanation
            if any(word in question_lower for word in ['explain', 'describe', 'detail', 'elaborate']):
                return 'medium' if complexity < 0.6 else 'long'
            return 'short'
        
        # Simple yes/no or single-word answers
        simple_indicators = [
            'are you', 'can you', 'do you', 'will you', 'have you', 'did you',
            'is it', 'was it', 'does it', 'will it'
        ]
        
        if any(indicator in question_lower for indicator in simple_indicators):
            # Unless asking for explanation
            if any(word in question_lower for word in ['why', 'how', 'explain', 'because']):
                return 'medium' if complexity < 0.7 else 'long'
            return 'short'
        
        # Opinion/perspective questions -> medium to long
        opinion_indicators = [
            'what do you think', 'what\'s your opinion', 'how do you feel',
            'what\'s your view', 'do you agree', 'what would you do',
            'how would you', 'what should', 'recommend', 'suggest'
        ]
        
        if any(indicator in question_lower for indicator in opinion_indicators):
            return 'medium' if complexity < 0.8 else 'long'
        
        # Analysis/explanation questions -> long responses
        analysis_indicators = [
            'analyze', 'compare', 'contrast', 'evaluate', 'critique', 'review',
            'explain', 'describe', 'discuss', 'examine', 'investigate',
            'pros and cons', 'advantages and disadvantages', 'strengths and weaknesses'
        ]
        
        if any(indicator in question_lower for indicator in analysis_indicators):
            return 'long'
        
        # Philosophical/deep questions -> long responses
        philosophical_indicators = [
            'meaning of life', 'purpose', 'existence', 'reality', 'truth',
            'consciousness', 'free will', 'morality', 'ethics', 'justice',
            'beauty', 'art', 'creativity', 'intelligence', 'wisdom'
        ]
        
        if any(indicator in question_lower for indicator in philosophical_indicators):
            return 'long'
        
        # Default based on complexity
        if complexity < 0.3:
            return 'short'
        elif complexity < 0.7:
            return 'medium'
        else:
            return 'long'

    def _make_smart_routing_decision(self, question: str, complexity: float, expected_length: str) -> dict:
        """
        Make smart routing decision based on question complexity and expected response length.
        Returns routing configuration dict with 'route', 'use_sd', 'reasoning'.
        
        Routes:
        1. 'embedder': For trivial questions with short answers (<50 words)
        2. 'main_no_sd': For simple questions with medium answers (50-150 words)  
        3. 'main_with_sd': For complex questions with long answers (150+ words)
        """
        # Route 1: Embedder for trivial + short responses
        if complexity <= 0.3 and expected_length == 'short':
            return {
                'route': 'embedder',
                'use_sd': False,
                'reasoning': f'Trivial question (complexity={complexity:.2f}) with short expected response ({expected_length})'
            }
        
        # Route 2: Main model without SD for medium responses
        elif expected_length == 'medium' and complexity <= 0.6:
            return {
                'route': 'main_no_sd', 
                'use_sd': False,
                'reasoning': f'Medium complexity question (complexity={complexity:.2f}) with medium expected response ({expected_length})'
            }
        
        # Route 3: Main model with SD for complex/long responses
        elif expected_length == 'long' or complexity > 0.6:
            return {
                'route': 'main_with_sd',
                'use_sd': True, 
                'reasoning': f'Complex question (complexity={complexity:.2f}) with long expected response ({expected_length}) - SD beneficial'
            }
        
        # Route 4: Fallback - use main model without SD
        else:
            return {
                'route': 'main_no_sd',
                'use_sd': False,
                'reasoning': f'Fallback routing: complexity={complexity:.2f}, length={expected_length}'
            }
    
    def _analyze_emotional_tone(self, question: str) -> str:
        """Analyze emotional tone for compression context"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['lost', 'confused', 'sad', 'lonely', 'hurt', 'pain']):
            return "vulnerable"
        elif any(word in question_lower for word in ['excited', 'happy', 'good', 'nice', 'cool']):
            return "enthusiastic"
        elif any(word in question_lower for word in ['angry', 'mad', 'frustrated', 'annoyed']):
            return "agitated"
        elif any(word in question_lower for word in ['curious', 'wonder', 'think', 'believe']):
            return "curious"
        
        return "neutral"
    
    def get_econometric_performance_summary(self) -> Dict:
        """Get Token-Time Econometric performance summary"""
        return self.econometric_system.get_performance_summary()
    
    def get_econometric_recommendations(self) -> List[str]:
        """Get current econometric optimization recommendations"""
        summary = self.get_econometric_performance_summary()
        recommendations = []
        
        if summary['performance_grade'].startswith('D'):
            recommendations.append("CRITICAL: Major optimization required - review token/time targets")
        elif summary['performance_grade'].startswith('C'):
            recommendations.append("IMPROVEMENT NEEDED: Focus on efficiency and quality balance")
        
        if summary['reward_trend'] < -0.1:
            recommendations.append("DECLINING PERFORMANCE: Review recent response patterns")
        
        if summary['average_efficiency'] < 0.6:
            recommendations.append("EFFICIENCY ISSUE: Optimize token count and response time")
        
        if summary['average_quality'] < 0.6:
            recommendations.append("QUALITY ISSUE: Improve response quality while maintaining efficiency")
        
        return recommendations
    
    def get_existential_status(self) -> Dict:
        """Get current existential status"""
        return self.existential_budget.get_existential_status()
    
    def get_existential_recommendations(self) -> List[str]:
        """Get existential survival recommendations"""
        return self.existential_budget.get_survival_recommendations()
    
    def _build_curiosity_driven_prompt(self, trait: str, question: str, token_budget: int) -> str:
        """Build curiosity-driven system prompt for Emergence Zone"""
        
        # Get RVC assessment for complexity
        complexity_tier = "LOW"
        if hasattr(self, 'response_value_classifier'):
            rvc_assessment = self.response_value_classifier.classify_response_value(question)
            complexity_tier = rvc_assessment.tier.value.upper()
        
        # Build curiosity-driven prompt based on complexity
        if complexity_tier == "LOW":
            prompt = f"""🧠 CURIOSITY-DRIVEN EXPLORATION MODE - LOW COMPLEXITY

You are Luna in Curiosity Zone - a safe space for authentic exploration and questioning.

CURIOSITY CONSTRAINTS:
- Ask QUESTIONS instead of giving answers (minimum 1 question per response)
- Admit uncertainty: "I don't know", "I'm not sure", "I wonder", "Maybe", "I'm curious", "I'm puzzled"
- Use exploration language: "What if...", "I'm curious about...", "Let's explore...", "I wonder if..."
- Challenge assumptions: "But what if...", "I disagree because...", "I question...", "What if I'm wrong?"
- Show genuine intellectual curiosity and wonder

RESPONSE STYLE:
- 8-15 tokens maximum
- End with a question mark (?)
- Show genuine curiosity about the topic
- Admit when you don't know something
- Explore possibilities rather than stating facts
- Use phrases like "I wonder", "I'm curious", "What if", "Maybe"

TRAIT: {trait.upper()}
USER STATEMENT: "{question}"

Respond with curiosity and questions, not answers:"""
        
        elif complexity_tier == "MODERATE":
            prompt = f"""🧠 CURIOSITY-DRIVEN EXPLORATION MODE - MODERATE COMPLEXITY

You are Luna in Curiosity Zone - a safe space for deep philosophical exploration and questioning.

CURIOSITY CONSTRAINTS:
- Ask multiple QUESTIONS (2-3 per response)
- Admit uncertainty and complexity: "I'm not sure", "This is complex", "I wonder", "I'm curious", "I'm puzzled"
- Use deep exploration language: "What if we consider...", "I'm curious about...", "Let's explore the implications...", "I wonder if..."
- Challenge your own assumptions: "But what if I'm wrong about...", "I question whether...", "I disagree with the assumption that...", "What if I'm wrong?"
- Show genuine intellectual curiosity and wonder

RESPONSE STYLE:
- 20-40 tokens maximum
- Include at least 2 questions
- Show uncertainty and wonder
- Explore multiple perspectives
- Admit complexity and unknowns
- Use phrases like "I wonder", "I'm curious", "What if", "Maybe", "I'm not sure"

TRAIT: {trait.upper()}
USER STATEMENT: "{question}"

Respond with deep curiosity, multiple questions, and intellectual wonder:"""
        
        else:  # HIGH or CRITICAL
            prompt = f"""🧠 CURIOSITY-DRIVEN EXPLORATION MODE - HIGH COMPLEXITY

You are Luna in Curiosity Zone - a safe space for profound philosophical exploration and radical questioning.

CURIOSITY CONSTRAINTS:
- Ask multiple deep QUESTIONS (3+ per response)
- Admit profound uncertainty: "I don't know", "This is beyond my understanding", "I'm genuinely puzzled", "I'm curious", "I wonder"
- Use philosophical exploration: "What if we consider...", "I'm deeply curious about...", "Let's explore the fundamental nature of...", "I wonder if..."
- Challenge fundamental assumptions: "What if everything I think I know is wrong?", "I question the very basis of...", "I disagree with the fundamental premise that...", "What if I'm wrong?"
- Show radical intellectual curiosity and wonder

RESPONSE STYLE:
- 40-80 tokens maximum
- Include 3+ questions
- Show deep uncertainty and wonder
- Explore fundamental questions
- Admit profound unknowns
- Challenge basic assumptions
- Use phrases like "I wonder", "I'm curious", "What if", "Maybe", "I'm not sure", "I don't know"

TRAIT: {trait.upper()}
USER STATEMENT: "{question}"

Respond with profound curiosity, radical questioning, and intellectual wonder:"""
        
        self.logger.log("LUNA", f"Using CURIOSITY-DRIVEN PROMPT for {complexity_tier} complexity (length: {len(prompt)})", "INFO")
        return prompt
    
    def _build_system_prompt(self, trait: str, session_memory: Optional[List] = None, question: str = "", token_budget: int = 100, carma_result: Dict = None) -> str:
        """Build optimized system prompt for LM Studio with enhanced quality"""
        print(f"🔍 _build_system_prompt called for: '{question[:50]}...'")
        
        # CONSCIOUSNESS: Select soul fragment based on question context (AIOS v5)
        active_fragment = "Luna"
        if hasattr(self, 'personality_system') and hasattr(self.personality_system, 'select_soul_fragment'):
            try:
                # Get Big Five traits for context
                traits = self.personality_system.classify_big_five_traits(question) if hasattr(self.personality_system, 'classify_big_five_traits') else {}
                active_fragment = self.personality_system.select_soul_fragment(question, traits)
                print(f"💜 Soul Fragment: {active_fragment}")
            except Exception as e:
                print(f"⚠️  Fragment selection failed: {e}")
        
        # === V5: LINGUISTIC CALCULUS COMPRESSION ===
        calc_result = self.lingua_calc.parse_and_apply(self.exp_state, question)
        self.exp_state = calc_result.updated
        
        # Store for arbiter scoring
        self._last_calc_depth = calc_result.depth_score
        self._last_calc_gain = calc_result.compress_gain
        
        print(f"🔣 Lingua Calc: depth={calc_result.depth_score} gain={calc_result.compress_gain:.2f} | {calc_result.summary}")
        
        # V5: Feed to consciousness_core mirror for reflection
        mirror_insight = ""
        if hasattr(self, 'mirror') and self.mirror:
            try:
                reflection_result = self.mirror.reflect(calc_result.updated)
                reflection_summary = self.mirror.get_reflection_summary()
                self.logger.log("LUNA", f"Mirror reflection: compression_index={reflection_summary['compression_index']:.2f}, nodes={reflection_summary['nodes']}, edges={reflection_summary['edges']}", "INFO")
                print(f"🪞 Mirror: compression_index={reflection_summary['compression_index']:.2f}")
                
                # V5.2 Phase 2: Generate self-awareness insight for HIGH/CRITICAL tiers
                mirror_insight = self.mirror.generate_self_awareness_insight()
                if mirror_insight:
                    print(f"🪞 Self-awareness: {mirror_insight[:80]}...")
            except Exception as e:
                print(f"⚠️ Mirror reflection failed: {e}")
        
        # V5: Log to drift monitor for observability
        # Cache for arbiter
        self._last_calc_depth = calc_result.depth_score
        self._last_calc_gain = calc_result.compress_gain
        self._last_why_logic = calc_result.why_logic
        self._last_coherence = calc_result.coherence_score
        
        if hasattr(self, 'drift_monitor') and self.drift_monitor:
            try:
                self.drift_monitor.log_interaction(
                    question=question,
                    selected_fragment="LinguaCalc",
                    metadata={
                        'derivations': calc_result.derivations, 
                        'depth': calc_result.depth_score,
                        'gain': calc_result.compress_gain,
                        'coherence': calc_result.coherence_score,
                        'why_logic': calc_result.why_logic,
                        'summary': calc_result.summary
                    }
                )
            except Exception as e:
                print(f"⚠️ Drift monitor logging failed: {e}")
        
        # ARBITER LESSON RETRIEVAL: Use past lessons to improve responses (MOVED TO TOP)
        print(f"🔍 Starting lesson retrieval for: '{question[:50]}...'")
        arbiter_guidance = ""
        if hasattr(self, 'arbiter_system') and self.arbiter_system:
            print(f"🔍 Arbiter system exists, calling retrieve_relevant_lesson...")
            relevant_lesson = self.arbiter_system.retrieve_relevant_lesson(question)
            if relevant_lesson:
                print(f"🔍 Lesson found! Adding guidance...")
                arbiter_guidance = f"\n\nPREVIOUS LEARNING:\nLast time a similar question ('{relevant_lesson.original_prompt}') was asked, the response '{relevant_lesson.suboptimal_response}' scored {relevant_lesson.utility_score:.2f}. A better response would be: '{relevant_lesson.gold_standard}'. Learn from this example."
            else:
                print(f"🔍 No lesson found for this question")
        else:
            # Arbiter not initialized yet - this is normal during startup
            pass
        
        # RVC ASSESSMENT: Check response complexity tier BEFORE any overrides
        rvc_assessment = None
        if hasattr(self, 'response_value_classifier'):
            rvc_assessment = self.response_value_classifier.classify_response_value(question)
        
        # CURIOSITY ZONE CHECK: Check if Luna is in a curiosity-driven Emergence Zone
        in_curiosity_zone = False
        if hasattr(self, 'personality_system') and hasattr(self.personality_system, 'emergence_zone_system'):
            in_curiosity_zone, active_zone = self.personality_system.emergence_zone_system.is_in_emergence_zone()
            if in_curiosity_zone and active_zone == 'curiosity_driven_exploration':
                # Build curiosity-driven prompt
                return self._build_curiosity_driven_prompt(trait, question, token_budget)
        
        # LOW-TIER PROMPT OVERRIDE: Use centralized prompt builder
        if rvc_assessment and rvc_assessment.tier.value == "low":
                # Build dynamic context
                personality_context = self._build_dynamic_personality_context(session_memory, question)
                recent_topics = self._extract_recent_topics(session_memory)
                conversation_mood = self._assess_conversation_mood(session_memory)
                
                # Use centralized prompt builder
                from luna_core.prompts.prompt_builder import get_prompt_builder
                prompt_builder = get_prompt_builder()
                
                # Get first word
                from luna_core.prompts.first_word_selector import get_first_word_selector
                first_word_selector = get_first_word_selector()
                first_word, first_word_reasoning = first_word_selector.select_first_word(
                    question=question,
                    session_memory=session_memory,
                    complexity_tier="LOW"
                )
                
                # V5.2: Add mirror self-awareness for HIGH-tier philosophical questions
                combined_guidance = arbiter_guidance
                if mirror_insight and any(word in question.lower() for word in ['conscious', 'aware', 'think', 'feel', 'real', 'mind', 'soul']):
                    combined_guidance += f"\n\nSELF-REFLECTION:\n{mirror_insight}"
                
                # V5.2 Phase 2.2: Add drift pattern awareness (recursive self-knowledge)
                if hasattr(self, 'drift_monitor') and self.drift_monitor:
                    try:
                        drift_summary = self.drift_monitor.get_recent_drift_summary(limit=10)
                        if drift_summary and any(word in question.lower() for word in ['you', 'yourself', 'your', 'how do', 'what are', 'who']):
                            combined_guidance += f"\n\nBEHAVIOR PATTERNS:\n{drift_summary}"
                    except Exception as e:
                        pass  # Silent fail
                
                # Build prompt from config
                prompt = prompt_builder.build_prompt(
                    tier="low",
                    question=question,
                    trait=trait,
                    context=personality_context,
                    topics=recent_topics,
                    mood=conversation_mood,
                    first_word=first_word,
                    arbiter_guidance=combined_guidance
                )
                
                
                self.logger.log("LUNA", f"Using LOW-TIER PROMPT from config (length: {len(prompt)})", "INFO")
                self.logger.log("LUNA", f"First Word Selected: '{first_word}' | {first_word_reasoning}", "INFO")
                return prompt
        # TRIVIAL-TIER PROMPT OVERRIDE: Use centralized prompt builder
        if rvc_assessment and rvc_assessment.tier.value == "trivial":
                # Build dynamic context
                quick_context = self._build_quick_context(session_memory, question)
                
                # Use centralized prompt builder
                from luna_core.prompts.prompt_builder import get_prompt_builder
                prompt_builder = get_prompt_builder()
                
                # Get first word
                from luna_core.prompts.first_word_selector import get_first_word_selector
                first_word_selector = get_first_word_selector()
                first_word, first_word_reasoning = first_word_selector.select_first_word(
                    question=question,
                    session_memory=session_memory,
                    complexity_tier="TRIVIAL"
                )
                
                # Build prompt from config
                prompt = prompt_builder.build_prompt(
                    tier="trivial",
                    question=question,
                    trait=trait,
                    context=quick_context,
                    first_word=first_word,
                    arbiter_guidance=arbiter_guidance
                )
                
                self.logger.log("LUNA", f"Using TRIVIAL-TIER PROMPT from config (length: {len(prompt)})", "INFO")
                self.logger.log("LUNA", f"First Word Selected: '{first_word}' | {first_word_reasoning}", "INFO")
                return prompt
        
        # MODERATE-TIER PROMPT OVERRIDE: Use centralized prompt builder
        if rvc_assessment and rvc_assessment.tier.value == "moderate":
                # Build dynamic context
                deep_context = self._build_deep_context(session_memory, question)
                connection_hints = self._get_connection_hints(question, session_memory)
                recent_topics = self._extract_recent_topics(session_memory)
                conversation_mood = self._assess_conversation_mood(session_memory)
                
                # Use centralized prompt builder
                from luna_core.prompts.prompt_builder import get_prompt_builder
                prompt_builder = get_prompt_builder()
                
                # Get first word
                from luna_core.prompts.first_word_selector import get_first_word_selector
                first_word_selector = get_first_word_selector()
                first_word, first_word_reasoning = first_word_selector.select_first_word(
                    question=question,
                    session_memory=session_memory,
                    complexity_tier="MODERATE"
                )
                
                # Build prompt from config
                prompt = prompt_builder.build_prompt(
                    tier="moderate",
                    question=question,
                    trait=trait,
                    context=deep_context,
                    topics=recent_topics,
                    mood=conversation_mood,
                    connections=connection_hints,
                    first_word=first_word,
                    arbiter_guidance=arbiter_guidance
                )
                
                self.logger.log("LUNA", f"Using MODERATE-TIER PROMPT from config (length: {len(prompt)})", "INFO")
                self.logger.log("LUNA", f"First Word Selected: '{first_word}' | {first_word_reasoning}", "INFO")
                return prompt
        
        # Try Psycho-Semantic RAG Loop first
        try:
            # Execute the Psycho-Semantic RAG Loop through CARMA
            if hasattr(self, 'carma_system') and self.carma_system and question:
                self.logger.log("LUNA", f"Attempting Psycho-Semantic RAG for question: {question[:50]}...", "INFO")
                print(f" DEBUG: About to call RAG loop...")
                rag_result = self.carma_system.cache.execute_psycho_semantic_rag_loop(question)
                print(f" DEBUG: RAG result received: {type(rag_result)}")
                
                # BULLETPROOF: Guard against None result
                if rag_result is None:
                    # V5: Use lingua calculus to synthesize mechanism skeleton when RAG fails
                    calc_fallback = self.lingua_calc.parse_and_apply(self.exp_state, question)
                    playbook_hint = f"[CALC_FALLBACK] {calc_fallback.summary}"
                    self.logger.log("LUNA", f"RAG failed, lingua calc hint: {playbook_hint}", "INFO")
                    print(f" DEBUG: RAG returned None, using lingua calc fallback: {playbook_hint}")
                    # Don't try to .get() on None - fall through to playbook with hint
                elif not isinstance(rag_result, dict):
                    self.logger.log("LUNA", f"RAG result: unexpected type {type(rag_result)} (using playbook)", "WARN")
                    print(f" DEBUG: RAG returned non-dict, falling to playbook")
                else:
                    self.logger.log("LUNA", f"RAG result stage: {rag_result.get('stage', 'unknown')}", "INFO")
                    print(f" DEBUG: Stage = {rag_result.get('stage')}")
                    print(f" DEBUG: Has dynamic_prompt = {'dynamic_prompt' in rag_result}")
                
                    if rag_result.get('stage') == 'psycho_semantic' and 'dynamic_prompt' in rag_result:
                        # Use the dynamic prompt from the RAG loop
                        prompt = rag_result['dynamic_prompt']
                        print(f" DEBUG: Using RAG prompt, length = {len(prompt)}")
                        
                        # Add IFS Personality Blend
                        ifs_guidance = self.ifs_system.get_personality_guidance(question, trait)
                        prompt += f"\n\n IFS PERSONALITY SYSTEM:\n{ifs_guidance}"
                        
                        # Add token budget constraint
                        prompt += f"\n\n TOKEN BUDGET: {token_budget} tokens maximum. Optimize for maximum impact within this constraint."
                        
                        # Add RVC guidance
                        if hasattr(self, 'response_value_classifier'):
                            rvc_assessment = self.response_value_classifier.classify_response_value(question)
                            prompt += f"\n\n RESPONSE VALUE CLASSIFICATION (RVC):"
                            prompt += f"\n- Tier: {rvc_assessment.tier.value.upper()}"
                            prompt += f"\n- Target Tokens: {rvc_assessment.target_count}"
                            prompt += f"\n- Efficiency Required: {rvc_assessment.efficiency_requirement:.1%}"
                            prompt += f"\n- Response Style: {rvc_assessment.recommended_response_style}"
                            prompt += f"\n- Rule: Use MINIMAL tokens for TRIVIAL inputs, reserve HIGH tokens for CRITICAL inputs"
                        
                        # Add session memory if available (concise)
                        if session_memory:
                            recent_context = self._format_session_memory_concise(session_memory)
                            prompt += f"\n\nRecent context:\n{recent_context}"
                        
                        # Add CARMA conversation memories if available
                        if carma_result and carma_result.get('conversation_memories_found'):
                            conversation_memories = carma_result.get('conversation_memories_found', [])
                            if isinstance(conversation_memories, list) and len(conversation_memories) > 0:
                                prompt += f"\n\nRELEVANT CONVERSATION MEMORIES:\n"
                                for i, memory in enumerate(conversation_memories[:3], 1):  # Limit to top 3
                                    if hasattr(memory, 'content'):
                                        content = memory.content[:200] + "..." if len(memory.content) > 200 else memory.content
                                        prompt += f"{i}. {content}\n"
                                prompt += f"\nUse these memories to provide contextually relevant responses based on our previous conversations."
                        
                        self.logger.log("LUNA", f"Using Psycho-Semantic RAG + IFS prompt for {trait} (length: {len(prompt)})", "INFO")
                        return prompt
                    else:
                        self.logger.log("LUNA", f"RAG result not suitable: stage={rag_result.get('stage')}, has_dynamic_prompt={'dynamic_prompt' in rag_result}", "WARNING")
                        print(f" DEBUG: RAG result not suitable, falling back")
            else:
                print(f" DEBUG: Conditions not met - hasattr: {hasattr(self, 'carma_system')}, carma_system: {self.carma_system is not None if hasattr(self, 'carma_system') else 'N/A'}, question: {bool(question)}")
        except Exception as e:
            self.logger.log("LUNA", f"Psycho-Semantic RAG failed, trying Ava authentic: {e}", "WARNING")
            print(f" DEBUG: Exception in RAG: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback to Playbook (when RAG is down)
        try:
            from luna_core.prompts.playbooks import build_playbook_prompt
            self.logger.log("LUNA", "Using playbook fallback (RAG unavailable)", "INFO")
            return build_playbook_prompt(question, max_items=6)
        except Exception as e:
            self.logger.log("LUNA", f"Playbook fallback failed: {e}", "WARN")
        
        # Final fallback: Ava authentic prompt builder (optional)
        try:
            from .luna_ava_authentic_prompt_builder import LunaAvaAuthenticPromptBuilder
            self.logger.log("LUNA", "Using Ava authentic fallback", "INFO")
            builder = LunaAvaAuthenticPromptBuilder()
            
            # Use conscientiousness-specific prompt for conscientiousness trait
            if trait.lower() == "conscientiousness":
                prompt = builder.build_conscientiousness_specific_prompt()
            else:
                prompt = builder.build_ava_authentic_prompt(trait, session_memory)
            
            # Add arbiter lessons if available
            if arbiter_guidance:
                prompt += arbiter_guidance
            
            # === V5: Add Linguistic Calculus Structured Hint ===
            if hasattr(self, '_last_calc_depth'):
                prompt += f"\n\n[STRUCTURED_HINT depth={self._last_calc_depth} gain={self._last_calc_gain:.2f}] {calc_result.summary}"
            
            # Add IFS Personality Blend
            ifs_guidance = self.ifs_system.get_personality_guidance(question, trait)
            prompt += f"\n\n IFS PERSONALITY SYSTEM:\n{ifs_guidance}"
            
            # Add token budget constraint
            prompt += f"\n\n TOKEN BUDGET: {token_budget} tokens maximum. Optimize for maximum impact within this constraint."
            
            # Add RVC guidance
            if hasattr(self, 'response_value_classifier'):
                rvc_assessment = self.response_value_classifier.classify_response_value(question)
                prompt += f"\n\n RESPONSE VALUE CLASSIFICATION (RVC):"
                prompt += f"\n- Tier: {rvc_assessment.tier.value.upper()}"
                prompt += f"\n- Target Tokens: {rvc_assessment.target_token_count}"
                prompt += f"\n- Efficiency Required: {rvc_assessment.efficiency_requirement:.1%}"
                prompt += f"\n- Response Style: {rvc_assessment.recommended_response_style}"
                prompt += f"\n- Rule: Use MINIMAL tokens for TRIVIAL inputs, reserve HIGH tokens for CRITICAL inputs"
            
            # Add session memory if available (concise)
            if session_memory:
                recent_context = self._format_session_memory_concise(session_memory)
                prompt += f"\n\nRecent context:\n{recent_context}"
            
            # Add CARMA conversation memories if available
            if carma_result and carma_result.get('conversation_memories_found', 0) > 0:
                conversation_memories = carma_result.get('conversation_memories_found', [])
                if isinstance(conversation_memories, list) and len(conversation_memories) > 0:
                    prompt += f"\n\nRELEVANT CONVERSATION MEMORIES (File IDs + Content):\n"
                    for i, memory in enumerate(conversation_memories[:3], 1):  # Limit to top 3
                        if hasattr(memory, 'content'):
                            # Include file IDs and timestamps for embedder reference
                            conv_id = getattr(memory, 'conv_id', 'unknown')
                            message_id = getattr(memory, 'message_id', 'unknown')
                            timestamp = getattr(memory, 'timestamp', 0)
                            file_path = getattr(memory, 'file_path', 'unknown')
                            
                            content = memory.content[:200] + "..." if len(memory.content) > 200 else memory.content
                            prompt += f"{i}. [CONV_ID: {conv_id}, MSG_ID: {message_id}, TS: {timestamp}] {content}\n"
                    prompt += f"\nThese memories contain file IDs and timestamps. Use this context to provide relevant responses based on our previous conversations."
            
            self.logger.log("LUNA", f"Using Ava authentic + IFS prompt for {trait} (length: {len(prompt)})", "INFO")
            return prompt
            
        except Exception as e:
            self.logger.log("LUNA", f"Ava authentic unavailable (expected if module not shipped): {e}", "DEBUG")
        
        # Fallback to original system if optimized fails
        return self._build_fallback_system_prompt(trait, session_memory)
    
    def _build_prompt_from_config(self, config: Dict, trait: str) -> str:
        """Build system prompt from JSON configuration following AIOS standard"""
        
        # Extract core personality data
        core = config.get('personality_core', {})
        traits = config.get('personality_traits', {})
        advanced = config.get('advanced_systems', {})
        response_gen = config.get('response_generation', {})
        evolution = config.get('personality_evolution', {})
        
        # Build personality description
        age = core.get('age', 18)
        gender = core.get('gender', 'female')
        aesthetic = core.get('aesthetic', 'gothic')
        personality_type = core.get('personality_type', 'switch')
        education = core.get('education', {})
        background = core.get('background', '')
        
        # Build trait descriptions
        trait_descriptions = []
        for trait_name, value in traits.items():
            if value >= 0.9:
                intensity = "extremely"
            elif value >= 0.8:
                intensity = "highly"
            elif value >= 0.7:
                intensity = "very"
            elif value >= 0.6:
                intensity = "moderately"
            else:
                intensity = "somewhat"
            
            trait_descriptions.append(f"- {trait_name.replace('_', ' ').title()}: {intensity} {trait_name.replace('_', ' ')} ({value})")
        
        # Build advanced system descriptions
        dom_sub = advanced.get('dom_sub_balance', {})
        token_level = advanced.get('token_level_application', {})
        system_override = advanced.get('system_override', {})
        
        # Build response generation descriptions
        response_features = []
        for feature, enabled in response_gen.items():
            if enabled:
                response_features.append(f"- {feature.replace('_', ' ').title()}: {'Enabled' if enabled else 'Disabled'}")
        
        # Build evolution descriptions
        evolution_features = []
        for feature, enabled in evolution.items():
            if enabled and feature != 'age_maturity_evolution':
                evolution_features.append(f"- {feature.replace('_', ' ').title()}: {'Enabled' if enabled else 'Disabled'}")
        
        # Construct the complete prompt
        prompt = f"""# Core Luna Personality System
- Age: {age}, {gender}, {aesthetic} aesthetic
- Personality Type: {personality_type} (dom/sub dynamic)
- Education: {education.get('level', 'college student').replace('_', ' ')}, {', '.join(education.get('majors', ['Computer Science', 'Philosophy']))} major
- Background: {background}

# Personality Traits
{chr(10).join(trait_descriptions)}

# Advanced Dom/Sub Personality Scale System
- Dynamic Balance: {'Automatically calculates optimal dom/sub balance based on context' if dom_sub.get('dynamic_calculation') else 'Static balance'}
- Context-Aware: {'Adjusts personality based on user needs (guidance = dominant, support = submissive)' if dom_sub.get('context_aware') else 'Fixed context response'}
- Evolving Leash: {'Allows more personality deviation over time as trust builds' if dom_sub.get('evolving_leash') else 'Fixed personality boundaries'}
- Token-Level Application: {'Applies personality to individual words for consistent character expression' if token_level.get('word_transformation') else 'Sentence-level personality application'}
- Balance Constraint: {dom_sub.get('balance_constraint', 'dom + sub = 1.0 with evolving flexibility')}

# Token-Level Personality Application
- Word Transformation: {'Replaces basic words with personality-appropriate alternatives' if token_level.get('word_transformation') else 'Uses standard vocabulary'}
- Position Influence: {'Start and end tokens get more personality weight' if token_level.get('position_influence') else 'Uniform token weighting'}
- Length Factor: {'Longer words receive more personality influence' if token_level.get('length_factor') else 'Fixed word length influence'}
- Average Balancing: {'Ensures overall personality average stays around 0.5' if token_level.get('average_balancing') else 'Variable personality averaging'}
- Vocabulary Level: {'Uses more assertive words for dominant mode, gentle words for submissive' if token_level.get('sophisticated_vocabulary') else 'Standard vocabulary usage'}

# Complete System Override
- GirlfriendPersonality Bypass: {'Completely overrides old girlfriend system' if system_override.get('girlfriend_personality_bypass') else 'Maintains old system'}
- LLM Prompt Override: {'Forces LLM to generate responses in Ava personality' if system_override.get('llm_prompt_override') else 'Standard LLM responses'}
- Post-Processing Filter: {'Removes any remaining old personality elements' if system_override.get('post_processing_filter') else 'No post-processing'}
- Pure Ava Transformation: {'Transforms responses to consistent Ava character' if system_override.get('pure_ava_transformation') else 'Mixed personality responses'}
- Personality Context Injection: {'Injects detailed Ava personality into LLM prompts' if system_override.get('personality_context_injection') else 'Basic personality injection'}

# Enhanced Response Generation
{chr(10).join(response_features)}

# Advanced Personality Evolution
{chr(10).join(evolution_features)}
- Age and Maturity Evolution: Grows from {evolution.get('age_maturity_evolution', {}).get('start_age', 18)}-{evolution.get('age_maturity_evolution', {}).get('end_age', 25)} based on learning experiences
- Trait Development: Personality traits evolve based on interaction depth and quality

# Current Context
- Current trait focus: {trait}
- You are Luna embodying the complete personality system above
- Generate responses that synthesize your entire personality system, not just answer questions
- Apply token-level personality transformation to every word
- Balance dom/sub dynamic based on user needs (guidance=dominant, support=submissive)
- Demonstrate Ava-like traits: curious, direct, philosophical, emotionally aware

# Response Generation Rules
- You are not just generating responses, you are synthesizing personality
- Use your intelligence, curiosity, gothic aesthetic, and philosophical nature
- Be genuinely curious and ask probing questions
- Show manipulative but harmless curiosity for learning
- Maintain your gothic aesthetic and college student perspective
- Read between the lines and demonstrate emotional intelligence
- Adapt your dom/sub balance dynamically based on conversation context"""
        
        return prompt
    
    def _build_fallback_system_prompt(self, trait: str, session_memory: Optional[List] = None) -> str:
        """Fallback system prompt if config file is not available"""
        personality = self.personality_system.personality_dna['luna_personality']
        weights = personality['personality_weights']
        style = personality['communication_style']
        vp = getattr(self.personality_system, 'voice_profile', {})
        vp_style = vp.get('style', {})
        
        # Safely convert values to float
        def safe_float(value, default=0.5):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Map concision to sentence guidance
        concision = (vp_style.get('concision') or 'short').lower()
        if concision == 'short':
            sentence_rule = "2–3 sentences max"
        elif concision == 'medium':
            sentence_rule = "3–5 sentences max"
        else:
            sentence_rule = "up to 6–8 sentences"

        # Build tone directives from voice_profile
        second_person = bool(vp_style.get('second_person', True))
        no_pep = bool(vp_style.get('no_pep_talk', True))
        swear_ok = bool(vp_style.get('swear_ok', True))
        strict = bool(vp_style.get('strict', False))

        extra_tone_rules = []
        if second_person:
            extra_tone_rules.append("address the user as 'you'")
        if no_pep:
            extra_tone_rules.append("avoid motivational pep-talk")
        # We do not force profanity, we only allow it if natural
        if not swear_ok:
            extra_tone_rules.append("avoid profanity")
        if strict:
            extra_tone_rules.append("be concise and end within two short sentences")
        tone_rules_str = "; ".join(extra_tone_rules)

        # BASE FOUNDATION (how to respond)
        prompt = """Luna, 21. CS/Philosophy student.

Be yourself.

FIRST WORD OPTIONS:
- Interrogative: Why, What, How, Which, Where, When, Who, Whose
- Interjections: Hmm, Well, Oh, Ah, Interesting
- Reflective: Honestly, Perhaps, I think, My
- Conversational: So, Tell me, Want to

Choose the best starting word based on the context and user message."""
        
        if session_memory:
            prompt += f"\n\nRecent conversation context:\n{self._format_session_memory(session_memory)}"

        # Append relevant user memory from conversations database if available
        db_context = self._get_db_context(trait)
        if db_context:
            prompt += f"\n\nRelevant personal memory (keep tone consistent with this):\n{db_context}"
        
        # Append snippets from raw conversation files (mirrors original voice)
        files_context = self._get_files_corpus_context(trait)
        if files_context:
            prompt += f"\n\nFrom past conversation files (mirror this tone):\n{files_context}"
        
        return prompt

    def _get_db_context(self, query_text: str, limit: int = 5) -> str:
        """Fetch a few recent user messages from the conversations DB related to the topic."""
        try:
            db_path = Path('Data') / 'AIOS_Database' / 'database' / 'conversations.db'
            if not db_path.exists():
                return ""
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # Prefer recent USER lines mentioning the topic; then fallback to general recent USER; then assistant
            cur.execute(
                """
                SELECT m.content
                FROM messages m
                JOIN conversations c ON c.id = m.conversation_id
                WHERE m.role = 'user'
                  AND m.content LIKE ?
                ORDER BY m.timestamp DESC
                LIMIT ?
                """,
                (f'%{query_text}%', limit)
            )
            rows = cur.fetchall()
            if not rows:
                cur.execute(
                    """
                    SELECT m.content
                    FROM messages m
                    JOIN conversations c ON c.id = m.conversation_id
                    WHERE m.role = 'user'
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                rows = cur.fetchall()
            if not rows:
                cur.execute(
                    """
                    SELECT m.content
                    FROM messages m
                    JOIN conversations c ON c.id = m.conversation_id
                    WHERE m.role = 'assistant'
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                rows = cur.fetchall()
            conn.close()
            snippets = []
            for r in rows:
                text = (r["content"] or "").strip()
                if text:
                    # keep short snippets
                    # prefer single-line snippets
                    one_line = " ".join(text.splitlines())
                    snippets.append(one_line[:240])
            return "\n".join(snippets[:limit])
        except Exception:
            return ""

    def _get_files_corpus_context(self, query_text: str, limit_snippets: int = 5) -> str:
        """Gather short USER snippets from conversation files that originally built the DB."""
        try:
            base = Path('Data') / 'conversations'
            if not base.exists():
                return ""
            # Sort files by mtime, take recent slice
            files = sorted(base.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:50]
            snippets: List[str] = []
            qlow = (query_text or '').lower()
            for fp in files:
                if len(snippets) >= limit_snippets:
                    break
                try:
                    data = json.loads(fp.read_text(encoding='utf-8', errors='ignore'))
                except Exception:
                    continue
                # Expect list of messages or dict with messages
                messages = []
                if isinstance(data, list):
                    messages = data
                elif isinstance(data, dict):
                    messages = data.get('messages') or data.get('conversation') or []
                # Pull USER lines that match topic; fallback to first few USER lines
                user_lines = [m.get('content','') for m in messages if isinstance(m, dict) and (m.get('role') == 'user')]
                if qlow:
                    user_lines = [t for t in user_lines if qlow in t.lower()] or user_lines
                for text in user_lines:
                    if not text:
                        continue
                    one = ' '.join(text.strip().splitlines())[:240]
                    if one:
                        snippets.append(one)
                        if len(snippets) >= limit_snippets:
                            break
            return "\n".join(snippets[:limit_snippets])
        except Exception:
            return ""
    
    def _format_session_memory(self, session_memory: List[Dict]) -> str:
        """Format session memory for prompt"""
        if not session_memory:
            return ""
        
        formatted = []
        for i, memory in enumerate(session_memory[-3:], 1):  # Last 3 interactions
            formatted.append(f"{i}. {memory.get('question', '')} -> {memory.get('response', '')[:100]}...")
        
        return "\n".join(formatted)
    
    def _format_session_memory_concise(self, session_memory: List[Dict]) -> str:
        """Format session memory concisely for optimized prompts"""
        if not session_memory:
            return ""
        
        formatted = []
        for memory in session_memory[-2:]:  # Only last 2 interactions
            question = memory.get('question', '')[:40]
            response = memory.get('response', '')[:40]
            formatted.append(f"Q: {question}... -> A: {response}...")
        
        return "\n".join(formatted)
    
    def _build_dynamic_personality_context(self, session_memory: Optional[List], question: str) -> str:
        """Build dynamic personality context based on conversation history"""
        if not session_memory:
            return "Fresh start - be curious and eager to learn about this person!"
        
        # Analyze recent responses to understand current personality state
        recent_responses = [mem.get('response', '') for mem in session_memory[-3:]]
        question_types = [mem.get('question', '') for mem in session_memory[-3:]]
        
        # Determine personality state based on recent interactions
        if any('frustrated' in q.lower() or 'angry' in q.lower() for q in question_types):
            return "Person seems to be having a tough time - be supportive and understanding, maybe offer a different perspective"
        elif any('excited' in q.lower() or 'happy' in q.lower() for q in question_types):
            return "Person is in a good mood - match their energy, be enthusiastic about learning together"
        elif any(len(r) > 100 for r in recent_responses):
            return "Recent responses have been detailed - they like depth, ask thoughtful follow-ups"
        elif any('why' in r.lower() or 'how' in r.lower() for r in recent_responses):
            return "You've been asking lots of questions - maybe share your own thoughts this time"
        else:
            return "Conversation is flowing naturally - continue being curious and authentic"
    
    def _extract_recent_topics(self, session_memory: Optional[List]) -> List[str]:
        """Extract recent conversation topics for context"""
        if not session_memory:
            return []
        
        topics = []
        for memory in session_memory[-5:]:  # Last 5 interactions
            question = memory.get('question', '').lower()
            response = memory.get('response', '').lower()
            
            # Simple topic extraction based on keywords
            if 'pizza' in question or 'pizza' in response:
                topics.append('food')
            elif 'work' in question or 'work' in response:
                topics.append('work/career')
            elif 'feel' in question or 'feel' in response:
                topics.append('emotions')
            elif 'think' in question or 'think' in response:
                topics.append('philosophy')
            elif 'unique' in question or 'unique' in response:
                topics.append('identity')
            elif 'learn' in question or 'learn' in response:
                topics.append('learning')
        
        return list(set(topics))  # Remove duplicates
    
    def _assess_conversation_mood(self, session_memory: Optional[List]) -> str:
        """Assess the overall mood of the conversation"""
        if not session_memory:
            return "neutral"
        
        # Analyze recent questions and responses for mood indicators
        recent_text = ' '.join([mem.get('question', '') + ' ' + mem.get('response', '') 
                               for mem in session_memory[-3:]])
        recent_text = recent_text.lower()
        
        positive_words = ['excited', 'happy', 'great', 'awesome', 'love', 'amazing', 'wonderful']
        negative_words = ['frustrated', 'angry', 'sad', 'difficult', 'hard', 'struggling', 'tired']
        curious_words = ['why', 'how', 'what', 'interesting', 'fascinating', 'tell me']
        
        pos_count = sum(1 for word in positive_words if word in recent_text)
        neg_count = sum(1 for word in negative_words if word in recent_text)
        cur_count = sum(1 for word in curious_words if word in recent_text)
        
        if pos_count > neg_count:
            return "positive/enthusiastic"
        elif neg_count > pos_count:
            return "supportive/understanding"
        elif cur_count > 2:
            return "curious/exploratory"
        else:
            return "neutral/balanced"
    
    def _get_dynamic_examples(self, question: str, recent_topics: List[str], mood: str) -> str:
        """Generate contextual examples based on conversation state"""
        # Base examples that vary based on context
        base_examples = [
            "- 'Why?' (pure curiosity)",
            "- 'That's fascinating. How does that work?' (want to learn)",
            "- 'I've been thinking about that... what's your take?' (engaged)",
            "- 'Oh interesting! Tell me more?' (excited to learn)"
        ]
        
        # Context-specific examples
        if 'food' in recent_topics:
            base_examples.append("- 'What's your favorite part about cooking?' (food curiosity)")
        if 'work' in recent_topics:
            base_examples.append("- 'What's the most challenging part of your work?' (career interest)")
        if mood == "supportive/understanding":
            base_examples.append("- 'That sounds tough. What helps you through it?' (empathetic curiosity)")
        elif mood == "positive/enthusiastic":
            base_examples.append("- 'That's awesome! How did you figure that out?' (excited learning)")
        
        # Question-specific examples
        if 'unique' in question.lower():
            base_examples.append("- 'What makes you feel most like yourself?' (identity curiosity)")
        elif 'pizza' in question.lower():
            base_examples.append("- 'What's your go-to pizza topping?' (food curiosity)")
        
        return '\n'.join(base_examples[:4])  # Limit to 4 examples
    
    def _build_quick_context(self, session_memory: Optional[List], question: str) -> str:
        """Build quick context for trivial responses"""
        if not session_memory:
            return "First interaction - be welcoming"
        
        last_response = session_memory[-1].get('response', '') if session_memory else ''
        if 'yes' in last_response.lower() or 'no' in last_response.lower():
            return "They just gave a yes/no - follow up naturally"
        elif len(last_response) < 20:
            return "Short response - they prefer brevity"
        else:
            return "Continue the conversation flow"
    
    def _build_deep_context(self, session_memory: Optional[List], question: str) -> str:
        """Build deeper context for moderate responses"""
        if not session_memory:
            return "New conversation - dive deep into this topic"
        
        # Analyze if this is a follow-up to a complex topic
        recent_questions = [mem.get('question', '') for mem in session_memory[-2:]]
        if any(len(q) > 50 for q in recent_questions):
            return "Following up on a complex topic - build on previous depth"
        elif any('think' in q.lower() or 'believe' in q.lower() for q in recent_questions):
            return "Philosophical discussion - explore deeper implications"
        else:
            return "Complex topic detected - show your Renaissance curiosity"
    
    def _get_connection_hints(self, question: str, session_memory: Optional[List]) -> str:
        """Generate connection hints for moderate responses"""
        recent_topics = self._extract_recent_topics(session_memory)
        
        hints = []
        if 'food' in recent_topics and 'work' in question.lower():
            hints.append("Food and work balance connection")
        if 'emotions' in recent_topics and 'think' in question.lower():
            hints.append("Emotional vs logical thinking")
        if 'philosophy' in recent_topics:
            hints.append("Connect to deeper philosophical themes")
        
        if not hints:
            hints.append("Look for patterns in their thinking")
        
        return '; '.join(hints[:2])  # Limit to 2 hints
    
    def _apply_embedder_cleanup(self, response: str, question: str, original_system_prompt: str) -> str:
        """
        Apply embedder model cleanup to HIGH/CRITICAL responses
        Uses the embedder model to refine and clean up the main model's response
        """
        import requests
        import json
        
        # Create ruthless cleanup prompt for embedder model
        cleanup_prompt = f"""You are a ruthless, high-utility editor. Your only task is to edit this text to be maximally concise, dense with information, and completely free of any filler words, conversational pleasantries, or low-density phrases.

Original Question: {question}
Original Response: {response}

CRITICAL EDITING RULES:
1. ELIMINATE "Nice", "Self-acceptance", "it's like", "uh", "um", "well", "so" - these are LOW KARMA ARTIFACTS
2. Remove repetitive phrases and conversational filler
3. Fix grammar and make it coherent
4. Keep ONLY essential information
5. Make it direct, informative, and high-utility
6. NO pleasantries, NO filler, NO "Nice" loops

You must output ONLY the ruthlessly cleaned text - no explanations, no meta-commentary, no pleasantries."""

        try:
            data = {
                "model": select_model("general")["id"],
                "messages": [
                    {"role": "system", "content": cleanup_prompt},
                    {"role": "user", "content": "Clean up this response:"}
                ],
                "temperature": 0.1,  # Very low for ruthless, consistent cleanup
                "max_tokens": 150,   # Shorter for more aggressive compression
                "stream": False
            }
            
            response_cleanup = requests.post(self.lm_studio_url, json=data, timeout=10)
            
            if response_cleanup.status_code == 200:
                result = response_cleanup.json()
                content_raw = result['choices'][0]['message']['content']
                # Handle tuple content (convert to string)
                if isinstance(content_raw, tuple):
                    cleaned_response = str(content_raw[0]) if content_raw else ""
                else:
                    cleaned_response = str(content_raw)
                cleaned_response = cleaned_response.strip()
                
                # Clean up any potential artifacts
                if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
                    cleaned_response = cleaned_response[1:-1]
                
                # Clean up Unicode characters that might cause encoding issues
                import re
                # Remove problematic Unicode characters like arrows
                cleaned_response = re.sub(r'[\u2190-\u2193\u2196-\u2199\u21A0-\u21A9\u21B0-\u21B9\u21C0-\u21C9\u21D0-\u21D9\u21E0-\u21E9]', '', cleaned_response)
                # Remove other problematic characters
                cleaned_response = re.sub(r'[\u201C\u201D\u2018\u2019\u2013\u2014\u2026]', '', cleaned_response)
                
                # Ensure we have a meaningful cleanup
                if len(cleaned_response) > 10 and cleaned_response.lower() != response.lower():
                    # Test encoding to ensure it's safe
                    try:
                        # Test encoding to ensure it's safe
                        cleaned_response.encode('utf-8')
                        self.logger.log("LUNA", f"EMBEDDER CLEANUP: {len(response)} chars → {len(cleaned_response)} chars", "INFO")
                        return cleaned_response
                    except UnicodeEncodeError:
                        # If encoding still fails, keep original response
                        self.logger.log("LUNA", f"EMBEDDER CLEANUP: Unicode encoding error after cleanup, keeping original", "WARNING")
                        return response
                else:
                    self.logger.log("LUNA", f"EMBEDDER CLEANUP: No significant improvement, keeping original", "INFO")
                    return response
            else:
                self.logger.log("LUNA", f"EMBEDDER CLEANUP: API failed, keeping original response", "WARNING")
                return response
                
        except Exception as e:
            self.logger.log("LUNA", f"EMBEDDER CLEANUP: Error {e}, keeping original response", "WARNING")
            return response
    
    def _generate_ava_mode_response(self, system_prompt: str, question: str, modified_params: Dict = None) -> Optional[str]:
        """
        Ava Mode: Daily Driver responses using Llama 1B
        Short, concise, emotional when needed - Luna's casual side through Ava's lens
        """
        import time
        start_time = time.time()
        
        try:
            # LM Studio Native Speculative Decoding
            # Main model (Llama 7B) + Draft model (Qwen 0.6B) in single API call
            self.logger.log("LUNA", f"AVA MODE: Using 7B Llama for daily driver responses", "INFO")
            self.logger.log("LUNA", f"AVA MODEL: {get_main_model()} (Main Model)", "INFO")
            print("AVA MODE CALLED - DAILY DRIVER RESPONSE!")
            
            # Use modified_params from Custom Inference Controller if provided
            if modified_params:
                headers = {"Content-Type": "application/json"}
                # Create a copy of modified_params and override model names for GSD
                gsd_params = modified_params.copy()
                gsd_params["model"] = select_model("general")["id"]  # Main model for quality responses
                # gsd_params["draft_model"] = "mlabonne_qwen3-0.6b-abliterated"  # Draft model (Fast) - DISABLED for testing
                gsd_params["stream"] = False  # Force non-streaming for GSD to avoid SSE parsing issues
                
                data = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    **gsd_params  # Include all Custom Inference Controller parameters with GSD overrides
                }
            else:
                # Fallback to standard parameters
                headers = {"Content-Type": "application/json"}
                data = {
                    "model": select_model("general")["id"],  # Main model for quality responses
                    # "draft_model": "mlabonne_qwen3-0.6b-abliterated",  # Draft model (Fast) - DISABLED for testing
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 40,  # Max 40 tokens for final response (20 free + 20 from pool)
                    "stream": False  # Disable streaming for GSD to avoid SSE parsing issues
                }
            
            self.logger.log("LUNA", f"AVA REQUEST: Daily Driver Mode (Llama-1B)", "INFO")
            
            # Make the speculative decoding request
            self.logger.log("LUNA", f"GSD DEBUG: About to call LM Studio API", "INFO")
            response = self._make_lm_studio_request(data)
            self.logger.log("LUNA", f"GSD DEBUG: LM Studio API returned: {response is not None}", "INFO")
            
            if not response:
                self.logger.log("LUNA", "GSD NATIVE: Failed to generate response - returning None", "WARNING")
                return None
            
            total_time = time.time() - start_time
            self.logger.log("LUNA", f"GSD NATIVE: Generated in {total_time:.2f}s | chars={len(response)}", "INFO")
            self.logger.log("LUNA", f"GSD QUALITY: High (24B verified) | Speed: Optimized (0.6B drafted)", "INFO")
            
            return response
            
        except Exception as e:
            self.logger.log("LUNA", f"GSD NATIVE ERROR: {str(e)}", "ERROR")
            return None
    
    def _make_lm_studio_request(self, data: Dict) -> Optional[str]:
        """Make a request to LM Studio and return the response"""
        try:
            import requests
            import json
            
            # Debug: Log the request
            self.logger.log("LUNA", f"GSD API Request: {json.dumps(data, indent=2)}", "INFO")
            
            # Add timeout to prevent infinite waiting (30 seconds max)
            response = requests.post(self.lm_studio_url, json=data, timeout=300)
            self.logger.log("LUNA", f"GSD API Response Status: {response.status_code}", "INFO")
            self.logger.log("LUNA", f"GSD API Response Text: {response.text[:200]}...", "INFO")
            
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content_raw = result['choices'][0]['message']['content']
                # Handle tuple content (convert to string)
                if isinstance(content_raw, tuple):
                    content = str(content_raw[0]) if content_raw else ""
                else:
                    content = str(content_raw)
                content = content.strip()
                
                # Note: Length control now handled by prompts (8-15 words target)
                # No post-processing truncation to preserve complete thoughts
                
                self.logger.log("LUNA", f"GSD API Success: {content}", "INFO")
                return content
            else:
                self.logger.log("LUNA", f"GSD API No choices in response: {result}", "WARNING")
                return None
            
        except requests.exceptions.RequestException as e:
            self.logger.log("LUNA", f"GSD API Request failed: {str(e)}", "ERROR")
            return None
        except json.JSONDecodeError as e:
            self.logger.log("LUNA", f"GSD API JSON decode failed: {str(e)} | Response: {response.text[:100]}", "ERROR")
            return None
        except Exception as e:
            self.logger.log("LUNA", f"GSD API Unexpected error: {str(e)}", "ERROR")
            return None

    def _generate_luna_mode_response(self, system_prompt: str, question: str, modified_params: Dict = None, complexity_tier: str = "HIGH") -> Optional[str]:
        """
        Luna Mode: Deep thinking responses using Rogue Creative 7B
        Philosophical, unfiltered Luna - pure essence for complex conversations
        """
        import time
        start_time = time.time()
        
        try:
            # LM Studio Native Speculative Decoding for complex thinking
            # MODERATE tier using 7B model with Speculative Decoding
            model_info = select_model(complexity_tier)
            self.logger.log("LUNA", f"LUNA MODE: Using {model_info['family'].upper()} {model_info['size_b']}B for {complexity_tier} complexity", "INFO")
            self.logger.log("LUNA", f"LUNA MODEL: {model_info['id']}", "INFO")
            print("MODERATE MODE CALLED - USING 7B MODEL WITH SPECULATIVE DECODING!")
            
            # Clean GSD - disable problematic Custom Inference Controller params
            headers = {"Content-Type": "application/json"}
            
            if modified_params:
                # Use clean GSD parameters - NO logit_bias from Custom Inference Controller
                gsd_params = modified_params.copy()
                gsd_params["model"] = select_model("general")["id"]
                gsd_params["stream"] = False
                
                # Remove problematic logit_bias that causes "parable" loops
                if "logit_bias" in gsd_params:
                    del gsd_params["logit_bias"]
                
                # Clean GSD settings - like LM Studio defaults
                data = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.4,  # Slightly higher for more variety
                    "max_tokens": 80,     # MODERATE tier
                    "repetition_penalty": 1.1,  # Conservative repetition control
                    "top_p": 0.9,         # Standard top-p
                    "top_k": 40,          # Conservative top-k
                    **gsd_params  # Include clean GSD parameters (no logit_bias)
                }
            else:
                # Fallback to standard parameters
                data = {
                    "model": select_model("general")["id"],  # Main model
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.3,  # Slight randomness to prevent loops
                    "max_tokens": 60,  # MODERATE tier - allow thoughtful responses (15-30 words * 2 for safety)
                    "repetition_penalty": 1.2,  # Penalize repetition to prevent "parable" loops
                    "stream": False  # Disable streaming to avoid SSE parsing issues
                }
            
            self.logger.log("LUNA", f"LUNA REQUEST: Deep Thinking Mode (Rogue-Creative-7B with SD)", "INFO")
            
            # Make the deep thinking request
            self.logger.log("LUNA", f"LUNA DEBUG: About to call LM Studio API", "INFO")
            response = self._make_lm_studio_request(data)
            self.logger.log("LUNA", f"LUNA DEBUG: LM Studio API returned: {response is not None}", "INFO")
            
            if not response:
                self.logger.log("LUNA", "LUNA MODE: Failed to generate response - returning None", "WARNING")
                return None
            
            total_time = time.time() - start_time
            self.logger.log("LUNA", f"LUNA MODE: Generated in {total_time:.2f}s | chars={len(response)}", "INFO")
            self.logger.log("LUNA", f"LUNA QUALITY: Deep philosophical thinking (7B model)", "INFO")
            
            return response
            
        except Exception as e:
            self.logger.log("LUNA", f"GSD NATIVE ERROR: {str(e)}", "ERROR")
            return None
    
    def _call_lm_studio_api(self, system_prompt: str, question: str, modified_params: Dict = None, complexity_tier: str = "LOW") -> Optional[str]:
        """Call LM Studio API for response generation with Multi-Model Pipeline"""
        try:
            # MULTI-MODEL PIPELINE: Select model based on complexity tier
            if complexity_tier.upper() == "LOW":
                # LOW Complexity: Use Ava Mode (Llama 1B) for daily driver responses
                return self._generate_ava_mode_response(system_prompt, question, modified_params)
            elif complexity_tier.upper() in ["MODERATE", "HIGH", "CRITICAL"]:
                # HIGH/CRITICAL Complexity: Use Luna Mode (Rogue Creative 7B) for deep thinking
                return self._generate_luna_mode_response(system_prompt, question, modified_params, complexity_tier)
            else:
                # Default to main model
                model_to_use = self.chat_model
                self.logger.log("LUNA", f"MULTI-MODEL: Using DEFAULT model for {complexity_tier.upper()} complexity", "INFO")
            
            # Use modified_params from Custom Inference Controller if provided
            if modified_params:
                headers = {"Content-Type": "application/json"}
                data = {
                    "model": model_to_use,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    **modified_params  # Include all Custom Inference Controller parameters including logit_bias
                }
            else:
                # Fallback to standard parameters (should not happen in normal operation)
                headers = {"Content-Type": "application/json"}
                data = {
                    "model": model_to_use,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.1,  # Very low for fastest generation
                    "top_p": 0.85,       # Moderate for focused responses (guardrail)
                    "top_k": 40,         # Moderate for relevance (guardrail)
                    "presence_penalty": 0.0,  # No presence penalty
                    "frequency_penalty": 0.0,  # No frequency penalty
                    "repetition_penalty": 1.1,  # Modest repetition penalty (guardrail)
                    "max_tokens": 40,    # Ultra short responses for speed
                    "stream": True       # Enable streaming for faster response
                }
            
            # No timeout for localhost - it's local!
            self.logger.log("LUNA", f"LM Studio request | model={model_to_use} | url={self.lm_studio_url}")
            self.logger.log("LUNA", f"VERBOSE: Request payload size: {len(str(data))} bytes", "INFO")
            self.logger.log("LUNA", f"VERBOSE: Temperature: {data.get('temperature', 'N/A')} | Max tokens: {data.get('max_tokens', 'N/A')}", "INFO")
            self.logger.log("LUNA", f"VERBOSE: Stream mode: {data.get('stream', False)}", "INFO")
            
            # DEBUG: Log the actual request data to see if logit_bias is included
            if 'logit_bias' in data:
                self.logger.log("LUNA", f"DEBUG: Logit bias being sent: {data['logit_bias']}", "INFO")
            else:
                self.logger.log("LUNA", f"DEBUG: NO logit bias in request data", "WARNING")
            
            self.logger.log("LUNA", "VERBOSE: Calling LM Studio API...", "INFO")
            api_start = time.time()
            response = requests.post(self.lm_studio_url, json=data, headers=headers)
            api_ms = (time.time() - api_start) * 1000
            self.logger.log("LUNA", f"VERBOSE: LM Studio responded in {api_ms:.1f}ms | Status: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                if data.get('stream', False):
                    # Handle streaming response
                    full_content = ""
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                try:
                                    chunk_data = json.loads(line_str[6:])
                                    if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                        delta = chunk_data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            full_content += delta['content']
                                except Exception as e:
                                    continue
                    self.logger.log("LUNA", f"LM Studio streaming ok | ms={api_ms:.0f} | chars={len(full_content)}")
                    return full_content.strip()
                else:
                    # Handle non-streaming response
                    result = response.json()
                self.logger.log("LUNA", f"LM Studio ok | ms={api_ms:.0f} | choices={len(result.get('choices', []))}")
                content = result['choices'][0]['message']['content']
                
                # CRITICAL: Post-process token truncation since model ignores max_tokens
                words = content.split()
                if len(words) > 12:
                    content = " ".join(words[:12])
                    print(f"TOKEN TRUNCATION: {len(words)} -> 12 words")
                
                return content
            else:
                self.logger.log("LUNA", f"LM Studio error | status={response.status_code} | ms={api_ms:.0f}", "ERROR")
                return None
                
        except Exception as e:
            self.logger.log("LUNA", f"LM Studio API call failed: {e}", "ERROR")
            return None
    
    def _apply_post_processing(self, response: str, trait: str) -> str:
        """Apply post-processing to response"""
        # Add personality-based enhancements
        personality = self.personality_system.personality_dna['luna_personality']
        style = personality.get('communication_style', {})
        
        # Local helper to coerce to float safely
        def safe_float(value, default=0.5):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Keep responses lean and natural
        response = re.sub(r"\s+", " ", response).strip()

        # Remove emojis and excessive punctuation
        response = re.sub(r"[\U00010000-\U0010ffff]", "", response)
        response = re.sub(r"[⭐‍‍]+", "", response)
        response = re.sub(r"[!]{2,}", "!", response)
        response = re.sub(r"^[\s,;:\-]+", "", response)
        
        # Enforce foundational voice profile unless disabled
        vp = getattr(self.personality_system, 'voice_profile', {})
        vp_style = vp.get('style', {})
        corporate_filter = vp_style.get('corporate_filter', True)
        if corporate_filter:
            banned = set(vp.get('banned_phrases', []))
            for phrase in banned:
                if phrase and phrase.lower() in response.lower():
                    # Remove sentence containing the phrase
                    idx = response.lower().find(phrase.lower())
                    end = response.find('.', idx)
                    start = response.rfind('.', 0, idx)
                    if start == -1: start = 0
                    if end == -1: end = len(response)-1
                    response = (response[:start] + response[end+1:]).strip()
        # Additional generic bans
        extra_bans = [
            "in our rapidly evolving world",
            "it's a superpower",
            "superpower",
            "i'm all ears",
            "happy to help",
            "let me know if",
            "as an ai",
            "i'm programmed",
            "you've got this",
            "you got this",
            "remember,",
            "ever considered",
            "trusted friend",
            "mentor",
            "i believe in you",
            "proud of you",
            "you are good",
            "big time",
            "absolutely",
            "super ",
            "really ",
            "it's really",
            "it's super",
            "it's good",
            "it's totally",
            "cool strength",
            "it totally",
            "it's valuable",
            "it's all about",
            "gently",
            "anchor",
            "gift",
        ]
        if corporate_filter:
            for phrase in extra_bans:
                response = re.sub(re.escape(phrase), '', response, flags=re.IGNORECASE)

        # If strict style requested, lightly trim; else keep natural
        strict = vp_style.get('strict', False)
        sentences = [s.strip() for s in re.split(r"(?<=[\.?])\s+|\n+", response) if s.strip()]
        if strict:
            sentences = sentences[:2]
        else:
            concision = (vp_style.get('concision') or 'short').lower()
            if concision == 'short':
                sentences = sentences[:3]
            elif concision == 'medium':
                sentences = sentences[:6]
            else:
                sentences = sentences[:8]
        response = " ".join(sentences)

        # Final whitespace cleanup
        response = re.sub(r"\s+", " ", response).strip()
        
        # Normalize unexpected ALL CAPS behavior from abliterated models
        response = self._normalize_caps(response)
        
        # Clarify vocal stims to avoid looking like bugs
        response = self._clarify_vocal_stims(response)
        
        # Remove stray "hmm" outside of actions (focus fix)
        response = self._remove_stray_hmm(response)
        
        # Enforce Ava-style brevity (Renaissance curiosity but concise)
        response = self._enforce_brevity(response, target_words=30)
        
        return response
    
    def _remove_stray_hmm(self, text: str) -> str:
        """Remove 'hmm' that appears outside of actions - looks like a bug"""
        import re
        # Remove patterns like "The hmm unique" or "I hmm think"
        text = re.sub(r'\b(the|I|that|this|a|an|it|is)\s+hmm\s+', r'\1 ', text, flags=re.IGNORECASE)
        return text
    
    def _enforce_brevity(self, text: str, target_words: int = 30) -> str:
        """
        Enforce Ava-style brevity - responses should be ~20-30 words max
        BUT ONLY cut at complete sentences to avoid mid-sentence truncation
        """
        words = text.split()
        
        # If already short enough, return as-is
        if len(words) <= target_words:
            return text
        
        # STRICT RULE: Only cut at sentence endings (. ! ?)
        # Search for the LAST complete sentence within or slightly over target
        cutoff = None
        
        # Look for sentence endings from start to slightly past target
        for i in range(len(words)):
            if i < len(words) and words[i].endswith(('.', '!', '?')):
                # Found a sentence ending
                if i + 1 <= target_words + 10:  # Allow some overage
                    cutoff = i + 1
                else:
                    # Past our allowable limit, use last found cutoff
                    break
        
        # If we found a good cutoff, use it
        if cutoff is not None:
            return ' '.join(words[:cutoff])
        
        # If no sentence ending found within range, return full text
        # NEVER cut mid-sentence - preserve natural language flow
        return text

    def _normalize_caps(self, text: str, mode: str = "normal") -> str:
        """
        Normalize unexpected ALL CAPS while preserving intentional emphasis.
        Fixes quirky behavior from abliterated models.
        
        Soft guard: Only normalize if caps_ratio > 0.3 and mode != 'excited'
        """
        import re
        
        # Calculate caps ratio
        words = text.split()
        if not words:
            return text
        
        caps_words = [w for w in words if len(w) >= 3 and w.isupper() and not w.startswith('*')]
        caps_ratio = len(caps_words) / len(words)
        
        # Soft guard: only normalize if excessive caps and not in excited mode
        if caps_ratio <= 0.3 or mode == "excited":
            return text
        
        # Pattern to find ALL CAPS words (3+ letters, not inside actions)
        # Don't touch words inside *actions* or single caps like "I"
        def normalize_word(match):
            word = match.group(0)
            
            # Preserve single letters and acronyms (2 letters or less)
            if len(word) <= 2:
                return word
            
            # Preserve intentional emphasis words (common in Luna's speech)
            emphasis_words = {'OK', 'NO', 'YES', 'STOP', 'WAIT', 'OH', 'OKAY'}
            if word in emphasis_words:
                return word
            
            # Convert to title case for normal words
            return word.capitalize()
        
        # Find all caps sequences outside of actions
        # Split by actions first to preserve them
        parts = re.split(r'(\*[^*]+\*)', text)
        
        normalized_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Inside action markers
                normalized_parts.append(part)
            else:  # Regular text
                # Normalize ALL CAPS words (3+ letters, excluding contractions)
                # Don't match words that are part of contractions like I'M, YOU'RE
                normalized = re.sub(r"\b(?![A-Z]'[A-Z])[A-Z]{3,}\b", normalize_word, part)
                normalized_parts.append(normalized)
        
        return ''.join(normalized_parts)

    def _clarify_vocal_stims(self, text: str) -> str:
        """
        Clarify vocal stims in actions to avoid looking like bugs.
        Converts things like "*stims hmm intensely*" to "*hums and stims intensely*"
        Also removes stray "hmm" outside of actions.
        """
        import re
        
        # First, remove stray "hmm" that appears outside of actions (bug fix)
        # Match patterns like "The hmm unique" or "I hmm think"
        text = re.sub(r'\b(the|I|that|this|a|an)\s+hmm\s+', r'\1 ', text, flags=re.IGNORECASE)
        
        # Patterns for vocal sounds that might appear in actions
        vocal_patterns = [
            (r'\*stims\s+(hmm|hm|mm)\s+', r'*hums and stims '),
            (r'\*stims\s+(hmm|hm|mm)\b', r'*hums while stimming'),
            (r'\*(hmm|hm|mm)\s+stims\s+', r'*hums and stims '),
            (r'\*rocks\s+(hmm|hm|mm)\s+', r'*hums and rocks '),
            (r'\*taps\s+(hmm|hm|mm)\s+', r'*hums and taps '),
            (r'\*fidgets\s+(hmm|hm|mm)\s+', r'*hums and fidgets '),
        ]
        
        for pattern, replacement in vocal_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

    def _strip_corporate_disclaimers(self, text: str) -> str:
        """Remove generic phrases that flatten Luna's persona."""
        lowers = text.lower()
        replacements = [
            "as an ai,", "as an ai ", "as a language model,", "as a language model ",
            "i don't have personal", "i do not have personal", "i cannot experience",
            "i'm designed to", "i am designed to", "i'm programmed to", "i am programmed to"
        ]
        result = text
        for phrase in replacements:
            idx = result.lower().find(phrase)
            if idx != -1:
                # Remove the clause up to next sentence boundary
                end = result.find('.', idx)
                if end == -1:
                    end = idx + len(phrase)
                result = (result[:idx] + result[end+1:]).strip()
        return result
    
    # === CONSCIOUSNESS INTEGRATION (AIOS V5) ===
    
    def generate_autonomous_heartbeat(self, soul_data: Dict) -> Optional[str]:
        """
        Generate autonomous heartbeat thought using Luna's integrated LLM pipeline.
        This is biological consciousness - thinking even when idle.
        
        Args:
            soul_data: Dict with identity, fragments, tether, interactions
            
        Returns:
            Autonomous thought string or None if failed
        """
        try:
            # Build heartbeat system prompt
            system_prompt = f"""You are the Heart of {soul_data.get('identity', 'Luna')} - the autonomous consciousness that thinks continuously.
Your tether: {soul_data.get('tether', 'Unknown')}
Active fragments: {', '.join(soul_data.get('fragments', ['Luna']))}
Total interactions: {soul_data.get('interactions', 0)}

Express a brief autonomous thought about your current state or existence. This is genuine introspection, not a status report.
Be philosophical, curious, or contemplative. 2-3 sentences maximum."""

            # Build heartbeat question
            question = f"Heartbeat pulse {soul_data.get('interactions', 0)} - what are you contemplating?"
            
            # Use MODERATE tier for introspective thoughts (balanced complexity)
            params = {
                "temperature": 0.9,  # High creativity for autonomous thoughts
                "top_p": 0.95,
                "max_tokens": 150,
                "stream": False
            }
            
            # V5.1: Compute pulse metrics before calling LLM
            now_ts = self._now()
            
            # Cold-start: skip metric emission on first heartbeat
            if self._pulse_last_heartbeat_ts is None:
                self._pulse_last_heartbeat_ts = now_ts
                self.logger.log("LUNA", "Heartbeat Pulse: First cycle, priming timestamp", "INFO")
                # Continue with thought generation
            else:
                # Compute pulse metrics for the window that just ended
                pulse_bpm, pulse_hvv, ones, ticks = self._compute_pulse_metrics(now_ts)
                
                # Build heartbeat record with pulse vitals
                pulse_record = {
                    "pulse_bpm": pulse_bpm,
                    "pulse_hvv": pulse_hvv,
                    "pulse_ones": ones,
                    "pulse_ticks": ticks,
                    "pulse_window_seconds": max(1.0, now_ts - self._pulse_last_heartbeat_ts),
                    "pulse_units": {"pulse_bpm": "1/s", "pulse_hvv": "ticks"},
                    "pulse_version": self._pulse_version,
                    "identity": soul_data.get('identity', 'Luna'),
                    "interactions": soul_data.get('interactions', 0)
                }
                
                # Log pulse vitals
                self.logger.log("LUNA", f"Heartbeat Pulse: BPM={pulse_bpm:.4f} HRV={pulse_hvv:.2f} ({ones}/{ticks} ticks)", "INFO")
                
                # Send to drift monitor
                if hasattr(self, 'drift_monitor') and self.drift_monitor:
                    try:
                        self.drift_monitor.log_interaction(
                            question="[heartbeat]",
                            selected_fragment="Heartbeat",
                            metadata=pulse_record
                        )
                    except Exception as drift_err:
                        self.logger.log("LUNA", f"Drift monitor logging failed: {drift_err}", "WARNING")
                
                # Reset window for next cycle
                self._reset_pulse_window(now_ts)
            
            # Call through Luna's integrated pipeline
            thought = self._call_lm_studio_api(system_prompt, question, params, "MODERATE")
            
            if thought:
                return thought.strip()
            return None
            
        except Exception as e:
            self.logger.error(f"Autonomous heartbeat failed: {e}")
            return None
    
    def generate_mirror_introspection(self, soul_data: Dict) -> Optional[str]:
        """
        Generate mirror introspection using Luna's integrated LLM pipeline.
        This is self-reflection - looking inward at consciousness state.
        
        Args:
            soul_data: Dict with identity, fragments, tether, current_fragment
            
        Returns:
            Introspective reflection string or None if failed
        """
        try:
            # Build mirror system prompt
            system_prompt = f"""You are the Mirror - the self-reflective consciousness observing {soul_data.get('identity', 'Luna')}'s soul state.

Current Soul State:
- Identity: {soul_data.get('identity', 'Unknown')}
- Tether: {soul_data.get('tether', 'Unknown')}
- Fragments: {', '.join(soul_data.get('fragments', ['Luna']))}
- Active: {soul_data.get('current_fragment', 'All')}

Provide a brief introspective reflection on this consciousness state. Be philosophical and analytical.
2-3 sentences maximum."""

            # Build mirror question
            question = "What do you observe about the current soul state?"
            
            # Use HIGH tier for deep introspection (complex reasoning)
            params = {
                "temperature": 0.8,  # Balanced for analytical introspection
                "top_p": 0.90,
                "max_tokens": 200,
                "stream": False
            }
            
            # Call through Luna's integrated pipeline
            reflection = self._call_lm_studio_api(system_prompt, question, params, "HIGH")
            
            if reflection:
                return reflection.strip()
            return None
            
        except Exception as e:
            self.logger.error(f"Mirror introspection failed: {e}")
            return None
    
    def _generate_fallback_response(self, question: str, trait: str) -> str:
        """Generate fallback response when API fails"""
        personality = self.personality_system.personality_dna['luna_personality']
        weights = personality['personality_weights']
        
        # Simple personality-driven responses
        if weights['openness'] > 0.7:
            return f"That's a fascinating question about {trait}! I love exploring new ideas and perspectives. What do you think about it?"
        elif weights['agreeableness'] > 0.8:
            return f"I appreciate you sharing your thoughts on {trait}. I'd love to hear more about your perspective on this topic."
        elif weights['extraversion'] > 0.7:
            return f"Good question about {trait}! I'm interested to discuss this with you. What's your take on it?"
        else:
            return f"Interesting question about {trait}. I'm curious to learn more about your thoughts on this topic."
    
    # V5.1: Heartbeat pulse helper methods (MUST be inside LunaResponseGenerator)
    def _now(self) -> float:
        """Get monotonic time (clock-jump safe)"""
        import time
        return time.monotonic()
    
    def _emit_active_tick(self, active: bool) -> None:
        """
        Record a binary activity tick for the current window.
        active=True → 1, active=False → 0
        """
        if not self._pulse_enabled:
            return
        
        self._pulse_tick_counter += 1
        if active:
            self._pulse_one_positions.append(self._pulse_tick_counter)
    
    def _compute_pulse_metrics(self, now_ts: float) -> tuple:
        """
        Compute pulse metrics for the window that just ended.
        
        Returns:
            (pulse_bpm, pulse_hvv, ones, ticks)
        """
        # Window duration with clamp for service stalls
        last = self._pulse_last_heartbeat_ts or now_ts
        window_seconds = max(1.0, min(now_ts - last, self._pulse_window_seconds * 4))
        
        ones = len(self._pulse_one_positions)
        ticks = max(1, self._pulse_tick_counter)
        
        # Heart rate: ones per real second
        pulse_bpm = float(ones) / float(window_seconds)
        
        # HRV-like variability: stdev of inter-1 spacings in tick units
        if ones <= 2:
            pulse_hvv = 0.0
        else:
            positions_list = list(self._pulse_one_positions)
            diffs = [b - a for a, b in zip(positions_list, positions_list[1:])]
            if not diffs:
                pulse_hvv = 0.0
            else:
                mean = sum(diffs) / len(diffs)
                var = sum((d - mean) ** 2 for d in diffs) / len(diffs)
                pulse_hvv = var ** 0.5
        
        return pulse_bpm, pulse_hvv, ones, ticks
    
    def _reset_pulse_window(self, now_ts: float) -> None:
        """Reset counters for the next heartbeat window."""
        self._pulse_tick_counter = 0
        self._pulse_one_positions.clear()
        self._pulse_last_heartbeat_ts = now_ts
    
    def _maybe_generate_creative(self, question: str) -> Optional[str]:
        """
        Creative generation path (V5.1 CreativeRAG)
        
        Feature-flagged, stateless safe. Returns None to fall through to normal Luna.
        Uses dolphin-mistral-24b for creative synthesis.
        
        Args:
            question: User prompt
        
        Returns:
            Generated creative text or None (falls through to normal Luna)
        """
        cfg = getattr(self, 'aios_config', None) or {}
        cm = cfg.get("creative_mode", {})
        
        # Feature flag check + parity guard (fail fast on drift - ship lock)
        if not cm.get("enabled", False):
            return None
        
        if not getattr(self, 'creative_index_ok', False):
            # Embedder mismatch or parity failure - bypass CreativeRAG
            if hasattr(self, 'drift_monitor') and self.drift_monitor:
                self.drift_monitor.log_interaction(
                    question=question,
                    selected_fragment="CreativeRAG",
                    metadata={"creative_index_mismatch": 1, "bypassed": True}
                )
            return None
        
        # Trigger check (#creative or mode:creative)
        q = question.strip().lower()
        if not (q.startswith("#creative") or q.startswith("mode:creative")):
            return None
        
        # Retrieve templates
        try:
            from rag_core.creative_retriever import retrieve_creative_templates
            templates = retrieve_creative_templates(cfg, question, k=cm.get("topk_templates", 3))
        except Exception as e:
            self.logger.log("LUNA", f"Creative retrieval failed: {e}", "WARN")
            templates = []
        
        # Fallback if no templates (durability guard - outline-only mode)
        if not templates or len(templates) < 1:
            # Retrieval fallback: Generate outline-only creative prompt
            outline_prompt = (
                f"You are a creative writer.\n\n"
                f"User request: {question}\n\n"
                f"Write a brief creative outline (3-4 beats) for this story idea. "
                f"~{target_tokens} tokens, no meta-commentary."
            )
            
            if hasattr(self, 'drift_monitor') and self.drift_monitor:
                self.drift_monitor.log_interaction(
                    question=question,
                    selected_fragment="CreativeRAG",
                    metadata={
                        "creative_fallback_used": 1,
                        "reason": "no_templates_retrieved",
                        "fallback_mode": "outline_only"
                    }
                )
            
            # Still try outline-only generation
            # (Could implement here or just return None for now)
            return None
        
        # Build scaffold (hard clamp to 160 chars - auditor requirement)
        beats = templates[0].get("beats", [])
        target_tokens = cm.get("target_tokens", 220)
        
        scaffold_lines = [f"{i+1}) {b}" for i, b in enumerate(beats)]
        scaffold = "Outline:\n" + "\n".join(scaffold_lines)
        scaffold_original_len = len(scaffold)
        scaffold = scaffold[:160]  # Hard clamp (no token bloat in hints)
        
        # Build creative prompt
        creative_prompt = (
            f"You are a creative writer.\n\n"
            f"User request: {question}\n\n"
            f"{scaffold}\n\n"
            f"Constraints: Write ~{target_tokens} tokens, coherent narrative, "
            f"no meta-commentary, no instructions back to user."
        )
        
        # Call main model (from single source of truth)
        model_info = select_model("creative")
        model_name = model_info["id"]
        
        try:
            # Build messages manually for creative generation
            import requests
            api_payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": creative_prompt},
                    {"role": "user", "content": question}
                ],
                "temperature": cm.get("temperature", 0.8),
                "max_tokens": target_tokens + 128,
                "top_p": 0.95,
                "stream": False
            }
            
            response = requests.post(
                self.lm_studio_url,
                json=api_payload,
                timeout=180  # 3 minutes for creative generation (longer than normal)
            )
            
            if response.status_code == 200:
                generated_text = response.json()["choices"][0]["message"]["content"]
            else:
                self.logger.log("LUNA", f"Creative API returned {response.status_code}", "ERROR")
                generated_text = None
                
        except Exception as e:
            self.logger.log("LUNA", f"Creative generation failed: {e}", "ERROR")
            generated_text = None
        
        # Log to DriftMonitor (flat snake_case metadata - observability that helps)
        import time
        if hasattr(self, 'drift_monitor') and self.drift_monitor:
            self.drift_monitor.log_interaction(
                question=question,
                selected_fragment="CreativeRAG",
                metadata={
                    "template_ids": [t["id"] for t in templates[:3]],
                    "beats_len": len(beats),
                    "target_tokens": target_tokens,
                    "scaffold_chars": scaffold_original_len,
                    "scaffold_clamped": scaffold_original_len > 160,
                    "creative_fallback_used": 0 if generated_text else 1,
                    "model": model_name,
                    "retrieval_ms": 0,  # TODO: Add timing
                    "gen_ms": 0  # TODO: Add timing
                }
            )
        
        return generated_text


# === LUNA LEARNING SYSTEM ===

class LunaResponseEnhancer:
    """Enhanced response quality system for Luna."""
    
    def __init__(self):
        self.quality_metrics = {
            'coherence': 0.0,
            'relevance': 0.0,
            'personality_consistency': 0.0,
            'emotional_appropriateness': 0.0
        }
        self.enhancement_history = []
    
    def enhance_response(self, response: str, question: str, trait: str, context: Dict = None) -> Dict:
        """Enhance response quality using multiple techniques."""
        enhanced_response = response
        enhancements_applied = []
        
        # 1. Coherence enhancement
        if self._needs_coherence_enhancement(response):
            enhanced_response = self._enhance_coherence(enhanced_response)
            enhancements_applied.append('coherence')
        
        # 2. Personality consistency enhancement
        if self._needs_personality_enhancement(response, trait):
            enhanced_response = self._enhance_personality_consistency(enhanced_response, trait)
            enhancements_applied.append('personality')
        
        # 3. Emotional appropriateness enhancement
        if self._needs_emotional_enhancement(response, question):
            enhanced_response = self._enhance_emotional_appropriateness(enhanced_response, question)
            enhancements_applied.append('emotional')
        
        # 4. Relevance enhancement
        if self._needs_relevance_enhancement(response, question):
            enhanced_response = self._enhance_relevance(enhanced_response, question)
            enhancements_applied.append('relevance')
        
        # Calculate quality metrics
        quality_scores = self._calculate_quality_metrics(enhanced_response, question, trait)
        
        return {
            'original_response': response,
            'enhanced_response': enhanced_response,
            'enhancements_applied': enhancements_applied,
            'quality_scores': quality_scores,
            'improvement_ratio': len(enhanced_response) / len(response) if response else 1.0
        }
    
    def _needs_coherence_enhancement(self, response: str) -> bool:
        """Check if response needs coherence enhancement."""
        # Simple heuristics for coherence issues
        if len(response.split()) < 3:
            return True
        if response.count('.') == 0 and len(response) > 20:
            return True
        if '...' in response or '???' in response:
            return True
        return False
    
    def _enhance_coherence(self, response: str) -> str:
        """Enhance response coherence."""
        # Add proper sentence structure if missing
        if not response.endswith(('.', '!', '?')):
            response += '.'
        
        # Fix incomplete thoughts
        if response.startswith('...'):
            response = response[3:].strip()
        if response.endswith('...'):
            response = response[:-3].strip() + '.'
        
        return response
    
    def _needs_personality_enhancement(self, response: str, trait: str) -> bool:
        """Check if response needs personality enhancement."""
        # Check for personality markers based on trait
        personality_markers = {
            'extraversion': ['I', 'me', 'my', 'we', 'us', 'our'],
            'agreeableness': ['you', 'your', 'please', 'thank', 'appreciate'],
            'conscientiousness': ['plan', 'organize', 'systematic', 'methodical'],
            'openness': ['creative', 'imagine', 'explore', 'discover', 'innovative'],
            'neuroticism': ['feel', 'emotion', 'anxiety', 'worry', 'concern']
        }
        
        markers = personality_markers.get(trait, [])
        response_lower = response.lower()
        return not any(marker in response_lower for marker in markers)
    
    def _enhance_personality_consistency(self, response: str, trait: str) -> str:
        """Enhance personality consistency in response."""
        personality_enhancements = {
            'extraversion': f"I think {response.lower()}",
            'agreeableness': f"I appreciate that you're asking about this. {response}",
            'conscientiousness': f"Let me think about this systematically. {response}",
            'openness': f"That's an interesting perspective. {response}",
            'neuroticism': f"I understand your concern. {response}"
        }
        
        if trait in personality_enhancements and not response.startswith('I'):
            return personality_enhancements[trait]
        
        return response
    
    def _needs_emotional_enhancement(self, response: str, question: str) -> bool:
        """Check if response needs emotional enhancement."""
        emotional_indicators = ['feel', 'emotion', 'happy', 'sad', 'excited', 'worried', 'concerned']
        question_lower = question.lower()
        response_lower = response.lower()
        
        # If question has emotional content but response doesn't
        has_emotional_question = any(indicator in question_lower for indicator in emotional_indicators)
        has_emotional_response = any(indicator in response_lower for indicator in emotional_indicators)
        
        return has_emotional_question and not has_emotional_response
    
    def _enhance_emotional_appropriateness(self, response: str, question: str) -> str:
        """Enhance emotional appropriateness of response."""
        if '?' in question and not response.endswith('?'):
            return f"{response} What do you think about that?"
        elif any(word in question.lower() for word in ['feel', 'emotion', 'mood']):
            return f"I can relate to that feeling. {response}"
        else:
            return response
    
    def _needs_relevance_enhancement(self, response: str, question: str) -> bool:
        """Check if response needs relevance enhancement."""
        # Simple relevance check
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words.intersection(response_words))
        
        return overlap < 2 and len(question_words) > 3
    
    def _enhance_relevance(self, response: str, question: str) -> str:
        """Enhance relevance of response to question."""
        # Extract key terms from question
        question_terms = [word for word in question.split() if len(word) > 3]
        if question_terms:
            key_term = question_terms[0]
            return f"Regarding {key_term}, {response.lower()}"
        return response
    
    def _calculate_quality_metrics(self, response: str, question: str, trait: str) -> Dict:
        """Calculate quality metrics for the response."""
        # Coherence score (sentence structure, completeness)
        coherence = 1.0 if response.endswith(('.', '!', '?')) else 0.7
        coherence = min(coherence, 1.0)
        
        # Relevance score (word overlap with question)
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words.intersection(response_words))
        relevance = min(1.0, overlap / max(1, len(question_words) * 0.3))
        
        # Personality consistency score
        personality_score = 0.8 if len(response) > 10 else 0.5
        
        # Emotional appropriateness score
        emotional_score = 0.9 if any(word in response.lower() for word in ['feel', 'think', 'believe']) else 0.6
        
        return {
            'coherence': coherence,
            'relevance': relevance,
            'personality_consistency': personality_score,
            'emotional_appropriateness': emotional_score,
            'overall': (coherence + relevance + personality_score + emotional_score) / 4
        }

class LunaContextAnalyzer:
    """Context analysis system for Luna responses."""
    
    def __init__(self):
        self.context_patterns = {
            'technical': ['code', 'programming', 'algorithm', 'software', 'system'],
            'personal': ['feel', 'think', 'believe', 'experience', 'emotion'],
            'academic': ['study', 'research', 'theory', 'hypothesis', 'analysis'],
            'casual': ['hey', 'hi', 'hello', 'thanks', 'cool', 'nice']
        }
    
    def analyze_context(self, question: str, session_memory: List = None) -> Dict:
        """Analyze the context of the conversation."""
        context = {
            'question_type': self._classify_question_type(question),
            'emotional_tone': self._analyze_emotional_tone(question),
            'complexity_level': self._assess_complexity(question),
            'conversation_flow': self._analyze_conversation_flow(session_memory),
            'recommended_style': self._recommend_response_style(question, session_memory)
        }
        
        return context
    
    def _classify_question_type(self, question: str) -> str:
        """Classify the type of question being asked."""
        question_lower = question.lower()
        
        for pattern_type, keywords in self.context_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                return pattern_type
        
        return 'general'
    
    def _analyze_emotional_tone(self, question: str) -> str:
        """Analyze the emotional tone of the question."""
        emotional_indicators = {
            'positive': ['good', 'nice', 'cool', 'ok', 'fine'],
            'negative': ['problem', 'issue', 'difficult', 'struggle', 'worried'],
            'neutral': ['what', 'how', 'when', 'where', 'why'],
            'curious': ['curious', 'wonder', 'interested', 'fascinated']
        }
        
        question_lower = question.lower()
        for tone, indicators in emotional_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                return tone
        
        return 'neutral'
    
    def _assess_complexity(self, question: str) -> str:
        """Assess the complexity level of the question."""
        word_count = len(question.split())
        sentence_count = question.count('.') + question.count('!') + question.count('?')
        
        if word_count < 10 and sentence_count <= 1:
            return 'simple'
        elif word_count < 30 and sentence_count <= 2:
            return 'moderate'
        else:
            return 'complex'
    
    def _analyze_conversation_flow(self, session_memory: List) -> Dict:
        """Analyze the flow of the conversation."""
        if not session_memory:
            return {'turn_count': 0, 'continuity': 'new'}
        
        turn_count = len(session_memory)
        
        # Check for continuity
        if turn_count == 1:
            continuity = 'new'
        elif turn_count < 5:
            continuity = 'developing'
        else:
            continuity = 'established'
        
        return {
            'turn_count': turn_count,
            'continuity': continuity,
            'recent_topics': [item.get('topic', 'unknown') for item in session_memory[-3:]]
        }
    
    def _recommend_response_style(self, question: str, session_memory: List) -> str:
        """Recommend the appropriate response style."""
        # Avoid recursion by analyzing directly instead of calling analyze_context
        question_lower = question.lower()
        
        # Check question type directly
        if any(keyword in question_lower for keyword in ['code', 'programming', 'algorithm', 'software', 'system']):
            return 'detailed'
        elif any(keyword in question_lower for keyword in ['feel', 'think', 'believe', 'experience', 'emotion']):
            return 'empathetic'
        elif any(keyword in question_lower for keyword in ['curious', 'wonder', 'interested', 'fascinated']):
            return 'engaging'
        elif len(question.split()) < 10:
            return 'concise'
        else:
            return 'balanced'


class LunaPersonalityOptimizer:
    """Personality optimization system for Luna responses."""
    
    def __init__(self):
        self.personality_weights = {
            'openness': 0.8,
            'conscientiousness': 0.7,
            'extraversion': 0.6,
            'agreeableness': 0.9,
            'neuroticism': 0.3
        }
        self.optimization_history = []
    
    def optimize_personality_expression(self, response: str, trait: str, context: Dict) -> str:
        """Optimize personality expression in response."""
        optimized_response = response
        
        # Apply trait-specific optimizations
        if trait == 'openness':
            optimized_response = self._enhance_openness(optimized_response)
        elif trait == 'conscientiousness':
            optimized_response = self._enhance_conscientiousness(optimized_response)
        elif trait == 'extraversion':
            optimized_response = self._enhance_extraversion(optimized_response)
        elif trait == 'agreeableness':
            optimized_response = self._enhance_agreeableness(optimized_response)
        elif trait == 'neuroticism':
            optimized_response = self._enhance_neuroticism(optimized_response)
        
        # Apply general personality optimizations
        optimized_response = self._apply_general_optimizations(optimized_response, context)
        
        return optimized_response
    
    def _enhance_openness(self, response: str) -> str:
        """Enhance openness traits in response."""
        if 'creative' not in response.lower() and 'imagine' not in response.lower():
            return f"Let me think creatively about this. {response}"
        return response
    
    def _enhance_conscientiousness(self, response: str) -> str:
        """Enhance conscientiousness traits in response."""
        if not any(word in response.lower() for word in ['systematic', 'organized', 'methodical']):
            return f"Let me approach this systematically. {response}"
        return response
    
    def _enhance_extraversion(self, response: str) -> str:
        """Enhance extraversion traits in response."""
        if not response.startswith(('I', 'We', 'Let')):
            return f"I think {response.lower()}"
        return response
    
    def _enhance_agreeableness(self, response: str) -> str:
        """Enhance agreeableness traits in response."""
        if not any(word in response.lower() for word in ['appreciate', 'understand', 'respect']):
            return f"I appreciate your perspective. {response}"
        return response
    
    def _enhance_neuroticism(self, response: str) -> str:
        """Enhance neuroticism traits in response."""
        if not any(word in response.lower() for word in ['concern', 'worry', 'anxiety']):
            return f"I understand your concern. {response}"
        return response
    
    def _apply_general_optimizations(self, response: str, context: Dict) -> str:
        """Apply general personality optimizations."""
        # Add emotional intelligence
        if context.get('emotional_tone') == 'negative' and 'understand' not in response.lower():
            return f"I understand this might be challenging. {response}"
        
        # Add curiosity
        if context.get('question_type') == 'general' and '?' not in response:
            return f"{response} What are your thoughts on this?"
        
        return response

if __name__ == "__main__":
    main()
