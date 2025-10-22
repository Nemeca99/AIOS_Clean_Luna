#!/usr/bin/env python3
"""
Lessons Module
Handles lesson retrieval and management from ArbiterCache
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


def get_relevant_lessons(arbiter_cache_dir: Path, current_prompt: str, 
                         max_lessons: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve relevant lessons from ArbiterCache for the current prompt.
    
    This is the Data Core's interface for lesson retrieval - it delegates to
    the Arbiter system's mycelium retriever for the actual matching logic.
    
    Args:
        arbiter_cache_dir: Path to ArbiterCache directory
        current_prompt: The user's current question/prompt
        max_lessons: Maximum number of lessons to return
        
    Returns:
        List of relevant lesson dictionaries with fields:
        - original_prompt
        - suboptimal_response  
        - gold_standard
        - utility_score
        - karma_delta
        - context_tags
        - timestamp
    """
    lessons_file = arbiter_cache_dir / "lessons.json"
    
    if not lessons_file.exists():
        return []
    
    try:
        # Load all lessons
        with open(lessons_file, 'r', encoding='utf-8') as f:
            all_lessons = json.load(f)
        
        if not all_lessons:
            return []
        
        # Score lessons by relevance
        current_prompt_lower = current_prompt.lower()
        scored_lessons = []
        
        for lesson in all_lessons:
            score = 0.0
            
            # Check for exact prompt match (highest priority)
            if lesson.get('original_prompt', '').lower() == current_prompt_lower:
                score += 100.0
            
            # Check tag matches
            tags = lesson.get('context_tags', [])
            for tag in tags:
                tag_lower = tag.lower()
                # Check if tag appears in prompt
                if tag_lower in current_prompt_lower:
                    score += 10.0
                # Check if any prompt word appears in tag
                for word in current_prompt_lower.split():
                    if len(word) > 3 and word in tag_lower:
                        score += 5.0
            
            # Check for word overlap between prompts
            lesson_prompt = lesson.get('original_prompt', '').lower()
            current_words = set(current_prompt_lower.split())
            lesson_words = set(lesson_prompt.split())
            word_overlap = len(current_words.intersection(lesson_words))
            if word_overlap > 0:
                score += word_overlap * 2.0
            
            if score > 0:
                scored_lessons.append({
                    'lesson': lesson,
                    'score': score
                })
        
        # Sort by score and return top matches
        scored_lessons.sort(key=lambda x: x['score'], reverse=True)
        top_lessons = [item['lesson'] for item in scored_lessons[:max_lessons]]
        
        return top_lessons
        
    except Exception as e:
        print(f"⚠️ Error retrieving lessons from Data Core: {e}")
        return []

