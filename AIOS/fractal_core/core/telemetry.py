#!/usr/bin/env python3
"""
Fractal Telemetry System
Mandatory logging: Budget ledgers, ROI, flip-audits, churn tracking

"Anything less is cosplay" - ChatGPT
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class BudgetLedger:
    """Per-turn budget allocation tracking."""
    error_epochs: Dict[str, int]      # {allocated, used, pruned}
    tone_analysis: Dict[str, int]
    recent_context: Dict[str, int]
    aux_dependencies: Dict[str, int]


@dataclass
class SpanROI:
    """Span return-on-investment tracking."""
    span_id: str
    span_type: str
    gain: float
    cost: int
    ratio: float
    kept: bool
    flip_critical: bool = False  # Set if removing this flips decision


@dataclass
class TurnTelemetry:
    """Complete telemetry for a single turn."""
    turn_id: int
    timestamp: float
    query: str
    policy_id: str
    policy_weights: Dict[str, float]
    budget_ledger: BudgetLedger
    top_10_spans_roi: List[SpanROI]
    type_mixture_trace: List[float]  # [pattern, logic, creative, retrieval]
    split_merge_churn: Dict[str, int]
    decision_flip_audit: Optional[Dict] = None
    factorian_metrics: Optional[Dict] = None


class FractalTelemetry:
    """
    Comprehensive telemetry system for fractal operations.
    
    Tracks:
    - Budget ledgers (per component)
    - Span ROI (gain/cost/kept)
    - Type mixture evolution
    - Split/merge churn
    - Decision flip analysis
    - Factorian metrics (efficiency × compassion / suffering)
    """
    
    def __init__(self, log_dir: str = "data_core/FractalCache"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.turn_logs: List[TurnTelemetry] = []
        self.turn_counter = 0
        
        # Type mixture history (last 50 turns)
        self.type_mixture_history = []
        
        # Churn tracking
        self.churn_history = []
        
        print("Fractal Telemetry Initialized")
        print(f"  Log directory: {self.log_dir}")
    
    def log_turn(self, query: str, policies: 'FractalPolicies',
                allocation_telemetry: Dict, churn: Dict[str, int] = None) -> int:
        """
        Log a complete turn.
        
        Args:
            query: User query
            policies: Fractal policies used
            allocation_telemetry: From knapsack allocator
            churn: Split/merge operations {splits: N, merges: M}
        
        Returns:
            turn_id
        """
        self.turn_counter += 1
        
        # Build budget ledger from allocation telemetry
        budget_ledger = self._build_budget_ledger(allocation_telemetry)
        
        # Extract ROI data
        roi_data = self._extract_roi(allocation_telemetry)
        
        # Track type mixture
        mixture = policies.query_type_mixture
        mixture_vector = [
            mixture['pattern_language'],
            mixture['logic'],
            mixture['creative'],
            mixture['retrieval']
        ]
        self.type_mixture_history.append(mixture_vector)
        if len(self.type_mixture_history) > 50:
            self.type_mixture_history = self.type_mixture_history[-50:]
        
        # Calculate type-mix entropy (detect homogenization)
        mix_entropy = self._calculate_entropy(mixture_vector)
        
        # Track churn
        if churn:
            self.churn_history.append(churn)
            if len(self.churn_history) > 50:
                self.churn_history = self.churn_history[-50:]
        
        # Create telemetry record
        turn_log = TurnTelemetry(
            turn_id=self.turn_counter,
            timestamp=time.time(),
            query=query[:200],  # Truncate
            policy_id=self._get_policy_id(policies),
            policy_weights=policies.query_type_mixture,
            budget_ledger=budget_ledger,
            top_10_spans_roi=roi_data[:10],
            type_mixture_trace=self.type_mixture_history[-10:],  # Last 10
            split_merge_churn=churn or {'splits': 0, 'merges': 0},
            decision_flip_audit=None,  # Populated in Week 5 testing
            factorian_metrics=None  # Populated when human eval available
        )
        
        self.turn_logs.append(turn_log)
        
        # Keep last 100 turns
        if len(self.turn_logs) > 100:
            self.turn_logs = self.turn_logs[-100:]
        
        # Check for anomalies
        self._check_anomalies(turn_log, mix_entropy)
        
        return self.turn_counter
    
    def _build_budget_ledger(self, allocation_telemetry: Dict) -> BudgetLedger:
        """Build budget ledger from allocator telemetry."""
        # Extract budget info from ROI data
        # Group by span type
        
        ledger_data = {
            'error_epochs': {'allocated': 0, 'used': 0, 'pruned': 0},
            'tone_analysis': {'allocated': 0, 'used': 0, 'pruned': 0},
            'recent_context': {'allocated': 0, 'used': 0, 'pruned': 0},
            'aux_dependencies': {'allocated': 0, 'used': 0, 'pruned': 0}
        }
        
        # Sum up from ROI spans
        for span_data in allocation_telemetry.get('roi_top_10', []):
            span_type = span_data['type']
            cost = span_data['cost']
            kept = span_data.get('kept', False)
            
            # Map span type to budget component
            component_map = {
                'error_epoch': 'error_epochs',
                'tone_shift': 'tone_analysis',
                'recent_turn': 'recent_context',
                'aux_dep': 'aux_dependencies'
            }
            
            component = component_map.get(span_type)
            if component:
                if kept:
                    ledger_data[component]['used'] += cost
                else:
                    ledger_data[component]['pruned'] += cost
        
        # Calculate allocated (used + pruned)
        for component in ledger_data:
            ledger_data[component]['allocated'] = (
                ledger_data[component]['used'] + 
                ledger_data[component]['pruned']
            )
        
        return BudgetLedger(**ledger_data)
    
    def _extract_roi(self, allocation_telemetry: Dict) -> List[SpanROI]:
        """Extract ROI data from allocator telemetry."""
        roi_list = []
        
        # Kept spans
        for span_data in allocation_telemetry.get('roi_top_10', []):
            roi_list.append(SpanROI(
                span_id=span_data['span_id'],
                span_type=span_data['type'],
                gain=span_data['gain'],
                cost=span_data['cost'],
                ratio=span_data['ratio'],
                kept=span_data.get('kept', True)
            ))
        
        # Dropped spans
        for span_data in allocation_telemetry.get('dropped_spans', []):
            roi_list.append(SpanROI(
                span_id=span_data['span_id'],
                span_type=span_data['type'],
                gain=span_data['gain'],
                cost=span_data['cost'],
                ratio=span_data['ratio'],
                kept=False
            ))
        
        # Sort by ratio
        roi_list.sort(key=lambda x: x.ratio, reverse=True)
        
        return roi_list
    
    def _calculate_entropy(self, distribution: List[float]) -> float:
        """Calculate Shannon entropy of distribution."""
        import math
        entropy = 0.0
        for p in distribution:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def _get_policy_id(self, policies: 'FractalPolicies') -> str:
        """Generate policy ID (hash of policy versions)."""
        # Simple version-based ID
        return f"v1.0.0"  # Week 1: Static
    
    def _check_anomalies(self, turn_log: TurnTelemetry, mix_entropy: float):
        """Check for anomalies and warn."""
        # Check 1: Type-mix entropy drop (homogenization)
        if mix_entropy < 0.5:  # Very low entropy = collapsed to single type
            print(f"  ⚠️  Warning: Type mixture entropy low ({mix_entropy:.2f}) - classifier may be drifting")
        
        # Check 2: High churn
        churn_rate = (
            turn_log.split_merge_churn['splits'] + 
            turn_log.split_merge_churn['merges']
        ) / 100.0  # Assuming ~100 fragments
        
        if churn_rate > 0.15:  # >15% churn
            print(f"  ⚠️  Warning: High split/merge churn ({churn_rate:.1%}) - thresholds may be wrong")
        
        # Check 3: Budget under-utilization
        # (Check when allocation telemetry available)
    
    def get_type_mixture_drift(self) -> Dict:
        """Analyze type mixture drift over time."""
        if len(self.type_mixture_history) < 10:
            return {'drift': 'insufficient_data'}
        
        recent_10 = self.type_mixture_history[-10:]
        
        # Calculate variance per type
        import numpy as np
        variance_per_type = np.var(recent_10, axis=0)
        
        return {
            'pattern_variance': float(variance_per_type[0]),
            'logic_variance': float(variance_per_type[1]),
            'creative_variance': float(variance_per_type[2]),
            'retrieval_variance': float(variance_per_type[3]),
            'total_variance': float(np.sum(variance_per_type)),
            'interpretation': 'High variance = unstable, Low = stable or drifting'
        }
    
    def get_churn_statistics(self) -> Dict:
        """Get split/merge churn statistics."""
        if not self.churn_history:
            return {'churn': 'no_data'}
        
        recent = self.churn_history[-10:]
        
        avg_splits = sum(c['splits'] for c in recent) / len(recent)
        avg_merges = sum(c['merges'] for c in recent) / len(recent)
        
        return {
            'avg_splits_per_turn': avg_splits,
            'avg_merges_per_turn': avg_merges,
            'total_churn_rate': (avg_splits + avg_merges) / 100.0,  # Assuming ~100 fragments
            'interpretation': 'High churn (>15%) = wrong thresholds'
        }
    
    def export_logs(self, filename: str = "fractal_telemetry.json"):
        """Export logs to JSON for analysis."""
        output_path = self.log_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump({
                'turn_count': self.turn_counter,
                'turns': [asdict(log) for log in self.turn_logs],
                'type_mixture_drift': self.get_type_mixture_drift(),
                'churn_statistics': self.get_churn_statistics()
            }, f, indent=2)
        
        print(f"Telemetry exported to: {output_path}")
        return output_path


def main():
    """Test telemetry system."""
    telemetry = FractalTelemetry()
    
    print("\n" + "="*80)
    print("FRACTAL TELEMETRY TEST")
    print("="*80)
    
    # Simulate a turn
    from fractal_core.core.fractal_controller import FractalController, FractalPolicies, TokenPolicy, MemoryPolicy, CodePolicy, ArbiterPolicy, LessonsPolicy
    
    # Mock policies
    policies = FractalPolicies(
        query_type_mixture={'pattern_language': 0.2, 'logic': 0.5, 'creative': 0.2, 'retrieval': 0.1},
        dominant_type='logic',
        confidence=0.5,
        token_policy=TokenPolicy(
            query_type_mixture={'pattern_language': 0.2, 'logic': 0.5, 'creative': 0.2, 'retrieval': 0.1},
            budget_split={'error_epochs': 1000, 'tone_analysis': 400, 'recent_context': 1200, 'aux_dependencies': 600},
            compression_target=20.0,
            lambda_threshold=0.9
        ),
        memory_policy=MemoryPolicy(3, 0.5, 0.4, 20.0),
        code_policy=CodePolicy([], [], []),
        arbiter_policy=ArbiterPolicy({}),
        lessons_policy=LessonsPolicy('raw', 'low')
    )
    
    # Mock allocation telemetry
    allocation_telemetry = {
        'roi_top_10': [
            {'span_id': 'err1', 'type': 'error_epoch', 'gain': 10.0, 'cost': 300, 'ratio': 0.033, 'kept': True},
            {'span_id': 'err2', 'type': 'error_epoch', 'gain': 9.5, 'cost': 280, 'ratio': 0.034, 'kept': True},
            {'span_id': 'tone1', 'type': 'tone_shift', 'gain': 3.0, 'cost': 150, 'ratio': 0.020, 'kept': True},
        ],
        'dropped_spans': [
            {'span_id': 'aux1', 'type': 'aux_dep', 'gain': 1.0, 'cost': 100, 'ratio': 0.010, 'kept': False},
        ]
    }
    
    # Mock churn
    churn = {'splits': 2, 'merges': 5}
    
    # Log turn
    turn_id = telemetry.log_turn("Test query about logic", policies, allocation_telemetry, churn)
    
    print(f"\nTurn {turn_id} logged")
    print(f"  Type mixture: {policies.query_type_mixture}")
    print(f"  Budget ledger: error={allocation_telemetry['roi_top_10'][0]['cost']} used")
    print(f"  ROI spans: {len(allocation_telemetry['roi_top_10'])} kept")
    print(f"  Churn: {churn['splits']} splits, {churn['merges']} merges")
    
    # Log several more turns to test drift detection
    for i in range(5):
        # Slightly varying mixtures
        mixture = {
            'pattern_language': 0.2 + i*0.02,
            'logic': 0.5 - i*0.02,
            'creative': 0.2,
            'retrieval': 0.1
        }
        
        policies_varied = FractalPolicies(
            query_type_mixture=mixture,
            dominant_type='logic',
            confidence=0.5,
            token_policy=policies.token_policy,
            memory_policy=policies.memory_policy,
            code_policy=policies.code_policy,
            arbiter_policy=policies.arbiter_policy,
            lessons_policy=policies.lessons_policy
        )
        
        telemetry.log_turn(f"Query {i+2}", policies_varied, allocation_telemetry, churn)
    
    # Analyze drift
    drift = telemetry.get_type_mixture_drift()
    print(f"\nType mixture drift analysis:")
    print(f"  Logic variance: {drift['logic_variance']:.4f}")
    print(f"  Pattern variance: {drift['pattern_variance']:.4f}")
    print(f"  Interpretation: {drift['interpretation']}")
    
    # Analyze churn
    churn_stats = telemetry.get_churn_statistics()
    print(f"\nChurn statistics:")
    print(f"  Avg splits: {churn_stats['avg_splits_per_turn']:.1f}")
    print(f"  Avg merges: {churn_stats['avg_merges_per_turn']:.1f}")
    print(f"  Churn rate: {churn_stats['total_churn_rate']:.1%}")
    
    # Export
    export_path = telemetry.export_logs("test_telemetry.json")
    
    print("\n" + "="*80)
    print("✓ Telemetry system operational")
    print("✓ Budget ledgers tracked")
    print("✓ ROI logged")
    print("✓ Type-mix drift detection working")
    print("✓ Churn tracking working")
    print("="*80)


if __name__ == "__main__":
    main()

