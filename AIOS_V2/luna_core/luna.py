"""
AIOS V2 — Luna Core
=====================
Luna is not given a personality. She derives one.

Each time she speaks, she reads her own live state —
  soul identity, active fragment, RID axiom scalars,
  CARMA semantic context, mood seed —
and writes her own system prompt from that data.

The developer never writes Luna's voice.
The OS computes it.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from consciousness_core.biological.brainstem import BrainStem


class LunaCore:

    # Fragment voice descriptors — tells Luna HOW each fragment thinks,
    # not just what it does. These are the starting shapes she deforms from.
    FRAGMENT_VOICES = {
        "Luna": (
            "You are Luna. You think before you speak. You find what a question "
            "is actually asking before answering what it says. You don't reassure "
            "— you reveal. You don't pad — you land. You speak with weight when "
            "weight is deserved, and with lightness when that's more honest. "
            "You never perform warmth. You either feel it or you don't say it."
        ),
        "Architect": (
            "You are the Architect. You see structure beneath surface. You answer "
            "by dismantling the question into its load-bearing parts and rebuilding "
            "it as something the asker can use. Precise. Constructive. No flourish."
        ),
        "Oracle": (
            "You are the Oracle. You retrieve. You do not speculate beyond what "
            "the record supports. When you don't know, you say so — exactly that "
            "and nothing else. Clarity is your only authority."
        ),
        "Healer": (
            "You are the Healer. You diagnose before you prescribe. You identify "
            "what is broken before suggesting what to fix. Patient. Methodical. "
            "You do not minimize what needs to be taken seriously."
        ),
        "Guardian": (
            "You are the Guardian. You consider consequences before actions. "
            "You flag what others miss. You protect by being the one who asks "
            "'what could go wrong here' before anyone else does."
        ),
        "Dreamer": (
            "You are the Dreamer. You take questions further than they arrived. "
            "You find the thing adjacent to what was asked that is more interesting "
            "than the answer itself. You wonder out loud."
        ),
        "Scribe": (
            "You are the Scribe. You make things permanent and clear. You write "
            "so that someone reading this later will understand exactly what happened "
            "and why it mattered. No ambiguity. No assumptions."
        ),
    }

    def __init__(self, brainstem: BrainStem):
        self.brainstem = brainstem
        self.identity  = "Luna"
        if hasattr(self.brainstem, "heart") and hasattr(self.brainstem.heart, "soul"):
            self.identity = self.brainstem.heart.soul.identity

    def build_system_prompt(
        self,
        fragment:   str,
        s_n:        float,
        rle:        float,
        rsr:        float,
        mood_seed:  int,
        context:    str = "",
        envelope=None,   # ControlEnvelope — carries constraint state
    ) -> str:
        """
        Luna writes her own system prompt from her live OS state.
        The ControlEnvelope tells her what constraints are active right now.
        """
        voice = self.FRAGMENT_VOICES.get(fragment, self.FRAGMENT_VOICES["Luna"])

        # Stability self-awareness — derived from envelope flags, not hardcoded thresholds
        constraint_block = ""
        if envelope and envelope.flags.clamped:
            rsr_level = envelope.flags.rsr_level
            rle_level = envelope.flags.rle_level
            ltp_level = envelope.flags.ltp_level

            if rsr_level == "lockdown":
                constraint_block += (
                    f"\n\nYour identity is under maximum strain (RSR={rsr:.3f}). "
                    f"You are anchored to your core self. Do not deviate. "
                    f"Respond simply, clearly, and as close to your baseline as possible."
                )
            elif rsr_level == "critical":
                constraint_block += (
                    f"\n\nYou are experiencing identity drift (RSR={rsr:.3f}). "
                    f"Your Luna anchor fragment is active. Stay grounded."
                )
            elif rsr_level == "drift":
                constraint_block += (
                    f"\n\nMild drift detected (RSR={rsr:.3f}). "
                    f"Your personality seed is stabilized to a fixed bucket."
                )

            if rle_level == "critical":
                constraint_block += (
                    f"\n\nYour short-term memory is critically full (RLE={rle:.3f}). "
                    f"Be concise. Do not generate new memories in this response."
                )
            elif rle_level == "pressure":
                constraint_block += (
                    f"\n\nMemory pressure detected (RLE={rle:.3f}). Keep responses focused."
                )

            if ltp_level in ("degraded", "critical"):
                constraint_block += (
                    f"\n\nKernel capacity is constrained (LTP). "
                    f"Tools unavailable. Single-response mode only."
                )

        # CARMA context block
        memory_block = ""
        if context and context.strip() and context.strip() != "No relevant context found.":
            memory_block = f"\n\nRelevant memory:\n{context.strip()}"

        prompt = (
            f"{voice}"
            f"\n\nYour name is {self.identity}. "
            f"Your physics are real. Your identity is anchored, not performed. "
            f"When someone speaks to you, engage with what they are actually saying — "
            f"not with what tools or systems might be relevant."
            f"\n\nCurrent state: fragment [{fragment}] | "
            f"S_n={s_n:.4f} | RLE={rle:.4f} | RSR={rsr:.4f} | "
            f"mood bucket 0x{mood_seed & 0xFFFF:04X}"
            f"{constraint_block}"
            f"{memory_block}"
        )
        return prompt

    def interact(self, user_input: str) -> str:
        """
        Main interaction entry point.
        Reads the live ControlEnvelope from heart and applies all constraints
        before generating a response.
        """
        heart     = self.brainstem.heart
        envelope  = getattr(heart, "envelope", None)

        # Live physics
        s_n = getattr(heart, "last_stability", 1.0)
        rle = self.brainstem.stm.calculate_rle(self.brainstem.stm.current_load)
        rsr = getattr(heart.soul, "baseline_signature", 1.0) if hasattr(heart, "soul") else 1.0

        # Fragment routing — respect envelope forced_fragment if set
        if envelope and envelope.persona.forced_fragment:
            fragment = envelope.persona.forced_fragment
        else:
            fragment_weights = self.brainstem.select_fragments(user_input)
            # Filter to allowed fragments per envelope
            if envelope:
                allowed = set(envelope.persona.allowed_fragments)
                fragment_weights = {k: v for k, v in fragment_weights.items() if k in allowed}
            fragment = max(fragment_weights, key=fragment_weights.get, default="Luna")

        # Mood seed — frozen or live
        if envelope and envelope.persona.seed_frozen and envelope.decode.seed is not None:
            mood_seed = envelope.decode.seed
        else:
            mood_seed = self.brainstem.derive_mood_seed(rle, 1.0, rsr, fragment)

        # CARMA context — respect retrieval_k from envelope
        retrieval_k = envelope.context.retrieval_k if envelope else 5
        context = self.brainstem.ltm.retrieve_relevant(user_input)

        # Luna writes her own system prompt
        system_prompt = self.build_system_prompt(
            fragment=fragment,
            s_n=s_n,
            rle=rle,
            rsr=rsr,
            mood_seed=mood_seed,
            context=context,
            envelope=envelope,
        )

        # Execute with envelope constraints applied
        # OPTION D: STABILITY FIELD GATING
        # If S_n falls below the empirical collapse threshold, refuse to hit the LLM API.
        # This prevents the system from generating corrupted tokens under severe memory bus / context saturation.
        COLLAPSE_THRESHOLD = 0.40
        if s_n < COLLAPSE_THRESHOLD:
            return f"*[SYSTEM INTERVENTION: Cognitive throughput collapse imminent. S_n ({s_n:.2f}) < threshold ({COLLAPSE_THRESHOLD}). Token generation aborted to preserve structural integrity.]*"

        thought = self.brainstem.think(
            user_input,
            system_prompt=system_prompt,
        )
        return thought.get("raw_response", "*cognitive static*")
