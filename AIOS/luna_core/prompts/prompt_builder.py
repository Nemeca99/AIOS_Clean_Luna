#!/usr/bin/env python3
"""
Centralized Prompt Builder
Loads prompt templates from config and assembles them dynamically
"""

import json
from pathlib import Path
from typing import Dict, Optional, List

class PromptBuilder:
    """Builds Luna prompts from centralized config"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default: luna_core/config/prompt_templates.json
            self.config_path = Path(__file__).parent.parent / "config" / "prompt_templates.json"
        else:
            self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load prompt templates from config"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Prompt config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def build_prompt(self, 
                    tier: str,
                    question: str,
                    trait: str,
                    context: str = "",
                    topics: List[str] = None,
                    mood: str = "neutral",
                    connections: str = "",
                    first_word: str = "",
                    arbiter_guidance: str = "",
                    carma_memories: str = "") -> str:
        """
        Build complete prompt from config templates
        
        Args:
            tier: Complexity tier (trivial, low, moderate, high, critical, extreme)
            question: User's question
            trait: Conversation trait (general, technical, etc)
            context: Dynamic context about conversation state
            topics: Recent conversation topics
            mood: Conversation mood
            connections: Cross-domain connection hints
            first_word: Selected first word for response
            arbiter_guidance: Lessons from Arbiter
            carma_memories: Relevant CARMA memories
        
        Returns:
            Complete assembled prompt
        """
        # Start with base foundation (same for all tiers)
        prompt = self.config['prompt_config']['base_foundation']['template']
        
        # Add dynamic context
        if connections:
            context_template = self.config['prompt_config']['context_templates']['with_connections']
            context_section = context_template.format(
                context=context if context else "New conversation",
                topics=', '.join(topics[:3]) if topics else 'New conversation',
                mood=mood,
                connections=connections
            )
        elif topics:
            context_template = self.config['prompt_config']['context_templates']['ongoing_conversation']
            context_section = context_template.format(
                context=context if context else "Ongoing conversation",
                topics=', '.join(topics[:3]) if topics else 'New conversation',
                mood=mood
            )
        elif context:
            context_template = self.config['prompt_config']['context_templates']['minimal']
            context_section = context_template.format(context=context)
        else:
            context_template = self.config['prompt_config']['context_templates']['fresh_conversation']
            context_section = context_template.format(
                context="New conversation",
                mood=mood
            )
        
        prompt += f"\n\n{context_section}"
        
        # Add tier-specific adjustment
        tier_lower = tier.lower()
        if tier_lower in self.config['prompt_config']['tier_adjustments']:
            tier_template = self.config['prompt_config']['tier_adjustments'][tier_lower]['template']
            prompt += tier_template
        
        # Add arbiter lessons if available
        if arbiter_guidance:
            prompt += arbiter_guidance
        
        # Add CARMA memories if available
        if carma_memories:
            prompt += f"\n\n{carma_memories}"
        
        # Add first word instruction if specified
        if first_word:
            first_word_instruction = self.config['prompt_config']['first_word_instruction']['template']
            prompt += first_word_instruction.format(first_word=first_word)
        
        # Add user question
        user_question_template = self.config['prompt_config']['user_question_template']['template']
        prompt += user_question_template.format(question=question, trait=trait.upper())
        
        return prompt
    
    def get_base_foundation(self) -> str:
        """Get just the base foundation template"""
        return self.config['prompt_config']['base_foundation']['template']
    
    def get_tier_description(self, tier: str) -> str:
        """Get description for a specific tier"""
        tier_lower = tier.lower()
        if tier_lower in self.config['prompt_config']['tier_adjustments']:
            return self.config['prompt_config']['tier_adjustments'][tier_lower]['description']
        return "Unknown tier"

def get_prompt_builder() -> PromptBuilder:
    """Factory function to get singleton instance"""
    if not hasattr(get_prompt_builder, "_instance"):
        get_prompt_builder._instance = PromptBuilder()
    return get_prompt_builder._instance

if __name__ == "__main__":
    # Test the prompt builder
    builder = PromptBuilder()
    
    print("=== BASE FOUNDATION ===")
    print(builder.get_base_foundation())
    
    print("\n=== LOW TIER EXAMPLE ===")
    prompt = builder.build_prompt(
        tier="low",
        question="How are you?",
        trait="general",
        context="Fresh start - be curious",
        mood="neutral",
        first_word="Why"
    )
    print(prompt)
    
    print("\n=== HIGH TIER UNLEASHED ===")
    prompt = builder.build_prompt(
        tier="high",
        question="What are you interested in?",
        trait="general",
        context="Deep exploration",
        mood="engaged"
    )
    print(prompt)

