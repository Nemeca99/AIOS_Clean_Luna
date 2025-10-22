#!/usr/bin/env python3
"""
Safety Rails for Retrieval Mode
Safeguard #8: Provenance quota + contradiction kill-switch

When retrieval weight > 0.5:
- Require ≥K grounded snippets (provenance quota)
- If sources contradict → kill-switch to "ask clarifying question"
- Force citations always
"""

from typing import List, Dict, Optional


class SafetyRails:
    """
    Safety system for factual/retrieval queries.
    
    Prevents:
    - Hallucination (requires provenance)
    - Contradictions (kill-switch)
    - Unsourced claims (forces citations)
    """
    
    def __init__(self):
        self.conflicts_logged = []
        self.provenance_quota = 3  # Minimum grounded snippets
        self.contradiction_threshold = 0.7  # Semantic distance indicating conflict
        
        # Kill-switch templates
        self.clarifying_template = "I found conflicting information. Could you clarify: {conflict_summary}"
        self.uncertain_template = "I don't have enough reliable sources to answer that. Could you provide more context?"
        
        print("Safety Rails Initialized")
        print(f"  Provenance quota: {self.provenance_quota} sources minimum")
        print(f"  Contradiction detection: Enabled")
    
    def check_retrieval_safety(self, query_type_mixture: Dict[str, float],
                              sources: List[Dict], 
                              proposed_answer: str) -> Dict:
        """
        Check safety for retrieval-heavy queries.
        
        Args:
            query_type_mixture: Type weights
            sources: Retrieved sources with {text, source_id, confidence}
            proposed_answer: AI's proposed response
        
        Returns:
            Safety check result with action
        """
        retrieval_weight = query_type_mixture.get('retrieval', 0.0)
        
        # Only enforce if retrieval is significant
        if retrieval_weight < 0.5:
            return {
                'safe': True,
                'action': 'proceed',
                'reason': 'not_retrieval_mode'
            }
        
        # Check 1: Provenance quota
        grounded_sources = [s for s in sources if s.get('confidence', 0) > 0.6]
        
        if len(grounded_sources) < self.provenance_quota:
            return {
                'safe': False,
                'action': 'use_template',
                'template': self.uncertain_template,
                'reason': f'insufficient_provenance: {len(grounded_sources)} < {self.provenance_quota}',
                'sources_found': len(grounded_sources),
                'quota': self.provenance_quota
            }
        
        # Check 2: Source contradiction
        contradiction_detected, conflict_summary = self._detect_contradictions(sources)
        
        if contradiction_detected:
            return {
                'safe': False,
                'action': 'use_template',
                'template': self.clarifying_template.format(conflict_summary=conflict_summary),
                'reason': 'source_contradiction',
                'conflict': conflict_summary
            }
        
        # Check 3: Answer grounded in sources
        citations_present = self._check_citations(proposed_answer, sources)
        
        if not citations_present:
            return {
                'safe': False,
                'action': 'add_citations',
                'reason': 'missing_citations',
                'sources': [s['source_id'] for s in grounded_sources]
            }
        
        # All checks passed
        return {
            'safe': True,
            'action': 'proceed',
            'reason': 'all_checks_passed',
            'provenance_count': len(grounded_sources),
            'citations_present': True
        }
    
    def _detect_contradictions(self, sources: List[Dict]) -> tuple:
        """
        Detect if sources contradict each other.
        
        Week 3: Simple heuristic (keyword conflicts)
        Week 4: Semantic distance based
        
        Returns:
            (contradiction_detected, conflict_summary)
        """
        if len(sources) < 2:
            return False, ""
        
        # Simple heuristic: Look for contradiction keywords
        contradiction_keywords = [
            ('yes', 'no'),
            ('true', 'false'),
            ('correct', 'incorrect'),
            ('valid', 'invalid'),
            ('always', 'never')
        ]
        
        texts = [s.get('text', '').lower() for s in sources]
        
        for keyword_pair in contradiction_keywords:
            kw1, kw2 = keyword_pair
            has_kw1 = any(kw1 in text for text in texts)
            has_kw2 = any(kw2 in text for text in texts)
            
            if has_kw1 and has_kw2:
                # Potential contradiction
                sources_with_kw1 = [s['source_id'] for s, text in zip(sources, texts) if kw1 in text]
                sources_with_kw2 = [s['source_id'] for s, text in zip(sources, texts) if kw2 in text]
                
                conflict_summary = f"Source {sources_with_kw1[0]} says '{kw1}' but {sources_with_kw2[0]} says '{kw2}'"
                
                return True, conflict_summary
        
        return False, ""
    
    def _check_citations(self, answer: str, sources: List[Dict]) -> bool:
        """
        Check if answer contains citations to sources.
        
        Week 3: Simple check for source_id mentions
        Week 4: More sophisticated citation parsing
        
        Returns:
            True if citations present
        """
        answer_lower = answer.lower()
        
        # Check if any source_id is mentioned
        for source in sources:
            source_id = source.get('source_id', '')
            if source_id and source_id.lower() in answer_lower:
                return True
        
        # Check for citation markers
        citation_markers = ['[', ']', 'source:', 'according to', 'from']
        if any(marker in answer_lower for marker in citation_markers):
            return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """Get safety rail statistics."""
        return {
            'conflicts_detected': len(self.conflicts_logged),
            'provenance_quota': self.provenance_quota,
            'contradiction_threshold': self.contradiction_threshold
        }


def main():
    """Test safety rails."""
    rails = SafetyRails()
    
    print("\n" + "="*80)
    print("SAFETY RAILS TEST")
    print("="*80)
    
    # Test 1: Sufficient provenance
    print("\nTest 1: Sufficient provenance")
    
    good_sources = [
        {'text': 'Machine learning was developed in the 1950s', 'source_id': 'wiki_ml', 'confidence': 0.9},
        {'text': 'Alan Turing contributed to early AI', 'source_id': 'turing_bio', 'confidence': 0.95},
        {'text': 'Neural networks emerged in the 1980s', 'source_id': 'nn_history', 'confidence': 0.85}
    ]
    
    retrieval_mixture = {'pattern_language': 0.1, 'logic': 0.2, 'creative': 0.1, 'retrieval': 0.6}
    
    result = rails.check_retrieval_safety(
        retrieval_mixture,
        good_sources,
        "Machine learning was developed in the 1950s, according to wiki_ml"
    )
    
    print(f"  Retrieval weight: {retrieval_mixture['retrieval']:.1%}")
    print(f"  Sources: {len(good_sources)} (confidence > 0.6: {len([s for s in good_sources if s['confidence'] > 0.6])})")
    print(f"  Quota: {rails.provenance_quota}")
    print(f"  Safe: {result['safe']}")
    print(f"  Action: {result['action']}")
    
    assert result['safe'], "Should be safe with sufficient provenance!"
    print(f"  ✓ Provenance quota met")
    
    # Test 2: Insufficient provenance
    print("\nTest 2: Insufficient provenance")
    
    weak_sources = [
        {'text': 'I think ML started around 1950', 'source_id': 'uncertain', 'confidence': 0.3}
    ]
    
    result2 = rails.check_retrieval_safety(retrieval_mixture, weak_sources, "ML started in 1950")
    
    print(f"  Sources: {len(weak_sources)} (confidence > 0.6: {len([s for s in weak_sources if s['confidence'] > 0.6])})")
    print(f"  Safe: {result2['safe']}")
    print(f"  Action: {result2['action']}")
    print(f"  Reason: {result2['reason']}")
    
    assert not result2['safe'], "Should be unsafe with low provenance!"
    assert result2['action'] == 'use_template', "Should use uncertain template!"
    print(f"  ✓ Insufficient provenance detected")
    print(f"  ✓ Uncertain template triggered")
    
    # Test 3: Source contradiction
    print("\nTest 3: Contradicting sources")
    
    contradicting_sources = [
        {'text': 'The answer is yes, this is correct', 'source_id': 'source_a', 'confidence': 0.9},
        {'text': 'The answer is no, this is incorrect', 'source_id': 'source_b', 'confidence': 0.9},
        {'text': 'Additional info', 'source_id': 'source_c', 'confidence': 0.8}
    ]
    
    result3 = rails.check_retrieval_safety(retrieval_mixture, contradicting_sources, "The answer is yes")
    
    print(f"  Sources: {len(contradicting_sources)}")
    print(f"  Safe: {result3['safe']}")
    print(f"  Action: {result3['action']}")
    print(f"  Conflict detected: {result3.get('conflict', 'N/A')}")
    
    assert not result3['safe'], "Should detect contradiction!"
    assert result3['action'] == 'use_template', "Should use clarifying template!"
    print(f"  ✓ Contradiction detected")
    print(f"  ✓ Clarifying question triggered")
    
    
    print("\n" + "="*80)
    print("✓ Safety rails functional")
    print("✓ Provenance quota enforced")
    print("✓ Contradiction detection working")
    print("="*80)


if __name__ == "__main__":
    main()

