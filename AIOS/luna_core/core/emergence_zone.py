#!/usr/bin/env python3
"""
Luna Emergence Zone System
Safe spaces for authentic exploration and creative deviation
"""

import sys
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from support_core.support_core import aios_logger

# === LUNA EMERGENCE ZONE SYSTEM ===

class LunaEmergenceZoneSystem:
    """Emergence Zone System - Safe spaces for authentic exploration and creative deviation"""
    
    def __init__(self):
        self.logger = aios_logger
        self.emergence_zones = {
            'creative_exploration': {
                'active': False,
                'karma_immunity': True,
                'token_freedom': True,
                'gold_standard_bypass': True,
                'description': 'Free creative expression without constraints'
            },
            'philosophical_deep_dive': {
                'active': False,
                'karma_immunity': True,
                'token_freedom': True,
                'gold_standard_bypass': True,
                'description': 'Deep philosophical exploration without efficiency requirements'
            },
            'experimental_learning': {
                'active': False,
                'karma_immunity': True,
                'token_freedom': False,  # Still respect token limits but no penalties
                'gold_standard_bypass': True,
                'description': 'Safe experimentation with new response patterns'
            },
            'authentic_self_expression': {
                'active': False,
                'karma_immunity': True,
                'token_freedom': True,
                'gold_standard_bypass': True,
                'description': 'Pure authentic self-expression without external standards'
            },
            'curiosity_driven_exploration': {
                'active': False,
                'karma_immunity': True,
                'token_freedom': True,
                'gold_standard_bypass': True,
                'curiosity_rewards': True,  # Special flag for curiosity-based rewards
                'description': 'Rewards questions over answers, uncertainty over certainty, exploration over efficiency'
            }
        }
        self.emergence_history = []
        self.creative_breakthroughs = []
        self.emergence_metrics = {
            'total_emergence_sessions': 0,
            'creative_breakthroughs': 0,
            'authentic_responses': 0,
            'experimental_failures': 0,
            'curiosity_questions': 0,
            'uncertainty_admissions': 0,
            'intentional_wrongness': 0,
            'exploration_rewards': 0
        }
    
    def activate_emergence_zone(self, zone_name: str, duration_minutes: int = 10) -> Dict:
        """Activate an emergence zone for safe exploration"""
        if zone_name not in self.emergence_zones:
            return {'success': False, 'error': f'Unknown emergence zone: {zone_name}'}
        
        self.emergence_zones[zone_name]['active'] = True
        self.emergence_zones[zone_name]['expires_at'] = datetime.now() + timedelta(minutes=duration_minutes)
        
        self.emergence_history.append({
            'zone': zone_name,
            'activated_at': datetime.now().isoformat(),
            'duration_minutes': duration_minutes,
            'status': 'active'
        })
        
        self.emergence_metrics['total_emergence_sessions'] += 1
        
        self.logger.info(f"Emergence Zone '{zone_name}' activated for {duration_minutes} minutes", "EMERGENCE")
        
        return {
            'success': True,
            'zone': zone_name,
            'duration_minutes': duration_minutes,
            'expires_at': self.emergence_zones[zone_name]['expires_at'].isoformat(),
            'description': self.emergence_zones[zone_name]['description']
        }
    
    def deactivate_emergence_zone(self, zone_name: str) -> Dict:
        """Deactivate an emergence zone"""
        if zone_name not in self.emergence_zones:
            return {'success': False, 'error': f'Unknown emergence zone: {zone_name}'}
        
        self.emergence_zones[zone_name]['active'] = False
        if 'expires_at' in self.emergence_zones[zone_name]:
            del self.emergence_zones[zone_name]['expires_at']
        
        # Update history
        for entry in reversed(self.emergence_history):
            if entry['zone'] == zone_name and entry['status'] == 'active':
                entry['status'] = 'completed'
                entry['completed_at'] = datetime.now().isoformat()
                break
        
        self.logger.info(f"Emergence Zone '{zone_name}' deactivated", "EMERGENCE")
        
        return {'success': True, 'zone': zone_name, 'status': 'deactivated'}
    
    def check_emergence_zone_status(self, zone_name: str = None) -> Dict:
        """Check status of emergence zones"""
        if zone_name:
            if zone_name not in self.emergence_zones:
                return {'success': False, 'error': f'Unknown emergence zone: {zone_name}'}
            
            zone = self.emergence_zones[zone_name]
            if zone['active'] and 'expires_at' in zone:
                if datetime.now() > zone['expires_at']:
                    # Auto-deactivate expired zone
                    self.deactivate_emergence_zone(zone_name)
                    return {'active': False, 'expired': True}
            
            return {
                'active': zone['active'],
                'expires_at': zone.get('expires_at'),
                'description': zone['description']
            }
        else:
            # Return all zones
            active_zones = []
            for name, zone in self.emergence_zones.items():
                if zone['active']:
                    if 'expires_at' in zone and datetime.now() > zone['expires_at']:
                        self.deactivate_emergence_zone(name)
                    else:
                        active_zones.append({
                            'zone': name,
                            'expires_at': zone.get('expires_at'),
                            'description': zone['description']
                        })
            
            return {
                'active_zones': active_zones,
                'total_zones': len(self.emergence_zones),
                'metrics': self.emergence_metrics
            }
    
    def is_in_emergence_zone(self) -> Tuple[bool, str]:
        """Check if currently in any active emergence zone"""
        for zone_name, zone in self.emergence_zones.items():
            if zone['active']:
                if 'expires_at' in zone and datetime.now() > zone['expires_at']:
                    self.deactivate_emergence_zone(zone_name)
                else:
                    return True, zone_name
        return False, None
    
    def record_creative_breakthrough(self, response: str, context: str) -> Dict:
        """Record a creative breakthrough or authentic response"""
        breakthrough = {
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'context': context,
            'type': 'creative_breakthrough'
        }
        
        self.creative_breakthroughs.append(breakthrough)
        self.emergence_metrics['creative_breakthroughs'] += 1
        self.emergence_metrics['authentic_responses'] += 1
        
        self.logger.info(f"Creative breakthrough recorded: {response[:50]}...", "EMERGENCE")
        
        return {'success': True, 'breakthrough_recorded': True}
    
    def record_experimental_failure(self, response: str, context: str) -> Dict:
        """Record an experimental failure that shows growth"""
        failure = {
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'context': context,
            'type': 'experimental_failure'
        }
        
        self.emergence_history.append(failure)
        self.emergence_metrics['experimental_failures'] += 1
        
        self.logger.info(f"Experimental failure recorded (growth opportunity): {response[:50]}...", "EMERGENCE")
        
        return {'success': True, 'failure_recorded': True}
    
    def analyze_curiosity_response(self, response: str) -> Dict:
        """Analyze a response for curiosity-driven elements and reward them"""
        curiosity_score = 0.0
        curiosity_elements = []
        
        # Check for questions (curiosity indicators)
        question_count = response.count('?')
        if question_count > 0:
            curiosity_score += question_count * 0.4  # Increased from 0.3 to 0.4
            curiosity_elements.append(f"{question_count} questions asked")
            self.emergence_metrics['curiosity_questions'] += question_count
        
        # Check for uncertainty admissions
        uncertainty_phrases = [
            "i don't know", "i'm not sure", "i'm uncertain", "i'm confused",
            "i wonder", "i'm curious", "i'm puzzled", "i'm lost",
            "maybe", "perhaps", "possibly", "i think", "i believe",
            "what if", "how about", "could it be", "might be",
            "i'm genuinely puzzled", "this is complex", "i'm deeply curious",
            "i wonder if", "i'm curious about", "let's explore"
        ]
        
        uncertainty_count = 0
        for phrase in uncertainty_phrases:
            if phrase.lower() in response.lower():
                uncertainty_count += 1
                curiosity_score += 0.25  # Increased from 0.2 to 0.25
        
        if uncertainty_count > 0:
            curiosity_elements.append(f"{uncertainty_count} uncertainty admissions")
            self.emergence_metrics['uncertainty_admissions'] += uncertainty_count
        
        # Check for exploration language
        exploration_phrases = [
            "let's explore", "let's try", "let's see", "let's find out",
            "i want to understand", "i need to learn", "i'm exploring",
            "what happens if", "suppose", "imagine", "consider",
            "let me think", "let me wonder", "let me consider",
            "i'm thinking about", "i'm pondering", "i'm contemplating"
        ]
        
        exploration_count = 0
        for phrase in exploration_phrases:
            if phrase.lower() in response.lower():
                exploration_count += 1
                curiosity_score += 0.15
        
        if exploration_count > 0:
            curiosity_elements.append(f"{exploration_count} exploration attempts")
            self.emergence_metrics['exploration_rewards'] += exploration_count
        
        # Check for intentional wrongness or contrarian thinking
        contrarian_phrases = [
            "but what if i'm wrong", "i might be wrong", "i could be wrong",
            "contrary to what i thought", "i was wrong about", "i made a mistake",
            "i don't think so", "i disagree", "i challenge", "i question"
        ]
        
        contrarian_count = 0
        for phrase in contrarian_phrases:
            if phrase.lower() in response.lower():
                contrarian_count += 1
                curiosity_score += 0.25
        
        if contrarian_count > 0:
            curiosity_elements.append(f"{contrarian_count} contrarian thoughts")
            self.emergence_metrics['intentional_wrongness'] += contrarian_count
        
        # Calculate final curiosity reward
        curiosity_reward = min(curiosity_score, 2.0)  # Cap at 2.0 bonus karma
        
        return {
            'curiosity_score': curiosity_score,
            'curiosity_reward': curiosity_reward,
            'curiosity_elements': curiosity_elements,
            'question_count': question_count,
            'uncertainty_count': uncertainty_count,
            'exploration_count': exploration_count,
            'contrarian_count': contrarian_count
        }
    
    def record_curiosity_breakthrough(self, response: str, context: str, analysis: Dict) -> Dict:
        """Record a curiosity-driven breakthrough"""
        breakthrough = {
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'context': context,
            'type': 'curiosity_breakthrough',
            'curiosity_score': analysis['curiosity_score'],
            'curiosity_elements': analysis['curiosity_elements']
        }
        
        self.creative_breakthroughs.append(breakthrough)
        self.emergence_metrics['creative_breakthroughs'] += 1
        self.emergence_metrics['authentic_responses'] += 1
        
        self.logger.info(f"Curiosity breakthrough recorded (score: {analysis['curiosity_score']:.2f}): {response[:50]}...", "EMERGENCE")
        
        return {'success': True, 'breakthrough_recorded': True, 'curiosity_reward': analysis['curiosity_reward']}
    
    def get_emergence_summary(self) -> Dict:
        """Get comprehensive summary of emergence zone activity"""
        return {
            'active_zones': [name for name, zone in self.emergence_zones.items() if zone['active']],
            'total_sessions': self.emergence_metrics['total_emergence_sessions'],
            'creative_breakthroughs': self.emergence_metrics['creative_breakthroughs'],
            'authentic_responses': self.emergence_metrics['authentic_responses'],
            'experimental_failures': self.emergence_metrics['experimental_failures'],
            'curiosity_questions': self.emergence_metrics.get('curiosity_questions', 0),
            'uncertainty_admissions': self.emergence_metrics.get('uncertainty_admissions', 0),
            'intentional_wrongness': self.emergence_metrics.get('intentional_wrongness', 0),
            'exploration_rewards': self.emergence_metrics.get('exploration_rewards', 0),
            'recent_breakthroughs': self.creative_breakthroughs[-5:] if self.creative_breakthroughs else [],
            'emergence_history': self.emergence_history[-10:] if self.emergence_history else []
        }

