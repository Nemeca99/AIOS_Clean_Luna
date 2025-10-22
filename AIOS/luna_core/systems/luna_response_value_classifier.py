#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Luna Response Value Classifier (RVC) System
============================================

Implements the Rule of Minimal Sufficient Response by classifying user input
complexity and emotional stakes to determine optimal token allocation.

This system enforces Contextual Resource Allocation - ensuring Luna doesn't
overspend on trivial greetings while reserving lifeblood for high-stakes queries.
"""

import re
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ResponseValueTier(Enum):
    """Response value tiers based on complexity and stakes - BALANCED FOR OPTIMAL MODEL USAGE"""
    TRIVIAL = "trivial"           # 8-15 tokens (greetings, simple acknowledgments)
    LOW = "low"                   # 20-35 tokens (1B daily driver: simple questions, brief responses)
    MODERATE = "moderate"         # 50-80 tokens (transition zone: medium complexity)
    HIGH = "high"                 # 100-200 tokens (20B muscle car: complex topics, emotional support)
    CRITICAL = "critical"         # 200-400 tokens (high-stakes: philosophical, crisis support)
    MAXIMUM = "maximum"           # 500-1000 tokens (maximum: deep analysis, complex reasoning)

@dataclass
class ResponseValueAssessment:
    """Assessment of response value and optimal token allocation"""
    tier: ResponseValueTier
    complexity_score: float
    emotional_stakes: float
    semantic_density: float
    target_token_count: int
    max_token_budget: int
    efficiency_requirement: float
    reasoning: str
    recommended_response_style: str

class LunaResponseValueClassifier:
    """
    Response Value Classifier (RVC) for Contextual Resource Allocation
    
    Enforces the Rule of Minimal Sufficient Response by analyzing user input
    and determining optimal token allocation based on complexity and stakes.
    """
    
    def __init__(self):
        """Initialize the RVC system"""
        # Complexity indicators
        self.complexity_patterns = {
            # High complexity indicators
            "philosophical": [
                r"\b(what is the meaning of life|existential|purpose of existence|nature of reality)\b",
                r"\b(intelligence|existence|reality|truth|wisdom)\b",
                r"\b(paradox|contradiction|irony|sophistication)\b",
                r"\b(comprehensive analysis|philosophical implications|deep understanding)\b"
            ],
            "analytical": [
                r"\b(explain|how does|how do|what is|what are|can you explain|can you describe)\b",
                r"\b(analyze|examine|evaluate|assess|compare|contrast)\b",
                r"\b(cause|effect|consequence|result|outcome)\b",
                r"\b(pattern|trend|correlation|relationship)\b",
                r"\b(hypothesis|theory|concept|framework)\b"
            ],
            "emotional": [
                r"\b(feel|emotion|mood|state|experience)\b",
                r"\b(love|hate|fear|joy|sadness|anger|anxiety)\b",
                r"\b(relationship|connection|bond|attachment)\b",
                r"\b(support|help|comfort|understanding)\b"
            ],
            "technical": [
                r"\b(how to|tutorial|guide|instruction|process)\b",
                r"\b(technical|scientific|mathematical|logical)\b",
                r"\b(algorithm|method|technique|approach)\b",
                r"\b(implementation|execution|performance)\b"
            ]
        }
        
        # Low complexity indicators (trivial responses)
        self.trivial_patterns = [
            r"^(hi|hello|hey|sup|what's up)\b",
            r"^(how are you|how's it going|how do you do)\b",
            r"^(thanks|thank you|thx)\b",
            r"^(ok|okay|alright|sure|yes|no)\b",
            r"^(good|bad|fine|ok|cool)\b",
            r"^(lol|lmao|haha|hehe)\b",
            r"^(bye|goodbye|see you|later)\b"
        ]
        
        # Emotional stakes indicators - ENHANCED FOR BETTER TIER DISTRIBUTION
        self.emotional_stakes_patterns = {
            "high_stakes": [
                r"\b(crisis|emergency|urgent|critical|serious)\b",
                r"\b(problem|issue|challenge|difficulty|struggle)\b",
                r"\b(help|support|advice|guidance|assistance)\b",
                r"\b(personal|private|confidential|sensitive)\b",
                r"\b(important|significant|meaningful|valuable)\b",
                r"\b(anxiety|overwhelmed|drowning|hard time|disappear)\b",
                r"\b(crawl under|blanket|feel like|can't|don't know)\b",
                r"\b(relationship|family|work|health|mental|emotional)\b",
                r"\b(trauma|ptsd|depression|panic|fear|worry)\b"
            ],
            "medium_stakes": [
                r"\b(question|ask|wonder|curious|think|opinion)\b",
                r"\b(like|dislike|prefer|enjoy|hate|love)\b",
                r"\b(experience|feeling|emotion|mood|state)\b"
            ],
            "low_stakes": [
                r"\b(casual|informal|just|simply|basic)\b",
                r"\b(quick|brief|short|simple|easy)\b",
                r"\b(chat|talk|conversation|discussion)\b",
                r"\b(hello|hi|hey|thanks|okay|sure)\b"
            ]
        }
        
        # Token allocation tiers - BALANCED FOR OPTIMAL MODEL USAGE
        self.token_tiers = {
            ResponseValueTier.TRIVIAL: (8, 15),     # Ultra-minimal: greetings, acknowledgments
            ResponseValueTier.LOW: (20, 35),        # Daily driver (1B): simple questions, brief responses
            ResponseValueTier.MODERATE: (50, 80),   # Transition zone: medium complexity
            ResponseValueTier.HIGH: (100, 200),     # Muscle car (20B): complex topics, emotional support
            ResponseValueTier.CRITICAL: (200, 400), # High-stakes: philosophical, crisis support
            ResponseValueTier.MAXIMUM: (500, 1000)  # Maximum: deep analysis, complex reasoning
        }
        
        # Efficiency requirements per tier - BALANCED FOR NEW TOKEN ALLOCATIONS
        self.efficiency_requirements = {
            ResponseValueTier.TRIVIAL: 0.6,    # 60% efficiency for ultra-short responses
            ResponseValueTier.LOW: 0.15,       # 15% efficiency for 1B daily driver responses
            ResponseValueTier.MODERATE: 0.25,  # 25% efficiency for transition zone
            ResponseValueTier.HIGH: 0.14,      # 14% efficiency for 20B muscle car responses (lowered for tuning)
            ResponseValueTier.CRITICAL: 0.15,  # 15% efficiency for high-stakes responses
            ResponseValueTier.MAXIMUM: 0.10    # 10% efficiency for maximum complexity
        }
    
    def classify_response_value(self, user_input: str, context: Dict = None) -> ResponseValueAssessment:
        """
        Classify the response value and determine optimal token allocation
        
        Args:
            user_input: The user's input to analyze
            context: Additional context about the conversation
            
        Returns:
            ResponseValueAssessment with tier, complexity, and token recommendations
        """
        # Normalize input
        normalized_input = user_input.lower().strip()
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(normalized_input)
        
        # Calculate emotional stakes
        emotional_stakes = self._calculate_emotional_stakes(normalized_input)
        
        # Calculate semantic density
        semantic_density = self._calculate_semantic_density(normalized_input)
        
        # Determine response tier
        tier = self._determine_response_tier(complexity_score, emotional_stakes, semantic_density)
        
        # Get token allocation
        target_tokens, max_tokens = self.token_tiers[tier]
        efficiency_requirement = self.efficiency_requirements[tier]
        
        # Generate reasoning
        reasoning = self._generate_reasoning(tier, complexity_score, emotional_stakes, semantic_density)
        
        # Get recommended response style
        response_style = self._get_recommended_response_style(tier, emotional_stakes)
        
        return ResponseValueAssessment(
            tier=tier,
            complexity_score=complexity_score,
            emotional_stakes=emotional_stakes,
            semantic_density=semantic_density,
            target_token_count=target_tokens,
            max_token_budget=max_tokens,
            efficiency_requirement=efficiency_requirement,
            reasoning=reasoning,
            recommended_response_style=response_style
        )
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate complexity score based on linguistic patterns and high-complexity domains"""
        score = 0.0
        
        # Check for trivial patterns (low complexity) - FORCE TRIVIAL TIER
        for pattern in self.trivial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return 0.005  # Force TRIVIAL tier for simple greetings (EVEN LOWER)
        
        # HIGH-COMPLEXITY DOMAINS - REDUCED TO PREVENT OVER-CLASSIFICATION
        high_complexity_domains = {
            "physics": ["quantum mechanics", "relativity theory", "thermodynamics", "electromagnetism", "particle physics"],
            "philosophy": ["meaning of life", "nature of intelligence", "existential reality", "fundamental truth", "free will"],
            "mathematics": ["calculus", "advanced algebra", "complex equation", "mathematical proof", "theoretical formula"],
            "computer_science": ["machine learning", "neural network", "artificial intelligence", "programming", "algorithm", "data"],
            "biology": ["evolutionary biology", "molecular genetics", "cellular biology", "organism development"],
            "chemistry": ["molecular compound", "chemical reaction", "organic synthesis", "catalyst"]
        }
        
        # Check for high-complexity domains first - BOOST SIGNIFICANTLY
        domain_complexity = 0.0
        for domain, keywords in high_complexity_domains.items():
            domain_matches = sum(1 for keyword in keywords if keyword in text.lower())
            if domain_matches > 0:
                domain_complexity = max(domain_complexity, 0.60 + (domain_matches * 0.10))  # Start at 0.60, boost by 0.10 per match (REDUCED)
        
        # Check for high complexity patterns
        for category, patterns in self.complexity_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                if category == "philosophical":
                    score += matches * 0.4
                elif category == "analytical":
                    score += matches * 0.3
                elif category == "emotional":
                    score += matches * 0.2
                elif category == "technical":
                    score += matches * 0.25
        
        # Length factor (but cap it to prevent simple long questions from being complex)
        word_count = len(text.split())
        if word_count > 20:
            score += 0.15  # Reduced from 0.2
        elif word_count > 10:
            score += 0.05  # Reduced from 0.1
        
        # Question complexity
        question_count = text.count('?')
        if question_count > 2:
            score += 0.2  # Reduced from 0.3
        elif question_count > 0:
            score += 0.05  # Reduced from 0.1
        
        # Combine factors - prioritize domain complexity
        if domain_complexity > 0.8:
            # High-complexity domain detected - boost significantly
            final_score = min(1.0, domain_complexity + (score * 0.1))
        else:
            final_score = min(1.0, score)
        
        return final_score
    
    def _calculate_emotional_stakes(self, text: str) -> float:
        """Calculate emotional stakes score - ENHANCED FOR BETTER TIER DISTRIBUTION"""
        score = 0.0
        
        # Check for high stakes indicators
        for pattern in self.emotional_stakes_patterns["high_stakes"]:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * 0.4  # Increased weight for high stakes
        
        # Check for medium stakes indicators
        for pattern in self.emotional_stakes_patterns["medium_stakes"]:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * 0.15  # Moderate weight for medium stakes
        
        # Check for low stakes indicators
        for pattern in self.emotional_stakes_patterns["low_stakes"]:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score -= matches * 0.1
        
        # Personal pronouns increase stakes
        personal_pronouns = len(re.findall(r"\b(i|me|my|myself|you|your|yourself)\b", text, re.IGNORECASE))
        score += personal_pronouns * 0.05
        
        
        return max(0.0, min(1.0, score))
    
    def _calculate_semantic_density(self, text: str) -> float:
        """Calculate semantic density (information per word)"""
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        # Check for trivial patterns first - these should have very low semantic density
        for pattern in self.trivial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return 0.01  # Force very low semantic density for trivial patterns
        
        # Count meaningful words (excluding common words)
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those"}
        
        meaningful_words = [word for word in text.split() if word.lower() not in common_words]
        semantic_density = len(meaningful_words) / word_count
        
        return min(1.0, semantic_density)
    
    def _determine_response_tier(self, complexity: float, emotional_stakes: float, semantic_density: float) -> ResponseValueTier:
        """Determine response tier based on combined scores"""
        # Weighted combination
        combined_score = (complexity * 0.5) + (emotional_stakes * 0.3) + (semantic_density * 0.2)
        
        
        # BALANCED THRESHOLDS FOR OPTIMAL MODEL DISTRIBUTION - ADJUSTED FOR BETTER TIER DISTRIBUTION
        if combined_score >= 0.75:
            return ResponseValueTier.MAXIMUM
        elif combined_score >= 0.55:
            return ResponseValueTier.CRITICAL
        elif combined_score >= 0.35:
            return ResponseValueTier.HIGH      # 20B model territory
        elif combined_score >= 0.25:           # INCREASED from 0.20
            return ResponseValueTier.MODERATE  # Transition zone
        elif combined_score >= 0.12:           # INCREASED from 0.08
            return ResponseValueTier.LOW       # 1B model territory
        else:
            return ResponseValueTier.TRIVIAL   # Simple greetings, acknowledgments
    
    def _generate_reasoning(self, tier: ResponseValueTier, complexity: float, emotional_stakes: float, semantic_density: float) -> str:
        """Generate reasoning for the classification"""
        reasoning_parts = []
        
        if tier == ResponseValueTier.TRIVIAL:
            reasoning_parts.append("Trivial input detected - minimal response required")
        elif tier == ResponseValueTier.LOW:
            reasoning_parts.append("Low complexity input - brief response appropriate")
        elif tier == ResponseValueTier.MODERATE:
            reasoning_parts.append("Moderate complexity - standard response length")
        elif tier == ResponseValueTier.HIGH:
            reasoning_parts.append("High complexity - substantial response justified")
        elif tier == ResponseValueTier.CRITICAL:
            reasoning_parts.append("Critical complexity - high token investment warranted")
        else:
            reasoning_parts.append("Maximum complexity - maximum token allocation")
        
        # Add specific reasoning
        if complexity > 0.5:
            reasoning_parts.append(f"High complexity score: {complexity:.2f}")
        if emotional_stakes > 0.5:
            reasoning_parts.append(f"High emotional stakes: {emotional_stakes:.2f}")
        if semantic_density > 0.5:
            reasoning_parts.append(f"High semantic density: {semantic_density:.2f}")
        
        return " | ".join(reasoning_parts)
    
    def _get_recommended_response_style(self, tier: ResponseValueTier, emotional_stakes: float) -> str:
        """Get recommended response style for the tier"""
        styles = {
            ResponseValueTier.TRIVIAL: "Concise and casual",
            ResponseValueTier.LOW: "Brief and friendly",
            ResponseValueTier.MODERATE: "Balanced and informative",
            ResponseValueTier.HIGH: "Substantial and thoughtful",
            ResponseValueTier.CRITICAL: "Comprehensive and deep",
            ResponseValueTier.MAXIMUM: "Maximum complexity and depth"
        }
        
        base_style = styles[tier]
        
        # Add emotional context
        if emotional_stakes > 0.7:
            base_style += " with high emotional sensitivity"
        elif emotional_stakes > 0.4:
            base_style += " with moderate emotional sensitivity"
        
        return base_style
    
    def get_token_budget_guidance(self, assessment: ResponseValueAssessment) -> str:
        """Get token budget guidance for the assessment"""
        return f"""
TOKEN BUDGET GUIDANCE:
- Tier: {assessment.tier.value.upper()}
- Target Tokens: {assessment.target_token_count}
- Max Budget: {assessment.max_token_budget}
- Efficiency Required: {assessment.efficiency_requirement:.1%}
- Response Style: {assessment.recommended_response_style}

REASONING: {assessment.reasoning}

RULE OF MINIMAL SUFFICIENT RESPONSE:
- Use MINIMAL tokens for TRIVIAL inputs
- Reserve HIGH tokens for CRITICAL inputs
- Maintain EFFICIENCY standards for each tier
- Never overspend on low-value transactions
        """.strip()
    
    def validate_response_efficiency(self, assessment: ResponseValueAssessment, actual_tokens: int, quality_score: float) -> Dict:
        """Validate if response meets efficiency requirements"""
        efficiency = quality_score / max(actual_tokens, 1)
        meets_requirement = efficiency >= assessment.efficiency_requirement
        
        return {
            "meets_efficiency_requirement": meets_requirement,
            "actual_efficiency": efficiency,
            "required_efficiency": assessment.efficiency_requirement,
            "efficiency_gap": assessment.efficiency_requirement - efficiency,
            "token_usage_appropriate": actual_tokens <= assessment.max_token_budget,
            "overspend_penalty": max(0, actual_tokens - assessment.max_token_budget),
            "efficiency_grade": "A" if efficiency >= 0.9 else "B" if efficiency >= 0.8 else "C" if efficiency >= 0.7 else "D" if efficiency >= 0.6 else "F"
        }

def main():
    """Test the Response Value Classifier"""
    rvc = LunaResponseValueClassifier()
    
    # Test cases
    test_cases = [
        "Hey how you doing",
        "What is the relationship between scarcity and functional intelligence?",
        "Can you help me with my homework?",
        "Thanks for the help",
        "I'm feeling really anxious about my future",
        "What's the weather like?",
        "Explain quantum computing in simple terms",
        "Hi there",
        "I need urgent advice about a personal crisis",
        "What's your favorite color?"
    ]
    
    print(" LUNA RESPONSE VALUE CLASSIFIER (RVC) TEST")
    print("=" * 60)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n Test Case {i}: '{test_input}'")
        print("-" * 40)
        
        assessment = rvc.classify_response_value(test_input)
        
        print(f"Tier: {assessment.tier.value.upper()}")
        print(f"Complexity: {assessment.complexity_score:.2f}")
        print(f"Emotional Stakes: {assessment.emotional_stakes:.2f}")
        print(f"Semantic Density: {assessment.semantic_density:.2f}")
        print(f"Target Tokens: {assessment.target_token_count}")
        print(f"Max Budget: {assessment.max_token_budget}")
        print(f"Efficiency Required: {assessment.efficiency_requirement:.1%}")
        print(f"Reasoning: {assessment.reasoning}")
        print(f"Response Style: {assessment.recommended_response_style}")
        
        # Test efficiency validation
        if assessment.tier == ResponseValueTier.TRIVIAL:
            # Test trivial response efficiency
            validation = rvc.validate_response_efficiency(assessment, 3, 0.9)
            print(f"Efficiency Validation: {validation['efficiency_grade']} ({validation['actual_efficiency']:.2f})")
        elif assessment.tier == ResponseValueTier.CRITICAL:
            # Test critical response efficiency
            validation = rvc.validate_response_efficiency(assessment, 200, 0.8)
            print(f"Efficiency Validation: {validation['efficiency_grade']} ({validation['actual_efficiency']:.2f})")

if __name__ == "__main__":
    main()
