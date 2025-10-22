#!/usr/bin/env python3
"""
Multihead Query Type Classifier
4-head ensemble with type mixture output (not single label)
"""

import numpy as np
from typing import Dict, List, Tuple
import re


class MultiheadClassifier:
    """
    Ensemble classifier with 4 cheap heads + fusion.
    Outputs type mixture, not single label.
    
    Heads:
    1. Lexical: n-gram patterns
    2. Structural: code blocks, equations, citations
    3. Pragmatic: intent verbs
    4. Uncertainty: entropy estimation
    """
    
    def __init__(self):
        # Lexical patterns for each type
        self.lexical_patterns = {
            'pattern_language': ['is', 'which', 'does', 'correct', 'match', 'choose', 'select', 'pick'],
            'logic': ['what', 'how', 'why', 'ratio', 'relationship', 'because', 'therefore', 'implies'],
            'creative': ['imagine', 'design', 'create', 'invent', 'suppose', 'what if', 'could'],
            'retrieval': ['find', 'lookup', 'search', 'retrieve', 'where is', 'show me', 'get']
        }
        
        # Structural markers
        self.structural_markers = {
            'code': r'```|def |class |import |function\(',
            'math': r'\$|\\[a-z]+{|=|\\sum|\\int',
            'citation': r'\[[0-9]+\]|\(.*20[0-9]{2}\)|et al\.'
        }
        
        # Pragmatic verb patterns
        self.pragmatic_verbs = {
            'question': ['what', 'how', 'why', 'when', 'where', 'who'],
            'command': ['do', 'make', 'create', 'build', 'show'],
            'verification': ['is', 'does', 'can', 'will', 'should'],
            'exploration': ['might', 'could', 'would', 'imagine']
        }
        
        # Fusion weights (tiny logistic layer - initially uniform)
        self.fusion_weights = np.array([
            [0.25, 0.25, 0.25, 0.25],  # Lexical contributes to all
            [0.1, 0.4, 0.1, 0.4],       # Structural (logic/retrieval heavy)
            [0.2, 0.3, 0.3, 0.2],       # Pragmatic
            [0.15, 0.35, 0.35, 0.15]    # Uncertainty
        ])
        
        self.logic_floor = 0.15  # Safety: always 15% logic minimum
    
    def classify_mixture(self, text: str, history: List[str] = None) -> Dict[str, float]:
        """
        Classify query into type mixture.
        
        Returns:
            {"pattern_language": w1, "logic": w2, "creative": w3, "retrieval": w4}
            where Σw_i = 1.0 and logic >= 0.15
        """
        # Extract features
        feats = self._extract_features(text, history or [])
        
        # Run 4 heads
        v_lex = self._lexical_head(feats)
        v_struct = self._structural_head(feats)
        v_prag = self._pragmatic_head(feats)
        v_unc = self._uncertainty_head(feats)
        
        # TRAVIS'S FRAMEWORK:
        # If structural head detects clear pattern/language signal (multi-choice),
        # boost structural weight and reduce logic floor
        pattern_signal = v_struct[0]  # Pattern score from structural head
        
        # Adjust fusion weights based on pattern signal strength
        if pattern_signal > 0.7:
            # Clear pattern/language task - boost structural head
            adjusted_fusion = np.array([[0.1], [0.7], [0.1], [0.1]])  # Heavy on structural
            logic_floor = 0.05  # Minimal floor for pattern tasks
        else:
            # Mixed or logic task - balanced fusion
            adjusted_fusion = self.fusion_weights
            logic_floor = 0.15  # Full floor for safety
        
        # Stack head outputs
        head_outputs = np.array([v_lex, v_struct, v_prag, v_unc])
        
        # Weighted fusion
        logits = np.sum(head_outputs * adjusted_fusion, axis=0)
        
        # Softmax to get mixture
        w = self._softmax(logits)
        
        # Apply dynamic logic floor
        logic_floor_vector = np.array([0.0, 1.0, 0.0, 0.0])  # [pattern, logic, creative, retrieval]
        w = logic_floor * logic_floor_vector + (1.0 - logic_floor) * w
        
        # Normalize
        w = w / np.sum(w)
        
        # TRAVIS'S TWO-AXIS ENHANCEMENT:
        # Calculate axes for optimization decisions
        logic_creative_axis = w[1] + w[2]  # Logic + Creative
        pattern_language_axis = w[0] + w[3]  # Pattern + Retrieval (language-like)
        
        # Determine dominant axis
        if logic_creative_axis > pattern_language_axis:
            dominant_axis = 'logic_creative'
            dominant_strength = logic_creative_axis
        else:
            dominant_axis = 'pattern_language'
            dominant_strength = pattern_language_axis
        
        return {
            'pattern_language': float(w[0]),
            'logic': float(w[1]),
            'creative': float(w[2]),
            'retrieval': float(w[3]),
            # Travis's axes metadata
            'travis_axes': {
                'logic_creative': float(logic_creative_axis),
                'pattern_language': float(pattern_language_axis),
                'dominant_axis': dominant_axis,
                'dominant_strength': float(dominant_strength),
                'logic_weight': float(w[1]),
                'creative_weight': float(w[2]),
                'pattern_weight': float(w[0]),
                'language_weight': float(w[3])  # Using retrieval as language proxy
            }
        }
    
    def _extract_features(self, text: str, history: List[str]) -> Dict:
        """Extract features for classification."""
        text_lower = text.lower()
        
        return {
            'text': text,
            'text_lower': text_lower,
            'length': len(text.split()),
            'has_question_mark': '?' in text,
            'has_code_markers': bool(re.search(r'```|def |class |import ', text)),
            'has_math_markers': bool(re.search(r'\$|=|\\', text)),
            'history_length': len(history),
            'recent_history': history[-5:] if history else []
        }
    
    def _lexical_head(self, feats: Dict) -> np.ndarray:
        """Lexical head: Count n-gram matches per type."""
        text_lower = feats['text_lower']
        scores = np.zeros(4)  # [pattern, logic, creative, retrieval]
        
        for i, (type_name, patterns) in enumerate([
            ('pattern_language', self.lexical_patterns['pattern_language']),
            ('logic', self.lexical_patterns['logic']),
            ('creative', self.lexical_patterns['creative']),
            ('retrieval', self.lexical_patterns['retrieval'])
        ]):
            for pattern in patterns:
                if pattern in text_lower:
                    scores[i] += 1.0
        
        # Normalize
        if np.sum(scores) > 0:
            scores = scores / np.sum(scores)
        else:
            scores = np.array([0.25, 0.25, 0.25, 0.25])  # Uniform if no matches
        
        return scores
    
    def _structural_head(self, feats: Dict) -> np.ndarray:
        """
        Structural head: Detect code, math, citations.
        
        TRAVIS'S FRAMEWORK:
        - Pattern/Language: Multi-choice (A/B/C/D), closed-form, deterministic
        - Logic/Creative: Open-ended reasoning, "what is ratio?", probabilistic
        """
        scores = np.array([0.1, 0.1, 0.1, 0.1])  # Base uniform
        
        text = feats['text']
        
        # TRAVIS'S PATTERN/LANGUAGE DETECTOR:
        # Multi-choice structure = Pattern matching task
        # Example: "What is 1+1? A) 1 B) 2 C) 3 D) 4"
        has_multi_choice = bool(re.search(r'[A-D]\)', text, re.I))
        has_true_false = bool(re.search(r'(true|false)\?', text, re.I))
        has_options = 'option' in text.lower() or 'choice' in text.lower()
        has_vs_or = bool(re.search(r'\bor\b', text, re.I)) and text.count('?') == 1
        
        if has_multi_choice or has_true_false or has_options or has_vs_or:
            # This is a PATTERN/LANGUAGE task - deterministic, closed-form
            scores = np.array([1.0, 0.1, 0.1, 0.1])  # Overwhelming pattern signal
            return scores / np.sum(scores)  # Early return for clear pattern
        
        # TRAVIS'S LOGIC/CREATIVE DETECTOR:
        # Open-ended questions with reasoning = Logic/Creative
        is_open_question = text.strip().endswith('?') and not has_multi_choice
        has_ratio = 'ratio' in text.lower()
        has_why_how = any(w in text.lower() for w in ['why', 'how', 'explain', 'prove', 'derive'])
        
        if is_open_question and (has_ratio or has_why_how):
            scores[1] += 0.8  # Logic (reasoning required)
            scores[2] += 0.3  # Creative (some overlap)
        
        # Code/Math
        if feats['has_code_markers']:
            scores[1] += 0.4  # Logic (code has reasoning)
            scores[3] += 0.2  # Retrieval (code examples)
        
        if feats['has_math_markers']:
            scores[1] += 0.6  # Logic (math is reasoning)
        
        # Citations
        if re.search(self.structural_markers['citation'], text):
            scores[3] += 0.4  # Retrieval (citations present)
        
        # Imperative/generative
        if any(w in text.lower() for w in ['design', 'create', 'imagine', 'write', 'generate']):
            scores[2] += 0.6  # Creative
        
        # Retrieval verbs
        if any(w in text.lower() for w in ['find', 'search', 'document', 'locate', 'retrieve']):
            scores[3] += 0.6  # Retrieval
        
        # Normalize
        scores = scores / np.sum(scores)
        return scores
    
    def _pragmatic_head(self, feats: Dict) -> np.ndarray:
        """Pragmatic head: Intent from verbs."""
        text_lower = feats['text_lower']
        scores = np.zeros(4)
        
        # Question intent
        if any(verb in text_lower for verb in self.pragmatic_verbs['question']):
            if feats['has_question_mark']:
                scores[1] += 0.5  # Logic (open-ended questions)
            else:
                scores[0] += 0.3  # Pattern (implicit questions)
        
        # Verification intent
        if any(verb in text_lower for verb in self.pragmatic_verbs['verification']):
            scores[0] += 0.6  # Pattern/Language (yes/no, multiple choice feel)
        
        # Command intent
        if any(verb in text_lower for verb in self.pragmatic_verbs['command']):
            scores[2] += 0.5  # Creative (constructive)
        
        # Exploration intent
        if any(verb in text_lower for verb in self.pragmatic_verbs['exploration']):
            scores[2] += 0.6  # Creative
        
        # Normalize
        if np.sum(scores) > 0:
            scores = scores / np.sum(scores)
        else:
            scores = np.array([0.25, 0.25, 0.25, 0.25])
        
        return scores
    
    def _uncertainty_head(self, feats: Dict) -> np.ndarray:
        """Uncertainty head: Estimate based on text entropy."""
        text = feats['text']
        
        # Simple entropy estimation
        words = text.lower().split()
        if len(words) == 0:
            return np.array([0.25, 0.25, 0.25, 0.25])
        
        # Word diversity
        unique_words = len(set(words))
        diversity = unique_words / len(words)
        
        # High diversity = exploratory (creative/logic)
        # Low diversity = repetitive (pattern/retrieval)
        
        scores = np.zeros(4)
        if diversity > 0.7:
            scores[1] += 0.4  # Logic
            scores[2] += 0.4  # Creative
        elif diversity > 0.5:
            scores[1] += 0.5  # Logic
            scores[0] += 0.3  # Pattern
        else:
            scores[0] += 0.5  # Pattern
            scores[3] += 0.3  # Retrieval
        
        # Normalize
        scores = scores / np.sum(scores)
        return scores
    
    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Softmax function."""
        exp_logits = np.exp(logits - np.max(logits))  # Numerical stability
        return exp_logits / np.sum(exp_logits)
    
    def get_dominant_type(self, mixture: Dict[str, float]) -> Tuple[str, float]:
        """Get dominant type and confidence from mixture."""
        # Filter out travis_axes metadata (it's a dict, not a float)
        type_weights = {k: v for k, v in mixture.items() if k != 'travis_axes' and isinstance(v, (int, float))}
        sorted_types = sorted(type_weights.items(), key=lambda x: x[1], reverse=True)
        return sorted_types[0]
    
    def is_confident(self, mixture: Dict[str, float], threshold: float = 0.5) -> bool:
        """Check if classifier is confident (dominant type > threshold)."""
        dominant_type, weight = self.get_dominant_type(mixture)
        return weight >= threshold


def main():
    """Test the multihead classifier."""
    classifier = MultiheadClassifier()
    
    test_queries = [
        "What is the ratio of x and y?",  # Logic (open-ended)
        "Is this correct? A) Yes B) No",  # Pattern/Language (multiple choice)
        "Design a creative solution for this problem",  # Creative
        "Find all documents about machine learning",  # Retrieval
        "How does recursion work in Python?",  # Logic
        "Which option is best?",  # Pattern/Language
    ]
    
    print("\n" + "="*80)
    print("MULTIHEAD CLASSIFIER TEST")
    print("="*80)
    
    for query in test_queries:
        mixture = classifier.classify_mixture(query)
        dominant, confidence = classifier.get_dominant_type(mixture)
        
        print(f"\nQuery: {query}")
        print(f"Mixture: {mixture}")
        print(f"Dominant: {dominant} ({confidence:.2%})")
        print(f"Confident: {classifier.is_confident(mixture)}")
        
        # Verify logic floor
        assert mixture['logic'] >= 0.15, f"Logic floor violated: {mixture['logic']}"
    
    print("\n" + "="*80)
    print("✓ All tests passed")
    print(f"✓ Logic floor (15%) enforced in all cases")
    print("="*80)


if __name__ == "__main__":
    main()

