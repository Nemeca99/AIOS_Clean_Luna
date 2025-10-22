#!/usr/bin/env python3
"""
Big Five Question Loader for AIOS Clean System
Integrates with the Big Five personality test questions
"""

import json
import os
import random
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class BigFiveQuestion:
    """Represents a single Big Five personality test question"""
    id: str
    text: str
    domain: str  # N, E, O, A, C (Neuroticism, Extraversion, Openness, Agreeableness, Conscientiousness)
    facet: int   # 1-6 (sub-facets within each domain)
    choices: List[Dict[str, Any]]  # Answer choices with scores

class BigFiveQuestionLoader:
    """Loads and manages Big Five personality test questions"""
    
    def __init__(self, data_path: str = "data_core/bigfive-web-3.0.2"):
        self.data_path = data_path
        self.questions: List[BigFiveQuestion] = []
        self.domain_mapping = {
            'N': 'neuroticism',
            'E': 'extraversion', 
            'O': 'openness',
            'A': 'agreeableness',
            'C': 'conscientiousness'
        }
        self._load_questions()
    
    def _load_questions(self):
        """Load questions from the Big Five test data"""
        try:
            # Try to load from actual Big Five data files first
            self.questions = self._load_real_bigfive_questions()
            if not self.questions:
                # Fallback to comprehensive question set
                self.questions = self._create_comprehensive_questions()
            print(f"Loaded {len(self.questions)} Big Five questions")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading Big Five questions: {e}")
            self.questions = self._create_comprehensive_questions()
    
    def _load_real_bigfive_questions(self) -> List[BigFiveQuestion]:
        """Load real Big Five questions from data files"""
        questions = []
        try:
            # Look for Big Five data files
            data_files = [
                "data_core/bigfive-web-3.0.2/questions.json",
                "data_core/bigfive/questions.json", 
                "data_core/bigfive_questions.json"
            ]
            
            for file_path in data_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        questions = self._parse_bigfive_data(data)
                        if questions:
                            break
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading real Big Five data: {e}")
        
        return questions
    
    def _parse_bigfive_data(self, data: Dict) -> List[BigFiveQuestion]:
        """Parse Big Five data format into questions"""
        questions = []
        try:
            if isinstance(data, list):
                for item in data:
                    if 'text' in item and 'domain' in item:
                        question = BigFiveQuestion(
                            id=item.get('id', f"{item['domain']}{len(questions)+1}"),
                            text=item['text'],
                            domain=item['domain'],
                            facet=item.get('facet', 1),
                            choices=self._create_standard_choices()
                        )
                        questions.append(question)
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error parsing Big Five data: {e}")
        
        return questions
    
    def _create_comprehensive_questions(self) -> List[BigFiveQuestion]:
        """Create comprehensive Big Five question set based on IPIP-NEO"""
        questions = []
        
        # Neuroticism questions (6 facets)
        neuroticism_questions = [
            ("I get stressed out easily", 1), ("I worry about things", 1),
            ("I am relaxed most of the time", 2), ("I seldom feel blue", 2),
            ("I am not easily bothered by things", 3), ("I rarely get irritated", 3),
            ("I often feel blue", 4), ("I dislike myself", 4),
            ("I am easily discouraged", 5), ("I panic easily", 5),
            ("I am not embarrassed easily", 6), ("I am not easily frustrated", 6)
        ]
        
        # Extraversion questions (6 facets)
        extraversion_questions = [
            ("I am the life of the party", 1), ("I feel comfortable around people", 1),
            ("I start conversations", 2), ("I talk to a lot of different people at parties", 2),
            ("I don't talk a lot", 3), ("I think a lot before I speak", 3),
            ("I am not interested in other people's problems", 4), ("I am not really interested in others", 4),
            ("I get a lot of pleasure from thrill seeking", 5), ("I like to be where the action is", 5),
            ("I am always cheerful", 6), ("I laugh a lot", 6)
        ]
        
        # Openness questions (6 facets)
        openness_questions = [
            ("I have a vivid imagination", 1), ("I have excellent ideas", 1),
            ("I am quick to understand things", 2), ("I use difficult words", 2),
            ("I spend time reflecting on things", 3), ("I am full of ideas", 3),
            ("I am not interested in abstract ideas", 4), ("I do not have a good imagination", 4),
            ("I am not interested in art", 5), ("I do not like poetry", 5),
            ("I believe in the importance of art", 6), ("I like music", 6)
        ]
        
        # Agreeableness questions (6 facets)
        agreeableness_questions = [
            ("I am interested in people", 1), ("I feel others' emotions", 1),
            ("I am concerned about others", 2), ("I have a soft heart", 2),
            ("I trust others", 3), ("I believe that others have good intentions", 3),
            ("I am not interested in other people's problems", 4), ("I am not really interested in others", 4),
            ("I am not interested in abstract ideas", 5), ("I do not have a good imagination", 5),
            ("I believe in the importance of art", 6), ("I like music", 6)
        ]
        
        # Conscientiousness questions (6 facets)
        conscientiousness_questions = [
            ("I am always prepared", 1), ("I pay attention to details", 1),
            ("I get chores done right away", 2), ("I like order", 2),
            ("I follow a schedule", 3), ("I am exacting in my work", 3),
            ("I leave my belongings around", 4), ("I make a mess of things", 4),
            ("I often forget to put things back in their proper place", 5), ("I shirk my duties", 5),
            ("I do things according to a plan", 6), ("I waste my time", 6)
        ]
        
        # Create questions for each domain
        domains = {
            'N': neuroticism_questions,
            'E': extraversion_questions, 
            'O': openness_questions,
            'A': agreeableness_questions,
            'C': conscientiousness_questions
        }
        
        question_id = 1
        for domain, domain_questions in domains.items():
            for text, facet in domain_questions:
                question = BigFiveQuestion(
                    id=f"{domain}{question_id}",
                    text=f"I am someone who {text.lower()}",
                    domain=domain,
                    facet=facet,
                    choices=self._create_standard_choices()
                )
                questions.append(question)
                question_id += 1
        
        return questions
    
    def _create_standard_choices(self) -> List[Dict[str, Any]]:
        """Create standard 5-point Likert scale choices"""
        return [
                    {"text": "Very Inaccurate", "score": 1},
                    {"text": "Moderately Inaccurate", "score": 2},
                    {"text": "Neither Accurate nor Inaccurate", "score": 3},
                    {"text": "Moderately Accurate", "score": 4},
                    {"text": "Very Accurate", "score": 5}
                ]
    
    
    def get_random_question(self) -> BigFiveQuestion:
        """Get a random Big Five question"""
        if not self.questions:
            # Create a minimal fallback question
            return BigFiveQuestion(
                id="FALLBACK1",
                text="I am someone who feels comfortable with myself",
                domain="N",
                facet=1,
                choices=self._create_standard_choices()
            )
        return random.choice(self.questions)
    
    def get_questions_by_domain(self, domain: str) -> List[BigFiveQuestion]:
        """Get all questions for a specific Big Five domain"""
        return [q for q in self.questions if q.domain == domain.upper()]
    
    def get_random_question_by_domain(self, domain: str) -> BigFiveQuestion:
        """Get a random question for a specific Big Five domain"""
        domain_questions = self.get_questions_by_domain(domain)
        if not domain_questions:
            return self.get_random_question()
        return random.choice(domain_questions)
    
    def get_all_questions_by_domain(self, domain: str) -> List[BigFiveQuestion]:
        """Get all questions for a specific Big Five domain"""
        return self.get_questions_by_domain(domain)
    
    def get_question_count(self) -> int:
        """Get total number of questions available"""
        return len(self.questions)
    
    def get_domain_name(self, domain_code: str) -> str:
        """Convert domain code to full name"""
        return self.domain_mapping.get(domain_code.upper(), domain_code.lower())
    
    def get_all_domains(self) -> List[str]:
        """Get all available Big Five domains"""
        return list(self.domain_mapping.keys())

# Global instance for easy access
bigfive_loader = BigFiveQuestionLoader()
