#!/usr/bin/env python3
"""
CARMA Memory Analytics
Memory analytics system for insights
"""

from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING
from datetime import datetime
from collections import defaultdict

if TYPE_CHECKING:
    from .fractal_cache import FractalMyceliumCache


class CARMAMemoryAnalytics:
    """Memory analytics system for CARMA insights."""
    
    def __init__(self):
        self.analytics_data = {
            'memory_growth': [],
            'access_patterns': [],
            'compression_stats': [],
            'cluster_evolution': []
        }
    
    def analyze_memory_system(self, cache: 'FractalMyceliumCache') -> Dict:
        """Analyze the memory system and provide insights."""
        analysis = {
            'memory_growth': self._analyze_memory_growth(cache),
            'access_patterns': self._analyze_access_patterns(cache),
            'fragment_distribution': self._analyze_fragment_distribution(cache),
            'temporal_patterns': self._analyze_temporal_patterns(cache),
            'recommendations': self._generate_recommendations(cache)
        }
        
        return analysis
    
    def _analyze_memory_growth(self, cache: 'FractalMyceliumCache') -> Dict:
        """Analyze memory growth patterns."""
        fragments = list(cache.file_registry.values())
        if not fragments:
            return {'growth_rate': 0.0, 'total_fragments': 0}
        
        timestamps = [f.get('timestamp', 0) for f in fragments if f.get('timestamp')]
        if len(timestamps) < 2:
            return {'growth_rate': 0.0, 'total_fragments': len(fragments)}
        
        timestamps.sort()
        time_span = timestamps[-1] - timestamps[0]
        growth_rate = len(timestamps) / (time_span / 3600) if time_span > 0 else 0  # fragments per hour
        
        return {
            'growth_rate': growth_rate,
            'total_fragments': len(fragments),
            'time_span_hours': time_span / 3600,
            'avg_fragments_per_hour': growth_rate
        }
    
    def _analyze_access_patterns(self, cache: 'FractalMyceliumCache') -> Dict:
        """Analyze memory access patterns."""
        fragments = list(cache.file_registry.values())
        access_counts = [f.get('access_count', 0) for f in fragments]
        
        if not access_counts:
            return {'avg_access': 0, 'access_distribution': {}}
        
        return {
            'avg_access': sum(access_counts) / len(access_counts),
            'max_access': max(access_counts),
            'min_access': min(access_counts),
            'access_distribution': {
                'high': len([c for c in access_counts if c > 10]),
                'medium': len([c for c in access_counts if 5 <= c <= 10]),
                'low': len([c for c in access_counts if c < 5])
            }
        }
    
    def _analyze_fragment_distribution(self, cache: 'FractalMyceliumCache') -> Dict:
        """Analyze fragment size and type distribution."""
        fragments = list(cache.file_registry.values())
        if not fragments:
            return {'size_distribution': {}, 'type_distribution': {}}
        
        sizes = [len(f.get('content', '')) for f in fragments]
        types = [f.get('type', 'unknown') for f in fragments]
        
        return {
            'size_distribution': {
                'small': len([s for s in sizes if s < 100]),
                'medium': len([s for s in sizes if 100 <= s < 500]),
                'large': len([s for s in sizes if s >= 500])
            },
            'type_distribution': {t: types.count(t) for t in set(types)},
            'avg_size': sum(sizes) / len(sizes),
            'total_content_size': sum(sizes)
        }
    
    def _analyze_temporal_patterns(self, cache: 'FractalMyceliumCache') -> Dict:
        """Analyze temporal patterns in memory creation."""
        fragments = list(cache.file_registry.values())
        timestamps = [f.get('timestamp', 0) for f in fragments if f.get('timestamp')]
        
        if len(timestamps) < 2:
            return {'temporal_distribution': {}, 'peak_hours': []}
        
        # Group by hour of day
        hour_counts = defaultdict(int)
        for ts in timestamps:
            hour = datetime.fromtimestamp(ts).hour
            hour_counts[hour] += 1
        
        peak_hours = [h for h, c in hour_counts.items() if c == max(hour_counts.values())]
        
        return {
            'temporal_distribution': dict(hour_counts),
            'peak_hours': peak_hours,
            'activity_level': 'high' if max(hour_counts.values()) > 5 else 'low'
        }
    
    def _generate_recommendations(self, cache: 'FractalMyceliumCache') -> List[str]:
        """Generate recommendations for memory system optimization."""
        recommendations = []
        fragments = list(cache.file_registry.values())
        
        if len(fragments) > 1000:
            recommendations.append("Consider enabling memory compression - large fragment count detected")
        
        access_counts = [f.get('access_count', 0) for f in fragments]
        if access_counts and max(access_counts) > 50:
            recommendations.append("High access frequency detected - consider caching frequently accessed fragments")
        
        sizes = [len(f.get('content', '')) for f in fragments]
        if sizes and sum(sizes) > 1000000:  # 1MB
            recommendations.append("Large memory footprint - consider implementing memory pruning")
        
        if len(fragments) > 100 and len(set(f.get('type', 'unknown') for f in fragments)) < 3:
            recommendations.append("Low fragment diversity - consider expanding memory types")
        
        return recommendations

if __name__ == "__main__":
    main()