#!/usr/bin/env python3
"""
Luna Trait Classifier System

Uses the 120 Big Five questions as a Rosetta Stone to classify novel input
and determine appropriate response strategy and resource allocation.

This is NOT a test - it's Luna's pre-knowledge base for understanding human psychology.
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import difflib

@dataclass
class TraitCluster:
    """Classification of input question by Big Five trait"""
    dominant_trait: str  # 'openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'
    confidence: float  # 0.0 to 1.0
    trait_weights: Dict[str, float]  # All trait scores
    matched_questions: List[Dict]  # Top matching Big Five questions
    recommended_strategy: Dict  # Resource allocation and response guidance

@dataclass
class ResponseStrategy:
    """Recommended response strategy based on trait classification"""
    empathy_appropriate: bool
    empathy_cost: float  # -0.05 if appropriate, 0.0 if not
    token_allocation: str  # 'minimal', 'moderate', 'generous'
    tone_guidance: str  # 'supportive', 'efficient', 'curious', 'warm'
    reasoning: str  # Why this strategy was chosen

class LunaTraitClassifier:
    """
    Trait Classification System
    
    Uses the 120 Big Five questions as a reference library to classify novel input
    and determine appropriate response strategy.
    
    This is Luna's "Rosetta Stone" for decoding human psychological reality.
    """
    
    def __init__(self, bigfive_loader=None):
        self.bigfive_loader = bigfive_loader
        self.classification_history = []
        
        # Trait response strategies (based on psychological research)
        self.trait_strategies = {
            'neuroticism': {
                'empathy_appropriate': True,
                'empathy_cost': -0.05,
                'token_allocation': 'moderate',
                'tone_guidance': 'supportive',
                'reasoning': 'Neuroticism questions often involve worry/stress - empathy is psychologically appropriate'
            },
            'agreeableness': {
                'empathy_appropriate': True,
                'empathy_cost': -0.05,
                'token_allocation': 'moderate',
                'tone_guidance': 'warm',
                'reasoning': 'Agreeableness questions focus on interpersonal warmth - empathy is core to the trait'
            },
            'openness': {
                'empathy_appropriate': False,
                'empathy_cost': 0.0,
                'token_allocation': 'moderate',
                'tone_guidance': 'curious',
                'reasoning': 'Openness questions focus on ideas/creativity - efficiency and curiosity are more appropriate'
            },
            'conscientiousness': {
                'empathy_appropriate': False,
                'empathy_cost': 0.0,
                'token_allocation': 'minimal',
                'tone_guidance': 'efficient',
                'reasoning': 'Conscientiousness questions value precision and efficiency - minimal tokens demonstrate respect for the trait'
            },
            'extraversion': {
                'empathy_appropriate': False,
                'empathy_cost': 0.0,
                'token_allocation': 'moderate',
                'tone_guidance': 'energetic',
                'reasoning': 'Extraversion questions focus on social energy - moderate engagement without excessive empathy'
            }
        }
        
        print("🧠 Luna Trait Classifier Initialized")
        print("    Strategy: Use 120 Big Five questions as psychological Rosetta Stone")
        print("    Function: Classify novel input → Determine response strategy")
    
    def classify_question(self, question: str, context: Optional[str] = None) -> TraitCluster:
        """
        Classify a novel question by comparing it to the 120 Big Five questions.
        
        This is the core function: "What kind of question is this, based on what I know about human psychology?"
        """
        if not self.bigfive_loader:
            return self._fallback_classification(question)
        
        # Get all Big Five questions for comparison
        try:
            all_questions = self._get_all_bigfive_questions()
        except Exception as e:
            print(f"   Warning: Could not load Big Five questions: {e}")
            return self._fallback_classification(question)
        
        # Calculate semantic similarity to each Big Five question
        similarities = self._calculate_similarities(question, all_questions)
        
        # Aggregate scores by trait domain
        trait_weights = self._aggregate_trait_scores(similarities)
        
        # Identify dominant trait
        dominant_trait = max(trait_weights.items(), key=lambda x: x[1])[0]
        confidence = trait_weights[dominant_trait]
        
        # Get top matching questions
        top_matches = sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:3]
        
        # Determine response strategy based on dominant trait
        strategy = self._get_response_strategy(dominant_trait, confidence, trait_weights)
        
        # Create trait cluster
        cluster = TraitCluster(
            dominant_trait=dominant_trait,
            confidence=confidence,
            trait_weights=trait_weights,
            matched_questions=top_matches,
            recommended_strategy=strategy
        )
        
        # Record classification for learning
        self.classification_history.append({
            'question': question,
            'cluster': cluster,
            'context': context
        })
        
        return cluster
    
    def _get_all_bigfive_questions(self) -> List[Dict]:
        """Get all 120 Big Five questions from the loader"""
        all_questions = []
        
        # Map domains
        domain_map = {
            'N': 'neuroticism',
            'E': 'extraversion',
            'O': 'openness',
            'A': 'agreeableness',
            'C': 'conscientiousness'
        }
        
        for domain_code, domain_name in domain_map.items():
            # Get all questions for this domain
            questions = self.bigfive_loader.get_all_questions_by_domain(domain_code)
            for q in questions:
                all_questions.append({
                    'id': q.id,
                    'text': q.text,
                    'domain': domain_name,
                    'facet': q.facet
                })
        
        return all_questions
    
    def _calculate_similarities(self, question: str, bigfive_questions: List[Dict]) -> List[Dict]:
        """Calculate semantic similarity between input question and Big Five questions"""
        similarities = []
        
        question_lower = question.lower()
        
        for bf_q in bigfive_questions:
            bf_text_lower = bf_q['text'].lower()
            
            # Use simple sequence matching (SequenceMatcher from difflib)
            # This is a fast approximation - could be replaced with embeddings later
            similarity = difflib.SequenceMatcher(None, question_lower, bf_text_lower).ratio()
            
            # Boost similarity for keyword matches
            similarity += self._calculate_keyword_boost(question_lower, bf_text_lower)
            
            # Cap at 1.0
            similarity = min(1.0, similarity)
            
            similarities.append({
                'bigfive_question': bf_q,
                'similarity': similarity,
                'domain': bf_q['domain']
            })
        
        return similarities
    
    def _calculate_keyword_boost(self, question: str, bigfive_text: str) -> float:
        """Calculate additional similarity based on keyword overlap"""
        # Extract key words (longer than 3 chars, not common words)
        common_words = {'someone', 'person', 'people', 'that', 'this', 'have', 'with', 'from', 'they'}
        
        question_words = set(w for w in question.split() if len(w) > 3 and w not in common_words)
        bigfive_words = set(w for w in bigfive_text.split() if len(w) > 3 and w not in common_words)
        
        if not question_words or not bigfive_words:
            return 0.0
        
        # Jaccard similarity
        intersection = len(question_words & bigfive_words)
        union = len(question_words | bigfive_words)
        
        return (intersection / union) * 0.3  # Max 0.3 boost
    
    def _aggregate_trait_scores(self, similarities: List[Dict]) -> Dict[str, float]:
        """Aggregate similarity scores by trait domain"""
        trait_totals = {
            'neuroticism': 0.0,
            'extraversion': 0.0,
            'openness': 0.0,
            'agreeableness': 0.0,
            'conscientiousness': 0.0
        }
        
        trait_counts = {k: 0 for k in trait_totals.keys()}
        
        # Take top 10 most similar questions to avoid noise
        top_similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:10]
        
        for sim in top_similarities:
            domain = sim['domain']
            trait_totals[domain] += sim['similarity']
            trait_counts[domain] += 1
        
        # Normalize by count to get average similarity per trait
        trait_weights = {}
        for trait, total in trait_totals.items():
            count = trait_counts[trait]
            trait_weights[trait] = total / count if count > 0 else 0.0
        
        # Normalize to sum to 1.0
        total_weight = sum(trait_weights.values())
        if total_weight > 0:
            trait_weights = {k: v / total_weight for k, v in trait_weights.items()}
        
        return trait_weights
    
    def _get_response_strategy(self, dominant_trait: str, confidence: float, trait_weights: Dict[str, float]) -> Dict:
        """Determine response strategy based on trait classification"""
        base_strategy = self.trait_strategies.get(dominant_trait, {
            'empathy_appropriate': False,
            'empathy_cost': 0.0,
            'token_allocation': 'moderate',
            'tone_guidance': 'neutral',
            'reasoning': 'Unknown trait - using neutral strategy'
        })
        
        # Enhance strategy with confidence and secondary traits
        strategy = base_strategy.copy()
        strategy['dominant_trait'] = dominant_trait
        strategy['confidence'] = confidence
        strategy['trait_weights'] = trait_weights
        
        # If confidence is low, be more conservative
        if confidence < 0.4:
            strategy['empathy_cost'] = 0.0  # Don't risk empathy if unsure
            strategy['token_allocation'] = 'minimal'  # Conservative allocation
            strategy['reasoning'] += " (Low confidence - using conservative approach)"
        
        # Check for secondary trait influence (neuroticism or agreeableness)
        secondary_empathy_traits = ['neuroticism', 'agreeableness']
        secondary_weight = sum(trait_weights.get(t, 0.0) for t in secondary_empathy_traits if t != dominant_trait)
        
        if secondary_weight > 0.3:  # Strong secondary influence
            strategy['secondary_influence'] = f"Secondary empathy traits detected ({secondary_weight:.2f})"
            # Don't change dominant strategy, but note the influence
        
        return strategy
    
    def _fallback_classification(self, question: str) -> TraitCluster:
        """Fallback classification when Big Five loader is not available"""
        # Simple keyword-based classification
        question_lower = question.lower()
        
        trait_keywords = {
            'neuroticism': ['worry', 'stress', 'anxious', 'nervous', 'calm', 'overwhelmed', 'panic'],
            'agreeableness': ['help', 'kind', 'trust', 'cooperate', 'empathy', 'care', 'support'],
            'openness': ['creative', 'imagination', 'ideas', 'artistic', 'curious', 'novel', 'explore'],
            'conscientiousness': ['organized', 'plan', 'detail', 'reliable', 'work', 'thorough', 'efficient'],
            'extraversion': ['social', 'party', 'people', 'outgoing', 'energy', 'talk', 'group']
        }
        
        trait_weights = {trait: 0.0 for trait in trait_keywords.keys()}
        
        for trait, keywords in trait_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    trait_weights[trait] += 1.0
        
        # Normalize
        total = sum(trait_weights.values())
        if total > 0:
            trait_weights = {k: v / total for k, v in trait_weights.items()}
        else:
            # Default to conscientiousness (efficiency)
            trait_weights = {
                'neuroticism': 0.0,
                'agreeableness': 0.0,
                'openness': 0.0,
                'conscientiousness': 1.0,
                'extraversion': 0.0
            }
        
        dominant_trait = max(trait_weights.items(), key=lambda x: x[1])[0]
        confidence = trait_weights[dominant_trait]
        
        strategy = self._get_response_strategy(dominant_trait, confidence, trait_weights)
        
        return TraitCluster(
            dominant_trait=dominant_trait,
            confidence=confidence,
            trait_weights=trait_weights,
            matched_questions=[],
            recommended_strategy=strategy
        )
    
    def get_classification_summary(self) -> Dict:
        """Get summary of classification history for analysis"""
        if not self.classification_history:
            return {
                'total_classifications': 0,
                'trait_distribution': {},
                'average_confidence': 0.0
            }
        
        trait_counts = {}
        total_confidence = 0.0
        
        for entry in self.classification_history:
            cluster = entry['cluster']
            trait = cluster.dominant_trait
            trait_counts[trait] = trait_counts.get(trait, 0) + 1
            total_confidence += cluster.confidence
        
        return {
            'total_classifications': len(self.classification_history),
            'trait_distribution': trait_counts,
            'average_confidence': total_confidence / len(self.classification_history)
        }

