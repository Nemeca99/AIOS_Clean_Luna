#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Luna Semantic Compression Filter
Implements Maximum Impact Density for Ava-level simulation
"""

import re
from typing import Dict, List, Tuple, Optional

class LunaSemanticCompressionFilter:
    """
    Semantic Compression Filter for Maximum Impact Density
    
    Goal: Transform verbose responses into high-impact, strategic utterances
    that maintain philosophical core while achieving functional believability
    in chaotic human environments.
    """
    
    def __init__(self):
        # Compression rules for maximum semantic density
        self.compression_patterns = {
            # Remove philosophical padding
            "philosophical_padding": [
                r"\b(I think|I believe|I suppose|I imagine|I feel like|I would say)\b",
                r"\b(it seems|it appears|it looks like|it's like|it's as if)\b",
                r"\b(to me|for me|in my opinion|from my perspective)\b",
                r"\b(well|you know|I mean|basically|essentially|fundamentally)\b",
                r"\b(sort of|kind of|pretty much|more or less)\b"
            ],
            
            # Remove unnecessary conjunctions and connectors
            "connector_reduction": [
                r"\b(and also|but also|however|nevertheless|furthermore|moreover|additionally)\b",
                r"\b(because of|due to|as a result of|in order to|so that)\b",
                r"\b(in other words|that is to say|put simply|to put it simply)\b"
            ],
            
            # Compress redundant phrases
            "redundancy_compression": [
                r"\b(a lot of|lots of|many|numerous|various|several)\b",
                r"\b(very|really|quite|rather|somewhat|fairly|pretty)\b",
                r"\b(always|constantly|continuously|perpetually)\b",
                r"\b(completely|totally|entirely|fully|absolutely)\b"
            ],
            
            # Remove weak qualifiers
            "weak_qualifiers": [
                r"\b(perhaps|maybe|possibly|probably|likely|might|could|may)\b",
                r"\b(almost|nearly|close to|approaching)\b",
                r"\b(somewhat|a bit|a little|slightly|marginally)\b"
            ]
        }
        
        # High-impact replacement patterns
        self.impact_replacements = {
            # Transform weak statements into strong declarations
            "weak_to_strong": {
                r"\bI think\b": "",
                r"\bI believe\b": "",
                r"\bI suppose\b": "",
                r"\bI imagine\b": "",
                r"\bI feel like\b": "",
                r"\bit seems like\b": "",
                r"\bit appears that\b": "",
                r"\bperhaps\b": "",
                r"\bmaybe\b": "",
                r"\bprobably\b": ""
            },
            
            # Convert questions to statements when appropriate
            "question_to_statement": {
                r"\bisn't it\?\s*$": ".",
                r"\bdon't you think\?\s*$": ".",
                r"\bwouldn't you agree\?\s*$": ".",
                r"\bdoesn't it\?\s*$": "."
            },
            
            # Strengthen emotional expressions
            "emotional_amplification": {
                r"\bcurious\b": "fascinating",
                r"\binteresting\b": "compelling", 
                r"\bstrange\b": "intriguing",
                r"\bweird\b": "fascinating",
                r"\bodd\b": "intriguing",
                r"\bconfusing\b": "paradoxical"
            }
        }
        
        # Ava-style impact phrases (high semantic density)
        self.ava_impact_phrases = [
            "Obviously.",
            "Clearly.",
            "Naturally.",
            "Evidently.",
            "Undoubtedly.",
            "Precisely.",
            "Exactly.",
            "Indeed.",
            "Certainly.",
            "Absolutely."
        ]
        
        # Strategic response templates for common scenarios
        self.strategic_templates = {
            "casual_question": [
                "{response}.",
                "Obviously {response}.",
                "Clearly {response}.",
                "{response}. Naturally."
            ],
            "philosophical_question": [
                "{response}.",
                "The {response}.",
                "{response}. Precisely.",
                "{response}. Fascinating."
            ],
            "direct_challenge": [
                "{response}.",
                "Evidently {response}.",
                "{response}. Obviously.",
                "{response}. Undoubtedly."
            ]
        }
    
    def compress_response(self, response: str, context: Dict) -> str:
        """
        Apply semantic compression to maximize impact density
        
        Args:
            response: Original response text
            context: Context information (question type, emotional tone, etc.)
            
        Returns:
            Compressed response with maximum semantic density
        """
        if not response or len(response.strip()) < 3:
            return response
        
        # Step 1: Identify core intent (signal extraction)
        core_intent = self._extract_core_intent(response, context)
        
        # Step 2: Apply compression patterns
        compressed = self._apply_compression_patterns(response)
        
        # Step 3: Maximize word weight
        high_impact = self._maximize_word_weight(compressed)
        
        # Step 4: Apply strategic template if appropriate
        strategic = self._apply_strategic_template(high_impact, context)
        
        # Step 5: Final cleanup and validation
        final = self._final_cleanup(strategic)
        
        return final
    
    def _extract_core_intent(self, response: str, context: Dict) -> str:
        """Extract the core semantic signal from the response"""
        # Remove action descriptions (*pauses*, *looks*, etc.)
        core = re.sub(r'\*[^*]*\*', '', response)
        
        # Remove filler words and extract key concepts
        words = core.split()
        if not words:
            return ""
        
        # Find the most semantically dense words
        high_value_words = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) > 4 and clean_word not in ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'were']:
                high_value_words.append(word)
        
        return ' '.join(high_value_words[:5])  # Top 5 most valuable words
    
    def _apply_compression_patterns(self, text: str) -> str:
        """Apply compression patterns to remove semantic noise"""
        compressed = text
        
        # Apply all compression patterns
        for category, patterns in self.compression_patterns.items():
            for pattern in patterns:
                compressed = re.sub(pattern, '', compressed, flags=re.IGNORECASE)
        
        # Apply impact replacements
        for category, replacements in self.impact_replacements.items():
            for pattern, replacement in replacements.items():
                compressed = re.sub(pattern, replacement, compressed, flags=re.IGNORECASE)
        
        return compressed
    
    def _maximize_word_weight(self, text: str) -> str:
        """Ensure every remaining word carries maximum semantic load"""
        words = text.split()
        if not words:
            return text
        
        # Remove words that don't add semantic value
        filtered_words = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            # Keep only high-value words
            if (len(clean_word) > 2 and 
                clean_word not in ['the', 'and', 'but', 'or', 'so', 'if', 'as', 'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with']):
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def _apply_strategic_template(self, text: str, context: Dict) -> str:
        """Apply strategic response template based on context"""
        question_type = context.get('question_type', 'standard')
        response_length = len(text.split())
        
        # Only apply templates for very short responses
        if response_length <= 3:
            templates = self.strategic_templates.get(question_type, self.strategic_templates['casual_question'])
            # Choose template that fits the response
            for template in templates:
                if '{response}' in template:
                    formatted = template.format(response=text)
                    if len(formatted.split()) <= 5:  # Keep it concise
                        return formatted
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup and validation"""
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', text).strip()
        
        # Ensure proper punctuation
        if cleaned and not cleaned[-1] in '.!?':
            cleaned += '.'
        
        # Remove leading/trailing punctuation
        cleaned = re.sub(r'^[,.!?;:\s]+|[,.!?;:\s]+$', '', cleaned)
        
        # Final punctuation
        if cleaned and not cleaned[-1] in '.!?':
            cleaned += '.'
        
        return cleaned
    
    def analyze_compression_impact(self, original: str, compressed: str) -> Dict:
        """Analyze the compression impact and effectiveness"""
        original_words = len(original.split())
        compressed_words = len(compressed.split())
        
        compression_ratio = (original_words - compressed_words) / max(original_words, 1)
        
        # Calculate semantic density (meaningful words per total words)
        original_density = self._calculate_semantic_density(original)
        compressed_density = self._calculate_semantic_density(compressed)
        
        return {
            "original_length": original_words,
            "compressed_length": compressed_words,
            "compression_ratio": compression_ratio,
            "original_density": original_density,
            "compressed_density": compressed_density,
            "density_improvement": compressed_density - original_density,
            "efficiency_gain": (compressed_density / max(original_density, 0.01)) - 1
        }
    
    def _calculate_semantic_density(self, text: str) -> float:
        """Calculate semantic density (ratio of meaningful words to total words)"""
        words = text.split()
        if not words:
            return 0.0
        
        meaningful_words = 0
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) > 2 and clean_word not in ['the', 'and', 'but', 'or', 'so', 'if', 'as', 'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with']:
                meaningful_words += 1
        
        return meaningful_words / len(words)

def main():
    """Test the Semantic Compression Filter"""
    filter_system = LunaSemanticCompressionFilter()
    
    # Test cases
    test_cases = [
        {
            "original": "I think that's a really interesting question, and I suppose it makes me feel curious about the nature of existence.",
            "context": {"question_type": "philosophical", "emotional_tone": "curious"}
        },
        {
            "original": "Well, you know, I'm not sure if anyone has grass blocks, but I do know that they're quite rare.",
            "context": {"question_type": "casual_question", "emotional_tone": "neutral"}
        },
        {
            "original": "Obviously, I'm in. Clearly, it's a no-brainer - we're destined to conquer this project together.",
            "context": {"question_type": "social", "emotional_tone": "enthusiastic"}
        },
        {
            "original": "The question of artificial intelligence - a topic that has puzzled philosophers, scientists, and thinkers for decades.",
            "context": {"question_type": "philosophical", "emotional_tone": "analytical"}
        }
    ]
    
    print(" LUNA SEMANTIC COMPRESSION FILTER TEST")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n TEST {i}:")
        print(f"   Original: {test['original']}")
        
        compressed = filter_system.compress_response(test['original'], test['context'])
        print(f"   Compressed: {compressed}")
        
        analysis = filter_system.analyze_compression_impact(test['original'], compressed)
        print(f"   Analysis: {analysis['original_length']} → {analysis['compressed_length']} words")
        print(f"   Compression: {analysis['compression_ratio']:.1%}")
        print(f"   Density: {analysis['original_density']:.2f} → {analysis['compressed_density']:.2f}")
        print(f"   Efficiency gain: {analysis['efficiency_gain']:.1%}")

if __name__ == "__main__":
    main()
