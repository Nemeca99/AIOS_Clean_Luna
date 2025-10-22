#!/usr/bin/env python3
"""
Dynamic LLM Parameters System
Adjusts temperature, top_p, top_k, and other LLM settings per message based on context
"""

from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class LLMParameters:
    """Dynamic LLM generation parameters"""
    temperature: float
    top_p: float
    top_k: int
    presence_penalty: float
    frequency_penalty: float
    repetition_penalty: float
    reasoning: str  # Why these parameters were chosen

class DynamicLLMParameterManager:
    """
    Manages dynamic LLM parameters based on conversation context
    
    Adjusts parameters to:
    - Increase creativity for creative/philosophical questions
    - Increase determinism for factual/technical questions
    - Reduce repetition when user asks similar questions
    - Vary responses based on conversation history
    """
    
    def __init__(self):
        # Base parameter sets for different scenarios
        self.parameter_profiles = {
            "deterministic": {
                "temperature": 0.0,
                "top_p": 1.0,
                "top_k": 0,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "repetition_penalty": 1.0,
                "reasoning": "Pure deterministic for factual consistency"
            },
            "balanced": {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 40,
                "presence_penalty": 0.1,
                "frequency_penalty": 0.1,
                "repetition_penalty": 1.1,
                "reasoning": "Balanced for natural conversation"
            },
            "creative": {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 100,
                "presence_penalty": 0.3,
                "frequency_penalty": 0.2,
                "repetition_penalty": 1.15,
                "reasoning": "High creativity for exploration"
            },
            "focused_creative": {
                "temperature": 0.5,
                "top_p": 0.85,
                "top_k": 50,
                "presence_penalty": 0.2,
                "frequency_penalty": 0.15,
                "repetition_penalty": 1.12,
                "reasoning": "Creative but focused responses"
            },
            "anti_repetition": {
                "temperature": 0.4,
                "top_p": 0.92,
                "top_k": 60,
                "presence_penalty": 0.5,
                "frequency_penalty": 0.4,
                "repetition_penalty": 1.3,
                "reasoning": "Strong penalties to avoid repeating phrases"
            }
        }
    
    def get_parameters(self, 
                      question: str,
                      session_memory: Optional[List[Dict]] = None,
                      complexity_tier: str = "LOW") -> LLMParameters:
        """
        Determine optimal LLM parameters based on complexity tier and context
        
        TIER-BASED TEMPERATURE MAPPING:
        - TRIVIAL: 0.0 - 0.25 (deterministic, simple facts)
        - LOW: 0.25 - 0.50 (balanced, daily conversation)
        - MODERATE: 0.50 - 0.75 (creative, interesting topics)
        - HIGH: 0.75 - 1.0 (highly creative, philosophical)
        - CRITICAL/EXTREME: 1.0+ (maximum creativity, deep exploration)
        
        Args:
            question: The current question
            session_memory: Recent conversation history
            complexity_tier: Complexity tier (TRIVIAL, LOW, MODERATE, HIGH, CRITICAL, EXTREME)
        
        Returns:
            LLMParameters with optimized settings
        """
        
        import random
        
        # Map tier to temperature range
        tier_temp_ranges = {
            "TRIVIAL": (0.0, 0.25),
            "LOW": (0.25, 0.50),
            "MODERATE": (0.50, 0.80),  # Increased ceiling for more creativity
            "HIGH": (0.80, 1.1),  # Increased for deeper philosophical thought
            "CRITICAL": (1.1, 1.3),  # Increased for maximum creative expression
            "EXTREME": (1.2, 1.5)  # Fully unleashed for consciousness exploration
        }
        
        # Get temperature range for this tier
        temp_min, temp_max = tier_temp_ranges.get(complexity_tier, (0.25, 0.50))
        
        # Add dynamic variation within the tier range
        # Use session memory length to add entropy
        conversation_entropy = 0.0
        if session_memory:
            # Longer conversations add more variation
            conversation_entropy = min(len(session_memory) * 0.02, 0.1)
        
        # Check for repetition - if repetitive, push toward higher end of range
        is_repetitive = self._check_repetition(question, session_memory)
        repetition_boost = 0.15 if is_repetitive else 0.0
        
        # Calculate dynamic temperature within tier range
        # Use random variation to ensure each response is unique
        tier_position = random.uniform(0.3, 0.9)  # Dynamic position within tier range
        base_temp = temp_min + (temp_max - temp_min) * tier_position
        
        # Apply modifiers
        temperature = min(base_temp + conversation_entropy + repetition_boost, temp_max)
        
        # Map tier to other parameters
        tier_params = {
            "TRIVIAL": {
                "top_p": 0.85,
                "top_k": 20,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "repetition_penalty": 1.0
            },
            "LOW": {
                "top_p": 0.90,
                "top_k": 40,
                "presence_penalty": 0.1,
                "frequency_penalty": 0.1,
                "repetition_penalty": 1.1
            },
            "MODERATE": {
                "top_p": 0.93,
                "top_k": 60,
                "presence_penalty": 0.2,
                "frequency_penalty": 0.15,
                "repetition_penalty": 1.15
            },
            "HIGH": {
                "top_p": 0.95,
                "top_k": 80,
                "presence_penalty": 0.3,
                "frequency_penalty": 0.2,
                "repetition_penalty": 1.2
            },
            "CRITICAL": {
                "top_p": 0.97,
                "top_k": 100,
                "presence_penalty": 0.4,
                "frequency_penalty": 0.25,
                "repetition_penalty": 1.25
            },
            "EXTREME": {
                "top_p": 0.98,
                "top_k": 120,
                "presence_penalty": 0.5,
                "frequency_penalty": 0.3,
                "repetition_penalty": 1.3
            }
        }
        
        # Get parameters for this tier
        params = tier_params.get(complexity_tier, tier_params["LOW"]).copy()
        
        # Apply anti-repetition boost if needed
        if is_repetitive:
            params["presence_penalty"] = min(params["presence_penalty"] + 0.3, 0.7)
            params["frequency_penalty"] = min(params["frequency_penalty"] + 0.2, 0.5)
            params["repetition_penalty"] = min(params["repetition_penalty"] + 0.2, 1.5)
        
        # Add slight random variation to all parameters for true dynamism
        params["top_p"] = min(params["top_p"] + random.uniform(-0.02, 0.02), 0.99)
        params["presence_penalty"] = max(0.0, params["presence_penalty"] + random.uniform(-0.05, 0.05))
        params["frequency_penalty"] = max(0.0, params["frequency_penalty"] + random.uniform(-0.05, 0.05))
        
        # CRITICAL: FIRST WORD DIVERSITY BOOST
        # The first word determines the entire response trajectory
        # Add extra randomness to break "I'm a..." template pattern
        
        # Boost temperature for first token to increase variety
        # This makes the model more likely to start with different words
        first_token_boost = random.uniform(0.0, 0.15)
        temperature = min(temperature + first_token_boost, temp_max)
        
        # Boost presence penalty to discourage repeating the same opening
        params["presence_penalty"] = min(params["presence_penalty"] + 0.2, 0.8)
        
        # Build reasoning
        reasoning = f"{complexity_tier} tier (temp={temperature:.3f})"
        if conversation_entropy > 0:
            reasoning += f" + conv_entropy={conversation_entropy:.2f}"
        if is_repetitive:
            reasoning += " + anti-repetition"
        if first_token_boost > 0:
            reasoning += f" + first_word_boost={first_token_boost:.2f}"
        
        return LLMParameters(
            temperature=temperature,
            top_p=params["top_p"],
            top_k=params["top_k"],
            presence_penalty=params["presence_penalty"],
            frequency_penalty=params["frequency_penalty"],
            repetition_penalty=params["repetition_penalty"],
            reasoning=reasoning
        )
    
    def _check_repetition(self, 
                         question: str, 
                         session_memory: Optional[List[Dict]] = None) -> bool:
        """
        Check if the current question is similar to recent questions
        
        Returns:
            True if repetitive pattern detected
        """
        if not session_memory or len(session_memory) < 2:
            return False
        
        # Get recent questions
        recent_questions = []
        for entry in session_memory[-5:]:  # Last 5 interactions
            if isinstance(entry, dict) and 'question' in entry:
                recent_questions.append(entry['question'].lower())
        
        if not recent_questions:
            return False
        
        # Simple keyword overlap check
        question_words = set(question.lower().split())
        
        for prev_q in recent_questions:
            prev_words = set(prev_q.split())
            overlap = len(question_words & prev_words)
            
            # If more than 50% overlap, consider it repetitive
            if overlap > len(question_words) * 0.5:
                return True
        
        return False
    
    def get_profile_description(self, profile_name: str) -> str:
        """Get human-readable description of a parameter profile"""
        if profile_name in self.parameter_profiles:
            return self.parameter_profiles[profile_name]["reasoning"]
        return "Unknown profile"

# Singleton instance
_dynamic_llm_manager = None

def get_dynamic_llm_manager() -> DynamicLLMParameterManager:
    """Get or create the singleton dynamic LLM manager"""
    global _dynamic_llm_manager
    if _dynamic_llm_manager is None:
        _dynamic_llm_manager = DynamicLLMParameterManager()
    return _dynamic_llm_manager

