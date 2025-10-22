"""
CARMA Memory Quality System
Deduplication, decay, and quality scoring for fragments
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FragmentQuality:
    """Quality metrics for a memory fragment"""
    fragment_id: str
    content_hash: str
    similarity_score: float  # 0-1, similarity to other fragments
    access_count: int
    last_accessed: str
    age_days: float
    decay_score: float  # 0-1, lower = should decay
    dedup_candidates: List[str]  # Similar fragment IDs


class MemoryQualityScorer:
    """
    Scores fragment quality for deduplication and decay decisions
    """
    
    def __init__(self, 
                 cache_dir: str = 'data_core/FractalCache',
                 similarity_threshold: float = 0.85,
                 decay_days: int = 90):
        self.cache_dir = Path(cache_dir)
        self.similarity_threshold = similarity_threshold
        self.decay_days = decay_days
    
    def score_fragment(self, fragment: Dict[str, Any], registry: Dict[str, Any]) -> FragmentQuality:
        """Score a single fragment for quality"""
        fragment_id = fragment.get('id', 'unknown')
        content = json.dumps(fragment.get('content', {}), sort_keys=True)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Access metrics
        access_count = registry.get(fragment_id, {}).get('access_count', 0)
        last_accessed_str = registry.get(fragment_id, {}).get('last_accessed', datetime.now().isoformat())
        
        try:
            last_accessed = datetime.fromisoformat(last_accessed_str)
        except Exception as e:
            last_accessed = datetime.now()
        
        age_days = (datetime.now() - last_accessed).days
        
        # Decay score (lower = more likely to decay)
        # Combines age and access frequency
        if access_count > 0:
            # Frequently accessed fragments resist decay
            access_factor = min(access_count / 10.0, 1.0)
            age_factor = 1.0 - min(age_days / self.decay_days, 1.0)
            decay_score = (access_factor * 0.7 + age_factor * 0.3)
        else:
            # Never accessed = high decay
            decay_score = max(0.1, 1.0 - age_days / self.decay_days)
        
        return FragmentQuality(
            fragment_id=fragment_id,
            content_hash=content_hash,
            similarity_score=0.0,  # Will be calculated by dedup
            access_count=access_count,
            last_accessed=last_accessed_str,
            age_days=age_days,
            decay_score=decay_score,
            dedup_candidates=[]
        )
    
    def find_duplicates(self, fragments: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Find duplicate fragments based on content hash
        
        Returns:
            Dict mapping fragment_id -> list of duplicate fragment_ids
        """
        # Group by content hash
        hash_to_ids = defaultdict(list)
        
        for fragment in fragments:
            content = json.dumps(fragment.get('content', {}), sort_keys=True)
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            fragment_id = fragment.get('id', 'unknown')
            hash_to_ids[content_hash].append(fragment_id)
        
        # Find duplicates
        duplicates = {}
        for content_hash, fragment_ids in hash_to_ids.items():
            if len(fragment_ids) > 1:
                # Keep oldest, mark others as duplicates
                for fid in fragment_ids:
                    duplicates[fid] = [f for f in fragment_ids if f != fid]
        
        return duplicates
    
    def recommend_removals(self, 
                          quality_scores: List[FragmentQuality],
                          max_remove: int = 100) -> List[str]:
        """
        Recommend fragments for removal based on quality scores
        
        Criteria:
        - Duplicates (keep highest access count)
        - Low decay score (old + rarely accessed)
        - Never accessed + old (>90 days)
        """
        removals = []
        
        # Group duplicates
        dup_groups = defaultdict(list)
        for score in quality_scores:
            if score.dedup_candidates:
                key = tuple(sorted([score.fragment_id] + score.dedup_candidates))
                dup_groups[key].append(score)
        
        # For each dup group, keep best, remove others
        for group in dup_groups.values():
            if len(group) <= 1:
                continue
            
            # Sort by access count (desc), then age (asc)
            sorted_group = sorted(group, key=lambda s: (-s.access_count, s.age_days))
            
            # Keep first, remove rest
            for score in sorted_group[1:]:
                if score.fragment_id not in removals:
                    removals.append(score.fragment_id)
        
        # Add low-quality fragments (if not already marked for dup removal)
        decay_candidates = [
            s for s in quality_scores
            if s.decay_score < 0.3 and s.fragment_id not in removals
        ]
        
        # Sort by decay score (lowest first)
        decay_candidates.sort(key=lambda s: s.decay_score)
        
        for score in decay_candidates:
            if len(removals) >= max_remove:
                break
            removals.append(score.fragment_id)
        
        return removals[:max_remove]


class MemoryDeduplicator:
    """Deduplicates CARMA memory fragments"""
    
    def __init__(self, cache_dir: str = 'data_core/FractalCache'):
        self.cache_dir = Path(cache_dir)
        self.registry_file = self.cache_dir / 'registry.json'
    
    def deduplicate(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Run deduplication on fragment cache
        
        Args:
            dry_run: If True, only report what would be removed
        
        Returns:
            Deduplication results
        """
        if not self.registry_file.exists():
            return {'error': 'Registry file not found'}
        
        # Load registry
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        fragments = list(registry.values())
        
        # Initialize scorer
        scorer = MemoryQualityScorer()
        
        # Find duplicates
        duplicates = scorer.find_duplicates(fragments)
        
        # Score all fragments
        quality_scores = []
        for fragment in fragments:
            score = scorer.score_fragment(fragment, registry)
            
            # Add dedup candidates
            fid = fragment.get('id', 'unknown')
            if fid in duplicates:
                score.dedup_candidates = duplicates[fid]
            
            quality_scores.append(score)
        
        # Get removal recommendations
        removals = scorer.recommend_removals(quality_scores, max_remove=100)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_fragments': len(fragments),
            'duplicate_groups': len(duplicates),
            'total_duplicates': sum(len(dups) for dups in duplicates.values()),
            'recommended_removals': len(removals),
            'dry_run': dry_run,
            'removals': removals
        }
        
        # Execute removals if not dry run
        if not dry_run and removals:
            removed_count = 0
            for fid in removals:
                if fid in registry:
                    del registry[fid]
                    removed_count += 1
            
            # Save updated registry
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
            
            results['actually_removed'] = removed_count
        
        return results


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Quality Tools')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Dedup command
    dedup_parser = subparsers.add_parser('dedup', help='Deduplicate fragments')
    dedup_parser.add_argument('--execute', action='store_true', help='Execute removal (default: dry-run)')
    dedup_parser.add_argument('--max-remove', type=int, default=100, help='Max fragments to remove')
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Show quality scores')
    score_parser.add_argument('--top', type=int, default=10, help='Show top N fragments')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'dedup':
        deduplicator = MemoryDeduplicator()
        results = deduplicator.deduplicate(dry_run=not args.execute)
        
        print("="*70)
        print("MEMORY DEDUPLICATION")
        print("="*70)
        print(f"Total fragments: {results['total_fragments']}")
        print(f"Duplicate groups: {results['duplicate_groups']}")
        print(f"Total duplicates: {results['total_duplicates']}")
        print(f"Recommended removals: {results['recommended_removals']}")
        
        if results['dry_run']:
            print("\nDRY RUN - No changes made")
            print("Run with --execute to perform deduplication")
        else:
            print(f"\nRemoved {results.get('actually_removed', 0)} fragments")
        
        print("="*70)


if __name__ == "__main__":
    main()

