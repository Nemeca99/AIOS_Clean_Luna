#!/usr/bin/env python3
"""
Enhanced Lesson Retrieval for Mycelium Architecture
Phase 2: Implement distributed learning with lessons.json as primary source
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

@dataclass
class EnhancedLesson:
    """Enhanced lesson with fragment tracking"""
    original_prompt: str
    suboptimal_response: str
    gold_standard: str
    utility_score: float
    karma_delta: float
    timestamp: float
    context_tags: List[str]
    context_files_used: List[str]  # NEW: Track which fragments contributed
    lesson_id: str  # NEW: Unique identifier for this lesson

@dataclass
class FragmentContribution:
    """Track how a fragment contributed to a lesson"""
    fragment_id: str
    contribution_score: float
    contribution_type: str  # 'semantic_match', 'context_enhancement', 'example_source'
    timestamp: float

class MyceliumLessonRetriever:
    """
    Enhanced lesson retrieval system implementing distributed learning architecture.
    
    Flow:
    1. Check lessons.json FIRST for exact/semantic matches
    2. If no lessons found, search FractalCache fragments
    3. Track fragment contributions to lessons
    4. Maintain bidirectional lesson-fragment relationships
    """
    
    def __init__(self, lessons_path: str, fragments_dir: str):
        self.lessons_path = Path(lessons_path)
        self.fragments_dir = Path(fragments_dir)
        self.lessons_cache: Dict[str, EnhancedLesson] = {}
        self.fragment_contributions: Dict[str, List[FragmentContribution]] = {}
        
        # Load lessons into memory
        self._load_lessons()
        
    def _load_lessons(self):
        """Load lessons from lessons.json into memory"""
        if not self.lessons_path.exists():
            print(f"Lessons file not found: {self.lessons_path}")
            return
            
        try:
            with open(self.lessons_path, 'r', encoding='utf-8') as f:
                lessons_data = json.load(f)
            
            for i, lesson_data in enumerate(lessons_data):
                lesson_id = f"lesson_{i:06d}"
                
                enhanced_lesson = EnhancedLesson(
                    original_prompt=lesson_data["original_prompt"],
                    suboptimal_response=lesson_data["suboptimal_response"],
                    gold_standard=lesson_data["gold_standard"],
                    utility_score=lesson_data["utility_score"],
                    karma_delta=lesson_data["karma_delta"],
                    timestamp=lesson_data["timestamp"],
                    context_tags=lesson_data["context_tags"],
                    context_files_used=lesson_data.get("context_files_used", []),
                    lesson_id=lesson_id
                )
                
                self.lessons_cache[lesson_id] = enhanced_lesson
                
            print(f"Loaded {len(self.lessons_cache)} lessons into mycelium cache")
            
        except Exception as e:
            print(f"Error loading lessons: {e}")
    
    def retrieve_relevant_lesson(self, current_prompt: str) -> Optional[EnhancedLesson]:
        """
        Retrieve the most relevant lesson using mycelium architecture.
        
        Priority:
        1. Exact prompt matches in lessons.json
        2. Semantic matches in lessons.json  
        3. Context tag overlaps in lessons.json
        4. Fall back to FractalCache fragments if no lessons found
        """
        print(f"🔍 MyceliumRetriever.retrieve_relevant_lesson called for: '{current_prompt[:50]}...'")
        current_tags = self._extract_context_tags(current_prompt)
        
        # Phase 1: Check lessons.json FIRST
        lesson_match = self._find_lesson_match(current_prompt, current_tags)
        if lesson_match:
            # Track which fragments contributed to this lesson
            self._track_lesson_usage(lesson_match, current_prompt)
            return lesson_match
        
        # Phase 2: No lesson found, search fragments
        print(f"No lesson found for prompt: '{current_prompt[:50]}...'")
        fragment_match = self._search_fragments(current_prompt, current_tags)
        
        if fragment_match:
            # Create a new lesson from fragment knowledge
            new_lesson = self._create_lesson_from_fragment(fragment_match, current_prompt, current_tags)
            return new_lesson
            
        return None
    
    def _find_lesson_match(self, prompt: str, tags: List[str]) -> Optional[EnhancedLesson]:
        """Find best matching lesson in lessons.json"""
        best_match = None
        best_score = 0.0
        
        for lesson in self.lessons_cache.values():
            score = self._calculate_lesson_relevance(lesson, prompt, tags)
            if score > best_score:
                best_score = score
                best_match = lesson
        
        # Only return if we have a good match (threshold: 0.3)
        if best_score >= 0.3:
            print(f"Found lesson match: {best_match.lesson_id} (score: {best_score:.3f})")
            return best_match
            
        return None
    
    def _calculate_lesson_relevance(self, lesson: EnhancedLesson, prompt: str, tags: List[str]) -> float:
        """Calculate relevance score between prompt and lesson"""
        score = 0.0
        
        # Exact prompt match (highest priority)
        if lesson.original_prompt.lower().strip() == prompt.lower().strip():
            score += 1.0
        
        # Semantic similarity (simplified - could use embeddings)
        prompt_words = set(prompt.lower().split())
        lesson_words = set(lesson.original_prompt.lower().split())
        word_overlap = len(prompt_words.intersection(lesson_words))
        if len(prompt_words) > 0:
            semantic_score = word_overlap / len(prompt_words)
            score += semantic_score * 0.6
        
        # Context tag overlap
        tag_overlap = len(set(tags).intersection(set(lesson.context_tags)))
        if len(lesson.context_tags) > 0:
            tag_score = tag_overlap / len(lesson.context_tags)
            score += tag_score * 0.4
        
        return score
    
    def _search_fragments(self, prompt: str, tags: List[str]) -> Optional[Dict]:
        """
        Search FractalCache fragments for relevant knowledge using semantic similarity
        Phase 4: Embedding-based fallback when no lessons match
        """
        import numpy as np
        
        print(f"🔍 Phase 4: Searching fragments semantically for: '{prompt[:50]}...'")
        
        # Get all fragments
        fragments = []
        if self.fractal_cache_dir.exists():
            for frag_file in self.fractal_cache_dir.glob("*.json"):
                try:
                    with open(frag_file, 'r', encoding='utf-8') as f:
                        frag_data = json.load(f)
                        frag_data['file_id'] = frag_file.stem
                        fragments.append(frag_data)
                except Exception as e:
                    continue
        
        if not fragments:
            print(f"❌ No fragments found in {self.fractal_cache_dir}")
            return None
        
        # Calculate semantic similarity using simple word overlap
        # (In production, you'd use proper embeddings here)
        best_fragment = None
        best_score = 0.0
        
        prompt_words = set(prompt.lower().split())
        
        for fragment in fragments:
            # Get fragment content
            content = fragment.get('content', '') or fragment.get('text', '')
            if not content:
                continue
            
            # Calculate word overlap similarity
            frag_words = set(str(content).lower().split())
            overlap = len(prompt_words.intersection(frag_words))
            
            # Normalize by prompt length
            if len(prompt_words) > 0:
                similarity = overlap / len(prompt_words)
                
                # Bonus for tag matches
                frag_tags = fragment.get('tags', []) or fragment.get('context_tags', [])
                tag_overlap = len(set(tags).intersection(set(frag_tags)))
                if tag_overlap > 0:
                    similarity += tag_overlap * 0.1
                
                if similarity > best_score:
                    best_score = similarity
                    best_fragment = fragment
        
        # Return if we found a good match (threshold: 0.2)
        if best_score >= 0.2 and best_fragment:
            print(f"✅ Found fragment match: {best_fragment.get('file_id', 'unknown')} (score: {best_score:.3f})")
            return best_fragment
        
        print(f"❌ No fragments matched above threshold (best: {best_score:.3f})")
        return None
    
    def _create_lesson_from_fragment(self, fragment: Dict, prompt: str, tags: List[str]) -> Optional[EnhancedLesson]:
        """
        Create a synthetic lesson from fragment knowledge
        This allows Luna to learn from fragments even when no exact lessons exist
        """
        import time
        
        # Extract fragment content as the "gold standard"
        content = fragment.get('content', '') or fragment.get('text', '')
        if not content:
            return None
        
        # Create a synthetic lesson
        # The fragment content becomes the gold standard
        # We don't have a suboptimal response, so we use a placeholder
        synthetic_lesson = EnhancedLesson(
            lesson_id=f"synthetic_from_{fragment.get('file_id', 'unknown')}",
            original_prompt=prompt,
            suboptimal_response="[No prior response - learning from fragment]",
            gold_standard=f"Based on relevant knowledge: {content[:500]}...",  # Truncate long fragments
            utility_score=0.5,  # Medium utility since it's synthetic
            karma_delta=0.0,  # Neutral karma
            timestamp=time.time(),
            context_tags=tags,
            context_files_used=[fragment.get('file_id', '')]
        )
        
        print(f"📚 Created synthetic lesson from fragment: {fragment.get('file_id', 'unknown')}")
        return synthetic_lesson
    
    def _track_lesson_usage(self, lesson: EnhancedLesson, prompt: str):
        """Track that this lesson was used for this prompt"""
        # Update fragment contribution tracking
        if not hasattr(self, 'lesson_usage_stats'):
            self.lesson_usage_stats = {}
        
        lesson_id = lesson.id if hasattr(lesson, 'id') else 'unknown'
        if lesson_id not in self.lesson_usage_stats:
            self.lesson_usage_stats[lesson_id] = {
                'times_used': 0,
                'prompts': [],
                'last_used': None
            }
        
        self.lesson_usage_stats[lesson_id]['times_used'] += 1
        self.lesson_usage_stats[lesson_id]['prompts'].append(prompt[:100])  # Store first 100 chars
        self.lesson_usage_stats[lesson_id]['last_used'] = datetime.now().isoformat()
    
    def _extract_context_tags(self, prompt: str) -> List[str]:
        """Extract context tags from prompt (simplified version)"""
        tags = []
        prompt_lower = prompt.lower()
        
        # Simple keyword-based tagging
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'greeting']):
            tags.append('greeting')
        if any(word in prompt_lower for word in ['pizza', 'food', 'eat', 'hungry']):
            tags.append('food')
        if any(word in prompt_lower for word in ['ai', 'machine learning', 'neural', 'algorithm']):
            tags.append('technical')
        if any(word in prompt_lower for word in ['feel', 'emotion', 'anxiety', 'depression']):
            tags.append('emotional')
        if any(word in prompt_lower for word in ['what', 'how', 'why', 'explain']):
            tags.append('question')
        
        return tags
    
    def update_lesson_with_fragment(self, lesson_id: str, fragment_id: str, contribution_score: float):
        """Update lesson to include fragment contribution (called by Arbiter)"""
        if lesson_id in self.lessons_cache:
            lesson = self.lessons_cache[lesson_id]
            if fragment_id not in lesson.context_files_used:
                lesson.context_files_used.append(fragment_id)
                
                # Track the contribution
                contribution = FragmentContribution(
                    fragment_id=fragment_id,
                    contribution_score=contribution_score,
                    contribution_type='context_enhancement',
                    timestamp=time.time()
                )
                
                if lesson_id not in self.fragment_contributions:
                    self.fragment_contributions[lesson_id] = []
                self.fragment_contributions[lesson_id].append(contribution)
    
    def save_enhanced_lessons(self):
        """Save enhanced lessons back to lessons.json"""
        lessons_data = []
        
        for lesson in self.lessons_cache.values():
            lesson_data = {
                "original_prompt": lesson.original_prompt,
                "suboptimal_response": lesson.suboptimal_response,
                "gold_standard": lesson.gold_standard,
                "utility_score": lesson.utility_score,
                "karma_delta": lesson.karma_delta,
                "timestamp": lesson.timestamp,
                "context_tags": lesson.context_tags,
                "context_files_used": lesson.context_files_used
            }
            lessons_data.append(lesson_data)
        
        try:
            with open(self.lessons_path, 'w', encoding='utf-8') as f:
                json.dump(lessons_data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(lessons_data)} enhanced lessons to {self.lessons_path}")
        except Exception as e:
            print(f"Error saving lessons: {e}")

# Integration function for existing Arbiter
def create_mycelium_retriever(arbiter_system) -> MyceliumLessonRetriever:
    """Create mycelium retriever integrated with existing Arbiter"""
    lessons_path = arbiter_system.cache_path / "lessons.json"
    fragments_dir = Path("data_core/FractalCache")
    
    return MyceliumLessonRetriever(str(lessons_path), str(fragments_dir))
