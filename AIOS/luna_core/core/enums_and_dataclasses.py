#!/usr/bin/env python3
"""
Luna Core Enums and Data Classes
Shared data structures used across Luna core components
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from support_core.support_core import SystemConfig

# === ENUMS ===

class LearningMode(Enum):
    REAL_LEARNING = "real_learning"
    SIMULATION = "simulation"
    TESTING = "testing"
    HEALTH_CHECK = "health"

# === DATA CLASSES ===

@dataclass
class PersonalityWeights:
    """Luna's personality weights for Big Five traits"""
    openness: float = 0.7
    conscientiousness: float = 0.6
    extraversion: float = 0.8
    agreeableness: float = 0.9
    neuroticism: float = 0.3

@dataclass
class CommunicationStyle:
    """Luna's communication style preferences"""
    formality: float = 0.3
    humor_level: float = 0.8
    empathy_level: float = SystemConfig.DEFAULT_EMPATHY
    technical_depth: float = 0.6
    creativity: float = 0.8

@dataclass
class LearningHistory:
    """Luna's learning history tracking"""
    total_questions: int = 0
    total_responses: int = 0
    learning_cycles: int = 0
    personality_evolution: List[Dict] = None
    dream_cycles: List[Dict] = None
    last_learning: datetime = None
    
    def __post_init__(self):
        if self.personality_evolution is None:
            self.personality_evolution = []
        if self.dream_cycles is None:
            self.dream_cycles = []
        if self.last_learning is None:
            self.last_learning = datetime.now()

