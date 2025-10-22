#!/usr/bin/env python3
"""
CARMA Executive Brain
Autonomous goal generation and execution system
"""

from __future__ import annotations
import sys
from pathlib import Path
import time
import random
import uuid
from typing import Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))
from support_core.support_core import SystemConfig

if TYPE_CHECKING:
    from .fractal_cache import FractalMyceliumCache


class CARMAExecutiveBrain:
    """Executive brain for autonomous goal generation and execution."""
    
    def __init__(self, cache: FractalMyceliumCache, goal_interval: int = SystemConfig.GOAL_INTERVAL):
        self.cache = cache
        self.goal_interval = goal_interval
        self.goals = []
        self.completed_goals = []
        self.system_metrics_history = []
        self.optimization_actions_count = 0
        self.completed_goals_count = 0
        
        # Goal templates
        self.goal_templates = [
            {"type": "cross_link", "description": "Create semantic cross-links between related fragments"},
            {"type": "evict", "description": "Evict low-value fragments to maintain cache health"},
            {"type": "reinforce", "description": "Reinforce frequently accessed fragments"},
            {"type": "super_fragment", "description": "Create super-fragments from related clusters"},
            {"type": "reflection_scan", "description": "Perform reflection scan for system optimization"},
            {"type": "paradox_probe", "description": "Probe for paradoxes and contradictions"},
            {"type": "deepen_hierarchy", "description": "Deepen memory hierarchy structure"}
        ]
        
        print(" CARMA Executive Brain Initialized")
        print(f"   Goal interval: {goal_interval}s")
        print(f"   Goal templates: {len(self.goal_templates)}")
    
    def generate_goals(self, metrics: Dict) -> List[Dict]:
        """Generate autonomous goals based on system metrics."""
        goals = []
        
        for template in self.goal_templates:
            if self._should_generate_goal(template["type"]):
                goal = {
                    "id": f"goal_{int(time.time())}_{random.randint(1000, 9999)}",
                    "type": template["type"],
                    "description": template["description"],
                    "created_at": time.time(),
                    "status": "pending",
                    "priority": random.uniform(0.5, 1.0)
                }
                goals.append(goal)
        
        return goals
    
    def _should_generate_goal(self, goal_type: str) -> bool:
        """Determine if a goal should be generated."""
        # Use goal_type to determine probability
        goal_probabilities = {
            'cross_link': 0.3,
            'evict': 0.2,
            'reinforce': 0.4,
            'super_fragment': 0.1
        }
        return random.random() < goal_probabilities.get(goal_type, 0.3)
    
    def execute_goals(self):
        """Execute pending goals."""
        for goal in self.goals[:]:
            if goal["status"] == "pending":
                success = self._execute_goal(goal)
                if success:
                    goal["status"] = "completed"
                    goal["completed_at"] = time.time()
                    self.completed_goals.append(goal)
                    self.completed_goals_count += 1
                else:
                    goal["status"] = "failed"
    
    def _execute_goal(self, goal: Dict) -> bool:
        """Execute a specific goal."""
        goal_type = goal["type"]
        
        if goal_type == "cross_link":
            return self._execute_cross_link_goal(goal)
        elif goal_type == "evict":
            return self._execute_evict_goal(goal)
        elif goal_type == "reinforce":
            return self._execute_reinforce_goal(goal)
        elif goal_type == "super_fragment":
            return self._execute_super_fragment_goal(goal)
        else:
            print(f"Unknown goal type: {goal_type}")
            return False
    
    def _execute_cross_link_goal(self, goal: Dict) -> bool:
        """Execute cross-linking goal."""
        try:
            fragments = list(self.cache.file_registry.items())
            if len(fragments) < 2:
                return False
            
            frag1_id, frag1_data = random.choice(fragments)
            frag2_id, frag2_data = random.choice(fragments)
            
            if frag1_id != frag2_id:
                if frag1_id not in self.cache.semantic_links:
                    self.cache.semantic_links[frag1_id] = []
                if frag2_id not in self.cache.semantic_links:
                    self.cache.semantic_links[frag2_id] = []
                
                if frag2_id not in self.cache.semantic_links[frag1_id]:
                    self.cache.semantic_links[frag1_id].append(frag2_id)
                if frag1_id not in self.cache.semantic_links[frag2_id]:
                    self.cache.semantic_links[frag2_id].append(frag1_id)
                
                # Log the cross-link creation using the variables
                print(f"Created cross-link between {frag1_id} and {frag2_id}")
                return True
        except Exception as e:
            print(f"Error executing cross-link goal: {e}")
        return False
    
    def _execute_evict_goal(self, goal: Dict) -> bool:
        """Execute eviction goal."""
        try:
            fragments = [(fid, data) for fid, data in self.cache.file_registry.items()]
            if not fragments:
                return False
            
            fragments.sort(key=lambda x: x[1].get('hits', 0))
            
            frag_id, frag_data = fragments[0]
            if frag_data.get('hits', 0) < 2:
                del self.cache.file_registry[frag_id]
                print(f"Evicted fragment {frag_id} with {frag_data.get('hits', 0)} hits")
                return True
        except Exception as e:
            print(f"Error executing evict goal: {e}")
        return False
    
    def _execute_reinforce_goal(self, goal: Dict) -> bool:
        """Execute reinforcement goal."""
        try:
            fragments = [(fid, data) for fid, data in self.cache.file_registry.items()]
            if not fragments:
                return False
            
            fragments.sort(key=lambda x: x[1].get('hits', 0), reverse=True)
            
            frag_id, frag_data = fragments[0]
            if 'hits' in frag_data:
                frag_data['hits'] += 1
            else:
                frag_data['hits'] = 1
            
            print(f"Reinforced fragment {frag_id} - hits now: {frag_data['hits']}")
            return True
        except Exception as e:
            print(f"Error executing reinforce goal: {e}")
        return False
    
    def _execute_super_fragment_goal(self, goal: Dict) -> bool:
        """Execute super-fragment creation goal."""
        try:
            clusters = self._identify_fragment_clusters()
            if not clusters:
                return False
            
            largest_cluster = max(clusters, key=len)
            if len(largest_cluster) >= 3:
                super_id = self._create_super_fragment(largest_cluster)
                if super_id:
                    print(f"Created super-fragment {super_id} from cluster of {len(largest_cluster)} fragments")
                return super_id is not None
        except Exception as e:
            print(f"Error executing super-fragment goal: {e}")
        return False
    
    def _identify_fragment_clusters(self) -> List[List[str]]:
        """Identify clusters of related fragments."""
        clusters = []
        processed = set()
        
        for frag_id, frag_data in self.cache.file_registry.items():
            if frag_id in processed:
                continue
            
            cluster = [frag_id]
            processed.add(frag_id)
            
            for other_id, other_data in self.cache.file_registry.items():
                if other_id in processed:
                    continue
                
                if self._are_fragments_related(frag_data, other_data):
                    cluster.append(other_id)
                    processed.add(other_id)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return clusters
    
    def _are_fragments_related(self, frag1: Dict, frag2: Dict) -> bool:
        """Check if two fragments are related."""
        content1 = frag1.get('content', '').lower()
        content2 = frag2.get('content', '').lower()
        
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total > 0.3
    
    def _create_super_fragment(self, cluster: List[str]) -> Optional[str]:
        """Create a super-fragment from a cluster."""
        try:
            combined_content = []
            for frag_id in cluster:
                frag_data = self.cache.file_registry.get(frag_id, {})
                content = frag_data.get('content', '')
                if content:
                    combined_content.append(content)
            
            if not combined_content:
                return None
            
            super_content = "\n\n".join(combined_content)
            super_id = f"super_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            super_frag = {
                'file_id': super_id,
                'content': super_content,
                'parent_id': None,
                'level': 1,
                'hits': 0,
                'created': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'specialization': 'meta_memory',
                'tags': ['super_fragment'],
                'children': cluster,
                'analysis': self.cache.analyze_content(super_content)
            }
            
            try:
                embedding = self.cache.embedder.embed(super_content)
                super_frag['embedding'] = embedding
            except Exception:
                super_frag['embedding'] = None
            
            self.cache.file_registry[super_id] = super_frag
            return super_id
            
        except Exception:
            return None
    
    def get_executive_status(self) -> Dict:
        """Get executive brain status."""
        return {
            'active_goals': len([g for g in self.goals if g['status'] == 'pending']),
            'completed_goals_count': self.completed_goals_count,
            'optimization_actions_count': self.optimization_actions_count,
            'system_metrics_history_count': len(self.system_metrics_history)
        }

