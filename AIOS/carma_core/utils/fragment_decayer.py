"""
CARMA Fragment Decay System
Time-based decay with freshness boost for recently accessed fragments
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class DecayPolicy:
    """Fragment decay policy configuration"""
    base_decay_days: int = 90  # Fragments start decaying after 90 days
    decay_rate: float = 0.01  # 1% per day after base period
    freshness_boost_hours: int = 24  # Recent access gets boost
    freshness_multiplier: float = 2.0  # 2x retrieval score for fresh fragments
    min_score: float = 0.1  # Minimum score before hard removal
    access_weight: float = 0.5  # How much to weight access count vs age


class FragmentDecayer:
    """
    Applies time-based decay to fragment scores
    """
    
    def __init__(self, 
                 cache_dir: str = 'data_core/FractalCache',
                 policy: DecayPolicy = None):
        self.cache_dir = Path(cache_dir)
        self.registry_file = self.cache_dir / 'registry.json'
        self.policy = policy or DecayPolicy()
    
    def calculate_decay_score(self, 
                              last_accessed: str,
                              access_count: int,
                              created: str = None) -> float:
        """
        Calculate decay score for a fragment
        
        Returns:
            Score between 0-1, where:
            - 1.0 = fresh, high value
            - 0.1-0.9 = aging, medium value
            - <0.1 = decayed, candidate for removal
        """
        try:
            last_access_dt = datetime.fromisoformat(last_accessed)
        except Exception as e:
            last_access_dt = datetime.now()
        
        # Calculate age in days
        age_days = (datetime.now() - last_access_dt).days
        
        # Apply freshness boost (recent access = higher score)
        freshness_hours = (datetime.now() - last_access_dt).total_seconds() / 3600
        if freshness_hours < self.policy.freshness_boost_hours:
            freshness_factor = self.policy.freshness_multiplier
        else:
            freshness_factor = 1.0
        
        # Calculate base score from age
        if age_days <= self.policy.base_decay_days:
            # Within base period - no decay
            age_score = 1.0
        else:
            # Apply decay
            days_over = age_days - self.policy.base_decay_days
            decay = days_over * self.policy.decay_rate
            age_score = max(self.policy.min_score, 1.0 - decay)
        
        # Calculate access score (log scale)
        import math
        access_score = min(1.0, math.log10(access_count + 1) / math.log10(100))
        
        # Combine scores
        combined = (
            age_score * (1 - self.policy.access_weight) +
            access_score * self.policy.access_weight
        )
        
        # Apply freshness boost
        final_score = min(1.0, combined * freshness_factor)
        
        return final_score
    
    def apply_decay(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Apply decay to all fragments and recommend removals
        
        Args:
            dry_run: If True, only report what would be removed
        
        Returns:
            Decay summary
        """
        if not self.registry_file.exists():
            return {'error': 'Registry file not found'}
        
        # Load registry
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        # Calculate decay scores
        decay_scores = {}
        removal_candidates = []
        
        for fid, fragment in registry.items():
            last_accessed = fragment.get('last_accessed', datetime.now().isoformat())
            access_count = fragment.get('access_count', 0)
            created = fragment.get('created', last_accessed)
            
            score = self.calculate_decay_score(last_accessed, access_count, created)
            decay_scores[fid] = score
            
            # Mark for removal if below threshold
            if score < self.policy.min_score:
                removal_candidates.append({
                    'fragment_id': fid,
                    'score': score,
                    'access_count': access_count,
                    'last_accessed': last_accessed
                })
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_fragments': len(registry),
            'avg_score': sum(decay_scores.values()) / len(decay_scores) if decay_scores else 0.0,
            'removal_candidates': len(removal_candidates),
            'dry_run': dry_run
        }
        
        # Execute removal if not dry run
        if not dry_run and removal_candidates:
            for candidate in removal_candidates:
                fid = candidate['fragment_id']
                if fid in registry:
                    del registry[fid]
            
            # Save updated registry
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
            
            summary['actually_removed'] = len(removal_candidates)
        
        summary['candidates'] = removal_candidates[:10]  # First 10 for inspection
        
        return summary
    
    def boost_fresh_fragments(self, hours: int = 24) -> Dict[str, Any]:
        """
        Identify recently accessed fragments for freshness boost
        
        Args:
            hours: Consider fragments accessed within this many hours as "fresh"
        
        Returns:
            Summary of fresh fragments
        """
        if not self.registry_file.exists():
            return {'error': 'Registry file not found'}
        
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        cutoff = datetime.now() - timedelta(hours=hours)
        fresh_fragments = []
        
        for fid, fragment in registry.items():
            try:
                last_accessed = datetime.fromisoformat(fragment.get('last_accessed', ''))
                if last_accessed >= cutoff:
                    fresh_fragments.append({
                        'fragment_id': fid,
                        'last_accessed': fragment['last_accessed'],
                        'access_count': fragment.get('access_count', 0)
                    })
            except Exception as e:
                continue
        
        return {
            'timestamp': datetime.now().isoformat(),
            'hours': hours,
            'total_fragments': len(registry),
            'fresh_count': len(fresh_fragments),
            'fresh_pct': len(fresh_fragments) / len(registry) * 100 if registry else 0.0,
            'fresh_fragments': fresh_fragments[:20]  # First 20
        }


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fragment Decay System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Decay command
    decay_parser = subparsers.add_parser('decay', help='Apply decay and remove old fragments')
    decay_parser.add_argument('--execute', action='store_true', help='Execute removal (default: dry-run)')
    
    # Fresh command
    fresh_parser = subparsers.add_parser('fresh', help='Show fresh fragments')
    fresh_parser.add_argument('--hours', type=int, default=24, help='Freshness window in hours')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    decayer = FragmentDecayer()
    
    if args.command == 'decay':
        result = decayer.apply_decay(dry_run=not args.execute)
        
        print("="*70)
        print("FRAGMENT DECAY ANALYSIS")
        print("="*70)
        print(f"Total fragments: {result['total_fragments']}")
        print(f"Average decay score: {result['avg_score']:.3f}")
        print(f"Removal candidates: {result['removal_candidates']}")
        
        if result['candidates']:
            print("\nCandidates for removal:")
            for c in result['candidates']:
                print(f"  {c['fragment_id']}: score={c['score']:.3f}, access={c['access_count']}")
        
        if result['dry_run']:
            print("\nDRY RUN - No changes made")
            print("Run with --execute to remove decayed fragments")
        else:
            print(f"\n✓ Removed {result.get('actually_removed', 0)} fragments")
        
        print("="*70)
    
    elif args.command == 'fresh':
        result = decayer.boost_fresh_fragments(hours=args.hours)
        
        print("="*70)
        print(f"FRESH FRAGMENTS (Last {args.hours}h)")
        print("="*70)
        print(f"Total fragments: {result['total_fragments']}")
        print(f"Fresh count: {result['fresh_count']} ({result['fresh_pct']:.1f}%)")
        
        if result['fresh_fragments']:
            print("\nRecently accessed:")
            for f in result['fresh_fragments'][:10]:
                print(f"  {f['fragment_id']}: {f['access_count']} accesses, last at {f['last_accessed']}")
        
        print("="*70)


if __name__ == "__main__":
    main()

