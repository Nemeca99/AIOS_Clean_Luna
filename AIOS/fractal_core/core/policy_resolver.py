#!/usr/bin/env python3
"""
Policy Resolver - Cross-Layer Conflict Resolution
Safeguard #7: When layers conflict, precedence determines winner

Precedence: retrieval > logic > pattern_language > creative
"""

from typing import Dict, Any


class PolicyResolver:
    """
    Resolves conflicts when different layers want different things.
    
    Example conflict:
    - Memory says: "Merge fragments" (compression)
    - Token says: "Expand reasoning" (detail)
    
    Resolver uses precedence: retrieval > logic > pattern > creative
    """
    
    def __init__(self, precedence: list = None):
        self.precedence = precedence or ['retrieval', 'logic', 'pattern_language', 'creative']
        
        # Conflict log
        self.conflicts_logged = []
        
        print("Policy Resolver Initialized")
        print(f"  Precedence: {' > '.join(self.precedence)}")
    
    def resolve_compression_conflict(self, memory_wants_compress: bool,
                                    token_wants_expand: bool,
                                    query_type_mixture: Dict[str, float]) -> Dict:
        """
        Resolve conflict between memory and token layers.
        
        Args:
            memory_wants_compress: Memory layer wants to merge/compress
            token_wants_expand: Token layer wants more detail
            query_type_mixture: Current type weights
        
        Returns:
            Resolution decision
        """
        if memory_wants_compress == (not token_wants_expand):
            # No conflict
            return {
                'conflict': False,
                'decision': 'compress' if memory_wants_compress else 'expand',
                'reason': 'layers_agree'
            }
        
        # Conflict exists - use precedence
        dominant_type = max(query_type_mixture.items(), key=lambda x: x[1])[0]
        
        # Higher precedence types prefer detail preservation
        precedence_rank = self.precedence.index(dominant_type) if dominant_type in self.precedence else 99
        
        # retrieval (0) and logic (1) prefer detail
        # pattern (2) and creative (3) allow compression
        
        if precedence_rank <= 1:  # retrieval or logic
            decision = 'expand'  # Preserve detail
            winner = 'token_layer'
        else:  # pattern or creative
            decision = 'compress'  # Allow compression
            winner = 'memory_layer'
        
        # Log conflict
        conflict_record = {
            'conflict': True,
            'decision': decision,
            'winner': winner,
            'dominant_type': dominant_type,
            'precedence_rank': precedence_rank,
            'reason': f'{dominant_type}_precedence'
        }
        
        self.conflicts_logged.append(conflict_record)
        
        return conflict_record
    
    def resolve_budget_conflict(self, requested_budgets: Dict[str, int],
                               available_budget: int,
                               query_type_mixture: Dict[str, float]) -> Dict[str, int]:
        """
        Resolve when requested budgets exceed available.
        
        Uses precedence to prioritize budget allocation.
        
        Args:
            requested_budgets: {component: requested_tokens}
            available_budget: Total available
            query_type_mixture: Type weights
        
        Returns:
            Allocated budgets (scaled to fit)
        """
        total_requested = sum(requested_budgets.values())
        
        if total_requested <= available_budget:
            # No conflict
            return requested_budgets
        
        # Conflict - need to scale down
        # Determine dominant type
        dominant_type = max(query_type_mixture.items(), key=lambda x: x[1])[0]
        
        # Protect components based on precedence
        if dominant_type in ['retrieval', 'logic']:
            # Protect error_epochs and aux_dependencies (reasoning/facts)
            protected = {'error_epochs', 'aux_dependencies'}
        else:
            # Protect recent_context and tone (style/recency)
            protected = {'recent_context', 'tone_analysis'}
        
        # Allocate: protected gets 100%, others scaled proportionally
        allocated = {}
        protected_total = sum(requested_budgets[k] for k in protected if k in requested_budgets)
        remaining = available_budget - protected_total
        
        unprotected_total = sum(requested_budgets[k] for k in requested_budgets if k not in protected)
        
        for component, requested in requested_budgets.items():
            if component in protected:
                allocated[component] = requested
            else:
                if unprotected_total > 0:
                    scale = remaining / unprotected_total
                    allocated[component] = int(requested * scale)
                else:
                    allocated[component] = 0
        
        # Log conflict
        self.conflicts_logged.append({
            'type': 'budget_conflict',
            'total_requested': total_requested,
            'available': available_budget,
            'protected': list(protected),
            'dominant_type': dominant_type
        })
        
        return allocated
    
    def get_conflict_statistics(self) -> Dict:
        """Get conflict resolution statistics."""
        if not self.conflicts_logged:
            return {'conflicts': 0, 'types': {}}
        
        conflict_types = {}
        for conflict in self.conflicts_logged:
            ctype = conflict.get('type', 'unknown')
            conflict_types[ctype] = conflict_types.get(ctype, 0) + 1
        
        return {
            'total_conflicts': len(self.conflicts_logged),
            'conflict_types': conflict_types,
            'latest_conflict': self.conflicts_logged[-1] if self.conflicts_logged else None
        }


def main():
    """Test policy resolver."""
    resolver = PolicyResolver()
    
    print("\n" + "="*80)
    print("POLICY RESOLVER TEST")
    print("="*80)
    
    # Test 1: Compression conflict
    print("\nTest 1: Memory vs Token conflict (Logic query)")
    
    logic_mixture = {'pattern_language': 0.1, 'logic': 0.7, 'creative': 0.1, 'retrieval': 0.1}
    
    result = resolver.resolve_compression_conflict(
        memory_wants_compress=True,
        token_wants_expand=True,
        query_type_mixture=logic_mixture
    )
    
    print(f"  Memory: wants to compress")
    print(f"  Token: wants to expand")
    print(f"  Dominant type: {result.get('dominant_type')}")
    print(f"  Decision: {result['decision']}")
    print(f"  Winner: {result.get('winner', 'N/A')}")
    print(f"  ✓ Logic precedence favors detail preservation")
    
    assert result['decision'] == 'expand', "Logic should prefer expansion!"
    
    # Test 2: Pattern query (should allow compression)
    print("\nTest 2: Memory vs Token conflict (Pattern query)")
    
    pattern_mixture = {'pattern_language': 0.7, 'logic': 0.2, 'creative': 0.05, 'retrieval': 0.05}
    
    result2 = resolver.resolve_compression_conflict(
        memory_wants_compress=True,
        token_wants_expand=True,
        query_type_mixture=pattern_mixture
    )
    
    print(f"  Dominant type: {result2.get('dominant_type')}")
    print(f"  Decision: {result2['decision']}")
    print(f"  ✓ Pattern precedence allows compression")
    
    assert result2['decision'] == 'compress', "Pattern should allow compression!"
    
    # Test 3: Budget conflict
    print("\nTest 3: Budget allocation conflict")
    
    requested = {
        'error_epochs': 1200,
        'tone_analysis': 800,
        'recent_context': 1200,
        'aux_dependencies': 800
    }
    
    available = 3000  # Total requested: 4000, available: 3000
    
    allocated = resolver.resolve_budget_conflict(requested, available, logic_mixture)
    
    print(f"  Requested: {sum(requested.values())} tokens")
    print(f"  Available: {available} tokens")
    print(f"  Conflict: {sum(requested.values()) - available} tokens over budget")
    print(f"  Allocated: {allocated}")
    print(f"  Total allocated: {sum(allocated.values())}")
    print(f"  Protected components (logic): error_epochs, aux_dependencies")
    
    assert sum(allocated.values()) <= available, "Exceeded budget!"
    assert allocated['error_epochs'] == requested['error_epochs'], "Error not protected!"
    print(f"  ✓ Protected components get full budget")
    print(f"  ✓ Others scaled proportionally")
    
    # Statistics
    stats = resolver.get_conflict_statistics()
    print(f"\nConflict Statistics:")
    print(f"  Total conflicts: {stats['total_conflicts']}")
    print(f"  By type: {stats['conflict_types']}")
    
    print("\n" + "="*80)
    print("✓ Policy resolver operational")
    print("✓ Precedence enforced: retrieval > logic > pattern > creative")
    print("✓ Conflicts logged and resolved transparently")
    print("="*80)


if __name__ == "__main__":
    main()

