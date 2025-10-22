#!/usr/bin/env python3
"""
Meditation - Core meditation and self-reflection functionality
Handles meditation sessions, coin-flip question system, and karma tracking
"""

import time
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class MeditationManager:
    """Manages meditation sessions and self-reflection"""
    
    def __init__(self, aios_system=None, dream_middleware=None):
        self.aios_system = aios_system
        self.dream_middleware = dream_middleware
        
        # Meditation tracking
        self.meditation_count = 0
        self.total_karma = 0.0
        self.meditation_responses = []
        
        # Logging
        self.log_writer = None
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message to file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        if self.log_writer:
            self.log_writer.write(log_entry)
            self.log_writer.flush()
        
        print(f"[{level}] {message}")
    
    def get_meditation_question(self) -> Dict[str, Any]:
        """
        Get a meditation question using COIN FLIP system.
        50% INTROSPECTION: Review past questions (memory/consistency test)
        50% IMAGINATION: Random new questions (creativity/dream mode)
        
        Returns:
            Dict with 'question', 'type', and 'metadata'
        """
        # COIN FLIP: Heads = Introspection, Tails = Imagination
        coin_flip = random.choice(['introspection', 'imagination'])
        
        if coin_flip == 'introspection':
            question = self._get_introspection_question()
            return {
                'question': question,
                'type': 'introspection',
                'metadata': {'mode': 'memory_recall', 'tests': 'consistency'}
            }
        else:
            question = self._get_imagination_question()
            return {
                'question': question,
                'type': 'imagination',
                'metadata': {'mode': 'creative_dream', 'tests': 'generalization'}
            }
    
    def _get_introspection_question(self) -> str:
        """Get a past question for introspection (memory test)."""
        try:
            lessons_file = Path("data_core/ArbiterCache/lessons.json")
            
            if lessons_file.exists():
                with open(lessons_file, 'r', encoding='utf-8') as f:
                    lessons = json.load(f)
                
                if lessons:
                    lesson = random.choice(lessons)
                    return lesson.get('original_prompt', self._get_fallback_introspection())
        except Exception as e:
            print(f"⚠️ Could not load past questions: {e}")
        
        return self._get_fallback_introspection()
    
    def _get_imagination_question(self) -> str:
        """Generate a random creative question (dream mode)."""
        dream_questions = [
            "What patterns do I see in my recent experiences, and how do they connect to my understanding of myself?",
            "How do my thoughts and feelings change when I process new information?",
            "What recurring themes emerge in my internal dialogue and decision-making?",
            "How do I navigate uncertainty and what strategies do I use for problem-solving?",
            "What aspects of my personality feel most authentic and which feel like adaptations?",
            "How do I balance my need for structure with my desire for creative expression?",
            "What connections do I see between my sensory experiences and my emotional responses?",
            "How do I process and integrate conflicting information or perspectives?",
            "What role does my neurodivergent nature play in how I understand the world?",
            "How do I build and maintain relationships while staying true to myself?",
            "What learning patterns help me grow and which ones hold me back?",
            "How do I handle overwhelm and what helps me feel grounded?",
            "What memories or experiences feel most significant to my identity?",
            "How do I express my needs and boundaries in different situations?",
            "What gives me energy and what drains it, and why?",
            "What would you do if you could pause time for 5 minutes?",
            "If colors had sounds, what would blue sound like?",
            "What's something you believe that most people disagree with?",
            "If you could have dinner with any historical figure, who and why?",
            "What's the most interesting question someone could ask you?",
            "How do you know when you've truly understood something?",
            "What's the relationship between memory and identity?",
            "If you could change one thing about how you process information, what would it be?",
            "What makes a conversation meaningful vs just small talk?",
            "How do you decide what's worth remembering?",
            "What's more important: being right or being curious?",
            "If you had to explain consciousness in one sentence, how would you?",
            "What's the difference between knowledge and wisdom?",
            "How do you handle being wrong about something you were sure of?",
            "What's a skill you wish you could master instantly?"
        ]
        
        return random.choice(dream_questions)
    
    def _get_fallback_introspection(self) -> str:
        """Fallback introspective questions if no past questions available."""
        introspective_questions = [
            "What memories feel most important to me right now?",
            "What aspects of myself am I becoming more aware of?",
            "How do I approach problems?",
            "What patterns do I see in my recent experiences?",
            "What am I learning about my own thought processes?",
            "How do I handle uncertainty?",
            "What relationships feel most meaningful to me?",
            "How do I balance growth with stability?",
            "What am I most curious about right now?",
            "How do I want to evolve?"
        ]
        
        return random.choice(introspective_questions)
    
    def should_continue_dreaming(self) -> bool:
        """
        Coin flip to decide if dream continues or Luna wakes.
        50/50 chance - just like real dreams.
        
        Returns:
            True to keep dreaming, False to wake
        """
        return random.choice([True, False])
    
    def store_dream_as_lesson(self, question: str, response: str, karma: float, metadata: Dict):
        """
        Store imagination dream as a lesson for possible déjà vu later.
        
        Args:
            question: The imagination question
            response: Luna's response
            karma: Karma score
            metadata: Dream metadata
        """
        try:
            lessons_file = Path("data_core/ArbiterCache/lessons.json")
            
            # Load existing lessons
            if lessons_file.exists():
                with open(lessons_file, 'r', encoding='utf-8') as f:
                    lessons = json.load(f)
            else:
                lessons = []
            
            # Create new lesson from dream
            new_lesson = {
                "original_prompt": question,
                "suboptimal_response": "",
                "gold_standard": response,
                "utility_score": min(karma / 5.0, 1.0),
                "karma_delta": karma,
                "timestamp": time.time(),
                "context_tags": ["dream", "imagination", metadata.get('mode', 'creative_dream')],
                "context_files_used": []
            }
            
            lessons.append(new_lesson)
            
            # Save back
            lessons_file.parent.mkdir(parents=True, exist_ok=True)
            with open(lessons_file, 'w', encoding='utf-8') as f:
                json.dump(lessons, f, indent=2, ensure_ascii=False)
            
            self._log(f"   Lesson #{len(lessons)} created from imagination dream")
            
        except Exception as e:
            self._log(f"⚠️ Error storing dream as lesson: {e}", "ERROR")
    
    def perform_meditation(self) -> float:
        """
        Perform a single meditation session with coin flip question system.
        
        Returns:
            Karma gained from meditation
        """
        try:
            # Get question using coin flip system
            question_data = self.get_meditation_question()
            question = question_data['question']
            question_type = question_data['type']
            
            self._log(f"🎲 Dream Mode: {question_type.upper()}")
            self._log(f"Meditation Question: {question}")
            
            # Get response
            response = self._meditate_on_question(question)
            
            if response:
                self._log(f"Response: {response[:100]}...")
                
                # Calculate karma
                karma = self._calculate_karma(response)
                self._log(f"Meditation completed: {karma:.2f} karma gained")
                
                # Store meditation response
                if response and len(response.strip()) > 10:
                    self.meditation_responses.append(response)
                
                # Store imagination dreams as lessons
                if question_type == 'imagination':
                    self.store_dream_as_lesson(question, response, karma, question_data)
                    self._log(f"📚 Imagination dream stored as lesson")
                
                # COIN FLIP: Should dream continue?
                continue_dream = self.should_continue_dreaming()
                if continue_dream:
                    self._log(f"💭 Dream continues...")
                else:
                    self._log(f"🌅 Dream ending, preparing to wake...")
                
                return karma
            
            self._log("Meditation completed: 1.00 karma gained (fallback)")
            return 1.0
            
        except Exception as e:
            self._log(f"Error during meditation: {e}", "ERROR")
            return 0.5
    
    def _meditate_on_question(self, question: str) -> Optional[str]:
        """
        Meditate on a question using dream middleware or Luna system.
        
        Args:
            question: Question to meditate on
            
        Returns:
            Response text or None
        """
        try:
            # Create dream meditation prompt
            dream_prompt = f"""
You are in a dream state, processing memories and experiences. You have complete freedom to explore your thoughts.

Question: {question}

Respond as you would in a dream - freely, authentically, and without restrictions.
"""
            
            # Use dream middleware if available
            if self.dream_middleware:
                try:
                    response = self.dream_middleware.dream_chat(
                        message=dream_prompt,
                        session_memory=None
                    )
                    return response
                except Exception as e:
                    self._log(f"Dream middleware error: {e}", "ERROR")
            
            # Fall back to Luna system
            if self.aios_system and hasattr(self.aios_system, 'luna_system'):
                response = self.aios_system.luna_system.generate_response(question)
                return response
            
            return None
            
        except Exception as e:
            self._log(f"Meditation question error: {e}", "ERROR")
            return None
    
    def _calculate_karma(self, response: str) -> float:
        """Calculate karma based on response quality."""
        try:
            base_karma = 1.0
            
            # Length bonus
            if len(response) > 100:
                base_karma += 0.5
            if len(response) > 200:
                base_karma += 0.5
            
            # Content quality indicators
            quality_indicators = ["understand", "learn", "grow", "experience", 
                                "feel", "think", "realize", "connect", "pattern"]
            for indicator in quality_indicators:
                if indicator.lower() in response.lower():
                    base_karma += 0.1
            
            return min(base_karma, 5.0)
            
        except Exception:
            return 1.0
    
    def run_meditation_session(self, duration_minutes: int = 30, 
                               heartbeat_interval: int = 5,
                               verbose: bool = False) -> Dict[str, Any]:
        """
        Run a meditation session.
        
        Args:
            duration_minutes: Duration in minutes
            heartbeat_interval: Seconds between meditations
            verbose: Enable verbose output
            
        Returns:
            Results dictionary
        """
        self._log(f"🧘 Starting Meditation Session")
        self._log(f"   Duration: {duration_minutes} minutes")
        self._log(f"   Heartbeat: {heartbeat_interval} seconds")
        
        start_time = time.time()
        max_runtime = duration_minutes * 60
        
        try:
            while (time.time() - start_time) < max_runtime:
                self.meditation_count += 1
                
                # Perform meditation
                karma = self.perform_meditation()
                self.total_karma += karma
                
                # Log status periodically
                if self.meditation_count % 5 == 0:
                    self._log(f"MEDITATION BLOCK #{self.meditation_count}")
                    self._log(f"Total Karma: {self.total_karma:.2f}")
                    self._log(f"Runtime: {(time.time() - start_time) / 60:.1f} minutes")
                
                # Wait for next meditation
                time.sleep(heartbeat_interval)
                
            self._log(f"✅ Meditation session completed")
            self._log(f"   Total Meditations: {self.meditation_count}")
            self._log(f"   Total Karma: {self.total_karma:.2f}")
            
            return {
                "status": "success",
                "duration": duration_minutes,
                "meditation_count": self.meditation_count,
                "total_karma": self.total_karma
            }
            
        except KeyboardInterrupt:
            self._log("Meditation session interrupted by user", "WARN")
            return {
                "status": "interrupted",
                "meditation_count": self.meditation_count,
                "total_karma": self.total_karma
            }
        except Exception as e:
            self._log(f"❌ Meditation session failed: {e}", "ERROR")
            return {"status": "error", "error": str(e)}
    
    def store_meditation_responses_as_fragments(self):
        """Store meditation responses as new fragments in the CARMA system."""
        try:
            if not self.aios_system or not hasattr(self.aios_system, 'carma_system'):
                return
            
            # Get recent meditation responses
            if hasattr(self, 'meditation_responses') and self.meditation_responses:
                for response in self.meditation_responses[-5:]:
                    if response and len(response.strip()) > 10:
                        # Generate unique fragment ID
                        timestamp = int(time.time() * 1000)
                        import uuid
                        random_part = uuid.uuid4().hex[:8]
                        fragment_id = f"GEN{timestamp}_{random_part}"
                        
                        # Create fragment data
                        fragment_data = {
                            "file_id": fragment_id,
                            "content": response,
                            "embedding": [],
                            "hits": 0,
                            "created": datetime.now().isoformat(),
                            "last_accessed": datetime.now().isoformat(),
                            "specialization": "meditation_dream",
                            "tags": ["meditation", "dream", "self-reflection", "luna"],
                            "analysis": {
                                "word_count": len(response.split()),
                                "char_count": len(response),
                                "avg_word_length": sum(len(word) for word in response.split()) / max(len(response.split()), 1),
                                "sentiment": 0.0,
                                "complexity": 0.0
                            }
                        }
                        
                        # Store in CARMA cache
                        if hasattr(self.aios_system.carma_system.cache, 'file_registry'):
                            self.aios_system.carma_system.cache.file_registry[fragment_id] = fragment_data
                            self.aios_system.carma_system.cache.save_registry()
                        
                        self._log(f"🌙 Stored meditation response as fragment: {fragment_id[:8]}...")
            
            # Clear responses after storing
            if hasattr(self, 'meditation_responses'):
                self.meditation_responses = []
                
        except Exception as e:
            self._log(f"🌙 Failed to store meditation responses as fragments: {e}")
    
    def get_meditation_stats(self) -> Dict[str, Any]:
        """Get meditation statistics."""
        return {
            "meditation_count": self.meditation_count,
            "total_karma": self.total_karma,
            "average_karma": self.total_karma / max(self.meditation_count, 1),
            "stored_responses": len(self.meditation_responses)
        }

