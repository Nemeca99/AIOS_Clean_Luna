#!/usr/bin/env python3
"""
Luna Question Generator
Generates questions for dream/meditation cycles using LM Studio
"""

import json
import requests
import random
from typing import List, Dict, Optional
from pathlib import Path


class LunaQuestionGenerator:
    """
    Generates questions for Luna's dream/meditation cycles
    Uses LM Studio instead of Questgen to avoid dependencies
    """
    
    def __init__(self, lm_studio_url: str = "http://localhost:1234/v1/chat/completions"):
        self.lm_studio_url = lm_studio_url
        self.question_types = ["introspective", "knowledge_test", "creativity", "memory_recall"]
    
    def generate_random_question(self, context: Optional[str] = None) -> str:
        """
        Generate a random question for imagination/dream mode
        This simulates random dream content - unexpected topics
        
        Args:
            context: Optional context from recent fragments/conversations
            
        Returns:
            A randomly generated question
        """
        
        # Dream prompt - generates unexpected, curious questions
        system_prompt = """Generate ONE creative, unexpected question that someone might randomly think about or dream about. 
Make it interesting but answerable - philosophical, curious, or thought-provoking.
Keep it short (10-20 words max).

Examples:
- "What would you do if you could pause time for 5 minutes?"
- "If you could have dinner with any historical figure, who and why?"
- "What's something you believe that most people disagree with?"
- "If colors had sounds, what would blue sound like?"

Generate ONE question now:"""
        
        try:
            response = requests.post(
                self.lm_studio_url,
                json={
                    "model": "llama-3.2-1b-instruct-abliterated",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Generate a random, interesting question:"}
                    ],
                    "temperature": 0.9,  # High creativity
                    "max_tokens": 50,
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                question = result['choices'][0]['message']['content'].strip()
                # Clean up common artifacts
                question = question.replace('"', '').replace("Question:", "").strip()
                return question
            else:
                # Fallback to hardcoded creative questions
                return self._get_fallback_random_question()
                
        except Exception as e:
            print(f"⚠️ Question generation failed: {e}")
            return self._get_fallback_random_question()
    
    def generate_recall_question(self, past_questions: List[str]) -> Optional[str]:
        """
        Select a past question for introspection/memory testing
        This tests if Luna remembers and stays consistent
        
        Args:
            past_questions: List of questions Luna has been asked before
            
        Returns:
            A randomly selected past question, or None if no history
        """
        if not past_questions:
            return None
        
        # Randomly select from past questions
        return random.choice(past_questions)
    
    def generate_knowledge_test_from_fragment(self, fragment_content: str) -> str:
        """
        Generate a test question from fragment knowledge
        Tests if Luna actually learned from stored fragments
        
        Args:
            fragment_content: Content from a FractalCache fragment
            
        Returns:
            A question that tests understanding of the fragment
        """
        
        system_prompt = f"""Based on this content, generate ONE specific question that tests understanding:

Content: {fragment_content[:300]}

Generate a question that:
- Tests if someone understood the key concept
- Is specific and answerable
- Short (10-20 words max)

Question:"""
        
        try:
            response = requests.post(
                self.lm_studio_url,
                json={
                    "model": "llama-3.2-1b-instruct-abliterated",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Generate the test question:"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 50,
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                question = result['choices'][0]['message']['content'].strip()
                question = question.replace('"', '').replace("Question:", "").strip()
                return question
            else:
                return f"What do you remember about: {fragment_content[:50]}...?"
                
        except Exception as e:
            print(f"⚠️ Knowledge test generation failed: {e}")
            return f"Tell me about: {fragment_content[:50]}...?"
    
    def _get_fallback_random_question(self) -> str:
        """Fallback random questions if generation fails"""
        creative_questions = [
            "What's the most interesting thing you've learned recently?",
            "If you could change one thing about how you think, what would it be?",
            "What's a topic you could talk about for hours?",
            "What makes you most curious?",
            "If you had to explain consciousness in one sentence, what would you say?",
            "What's the difference between knowledge and understanding?",
            "How do you know when you've truly learned something?",
            "What's more important: being right or being curious?",
            "If you could master any skill instantly, what would it be and why?",
            "What's a question you wish people would ask you?",
            "How do you decide what's worth remembering?",
            "What's the relationship between memory and identity?",
            "If you could give advice to a younger version of yourself, what would it be?",
            "What's something you believe strongly but can't prove?",
            "How do you handle being wrong about something important?"
        ]
        
        return random.choice(creative_questions)
    
    def get_past_questions_from_data_core(self, data_core, max_questions: int = 100) -> List[str]:
        """
        Get past questions from lessons for introspection mode
        
        Args:
            data_core: Data Core instance
            max_questions: Max number of questions to retrieve
            
        Returns:
            List of past questions Luna has been asked
        """
        try:
            lessons_file = Path("data_core/ArbiterCache/lessons.json")
            if not lessons_file.exists():
                return []
            
            with open(lessons_file, 'r', encoding='utf-8') as f:
                lessons = json.load(f)
            
            # Extract unique questions
            questions = list(set([lesson.get('original_prompt', '') for lesson in lessons if lesson.get('original_prompt')]))
            
            # Limit and shuffle
            random.shuffle(questions)
            return questions[:max_questions]
            
        except Exception as e:
            print(f"⚠️ Error loading past questions: {e}")
            return []


# Factory function
def create_question_generator() -> LunaQuestionGenerator:
    """Create a question generator instance"""
    return LunaQuestionGenerator()

