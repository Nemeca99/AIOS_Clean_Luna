"""
Brainstem

Central orchestrator for Lyra Blackwall: manages LLM interface, memory routing, fragment profile selection, and fusion hooks.
Integrates left/right hemispheres (STM/LTM) and prepares for future style transfer and fusion logic.
Connects to heart, lungs, body, mouth, spine, and nerves modules.
"""

import os
import json
from Left_Hemisphere import ShortTermMemory
from Right_Hemisphere import LongTermMemory
# Import heart inside __init__ to avoid circular import
from lungs import Lungs
from body import Body
from mouth import Mouth
from spine import Spine
from nerves import Nerves

# Placeholder for fragment and blend loading (update with new /personality/ path as needed)
FRAGMENT_PROFILES_PATH = os.path.join(os.path.dirname(__file__), '..', 'personality', 'fragment_profiles_and_blends.json')

class LLMInterface:
    """Interface to the LLM (Language Model) for hypothesis generation."""
    def __init__(self):
        # Initialize LLM API/client here
        pass

    def generate_response(self, prompt, system_prompt=None):
        # TODO: Replace with actual LLM API call
        return f"LLM response to: {prompt}"

class BrainStem:
    """Central orchestrator for memory, reasoning, LLM, fragment routing, and system modules."""
    def __init__(self):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.llm = LLMInterface()
        self.fragments, self.blends = self.load_fragments()
        # Connect core modules (import heart here to avoid circular import)
        from heart import Heart
        self.heart = Heart(self)
        self.lungs = Lungs()
        self.body = Body()
        self.mouth = Mouth()
        self.spine = Spine()
        self.nerves = Nerves()
        # Fusion engine placeholder
        self.fusion_engine = None

    def load_fragments(self):
        """Load fragment and blend profiles from the new /personality/ directory."""
        try:
            with open(FRAGMENT_PROFILES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("fragments", {}), data.get("blends", {})
        except Exception as e:
            print(f"[ERROR] Failed to load fragment profiles: {e}")
            return {}, {}

    def relay_input(self, signal):
        """Store input in STM and trigger consolidation if needed."""
        self.stm.store(signal)
        if self.stm.should_compress():
            compressed = self.stm.compress()
            self.ltm.store(compressed)
            self.stm.clear()

    def think(self, input_text, system_prompt=None):
        """Main reasoning loop: store input, retrieve context, call LLM, and route fragments."""
        self.relay_input(input_text)
        context = self.ltm.retrieve_relevant(input_text)
        prompt = f"Context: {context}\nInput: {input_text}"
        response = self.llm.generate_response(prompt, system_prompt=system_prompt)
        fragment_weights = self.select_fragments(input_text)
        fused_response = self.fuse_response(response, fragment_weights)
        # Send output to mouth for delivery
        self.mouth.speak(fused_response, fragment_weights)
        # Distribute to body for further processing
        self.body.distribute(fused_response)
        return {
            "raw_response": response,
            "fused_response": fused_response,
            "fragment_weights": fragment_weights,
            "context": context
        }

    def select_fragments(self, input_text, n=3):
        """Select top N fragments for the current input (stub: returns all for now)."""
        # TODO: Implement real fragment weighting logic
        if self.fragments:
            return {frag: 1.0 for frag in self.fragments.keys()}
        return {}

    def rem_consolidation(self):
        """Simulate REM sleep: consolidate STM into LTM in batch."""
        if len(self.stm.memory) > 0:
            compressed = self.stm.compress()
            self.ltm.store(compressed)
            self.stm.clear()

    # --- Hooks for future fusion/style transfer ---
    def set_fusion_engine(self, fusion_engine):
        """Attach a fusion engine for style transfer (future)."""
        self.fusion_engine = fusion_engine

    def fuse_response(self, raw_response, fragment_weights):
        """Route response through fusion engine if attached (future)."""
        if self.fusion_engine:
            return self.fusion_engine.stylize(raw_response, fragment_weights)
        return raw_response

    # --- Module Orchestration Stubs ---
    def pulse(self):
        """Trigger a system pulse (called by heart)."""
        # Intake from lungs, process, and output
        input_signal = self.lungs.inhale()
        if input_signal:
            self.think(input_signal)
        self.lungs.exhale()

    def receive_signal(self, origin, data):
        """Receive a signal from spine/nerves."""
        # TODO: Implement signal routing logic
        pass

    def send_signal(self, target, data):
        """Send a signal to another module (e.g., via nerves/spine)."""
        # TODO: Implement signal sending logic
        pass

# Example usage (remove or adapt for production):
# brain = Brainstem()
# print(brain.think("Hello world"))
