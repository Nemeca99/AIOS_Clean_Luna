#!/usr/bin/env python3
"""
CARMA Memory Clusterer
Memory clustering system for organizing fragments
"""

import numpy as np
from typing import Dict, List


class CARMAMemoryClusterer:
    """Memory clustering system for organizing CARMA fragments."""
    
    def __init__(self):
        self.clusters = {}
        self.cluster_centers = {}
        self.cluster_metadata = {}
    
    def cluster_memories(self, fragments: List[Dict], num_clusters: int = 5) -> Dict:
        """Cluster memory fragments into groups."""
        if len(fragments) < 2:
            return {'clusters': {0: fragments}, 'metadata': {}}
        
        # Extract features for clustering
        features = self._extract_features(fragments)
        
        # Simple k-means clustering (simplified)
        clusters = self._kmeans_clustering(features, num_clusters)
        
        # Organize fragments by cluster
        cluster_groups = defaultdict(list)
        for i, cluster_id in enumerate(clusters):
            cluster_groups[cluster_id].append(fragments[i])
        
        # Calculate cluster metadata
        metadata = self._calculate_cluster_metadata(cluster_groups)
        
        self.clusters = dict(cluster_groups)
        self.cluster_metadata = metadata
        
        return {
            'clusters': dict(cluster_groups),
            'metadata': metadata,
            'num_clusters': len(cluster_groups)
        }
    
    def _extract_features(self, fragments: List[Dict]) -> List[List[float]]:
        """Extract numerical features from fragments."""
        features = []
        for fragment in fragments:
            content = fragment.get('content', '')
            feature_vector = [
                len(content),  # Length
                content.count('.'),  # Sentence count
                content.count(' '),  # Word count
                len(set(content.lower().split())),  # Unique words
                fragment.get('timestamp', 0) % 86400,  # Time of day
            ]
            features.append(feature_vector)
        return features
    
    def _kmeans_clustering(self, features: List[List[float]], k: int) -> List[int]:
        """Simple k-means clustering implementation."""
        if len(features) <= k:
            return list(range(len(features)))
        
        # Initialize centroids randomly
        centroids = random.sample(features, k)
        clusters = [0] * len(features)
        
        # Iterate until convergence
        for _ in range(10):  # Max 10 iterations
            # Assign points to nearest centroid
            for i, point in enumerate(features):
                distances = [self._euclidean_distance(point, centroid) for centroid in centroids]
                clusters[i] = distances.index(min(distances))
            
            # Update centroids
            new_centroids = []
            for cluster_id in range(k):
                cluster_points = [features[i] for i, c in enumerate(clusters) if c == cluster_id]
                if cluster_points:
                    centroid = [sum(coord) / len(cluster_points) for coord in zip(*cluster_points)]
                    new_centroids.append(centroid)
                else:
                    new_centroids.append(centroids[cluster_id])
            
            if new_centroids == centroids:
                break
            centroids = new_centroids
        
        return clusters
    
    def _euclidean_distance(self, point1: List[float], point2: List[float]) -> float:
        """Calculate Euclidean distance between two points."""
        return sum((a - b) ** 2 for a, b in zip(point1, point2)) ** 0.5
    
    def _calculate_cluster_metadata(self, cluster_groups: Dict) -> Dict:
        """Calculate metadata for each cluster."""
        metadata = {}
        for cluster_id, fragments in cluster_groups.items():
            if not fragments:
                continue
            
            contents = [f.get('content', '') for f in fragments]
            timestamps = [f.get('timestamp', 0) for f in fragments]
            
            metadata[cluster_id] = {
                'size': len(fragments),
                'avg_length': sum(len(c) for c in contents) / len(contents),
                'time_span': max(timestamps) - min(timestamps) if timestamps else 0,
                'common_words': self._find_common_words(contents),
                'themes': self._identify_themes(contents)
            }
        
        return metadata
    
    def _find_common_words(self, contents: List[str]) -> List[str]:
        """Find common words across cluster contents."""
        word_counts = defaultdict(int)
        for content in contents:
            words = content.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_counts[word] += 1
        
        # Return top 5 most common words
        return [word for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    def _identify_themes(self, contents: List[str]) -> List[str]:
        """Identify themes in cluster contents (simplified)."""
        # Simple theme detection based on keywords
        theme_keywords = {
            'technology': ['computer', 'software', 'ai', 'algorithm', 'data', 'system'],
            'science': ['research', 'study', 'experiment', 'hypothesis', 'theory'],
            'personal': ['feel', 'think', 'believe', 'experience', 'emotion'],
            'learning': ['learn', 'understand', 'knowledge', 'education', 'study']
        }
        
        all_text = ' '.join(contents).lower()
        themes = []
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)
        
        return themes
