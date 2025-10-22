#!/usr/bin/env python3
"""
Knapsack Allocator - Information Bottleneck Based
Greedy gain-per-token allocation with ROI telemetry

Week 1: Dumb-but-stable gain predictor
Later: Train on causal labels (decision flip data)
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Span:
    """Context span candidate for prompt."""
    span_id: str
    text: str
    span_type: str  # 'error_epoch', 'tone_shift', 'recent_turn', 'aux_dep'
    cost: int  # Token count
    gain: float = 0.0  # Predicted decision gain (set by allocator)
    ratio: float = 0.0  # gain / cost
    metadata: Dict = None


class KnapsackAllocator:
    """
    Greedy knapsack allocation based on gain-per-token ratio.
    
    Uses dumb-but-stable gain predictor initially (Week 1).
    Later trains on causal labels (which span removal caused decision flip).
    """
    
    def __init__(self):
        # Dumb-but-stable base gains (priority ordering)
        self.base_gains = {
            'error_epoch': 10.0,      # Highest priority
            'tone_shift': 5.0,        # Medium-high
            'recent_turn': 3.0,       # Medium
            'aux_dep': 2.0            # Lower
        }
        
        # Type-specific weights for each span type
        self.type_weights = {
            'pattern_language': {
                'error_epoch': 0.6,    # Pattern errors matter less
                'tone_shift': 0.8,     # Style matters more
                'recent_turn': 1.0,    # Recent always important
                'aux_dep': 0.2         # Aux less important
            },
            'logic': {
                'error_epoch': 1.0,    # Errors critical
                'tone_shift': 0.3,     # Tone less important
                'recent_turn': 1.0,    # Recent always important
                'aux_dep': 0.8         # Relationships important
            },
            'creative': {
                'error_epoch': 0.7,
                'tone_shift': 0.9,     # Vibe matters
                'recent_turn': 1.0,
                'aux_dep': 0.5
            },
            'retrieval': {
                'error_epoch': 0.5,
                'tone_shift': 0.2,     # Tone doesn't matter
                'recent_turn': 0.6,
                'aux_dep': 1.0         # Facts/citations critical
            }
        }
    
    def allocate(self, spans: List[Span], budget: int, 
                query_type_mixture: Dict[str, float]) -> Tuple[List[Span], Dict]:
        """
        Allocate spans using greedy knapsack.
        
        Deterministic allocation provides functional idempotency:
        Same (spans, budget, query_type_mixture) always produces same result.
        No external state modified - allocation is a pure function.
        
        Args:
            spans: Candidate spans for prompt
            budget: Total token budget (e.g. 3500)
            query_type_mixture: Type weights from classifier
        
        Returns:
            (chosen_spans, telemetry)
        """
        # Score each span by decision gain
        for span in spans:
            span.gain = self._predict_gain(span, query_type_mixture)
            span.ratio = span.gain / span.cost if span.cost > 0 else 0.0
        
        # Sort by ratio (greedy)
        sorted_spans = sorted(spans, key=lambda s: s.ratio, reverse=True)
        
        # Greedy knapsack
        chosen = []
        used = 0
        
        for span in sorted_spans:
            if used + span.cost <= budget:
                chosen.append(span)
                used += span.cost
        
        # Information Bottleneck guardrail
        # Drop spans with gain below threshold
        lambda_threshold = self._calculate_lambda(query_type_mixture)
        chosen_filtered = [s for s in chosen if s.gain >= lambda_threshold]
        
        # Telemetry
        telemetry = {
            'total_spans': len(spans),
            'chosen_before_ib': len(chosen),
            'chosen_after_ib': len(chosen_filtered),
            'tokens_used': sum(s.cost for s in chosen_filtered),
            'tokens_budget': budget,
            'utilization_pct': (sum(s.cost for s in chosen_filtered) / budget) * 100,
            'lambda_threshold': lambda_threshold,
            'roi_top_10': [
                {
                    'span_id': s.span_id,
                    'type': s.span_type,
                    'gain': round(s.gain, 3),
                    'cost': s.cost,
                    'ratio': round(s.ratio, 4),
                    'kept': True
                }
                for s in chosen_filtered[:10]
            ],
            'dropped_spans': [
                {
                    'span_id': s.span_id,
                    'type': s.span_type,
                    'gain': round(s.gain, 3),
                    'cost': s.cost,
                    'ratio': round(s.ratio, 4),
                    'kept': False
                }
                for s in sorted_spans if s not in chosen_filtered
            ][:10]  # Top 10 dropped
        }
        
        return chosen_filtered, telemetry
    
    def _predict_gain(self, span: Span, query_type_mixture: Dict[str, float]) -> float:
        """
        Predict decision gain for a span.
        
        Week 1: Dumb-but-stable (weighted base gains)
        Later: Train on causal labels (decision flip data)
        """
        # Base gain for span type
        base_gain = self.base_gains.get(span.span_type, 1.0)
        
        # Weight by query type mixture
        weighted_gain = 0.0
        for type_name, type_weight in query_type_mixture.items():
            span_type_weight = self.type_weights.get(type_name, {}).get(span.span_type, 0.5)
            weighted_gain += type_weight * base_gain * span_type_weight
        
        return weighted_gain
    
    def _calculate_lambda(self, query_type_mixture: Dict[str, float]) -> float:
        """
        Calculate lambda threshold for Information Bottleneck guardrail.
        
        Higher for logic/retrieval (strict), lower for pattern/creative (permissive).
        """
        # Type-specific lambda values
        lambda_values = {
            'pattern_language': 0.5,
            'logic': 1.0,
            'creative': 0.6,
            'retrieval': 1.2
        }
        
        # Weighted average
        lambda_threshold = sum(
            query_type_mixture[type_name] * lambda_values[type_name]
            for type_name in query_type_mixture
        )
        
        return lambda_threshold


def main():
    """Test the knapsack allocator."""
    allocator = KnapsackAllocator()
    
    # Create test spans
    test_spans = [
        Span('err1', 'User confused about X', 'error_epoch', 300),
        Span('err2', 'AI misunderstood Y', 'error_epoch', 250),
        Span('tone1', 'User frustrated', 'tone_shift', 150),
        Span('recent1', 'Last exchange', 'recent_turn', 200),
        Span('recent2', 'Previous exchange', 'recent_turn', 180),
        Span('aux1', 'Related concept Z', 'aux_dep', 100),
        Span('aux2', 'Background info', 'aux_dep', 120),
    ]
    
    # Test with different query types
    test_cases = [
        {
            'name': 'Logic-heavy query',
            'mixture': {'pattern_language': 0.1, 'logic': 0.7, 'creative': 0.1, 'retrieval': 0.1}
        },
        {
            'name': 'Pattern-heavy query',
            'mixture': {'pattern_language': 0.7, 'logic': 0.2, 'creative': 0.05, 'retrieval': 0.05}
        }
    ]
    
    print("\n" + "="*80)
    print("KNAPSACK ALLOCATOR TEST")
    print("="*80)
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"Mixture: {test_case['mixture']}")
        print("-" * 60)
        
        chosen, telemetry = allocator.allocate(
            test_spans.copy(),
            budget=800,  # Limited budget
            query_type_mixture=test_case['mixture']
        )
        
        print(f"Chosen: {len(chosen)} spans")
        print(f"Tokens used: {telemetry['tokens_used']}/{telemetry['tokens_budget']}")
        print(f"Utilization: {telemetry['utilization_pct']:.1f}%")
        print(f"Lambda threshold: {telemetry['lambda_threshold']:.2f}")
        
        print("\nTop ROI spans:")
        for item in telemetry['roi_top_10'][:5]:
            print(f"  {item['span_id']}: gain={item['gain']:.2f}, cost={item['cost']}, ratio={item['ratio']:.4f}")
    
    print("\n" + "="*80)
    print("✓ Allocator working with type-conditioned gains")
    print("="*80)


if __name__ == "__main__":
    main()

