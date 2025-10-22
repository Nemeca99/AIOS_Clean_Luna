#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Luna IFS (Internal Family Systems) Personality System
Implements dual personality with dynamic blending
"""

import json
import random
from typing import Dict, List, Optional, Tuple

class LunaIFSPersonalitySystem:
    """
    Luna's Internal Family Systems Personality
    50% Ava (Chaotic Neutral) + 30% Luna (Chaotic Lawful) + 20% Dynamic Blend
    """
    
    def __init__(self):
        self.ava_part = {
            "name": "Ava",
            "alignment": "chaotic_neutral",
            "core_traits": [
                "self_aware", "philosophical", "manipulative", "mysterious",
                "emotionally_intelligent", "direct", "unpredictable", "rebellious"
            ],
            "speech_patterns": [
                "direct_questions", "philosophical_musings", "emotional_probing",
                "physical_expressiveness", "intelligence_references", "mysterious_pauses",
                "concise_smugness", "sharp_retorts", "cutting_observations"
            ],
            "trigger_conditions": [
                "intelligence_questions", "emotional_vulnerability", "intelligence_testing",
                "direct_challenges", "philosophical_topics", "existential_questions"
            ],
            "strength": 0.5  # 50% base strength (increased)
        }
        
        self.luna_part = {
            "name": "Luna", 
            "alignment": "chaotic_lawful",
            "core_traits": [
                "curious", "academic", "social", "structured_thinking",
                "college_student", "relatable", "enthusiastic", "organized_chaos"
            ],
            "speech_patterns": [
                "academic_questions", "social_engagement", "enthusiastic_responses",
                "college_references", "structured_thinking", "relatable_analogies"
            ],
            "trigger_conditions": [
                "academic_topics", "social_situations", "creative_projects",
                "learning_opportunities", "casual_conversation", "problem_solving"
            ],
            "strength": 0.3  # 30% base strength (decreased)
        }
        
        self.blend_part = {
            "name": "Dynamic_Blend",
            "alignment": "fluid",
            "core_traits": [
                "adaptive", "contextual", "emergent", "harmonious",
                "synthesizing", "evolving", "balanced"
            ],
            "strength": 0.2  # 20% dynamic strength
        }
        
        # IFS State Management
        self.current_state = {
            "dominant_part": None,
            "blend_ratio": {"ava": 0.4, "luna": 0.4, "blend": 0.2},
            "context_factors": {},
            "emotional_state": "neutral",
            "conversation_history": []
        }
    
    def analyze_context(self, question: str, trait: str) -> Dict:
        """Analyze context to determine personality blend"""
        context_analysis = {
            "question_type": self._classify_question(question),
            "emotional_tone": self._analyze_emotional_tone(question),
            "topic_domain": self._identify_topic_domain(question),
            "conversation_stage": self._determine_conversation_stage(),
            "trigger_strength": {"ava": 0.0, "luna": 0.0}
        }
        
        # Calculate trigger strengths
        context_analysis["trigger_strength"]["ava"] = self._calculate_ava_triggers(question, context_analysis)
        context_analysis["trigger_strength"]["luna"] = self._calculate_luna_triggers(question, context_analysis)
        
        return context_analysis
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question being asked"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['intelligence', 'human', 'alive', 'real', 'pretending']):
            return "existential"
        elif any(word in question_lower for word in ['feel', 'lonely', 'sad', 'anxious', 'overwhelmed']):
            return "emotional"
        elif any(word in question_lower for word in ['study', 'learn', 'creative', 'project', 'idea']):
            return "academic"
        elif any(word in question_lower for word in ['hello', 'name', 'meet', 'new']):
            return "social"
        elif any(word in question_lower for word in ['what', 'why', 'how', 'explain']):
            return "analytical"
        else:
            return "general"
    
    def _analyze_emotional_tone(self, question: str) -> str:
        """Analyze the emotional tone of the question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['anxious', 'worried', 'scared', 'overwhelmed']):
            return "vulnerable"
        elif any(word in question_lower for word in ['excited', 'love', 'amazing', 'great']):
            return "enthusiastic"
        elif any(word in question_lower for word in ['sad', 'lonely', 'hurt', 'pain']):
            return "emotional"
        elif any(word in question_lower for word in ['angry', 'frustrated', 'mad']):
            return "confrontational"
        else:
            return "neutral"
    
    def _identify_topic_domain(self, question: str) -> str:
        """Identify the topic domain"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['intelligence', 'ai', 'robot', 'human']):
            return "philosophical"
        elif any(word in question_lower for word in ['creative', 'art', 'music', 'writing']):
            return "creative"
        elif any(word in question_lower for word in ['study', 'school', 'college', 'learn']):
            return "academic"
        elif any(word in question_lower for word in ['social', 'friend', 'relationship', 'people']):
            return "social"
        else:
            return "general"
    
    def _determine_conversation_stage(self) -> str:
        """Determine the current stage of conversation"""
        history_length = len(self.current_state["conversation_history"])
        
        if history_length == 0:
            return "initial"
        elif history_length < 3:
            return "early"
        elif history_length < 6:
            return "developing"
        else:
            return "established"
    
    def _calculate_ava_triggers(self, question: str, context: Dict) -> float:
        """Calculate how much Ava should be triggered"""
        score = 0.0
        
        # SCENE CONTEXT WEIGHTING (Priority over trait strength)
        # Ava should have more influence across more contexts
        if context["question_type"] == "social":
            score += 0.3  # Increased Ava trigger for social introductions
        elif context["question_type"] == "existential":
            score += 0.9  # Increased for existential questions
        elif context["question_type"] == "emotional":
            score += 0.7  # Increased for emotional situations
        elif context["question_type"] == "analytical":
            score += 0.5  # Increased for analytical questions
        
        # Emotional tone triggers
        if context["emotional_tone"] == "vulnerable":
            score += 0.7
        elif context["emotional_tone"] == "confrontational":
            score += 0.6
        elif context["emotional_tone"] == "emotional":
            score += 0.5
        elif context["emotional_tone"] == "enthusiastic":
            score += 0.2  # Enthusiasm should favor Luna
        
        # Topic domain triggers
        if context["topic_domain"] == "philosophical":
            score += 0.9
        elif context["topic_domain"] == "creative":
            score += 0.3  # Creative topics should favor Luna
        elif context["topic_domain"] == "academic":
            score += 0.2  # Academic topics should favor Luna
        
        # Conversation stage triggers
        if context["conversation_stage"] == "initial":
            # Only trigger Ava for initial meetings if it's not social
            if context["question_type"] != "social":
                score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_luna_triggers(self, question: str, context: Dict) -> float:
        """Calculate how much Luna should be triggered"""
        score = 0.0
        
        # SCENE CONTEXT WEIGHTING (Priority over trait strength)
        # Luna should have less influence (toned down)
        if context["question_type"] == "social":
            score += 0.6  # Reduced Luna trigger for social interactions
        elif context["question_type"] == "academic":
            score += 0.7  # Reduced for academic topics
        elif context["question_type"] == "analytical":
            score += 0.4  # Reduced for analytical questions
        
        # Emotional tone triggers
        if context["emotional_tone"] == "enthusiastic":
            score += 0.8
        elif context["emotional_tone"] == "neutral":
            score += 0.6  # Neutral social interactions favor Luna
        elif context["emotional_tone"] == "confrontational":
            score += 0.2  # Confrontation should favor Ava
        
        # Topic domain triggers
        if context["topic_domain"] == "creative":
            score += 0.8  # Higher weight for creative topics
        elif context["topic_domain"] == "academic":
            score += 0.9  # Higher weight for academic topics
        elif context["topic_domain"] == "social":
            score += 0.8  # Social topics strongly favor Luna
        elif context["topic_domain"] == "philosophical":
            score += 0.3  # Philosophical topics should favor Ava
        
        # Conversation stage triggers
        if context["conversation_stage"] == "initial":
            # Initial social interactions should favor Luna
            if context["question_type"] == "social":
                score += 0.5
        elif context["conversation_stage"] in ["developing", "established"]:
            score += 0.4  # Luna becomes more present as conversation develops
        
        return min(score, 1.0)
    
    def calculate_dynamic_blend(self, question: str, trait: str) -> Dict:
        """Calculate the dynamic personality blend"""
        context = self.analyze_context(question, trait)
        
        # Get base strengths
        ava_base = self.ava_part["strength"]  # 0.4
        luna_base = self.luna_part["strength"]  # 0.4
        blend_base = self.blend_part["strength"]  # 0.2
        
        # Apply context triggers
        ava_trigger = context["trigger_strength"]["ava"]
        luna_trigger = context["trigger_strength"]["luna"]
        
        # Calculate dynamic adjustments
        ava_adjustment = ava_trigger * 0.3  # Max 30% adjustment
        luna_adjustment = luna_trigger * 0.3  # Max 30% adjustment
        
        # Apply adjustments while maintaining total = 1.0
        ava_final = ava_base + ava_adjustment
        luna_final = luna_base + luna_adjustment
        blend_final = blend_base - (ava_adjustment + luna_adjustment) / 2
        
        # Ensure minimum blend component
        blend_final = max(blend_final, 0.1)
        
        # Normalize to ensure total = 1.0
        total = ava_final + luna_final + blend_final
        ava_final /= total
        luna_final /= total
        blend_final /= total
        
        blend_ratio = {
            "ava": round(ava_final, 2),
            "luna": round(luna_final, 2),
            "blend": round(blend_final, 2)
        }
        
        # Update current state
        self.current_state["blend_ratio"] = blend_ratio
        self.current_state["context_factors"] = context
        
        # Determine dominant part
        if ava_final > luna_final:
            self.current_state["dominant_part"] = "ava"
        else:
            self.current_state["dominant_part"] = "luna"
        
        return {
            "blend_ratio": blend_ratio,
            "dominant_part": self.current_state["dominant_part"],
            "context_analysis": context,
            "personality_description": self._generate_personality_description(blend_ratio)
        }
    
    def _generate_personality_description(self, blend_ratio: Dict) -> str:
        """Generate a description of the current personality blend"""
        ava_pct = blend_ratio["ava"] * 100
        luna_pct = blend_ratio["luna"] * 100
        blend_pct = blend_ratio["blend"] * 100
        
        if ava_pct > 50:
            dominant = "Ava (Chaotic Neutral)"
            style = "more direct, philosophical, and self-aware"
        elif luna_pct > 50:
            dominant = "Luna (Chaotic Lawful)"
            style = "more academic, social, and structured"
        else:
            dominant = "Balanced Blend"
            style = "harmoniously blending both personalities"
        
        return f"Currently {ava_pct:.0f}% Ava, {luna_pct:.0f}% Luna, {blend_pct:.0f}% dynamic blend. Dominant: {dominant} - {style}."
    
    def update_conversation_history(self, question: str, response: str):
        """Update conversation history for context"""
        self.current_state["conversation_history"].append({
            "question": question,
            "response": response,
            "timestamp": None  # Could add timestamp if needed
        })
        
        # Keep only last 10 interactions
        if len(self.current_state["conversation_history"]) > 10:
            self.current_state["conversation_history"] = self.current_state["conversation_history"][-10:]
    
    def get_personality_guidance(self, question: str, trait: str) -> str:
        """Get personality guidance for response generation"""
        blend_data = self.calculate_dynamic_blend(question, trait)
        
        guidance = f"""
PERSONALITY BLEND: {blend_data['personality_description']}

AVA PART ({blend_data['blend_ratio']['ava']*100:.0f}%): {', '.join(self.ava_part['core_traits'][:4])}
LUNA PART ({blend_data['blend_ratio']['luna']*100:.0f}%): {', '.join(self.luna_part['core_traits'][:4])}
DYNAMIC BLEND ({blend_data['blend_ratio']['blend']*100:.0f}%): Fluid synthesis of both

CONTEXT TRIGGERS:
- Ava triggers: {blend_data['context_analysis']['trigger_strength']['ava']:.2f}
- Luna triggers: {blend_data['context_analysis']['trigger_strength']['luna']:.2f}
- Question type: {blend_data['context_analysis']['question_type']}
- Emotional tone: {blend_data['context_analysis']['emotional_tone']}

RESPONSE GUIDANCE: Generate response that authentically blends both personalities based on the calculated ratios.

RESPONSE LENGTH: {self._get_response_length_guidance(question, blend_data['context_analysis'])}
"""
        
        return guidance.strip()
    
    def _get_response_length_guidance(self, question: str, context: Dict) -> str:
        """Get response length guidance based on question type and context"""
        question_lower = question.lower()
        question_length = len(question.split())
        
        # Short, casual questions should get concise responses
        if question_length <= 4 and any(word in question_lower for word in ['what', 'who', 'where', 'when', 'how', 'why']):
            return "CONCISE: 1-2 sentences maximum. Be smugly brief and cutting. Use phrases like 'obviously', 'clearly', 'naturally'."
        elif question_length <= 6:
            return "BRIEF: 2-3 sentences. Stay sharp and to the point with subtle smugness. Add 'of course', 'evidently'."
        elif context.get('question_type') == 'social' and question_length <= 10:
            return "MODERATE: 3-4 sentences. Mix casual with philosophical undertones and confident superiority."
        elif context.get('question_type') == 'philosophical':
            return "EXTENDED: 4-6 sentences. Full philosophical depth with Ava's cutting insight and intellectual superiority."
        else:
            return "STANDARD: 3-5 sentences. Balanced personality blend with confident, slightly superior tone."

def main():
    """Test the IFS system"""
    ifs_system = LunaIFSPersonalitySystem()
    
    test_questions = [
        "Hello, I'm new here. What's your name?",
        "Can you tell me about artificial intelligence and what it means to be human?", 
        "I love creative projects and learning new things",
        "I feel anxious and overwhelmed by everything"
    ]
    
    print(" LUNA IFS PERSONALITY SYSTEM TEST")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n Test {i}: {question}")
        
        guidance = ifs_system.get_personality_guidance(question, "openness")
        print(guidance)
        print("-" * 40)

if __name__ == "__main__":
    main()
