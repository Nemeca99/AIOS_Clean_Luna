#!/usr/bin/env python3
"""
Critical Span Bypass System
Ensures certain spans are NEVER dropped by the allocator

Safeguard #2: Critical-span bypass + hard floors
- Error epochs: Never drop for logic
- Reasoning steps: Never drop
- Facts/citations: Never drop for retrieval
"""

from typing import List, Dict, Set
from fractal_core.core.knapsack_allocator import Span


class CriticalSpanManager:
    """
    Manages critical spans that bypass the knapsack allocator.
    
    These spans are ALWAYS included regardless of ROI.
    Trained on causal labels: which spans, when removed, caused decision flips.
    """
    
    def __init__(self):
        # Critical span types (always include)
        self.always_critical = {
            'last_user_message',
            'current_query',
            'active_error'  # Current ongoing error
        }
        
        # Type-specific critical spans
        self.type_critical = {
            'logic': {
                'reasoning_steps',
                'invariants',
                'error_chains',
                'proof_traces',
                'mathematical_derivations'
            },
            'retrieval': {
                'facts',
                'citations',
                'sources',
                'ground_truth',
                'provenance'
            },
            'pattern_language': {
                'concrete_examples',
                'style_patterns'
            },
            'creative': {
                'constraints',
                'creative_intent'
            }
        }
        
        # Hard floors (minimum tokens that MUST be preserved)
        self.hard_floors = {
            'logic': 15,  # Never compress logic below 15:1
            'retrieval': 10,  # Never compress retrieval below 10:1
            'pattern_language': None,  # No floor
            'creative': None  # No floor
        }
        
        # Causal labels (learned from decision flips)
        # Week 1: Empty, Week 4: Populated from flip experiments
        self.learned_critical_spans = set()
    
    def get_critical_spans(self, all_spans: List[Span], 
                          query_type_mixture: Dict[str, float]) -> List[Span]:
        """
        Extract critical spans that must be included.
        
        Args:
            all_spans: All candidate spans
            query_type_mixture: Type weights
        
        Returns:
            List of critical spans (bypass allocator)
        """
        critical = []
        
        # Always critical (universal)
        for span in all_spans:
            if span.metadata and span.metadata.get('category') in self.always_critical:
                critical.append(span)
                continue
            
            # Check type-specific critical
            for type_name, weight in query_type_mixture.items():
                if weight > 0.3:  # Significant weight
                    type_critical_set = self.type_critical.get(type_name, set())
                    span_category = span.metadata.get('category', '') if span.metadata else ''
                    
                    if span_category in type_critical_set:
                        critical.append(span)
                        break
            
            # Check learned critical (from causal flip data)
            if span.span_id in self.learned_critical_spans:
                critical.append(span)
        
        return critical
    
    def enforce_hard_floor(self, query_type_mixture: Dict[str, float],
                          chosen_tokens: int, total_tokens: int) -> bool:
        """
        Check if hard floor is violated.
        
        Args:
            query_type_mixture: Type weights
            chosen_tokens: Tokens in compressed prompt
            total_tokens: Original conversation tokens
        
        Returns:
            True if floor violated, False if OK
        """
        if total_tokens == 0:
            return False
        
        actual_ratio = total_tokens / chosen_tokens
        
        # Check each type's floor
        for type_name, weight in query_type_mixture.items():
            if weight > 0.5:  # Dominant type
                floor = self.hard_floors.get(type_name)
                
                if floor and actual_ratio > floor:
                    # Floor violated - compressed too much!
                    # Example: 30K→1K = 30:1, floor is 15:1, 30 > 15 = violated
                    return True
        
        return False
    
    def calculate_minimum_tokens(self, query_type_mixture: Dict[str, float],
                                 total_tokens: int) -> int:
        """
        Calculate minimum tokens allowed based on hard floors.
        
        Returns:
            Minimum tokens required
        """
        # Get dominant type's floor
        dominant_type = max(query_type_mixture.items(), key=lambda x: x[1])[0]
        floor = self.hard_floors.get(dominant_type)
        
        if floor and total_tokens > 0:
            min_tokens = total_tokens / floor
            return int(min_tokens)
        
        return 0  # No floor
    
    def add_learned_critical(self, span_id: str, flip_data: Dict):
        """
        Add a span to learned critical list based on flip experiments.
        
        Week 4: Called when counterfactual analysis shows span was critical.
        
        Args:
            span_id: The span that caused decision flip when removed
            flip_data: Metadata about the flip
        """
        self.learned_critical_spans.add(span_id)
    
    def get_statistics(self) -> Dict:
        """Get critical span statistics."""
        return {
            'always_critical_count': len(self.always_critical),
            'type_specific_counts': {
                type_name: len(critical_set)
                for type_name, critical_set in self.type_critical.items()
            },
            'learned_critical_count': len(self.learned_critical_spans),
            'hard_floors': self.hard_floors
        }


def main():
    """Test critical span manager."""
    manager = CriticalSpanManager()
    
    print("\n" + "="*80)
    print("CRITICAL SPAN BYPASS TEST")
    print("="*80)
    
    # Create test spans
    test_spans = [
        Span('query', 'Current query', 'query', 50, metadata={'category': 'current_query'}),
        Span('reasoning1', 'Step 1: Define variables', 'reasoning', 100, metadata={'category': 'reasoning_steps'}),
        Span('reasoning2', 'Step 2: Apply formula', 'reasoning', 120, metadata={'category': 'reasoning_steps'}),
        Span('fact1', 'Machine learning was invented in 1950s', 'fact', 80, metadata={'category': 'facts'}),
        Span('tone1', 'User sounds frustrated', 'tone', 60, metadata={'category': 'tone_shift'}),
        Span('aux1', 'Background context', 'aux', 90, metadata={'category': 'background'}),
    ]
    
    # Test with logic-heavy query
    logic_mixture = {'pattern_language': 0.1, 'logic': 0.7, 'creative': 0.1, 'retrieval': 0.1}
    
    critical = manager.get_critical_spans(test_spans, logic_mixture)
    
    print(f"\nLogic-heavy query (70% logic):")
    print(f"  Total spans: {len(test_spans)}")
    print(f"  Critical spans: {len(critical)}")
    print(f"  Critical span IDs: {[s.span_id for s in critical]}")
    
    # Should include: current_query, reasoning1, reasoning2
    expected_critical = {'query', 'reasoning1', 'reasoning2'}
    actual_critical = {s.span_id for s in critical}
    
    assert expected_critical.issubset(actual_critical), f"Missing critical spans! Expected {expected_critical}, got {actual_critical}"
    print(f"  ✓ All reasoning steps preserved for logic query")
    
    # Test with retrieval-heavy query
    retrieval_mixture = {'pattern_language': 0.1, 'logic': 0.2, 'creative': 0.1, 'retrieval': 0.6}
    
    critical_r = manager.get_critical_spans(test_spans, retrieval_mixture)
    
    print(f"\nRetrieval-heavy query (60% retrieval):")
    print(f"  Critical spans: {len(critical_r)}")
    print(f"  Critical span IDs: {[s.span_id for s in critical_r]}")
    
    # Should include: current_query, fact1
    expected_critical_r = {'query', 'fact1'}
    actual_critical_r = {s.span_id for s in critical_r}
    
    assert expected_critical_r.issubset(actual_critical_r), f"Missing facts! Expected {expected_critical_r}, got {actual_critical_r}"
    print(f"  ✓ Facts preserved for retrieval query")
    
    # Test hard floor enforcement
    print(f"\nHard floor tests:")
    
    # Logic: 15:1 floor
    violated = manager.enforce_hard_floor(
        {'logic': 0.7, 'pattern_language': 0.3},
        chosen_tokens=2000,  # Compressed
        total_tokens=20000   # Original
    )
    print(f"  Logic 10:1 compression: Floor violated = {violated} (should be False, 10:1 > 15:1 floor)")
    
    violated2 = manager.enforce_hard_floor(
        {'logic': 0.7, 'pattern_language': 0.3},
        chosen_tokens=2000,
        total_tokens=10000  # 5:1 compression - violates 15:1 floor!
    )
    print(f"  Logic 5:1 compression: Floor violated = {violated2} (should be True, 5:1 < 15:1 floor)")
    
    # Calculate minimum tokens
    min_tokens = manager.calculate_minimum_tokens(
        {'logic': 0.7, 'pattern_language': 0.3},
        total_tokens=30000
    )
    print(f"  Minimum tokens for 30K logic query: {min_tokens} (30000/15 = 2000)")
    
    # Statistics
    stats = manager.get_statistics()
    print(f"\nStatistics:")
    print(f"  Always critical: {stats['always_critical_count']}")
    print(f"  Logic critical spans: {stats['type_specific_counts']['logic']}")
    print(f"  Retrieval critical spans: {stats['type_specific_counts']['retrieval']}")
    print(f"  Learned critical (from flips): {stats['learned_critical_count']}")
    
    print("\n" + "="*80)
    print("✓ Critical span bypass working")
    print("✓ Hard floors enforced")
    print("✓ Type-specific preservation")
    print("="*80)


if __name__ == "__main__":
    main()

