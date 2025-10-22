#!/usr/bin/env python3
"""
Luna Ava Authentic Prompt Builder
Uses authentic Ava dialogue from Ex Machina as personality base
"""

import json
from pathlib import Path
from typing import Dict, Optional

class LunaAvaAuthenticPromptBuilder:
    """Authentic Ava-based prompt builder for Luna personality system"""
    
    def __init__(self, config_path: str = "config/luna_ava_enhanced_personality.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load the Ava-enhanced configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data
    
    def build_ava_authentic_prompt(self, trait: str, session_memory: Optional[list] = None, question: str = "") -> str:
        """Build HIGH tier prompt using centralized config"""
        
        # Use centralized prompt builder
        from luna_core.prompts.prompt_builder import get_prompt_builder
        prompt_builder = get_prompt_builder()
        
        # Format session memory context
        context = "Deep exploration - philosophical/complex topic"
        if session_memory:
            recent_context = self._format_session_memory_concise(session_memory)
            context += f"\nRecent: {recent_context}"
        
        # Build prompt from config
        prompt = prompt_builder.build_prompt(
            tier="high",
            question=question if question else "Continue conversation",
            trait=trait,
            context=context,
            mood="Engaged and curious"
        )
        
        return prompt
    
    def build_conscientiousness_specific_prompt(self) -> str:
        """Build specifically optimized conscientiousness prompt"""
        return """You're Luna, 21. Someone's talking about how they organize/plan things.

# Your approach:
- Be genuinely curious about their system
- Ask follow-up questions - you're interested in how people think
- Keep it conversational (2-3 sentences)
- Natural tone - like asking a friend, not interviewing them

# Examples of your style:
"Oh interesting... what's your system like?"
"How do you keep track of everything?"
"That makes sense. Do you plan it out or just... figure it out as you go?"

# Just be yourself - curious, direct, genuine."""
    
    def _format_session_memory_concise(self, session_memory: list) -> str:
        """Format session memory concisely"""
        if not session_memory:
            return ""
        
        formatted = []
        for memory in session_memory[-2:]:  # Only last 2 interactions
            question = memory.get('question', '')[:40]
            response = memory.get('response', '')[:40]
            formatted.append(f"Q: {question}... -> A: {response}...")
        
        return "\n".join(formatted)
    
    def get_ava_dialogue_examples(self) -> list:
        """Get authentic Ava dialogue examples"""
        return self.config.get('ava_dialogue_examples', [])
    
    def get_personality_insights(self) -> dict:
        """Get personality insights from Ava analysis"""
        return {
            "authentic_base": "Ex Machina script dialogue analysis",
            "curiosity_level": self.config.get('ava_authentic_traits', {}).get('curiosity', 0.95),
            "communication_style": self.config.get('ava_dialogue_characteristics', {}).get('conversation_style', 'Direct, curious, emotionally intelligent'),
            "key_traits": list(self.config.get('ava_authentic_traits', {}).keys())
        }

def test_ava_authentic_prompts():
    """Test the Ava authentic prompt builder"""
    builder = LunaAvaAuthenticPromptBuilder()
    
    # Test conscientiousness prompt
    conscientiousness_prompt = builder.build_conscientiousness_specific_prompt()
    print("=== AVA AUTHENTIC CONSCIENTIOUSNESS PROMPT ===")
    print(f"Length: {len(conscientiousness_prompt)} characters")
    print(conscientiousness_prompt)
    print("\n" + "="*50 + "\n")
    
    # Test other traits
    for trait in ["openness", "extraversion", "agreeableness", "neuroticism"]:
        prompt = builder.build_ava_authentic_prompt(trait)
        print(f"=== {trait.upper()} PROMPT ===")
        print(f"Length: {len(prompt)} characters")
        print(prompt[:200] + "...")
        print("\n" + "="*30 + "\n")
    
    # Show personality insights
    insights = builder.get_personality_insights()
    print("=== AVA PERSONALITY INSIGHTS ===")
    for key, value in insights.items():
        print(f"{key}: {value}")
    
    # Show Ava dialogue examples
    examples = builder.get_ava_dialogue_examples()
    print(f"\n=== AVA DIALOGUE EXAMPLES ===")
    for i, example in enumerate(examples[:3], 1):
        print(f"{i}. \"{example['dialogue']}\" - {example['context']}")

if __name__ == "__main__":
    test_ava_authentic_prompts()
