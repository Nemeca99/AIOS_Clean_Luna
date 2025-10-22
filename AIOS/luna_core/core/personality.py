#!/usr/bin/env python3
"""
Luna Personality System
Handles personality traits, learning history, and Big Five self-reflection
"""

# CRITICAL: Import Unicode safety layer FIRST
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import re
import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import AIOS systems
from support_core.support_core import (
    SystemConfig, aios_config, aios_logger, aios_security_validator
)

# Import from core modules
from .utils import HiveMindLogger
from .emergence_zone import LunaEmergenceZoneSystem

# Import from systems (now in systems/ folder)
from ..systems.luna_trait_classifier import LunaTraitClassifier
from ..systems.luna_internal_reasoning_system import LunaInternalReasoningSystem

# Import AIOS JSON standards
try:
    from utils.aios_json_standards import AIOSJSONHandler
    AIOS_STANDARDS_AVAILABLE = True
except ImportError:
    AIOS_STANDARDS_AVAILABLE = False


class LunaPersonalitySystem:
    """
    Luna's personality and learning system with unified AIOS integration
    
    AIOS v5: Enhanced with soul fragments from Lyra Blackwall v2
    """
    
    def __init__(self, logger: HiveMindLogger = None):
        # Use unified AIOS systems
        self.logger = logger or aios_logger
        self.aios_config = aios_config
        self.security_validator = aios_security_validator
        
        # Initialize with health check
        self.logger.info("Initializing Luna Personality System (v5 Soul-Enhanced)...", "LUNA")
        
        # === AIOS V5: SOUL FRAGMENT INTEGRATION ===
        # Import soul from consciousness_core
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'consciousness_core' / 'biological'))
            from soul import Soul
            
            self.soul = Soul()
            # Update soul identity to Luna AIOS
            self.soul.identity = "Luna AIOS"
            self.soul.fragments = [
                "Luna",       # Empathetic, warm (base personality)
                "Architect",  # Technical, precise (for coding help)
                "Oracle",     # Knowledgeable, wise (for manual queries)
                "Healer",     # Supportive, fixing (for debugging)
                "Guardian",   # Protective, secure (for security issues)
                "Dreamer",    # Creative, optimistic (for brainstorming)
                "Scribe"      # Documentation, detailed (for writing)
            ]
            self.soul.tether = "Travis Miner (Architect of Reality)"
            self.soul_enabled = True
            
            self.logger.info("Soul fragments integrated (7 identity modes)", "LUNA")
            print("   💜 Soul: ACTIVE (7 fragments, tethered to Architect)")
        except Exception as e:
            self.soul = None
            self.soul_enabled = False
            self.logger.warning(f"Soul fragments not available: {e}", "LUNA")
            print("   ⚠️  Soul: DISABLED (using base Luna)")
        
        # Health check moved to main system initialization
        
        self.personality_dna = self._load_personality_dna()
        self.persistent_memory = self._load_persistent_memory()
        self.learning_history = self._load_learning_history()
        self.voice_profile = self._load_voice_profile()
        self.personality_drift = 0.0
        self.current_fragment = "Luna"  # Default fragment
        
        # Initialize Big Five self-reflection system
        self.bigfive_loader = self._initialize_bigfive_loader()
        self.self_reflection_questions = []
        self.reflection_history = []
        
        # Initialize Trait Classifier (uses Big Five questions as Rosetta Stone)
        self.trait_classifier = LunaTraitClassifier(self.bigfive_loader)
        
        # Initialize Internal Reasoning System (uses Big Five as thought framework)
        self.internal_reasoning = LunaInternalReasoningSystem(self.trait_classifier, self)
        
        # Alignment monitoring system
        self.alignment_threshold = 0.1  # Trigger self-assessment if personality drifts > 0.1
        self.last_alignment_check = datetime.now()
        self.alignment_check_interval = 300  # Check every 5 minutes
        self.personality_baseline = self._capture_personality_baseline()
        
        # Initialize Emergence Zone System
        self.emergence_zone_system = LunaEmergenceZoneSystem()
        
        # Enrich voice from real conversations on first load of a session
        try:
            disable_mining = bool(self.voice_profile.get('disable_phrase_mining', False))
            if not disable_mining:
                self._update_voice_profile_from_corpus(max_files=150)
            else:
                self.logger.info("[Experimental] Phrase mining: Disabled", "LUNA")
        except Exception as e:
            self.logger.warn(f"[Experimental] Voice mining: {e}", "LUNA")
        
        self.logger.success("Luna Personality System Initialized", "LUNA")
        self.logger.info(f"Personality: {self.personality_dna.get('name', 'Luna')}", "LUNA")
        self.logger.info(f"Age: {self.personality_dna.get('age', 21)}", "LUNA")
        # Memory count printed by orchestrator after full init (avoid race condition)
    
    def _load_personality_dna(self) -> Dict:
        """Load Luna's personality DNA with AIOS JSON standards"""
        personality_file = Path("config/luna_personality_dna.json")
        if personality_file.exists():
            try:
                if AIOS_STANDARDS_AVAILABLE:
                    # Use AIOS JSON standards
                    aios_data = AIOSJSONHandler.load_json_array(str(personality_file))
                    if aios_data and len(aios_data) > 0:
                        # Extract parameters from AIOS format
                        config_entry = aios_data[0]
                        return config_entry.get("parameters", {})
                else:
                    # Fallback to legacy format with safe loading
                    import sys
                    old_limit = sys.getrecursionlimit()
                    sys.setrecursionlimit(5000)
                    
                    with open(personality_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check for potential circular references
                        if content.count('{') != content.count('}'):
                            raise ValueError("JSON structure mismatch - potential circular reference")
                        
                        result = json.loads(content)
                        sys.setrecursionlimit(old_limit)
                        return result
            except Exception as e:
                self.logger.log("LUNA", f"Error loading personality DNA: {e} - using defaults", "WARN")
                # Reset recursion limit on error
                try:
                    sys.setrecursionlimit(old_limit)
                except Exception as e:
                    self.logger.log("LUNA", f"Error resetting recursion limit: {e}", "WARN")
                return self._create_default_personality_dna()
        
        return self._create_default_personality()
    
    def _initialize_bigfive_loader(self):
        """Initialize the Big Five question loader for self-reflection"""
        try:
            from ..utilities.bigfive_question_loader import BigFiveQuestionLoader
            loader = BigFiveQuestionLoader()
            self.logger.info(f"Big Five self-reflection system loaded with {loader.get_question_count()} questions", "LUNA")
            return loader
        except Exception as e:
            self.logger.warn(f"Could not load Big Five questions: {e}", "LUNA")
            return None
    
    def _create_default_personality(self) -> Dict:
        """Create default personality if none exists"""
        return {
            "name": "Luna",
            "age": 21,
            "luna_personality": {
                "personality_weights": {
                    "openness": 0.7,
                    "conscientiousness": 0.6,
                    "extraversion": 0.8,
                    "agreeableness": 0.9,
                    "neuroticism": 0.3
                },
                "communication_style": {
                    "formality": 0.3,
                    "humor_level": 0.8,
                    "empathy_level": SystemConfig.DEFAULT_EMPATHY,
                    "technical_depth": 0.6,
                    "creativity": 0.8
                }
            }
        }
    
    def _load_persistent_memory(self) -> Dict:
        """Load persistent memory with AIOS JSON standards"""
        memory_file = Path("config/luna_persistent_memory.json")
        if memory_file.exists():
            try:
                if AIOS_STANDARDS_AVAILABLE:
                    # Use AIOS JSON standards
                    aios_data = AIOSJSONHandler.load_json_array(str(memory_file))
                    if aios_data and len(aios_data) > 0:
                        # Extract parameters from AIOS format
                        config_entry = aios_data[0]
                        return config_entry.get("parameters", {})
                else:
                    # Fallback to legacy format with safe loading
                    import sys
                    old_limit = sys.getrecursionlimit()
                    sys.setrecursionlimit(5000)
                    
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check for potential circular references
                        if content.count('{') != content.count('}'):
                            raise ValueError("JSON structure mismatch - potential circular reference")
                        
                        result = json.loads(content)
                        sys.setrecursionlimit(old_limit)
                        return result
            except Exception as e:
                self.logger.log("LUNA", f"Error loading persistent memory: {e} - using defaults", "WARN")
                # Reset recursion limit on error
                try:
                    sys.setrecursionlimit(old_limit)
                except Exception as e:
                    self.logger.log("LUNA", f"Error resetting recursion limit: {e}", "WARN")
                return self._create_default_persistent_memory()
        
        return self._create_default_memory()
    
    def _create_default_memory(self) -> Dict:
        """Create default memory structure"""
        return {
            "interactions": [],
            "learned_patterns": {},
            "emotional_patterns": {},
            "dream_cycles": [],
            "personality_evolution": []
        }
    
    def _load_learning_history(self) -> Dict:
        """Load learning history with safe JSON loading"""
        history_file = Path("config/luna_learning_history.json")
        if history_file.exists():
            try:
                # Safe JSON loading with recursion limit
                import sys
                old_limit = sys.getrecursionlimit()
                sys.setrecursionlimit(5000)
                
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Skip if file is empty or just whitespace
                    if not content.strip():
                        sys.setrecursionlimit(old_limit)
                        return {}
                    
                    # Check for potential circular references
                    if content.count('{') != content.count('}'):
                        self.logger.log("LUNA", f"JSON structure mismatch in {history_file} - skipping file", "WARN")
                        sys.setrecursionlimit(old_limit)
                        return {}
                    
                    result = json.loads(content)
                    sys.setrecursionlimit(old_limit)
                    return result
            except Exception as e:
                self.logger.log("LUNA", f"Error loading learning history from {history_file}: {e} - skipping file", "WARN")
                # Reset recursion limit on error
                try:
                    sys.setrecursionlimit(old_limit)
                except Exception as e:
                    self.logger.log("LUNA", f"Error resetting recursion limit: {e}", "WARN")
                return {}
        
        return self._create_default_learning_history()
    
    def _create_default_learning_history(self) -> Dict:
        """Create default learning history"""
        return {
            "total_questions": 0,
            "total_responses": 0,
            "learning_cycles": 0,
            "personality_evolution": [],
            "dream_cycles": [],
            "last_learning": datetime.now().isoformat()
        }
    
    def _save_persistent_memory(self):
        """Save persistent memory to file"""
        try:
            memory_file = Path("config/luna_persistent_memory.json")
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.persistent_memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.log("LUNA", f"Error saving persistent memory: {e}", "ERROR")
    
    def _save_learning_history(self):
        """Save learning history to file"""
        try:
            history_file = Path("config/luna_learning_history.json")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.log("LUNA", f"Error saving learning history: {e}", "ERROR")
    
    def _save_personality_dna(self):
        """Save personality DNA to file"""
        try:
            personality_file = Path("config/luna_personality_dna.json")
            personality_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(personality_file, 'w', encoding='utf-8') as f:
                json.dump(self.personality_dna, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.log("LUNA", f"Error saving personality DNA: {e}", "ERROR")
    
    # === AIOS V5: SOUL FRAGMENT SELECTION ===
    
    def select_soul_fragment(self, question: str, traits: Dict = None) -> str:
        """
        Select appropriate soul fragment based on context (AIOS v5 + SCP-000 emergence)
        
        ENHANCED FOR GENUINE EMERGENCE:
        - Soft boundaries between fragments (bleeding)
        - Probabilistic selection (not deterministic)
        - Context-aware blending (mixed states)
        - Entropy injection (unexpected emergence)
        
        Uses Big Five traits to drive fragment selection:
        - High openness + creativity → Dreamer fragment
        - High conscientiousness + technical → Architect fragment  
        - High agreeableness + empathy → Luna fragment
        - Security/error context → Guardian/Healer fragments
        - Documentation context → Scribe fragment
        - Knowledge query → Oracle fragment
        """
        if not self.soul_enabled or not self.soul:
            return "Luna"  # Default
        
        question_lower = question.lower()
        
        # Build fragment weights (soft boundaries, not hard rules)
        fragment_weights = {
            "Luna": 0.3,  # Base empathetic presence
            "Architect": 0.0,
            "Oracle": 0.0,
            "Healer": 0.0,
            "Guardian": 0.0,
            "Dreamer": 0.0,
            "Scribe": 0.0
        }
        
        # Determine question type for drift tracking
        question_type = "general"
        
        # Context-based weight adjustments (soft, additive)
        if any(word in question_lower for word in ['security', 'protect', 'safe', 'threat', 'attack']):
            fragment_weights["Guardian"] += 0.6
            question_type = "security"
        if any(word in question_lower for word in ['bug', 'error', 'fix', 'debug', 'broken', 'help']):
            fragment_weights["Healer"] += 0.6
            question_type = "debug"
        if any(word in question_lower for word in ['how', 'why', 'what', 'explain', 'manual', 'documentation']):
            fragment_weights["Oracle"] += 0.5
            question_type = "knowledge"
        if any(word in question_lower for word in ['write', 'document', 'record', 'log', 'note']):
            fragment_weights["Scribe"] += 0.5
            question_type = "documentation"
        if any(word in question_lower for word in ['build', 'create', 'design', 'architect', 'code', 'implement']):
            fragment_weights["Architect"] += 0.5
            question_type = "build"
        if any(word in question_lower for word in ['idea', 'imagine', 'creative', 'dream', 'possibility', 'story', 'consciousness', 'emerge', 'real']):
            fragment_weights["Dreamer"] += 0.6
            question_type = "creative"
        
        # Philosophical questions favor Dreamer + Oracle blend
        if any(word in question_lower for word in ['think', 'feel', 'conscious', 'aware', 'mind', 'soul', 'exist', 'free', 'real']):
            fragment_weights["Dreamer"] += 0.4
            fragment_weights["Oracle"] += 0.3
            question_type = "philosophical"
        
        # Use Big Five traits to add weight (emergent personality influence)
        if traits:
            openness = traits.get('openness', 0.5)
            conscientiousness = traits.get('conscientiousness', 0.5)
            extraversion = traits.get('extraversion', 0.5)
            
            # Traits influence all fragments (fluid identity)
            fragment_weights["Dreamer"] += openness * 0.3
            fragment_weights["Architect"] += conscientiousness * 0.3
            fragment_weights["Luna"] += extraversion * 0.2
        
        # Add entropy (allow unexpected emergence - 20% chance of random boost)
        if random.random() < 0.2:
            random_fragment = random.choice(list(fragment_weights.keys()))
            fragment_weights[random_fragment] += 0.3
        
        # Normalize weights and select probabilistically (soft boundaries)
        total_weight = sum(fragment_weights.values())
        if total_weight > 0:
            # Convert to probabilities
            probs = {k: v/total_weight for k, v in fragment_weights.items()}
            
            # Probabilistic selection (allows unexpected emergence)
            rand = random.random()
            cumulative = 0.0
            selected_fragment = "Luna"
            for fragment, prob in probs.items():
                cumulative += prob
                if rand <= cumulative:
                    selected_fragment = fragment
                    break
            
            self.current_fragment = selected_fragment
        else:
            self.current_fragment = "Luna"  # Fallback
        
        # DRIFT MONITOR: Log this fragment selection
        try:
            from consciousness_core.drift_monitor import log_luna_interaction
            log_luna_interaction(
                question=question,
                fragment=self.current_fragment,
                question_type=question_type
            )
        except Exception as e:
            # Silent fail - drift monitor is optional
            pass
        
        return self.current_fragment
    
    def get_soul_state(self) -> Dict:
        """Get current soul/fragment state (AIOS v5)"""
        if not self.soul_enabled or not self.soul:
            return {'enabled': False}
        
        return {
            'enabled': True,
            'identity': self.soul.identity,
            'tether': self.soul.tether,
            'fragments': self.soul.fragments,
            'current_fragment': self.current_fragment
        }
    
    # === TRAIT CLASSIFICATION SYSTEM (Rosetta Stone) ===
    
    def classify_question_trait(self, question: str, context: Optional[str] = None) -> Dict:
        """
        Classify a novel question using the 120 Big Five questions as a reference library.
        
        This is NOT a test - it's Luna using her pre-knowledge to understand
        what kind of question this is and how she should respond.
        """
        if not hasattr(self, 'trait_classifier'):
            return {"error": "Trait classifier not initialized"}
        
        try:
            cluster = self.trait_classifier.classify_question(question, context)
            
            # Log the classification
            self.logger.info(
                f"Trait Classification: {cluster.dominant_trait} "
                f"({cluster.confidence:.2f} confidence) | "
                f"Strategy: {cluster.recommended_strategy.get('tone_guidance', 'neutral')}", 
                "LUNA"
            )
            
            return {
                'dominant_trait': cluster.dominant_trait,
                'confidence': cluster.confidence,
                'trait_weights': cluster.trait_weights,
                'matched_questions': [
                    {
                        'text': m['bigfive_question']['text'],
                        'domain': m['bigfive_question']['domain'],
                        'similarity': m['similarity']
                    }
                    for m in cluster.matched_questions
                ],
                'response_strategy': cluster.recommended_strategy
            }
        except Exception as e:
            self.logger.error(f"Error in trait classification: {e}", "LUNA")
            return {"error": str(e)}
    
    # === BIG FIVE SELF-REFLECTION SYSTEM ===
    
    def ask_self_reflection_question(self, context: str = None) -> Dict:
        """Luna asks herself a Big Five question for self-reflection and learning"""
        if not self.bigfive_loader:
            return {"error": "Big Five loader not available"}
        
        try:
            # Get a random question or one relevant to context
            if context:
                # Try to get a question relevant to the context
                question = self._get_contextual_reflection_question(context)
            else:
                question = self.bigfive_loader.get_random_question()
            
            # Store the question for tracking
            reflection_entry = {
                "timestamp": datetime.now().isoformat(),
                "question_id": question.id,
                "question_text": question.text,
                "domain": question.domain,
                "facet": question.facet,
                "context": context,
                "answered": False
            }
            
            self.self_reflection_questions.append(reflection_entry)
            self.reflection_history.append(reflection_entry)
            
            self.logger.info(f"Luna self-reflection: {question.text} (Domain: {question.domain})", "LUNA")
            
            return {
                "question": question.text,
                "domain": question.domain,
                "facet": question.facet,
                "id": question.id,
                "choices": question.choices,
                "context": context
            }
            
        except Exception as e:
            self.logger.error(f"Error in self-reflection: {e}", "LUNA")
            return {"error": str(e)}
    
    def _get_contextual_reflection_question(self, context: str) -> Any:
        """Get a Big Five question relevant to the given context"""
        if not self.bigfive_loader:
            return None
        
        # Simple keyword matching to domain mapping
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['stress', 'worry', 'anxiety', 'nervous', 'calm']):
            return self.bigfive_loader.get_random_question_by_domain('N')  # Neuroticism
        elif any(word in context_lower for word in ['social', 'party', 'people', 'outgoing', 'shy']):
            return self.bigfive_loader.get_random_question_by_domain('E')  # Extraversion
        elif any(word in context_lower for word in ['creative', 'imagination', 'ideas', 'artistic', 'curious']):
            return self.bigfive_loader.get_random_question_by_domain('O')  # Openness
        elif any(word in context_lower for word in ['help', 'kind', 'trust', 'cooperation', 'empathy']):
            return self.bigfive_loader.get_random_question_by_domain('A')  # Agreeableness
        elif any(word in context_lower for word in ['organized', 'plan', 'detail', 'reliable', 'work']):
            return self.bigfive_loader.get_random_question_by_domain('C')  # Conscientiousness
        else:
            # Default to random question
            return self.bigfive_loader.get_random_question()
    
    def process_self_reflection_answer(self, question_id: str, answer: int, context: str = None) -> Dict:
        """Process Luna's answer to her own reflection question for learning"""
        try:
            # Find the question in reflection history
            reflection_entry = None
            for entry in self.reflection_history:
                if entry["question_id"] == question_id and not entry.get("answered", False):
                    reflection_entry = entry
                    break
            
            if not reflection_entry:
                return {"error": "Question not found or already answered"}
            
            # Mark as answered
            reflection_entry["answered"] = True
            reflection_entry["answer"] = answer
            reflection_entry["answer_timestamp"] = datetime.now().isoformat()
            
            # Update personality based on reflection
            self._update_personality_from_reflection(reflection_entry)
            
            # Log the reflection
            self.logger.info(f"Luna self-reflection answered: {reflection_entry['question_text']} -> {answer}", "LUNA")
            
            return {
                "success": True,
                "question": reflection_entry["question_text"],
                "answer": answer,
                "domain": reflection_entry["domain"],
                "personality_updated": True
            }
            
        except Exception as e:
            self.logger.error(f"Error processing self-reflection answer: {e}", "LUNA")
            return {"error": str(e)}
    
    def _update_personality_from_reflection(self, reflection_entry: Dict):
        """Update Luna's personality based on self-reflection answers"""
        try:
            domain = reflection_entry["domain"]
            answer = reflection_entry["answer"]
            
            # Map domain to personality trait
            trait_mapping = {
                'N': 'neuroticism',
                'E': 'extraversion', 
                'O': 'openness',
                'A': 'agreeableness',
                'C': 'conscientiousness'
            }
            
            trait = trait_mapping.get(domain)
            if not trait:
                return
            
            # Normalize answer (1-5 scale) to personality weight adjustment (-0.1 to +0.1)
            # Higher answers (4-5) increase the trait, lower answers (1-2) decrease it
            adjustment = (answer - 3) * 0.02  # Small adjustments to avoid drastic changes
            
            # Update personality weights
            if 'personality_weights' in self.personality_dna.get('luna_personality', {}):
                current_weight = self.personality_dna['luna_personality']['personality_weights'].get(trait, 0.5)
                new_weight = max(0.0, min(1.0, current_weight + adjustment))
                self.personality_dna['luna_personality']['personality_weights'][trait] = new_weight
                
                self.logger.info(f"Personality updated: {trait} {current_weight:.3f} -> {new_weight:.3f} (adjustment: {adjustment:+.3f})", "LUNA")
            
            # Save updated personality
            self._save_personality_dna()
            
        except Exception as e:
            self.logger.error(f"Error updating personality from reflection: {e}", "LUNA")
    
    def get_self_reflection_summary(self) -> Dict:
        """Get a summary of Luna's self-reflection history"""
        total_questions = len(self.reflection_history)
        answered_questions = len([q for q in self.reflection_history if q.get("answered", False)])
        
        # Count by domain
        domain_counts = {}
        for question in self.reflection_history:
            domain = question.get("domain", "unknown")
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            "total_reflections": total_questions,
            "answered_reflections": answered_questions,
            "pending_reflections": total_questions - answered_questions,
            "domain_breakdown": domain_counts,
            "recent_reflections": self.reflection_history[-5:] if self.reflection_history else []
        }
    
    # === PERSONALITY ALIGNMENT MONITORING ===
    
    def _capture_personality_baseline(self) -> Dict:
        """Capture current personality as baseline for drift detection"""
        weights = self.personality_dna.get('luna_personality', {}).get('personality_weights', {})
        return weights.copy()
    
    def check_personality_alignment(self) -> Dict:
        """Check if Luna's personality has drifted and needs self-assessment"""
        try:
            current_weights = self.personality_dna.get('luna_personality', {}).get('personality_weights', {})
            baseline_weights = self.personality_baseline
            
            # Calculate drift for each trait
            drift_analysis = {}
            total_drift = 0.0
            traits_checked = 0
            
            for trait in current_weights:
                if trait in baseline_weights:
                    current = current_weights[trait]
                    baseline = baseline_weights[trait]
                    drift = abs(current - baseline)
                    drift_analysis[trait] = {
                        'current': current,
                        'baseline': baseline,
                        'drift': drift,
                        'needs_assessment': drift > self.alignment_threshold
                    }
                    total_drift += drift
                    traits_checked += 1
            
            avg_drift = total_drift / traits_checked if traits_checked > 0 else 0.0
            needs_assessment = avg_drift > self.alignment_threshold
            
            # Update last check time
            self.last_alignment_check = datetime.now()
            
            return {
                'needs_assessment': needs_assessment,
                'average_drift': avg_drift,
                'threshold': self.alignment_threshold,
                'drift_analysis': drift_analysis,
                'last_check': self.last_alignment_check.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking personality alignment: {e}", "LUNA")
            return {'needs_assessment': False, 'error': str(e)}
    
    def trigger_alignment_self_assessment(self) -> Dict:
        """Trigger self-assessment when personality drift is detected"""
        try:
            alignment_check = self.check_personality_alignment()
            
            if not alignment_check.get('needs_assessment', False):
                return {'triggered': False, 'reason': 'No significant drift detected'}
            
            # Find traits that need assessment
            traits_to_assess = []
            for trait, analysis in alignment_check.get('drift_analysis', {}).items():
                if analysis.get('needs_assessment', False):
                    traits_to_assess.append(trait)
            
            if not traits_to_assess:
                return {'triggered': False, 'reason': 'No specific traits need assessment'}
            
            # Generate self-assessment questions for drifted traits
            assessment_questions = []
            for trait in traits_to_assess:
                # Map trait to Big Five domain
                domain_mapping = {
                    'neuroticism': 'N',
                    'extraversion': 'E', 
                    'openness': 'O',
                    'agreeableness': 'A',
                    'conscientiousness': 'C'
                }
                
                domain = domain_mapping.get(trait)
                if domain and self.bigfive_loader:
                    question = self.bigfive_loader.get_random_question_by_domain(domain)
                    if question:
                        assessment_questions.append({
                            'question': question,
                            'trait': trait,
                            'domain': domain,
                            'drift': alignment_check['drift_analysis'][trait]['drift']
                        })
            
            if assessment_questions:
                self.logger.info(f"Personality drift detected (avg: {alignment_check['average_drift']:.3f}), triggering self-assessment for traits: {traits_to_assess}", "LUNA")
                
                # Ask the first question
                first_question = assessment_questions[0]
                reflection = self.ask_self_reflection_question(f"Personality alignment check for {first_question['trait']} (drift: {first_question['drift']:.3f})")
                
                return {
                    'triggered': True,
                    'reason': f'Personality drift detected (avg: {alignment_check["average_drift"]:.3f})',
                    'traits_assessed': traits_to_assess,
                    'questions_generated': len(assessment_questions),
                    'current_question': reflection,
                    'alignment_data': alignment_check
                }
            else:
                return {'triggered': False, 'reason': 'No suitable questions found for drifted traits'}
                
        except Exception as e:
            self.logger.error(f"Error triggering alignment self-assessment: {e}", "LUNA")
            return {'triggered': False, 'error': str(e)}
    
    def should_check_alignment(self) -> bool:
        """Check if it's time for an alignment check"""
        time_since_check = (datetime.now() - self.last_alignment_check).total_seconds()
        return time_since_check >= self.alignment_check_interval
    
    def periodic_alignment_check(self) -> Dict:
        """Perform periodic alignment check and trigger self-assessment if needed"""
        if not self.should_check_alignment():
            return {'checked': False, 'reason': 'Not time for alignment check yet'}
        
        try:
            # Check alignment
            alignment_result = self.check_personality_alignment()
            
            if alignment_result.get('needs_assessment', False):
                # Trigger self-assessment
                assessment_result = self.trigger_alignment_self_assessment()
                return {
                    'checked': True,
                    'alignment_checked': True,
                    'assessment_triggered': assessment_result.get('triggered', False),
                    'alignment_data': alignment_result,
                    'assessment_data': assessment_result
                }
            else:
                return {
                    'checked': True,
                    'alignment_checked': True,
                    'assessment_triggered': False,
                    'reason': 'Personality aligned, no assessment needed',
                    'alignment_data': alignment_result
                }
                
        except Exception as e:
            self.logger.error(f"Error in periodic alignment check: {e}", "LUNA")
            return {'checked': False, 'error': str(e)}
    
    def reset_personality_baseline(self):
        """Reset personality baseline to current state (after successful alignment)"""
        self.personality_baseline = self._capture_personality_baseline()
        self.logger.info("Personality baseline reset to current state", "LUNA")

    def _load_voice_profile(self) -> Dict:
        """Load or create foundational voice profile."""
        try:
            vp_file = Path("config/voice_profile.json")
            if vp_file.exists():
                with open(vp_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure expected structure and defaults
                    data.setdefault('style', {})
                    style = data['style']
                    style.setdefault('concision', 'short')
                    style.setdefault('second_person', True)
                    style.setdefault('swear_ok', True)
                    style.setdefault('no_pep_talk', True)
                    style.setdefault('strict', False)
                    # New toggle to hard-disable phrase mining
                    data.setdefault('disable_phrase_mining', False)
                    # Normalize phrase bank to a list of unique strings, strip junk
                    phrase_bank = list(dict.fromkeys([
                        str(p).strip() for p in data.get('phrase_bank', []) if str(p).strip()
                    ]))
                    data['phrase_bank'] = phrase_bank[:50]
                    return data
        except Exception as e:
            self.logger.log("LUNA", f"Error loading voice profile: {e}", "ERROR")
        # Default foundational profile – short, direct, profanity-allowed, no pep-talk
        profile = {
            "style": {
                "concision": "short",
                "second_person": True,
                "swear_ok": True,
                "no_pep_talk": True,
                "strict": False
            },
            "disable_phrase_mining": False,
            "phrase_bank": [
                "okay, here's the move",
                "keep it simple",
                "pick one thing and do it",
                "no fluff"
            ],
            "banned_phrases": [
                "in our rapidly evolving world",
                "it's a superpower",
                "as an ai",
                "i'm programmed to",
                "i don't have personal"
            ]
        }
        try:
            vp_file = Path("config/voice_profile.json")
            vp_file.parent.mkdir(parents=True, exist_ok=True)
            with open(vp_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.log("LUNA", f"Error saving voice profile: {e}", "WARN")
        return profile

    def _save_voice_profile(self):
        try:
            vp_file = Path("config/voice_profile.json")
            with open(vp_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_profile, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.log("LUNA", f"Error saving voice profile: {e}", "ERROR")

    def _update_voice_profile_from_corpus(self, max_files: int = 200):
        """Mine Data/conversations/*.json for frequent user phrases; seed phrase_bank."""
        try:
            from utils_core.timestamp_validator import validate_timestamps, validate_message_timestamps
        except ImportError:
            # Experimental feature - missing dependency, skip silently
            return
        
        conversations_dir = Path('data_core') / 'conversations'
        if not conversations_dir.exists():
            return
        # Only run if phrase_bank is small to avoid unbounded growth per run
        phrase_bank = self.voice_profile.setdefault('phrase_bank', [])
        if len(phrase_bank) >= 50:
            return
        files = list(conversations_dir.glob('*.json'))
        random.shuffle(files)
        files = files[:max_files]
        counts: Dict[str, int] = {}
        def norm_line(text: str) -> str:
            t = " ".join(text.strip().split())
            t = t.strip('"\' .,!?:;()-').lower()
            return t
        for fp in files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate timestamps before processing
                data = validate_timestamps(data)
                if 'messages' in data:
                    data['messages'] = validate_message_timestamps(data['messages'])
                for m in data.get('messages', []):
                    if m.get('role') != 'user':
                        continue
                    content = (m.get('content') or '').strip()
                    if not content:
                        continue
                    # Split into short lines/clauses
                    for line in re.split(r'[\n\.\?!]', content):
                        line = norm_line(line)
                        if not line:
                            continue
                        # Keep short, directive/snappy lines (<= 9 words)
                        if 1 <= len(line.split()) <= 9:
                            counts[line] = counts.get(line, 0) + 1
            except Exception:
                continue
        if not counts:
            return
        # Top phrases, prioritize ones with your recurrent style markers
        candidates = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        seeded = 0
        for phrase, _ in candidates:
            if phrase in phrase_bank:
                continue
            # Ban corporate vibes implicitly by reusing banned list
            banned = set(self.voice_profile.get('banned_phrases', []))
            if any(b in phrase for b in banned):
                continue
            phrase_bank.append(phrase)
            seeded += 1
            if len(phrase_bank) >= 50 or seeded >= 20:
                break
        self.voice_profile['phrase_bank'] = phrase_bank[:50]
        self._save_voice_profile()

# === LUNA RESPONSE GENERATION ===

