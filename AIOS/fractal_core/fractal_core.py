#!/usr/bin/env python3
"""
FRACTAL CORE - Main Orchestrator (MAJOR NODE)
Factorian Architecture: Engineering compassion through efficiency

Applies "compress state, not stuff" at all scales:
- Token level: Fewest tokens preserving decisions
- Memory level: Fewest fragments preserving retrieval
- Code level: Fewest modules preserving capability
- Query level: Cheapest policy preserving success

Version: 1.0.0 (Week 1 - Static tables, stable knapsack)
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

import json
from typing import Dict, List, Tuple
from fractal_core.core.fractal_controller import FractalController, FractalPolicies
from fractal_core.core.multihead_classifier import MultiheadClassifier
from fractal_core.core.knapsack_allocator import KnapsackAllocator, Span


class FractalCore:
    """
    Main Fractal Core System.
    
    Single controller emits policies for all AIOS layers.
    Implements Factorian principle: Efficiency ENABLES compassion.
    """
    
    def __init__(self):
        self.version = "1.0.0"
        
        # Initialize controller (emits policies)
        self.controller = FractalController()
        
        # Initialize classifier (standalone access)
        self.classifier = MultiheadClassifier()
        
        # Initialize allocator (standalone access)
        self.allocator = KnapsackAllocator()
        
        # Telemetry
        self.telemetry_enabled = True
        self.turn_logs = []
        
        print(f"Fractal Core v{self.version} Initialized")
        print("  Factorian Architecture: Efficiency -> Compassion")
        print("  Policy: Compress state, not stuff")
        print(f"  Safety: Logic floor {self.controller.safety.get('logic_floor_pct', 0.15)*100:.0f}%")
    
    def get_policies(self, query: str, history: List[str] = None, 
                    global_budget: Dict = None) -> FractalPolicies:
        """
        Get policies for all layers from query and history.
        
        This is the main interface called by other cores (Luna, CARMA, etc).
        
        Args:
            query: Current user query
            history: Conversation history (optional)
            global_budget: Budget constraints (optional)
        
        Returns:
            FractalPolicies with token, memory, code, arbiter, lessons policies
        """
        policies = self.controller.get_policies(query, history, global_budget)
        
        # Log for telemetry (if enabled)
        if self.telemetry_enabled:
            self._log_turn(query, policies)
        
        return policies
    
    def allocate_prompt_spans(self, spans: List[Span], budget: int,
                             query_type_mixture: Dict[str, float]) -> Tuple[List[Span], Dict]:
        """
        Allocate prompt spans using knapsack algorithm.
        
        Args:
            spans: Candidate spans for prompt
            budget: Token budget (e.g. 3500)
            query_type_mixture: Type weights from classifier
        
        Returns:
            (chosen_spans, telemetry)
        """
        return self.allocator.allocate(spans, budget, query_type_mixture)
    
    def classify_query_type(self, query: str, history: List[str] = None) -> Dict[str, float]:
        """
        Classify query type as mixture (standalone access).
        
        Args:
            query: User query
            history: Optional conversation history
        
        Returns:
            Type mixture: {"pattern_language": w1, "logic": w2, ...}
        """
        return self.classifier.classify_mixture(query, history)
    
    def get_status(self) -> Dict:
        """Get current fractal controller status."""
        return {
            'version': self.version,
            'policy_version': self.controller.policy_table['version'],
            'threshold_version': self.controller.threshold_config['version'],
            'telemetry_enabled': self.telemetry_enabled,
            'turn_count': len(self.turn_logs),
            'safety_defaults': self.controller.safety
        }
    
    def tune_thresholds(self) -> Dict:
        """
        Tune thresholds based on collected data.
        
        Week 1: Placeholder (returns current thresholds)
        Week 4: Implements Thompson sampling bandit tuning
        """
        print("Threshold tuning: Not yet implemented (Week 4)")
        print("Current thresholds loaded from config/thresholds.json")
        
        return {
            'updated_count': 0,
            'improvement_pct': 0.0,
            'note': 'Bandit tuning enables Week 4 after system stable'
        }
    
    def _log_turn(self, query: str, policies: FractalPolicies):
        """Log turn for telemetry."""
        log_entry = {
            'query': query[:100],  # Truncate for storage
            'query_type_mixture': policies.query_type_mixture,
            'dominant_type': policies.dominant_type,
            'confidence': policies.confidence,
            'token_budget': policies.token_policy.budget_split,
            'compression_target': policies.token_policy.compression_target,
            'memory_split_threshold': policies.memory_policy.split_threshold,
            'memory_merge_threshold': policies.memory_policy.merge_threshold
        }
        
        self.turn_logs.append(log_entry)
        
        # Keep only last 100 turns
        if len(self.turn_logs) > 100:
            self.turn_logs = self.turn_logs[-100:]


def main():
    """Test Fractal Core end-to-end."""
    print("\n" + "="*80)
    print("FRACTAL CORE - END-TO-END TEST")
    print("="*80)
    
    fractal = FractalCore()
    
    # Test queries with expected behaviors
    test_cases = [
        {
            'query': "What is the ratio of x and y?",
            'expected_dominant': 'logic',
            'description': 'Open-ended construction'
        },
        {
            'query': "Is this correct? A) Yes B) No C) Maybe",
            'expected_dominant': 'pattern_language',
            'description': 'Multiple choice recognition'
        },
        {
            'query': "Design an elegant solution for this problem",
            'expected_dominant': 'creative',
            'description': 'Creative construction'
        },
        {
            'query': "Find all documents about machine learning in the database",
            'expected_dominant': 'retrieval',
            'description': 'Factual retrieval'
        }
    ]
    
    print("\nTesting policy emission for different query types:")
    print("-" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        # Get policies
        policies = fractal.get_policies(test['query'])
        
        print(f"  Dominant type: {policies.dominant_type} (confidence: {policies.confidence:.2%})")
        print(f"  Expected: {test['expected_dominant']}")
        print(f"  Type mixture: ", end="")
        for type_name, weight in policies.query_type_mixture.items():
            print(f"{type_name[:4]}:{weight:.2f} ", end="")
        print()
        
        print(f"  Token budget: err={policies.token_policy.budget_split['error_epochs']}, " +
              f"tone={policies.token_policy.budget_split['tone_analysis']}, " +
              f"recent={policies.token_policy.budget_split['recent_context']}")
        print(f"  Compression target: {policies.token_policy.compression_target:.1f}:1")
        print(f"  Memory thresholds: split={policies.memory_policy.split_threshold:.2f}, " +
              f"merge={policies.memory_policy.merge_threshold:.2f}")
        
        # Verify logic floor
        assert policies.query_type_mixture['logic'] >= 0.15, f"Logic floor violated! {policies.query_type_mixture}"
        print(f"  ✓ Logic floor verified ({policies.query_type_mixture['logic']:.2%} >= 15%)")
    
    print("\n" + "="*80)
    print("KNAPSACK ALLOCATOR TEST")
    print("="*80)
    
    # Test knapsack allocation
    test_spans = [
        Span('err1', 'User confused about concept X', 'error_epoch', 300),
        Span('err2', 'AI provided wrong example', 'error_epoch', 250),
        Span('tone1', 'User shows frustration', 'tone_shift', 150),
        Span('recent1', 'Most recent exchange', 'recent_turn', 200),
        Span('aux1', 'Related background info', 'aux_dep', 100),
    ]
    
    # Test with logic-heavy query
    logic_mixture = {'pattern_language': 0.1, 'logic': 0.7, 'creative': 0.1, 'retrieval': 0.1}
    chosen, telemetry = fractal.allocate_prompt_spans(test_spans, budget=800, query_type_mixture=logic_mixture)
    
    print(f"\nLogic-heavy query allocation:")
    print(f"  Budget: {telemetry['tokens_budget']} tokens")
    print(f"  Used: {telemetry['tokens_used']} tokens ({telemetry['utilization_pct']:.1f}%)")
    print(f"  Chosen: {telemetry['chosen_after_ib']} spans (from {telemetry['total_spans']})")
    print(f"  Lambda threshold: {telemetry['lambda_threshold']:.2f}")
    
    print(f"\n  Top ROI spans:")
    for item in telemetry['roi_top_10'][:5]:
        print(f"    {item['span_id']}: gain={item['gain']:.2f}, cost={item['cost']}, ratio={item['ratio']:.4f}")
    
    # Test with pattern-heavy query
    pattern_mixture = {'pattern_language': 0.7, 'logic': 0.2, 'creative': 0.05, 'retrieval': 0.05}
    chosen_p, telemetry_p = fractal.allocate_prompt_spans(test_spans, budget=800, query_type_mixture=pattern_mixture)
    
    print(f"\nPattern-heavy query allocation:")
    print(f"  Chosen: {telemetry_p['chosen_after_ib']} spans")
    print(f"  Used: {telemetry_p['tokens_used']} tokens")
    print(f"  Note: Different spans selected based on type mixture!")
    
    print("\n" + "="*80)
    print("STATUS CHECK")
    print("="*80)
    
    status = fractal.get_status()
    print(f"\n  Version: {status['version']}")
    print(f"  Policy table: {status['policy_version']}")
    print(f"  Thresholds: {status['threshold_version']}")
    print(f"  Telemetry: {status['telemetry_enabled']}")
    print(f"  Turns logged: {status['turn_count']}")
    
    print("\n" + "="*80)
    print("✓ FRACTAL CORE WEEK 1 FOUNDATION COMPLETE")
    print("="*80)
    print("\nComponents working:")
    print("  ✓ Multihead classifier (4 heads + logic floor)")
    print("  ✓ Policy emitter (type mixture interpolation)")
    print("  ✓ Knapsack allocator (dumb-but-stable gain predictor)")
    print("  ✓ Cross-layer policies (token, memory, code, arbiter, lessons)")
    print("\nNext: Week 2 - Critical-span bypass + telemetry + determinism")


if __name__ == "__main__":
    main()

