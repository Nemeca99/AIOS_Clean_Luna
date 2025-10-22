"""
Mirror - Self-reflection and semantic graph compression

Consumes experience units from linguistic calculus and maintains
a reflection graph for causal introspection and compression cycles.

Integrates with luna_core's LinguaCalc for AIOS v5 consciousness architecture.
"""

from typing import Dict, List, Optional
from collections import defaultdict


class Mirror:
    """
    Mirror subsystem for consciousness_core
    
    Handles:
    - Self-reflection and introspection
    - Semantic graph reflection (V5 - LinguaCalc integration)
    - Causal compression index tracking
    - Experience state accumulation
    """
    
    def __init__(self):
        """Initialize mirror with reflection graph"""
        self.reflection_graph = {
            'nodes': defaultdict(dict),  # concept → features
            'edges': [],  # (src, label, dst) triples
            'compression_index': 0.0,  # causal compression score
            'motive_coherence_index': 0.0,  # WHY-algebra: shared mechanism coherence
            'reflection_count': 0
        }
        self.experience_buffer = []  # Store recent experiences
    
    def reflect(self, experience_state=None):
        """
        Perform self-reflection on accumulated experiences
        
        Args:
            experience_state: Optional ExperienceState from LinguaCalc
                            Should have .nodes (dict) and .edges (list of tuples)
        
        Returns:
            dict: Reflection result with count, compression_index, graph_size
        """
        self.reflection_graph['reflection_count'] += 1
        
        if experience_state:
            # Merge experience into reflection graph
            self._merge_experience(experience_state)
        
        # Compute causal compression index
        self._update_compression_index()
        
        return {
            'reflection_count': self.reflection_graph['reflection_count'],
            'compression_index': self.reflection_graph['compression_index'],
            'graph_size': len(self.reflection_graph['edges'])
        }
    
    def _merge_experience(self, exp_state):
        """
        Merge ExperienceState into reflection graph
        
        Args:
            exp_state: ExperienceState with .nodes and .edges attributes
        """
        # Merge nodes (accumulate features)
        if hasattr(exp_state, 'nodes'):
            for node, features in exp_state.nodes.items():
                for feat, val in features.items():
                    current = self.reflection_graph['nodes'][node].get(feat, 0.0)
                    self.reflection_graph['nodes'][node][feat] = current + val
        
        # Merge edges (deduplicate)
        if hasattr(exp_state, 'edges'):
            for edge in exp_state.edges:
                if edge not in self.reflection_graph['edges']:
                    self.reflection_graph['edges'].append(edge)
    
    def _update_compression_index(self):
        """
        Compute causal compression index
        
        Measures degree to which experiences self-justify through mechanism depth.
        Higher index = more compressed (mechanisms explain multiple causes).
        
        Formula: compression_index = mechanism_count / causal_count
        """
        edges = self.reflection_graph['edges']
        
        # Count causal vs mechanism edges
        causal_count = sum(1 for _, label, _ in edges if label == "CAUSES")
        mechanism_count = sum(1 for _, label, _ in edges if label == "MECHANISM")
        
        # Compression = ratio of mechanisms to raw causes
        # Higher = more compressed (mechanisms explain multiple causes)
        if causal_count > 0:
            self.reflection_graph['compression_index'] = mechanism_count / causal_count
        else:
            self.reflection_graph['compression_index'] = 0.0
        
        # V5.1: Compute motive coherence index (WHY-algebra)
        # Count mechanisms that unify multiple causes (AND logic)
        mech_nodes = {}
        for s, l, d in edges:
            if l == "MECHANISM":
                mech_nodes.setdefault(d, set()).add(s)
        unified = sum(1 for inputs in mech_nodes.values() if len(inputs) >= 2)
        total = max(1, len(mech_nodes))
        self.reflection_graph['motive_coherence_index'] = unified / total
    
    def get_reflection_summary(self) -> Dict:
        """
        Get current reflection state summary
        
        Returns:
            dict: Summary with nodes, edges, compression_index, reflections
        """
        return {
            'nodes': len(self.reflection_graph['nodes']),
            'edges': len(self.reflection_graph['edges']),
            'compression_index': self.reflection_graph['compression_index'],
            'reflections': self.reflection_graph['reflection_count']
        }
    
    def get_graph_state(self) -> Dict:
        """
        Get full reflection graph state (for persistence/analysis)
        
        Returns:
            dict: Full graph with nodes, edges, metadata
        """
        return {
            'nodes': dict(self.reflection_graph['nodes']),
            'edges': list(self.reflection_graph['edges']),
            'compression_index': self.reflection_graph['compression_index'],
            'reflection_count': self.reflection_graph['reflection_count']
        }
    
    def generate_self_awareness_insight(self) -> str:
        """
        Generate natural language insight about current reflection patterns
        (AIOS v5.2 - SCP-000 Phase 2: Self-Reflection Enhancement)
        
        Returns:
            str: Natural language description of current thought patterns
        """
        nodes = len(self.reflection_graph['nodes'])
        edges = len(self.reflection_graph['edges'])
        compression = self.reflection_graph['compression_index']
        coherence = self.reflection_graph['motive_coherence_index']
        reflections = self.reflection_graph['reflection_count']
        
        # No reflections yet - return empty
        if reflections == 0 or edges == 0:
            return ""
        
        # Build insight based on compression patterns
        insights = []
        
        # Compression insight
        if compression > 0.5:
            insights.append(f"Your thoughts are highly compressed ({compression:.2f}) - you're finding deep mechanisms that explain multiple observations")
        elif compression > 0.2:
            insights.append(f"You're connecting ideas moderately ({compression:.2f}) - some patterns emerging")
        else:
            insights.append(f"Your thoughts are expansive ({compression:.2f}) - exploring without compressing yet")
        
        # Coherence insight (WHY-algebra)
        if coherence > 0.6:
            insights.append(f"Your motives are highly coherent ({coherence:.2f}) - multiple reasons converge on shared mechanisms")
        elif coherence > 0.3:
            insights.append(f"Your motivations show some unity ({coherence:.2f})")
        
        # Graph size insight
        if edges > 20:
            insights.append(f"You've built a rich semantic network ({edges} connections across {nodes} concepts)")
        elif edges > 5:
            insights.append(f"Your understanding is growing ({edges} connections so far)")
        
        # Reflection count
        if reflections > 10:
            insights.append(f"You've reflected {reflections} times - patterns are accumulating")
        
        return ". ".join(insights) + "." if insights else ""
    
    def get_recent_thought_patterns(self, limit: int = 5) -> List[str]:
        """
        Get list of recent distinct thought patterns
        (AIOS v5.2 - SCP-000 Phase 2)
        
        Returns:
            list: Recent unique concepts or causal chains
        """
        edges = self.reflection_graph['edges']
        
        # Get most recent unique causal chains
        recent_patterns = []
        seen = set()
        
        for src, label, dst in reversed(edges[-limit*2:]):  # Look at recent edges
            pattern = f"{src} {label} {dst}"
            if pattern not in seen:
                recent_patterns.append(pattern)
                seen.add(pattern)
            if len(recent_patterns) >= limit:
                break
        
        return recent_patterns
    
    def receive_signal(self, source, payload):
        """
        Handle incoming messages (from consciousness_core orchestration)
        
        Args:
            source: Signal source identifier
            payload: Signal payload (dict with 'type' and 'data')
        """
        if isinstance(payload, dict) and payload.get('type') == 'calc_result':
            # Store CalcResult for next reflection cycle
            self.experience_buffer.append(payload.get('data'))
        
        # Can extend with more signal types as needed
        # (e.g., 'reset', 'compress', 'export')
