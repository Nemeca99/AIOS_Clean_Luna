#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Luna Soul Metric System
Implements controlled imperfection and cognitive friction for authentic human simulation
"""

import random
import time
import re
from typing import Dict, List, Tuple, Optional

class LunaSoulMetricSystem:
    """
    Soul Metric System for controlled imperfection and cognitive friction
    
    Goal: Add the "soul" of human imperfection to Luna's responses while maintaining
    structural integrity. Simulates resource expenditure, cognitive friction,
    and controlled variations that make responses feel authentically human.
    """
    
    def __init__(self):
        # Cognitive friction patterns (simulating mental effort)
        self.cognitive_friction_patterns = {
            # Micro-pauses and hesitations
            "hesitation": [
                "...", "..", "hmm", "well", "um", "uh", "let me think"
            ],
            
            # Intentional ambiguity (simulating struggle to express complex thoughts)
            "semantic_ambiguity": [
                "sort of", "kind of", "in a way", "I guess", "maybe",
                "it's like", "you know", "I mean"
            ],
            
            # Resource expenditure indicators
            "effort_indicators": [
                "trying to", "struggling to", "working on", "figuring out",
                "wrapping my head around", "getting my thoughts together"
            ],
            
            # Fatigue simulation (longer responses show more "effort")
            "fatigue_indicators": [
                "honestly", "to be honest", "frankly", "really",
                "actually", "seriously"
            ]
        }
        
        # Human-like response variations based on emotional stake
        self.response_variations = {
            # Low stake responses (casual, brief, slang-like)
            "low_stake": {
                "length_range": (2, 8),
                "style": "casual",
                "friction_level": 0.1,
                "patterns": ["yeah", "sure", "ok", "got it", "right", "exactly"]
            },
            
            # Medium stake responses (balanced, some effort)
            "medium_stake": {
                "length_range": (6, 15),
                "style": "thoughtful",
                "friction_level": 0.3,
                "patterns": ["I think", "probably", "seems like", "might be"]
            },
            
            # High stake responses (philosophical, more friction, longer)
            "high_stake": {
                "length_range": (12, 25),
                "style": "philosophical",
                "friction_level": 0.6,
                "patterns": ["fascinating", "intriguing", "compelling", "profound"]
            }
        }
        
        # Emotional investment patterns
        self.emotional_investment = {
            "excitement": {
                "indicators": ["!", "amazing", "incredible", "wow", "seriously"],
                "friction_reduction": 0.2  # Less friction when excited
            },
            "uncertainty": {
                "indicators": ["?", "maybe", "perhaps", "not sure", "wondering"],
                "friction_increase": 0.3  # More friction when uncertain
            },
            "confidence": {
                "indicators": ["obviously", "clearly", "definitely", "absolutely"],
                "friction_reduction": 0.1  # Slightly less friction when confident
            },
            "fatigue": {
                "indicators": ["tired", "exhausted", "long day", "struggling"],
                "friction_increase": 0.4  # More friction when fatigued
            }
        }
        
        # Micro-latency simulation (controlled response delays)
        self.micro_latency_config = {
            "base_delay": 0.1,  # Base delay in seconds
            "complexity_multiplier": 0.05,  # Additional delay per complexity point
            "emotional_multiplier": 0.02,  # Additional delay for emotional content
            "random_variance": 0.03  # Random variance for naturalness
        }
        
        # Semantic ambiguity patterns (intentional imprecision)
        self.semantic_ambiguity = {
            "approximations": [
                "about", "around", "roughly", "approximately", "give or take"
            ],
            "uncertainty": [
                "might be", "could be", "possibly", "likely", "probably"
            ],
            "vagueness": [
                "something like", "sort of", "kind of", "in a sense", "to some degree"
            ]
        }
    
    def apply_soul_metrics(self, response: str, context: Dict) -> str:
        """
        Apply soul metrics to make response feel authentically human
        
        Args:
            response: The compressed response
            context: Context including emotional stake, question type, etc.
            
        Returns:
            Response with controlled imperfection and cognitive friction
        """
        if not response or len(response.strip()) < 2:
            return response
        
        # Step 1: Assess emotional stake and determine response variation
        stake_level = self._assess_emotional_stake(context)
        variation_config = self.response_variations[stake_level]
        
        # Step 2: Add cognitive friction based on complexity and stake
        friction_response = self._add_cognitive_friction(response, context, variation_config)
        
        # Step 3: Apply semantic ambiguity for human-like imprecision
        ambiguous_response = self._add_semantic_ambiguity(friction_response, context)
        
        # Step 4: Add micro-latency indicators (ellipsis, pauses)
        latency_response = self._add_micro_latency_indicators(ambiguous_response, context)
        
        # Step 5: Final humanization (remove perfect punctuation, add natural breaks)
        humanized_response = self._humanize_punctuation(latency_response)
        
        return humanized_response
    
    def _assess_emotional_stake(self, context: Dict) -> str:
        """Assess the emotional stake of the response"""
        question_type = context.get('question_type', 'standard')
        emotional_tone = context.get('emotional_tone', 'neutral')
        trait = context.get('trait', 'openness')
        
        # High stake scenarios
        if (question_type == 'philosophical' or 
            emotional_tone in ['vulnerable', 'agitated'] or
            trait in ['conscientiousness', 'neuroticism']):
            return 'high_stake'
        
        # Medium stake scenarios
        elif (question_type in ['social', 'direct_challenge'] or
              emotional_tone in ['curious', 'enthusiastic']):
            return 'medium_stake'
        
        # Low stake scenarios
        else:
            return 'low_stake'
    
    def _add_cognitive_friction(self, response: str, context: Dict, variation_config: Dict) -> str:
        """Add cognitive friction to simulate mental effort"""
        friction_level = variation_config['friction_level']
        
        # Determine if friction should be added based on complexity
        word_count = len(response.split())
        complexity_score = min(word_count / 20, 1.0)  # Normalize complexity
        
        # Add friction if complexity is high or random chance
        if complexity_score > 0.5 or random.random() < friction_level:
            friction_type = random.choice(list(self.cognitive_friction_patterns.keys()))
            friction_pattern = random.choice(self.cognitive_friction_patterns[friction_type])
            
            # Insert friction at natural break points
            if friction_type == "hesitation":
                # Add at beginning or after first word
                if random.random() < 0.5:
                    return f"{friction_pattern} {response}"
                else:
                    words = response.split()
                    if len(words) > 1:
                        words.insert(1, friction_pattern)
                        return " ".join(words)
            
            elif friction_type == "semantic_ambiguity":
                # Add before key words
                words = response.split()
                if len(words) > 2:
                    insert_pos = random.randint(1, len(words) - 1)
                    words.insert(insert_pos, friction_pattern)
                    return " ".join(words)
        
        return response
    
    def _add_semantic_ambiguity(self, response: str, context: Dict) -> str:
        """Add intentional semantic ambiguity for human-like imprecision"""
        # Add approximations or uncertainty markers
        if random.random() < 0.3:  # 30% chance
            ambiguity_type = random.choice(list(self.semantic_ambiguity.keys()))
            ambiguity_word = random.choice(self.semantic_ambiguity[ambiguity_type])
            
            # Insert at natural positions
            words = response.split()
            if len(words) > 1:
                insert_pos = random.randint(0, len(words) - 1)
                words.insert(insert_pos, ambiguity_word)
                return " ".join(words)
        
        return response
    
    def _add_micro_latency_indicators(self, response: str, context: Dict) -> str:
        """Add micro-latency indicators (ellipsis, pauses)"""
        # Add ellipsis for thinking pauses
        if random.random() < 0.2:  # 20% chance
            ellipsis_type = random.choice(['...', '..', '…'])
            
            # Insert at natural break points
            if ',' in response:
                response = response.replace(',', f',{ellipsis_type}', 1)
            elif '.' in response and not response.endswith('.'):
                response = response.replace('.', f'{ellipsis_type}.', 1)
            else:
                # Add at end if no natural break
                response = response.rstrip('.') + f'{ellipsis_type}.'
        
        return response
    
    def _humanize_punctuation(self, response: str) -> str:
        """Humanize punctuation for natural feel"""
        # Remove excessive punctuation
        response = re.sub(r'[!]{2,}', '!', response)
        response = re.sub(r'[?]{2,}', '?', response)
        
        # Add natural punctuation variations
        if response.endswith('.') and random.random() < 0.1:
            # Sometimes use ellipsis instead of period
            response = response[:-1] + '...'
        
        # Add occasional comma variations
        if random.random() < 0.15 and ',' not in response:
            words = response.split()
            if len(words) > 3:
                # Add comma at natural break
                break_point = random.randint(2, len(words) - 2)
                words[break_point] = words[break_point] + ','
                response = ' '.join(words)
        
        return response
    
    def simulate_micro_latency(self, context: Dict) -> float:
        """Simulate micro-latency for response timing"""
        base_delay = self.micro_latency_config['base_delay']
        
        # Calculate complexity-based delay
        complexity_score = len(context.get('response', '').split()) / 20
        complexity_delay = complexity_score * self.micro_latency_config['complexity_multiplier']
        
        # Calculate emotional delay
        emotional_tone = context.get('emotional_tone', 'neutral')
        emotional_delay = 0
        if emotional_tone in ['vulnerable', 'agitated']:
            emotional_delay = self.micro_latency_config['emotional_multiplier']
        
        # Add random variance
        random_variance = random.uniform(
            -self.micro_latency_config['random_variance'],
            self.micro_latency_config['random_variance']
        )
        
        total_delay = base_delay + complexity_delay + emotional_delay + random_variance
        return max(0, total_delay)  # Ensure non-negative
    
    def analyze_soul_metrics(self, original: str, soul_enhanced: str, context: Dict) -> Dict:
        """Analyze the soul metrics applied"""
        # Count friction indicators
        friction_count = 0
        for pattern_list in self.cognitive_friction_patterns.values():
            for pattern in pattern_list:
                friction_count += soul_enhanced.lower().count(pattern.lower())
        
        # Count ambiguity indicators
        ambiguity_count = 0
        for pattern_list in self.semantic_ambiguity.values():
            for pattern in pattern_list:
                ambiguity_count += soul_enhanced.lower().count(pattern.lower())
        
        # Count latency indicators
        latency_count = soul_enhanced.count('...') + soul_enhanced.count('..') + soul_enhanced.count('…')
        
        # Calculate soul score (higher = more human-like imperfection)
        soul_score = (friction_count + ambiguity_count + latency_count) / max(len(soul_enhanced.split()), 1)
        
        return {
            "friction_indicators": friction_count,
            "ambiguity_indicators": ambiguity_count,
            "latency_indicators": latency_count,
            "soul_score": soul_score,
            "emotional_stake": self._assess_emotional_stake(context),
            "human_likeness": "High" if soul_score > 0.1 else "Medium" if soul_score > 0.05 else "Low"
        }

def main():
    """Test the Soul Metric System"""
    soul_system = LunaSoulMetricSystem()
    
    # Test cases
    test_cases = [
        {
            "original": "Obviously.",
            "context": {"question_type": "casual_question", "emotional_tone": "neutral", "trait": "openness"}
        },
        {
            "original": "Fascinating. Curious about existence.",
            "context": {"question_type": "philosophical", "emotional_tone": "curious", "trait": "openness"}
        },
        {
            "original": "I'm here. You're not alone.",
            "context": {"question_type": "emotional", "emotional_tone": "vulnerable", "trait": "agreeableness"}
        },
        {
            "original": "Clearly, we're destined to conquer this.",
            "context": {"question_type": "social", "emotional_tone": "enthusiastic", "trait": "extraversion"}
        }
    ]
    
    print(" LUNA SOUL METRIC SYSTEM TEST")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n TEST {i}:")
        print(f"   Original: {test['original']}")
        
        soul_enhanced = soul_system.apply_soul_metrics(test['original'], test['context'])
        print(f"   Soul Enhanced: {soul_enhanced}")
        
        analysis = soul_system.analyze_soul_metrics(test['original'], soul_enhanced, test['context'])
        print(f"   Analysis:")
        print(f"     Friction: {analysis['friction_indicators']}")
        print(f"     Ambiguity: {analysis['ambiguity_indicators']}")
        print(f"     Latency: {analysis['latency_indicators']}")
        print(f"     Soul Score: {analysis['soul_score']:.3f}")
        print(f"     Human Likeness: {analysis['human_likeness']}")
        print(f"     Emotional Stake: {analysis['emotional_stake']}")

if __name__ == "__main__":
    main()
