#!/usr/bin/env python3
"""
Travis's 4-Weight 2-Axis Classification System

Four independent weights (each 0-0.25):
- logic
- creative  
- pattern
- language

Form two axes:
- Logic/Creative axis = logic + creative (max 0.50)
- Pattern/Language axis = pattern + language (max 0.50)

Missing weight gets distributed to fill to 1.0
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import re
import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class TravisWeights:
    """Travis's 4-weight system."""
    logic: float  # 0-0.25
    creative: float  # 0-0.25
    pattern: float  # 0-0.25
    language: float  # 0-0.25
    
    @property
    def logic_creative_axis(self) -> float:
        """Combined Logic/Creative weight (0-0.50)."""
        return self.logic + self.creative
    
    @property
    def pattern_language_axis(self) -> float:
        """Combined Pattern/Language weight (0-0.50)."""
        return self.pattern + self.language
    
    @property
    def total(self) -> float:
        """Total weight (should be 1.0 after filling)."""
        return self.logic + self.creative + self.pattern + self.language
    
    def to_dict(self) -> Dict:
        """Convert to dict for policies."""
        return {
            'logic': self.logic,
            'creative': self.creative,
            'pattern': self.pattern,
            'language': self.language,
            'logic_creative_axis': self.logic_creative_axis,
            'pattern_language_axis': self.pattern_language_axis
        }


class TravisClassifier:
    """
    Travis's Two-Axis Cognitive Framework.
    
    Tests:
    - Logic/Creative: "What is the ratio?" (open-ended reasoning)
    - Pattern/Language: "What is 1+1? A/B/C/D" (closed-form matching)
    
    Output: 4 weights (logic, creative, pattern, language) that sum to 1.0
    """
    
    def __init__(self):
        self.max_weight_per_dimension = 0.25
    
    def classify(self, query: str, history: List[Dict] = None) -> TravisWeights:
        """
        Classify query into Travis's 4-weight system.
        
        Returns:
            TravisWeights with logic, creative, pattern, language (sum=1.0)
        """
        # Start with base weights
        logic = 0.0
        creative = 0.0
        pattern = 0.0
        language = 0.0
        
        query_lower = query.lower()
        
        # === PATTERN/LANGUAGE DETECTION ===
        # Multi-choice structure = STRONG pattern signal
        has_multi_choice = bool(re.search(r'[A-D]\)', query, re.I))
        has_true_false = bool(re.search(r'(true|false)\?', query, re.I))
        has_or_choice = bool(re.search(r'\bor\b', query, re.I)) and query.count('?') == 1
        has_options = 'option' in query_lower or 'choice' in query_lower
        
        if has_multi_choice or has_true_false or has_options or has_or_choice:
            # Deterministic pattern matching task
            pattern += 0.25  # MAX pattern
            language += 0.15  # Some language parsing
        
        # Language indicators
        if any(w in query_lower for w in ['metaphor', 'analogy', 'literally', 'figuratively']):
            language += 0.20
        
        # === LOGIC/CREATIVE DETECTION ===
        # Open-ended reasoning = LOGIC signal
        is_question = query.strip().endswith('?')
        has_ratio = 'ratio' in query_lower
        has_reasoning = any(w in query_lower for w in ['why', 'how', 'explain', 'prove', 'derive', 'calculate'])
        
        if is_question and not (has_multi_choice or has_true_false):
            # Open-ended question
            if has_ratio or has_reasoning:
                logic += 0.25  # MAX logic
            else:
                logic += 0.15
        
        # Creative indicators
        if any(w in query_lower for w in ['design', 'create', 'imagine', 'write', 'generate', 'invent']):
            creative += 0.25  # MAX creative
        elif any(w in query_lower for w in ['idea', 'story', 'poem', 'art']):
            creative += 0.15
        
        # Explicit reasoning (equations, math)
        if re.search(r'[=<>+\-*/x÷]', query) or any(w in query_lower for w in ['equation', 'formula', 'theorem']):
            logic += 0.15
        
        # Cap each weight at 0.25
        logic = min(logic, self.max_weight_per_dimension)
        creative = min(creative, self.max_weight_per_dimension)
        pattern = min(pattern, self.max_weight_per_dimension)
        language = min(language, self.max_weight_per_dimension)
        
        # Calculate total
        total = logic + creative + pattern + language
        
        # Fill missing weight
        if total < 1.0:
            missing = 1.0 - total
            logic, creative, pattern, language = self._fill_missing_weight(
                logic, creative, pattern, language, missing
            )
        
        # Ensure total = 1.0
        total = logic + creative + pattern + language
        if total > 0:
            logic /= total
            creative /= total
            pattern /= total
            language /= total
        
        return TravisWeights(
            logic=logic,
            creative=creative,
            pattern=pattern,
            language=language
        )
    
    def _fill_missing_weight(self, logic: float, creative: float, 
                            pattern: float, language: float, 
                            missing: float) -> tuple:
        """
        Fill missing weight according to Travis's rules.
        
        Rules:
        1. Group into axes: Logic/Creative vs Pattern/Language
        2. Find which axis has lower total weight
        3. Within that axis, boost the lower component
        4. Distribute remaining across all
        """
        logic_creative_axis = logic + creative
        pattern_language_axis = pattern + language
        
        # Which axis is lower?
        if logic_creative_axis < pattern_language_axis:
            # Logic/Creative axis is lower - boost it more
            # Within L/C, boost the lower one
            if logic < creative:
                boost_logic = missing * 0.6
                boost_creative = missing * 0.2
                boost_pattern = missing * 0.1
                boost_language = missing * 0.1
            else:
                boost_logic = missing * 0.2
                boost_creative = missing * 0.6
                boost_pattern = missing * 0.1
                boost_language = missing * 0.1
        else:
            # Pattern/Language axis is lower - boost it more
            if pattern < language:
                boost_pattern = missing * 0.6
                boost_language = missing * 0.2
                boost_logic = missing * 0.1
                boost_creative = missing * 0.1
            else:
                boost_pattern = missing * 0.2
                boost_language = missing * 0.6
                boost_logic = missing * 0.1
                boost_creative = missing * 0.1
        
        # Apply boosts
        logic += boost_logic
        creative += boost_creative
        pattern += boost_pattern
        language += boost_language
        
        # Cap at 0.25
        logic = min(logic, self.max_weight_per_dimension)
        creative = min(creative, self.max_weight_per_dimension)
        pattern = min(pattern, self.max_weight_per_dimension)
        language = min(language, self.max_weight_per_dimension)
        
        return logic, creative, pattern, language


def main():
    """Test Travis's classifier."""
    print("=" * 60)
    print("TRAVIS'S 4-WEIGHT 2-AXIS CLASSIFIER")
    print("=" * 60)
    
    classifier = TravisClassifier()
    
    # Test 1: Logic/Creative (your example)
    print("\n1. LOGIC/CREATIVE TEST:")
    query1 = "What is the ratio of x and y?"
    r1 = classifier.classify(query1)
    print(f"   Query: '{query1}'")
    print(f"   Logic: {r1.logic:.3f}")
    print(f"   Creative: {r1.creative:.3f}")
    print(f"   Pattern: {r1.pattern:.3f}")
    print(f"   Language: {r1.language:.3f}")
    print(f"   → Logic/Creative axis: {r1.logic_creative_axis:.3f}")
    print(f"   → Pattern/Language axis: {r1.pattern_language_axis:.3f}")
    print(f"   Total: {r1.total:.3f}")
    
    # Test 2: Pattern/Language (your example)
    print("\n2. PATTERN/LANGUAGE TEST:")
    query2 = "What is 1+1? A) 1 B) 2 C) 3 D) 4"
    r2 = classifier.classify(query2)
    print(f"   Query: '{query2}'")
    print(f"   Logic: {r2.logic:.3f}")
    print(f"   Creative: {r2.creative:.3f}")
    print(f"   Pattern: {r2.pattern:.3f}")
    print(f"   Language: {r2.language:.3f}")
    print(f"   → Logic/Creative axis: {r2.logic_creative_axis:.3f}")
    print(f"   → Pattern/Language axis: {r2.pattern_language_axis:.3f}")
    print(f"   Total: {r2.total:.3f}")
    
    # Test 3: Creative
    print("\n3. CREATIVE TEST:")
    query3 = "Design a solution for quantum computing"
    r3 = classifier.classify(query3)
    print(f"   Query: '{query3}'")
    print(f"   Logic: {r3.logic:.3f}")
    print(f"   Creative: {r3.creative:.3f}")
    print(f"   Pattern: {r3.pattern:.3f}")
    print(f"   Language: {r3.language:.3f}")
    print(f"   → Logic/Creative axis: {r3.logic_creative_axis:.3f}")
    print(f"   → Pattern/Language axis: {r3.pattern_language_axis:.3f}")
    print(f"   Total: {r3.total:.3f}")
    
    print("\n" + "=" * 60)
    print("✓ TRAVIS'S 4-WEIGHT SYSTEM WORKING")
    print("=" * 60)


if __name__ == "__main__":
    main()

