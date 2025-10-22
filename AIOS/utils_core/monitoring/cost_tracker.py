"""
Cost & Performance Tracker
Tracks token usage, API costs, latency, and cache hit rates
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    timestamp: str
    conv_id: str
    msg_id: int
    source: str  # main_model, embedder, cache
    tokens_prompt: int
    tokens_completion: int
    tokens_total: int
    latency_ms: float
    cache_hit: bool
    timeout: bool
    retries: int
    cost_usd: float


class CostTracker:
    """
    Tracks cost and performance metrics
    """
    
    # Pricing (adjust based on your LM Studio/API costs)
    PRICING = {
        'main_model': {
            'prompt': 0.0,  # LM Studio is free (localhost)
            'completion': 0.0
        },
        'embedder': {
            'prompt': 0.0,
            'completion': 0.0
        }
    }
    
    def __init__(self, metrics_file: str = 'data_core/analytics/cost_metrics.ndjson'):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory stats for current session
        self.session_stats = {
            'requests': 0,
            'cache_hits': 0,
            'timeouts': 0,
            'retries': 0,
            'total_tokens': 0,
            'total_latency_ms': 0.0,
            'total_cost_usd': 0.0
        }
    
    def log_request(self, metrics: RequestMetrics):
        """Log a request's metrics"""
        # Update session stats
        self.session_stats['requests'] += 1
        if metrics.cache_hit:
            self.session_stats['cache_hits'] += 1
        if metrics.timeout:
            self.session_stats['timeouts'] += 1
        self.session_stats['retries'] += metrics.retries
        self.session_stats['total_tokens'] += metrics.tokens_total
        self.session_stats['total_latency_ms'] += metrics.latency_ms
        self.session_stats['total_cost_usd'] += metrics.cost_usd
        
        # Append to file
        with open(self.metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(metrics), ensure_ascii=False) + '\n')
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        requests = self.session_stats['requests']
        
        return {
            'requests': requests,
            'cache_hit_rate': self.session_stats['cache_hits'] / requests if requests > 0 else 0.0,
            'timeout_rate': self.session_stats['timeouts'] / requests if requests > 0 else 0.0,
            'avg_retries': self.session_stats['retries'] / requests if requests > 0 else 0.0,
            'avg_tokens': self.session_stats['total_tokens'] / requests if requests > 0 else 0.0,
            'avg_latency_ms': self.session_stats['total_latency_ms'] / requests if requests > 0 else 0.0,
            'total_cost_usd': self.session_stats['total_cost_usd']
        }
    
    def calculate_cost(self, source: str, tokens_prompt: int, tokens_completion: int) -> float:
        """Calculate cost for a request"""
        pricing = self.PRICING.get(source, {'prompt': 0.0, 'completion': 0.0})
        cost = (tokens_prompt * pricing['prompt'] + tokens_completion * pricing['completion'])
        return cost
    
    def analyze_metrics(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """
        Analyze metrics from file
        
        Args:
            lookback_hours: Hours to look back
        
        Returns:
            Analysis summary
        """
        if not self.metrics_file.exists():
            return {'error': 'Metrics file not found'}
        
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        
        stats = defaultdict(lambda: {
            'count': 0,
            'tokens': 0,
            'latency_ms': 0.0,
            'cost_usd': 0.0
        })
        
        cache_hits = 0
        timeouts = 0
        total_retries = 0
        total_requests = 0
        
        with open(self.metrics_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    metrics = json.loads(line)
                    
                    # Check if within lookback window
                    ts = datetime.fromisoformat(metrics['timestamp'])
                    if ts < cutoff:
                        continue
                    
                    total_requests += 1
                    source = metrics['source']
                    
                    stats[source]['count'] += 1
                    stats[source]['tokens'] += metrics['tokens_total']
                    stats[source]['latency_ms'] += metrics['latency_ms']
                    stats[source]['cost_usd'] += metrics['cost_usd']
                    
                    if metrics['cache_hit']:
                        cache_hits += 1
                    if metrics['timeout']:
                        timeouts += 1
                    total_retries += metrics['retries']
                
                except Exception as e:
                    continue
        
        # Calculate aggregates
        summary = {
            'lookback_hours': lookback_hours,
            'total_requests': total_requests,
            'cache_hit_rate': cache_hits / total_requests if total_requests > 0 else 0.0,
            'timeout_rate': timeouts / total_requests if total_requests > 0 else 0.0,
            'avg_retries': total_retries / total_requests if total_requests > 0 else 0.0,
            'by_source': {}
        }
        
        for source, data in stats.items():
            if data['count'] > 0:
                summary['by_source'][source] = {
                    'count': data['count'],
                    'avg_tokens': data['tokens'] / data['count'],
                    'avg_latency_ms': data['latency_ms'] / data['count'],
                    'total_cost_usd': data['cost_usd']
                }
        
        return summary


# Global tracker instance
_cost_tracker: Optional[CostTracker] = None

def get_cost_tracker() -> CostTracker:
    """Get singleton cost tracker"""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cost & Performance Tracker')
    parser.add_argument('--hours', type=int, default=24, help='Hours to analyze (default: 24)')
    
    args = parser.parse_args()
    
    tracker = CostTracker()
    summary = tracker.analyze_metrics(lookback_hours=args.hours)
    
    if 'error' in summary:
        print(f"Error: {summary['error']}")
        return
    
    print("="*70)
    print(f"COST & PERFORMANCE ANALYSIS (Last {args.hours}h)")
    print("="*70)
    print(f"Total requests: {summary['total_requests']}")
    print(f"Cache hit rate: {summary['cache_hit_rate']:.1%}")
    print(f"Timeout rate: {summary['timeout_rate']:.1%}")
    print(f"Avg retries: {summary['avg_retries']:.2f}")
    
    print("\nBy source:")
    for source, data in summary['by_source'].items():
        print(f"\n  {source}:")
        print(f"    Requests: {data['count']}")
        print(f"    Avg tokens: {data['avg_tokens']:.0f}")
        print(f"    Avg latency: {data['avg_latency_ms']:.0f}ms")
        print(f"    Total cost: ${data['total_cost_usd']:.4f}")
    
    print("="*70)


if __name__ == "__main__":
    main()

