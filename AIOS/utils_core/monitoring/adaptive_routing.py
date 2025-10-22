"""
Adaptive Routing Controller
Adjusts conversation math weights based on hypothesis test results.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import random


@dataclass
class AdaptiveConfig:
    """Configuration for adaptive routing"""
    # A/B bucket assignment
    control_bucket_pct: float = 0.5  # 50% control, 50% treatment
    
    # Adaptation parameters
    min_samples_before_adapt: int = 10  # Minimum conversation messages before adapting
    adaptation_strength: float = 0.1  # How much to adjust weights (0.0-1.0)
    
    # Quality thresholds
    min_quality_rate: float = 0.6  # Minimum 60% hypothesis pass rate to adapt
    max_latency_ms: float = 20000.0  # Maximum 20s latency
    
    # Persistence
    state_file: str = "data_core/analytics/adaptive_routing_state.json"


@dataclass
class AdaptiveBucket:
    """A/B test bucket state"""
    bucket_id: str  # 'control' or 'treatment'
    boundary_offset: float = 0.0  # Adjustment to routing boundary
    sample_count: int = 0  # Number of messages processed
    
    # Metrics
    quality_score: float = 0.0
    avg_latency_ms: float = 0.0
    hypothesis_pass_rate: float = 0.0


class AdaptiveRouter:
    """
    Adaptive routing controller that adjusts conversation math weights
    based on hypothesis test results.
    """
    
    def __init__(self, config: Optional[AdaptiveConfig] = None):
        self.config = config or AdaptiveConfig()
        self.buckets: Dict[str, AdaptiveBucket] = {
            'control': AdaptiveBucket(bucket_id='control'),
            'treatment': AdaptiveBucket(bucket_id='treatment')
        }
        self.conversation_buckets: Dict[str, str] = {}  # conv_id -> bucket_id
        
        # Load previous state if exists
        self._load_state()
    
    def assign_bucket(self, conv_id: str) -> str:
        """
        Assign a conversation to a bucket (control or treatment).
        Uses deterministic hashing for consistent assignment.
        """
        if conv_id in self.conversation_buckets:
            return self.conversation_buckets[conv_id]
        
        # Deterministic assignment based on conv_id hash
        hash_val = hash(conv_id) % 100
        bucket = 'control' if hash_val < (self.config.control_bucket_pct * 100) else 'treatment'
        
        self.conversation_buckets[conv_id] = bucket
        return bucket
    
    def current_boundary(self, conv_id: Optional[str] = None) -> float:
        """
        Get the current routing boundary (0.5 baseline).
        Treatment bucket may have offset applied.
        """
        if conv_id is None:
            return 0.5
        
        bucket_id = self.assign_bucket(conv_id)
        bucket = self.buckets[bucket_id]
        
        # Baseline is 0.5, treatment may have offset
        boundary = 0.5
        if bucket_id == 'treatment':
            boundary += bucket.boundary_offset
        
        # Clamp to valid range [0.4, 0.6]
        return max(0.4, min(0.6, boundary))
    
    def update_from_hypotheses(
        self,
        hypothesis_results: Dict[str, Any],
        msg_seq: int,
        conv_id: str
    ) -> Dict[str, Any]:
        """
        Update adaptive routing based on hypothesis test results.
        
        Args:
            hypothesis_results: Results from CARMA hypothesis testing
            msg_seq: Message sequence number in conversation
            conv_id: Conversation ID
        
        Returns:
            Adaptive routing metadata
        """
        bucket_id = self.assign_bucket(conv_id)
        bucket = self.buckets[bucket_id]
        
        # Update bucket metrics
        bucket.sample_count += 1
        
        # Extract metrics from hypothesis results
        if 'rates' in hypothesis_results:
            rates = hypothesis_results['rates']
            bucket.quality_score = rates.get('quality', 0.0)
            bucket.avg_latency_ms = rates.get('latency', 0.0) * 1000  # Convert to ms
        
        if 'passed' in hypothesis_results and 'failed' in hypothesis_results:
            total = hypothesis_results['passed'] + hypothesis_results['failed']
            if total > 0:
                bucket.hypothesis_pass_rate = hypothesis_results['passed'] / total
        
        # Adaptive logic: adjust treatment bucket based on performance
        adaptation = {}
        if bucket_id == 'treatment' and bucket.sample_count >= self.config.min_samples_before_adapt:
            control = self.buckets['control']
            
            # Compare treatment to control
            quality_delta = bucket.hypothesis_pass_rate - control.hypothesis_pass_rate
            latency_delta = bucket.avg_latency_ms - control.avg_latency_ms
            
            # Adapt if treatment is better
            if quality_delta > 0.05 and latency_delta < 1000:  # 5% quality improvement, <1s latency increase
                # Push boundary toward main model (increase weight)
                adjustment = self.config.adaptation_strength * quality_delta
                bucket.boundary_offset = max(-0.1, min(0.1, bucket.boundary_offset + adjustment))
                
                adaptation = {
                    'adapted': True,
                    'direction': 'toward_main_model' if adjustment > 0 else 'toward_embedder',
                    'adjustment': adjustment,
                    'new_boundary': self.current_boundary(conv_id),
                    'reason': f"Quality delta: {quality_delta:.3f}, Latency delta: {latency_delta:.0f}ms"
                }
            elif quality_delta < -0.05 or latency_delta > 2000:  # 5% quality drop or >2s latency increase
                # Pull boundary toward embedder (decrease weight)
                adjustment = -self.config.adaptation_strength * abs(quality_delta)
                bucket.boundary_offset = max(-0.1, min(0.1, bucket.boundary_offset + adjustment))
                
                adaptation = {
                    'adapted': True,
                    'direction': 'toward_embedder',
                    'adjustment': adjustment,
                    'new_boundary': self.current_boundary(conv_id),
                    'reason': f"Quality delta: {quality_delta:.3f}, Latency delta: {latency_delta:.0f}ms"
                }
        
        # Save state
        self._save_state()
        
        return {
            'bucket': bucket_id,
            'boundary': self.current_boundary(conv_id),
            'sample_count': bucket.sample_count,
            'metrics': {
                'quality_score': bucket.quality_score,
                'avg_latency_ms': bucket.avg_latency_ms,
                'hypothesis_pass_rate': bucket.hypothesis_pass_rate
            },
            'adaptive': adaptation if adaptation else {'adapted': False}
        }
    
    def _save_state(self):
        """Save adaptive routing state to disk"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'buckets': {
                bucket_id: {
                    'boundary_offset': bucket.boundary_offset,
                    'sample_count': bucket.sample_count,
                    'quality_score': bucket.quality_score,
                    'avg_latency_ms': bucket.avg_latency_ms,
                    'hypothesis_pass_rate': bucket.hypothesis_pass_rate
                }
                for bucket_id, bucket in self.buckets.items()
            },
            'conversation_buckets': self.conversation_buckets
        }
        
        # Ensure directory exists
        state_path = Path(self.config.state_file)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write atomically
        temp_path = state_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(state, f, indent=2)
        temp_path.replace(state_path)
    
    def _load_state(self):
        """Load adaptive routing state from disk"""
        state_path = Path(self.config.state_file)
        if not state_path.exists():
            return
        
        try:
            with open(state_path, 'r') as f:
                state = json.load(f)
            
            # Restore bucket state
            for bucket_id, bucket_data in state.get('buckets', {}).items():
                if bucket_id in self.buckets:
                    self.buckets[bucket_id].boundary_offset = bucket_data.get('boundary_offset', 0.0)
                    self.buckets[bucket_id].sample_count = bucket_data.get('sample_count', 0)
                    self.buckets[bucket_id].quality_score = bucket_data.get('quality_score', 0.0)
                    self.buckets[bucket_id].avg_latency_ms = bucket_data.get('avg_latency_ms', 0.0)
                    self.buckets[bucket_id].hypothesis_pass_rate = bucket_data.get('hypothesis_pass_rate', 0.0)
            
            # Restore conversation assignments
            self.conversation_buckets = state.get('conversation_buckets', {})
        
        except Exception as e:
            print(f"Warning: Failed to load adaptive routing state: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of adaptive routing state"""
        return {
            'buckets': {
                bucket_id: {
                    'boundary': 0.5 if bucket_id == 'control' else 0.5 + bucket.boundary_offset,
                    'sample_count': bucket.sample_count,
                    'metrics': {
                        'quality_score': bucket.quality_score,
                        'avg_latency_ms': bucket.avg_latency_ms,
                        'hypothesis_pass_rate': bucket.hypothesis_pass_rate
                    }
                }
                for bucket_id, bucket in self.buckets.items()
            },
            'total_conversations': len(self.conversation_buckets),
            'config': {
                'control_bucket_pct': self.config.control_bucket_pct,
                'adaptation_strength': self.config.adaptation_strength,
                'min_samples_before_adapt': self.config.min_samples_before_adapt
            }
        }


# Singleton instance
_adaptive_router: Optional[AdaptiveRouter] = None


def get_adaptive_router(config: Optional[AdaptiveConfig] = None) -> AdaptiveRouter:
    """Get the singleton adaptive router instance"""
    global _adaptive_router
    if _adaptive_router is None:
        _adaptive_router = AdaptiveRouter(config)
    return _adaptive_router

