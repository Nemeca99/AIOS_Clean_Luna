#!/usr/bin/env python3
"""
Luna Internal Reasoning System

Uses the 120 Big Five questions as an INTERNAL REASONING FRAMEWORK.

Process:
1. User asks a novel question (from 500 good questions or anywhere)
2. Luna finds the closest Big Five question(s) from her 120
3. Luna checks: "Have I answered this Big Five question before?"
   - If NO: She answers the Big Five question FIRST (internal self-reflection)
   - If YES: She uses her previous answer as context
4. Luna uses her Big Five answer to inform her response to the user

This is Luna THINKING THROUGH a question by relating it to her psychological framework.
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class InternalReasoningResult:
    """Result of Luna's internal reasoning process"""
    user_question: str
    matched_bigfive_questions: List[Dict]  # Top matching Big Five questions
    bigfive_answers: List[Dict]  # Luna's answers to those questions
    reasoning_chain: str  # Luna's thought process
    recommended_response_strategy: Dict  # How to respond to user

class LunaInternalReasoningSystem:
    """
    Internal Reasoning System
    
    Uses the 120 Big Five questions as Luna's internal reasoning framework.
    When asked a novel question, she thinks through it by relating it to
    her Big Five personality questions.
    
    This is NOT a test - it's how Luna THINKS.
    """
    
    def __init__(self, trait_classifier=None, personality_system=None):
        self.trait_classifier = trait_classifier
        self.personality_system = personality_system
        
        # Track Luna's Big Five answers (her internal self-knowledge)
        self.bigfive_answer_history = self._load_bigfive_answers()
        
        # Reasoning history (for learning and improvement)
        self.reasoning_history = []
        
        print("🧠 Luna Internal Reasoning System Initialized")
        print("    Strategy: Use Big Five as internal thought framework")
        print("    Process: Novel Question → Find Similar Big Five → Answer Big Five First → Use as Context")
    
    def _load_bigfive_answers(self) -> Dict:
        """Load Luna's previous answers to Big Five questions"""
        answer_file = Path("data_core/FractalCache/luna_bigfive_answers.json")
        
        if answer_file.exists():
            try:
                with open(answer_file, 'r', encoding='utf-8') as f:
                    answers = json.load(f)
                print(f"    Loaded {len(answers)} previous Big Five answers")
                return answers
            except Exception as e:
                print(f"    Warning: Could not load Big Five answers: {e}")
        
        return {}  # Fresh start
    
    def _save_bigfive_answers(self):
        """Save Luna's Big Five answers"""
        answer_file = Path("data_core/FractalCache/luna_bigfive_answers.json")
        answer_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(answer_file, 'w', encoding='utf-8') as f:
                json.dump(self.bigfive_answer_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"    Warning: Could not save Big Five answers: {e}")
    
    def reason_through_question(self, user_question: str) -> InternalReasoningResult:
        """
        Luna's internal reasoning process:
        
        1. Find similar Big Five questions
        2. Check if she's answered them before
        3. If not, answer them first (internal self-reflection)
        4. Use Big Five answers to inform response to user
        """
        
        # Step 1: Find similar Big Five questions using trait classifier
        if not self.trait_classifier:
            return self._fallback_reasoning(user_question)
        
        classification = self.trait_classifier.classify_question(user_question)
        
        # Get top 3 matching Big Five questions
        matched_questions = classification.matched_questions[:3]
        
        # Step 2: Check if Luna has answered these Big Five questions before
        bigfive_answers = []
        unanswered_questions = []
        
        for match in matched_questions:
            q_text = match['bigfive_question']['text']
            q_id = match['bigfive_question']['id']
            
            if q_id in self.bigfive_answer_history:
                # Luna has answered this before
                bigfive_answers.append({
                    'question': q_text,
                    'question_id': q_id,
                    'answer': self.bigfive_answer_history[q_id]['answer'],
                    'trait': match['bigfive_question']['domain'],
                    'timestamp': self.bigfive_answer_history[q_id]['timestamp'],
                    'similarity': match['similarity']
                })
            else:
                # Luna needs to answer this first
                unanswered_questions.append({
                    'question': q_text,
                    'question_id': q_id,
                    'trait': match['bigfive_question']['domain'],
                    'similarity': match['similarity']
                })
        
        # Step 3: Answer unanswered Big Five questions (internal self-reflection)
        if unanswered_questions:
            print(f"    🧠 Internal Reasoning: Luna needs to answer {len(unanswered_questions)} Big Five questions first")
            
            for unanswered in unanswered_questions:
                # Luna answers the Big Five question internally
                internal_answer = self._generate_internal_bigfive_answer(
                    unanswered['question'],
                    unanswered['trait']
                )
                
                # Store the answer
                self.bigfive_answer_history[unanswered['question_id']] = {
                    'answer': internal_answer,
                    'timestamp': time.time(),
                    'trait': unanswered['trait']
                }
                
                # Add to bigfive_answers list
                bigfive_answers.append({
                    'question': unanswered['question'],
                    'question_id': unanswered['question_id'],
                    'answer': internal_answer,
                    'trait': unanswered['trait'],
                    'timestamp': time.time(),
                    'similarity': unanswered['similarity'],
                    'newly_answered': True
                })
            
            # Save updated answers
            self._save_bigfive_answers()
        
        # Step 4: Build reasoning chain
        reasoning_chain = self._build_reasoning_chain(
            user_question,
            matched_questions,
            bigfive_answers
        )
        
        # Step 5: Determine response strategy
        response_strategy = self._determine_response_strategy(
            user_question,
            classification,
            bigfive_answers
        )
        
        # Create result
        result = InternalReasoningResult(
            user_question=user_question,
            matched_bigfive_questions=matched_questions,
            bigfive_answers=bigfive_answers,
            reasoning_chain=reasoning_chain,
            recommended_response_strategy=response_strategy
        )
        
        # Record for learning
        self.reasoning_history.append({
            'user_question': user_question,
            'matched_questions': [m['bigfive_question']['text'] for m in matched_questions],
            'bigfive_answers_used': len(bigfive_answers),
            'newly_answered': len([a for a in bigfive_answers if a.get('newly_answered', False)]),
            'timestamp': time.time()
        })
        
        return result
    
    def _generate_internal_bigfive_answer(self, question: str, trait: str) -> str:
        """
        Generate Luna's internal answer to a Big Five question.
        
        This is Luna answering for HERSELF, not for the user.
        It's her establishing her own position on this psychological dimension.
        """
        
        # Use personality system to generate answer if available
        if self.personality_system:
            # Get Luna's personality weights
            weights = self.personality_system.personality_dna.get('luna_personality', {}).get('personality_weights', {})
            
            # Generate answer based on trait
            trait_weight = weights.get(trait.lower(), 0.5)
            
            # Simple scale: 1-5 (Very Inaccurate to Very Accurate)
            if trait_weight >= 0.8:
                answer_score = 5
                answer_text = "Very Accurate"
            elif trait_weight >= 0.6:
                answer_score = 4
                answer_text = "Moderately Accurate"
            elif trait_weight >= 0.4:
                answer_score = 3
                answer_text = "Neither Accurate nor Inaccurate"
            elif trait_weight >= 0.2:
                answer_score = 2
                answer_text = "Moderately Inaccurate"
            else:
                answer_score = 1
                answer_text = "Very Inaccurate"
            
            return f"{answer_text} (Score: {answer_score}/5, Weight: {trait_weight:.2f})"
        
        # Fallback: Neutral answer
        return "Neither Accurate nor Inaccurate (Score: 3/5)"
    
    def _build_reasoning_chain(self, user_question: str, matched_questions: List[Dict], 
                               bigfive_answers: List[Dict]) -> str:
        """Build Luna's reasoning chain (her thought process)"""
        
        reasoning = f"User Question: '{user_question}'\n\n"
        reasoning += "Internal Reasoning:\n"
        
        for i, answer in enumerate(bigfive_answers, 1):
            similarity = answer['similarity']
            reasoning += f"  {i}. Similar to: '{answer['question']}' ({similarity:.1%} match)\n"
            reasoning += f"     My Answer: {answer['answer']}\n"
            reasoning += f"     Trait: {answer['trait']}\n"
            if answer.get('newly_answered'):
                reasoning += f"     ⚡ NEWLY ANSWERED (internal self-reflection)\n"
            reasoning += "\n"
        
        reasoning += "Therefore: Use my understanding of these traits to inform my response."
        
        return reasoning
    
    def _determine_response_strategy(self, user_question: str, classification, 
                                    bigfive_answers: List[Dict]) -> Dict:
        """Determine how Luna should respond based on her internal reasoning"""
        
        # Base strategy from classification
        strategy = classification.recommended_strategy.copy()
        
        # Enhance with Big Five answer context
        strategy['bigfive_context'] = []
        
        for answer in bigfive_answers:
            strategy['bigfive_context'].append({
                'trait': answer['trait'],
                'my_position': answer['answer'],
                'relevance': answer['similarity']
            })
        
        # Add reasoning guidance
        if len(bigfive_answers) > 0:
            dominant_trait = bigfive_answers[0]['trait']
            strategy['reasoning_guidance'] = (
                f"I've thought through this question by relating it to my {dominant_trait} trait. "
                f"Based on my self-understanding, I should respond with {strategy.get('tone_guidance', 'appropriate')} tone."
            )
        
        return strategy
    
    def _fallback_reasoning(self, user_question: str) -> InternalReasoningResult:
        """Fallback reasoning when trait classifier is not available"""
        return InternalReasoningResult(
            user_question=user_question,
            matched_bigfive_questions=[],
            bigfive_answers=[],
            reasoning_chain="Trait classifier not available - using direct response",
            recommended_response_strategy={}
        )
    
    def get_reasoning_summary(self) -> Dict:
        """Get summary of Luna's reasoning history"""
        if not self.reasoning_history:
            return {
                'total_reasonings': 0,
                'total_bigfive_answered': len(self.bigfive_answer_history),
                'average_matches_used': 0.0
            }
        
        total_matched = sum(r['bigfive_answers_used'] for r in self.reasoning_history)
        total_newly_answered = sum(r['newly_answered'] for r in self.reasoning_history)
        
        return {
            'total_reasonings': len(self.reasoning_history),
            'total_bigfive_answered': len(self.bigfive_answer_history),
            'total_newly_answered_this_session': total_newly_answered,
            'average_matches_used': total_matched / len(self.reasoning_history)
        }

