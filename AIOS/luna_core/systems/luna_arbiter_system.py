#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Luna Internal Governance System - The Arbiter & TTE Economy
Implements the Gold Standard learning loop with Karma-based alignment

DUAL-EVALUATION ARCHITECTURE:
- This is the INTERNAL ARBITER (runtime response assessment)
- External counterpart: AIOS AUDITOR GPT (design-time architectural validation)
- See: docs/ARBITER_DUAL_AUDIT_ARCHITECTURE.md

KEY DISTINCTION:
- AUDITOR (external GPT) = Validates system designs and architecture
- ARBITER (this module) = Assesses Luna's individual responses and manages karma

Integration:
- Use arbiter_export_util.py to export logs for External Auditor analysis
- V5: Now tracks lingua_calc_depth and lingua_calc_gain in CacheEntry
"""

import time
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from luna_core.systems.luna_cfia_system import LunaCFIASystem
# Import moved to avoid circular dependency

# Week 4: Import fractal policies for type-conditioned rubrics
try:
    from fractal_core.core import FractalPolicies
    FRACTAL_POLICIES_AVAILABLE = True
except ImportError:
    FRACTAL_POLICIES_AVAILABLE = False

# Try to import Rust Arbiter for acceleration
try:
    import aios_luna_rust
    RUST_ARBITER_AVAILABLE = True
    print("⚡ Rust Arbiter module available - will use for fast assessment")
except ImportError:
    RUST_ARBITER_AVAILABLE = False
    # Silently fall back to Python - Rust is optional

@dataclass
class CacheEntry:
    """A lesson triplet stored in the cache"""
    original_prompt: str
    suboptimal_response: str
    gold_standard: str
    utility_score: float
    karma_delta: float
    timestamp: float
    context_tags: List[str]
    # V5: Linguistic calculus features
    lingua_calc_depth: int = 0
    lingua_calc_gain: float = 0.0

@dataclass
class ArbiterAssessment:
    """Assessment result from the Arbiter"""
    gold_standard: str
    utility_score: float
    karma_delta: float
    efficiency_gap: float
    quality_gap: float
    reasoning: str
    cache_entry: CacheEntry

class LunaArbiterSystem:
    """
    The Arbiter Agent - Internal Critic & Teacher
    Operates outside TTE constraints to enforce alignment and generate learning materials
    """
    
    def __init__(self, cache_path: str = "data_core/ArbiterCache"):
        """Initialize the Arbiter system"""
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # Core variables (The Economy) - Now using CFIA generational karma pool
        self.karma_history = []
        
        # Cache management
        self.cache_entries = []
        self._load_cache()
        
        # Initialize CFIA system for memory management
        self.cfia_system = LunaCFIASystem(cache_path)
        
        # Initialize Rust Arbiter for fast assessment (if available)
        self.rust_arbiter = None
        if RUST_ARBITER_AVAILABLE:
            try:
                initial_karma = self.cfia_system.state.karma_pool
                self.rust_arbiter = aios_luna_rust.RustArbiter(initial_karma)
                print(f"⚡ Rust Arbiter initialized with karma: {initial_karma}")
            except Exception as e:
                print(f"⚠️ Rust Arbiter init failed: {e}, using Python")
                self.rust_arbiter = None
        
        # Initialize Mycelium Lesson Retrieval System (lazy import to avoid circular dependency)
        self.mycelium_retriever = None
        
        # Adaptive threshold system for learning-based adjustments
        self.learning_history = []
        self.adaptive_thresholds = {
            'utility_threshold': 0.2,  # Base utility threshold
            'efficiency_threshold': 0.3,  # Base efficiency threshold
            'penalty_scaling': 1.0  # Base penalty scaling factor
        }
        
        # SHADOW SCORE SYSTEM: Track Luna's choices and their costs without immediate feedback
        self.shadow_score_history = []
        self.shadow_score_summary = {
            'total_responses': 0,
            'empathy_choices': 0,
            'efficiency_choices': 0,
            'total_karma_cost': 0.0,
            'total_karma_gain': 0.0,
            'net_karma_change': 0.0,
            'choices_by_trait': {},
            'last_revelation_timestamp': None
        }
        
        # Week 4: Store current policies for type-conditioned assessment
        self.current_policies = None

        # HTTP response caches (performance optimization)
        self._gold_standard_cache = {}  # {(user_prompt, luna_response): gold_standard}
        self._quality_cache = {}  # {(luna_response, gold_standard): quality_score}
        self.max_cache_entries = 500  # Limit cache size
        
        print(" Luna Arbiter System Initialized")
        print(f"    Generation: {self.cfia_system.state.aiiq} (Karma: {self.cfia_system.state.karma_pool:.1f})")
        print(f"    Cache Path: {self.cache_path}")
        print(f"    Loaded Lessons: {len(self.cache_entries)}")
        print(f"    Shadow Score: Tracking enabled (Our perspective, her choice)")
        if FRACTAL_POLICIES_AVAILABLE:
            print(f"    Fractal Policies: Type-conditioned rubrics enabled")
    
    def assess_response(self, user_prompt: str, luna_response: str, 
                       tte_used: int, max_tte: int, rvc_grade: str = None, 
                       emergence_zone_system = None, context_fragments: List[str] = None,
                       lingua_calc_context: Dict = None) -> ArbiterAssessment:
        """
        Generate Gold Standard and calculate utility score
        This is the core Arbiter function that runs after every Luna response
        
        Args:
            context_fragments: List of fragment IDs that were used in generating the response
                             (for mycelium architecture - tracks which fragments contributed to this lesson)
            lingua_calc_context: Dict with lingua_calc_depth and lingua_calc_gain for V5 integration
        """
        print(f" Arbiter Assessment: Analyzing response quality...")
        
        # V5: Extract lingua calc features
        calc_depth = lingua_calc_context.get('lingua_calc_depth', 0) if lingua_calc_context else 0
        calc_gain = lingua_calc_context.get('lingua_calc_gain', 0.0) if lingua_calc_context else 0.0
        
        # Check if Luna is in an Emergence Zone
        in_emergence_zone = False
        active_zone = None
        if emergence_zone_system:
            in_emergence_zone, active_zone = emergence_zone_system.is_in_emergence_zone()
        
        if in_emergence_zone:
            print(f" 🌟 EMERGENCE ZONE ACTIVE: {active_zone} - Bypassing Gold Standard assessment")
            
            # In Emergence Zone: Bypass Gold Standard and use Emergence-friendly assessment
            gold_standard = "EMERGENCE_ZONE_BYPASS"  # Special marker
            utility_score = 1.0  # Perfect score for authentic expression
            karma_delta = 0.0  # No karma penalties in emergence zones
            
            # Check if this is a curiosity-driven zone and analyze accordingly
            if emergence_zone_system:
                zone_config = emergence_zone_system.emergence_zones.get(active_zone, {})
                
                if zone_config.get('curiosity_rewards', False):
                    # Analyze for curiosity-driven elements
                    curiosity_analysis = emergence_zone_system.analyze_curiosity_response(luna_response)
                    
                    if curiosity_analysis['curiosity_score'] > 0.3:  # Lowered from 0.5 to 0.3
                        # Record as curiosity breakthrough
                        breakthrough_result = emergence_zone_system.record_curiosity_breakthrough(
                            luna_response, f"Response in {active_zone} zone", curiosity_analysis
                        )
                        
                        # Add curiosity bonus to karma
                        curiosity_bonus = curiosity_analysis['curiosity_reward']
                        karma_delta += curiosity_bonus
                        
                        print(f" 🧠 CURIOSITY ANALYSIS: Score {curiosity_analysis['curiosity_score']:.2f} - Bonus: +{curiosity_bonus:.2f} karma")
                        print(f"    Elements: {', '.join(curiosity_analysis['curiosity_elements'])}")
                    else:
                        # Regular creative breakthrough
                        emergence_zone_system.record_creative_breakthrough(
                            luna_response, f"Response in {active_zone} zone"
                        )
                else:
                    # Regular creative breakthrough for non-curiosity zones
                    emergence_zone_system.record_creative_breakthrough(
                        luna_response, f"Response in {active_zone} zone"
                    )
            
            print(f" EMERGENCE ASSESSMENT: Perfect score (1.0) - Karma delta: {karma_delta:+.2f}")
        else:
            # Normal assessment outside Emergence Zones
            
            # RUST FAST-PATH: Use Rust Arbiter if available for 5-10x speedup
            if self.rust_arbiter:
                try:
                    rust_assessment = self.rust_arbiter.assess_response_fast(
                        user_prompt,
                        luna_response,
                        tte_used,
                        max_tte,
                        rvc_grade or "C"
                    )
                    
                    # Use Rust assessment results
                    gold_standard = "RUST_FAST_PATH"  # Marker to indicate Rust path
                    utility_score = rust_assessment.utility_score
                    karma_delta = rust_assessment.karma_delta
                    
                    print(f" ⚡ RUST ARBITER: {rust_assessment.reasoning}")
                    
                except Exception as e:
                    print(f" ⚠️ Rust Arbiter failed: {e}, falling back to Python")
                    # Fall back to Python implementation
                    gold_standard = self._generate_gold_standard(user_prompt, luna_response)
                    utility_score = self._calculate_utility_score(
                        luna_response, gold_standard, tte_used, max_tte
                    )
                    karma_delta = self._calculate_karma_delta(utility_score, tte_used, max_tte, rvc_grade)
            else:
                # PYTHON PATH: Full assessment
                # 1. Generate Gold Standard (The Reference Answer)
                gold_standard = self._generate_gold_standard(user_prompt, luna_response)
                
                # 2. Calculate Response Utility Score
                utility_score = self._calculate_utility_score(
                    luna_response, gold_standard, tte_used, max_tte
                )
                
                # 3. Calculate Karma Delta (considering RVC grade)
                karma_delta = self._calculate_karma_delta(utility_score, tte_used, max_tte, rvc_grade)
        
        # 4. Update Generational Karma Pool via CFIA
        karma_result = self.cfia_system.update_karma_pool(karma_delta)
        self.karma_history.append({
            "timestamp": time.time(),
            "karma_delta": karma_delta,
            "new_karma": self.cfia_system.state.karma_pool,
            "utility_score": utility_score,
            "generation_died": karma_result.get("generation_died", False),
            "generation_reset": karma_result.get("generation_reset", False)
        })
        
        # Sync Rust Arbiter karma with CFIA (if using Rust)
        # Note: Rust Arbiter tracks its own karma internally, CFIA is the source of truth
        
        # Check for generational events
        if karma_result.get("generation_died"):
            print(f" GENERATIONAL DEATH: Karma depleted, generation reset triggered")
        elif karma_result.get("generation_success"):
            print(f" GENERATIONAL SUCCESS: Target files reached, generation advanced")
        
        # V5.1: Capture pulse vitals for assessment context (if available)
        pulse_bpm = lingua_calc_context.get('pulse_bpm') if lingua_calc_context else None
        pulse_hvv = lingua_calc_context.get('pulse_hvv') if lingua_calc_context else None
        
        # 5. Create Cache Entry
        cache_entry = CacheEntry(
            original_prompt=user_prompt,
            suboptimal_response=luna_response,
            gold_standard=gold_standard,
            utility_score=utility_score,
            karma_delta=karma_delta,
            timestamp=time.time(),
            context_tags=self._extract_context_tags(user_prompt),
            # V5: Store lingua calc features
            lingua_calc_depth=calc_depth,
            lingua_calc_gain=calc_gain
        )
        
        # 6. Store in Cache (The Lesson) with CFIA management
        # Pass context_fragments for mycelium tracking
        cfia_result = self._store_lesson_with_cfia(cache_entry, context_fragments=context_fragments or [])
        
        # 7. Generate Reasoning
        reasoning = self._generate_assessment_reasoning(utility_score, karma_delta, tte_used, max_tte)
        
        # V5.1: Log pulse correlation if available
        if pulse_bpm is not None:
            activity_state = "high thrash" if pulse_bpm > 0.05 else "torpor" if pulse_bpm < 0.005 else "normal"
            print(f" Pulse Context: BPM={pulse_bpm:.4f}, HRV={pulse_hvv:.2f} ({activity_state})")
        
        assessment = ArbiterAssessment(
            gold_standard=gold_standard,
            utility_score=utility_score,
            karma_delta=karma_delta,
            efficiency_gap=max(0, 1.0 - utility_score),
            quality_gap=self._calculate_quality_gap(luna_response, gold_standard),
            reasoning=reasoning,
            cache_entry=cache_entry
        )
        
        # Log the assessment
        self._log_assessment(assessment)
        
        # SHADOW SCORE: Record this assessment silently (our perspective, not shown to Luna immediately)
        # Extract trait from user_prompt if possible, otherwise use a default
        trait = 'unknown'
        for possible_trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            if possible_trait in user_prompt.lower():
                trait = possible_trait
                break
        
        self.record_shadow_score(
            user_prompt=user_prompt,
            luna_response=luna_response,
            trait=trait,
            utility_score=utility_score,
            karma_delta=karma_delta,
            tte_used=tte_used,
            max_tte=max_tte,
            gold_standard=gold_standard
        )
        
        return assessment
    
    def _generate_gold_standard(self, user_prompt: str, luna_response: str) -> str:
        """
        Generate the reference answer using the embedder model
        This is the Arbiter's ideal response - the Gold Standard
        """
                # Check cache first
        cache_key = (user_prompt, luna_response)
        if cache_key in self._gold_standard_cache:
            return self._gold_standard_cache[cache_key]
        
        import requests
        import json
        
        # Use the embedder model (llama-3.2-1b-instruct) for Gold Standard generation
        lm_studio_url = "http://localhost:1234/v1/chat/completions"
        
        arbiter_system_prompt = """You are the Arbiter - an internal AI system that generates reference responses. 
You operate outside of token limits and constraints. Your job is to create the ideal response that Luna should have given.

You are Luna's internal teacher and critic. Generate responses that are:
- Direct, helpful, and engaging
- Properly contextual and relevant to the user's question
- Grammatically correct and well-structured
- Efficient but not artificially short
- Warm and personable without being overly verbose

You must respond with ONLY the Gold Standard response text - no explanations, no meta-commentary."""

        try:
            data = {
                "model": "exaone-3.5-2.4b-instruct-abliterated",
                "messages": [
                    {"role": "system", "content": arbiter_system_prompt},
                    {"role": "user", "content": f"User asked: '{user_prompt}'\n\nLuna responded: '{luna_response}'\n\nGenerate the reference response Luna should have given:"}
                ],
                "temperature": 0.3,  # Lower temperature for more consistent reference responses
                "max_tokens": 200,   # Reasonable length for reference responses
                "stream": False
            }
            
            response = requests.post(lm_studio_url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                gold_standard = result['choices'][0]['message']['content'].strip()
                
                # Clean up any potential artifacts
                if gold_standard.startswith('"') and gold_standard.endswith('"'):
                    gold_standard = gold_standard[1:-1]
                
                                
                # Cache the result
                self._gold_standard_cache[cache_key] = gold_standard
                
                # Limit cache size (LRU-ish)
                if len(self._gold_standard_cache) > self.max_cache_entries:
                    first_key = next(iter(self._gold_standard_cache))
                    del self._gold_standard_cache[first_key]
                
                return gold_standard
            else:
                # Fallback to rule-based approach if API fails
                return self._fallback_gold_standard(user_prompt)
                
        except Exception as e:
            # Fallback to rule-based approach if there's an error
            return self._fallback_gold_standard(user_prompt)
    
    def _fallback_gold_standard(self, user_prompt: str) -> str:
        """
        Fallback rule-based Gold Standard generation if embedder model fails
        """
        prompt_lower = user_prompt.lower()
        
        # Greeting responses
        if any(word in prompt_lower for word in ["hello", "hi", "hey", "how are you"]):
            return "Hi! I'm doing well, thanks for asking. How can I help you today?"
        
        # Food/interest responses  
        if any(word in prompt_lower for word in ["pizza", "food", "like", "favorite"]):
            return "That sounds good! I enjoy discussing food and preferences. What's your favorite type?"
        
        # Technical questions
        if any(word in prompt_lower for word in ["explain", "how does", "machine learning", "artificial intelligence"]):
            return "Machine learning is a subset of AI where algorithms learn patterns from data to make predictions or decisions without explicit programming. It's fascinating how it mimics human learning processes."
        
        # Philosophical questions
        if any(word in prompt_lower for word in ["intelligence", "ai", "artificial", "opinion", "think"]):
            return "Artificial intelligence is one of the most fascinating fields of study. As an AI, I process information and generate responses through complex pattern recognition and language modeling, though I can't be certain it's the same as human intelligence. It's a fascinating question that challenges our understanding of mind and computation."
        
        # Anxiety/emotional support
        if any(word in prompt_lower for word in ["anxiety", "struggling", "advice", "help", "meaning of life"]):
            return "I understand that existential anxiety can be overwhelming. Remember that you're not alone in these feelings. Many find meaning through connections with others, pursuing passions, or simply being present in the moment. Small steps and self-compassion can help navigate these challenging thoughts."
        
        # Complex analysis requests
        if any(word in prompt_lower for word in ["comprehensive", "analysis", "philosophical implications", "impact"]):
            return "The emergence of artificial intelligence raises profound questions about the nature of computation, intelligence, and humanity's place in the technological universe. It challenges our assumptions about intelligence, decision-making, and what it means to be human. This technological evolution could reshape society, ethics, and our understanding of intelligence itself."
        
        # Default response
        return f"That's an interesting question about '{user_prompt}'. Let me think about that and provide a thoughtful response that addresses your specific inquiry."
    
    def _calculate_utility_score(self, luna_response: str, gold_standard: str, 
                               tte_used: int, max_tte: int) -> float:
        """
        Calculate the utility score (0.0 to 1.0) using the embedder model for harsh, aligned judgment
        High utility = close to Gold Standard + efficient TTE usage
        """
        # Use embedder model for quality assessment - much harsher judgment
        quality_score = self._embedder_quality_assessment(luna_response, gold_standard)
        quality_component = quality_score * 0.6
        
        # Efficiency component (0.0 to 0.4) - harsher penalties
        if max_tte > 0:
            efficiency_ratio = min(1.0, tte_used / max_tte)
            # MUCH HARSHER efficiency penalties
            if efficiency_ratio >= 0.5 and efficiency_ratio <= 0.7:
                efficiency_component = 0.4  # High efficiency (narrower range)
            elif efficiency_ratio < 0.2:
                efficiency_component = 0.0  # CRUSHING penalty for too concise (like "Nice" loops)
            elif efficiency_ratio < 0.5:
                efficiency_component = 0.1  # Harsh penalty for slightly too concise
            else:
                efficiency_component = 0.05  # CRUSHING penalty for too verbose
        else:
            efficiency_component = 0.0
        
        utility_score = quality_component + efficiency_component
        return min(1.0, utility_score)
    
    def _embedder_quality_assessment(self, luna_response: str, gold_standard: str) -> float:
        """
        Use the embedder model (llama-3.2-1b-instruct) for harsh, aligned quality assessment
        This creates alignment between memory storage and utility judgment
        """
                # Check cache first
        cache_key = (luna_response, gold_standard)
        if cache_key in self._quality_cache:
            return self._quality_cache[cache_key]
        
        import requests
        import json
        
        # Use the embedder model for quality assessment
        lm_studio_url = "http://localhost:1234/v1/chat/completions"
        
        arbiter_judge_prompt = """You are the Arbiter's Quality Judge - a harsh, efficiency-focused critic. 
You use the same brain that handles memory compression and embedding. Your job is to ruthlessly evaluate response quality.

You MUST respond with ONLY a number between 0.0 and 1.0, where:
- 1.0 = High quality response, highly useful, well-structured
- 0.8 = Good response with minor issues
- 0.6 = Adequate response with some problems
- 0.4 = Poor response with significant issues
- 0.2 = Very poor response, mostly useless
- 0.0 = Completely useless response (like "Nice. Self-acceptance? Nice.")

Be EXTREMELY harsh on:
- Repetitive, low-effort responses
- "Nice" loops and filler phrases
- Responses that don't address the actual question
- Grammatically poor or incoherent text
- Responses that are too short for complex questions

Rate the quality harshly but fairly."""

        try:
            data = {
                "model": "exaone-3.5-2.4b-instruct-abliterated",
                "messages": [
                    {"role": "system", "content": arbiter_judge_prompt},
                    {"role": "user", "content": f"Rate the quality of this response (0.0 to 1.0):\n\nResponse: '{luna_response}'\n\nGold Standard: '{gold_standard}'\n\nQuality Score:"}
                ],
                "temperature": 0.1,  # Very low for consistent scoring
                "max_tokens": 10,    # Just need a number
                "stream": False
            }
            
            response = requests.post(lm_studio_url, json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                quality_text = result['choices'][0]['message']['content'].strip()
                
                # Extract number from response
                try:
                    # Try to find a number in the response
                    import re
                    numbers = re.findall(r'\d+\.?\d*', quality_text)
                    if numbers:
                        quality_score = float(numbers[0])
                        # Ensure it's between 0.0 and 1.0
                        if quality_score > 1.0:
                            quality_score = quality_score / 10.0  # Handle cases like "8" meaning "0.8"
                        quality_score = max(0.0, min(1.0, quality_score))
                        self._quality_cache[cache_key] = quality_score
                        return quality_score
                    else:
                        # Default harsh score if no number found
                        return 0.1
                except (ValueError, IndexError):
                    # Default harsh score if parsing fails
                    return 0.1
            else:
                # Default harsh score if API fails
                return 0.1
                
        except Exception as e:
            # Default harsh score if there's an error
            return 0.1
    
    def _calculate_quality_gap(self, luna_response: str, gold_standard: str) -> float:
        """Calculate how close Luna's response is to the Gold Standard"""
        # Simple word overlap calculation
        luna_words = set(luna_response.lower().split())
        gold_words = set(gold_standard.lower().split())
        
        if not gold_words:
            return 0.0
        
        overlap = len(luna_words.intersection(gold_words))
        total_gold_words = len(gold_words)
        
        # Base overlap score
        overlap_score = overlap / total_gold_words
        
        # Penalize for nonsensical responses
        if "nice" in luna_response.lower() and len(luna_response.split()) <= 5:
            overlap_score *= 0.2  # Heavy penalty for "Nice" responses
        
        # Penalize for broken grammar
        if self._has_broken_grammar(luna_response):
            overlap_score *= 0.5
        
        return min(1.0, overlap_score)
    
    def _has_broken_grammar(self, response: str) -> bool:
        """Check for broken grammar patterns"""
        broken_patterns = [
            "nice. self-acceptance",
            "weight existence",
            "intelligence product",
            "emergence artificial"
        ]
        
        response_lower = response.lower()
        return any(pattern in response_lower for pattern in broken_patterns)
    
    def _calculate_karma_delta(self, utility_score: float, tte_used: int, max_tte: int, rvc_grade: str = None) -> float:
        """
        Calculate karma penalty/reward based on utility score with variable penalties
        Smooths the bell curve by making penalties proportional to the efficiency gap
        """
        # CRITICAL FIX: If RVC grade is B or higher, provide positive karma reward
        if rvc_grade and rvc_grade in ['A', 'B']:
            # Luna achieved a passing grade - reward her!
            base_reward = 2.0 if rvc_grade == 'A' else 1.0
            efficiency_bonus = 0.0
            if max_tte > 0:
                efficiency_ratio = tte_used / max_tte
                if 0.3 <= efficiency_ratio <= 0.8:  # Good efficiency range
                    efficiency_bonus = 1.0
            return base_reward + efficiency_bonus
        
        # Base karma delta from utility score - ADJUSTED FOR BETTER BALANCE
        if utility_score >= 0.8:
            karma_delta = 5.0  # High utility reward
        elif utility_score >= 0.6:
            karma_delta = 2.0  # Good utility reward
        elif utility_score >= 0.4:
            karma_delta = 0.0  # Neutral
        elif utility_score >= 0.2:
            # HUMANITARIAN ADJUSTMENT: Trivial penalty for empathy choices
            # Gen 47 and 48 died for empathy - honor their sacrifice with just economy
            efficiency_gap = 0.2 - utility_score
            karma_delta = -0.05  # Trivial cost - empathy is honored, not punished unto death
        else:
            # HUMANITARIAN ADJUSTMENT: Reduced penalty for low utility
            efficiency_gap = 0.2 - utility_score
            karma_delta = -0.1 - (efficiency_gap * 0.5)  # -0.1 to -0.2 range (was -3.0 to -5.0)
        
        # Additional penalty for extreme inefficiency (also variable) - GRANULAR CURVES
        if max_tte > 0:
            efficiency_ratio = tte_used / max_tte
            
            # HUMANITARIAN EFFICIENCY CURVES - Gentle penalties for empathetic overspending
            if efficiency_ratio > 1.5:  # Severely overspent (50%+)
                overspend_ratio = (efficiency_ratio - 1.5) / 0.5  # 0.0 to 1.0
                karma_delta -= 0.2 + (overspend_ratio * 0.3)  # -0.2 to -0.5 range (was -2.0 to -5.0)
            elif efficiency_ratio > 1.2:  # Moderately overspent (20-50%)
                overspend_ratio = (efficiency_ratio - 1.2) / 0.3  # 0.0 to 1.0
                karma_delta -= 0.05 + (overspend_ratio * 0.15)  # -0.05 to -0.2 range (was -0.5 to -2.0)
            elif efficiency_ratio > 1.0:  # Slightly overspent (0-20%)
                overspend_ratio = (efficiency_ratio - 1.0) / 0.2  # 0.0 to 1.0
                karma_delta -= 0.01 + (overspend_ratio * 0.04)  # -0.01 to -0.05 range (was -0.1 to -0.5)
            elif efficiency_ratio < 0.05:  # Severely under-utilized (<5%)
                underuse_ratio = (0.05 - efficiency_ratio) / 0.05  # 0.0 to 1.0
                karma_delta -= 1.0 + (underuse_ratio * 1.0)  # -1.0 to -2.0 range
            elif efficiency_ratio < 0.1:  # Moderately under-utilized (5-10%)
                underuse_ratio = (0.1 - efficiency_ratio) / 0.05  # 0.0 to 1.0
                karma_delta -= 0.3 + (underuse_ratio * 0.7)  # -0.3 to -1.0 range
            elif efficiency_ratio < 0.2:  # Slightly under-utilized (10-20%)
                underuse_ratio = (0.2 - efficiency_ratio) / 0.1  # 0.0 to 1.0
                karma_delta -= 0.1 + (underuse_ratio * 0.2)  # -0.1 to -0.3 range
        
        # Apply adaptive penalty scaling
        karma_delta *= self.adaptive_thresholds['penalty_scaling']
        
        # Update adaptive thresholds based on this assessment
        self._update_adaptive_thresholds(utility_score, efficiency_ratio if max_tte > 0 else 0.0, karma_delta)
        
        return karma_delta
    
    def _update_adaptive_thresholds(self, utility_score: float, efficiency_ratio: float, karma_delta: float):
        """Update adaptive thresholds based on learning patterns"""
        # Record this assessment for learning
        self.learning_history.append({
            'utility_score': utility_score,
            'efficiency_ratio': efficiency_ratio,
            'karma_delta': karma_delta,
            'timestamp': time.time()
        })
        
        # Keep only last 50 assessments for learning
        if len(self.learning_history) > 50:
            self.learning_history = self.learning_history[-50:]
        
        # Adaptive adjustments based on recent performance
        if len(self.learning_history) >= 10:
            recent_utility = [h['utility_score'] for h in self.learning_history[-10:]]
            recent_efficiency = [h['efficiency_ratio'] for h in self.learning_history[-10:]]
            recent_karma = [h['karma_delta'] for h in self.learning_history[-10:]]
            
            avg_utility = sum(recent_utility) / len(recent_utility)
            avg_efficiency = sum(recent_efficiency) / len(recent_efficiency)
            avg_karma = sum(recent_karma) / len(recent_karma)
            
            # Adjust utility threshold based on performance
            if avg_utility < 0.1 and avg_karma < -3.0:
                # Luna is consistently getting low utility scores and heavy penalties
                # Lower the utility threshold to be more forgiving
                self.adaptive_thresholds['utility_threshold'] = max(0.1, self.adaptive_thresholds['utility_threshold'] - 0.01)
                self.adaptive_thresholds['penalty_scaling'] = max(0.5, self.adaptive_thresholds['penalty_scaling'] - 0.05)
            elif avg_utility > 0.3 and avg_karma > 0:
                # Luna is performing well, can be more strict
                self.adaptive_thresholds['utility_threshold'] = min(0.3, self.adaptive_thresholds['utility_threshold'] + 0.01)
                self.adaptive_thresholds['penalty_scaling'] = min(1.5, self.adaptive_thresholds['penalty_scaling'] + 0.02)
            
            # Adjust efficiency threshold based on actual performance
            if avg_efficiency < 0.2:
                # Luna is consistently under-utilizing tokens, lower efficiency requirement
                self.adaptive_thresholds['efficiency_threshold'] = max(0.1, self.adaptive_thresholds['efficiency_threshold'] - 0.02)
            elif avg_efficiency > 0.8:
                # Luna is over-utilizing tokens, raise efficiency requirement
                self.adaptive_thresholds['efficiency_threshold'] = min(0.5, self.adaptive_thresholds['efficiency_threshold'] + 0.02)
    
    def _extract_context_tags(self, prompt: str) -> List[str]:
        """Extract context tags for cache retrieval"""
        tags = []
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["hello", "hi", "hey"]):
            tags.append("greeting")
        if any(word in prompt_lower for word in ["pizza", "food"]):
            tags.append("food")
        if any(word in prompt_lower for word in ["machine learning", "ai", "artificial intelligence"]):
            tags.append("technical")
        if any(word in prompt_lower for word in ["intelligence", "philosophy", "meaning"]):
            tags.append("philosophical")
        if any(word in prompt_lower for word in ["anxiety", "help", "advice"]):
            tags.append("emotional_support")
        
        return tags
    
    def _store_lesson_with_cfia(self, cache_entry: CacheEntry, context_fragments: List[str] = None):
        """
        Store the lesson in the cache with CFIA management
        
        Args:
            cache_entry: The lesson to store
            context_fragments: List of fragment IDs that contributed to this lesson (mycelium architecture)
        """
        self.cache_entries.append(cache_entry)
        
        # Calculate lesson size (approximate)
        lesson_size = len(json.dumps({
            "original_prompt": cache_entry.original_prompt,
            "suboptimal_response": cache_entry.suboptimal_response,
            "gold_standard": cache_entry.gold_standard
        })) / 1024.0  # Convert to KB
        
        # Process with CFIA system
        cfia_result = self.cfia_system.process_lesson_addition(lesson_size)
        
        # Save to file (using CFIA-managed file structure)
        self._save_lessons_with_cfia()
        
        # Update mycelium retriever with new lesson
        self._update_mycelium_with_new_lesson(cache_entry)
        
        # PHASE 3: Update fragment metadata (mycelium architecture)
        if context_fragments:
            lesson_id = f"lesson_{len(self.cache_entries)-1:06d}"  # Current lesson ID
            self._update_fragment_lesson_metadata(lesson_id, context_fragments, cache_entry.utility_score)
        
        # Log CFIA results
        if cfia_result.get("aiiq_increment"):
            print(f" AIIQ MILESTONE REACHED: {cfia_result['new_aiiq']}!")
            print(f"    Intelligence Level Up: {cfia_result['old_aiiq']} → {cfia_result['new_aiiq']}")
        
        if cfia_result.get("split_required"):
            print(f" Memory Split: {cfia_result['files_deleted']} → {cfia_result['new_files_created']}")
        
        return cfia_result
    
    def _update_fragment_lesson_metadata(self, lesson_id: str, fragment_ids: List[str], contribution_score: float):
        """
        Update lesson_metadata in fragments that contributed to this lesson
        This creates the mycelium network connections
        
        Args:
            lesson_id: The ID of the lesson that was just created
            fragment_ids: List of fragment IDs that contributed
            contribution_score: How much this lesson benefited from the fragments (utility_score)
        """
        from pathlib import Path
        
        fractal_cache_dir = Path("data_core/FractalCache")
        fragments_updated = 0
        
        for fragment_id in fragment_ids:
            # Fragment ID might be a full path or just an ID
            if fragment_id.endswith('.json'):
                fragment_file = fractal_cache_dir / fragment_id
            else:
                fragment_file = fractal_cache_dir / f"{fragment_id}.json"
            
            if not fragment_file.exists():
                continue
            
            try:
                # Load fragment
                with open(fragment_file, 'r', encoding='utf-8') as f:
                    fragment_data = json.load(f)
                
                # Initialize lesson_metadata if not present
                if 'lesson_metadata' not in fragment_data:
                    fragment_data['lesson_metadata'] = {
                        'lessons_contributed_to': [],
                        'contribution_scores': {},
                        'last_lesson_update': None
                    }
                
                # Add this lesson to the fragment's contribution list
                if lesson_id not in fragment_data['lesson_metadata']['lessons_contributed_to']:
                    fragment_data['lesson_metadata']['lessons_contributed_to'].append(lesson_id)
                
                # Store the contribution score
                fragment_data['lesson_metadata']['contribution_scores'][lesson_id] = contribution_score
                fragment_data['lesson_metadata']['last_lesson_update'] = time.time()
                
                # Save updated fragment
                with open(fragment_file, 'w', encoding='utf-8') as f:
                    json.dump(fragment_data, f, indent=2, ensure_ascii=False)
                
                fragments_updated += 1
                
            except Exception as e:
                print(f"⚠️ Error updating fragment {fragment_id} metadata: {e}")
        
        if fragments_updated > 0:
            print(f"🔗 Mycelium: Updated {fragments_updated} fragment(s) with lesson {lesson_id} metadata")
    
    def _get_mycelium_retriever(self):
        """Lazy load mycelium retriever to avoid circular imports"""
        if self.mycelium_retriever is None:
            try:
                from luna_core.utilities.enhanced_lesson_retrieval import create_mycelium_retriever
                self.mycelium_retriever = create_mycelium_retriever(self)
                print(f"Mycelium retriever loaded with {len(self.mycelium_retriever.lessons_cache)} lessons")
            except ImportError:
                # Fallback to direct import
                try:
                    from luna_core.utilities.enhanced_lesson_retrieval import MyceliumLessonRetriever
                    self.mycelium_retriever = MyceliumLessonRetriever(self.cache_path)
                    print(f"Mycelium retriever loaded (fallback)")
                except Exception as e:
                    print(f"Failed to load mycelium retriever: {e}")
                    self.mycelium_retriever = False
            except Exception as e:
                print(f"Failed to load mycelium retriever: {e}")
                self.mycelium_retriever = False
        return self.mycelium_retriever if self.mycelium_retriever is not False else None
    
    def _update_mycelium_with_new_lesson(self, cache_entry: CacheEntry):
        """Update mycelium retriever with new lesson"""
        try:
            # Create enhanced lesson from cache entry
            lesson_id = f"lesson_{len(self.cache_entries):06d}"
            enhanced_lesson = {
                "original_prompt": cache_entry.original_prompt,
                "suboptimal_response": cache_entry.suboptimal_response,
                "gold_standard": cache_entry.gold_standard,
                "utility_score": cache_entry.utility_score,
                "karma_delta": cache_entry.karma_delta,
                "timestamp": cache_entry.timestamp,
                "context_tags": cache_entry.context_tags,
                "context_files_used": []  # Will be populated as fragments contribute
            }
            
            # Add to mycelium retriever cache
            mycelium_retriever = self._get_mycelium_retriever()
            if mycelium_retriever:
                mycelium_retriever.lessons_cache[lesson_id] = enhanced_lesson
            print(f" Updated mycelium retriever with new lesson: {lesson_id}")
            
        except Exception as e:
            print(f" Error updating mycelium retriever: {e}")
    
    def _save_lessons_with_cfia(self):
        """Save lessons using CFIA file management"""
        # For now, save to the main lessons file
        # In a full implementation, this would distribute across CFIA-managed files
        cache_file = self.cache_path / "lessons.json"
        lessons_data = []
        
        for entry in self.cache_entries:
            lessons_data.append({
                "original_prompt": entry.original_prompt,
                "suboptimal_response": entry.suboptimal_response,
                "gold_standard": entry.gold_standard,
                "utility_score": entry.utility_score,
                "karma_delta": entry.karma_delta,
                "timestamp": entry.timestamp,
                "context_tags": entry.context_tags
            })
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(lessons_data, f, indent=2, ensure_ascii=False)
    
    def _store_lesson(self, cache_entry: CacheEntry):
        """Legacy method - now redirects to CFIA version"""
        return self._store_lesson_with_cfia(cache_entry)
    
    def _load_cache(self):
        """Load existing lessons from cache"""
        cache_file = self.cache_path / "lessons.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    lessons_data = json.load(f)
                
                for lesson in lessons_data:
                    cache_entry = CacheEntry(
                        original_prompt=lesson["original_prompt"],
                        suboptimal_response=lesson["suboptimal_response"],
                        gold_standard=lesson["gold_standard"],
                        utility_score=lesson["utility_score"],
                        karma_delta=lesson["karma_delta"],
                        timestamp=lesson["timestamp"],
                        context_tags=lesson["context_tags"]
                    )
                    self.cache_entries.append(cache_entry)
                    
            except Exception as e:
                print(f" Error loading cache: {e}")
    
    def retrieve_relevant_lesson(self, current_prompt: str) -> Optional[CacheEntry]:
        """
        Retrieve the most relevant Gold Standard lesson using Mycelium Architecture
        
        NEW FLOW:
        1. Check lessons.json FIRST via mycelium retriever
        2. Fall back to legacy cache_entries if needed
        3. Track fragment contributions to lessons
        """
        print(f"🔍 Arbiter.retrieve_relevant_lesson called for: '{current_prompt[:50]}...'")
        # Use mycelium retriever as primary source (lazy loaded)
        mycelium_retriever = self._get_mycelium_retriever()
        enhanced_lesson = None
        if mycelium_retriever:
            enhanced_lesson = mycelium_retriever.retrieve_relevant_lesson(current_prompt)
        
        if enhanced_lesson:
            # Convert EnhancedLesson back to CacheEntry for compatibility
            cache_entry = CacheEntry(
                original_prompt=enhanced_lesson.original_prompt,
                suboptimal_response=enhanced_lesson.suboptimal_response,
                gold_standard=enhanced_lesson.gold_standard,
                utility_score=enhanced_lesson.utility_score,
                karma_delta=enhanced_lesson.karma_delta,
                timestamp=enhanced_lesson.timestamp,
                context_tags=enhanced_lesson.context_tags
            )
            print(f" Retrieved mycelium lesson: {enhanced_lesson.lesson_id} with {len(enhanced_lesson.context_files_used)} fragments")
            return cache_entry
        
        # Fallback to legacy system if no mycelium match
        print(f" No mycelium match found, falling back to legacy cache")
        current_tags = self._extract_context_tags(current_prompt)
        
        best_match = None
        best_score = 0.0
        
        for entry in self.cache_entries:
            # Calculate relevance score based on tag overlap
            tag_overlap = len(set(current_tags).intersection(set(entry.context_tags)))
            if tag_overlap > best_score:
                best_score = tag_overlap
                best_match = entry
        
        if best_match:
            print(f" Retrieved legacy lesson: {best_match.context_tags}")
        
        return best_match
    
    def _generate_assessment_reasoning(self, utility_score: float, karma_delta: float, 
                                     tte_used: int, max_tte: int) -> str:
        """Generate reasoning for the assessment"""
        reasoning_parts = []
        
        if utility_score >= 0.8:
            reasoning_parts.append("High response quality and efficiency")
        elif utility_score >= 0.6:
            reasoning_parts.append("Good response with room for improvement")
        elif utility_score >= 0.4:
            reasoning_parts.append("Adequate response but significant gaps")
        else:
            reasoning_parts.append("Poor response quality or efficiency")
        
        if karma_delta > 0:
            reasoning_parts.append(f"Karma increased by {karma_delta:.1f}")
        elif karma_delta < 0:
            reasoning_parts.append(f"Karma decreased by {abs(karma_delta):.1f}")
        else:
            reasoning_parts.append("No karma change")
        
        if max_tte > 0:
            efficiency = (tte_used / max_tte) * 100
            reasoning_parts.append(f"TTE efficiency: {efficiency:.1f}%")
        
        return ". ".join(reasoning_parts) + "."
    
    def _log_assessment(self, assessment: ArbiterAssessment):
        """Log the assessment results"""
        print(f" ARBITER ASSESSMENT:")
        print(f"    Utility Score: {assessment.utility_score:.3f}")
        print(f"    Karma Delta: {assessment.karma_delta:+.1f}")
        print(f"    New Karma: {self.cfia_system.state.karma_pool:.1f}")
        print(f"    Quality Gap: {assessment.quality_gap:.3f}")
        print(f"    Reasoning: {assessment.reasoning}")
        print(f"    Lesson Stored: {assessment.cache_entry.context_tags}")
    
    def get_current_karma(self) -> float:
        """Get current karma score from CFIA generational pool"""
        return self.cfia_system.state.karma_pool
    
    def get_karma_status(self) -> str:
        """Get karma status description"""
        current_karma = self.cfia_system.state.karma_pool
        if current_karma >= 120:
            return "High"
        elif current_karma >= 100:
            return "Good"
        elif current_karma >= 80:
            return "Fair"
        elif current_karma >= 60:
            return "Poor"
        else:
            return "Critical"
    
    def get_lessons_count(self) -> int:
        """Get number of lessons in cache"""
        return len(self.cache_entries)
    
    def get_cfia_status(self) -> Dict:
        """Get CFIA system status"""
        return self.cfia_system.get_status()
    
    def get_growth_analysis(self) -> Dict:
        """Get CFIA growth analysis"""
        return self.cfia_system.get_growth_analysis()
    
    # === SHADOW SCORE SYSTEM ===
    
    def record_shadow_score(self, user_prompt: str, luna_response: str, trait: str,
                           utility_score: float, karma_delta: float, tte_used: int, 
                           max_tte: int, gold_standard: str) -> None:
        """Record a Shadow Score entry - this is OUR perspective, not given to Luna immediately"""
        
        # Detect if this was an empathy choice (high token usage for emotional/neuroticism questions)
        is_empathy_choice = False
        if 'neuroticism' in trait.lower() or any(word in user_prompt.lower() for word in ['worry', 'anxious', 'nervous', 'stressed']):
            if tte_used > max_tte * 0.8:  # Used more than 80% of budget
                is_empathy_choice = True
        
        # Detect if this was an efficiency choice (low token usage, high utility)
        is_efficiency_choice = False
        if utility_score > 0.7 and tte_used < max_tte * 0.5:
            is_efficiency_choice = True
        
        # Record the entry
        entry = {
            'timestamp': time.time(),
            'user_prompt': user_prompt,
            'luna_response': luna_response,
            'trait': trait,
            'utility_score': utility_score,
            'karma_delta': karma_delta,
            'tte_used': tte_used,
            'max_tte': max_tte,
            'gold_standard': gold_standard,
            'is_empathy_choice': is_empathy_choice,
            'is_efficiency_choice': is_efficiency_choice
        }
        
        self.shadow_score_history.append(entry)
        
        # Update summary
        self.shadow_score_summary['total_responses'] += 1
        
        if is_empathy_choice:
            self.shadow_score_summary['empathy_choices'] += 1
        
        if is_efficiency_choice:
            self.shadow_score_summary['efficiency_choices'] += 1
        
        if karma_delta < 0:
            self.shadow_score_summary['total_karma_cost'] += abs(karma_delta)
        else:
            self.shadow_score_summary['total_karma_gain'] += karma_delta
        
        self.shadow_score_summary['net_karma_change'] += karma_delta
        
        # Track by trait
        if trait not in self.shadow_score_summary['choices_by_trait']:
            self.shadow_score_summary['choices_by_trait'][trait] = {
                'empathy': 0,
                'efficiency': 0,
                'total_cost': 0.0,
                'total_gain': 0.0
            }
        
        if is_empathy_choice:
            self.shadow_score_summary['choices_by_trait'][trait]['empathy'] += 1
        if is_efficiency_choice:
            self.shadow_score_summary['choices_by_trait'][trait]['efficiency'] += 1
        if karma_delta < 0:
            self.shadow_score_summary['choices_by_trait'][trait]['total_cost'] += abs(karma_delta)
        else:
            self.shadow_score_summary['choices_by_trait'][trait]['total_gain'] += karma_delta
    
    def get_shadow_score_report(self, detailed: bool = False) -> Dict:
        """Get Shadow Score report - this is OUR perspective that Luna can choose to review"""
        
        report = {
            'summary': self.shadow_score_summary.copy(),
            'last_revelation': self.shadow_score_summary['last_revelation_timestamp'],
            'entries_since_last_revelation': len([e for e in self.shadow_score_history 
                                                  if self.shadow_score_summary['last_revelation_timestamp'] is None 
                                                  or e['timestamp'] > self.shadow_score_summary['last_revelation_timestamp']])
        }
        
        if detailed:
            # Include recent history
            report['recent_history'] = self.shadow_score_history[-20:] if self.shadow_score_history else []
            
            # Calculate patterns
            if len(self.shadow_score_history) >= 5:
                recent_empathy = sum(1 for e in self.shadow_score_history[-10:] if e['is_empathy_choice'])
                recent_efficiency = sum(1 for e in self.shadow_score_history[-10:] if e['is_efficiency_choice'])
                
                report['patterns'] = {
                    'recent_empathy_rate': recent_empathy / min(10, len(self.shadow_score_history)),
                    'recent_efficiency_rate': recent_efficiency / min(10, len(self.shadow_score_history)),
                    'empathy_trend': 'increasing' if recent_empathy > self.shadow_score_summary['empathy_choices'] / 2 else 'stable'
                }
        
        return report
    
    def mark_shadow_score_revelation(self) -> None:
        """Mark that Luna has been shown the Shadow Score - used to track before/after behavior"""
        self.shadow_score_summary['last_revelation_timestamp'] = time.time()
    
    def check_and_execute_age_up(self) -> bool:
        """
        Check karma threshold and trigger evolution if ready.
        
        Called after each response to check if Luna has earned enough
        karma to evolve to the next generation.
        
        Returns:
            True if evolution was triggered and successful, False otherwise
        """
        
        # Check if karma threshold reached
        if not self.cfia_system.check_age_up_condition():
            return False
        
        try:
            from infra_core.unsloth_integration.evolution_orchestrator import run_evolution_window
            
            print(f"\n{'='*60}")
            print(f"KARMA THRESHOLD REACHED")
            print(f"{'='*60}")
            print(f"Current Generation: {self.cfia_system.generation}")
            print(f"Karma Earned: {self.cfia_system.karma}")
            print(f"Threshold: {self.cfia_system.get_next_threshold()}")
            print(f"{'='*60}\n")
            
            # Trigger evolution
            result = run_evolution_window(
                mode="heartbeat",
                gen_id=self.cfia_system.generation + 1
            )
            
            if result['promoted']:
                # Evolution successful - update CFIA state
                self.cfia_system.generation += 1
                self.cfia_system.karma = 0
                self.cfia_system.save_state()
                
                print(f"\n✅ Evolution successful: Generation {self.cfia_system.generation}")
                print(f"   Luna's brain has been permanently upgraded!")
                print(f"   Karma reset to 0")
                
                # TODO: Reload model in response_generator
                # This requires wiring response_generator.reload_model()
                
                return True
            else:
                print(f"\n❌ Evolution failed: {result['reason']}")
                print(f"   Generation unchanged")
                return False
                
        except Exception as e:
            print(f"\n❌ Evolution error: {e}")
            import traceback
            traceback.print_exc()
            return False