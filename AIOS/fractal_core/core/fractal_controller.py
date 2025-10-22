#!/usr/bin/env python3
"""
Fractal Controller - Unified Policy Emitter
Single controller emits policies for all layers (token, memory, code, arbiter, lessons)

Week 1: Static policy tables
Week 4: Enable bandit tuning (after system stable)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np

from fractal_core.core.multihead_classifier import MultiheadClassifier


@dataclass
class TokenPolicy:
    """Token allocation policy."""
    query_type_mixture: Dict[str, float]
    budget_split: Dict[str, int]  # {error, tone, recent, aux}
    compression_target: float
    lambda_threshold: float


@dataclass
class MemoryPolicy:
    """Memory split/merge policy."""
    cache_depth: int
    split_threshold: float
    merge_threshold: float
    compression_ratio_target: float


@dataclass
class CodePolicy:
    """Module loading policy."""
    modules_enabled: List[str]
    modules_cold: List[str]
    lazy_load_order: List[str]


@dataclass
class ArbiterPolicy:
    """Arbiter evaluation policy."""
    rubric_weights: Dict[str, float]
    noise_sigma: float = 0.05


@dataclass
class LessonsPolicy:
    """Lesson storage policy."""
    store_mode: str  # 'raw', 'pattern', 'superpattern'
    compression_level: str


@dataclass
class FractalPolicies:
    """Complete policy set for all layers."""
    query_type_mixture: Dict[str, float]
    dominant_type: str
    confidence: float
    token_policy: TokenPolicy
    memory_policy: MemoryPolicy
    code_policy: CodePolicy
    arbiter_policy: ArbiterPolicy
    lessons_policy: LessonsPolicy


class FractalController:
    """
    Unified controller applying Information Bottleneck at all scales.
    
    Core principle: Compress state, not stuff.
    Factorian: Efficiency enables compassion.
    """
    
    def __init__(self, policy_file: str = None, threshold_file: str = None):
        # Load configuration
        if policy_file is None:
            policy_file = Path(__file__).parent.parent / "config" / "policy_table.json"
        if threshold_file is None:
            threshold_file = Path(__file__).parent.parent / "config" / "thresholds.json"
        
        with open(policy_file, 'r') as f:
            self.policy_table = json.load(f)
        
        with open(threshold_file, 'r') as f:
            self.threshold_config = json.load(f)
        
        # Initialize classifier
        self.classifier = MultiheadClassifier()
        
        # Cross-layer precedence (for conflict resolution)
        self.precedence = self.policy_table.get('cross_layer_precedence', 
            ['retrieval', 'logic', 'pattern_language', 'creative'])
        
        # Safety defaults
        self.safety = self.policy_table.get('safety_defaults', {})
        
        print("Fractal Controller Initialized")
        print(f"  Policy version: {self.policy_table['version']}")
        print(f"  Threshold version: {self.threshold_config['version']}")
        print(f"  Safety: Logic floor {self.safety.get('logic_floor_pct', 0.15)*100:.0f}%")
    
    def get_policies(self, query: str, history: List[str] = None,
                    global_budget: Dict = None) -> FractalPolicies:
        """
        Main entry point: Get policies for all layers.
        
        Args:
            query: Current user query
            history: Conversation history
            global_budget: {tokens, latency_ms, cost_usd, vram_mb}
        
        Returns:
            Complete policy set for all layers
        """
        # 1. Classify as type mixture (not single label)
        query_type_mixture = self.classifier.classify_mixture(query, history)
        dominant_type, confidence = self.classifier.get_dominant_type(query_type_mixture)
        
        # Set default budget if not provided
        if global_budget is None:
            global_budget = {'tokens': 3500, 'latency_ms': 500, 'cost_usd': 0.01, 'vram_mb': 2000}
        
        # 2. Emit policies for each layer
        token_policy = self._emit_token_policy(query_type_mixture, global_budget)
        memory_policy = self._emit_memory_policy(query_type_mixture)
        code_policy = self._emit_code_policy(query_type_mixture)
        arbiter_policy = self._emit_arbiter_policy(query_type_mixture)
        lessons_policy = self._emit_lessons_policy(query_type_mixture)
        
        return FractalPolicies(
            query_type_mixture=query_type_mixture,
            dominant_type=dominant_type,
            confidence=confidence,
            token_policy=token_policy,
            memory_policy=memory_policy,
            code_policy=code_policy,
            arbiter_policy=arbiter_policy,
            lessons_policy=lessons_policy
        )
    
    def _emit_token_policy(self, query_type_mixture: Dict[str, float],
                          global_budget: Dict) -> TokenPolicy:
        """Emit token allocation policy using mixture interpolation."""
        budget = global_budget['tokens']
        
        # Get Travis's axes if available (skip in iteration)
        travis_axes = query_type_mixture.get('travis_axes', {})
        
        # Interpolate budget splits across types (skip travis_axes metadata)
        budget_split = {}
        for component in ['error_epochs', 'tone_analysis', 'recent_context', 'aux_dependencies']:
            budget_split[component] = 0
            for type_name, weight in query_type_mixture.items():
                if type_name == 'travis_axes':  # Skip metadata
                    continue
                type_policy = self.policy_table[type_name]
                component_budget = type_policy['token_budget'].get(component, 0)
                budget_split[component] += weight * component_budget
            budget_split[component] = int(budget_split[component])
        
        # Calculate target compression ratio
        compression_target = 0
        for type_name, weight in query_type_mixture.items():
            if type_name == 'travis_axes':  # Skip metadata
                continue
            type_policy = self.policy_table[type_name]
            compression_target += weight * type_policy['target_compression']
        
        # TRAVIS'S AXIS ADJUSTMENT:
        # Use his axes to adjust compression strategy
        if travis_axes:
            dominant_axis = travis_axes.get('dominant_axis', 'logic_creative')
            dominant_strength = travis_axes.get('dominant_strength', 0.5)
            
            if dominant_axis == 'pattern_language' and dominant_strength > 0.55:
                # Pattern/Language dominant → increase compression (safe)
                compression_boost = (dominant_strength - 0.5) * 20.0
                compression_target += compression_boost
            elif dominant_axis == 'logic_creative' and dominant_strength > 0.55:
                # Logic/Creative dominant → decrease compression (preserve reasoning)
                compression_penalty = (dominant_strength - 0.5) * 10.0
                compression_target = max(15.0, compression_target - compression_penalty)
        
        # Calculate lambda threshold for IB guardrail
        lambda_threshold = self._calculate_lambda_mixture(query_type_mixture)
        
        return TokenPolicy(
            query_type_mixture=query_type_mixture,
            budget_split=budget_split,
            compression_target=compression_target,
            lambda_threshold=lambda_threshold
        )
    
    def _emit_memory_policy(self, query_type_mixture: Dict[str, float]) -> MemoryPolicy:
        """Emit memory policy with interpolated thresholds."""
        # Interpolate split threshold
        split_threshold = 0
        merge_threshold = 0
        cache_depth = 0
        compression_target = 0
        
        for type_name, weight in query_type_mixture.items():
            if type_name == 'travis_axes':  # Skip metadata
                continue
            type_policy = self.policy_table[type_name]
            memory_config = type_policy['memory']
            
            split_threshold += weight * memory_config['split_threshold_base']
            merge_threshold += weight * memory_config['merge_threshold_base']
            cache_depth += weight * memory_config['cache_depth']
            
            # Target ratio
            ratio_range = type_policy['compression_ratio_range']
            compression_target += weight * sum(ratio_range) / 2
        
        cache_depth = int(cache_depth)
        
        return MemoryPolicy(
            cache_depth=cache_depth,
            split_threshold=split_threshold,
            merge_threshold=merge_threshold,
            compression_ratio_target=compression_target
        )
    
    def _emit_code_policy(self, query_type_mixture: Dict[str, float]) -> CodePolicy:
        """Emit module loading policy (placeholder - Week 3)."""
        # Filter out travis_axes metadata, then get dominant type
        type_weights = {k: v for k, v in query_type_mixture.items() if k != 'travis_axes'}
        dominant_type = max(type_weights.items(), key=lambda x: x[1])[0]
        
        module_map = {
            'pattern_language': {
                'enabled': ['examples_core', 'style_core'],
                'cold': ['reason_core']
            },
            'logic': {
                'enabled': ['reason_core', 'trace_core'],
                'cold': ['examples_core']
            },
            'creative': {
                'enabled': ['vibe_core', 'constraint_core'],
                'cold': []
            },
            'retrieval': {
                'enabled': ['fact_core', 'citation_core'],
                'cold': ['vibe_core']
            }
        }
        
        config = module_map.get(dominant_type, {'enabled': [], 'cold': []})
        
        return CodePolicy(
            modules_enabled=config['enabled'],
            modules_cold=config['cold'],
            lazy_load_order=config['enabled'] + config['cold']
        )
    
    def _emit_arbiter_policy(self, query_type_mixture: Dict[str, float]) -> ArbiterPolicy:
        """Emit arbiter rubric policy with mixture interpolation."""
        # Collect all possible rubric metrics across types
        all_metrics = set()
        for type_name in query_type_mixture:
            if type_name == 'travis_axes':  # Skip metadata
                continue
            type_policy = self.policy_table[type_name]
            all_metrics.update(type_policy['arbiter_rubric'].keys())
        
        # Interpolate rubric weights
        rubric_weights = {}
        for metric in all_metrics:
            rubric_weights[metric] = 0
            for type_name, weight in query_type_mixture.items():
                if type_name == 'travis_axes':  # Skip metadata
                    continue
                type_policy = self.policy_table[type_name]
                metric_weight = type_policy['arbiter_rubric'].get(metric, 0.0)
                rubric_weights[metric] += weight * metric_weight
        
        # Normalize to sum to 1.0
        total = sum(rubric_weights.values())
        if total > 0:
            rubric_weights = {k: v/total for k, v in rubric_weights.items()}
        
        return ArbiterPolicy(
            rubric_weights=rubric_weights,
            noise_sigma=self.safety.get('arbiter_noise_sigma', 0.05)
        )
    
    def _emit_lessons_policy(self, query_type_mixture: Dict[str, float]) -> LessonsPolicy:
        """Emit lesson storage policy."""
        # Filter out travis_axes metadata
        type_weights = {k: v for k, v in query_type_mixture.items() if k != 'travis_axes'}
        dominant_type = max(type_weights.items(), key=lambda x: x[1])[0]
        
        # Storage mode based on dominant type
        if query_type_mixture['pattern_language'] > 0.5:
            mode = 'pattern'  # Convert to templates
            compression = 'high'
        elif query_type_mixture['logic'] > 0.5:
            mode = 'raw'  # Preserve chains
            compression = 'low'
        elif query_type_mixture['creative'] > 0.5:
            mode = 'superpattern'  # Abstract patterns
            compression = 'medium'
        else:
            mode = 'mixed'
            compression = 'medium'
        
        return LessonsPolicy(
            store_mode=mode,
            compression_level=compression
        )
    
    def _calculate_lambda_mixture(self, query_type_mixture: Dict[str, float]) -> float:
        """Calculate lambda threshold for IB guardrail (mixture-weighted)."""
        lambda_values = {
            'pattern_language': 0.5,
            'logic': 1.0,
            'creative': 0.6,
            'retrieval': 1.2
        }
        
        return sum(
            query_type_mixture[type_name] * lambda_values[type_name]
            for type_name in query_type_mixture
            if type_name != 'travis_axes'  # Skip metadata
        )


def main():
    """Test the fractal controller."""
    controller = FractalController()
    
    test_queries = [
        ("What is the ratio of x and y?", "logic"),
        ("Is this correct? A) Yes B) No", "pattern"),
        ("Design a creative solution", "creative"),
        ("Find documents about AI", "retrieval"),
    ]
    
    print("\n" + "="*80)
    print("FRACTAL CONTROLLER TEST")
    print("="*80)
    
    for query, expected_type in test_queries:
        policies = controller.get_policies(query)
        
        print(f"\nQuery: {query}")
        print(f"Expected: {expected_type}")
        print(f"Dominant: {policies.dominant_type} ({policies.confidence:.2%})")
        print(f"Mixture: {policies.query_type_mixture}")
        print(f"Token budget: {policies.token_policy.budget_split}")
        print(f"Compression target: {policies.token_policy.compression_target:.1f}:1")
        print(f"Memory: split={policies.memory_policy.split_threshold:.2f}, merge={policies.memory_policy.merge_threshold:.2f}")
        print(f"Arbiter rubric: {policies.arbiter_policy.rubric_weights}")
        
        # Verify logic floor
        assert policies.query_type_mixture['logic'] >= 0.15, "Logic floor violated!"
    
    print("\n" + "="*80)
    print("✓ Controller emitting consistent policies across layers")
    print("✓ Logic floor (15%) enforced")
    print("="*80)


if __name__ == "__main__":
    main()

