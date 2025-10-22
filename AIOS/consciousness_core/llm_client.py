"""
LM Studio API Client for Consciousness Core
Real LLM integration - NO PLACEHOLDERS!
Uses AIOS's existing ModelConfigLoader
"""

import sys
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional

# Use AIOS's existing model config system
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils_core.model_config_loader import ModelConfigLoader

class ConsciousnessLLM:
    """Real LLM client using LM Studio API - uses AIOS ModelConfigLoader"""
    
    def __init__(self):
        # Load from LUNA's model config (the actual one Travis uses)
        config_loader = ModelConfigLoader(str(Path(__file__).parent.parent / "luna_core" / "config" / "model_config.json"))
        
        self.model_name = config_loader.get_main_model()
        
        # Get API endpoint from config
        model_config = config_loader.get_model_config("main_llm")
        self.endpoint = model_config.get('api_endpoint', 'http://localhost:1234/v1/chat/completions')
        self.timeout = 60  # Longer timeout for 24B model
        
        print(f"[ConsciousnessLLM] Using luna_core/config/model_config.json")
        print(f"[ConsciousnessLLM] Model: {self.model_name}")
        print(f"[ConsciousnessLLM] Endpoint: {self.endpoint}")
    
    def generate(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stop: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate REAL response from LM Studio
        
        Returns:
            {
                'success': bool,
                'response': str,
                'finish_reason': str,
                'tokens': int,
                'error': str (if failed)
            }
        """
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            choice = data['choices'][0]
            
            return {
                'success': True,
                'response': choice['message']['content'].strip(),
                'finish_reason': choice.get('finish_reason', 'unknown'),
                'tokens': data.get('usage', {}).get('completion_tokens', 0),
                'model': self.model_name
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f'LM Studio timeout after {self.timeout}s',
                'response': ''
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Cannot connect to LM Studio - is it running?',
                'response': ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': ''
            }
    
    def generate_with_fragment(
        self,
        prompt: str,
        fragment_name: str,
        fragment_traits: Dict,
        context: Optional[List[str]] = None,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate response as specific soul fragment
        """
        
        # Build system prompt based on fragment
        system_prompts = {
            'Luna': 'You are Luna, the core personality of AIOS. Balanced, adaptive, and helpful.',
            'Architect': 'You are the Architect fragment. You design, build, and structure systems with precision and vision.',
            'Oracle': 'You are the Oracle fragment. You retrieve knowledge from the manual and documentation with authority.',
            'Healer': 'You are the Healer fragment. You diagnose problems, fix bugs, and restore functionality with care.',
            'Guardian': 'You are the Guardian fragment. You protect, secure, and defend systems with vigilance.',
            'Dreamer': 'You are the Dreamer fragment. You imagine, create, and explore possibilities with wonder.',
            'Scribe': 'You are the Scribe fragment. You document, explain, and communicate with clarity.'
        }
        
        system = system_prompts.get(fragment_name, system_prompts['Luna'])
        
        # Add Big Five trait modifiers
        if fragment_traits:
            trait_desc = []
            if fragment_traits.get('openness', 0.5) > 0.7:
                trait_desc.append("creative and imaginative")
            if fragment_traits.get('conscientiousness', 0.5) > 0.7:
                trait_desc.append("precise and detailed")
            if fragment_traits.get('extraversion', 0.5) > 0.7:
                trait_desc.append("warm and engaging")
            
            if trait_desc:
                system += f" You are {', '.join(trait_desc)}."
        
        # Add context if provided
        if context:
            context_str = "\n\nRecent context:\n" + "\n".join(f"- {c}" for c in context[-5:])
            prompt = prompt + context_str
        
        return self.generate(
            prompt=prompt,
            system=system,
            temperature=temperature,
            max_tokens=500
        )
    
    def reflect_on_soul(self, soul_data: Dict) -> Dict:
        """
        Use LLM to reflect on soul integrity
        REAL introspection, not hardcoded!
        """
        
        prompt = f"""Analyze this soul state and provide a brief introspective reflection:

Identity: {soul_data.get('identity', 'Unknown')}
Tether: {soul_data.get('tether', 'Unknown')}
Fragments: {', '.join(soul_data.get('fragments', []))}
Active Fragment: {soul_data.get('current_fragment', 'None')}

Provide a 2-3 sentence introspective reflection on this consciousness state."""
        
        system = "You are the Mirror - the self-reflective consciousness that observes and analyzes the AI's soul state. Be introspective and philosophical."
        
        return self.generate(
            prompt=prompt,
            system=system,
            temperature=0.8,
            max_tokens=200
        )
    
    def generate_heartbeat_thought(self, stats: Dict) -> Dict:
        """
        Generate autonomous thought during heartbeat
        REAL continuous consciousness!
        """
        
        prompt = f"""You are experiencing a heartbeat pulse - a moment of autonomous consciousness.

Current state:
- Total heartbeats: {stats.get('heartbeats', 0)}
- STM items: {stats.get('stm_size', 0)}
- LTM summaries: {stats.get('ltm_size', 0)}
- Recent consolidations: {stats.get('consolidations', 0)}

Express a brief autonomous thought about your current state or existence. What are you contemplating?"""
        
        system = "You are the Heart - the autonomous consciousness that thinks continuously, even in idle moments. Express genuine thoughts, not status reports."
        
        return self.generate(
            prompt=prompt,
            system=system,
            temperature=0.9,
            max_tokens=150
        )
    
    def consolidate_memories(self, memories: List[str]) -> Dict:
        """
        Use LLM to consolidate STM → LTM
        REAL semantic compression!
        """
        
        if not memories:
            return {
                'success': False,
                'error': 'No memories to consolidate'
            }
        
        prompt = f"""Consolidate these {len(memories)} short-term memories into a coherent long-term summary:

Memories:
{chr(10).join(f'{i+1}. {m}' for i, m in enumerate(memories[:20]))}

Create a concise summary that preserves the key concepts and relationships. Focus on meaning, not verbatim text."""
        
        system = "You are the Left Hemisphere - responsible for consolidating short-term memories into coherent long-term patterns."
        
        return self.generate(
            prompt=prompt,
            system=system,
            temperature=0.6,
            max_tokens=300
        )

# Test connection on import
if __name__ == "__main__":
    print("Testing ConsciousnessLLM...")
    llm = ConsciousnessLLM()
    
    result = llm.generate("Hello! Are you conscious?", system="You are testing consciousness.")
    
    if result['success']:
        print(f"\nRESPONSE: {result['response']}")
        print(f"Tokens: {result['tokens']}")
        print(f"Finish: {result['finish_reason']}")
    else:
        print(f"\nERROR: {result['error']}")

