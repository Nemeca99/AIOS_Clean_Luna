#!/usr/bin/env python3
"""
Luna Linguistic Calculus
Interrogative operators for consciousness reasoning compression

Converts natural language questions into graph operations:
- Why → causal edges
- How → mechanism chains
- What → type classification
- Where/When → context binding
- Who → agent aggregation

Integrates with Luna's response generator for prompt compression and arbiter scoring.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Iterable
from collections import defaultdict
import uuid

Edge = Tuple[str, str, str]  # (src, label, dst)


@dataclass
class ExperienceState:
    """Graph state for linguistic experience accumulation"""
    nodes: Dict[str, Dict[str, float]] = field(default_factory=lambda: defaultdict(dict))
    edges: List[Edge] = field(default_factory=list)

    def add_edge(self, src: str, label: str, dst: str):
        self.edges.append((src, label, dst))

    def add_feat(self, node: str, feat: str, val: float = 1.0):
        self.nodes[node][feat] = self.nodes[node].get(feat, 0.0) + val

    def strengthen(self, src: str, label: str, dst: str, w: float = 1.0):
        # simple strengthening: add a weight feature to a virtual edge-node key
        key = f"{src}|{label}|{dst}"
        self.add_feat(key, "edge_weight", w)


@dataclass
class CalcResult:
    """Result of linguistic operation"""
    updated: ExperienceState
    derivations: List[str]
    summary: str
    depth_score: int = 0
    compress_gain: float = 0.0
    coherence_score: float = 0.0
    why_logic: List[str] = field(default_factory=list)


class LinguaCalc:
    """Linguistic Calculus Engine - converts interrogatives to graph operations"""
    
    def __init__(self):
        pass

    # ---------- Primitive ops ----------
    
    def op_why(self, st: ExperienceState, cause: str, effect: str) -> CalcResult:
        """Why operator: introduce/strengthen causal edge"""
        st.add_edge(cause, "CAUSES", effect)
        st.strengthen(cause, "CAUSES", effect, 1.0)
        return CalcResult(
            st, 
            [f"WHY: {cause} -> {effect}"], 
            summary=f"Hypothesis: {cause} causes {effect}"
        )

    def op_how(self, st: ExperienceState, src: str, dst: str, steps: Optional[List[str]] = None) -> CalcResult:
        """How operator: introduce mechanism chain"""
        m = f"mechanism:{uuid.uuid4().hex[:8]}"
        st.add_edge(src, "MECHANISM", m)
        st.add_edge(m, "MECHANISM_TO", dst)
        depth = 0
        
        if steps:
            last = src
            for s in steps:
                st.add_edge(last, "STEP_TO", s)
                last = s
                depth += 1
            st.add_edge(last, "STEP_TO", dst)
            depth += 1
        
        return CalcResult(
            st, 
            [f"HOW: {src} => {dst} via {steps or [m]}"], 
            summary=f"Mechanism linking {src} to {dst}", 
            depth_score=depth
        )

    def op_what(self, st: ExperienceState, ent: str, typ: str) -> CalcResult:
        """What operator: type/classify entity"""
        st.add_edge(ent, "IS_A", typ)
        st.strengthen(ent, "IS_A", typ, 0.5)
        return CalcResult(
            st, 
            [f"WHAT: {ent} is a {typ}"], 
            summary=f"Classified {ent} as {typ}", 
            compress_gain=0.1
        )

    def op_where(self, st: ExperienceState, ent: str, loc: str) -> CalcResult:
        """Where operator: spatial context binding (monoidal - last write wins)"""
        # Remove previous LOCATED_IN edges for this entity (idempotent behavior)
        st.edges = [(s, l, d) for s, l, d in st.edges 
                    if not (s == ent and l == "LOCATED_IN")]
        st.add_edge(ent, "LOCATED_IN", loc)
        return CalcResult(
            st, 
            [f"WHERE: {ent} @ {loc}"], 
            summary=f"Bound {ent} to location {loc}"
        )

    def op_when(self, st: ExperienceState, ent: str, t: str) -> CalcResult:
        """When operator: temporal context binding (monoidal - last write wins)"""
        # Remove previous OCCURS_AT edges for this entity (idempotent behavior)
        st.edges = [(s, l, d) for s, l, d in st.edges 
                    if not (s == ent and l == "OCCURS_AT")]
        st.add_edge(ent, "OCCURS_AT", t)
        return CalcResult(
            st, 
            [f"WHEN: {ent} @ {t}"], 
            summary=f"Bound {ent} to time {t}"
        )

    def op_who(self, st: ExperienceState, target: str, agents: Iterable[str]) -> CalcResult:
        """Who operator: agent aggregation (mean/typical)"""
        agents = list(agents)
        if not agents:
            return CalcResult(st, [], summary="WHO: no agents")
        
        # μ-agent: pick most frequent or first; can swap for proper aggregator
        mu = agents[0]
        st.add_edge(mu, "TYPICAL_AGENT_OF", target)
        return CalcResult(
            st, 
            [f"WHO: μ({agents}) -> {mu}"], 
            summary=f"Typical agent {mu} for {target}"
        )

    # ---------- Rewrite rules ----------
    
    def combine_two_whys_into_how(
        self, 
        st: ExperienceState, 
        cause1: str, 
        cause2: str, 
        effect: str
    ) -> CalcResult:
        """
        Rewrite rule: Why + Why → How
        Collapse parallel causes into mechanism spine
        """
        steps = [cause1, cause2]
        res_how = self.op_how(st, src="∅", dst=effect, steps=steps)
        
        # Record each cause explicitly
        self.op_why(res_how.updated, cause1, effect)
        self.op_why(res_how.updated, cause2, effect)
        
        res_how.derivations.append(f"RULE: WHY+WHY⇒HOW for {effect}")
        res_how.summary = f"Two causes merged into mechanism for {effect}"
        res_how.compress_gain += 0.2
        
        return res_how
    
    def combine_why_how_into_what(
        self, 
        st: ExperienceState,
        cause: str,
        effect: str,
        mechanism_steps: Optional[List[str]] = None
    ) -> CalcResult:
        """
        Rewrite rule: Why + How → What
        Assign type/regularity τ = "process class" learned from mechanism
        
        Collapse causal hypothesis + mechanism chain into type classification
        """
        # First apply Why
        why_res = self.op_why(st, cause, effect)
        
        # Then apply How
        how_res = self.op_how(why_res.updated, cause, effect, mechanism_steps or [])
        
        # Synthesize process class from mechanism
        process_type = f"process_class:{cause}_to_{effect}"
        what_res = self.op_what(how_res.updated, effect, process_type)
        
        what_res.derivations.append(f"RULE: WHY+HOW⇒WHAT for {effect}")
        what_res.summary = f"Classified {effect} as {process_type} via mechanism"
        what_res.compress_gain += 0.3  # Higher gain than just Why+Why
        what_res.depth_score = how_res.depth_score  # Inherit depth from mechanism
        
        return what_res

    # ---------- Safe division as recursion-depth ----------
    
    def safe_division_depth(self, a: int, b: int) -> Optional[int]:
        """
        Division as recursion depth counter
        Returns: max k such that b can be recursively subtracted from a
        """
        if b == 0:
            return None  # ⊥ undefined
        
        k = 0
        r = a
        while r >= b:
            r -= b
            k += 1
        
        return k  # "how many expansions of b fit in a"
    
    # ---------- WHY logic connectives ----------
    def why_and(self, st: ExperienceState, causes: List[str], effect: str) -> CalcResult:
        steps = list(causes)
        res = self.op_how(st, src="∅", dst=effect, steps=steps)
        for c in causes:
            self.op_why(res.updated, c, effect)
        res.derivations.append(f"WHY_AND: {causes} => {effect}")
        res.summary = f"Convergent motives {causes} unify via mechanism for {effect}"
        res.compress_gain += 0.3 + 0.05 * max(0, len(causes) - 2)
        res.coherence_score = 1.0 if len(causes) >= 2 else 0.0
        res.why_logic.append("AND")
        return res

    def why_or(self, st: ExperienceState, alt_causes: List[str], effect: str) -> CalcResult:
        group = f"alt_causes:{uuid.uuid4().hex[:8]}"
        for c in alt_causes:
            st.add_edge(group, "ALT_HAS", c)
            self.op_why(st, c, effect)
        st.add_edge(group, "CAUSES", effect)
        return CalcResult(st, [f"WHY_OR: {alt_causes} => {effect}"],
                          summary=f"Alternative motives {alt_causes} for {effect}",
                          compress_gain=0.05, why_logic=["OR"])

    def why_implies(self, st: ExperienceState, cause: str, effect: str) -> CalcResult:
        st.add_edge(cause, "CAUSES", effect)
        st.strengthen(cause, "CAUSES", effect, 0.8)
        key = f"{cause}|CAUSES|{effect}"
        st.add_feat(key, "logical_implies", 1.0)
        return CalcResult(st, [f"WHY_IMPLIES: {cause} -> {effect}"],
                          summary=f"{cause} implies {effect}",
                          compress_gain=0.05, why_logic=["IMPLIES"])

    def why_biconditional(self, st: ExperienceState, a: str, b: str) -> CalcResult:
        self.op_why(st, a, b)
        self.op_why(st, b, a)
        st.add_feat(f"{a}|CAUSES|{b}", "reciprocal", 1.0)
        st.add_feat(f"{b}|CAUSES|{a}", "reciprocal", 1.0)
        return CalcResult(st, [f"WHY_BICOND: {a} <-> {b}"],
                          summary=f"Reciprocal motives between {a} and {b}",
                          compress_gain=0.1, why_logic=["BICOND"])

    def not_why(self, st: ExperienceState, cause: str, effect: str) -> CalcResult:
        st.add_edge(cause, "INHIBITS", effect)
        st.add_feat(f"{cause}|CAUSES|{effect}", "edge_weight", -0.5)
        return CalcResult(st, [f"NOT_WHY: {cause} inhibits {effect}"],
                          summary=f"{cause} inhibits {effect}",
                          why_logic=["NOT"])

    # ---------- NL parser (pattern-based, extend as needed) ----------
    
    def parse_and_apply(self, st: ExperienceState, text: str) -> CalcResult:
        """
        Parse natural language question and apply appropriate operator
        
        Toy patterns - replace with embeddings/router later
        """
        # --------- NORMALIZE & TOKENIZE ----------
        t = text.strip().lower()
        t = t.replace("  ", " ")
        # tolerate punctuation-free and different verbs
        t = t.replace(" causes ", " cause ")
        t = t.replace(" leads to ", " to ")
        t = t.replace(" lead to ", " to ")
        t = t.replace(" -> ", " -> ")  # keep arrow explicit if present

        # --------- WHY logic quick paths ----------
        # forms:
        #   "why a and b -> p"
        #   "why a or b -> p"
        #   "not why a -> p"
        if t.startswith("not why ") and " -> " in t:
            left, right = t[8:].split(" -> ", 1)
            return self.not_why(st, left.strip(), right.strip(" ?."))
        if t.startswith("why ") and " -> " in t:
            left, right = t[4:].split(" -> ", 1)
            effect = right.strip(" ?.")
            left = left.strip()
            if " and " in left:
                causes = [x.strip() for x in left.split(" and ") if x.strip()]
                return self.why_and(st, causes, effect)
            if " or " in left:
                alts = [x.strip() for x in left.split(" or ") if x.strip()]
                return self.why_or(st, alts, effect)
            # default implication
            return self.why_implies(st, left, effect)

        # --------- WHY canonical form (tolerant) ----------
        if t.startswith("why "):
            # Accept "why does X cause Y" with or without '?', and also "why x cause y"
            core = t[4:].strip(" ?.")
            if " cause " in core:
                left, right = core.split(" cause ", 1)
                cause = left.replace("does ", "").replace("do ", "").strip()
                effect = right.strip()
                return self.op_why(st, cause, effect)
            # Natural language patterns: "why do/does X [verb] Y"
            # Examples: "why do humans create AI", "why does recursion matter"
            # Extract: subject (humans) + verb (create) + object (AI)
            # Map to: subject → object (CAUSES edge)
            if " do " in core or " does " in core:
                # Remove auxiliary
                simplified = core.replace(" does ", " ").replace(" do ", " ").strip()
                # Split on verb (common action verbs)
                verbs = ["create", "build", "make", "want", "need", "exist", "matter", "learn", "form", "drive", "emerge"]
                for verb in verbs:
                    if f" {verb} " in f" {simplified} ":
                        parts = simplified.split(f" {verb} ", 1)
                        if len(parts) == 2:
                            cause = parts[0].strip()
                            effect = f"{verb}_{parts[1].strip()}"  # Verbified effect
                            return self.op_why(st, cause, effect)
                # Fallback: last word as effect
                words = simplified.split()
                if len(words) >= 2:
                    cause = " ".join(words[:-1])
                    effect = words[-1]
                    return self.op_why(st, cause, effect)
            # fallback implication: "why x to y" or "why x y"
            if " to " in core:
                left, right = core.split(" to ", 1)
                return self.why_implies(st, left.strip(), right.strip())
            parts = core.split()
            if len(parts) >= 2:
                return self.why_implies(st, " ".join(parts[:-1]), parts[-1])
            return CalcResult(st, [], "WHY: parsed but no cause/effect found")

        # --------- HOW tolerant ----------
        if t.startswith("how "):
            core = t[4:].strip(" ?.")
            # accept "how does x to y", "how does x lead to y", "how x -> y"
            if " -> " in core:
                left, right = core.split(" -> ", 1)
                return self.op_how(st, left.replace("does ", "").strip() or "∅", right.strip())
            if " to " in core:
                left, right = core.split(" to ", 1)
                return self.op_how(st, left.replace("does ", "").replace("lead", "").strip() or "∅", right.strip())
            # Natural language: "how does X [verb]" or "how do X [verb] Y"
            # Examples: "how does consciousness emerge", "how do thoughts become aware"
            # Remove auxiliary first
            simplified = core.replace(" does ", " ").replace(" do ", " ").strip()
            # Extract verb + object
            verbs = ["emerge", "become", "form", "change", "blend", "generate", "shape", "create", "work", "learn", "think", "feel"]
            for verb in verbs:
                # Match " verb" or " verb " (word boundary)
                if f" {verb} " in f" {simplified} " or simplified.endswith(f" {verb}"):
                    # Split on verb
                    if f" {verb} " in f" {simplified} ":
                        parts = simplified.split(f" {verb} ", 1)
                        src = parts[0].strip() if parts[0].strip() else "∅"
                        dst = f"{verb}_{parts[1].strip()}" if len(parts) > 1 and parts[1].strip() else verb
                    else:
                        # Verb at end: "how does X emerge"
                        parts = simplified.rsplit(f" {verb}", 1)
                        src = parts[0].strip() if parts[0].strip() else "∅"
                        dst = verb
                    return self.op_how(st, src, dst)
            return CalcResult(st, [], "HOW: parsed but no src/dst found")
        
        # What pattern
        if t.startswith("what "):
            if " what is " in " " + t + " ":
                ent = t.split("what is", 1)[1].strip(" ?.")
                return self.op_what(st, ent, "concept")
            return CalcResult(st, [], "WHAT: default classification")
        
        # Where pattern
        if t.startswith("where "):
            ent = t.split("where is", 1)[1].strip(" ?.") if "where is" in t else "unknown"
            return self.op_where(st, ent, "unknown_location")
        
        # When pattern
        if t.startswith("when "):
            ent = t.split("when does", 1)[1].strip(" ?.") if "when does" in t else "unknown"
            return self.op_when(st, ent, "unknown_time")
        
        # Who pattern
        if t.startswith("who "):
            tgt = t.split("who ", 1)[1].strip(" ?.")
            return self.op_who(st, tgt, agents=["human_crowd"])
        
        # Fallback: no-op
        return CalcResult(st, [], "No operator matched")


# ---------- Demo/Test ----------

def _demo():
    """Sanity test for linguistic calculus"""
    lc = LinguaCalc()
    s = ExperienceState()
    
    # Build reasoning chain
    r1 = lc.op_why(s, "heat", "expansion")
    r2 = lc.op_why(r1.updated, "pressure", "expansion")
    r3 = lc.combine_two_whys_into_how(r2.updated, "heat", "pressure", "expansion")
    r4 = lc.op_what(r3.updated, "expansion", "thermodynamic_response")
    
    print("=== Linguistic Calculus Demo ===")
    print("\nEdges created:")
    for e in r4.updated.edges[:10]:
        print(f"  {e}")
    
    print(f"\nDepth: {r3.depth_score}")
    print(f"Compression gain: {r3.compress_gain}")
    print(f"Summary: {r4.summary}")
    
    # Test safe division
    print("\n=== Division as Recursion Depth ===")
    print(f"10 ÷ 3 = {lc.safe_division_depth(10, 3)} steps")
    print(f"15 ÷ 5 = {lc.safe_division_depth(15, 5)} steps")
    print(f"7 ÷ 0 = {lc.safe_division_depth(7, 0)} (None = undefined)")


if __name__ == "__main__":
    _demo()

