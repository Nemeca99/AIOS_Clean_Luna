#!/usr/bin/env python3
"""
First Word Selector System
Architecture-based approach to controlling Luna's response trajectory
by selecting the opening word strategically
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class FirstWordSelector:
    """
    Selects the first word of Luna's response using a weighted shopping list
    
    THE FIRST WORD DETERMINES THE TRAJECTORY:
    - "Why/What/How" → Questioning mode (Ava-like, curious)
    - "I'm a" → Template explanation mode (gets stuck in patterns)
    - "Hmmm/Well/Oh" → Thoughtful consideration mode
    - "My/Being" → Direct description mode
    
    Based on interrogative word architecture from linguistics, not math.
    """
    
    def __init__(self, patterns_file: str = "extra/scripts/first_word_patterns.json"):
        self.patterns_file = Path(patterns_file)
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load first word patterns from JSON file"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load first word patterns: {e}")
        
        # Fallback patterns
        return {
            "interrogative_words": {
                "weight": 0.4,
                "patterns": ["Why", "What", "How"]
            },
            "interjections": {
                "weight": 0.3,
                "patterns": ["Hmmm...", "Well"]
            },
            "reflective": {
                "weight": 0.3,
                "patterns": ["I think", "Honestly"]
            }
        }
    
    def select_first_word(self, 
                         question: str,
                         session_memory: Optional[List[Dict]] = None,
                         complexity_tier: str = "LOW") -> Tuple[str, str]:
        """
        Select the first word/phrase for Luna's response
        
        Args:
            question: The user's question
            session_memory: Recent conversation history
            complexity_tier: Complexity tier (affects weights)
        
        Returns:
            Tuple of (selected_word, reasoning)
        """
        
        # Build weighted list of categories
        category_weights = []
        
        for category_name, category_data in self.patterns.items():
            if category_name == "banned_patterns":
                continue  # Skip banned patterns
            
            weight = category_data.get("weight", 0.1)
            
            # Adjust weights based on tier
            if complexity_tier in ["MODERATE", "HIGH", "CRITICAL", "EXTREME"]:
                # Boost interrogative and reflective for complex questions
                if category_name == "interrogative_words":
                    weight *= 1.5
                elif category_name == "reflective":
                    weight *= 1.3
            
            # Adjust weights based on question type
            question_lower = question.lower()
            
            # If user is asking about Luna, boost questioning mode
            identity_keywords = ['you', 'yourself', 'unique', 'different', 'special']
            if any(kw in question_lower for kw in identity_keywords):
                if category_name == "interrogative_words":
                    weight *= 2.0  # Strongly prefer asking back
                elif category_name == "direct_descriptive":
                    weight *= 0.3  # Reduce "I'm a" responses
            
            category_weights.append((category_name, weight))
        
        # Select category using weighted random
        total_weight = sum(w for _, w in category_weights)
        rand = random.uniform(0, total_weight)
        
        cumulative = 0
        selected_category = None
        
        for cat_name, weight in category_weights:
            cumulative += weight
            if rand <= cumulative:
                selected_category = cat_name
                break
        
        if not selected_category:
            selected_category = category_weights[0][0]  # Fallback to first
        
        # Select random word from chosen category
        category_data = self.patterns[selected_category]
        patterns = category_data.get("patterns", [])
        
        if not patterns:
            return "", "No patterns available"
        
        selected_word = random.choice(patterns)
        
        # Build reasoning
        reasoning = f"{selected_category}: '{selected_word}'"
        if complexity_tier in ["MODERATE", "HIGH", "CRITICAL"]:
            reasoning += f" (complex tier boost)"
        
        return selected_word, reasoning
    
    def build_first_word_instruction(self, first_word: str) -> str:
        """
        Build an instruction for the LLM to start with the selected word
        
        Args:
            first_word: The word/phrase to start with
        
        Returns:
            Instruction string to add to system prompt
        """
        return f"\n\nCRITICAL: Start your response with '{first_word}' - this is your opening anchor point."
    
    def is_banned_pattern(self, response: str) -> bool:
        """
        Check if response starts with a banned pattern
        
        Args:
            response: The generated response
        
        Returns:
            True if response uses a banned pattern
        """
        banned = self.patterns.get("banned_patterns", {}).get("patterns", [])
        
        for pattern in banned:
            if response.strip().lower().startswith(pattern.lower()):
                return True
        
        return False

# Singleton instance
_first_word_selector = None

def get_first_word_selector() -> FirstWordSelector:
    """Get or create the singleton first word selector"""
    global _first_word_selector
    if _first_word_selector is None:
        _first_word_selector = FirstWordSelector()
    return _first_word_selector

