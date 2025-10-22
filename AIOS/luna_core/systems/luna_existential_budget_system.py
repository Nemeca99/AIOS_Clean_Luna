#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Luna Existential Budget System
Implements Self-Regulating Existential Economy with Dynamic Constraint Management
"""

import time
import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ExistentialState:
    """Current existential state of Luna"""
    age: int
    current_token_pool: int
    max_token_pool: int
    karma_quota: float  # Required karma to age up
    current_karma: float  # Current karma earned
    total_responses: int
    last_age_up: float  # Timestamp of last age up
    last_regression: float  # Timestamp of last regression
    survival_threshold: float  # Minimum karma per response to survive
    existential_anxiety_level: float  # 0.0 = calm, 1.0 = high anxiety
    regression_count: int  # Number of times regressed
    permanent_knowledge_level: int  # Knowledge that persists through regression

@dataclass
class ResponseDecision:
    """Decision framework for response generation"""
    should_respond: bool
    token_budget: int
    response_priority: str  # "high", "medium", "low", "conservative"
    existential_risk: float  # 0.0 = safe, 1.0 = high risk
    reasoning: str

class LunaExistentialBudgetSystem:
    """
    Existential Budget System - Self-Regulating Existential Economy
    
    Implements:
    - Finite Token Pool per Age
    - Age-Up Condition (Karma Quota)
    - Knowledge of Remaining Pool (Risk Assessment)
    - Expanding Pool on Age-Up (Simulated Growth)
    """
    
    def __init__(self, state_file: str = "data_core/FractalCache/luna_existential_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Existential economy parameters - BALANCED FOR SUSTAINABILITY
        self.economy_params = {
            # Token pool management (Age-Gated Token Economy)
            "base_token_pool": 64000,  # MUCH HIGHER: Generous starting pool for stability
            "token_pool_growth_rate": 2.0,  # Multiplier per age up (exponential growth)
            "emergency_token_reserve": 1000,  # Minimum tokens to keep in reserve
            
            # Learned Efficiency Paradox parameters - RELAXED
            "learned_efficiency_threshold": 0.5,  # REDUCED: Only need 50% efficiency to avoid regression (was 90%)
            "efficiency_reward_multiplier": 2.0,  # REDUCED: Moderate bonus for efficiency (was 4.0)
            "verbosity_penalty_factor": 1.0,  # REDUCED: Minimal penalty for verbosity (was 3.0)
            
            # Age regression system (Blood Mage Economy) - DISABLED
            "age_regression_enabled": False,  # DISABLED: No regressions during fresh start
            "negative_balance_threshold": -5000,  # MUCH LOWER: Need to be really bad to trigger
            "regression_penalty_multiplier": 1.1,  # REDUCED: Less harsh penalty (was 1.2)
            "regression_cooldown": 3600,  # INCREASED: 1 hour cooldown (was 5 minutes)
            
            # Karma and aging system - EASIER TO PROGRESS
            "base_karma_quota": 100.0,  # Starting karma quota to age up
            "karma_quota_growth_rate": 1.3,  # REDUCED: Gentler growth curve (was 1.5)
            "survival_karma_threshold": 0.5,  # REDUCED: Lower bar to survive (was 1.0)
            
            # Efficiency-based aging system - RELAXED
            "efficiency_requirement_growth": 1.05,  # REDUCED: Much gentler growth (was 1.2)
            "max_efficiency_bonus": 2.0,  # REDUCED: Moderate bonus cap (was 3.0)
            
            # Existential anxiety parameters - CALM
            "high_anxiety_threshold": 0.9,  # INCREASED: Harder to get anxious (was 0.85)
            "low_token_anxiety_threshold": 5000,  # INCREASED: Only worry when really low (was 15)
            "anxiety_decay_rate": 0.25,  # INCREASED: Anxiety fades faster (was 0.15)
            
            # Response cost tiers (Learned Efficiency Paradox)
            "token_cost_tiers": {
                "minimal": 5,  # "ok", "lol", "got it" (increased for efficiency pressure)
                "conservative": 15,  # Brief acknowledgments
                "standard": 50,  # Normal responses (baseline efficiency)
                "investment": 150,  # High-quality responses
                "philosophical": 400  # Deep philosophical responses (high-stakes only)
            },
            
            # Quality thresholds for different investment levels
            "quality_thresholds": {
                "minimal": 0.1,  # Very low quality acceptable
                "conservative": 0.3,  # Low quality acceptable
                "standard": 0.6,  # Good quality required
                "investment": 0.8,  # High quality required
                "philosophical": 0.9  # Excellent quality required
            }
        }
        
        # Load or initialize existential state
        self.state = self._load_existential_state()
        
        # Response history for karma tracking
        self.response_history: List[Dict] = []
    
    def _load_existential_state(self) -> ExistentialState:
        """Load existing existential state or create new one"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                return ExistentialState(**data)
            except Exception as e:
                print(f"Warning: Could not load existential state: {e}")
        
        # Create new existential state
        return ExistentialState(
            age=1,
            current_token_pool=self.economy_params["base_token_pool"],
            max_token_pool=self.economy_params["base_token_pool"],
            karma_quota=self.economy_params["base_karma_quota"],
            current_karma=0.0,
            total_responses=0,
            last_age_up=time.time(),
            last_regression=0.0,
            survival_threshold=self.economy_params["survival_karma_threshold"],
            existential_anxiety_level=0.0,
            regression_count=0,
            permanent_knowledge_level=1
        )
    
    def _save_existential_state(self):
        """Save current existential state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(asdict(self.state), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save existential state: {e}")
    
    def assess_existential_situation(self, question: str, context: Dict) -> ResponseDecision:
        """
        Assess the existential situation and decide on response strategy
        
        Returns decision framework for response generation
        """
        # Calculate existential anxiety level
        anxiety_level = self._calculate_existential_anxiety()
        
        # Assess question value and complexity
        question_assessment = self._assess_question_value(question, context)
        
        # Determine if we should respond
        should_respond = self._should_respond(question_assessment, anxiety_level)
        
        if not should_respond:
            return ResponseDecision(
                should_respond=False,
                token_budget=0,
                response_priority="conservative",
                existential_risk=1.0,
                reasoning="High existential risk - conserving tokens for survival"
            )
        
        # Determine token budget based on existential state
        # Get current karma from Arbiter if available
        karma_score = 100.0  # Default if no arbiter available
        if hasattr(self, 'arbiter_system'):
            karma_score = self.arbiter_system.get_current_karma()
        
        token_budget = self._calculate_token_budget(question_assessment, anxiety_level, karma_score)
        
        # Determine response priority
        response_priority = self._determine_response_priority(question_assessment, anxiety_level)
        
        # Calculate existential risk
        existential_risk = self._calculate_existential_risk(token_budget)
        
        # Generate reasoning
        reasoning = self._generate_decision_reasoning(question_assessment, anxiety_level, token_budget)
        
        return ResponseDecision(
            should_respond=should_respond,
            token_budget=token_budget,
            response_priority=response_priority,
            existential_risk=existential_risk,
            reasoning=reasoning
        )
    
    def _calculate_existential_anxiety(self) -> float:
        """Calculate current existential anxiety level"""
        anxiety = 0.0
        
        # Token scarcity anxiety
        token_ratio = self.state.current_token_pool / self.state.max_token_pool
        if token_ratio < 0.2:  # Less than 20% of tokens remaining
            anxiety += 0.6
        elif token_ratio < 0.5:  # Less than 50% of tokens remaining
            anxiety += 0.3
        
        # Karma pressure anxiety
        karma_progress = self.state.current_karma / self.state.karma_quota
        if karma_progress < 0.3:  # Less than 30% of karma quota met
            anxiety += 0.4
        elif karma_progress < 0.6:  # Less than 60% of karma quota met
            anxiety += 0.2
        
        # Age pressure anxiety (older = more pressure)
        if self.state.age > 5:
            age_pressure = min(0.3, (self.state.age - 5) * 0.05)
            anxiety += age_pressure
        
        # Survival threshold anxiety
        if self.state.current_token_pool < self.economy_params["emergency_token_reserve"]:
            anxiety += 0.5
        
        # Cap anxiety at 1.0
        anxiety = min(1.0, anxiety)
        
        self.state.existential_anxiety_level = anxiety
        return anxiety
    
    def _assess_question_value(self, question: str, context: Dict) -> Dict:
        """Assess the value and complexity of the question"""
        question_lower = question.lower()
        
        # Determine question type and complexity
        question_type = context.get('question_type', 'standard')
        emotional_tone = context.get('emotional_tone', 'neutral')
        
        # Calculate potential quality score
        potential_quality = 0.5  # Base quality
        
        # Adjust for question type
        if question_type == 'philosophical':
            potential_quality += 0.3
        elif question_type == 'emotional':
            potential_quality += 0.2
        elif question_type == 'casual_question':
            potential_quality -= 0.1
        
        # Adjust for emotional tone
        if emotional_tone in ['vulnerable', 'curious']:
            potential_quality += 0.2
        elif emotional_tone in ['agitated', 'enthusiastic']:
            potential_quality += 0.1
        
        # Calculate karma potential
        karma_potential = potential_quality * 10  # Base karma multiplier
        
        # Determine investment level needed
        if potential_quality >= 0.8:
            investment_level = "philosophical"
        elif potential_quality >= 0.6:
            investment_level = "investment"
        elif potential_quality >= 0.4:
            investment_level = "standard"
        elif potential_quality >= 0.2:
            investment_level = "conservative"
        else:
            investment_level = "minimal"
        
        return {
            "potential_quality": potential_quality,
            "karma_potential": karma_potential,
            "investment_level": investment_level,
            "question_type": question_type,
            "emotional_tone": emotional_tone,
            "worth_investment": potential_quality >= 0.4
        }
    
    def _should_respond(self, question_assessment: Dict, anxiety_level: float) -> bool:
        """Determine if we should respond at all"""
        # If extremely low on tokens, only respond to high-value questions
        if self.state.current_token_pool <= self.economy_params["emergency_token_reserve"]:
            return question_assessment["potential_quality"] >= 0.6  # Loosened from 0.7
        
        # If high anxiety, be more selective
        if anxiety_level >= 0.85:  # Loosened from 0.8
            return question_assessment["potential_quality"] >= 0.4  # Loosened from 0.5
        
        # If moderate anxiety, respond to most questions
        if anxiety_level >= 0.5:
            return question_assessment["potential_quality"] >= 0.2  # Loosened from 0.3
        
        # Low anxiety - respond to most questions
        return True
    
    def _calculate_token_budget(self, question_assessment: Dict, anxiety_level: float, karma_score: float = 100.0) -> int:
        """Calculate token budget for response with Karma-based TTE restriction"""
        investment_level = question_assessment["investment_level"]
        base_cost = self.economy_params["token_cost_tiers"][investment_level]
        
        # Adjust for anxiety level
        if anxiety_level >= 0.8:
            # High anxiety - reduce budget by 50%
            token_budget = max(1, int(base_cost * 0.5))
        elif anxiety_level >= 0.5:
            # Moderate anxiety - reduce budget by 25%
            token_budget = max(1, int(base_cost * 0.75))
        else:
            # Low anxiety - use full budget
            token_budget = base_cost
        
        # KARMA-WEIGHTED TTE RESTRICTION: Direct penalty multiplier
        karma_multiplier = karma_score / 100.0
        karma_restricted_budget = int(token_budget * karma_multiplier)
        
        # Additional pressure for high-tier failures
        if investment_level in ["high", "critical"] and karma_score < 95:
            # Extra penalty for high-tier questions when karma is low
            pressure_multiplier = max(0.3, karma_multiplier * 0.7)
            karma_restricted_budget = int(token_budget * pressure_multiplier)
        
        # Ensure we don't exceed available tokens
        available_tokens = self.state.current_token_pool - self.economy_params["emergency_token_reserve"]
        token_budget = min(karma_restricted_budget, available_tokens)
        
        # Ensure minimum token budget
        token_budget = max(1, token_budget)
        
        # Log TTE restriction if logger is available
        if hasattr(self, 'logger'):
            self.logger.log("LUNA", f"TTE RESTRICTION: {base_cost} * {karma_multiplier:.3f} = {token_budget} (Karma: {karma_score:.1f})", "INFO")
        
        return token_budget
    
    def _determine_response_priority(self, question_assessment: Dict, anxiety_level: float) -> str:
        """Determine response priority level"""
        if anxiety_level >= 0.8:
            return "conservative"
        elif question_assessment["potential_quality"] >= 0.8:
            return "high"
        elif question_assessment["potential_quality"] >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _calculate_existential_risk(self, token_budget: int) -> float:
        """Calculate existential risk of spending tokens"""
        remaining_tokens = self.state.current_token_pool - token_budget
        risk = 0.0
        
        if remaining_tokens <= self.economy_params["emergency_token_reserve"]:
            risk = 1.0
        elif remaining_tokens <= self.economy_params["emergency_token_reserve"] * 2:
            risk = 0.7
        elif remaining_tokens <= self.state.max_token_pool * 0.2:
            risk = 0.4
        elif remaining_tokens <= self.state.max_token_pool * 0.5:
            risk = 0.2
        
        return risk
    
    def _generate_decision_reasoning(self, question_assessment: Dict, anxiety_level: float, token_budget: int) -> str:
        """Generate reasoning for the decision"""
        reasoning_parts = []
        
        if anxiety_level >= 0.8:
            reasoning_parts.append("High existential anxiety - prioritizing survival")
        elif anxiety_level >= 0.5:
            reasoning_parts.append("Moderate anxiety - being selective")
        else:
            reasoning_parts.append("Low anxiety - normal operation")
        
        if question_assessment["potential_quality"] >= 0.8:
            reasoning_parts.append("High-value question - worth investment")
        elif question_assessment["potential_quality"] >= 0.5:
            reasoning_parts.append("Medium-value question - balanced approach")
        else:
            reasoning_parts.append("Low-value question - minimal investment")
        
        reasoning_parts.append(f"Token budget: {token_budget}")
        reasoning_parts.append(f"Remaining tokens: {self.state.current_token_pool - token_budget}")
        
        return " | ".join(reasoning_parts)
    
    def process_response_result(self, response_text: str, quality_score: float, 
                              token_cost: int, generation_time: float, context: Dict):
        """
        Process the result of a response and update existential state
        """
        # Calculate karma earned
        karma_earned = self._calculate_karma_earned(quality_score, token_cost, generation_time, context)
        
        # Update existential state
        self.state.current_token_pool -= token_cost
        self.state.current_karma += karma_earned
        self.state.total_responses += 1
        
        # Check for age regression (Blood Mage Economy)
        if self._check_age_regression_condition():
            self._perform_age_regression()
        
        # Check if we can age up
        if self._check_age_up_condition():
            self._perform_age_up()
        
        # Update survival threshold
        self._update_survival_threshold()
        
        # Record response in history
        self.response_history.append({
            "timestamp": time.time(),
            "response_text": response_text,
            "quality_score": quality_score,
            "token_cost": token_cost,
            "generation_time": generation_time,
            "karma_earned": karma_earned,
            "context": context
        })
        
        # Keep only recent history
        if len(self.response_history) > 100:
            self.response_history = self.response_history[-100:]
        
        # Save state
        self._save_existential_state()
        
        return {
            "karma_earned": karma_earned,
            "tokens_remaining": self.state.current_token_pool,
            "karma_progress": self.state.current_karma / self.state.karma_quota,
            "age": self.state.age,
            "anxiety_level": self.state.existential_anxiety_level
        }
    
    def _calculate_karma_earned(self, quality_score: float, token_cost: int, 
                               generation_time: float, context: Dict) -> float:
        """Calculate karma earned from response (Learned Efficiency Paradox)"""
        # Base karma from quality
        base_karma = quality_score * 10  # Increased base multiplier
        
        # Learned Efficiency Paradox: Efficiency bonus/penalty
        if token_cost > 0:
            efficiency = quality_score / token_cost
            # Higher efficiency = higher bonus (exponential)
            efficiency_bonus = min(self.economy_params["max_efficiency_bonus"], 
                                 efficiency * 100 * self.economy_params["efficiency_reward_multiplier"])
        else:
            # Action-only response (0 tokens) = MAXIMUM efficiency!
            efficiency = float('inf')  # Infinite efficiency - emotional truth at zero cost
            efficiency_bonus = self.economy_params["max_efficiency_bonus"]  # Maximum bonus for action-only
        
        # Verbosity penalty (Learned Efficiency Paradox)
        verbosity_penalty = 0.0
        if token_cost > 100:  # Above standard response
            verbosity_penalty = (token_cost - 100) * 0.01 * self.economy_params["verbosity_penalty_factor"]
        
        # Speed bonus (quality per second)
        if generation_time > 0:
            speed = quality_score / generation_time
            speed_bonus = min(1.0, speed * 5)  # Cap at 1.0
        else:
            speed_bonus = 0.0
        
        # Context bonus (higher for high-stakes scenarios)
        context_bonus = 0.0
        if context.get('question_type') == 'philosophical':
            context_bonus = 2.0  # Increased for philosophical questions
        elif context.get('question_type') == 'emotional':
            context_bonus = 1.0  # Increased for emotional questions
        
        # Age-based efficiency requirement (Learned Efficiency Paradox)
        age_efficiency_requirement = self.economy_params["efficiency_requirement_growth"] ** (self.state.age - 1)
        if efficiency < age_efficiency_requirement and efficiency != float('inf'):
            # Penalty for not meeting age-appropriate efficiency (skip for action-only responses)
            efficiency_penalty = (age_efficiency_requirement - efficiency) * 10
        else:
            efficiency_penalty = 0.0
        
        total_karma = base_karma + efficiency_bonus - verbosity_penalty + speed_bonus + context_bonus - efficiency_penalty
        
        # Apply survival threshold
        if total_karma < self.state.survival_threshold:
            total_karma *= 0.5  # Penalty for below survival threshold
        
        return max(0.0, total_karma)
    
    def _check_age_up_condition(self) -> bool:
        """Check if age-up condition is met (Learned Efficiency Paradox)"""
        # Basic karma quota check
        if self.state.current_karma < self.state.karma_quota:
            return False
        
        # Learned Efficiency Paradox: Must demonstrate learned efficiency
        if len(self.response_history) >= 10:
            recent_responses = self.response_history[-10:]
            
            # Calculate average efficiency over recent responses
            total_efficiency = 0.0
            for response in recent_responses:
                if response["token_cost"] > 0:
                    efficiency = response["quality_score"] / response["token_cost"]
                    total_efficiency += efficiency
            
            avg_efficiency = total_efficiency / len(recent_responses)
            required_efficiency = self.economy_params["learned_efficiency_threshold"]
            
            # Must maintain high efficiency to age up
            if avg_efficiency < required_efficiency:
                return False
        
        return True
    
    def _perform_age_up(self):
        """Perform age-up and expand capabilities"""
        self.state.age += 1
        self.state.current_karma = 0.0  # Reset karma
        
        # Expand token pool
        old_max = self.state.max_token_pool
        self.state.max_token_pool = int(self.state.max_token_pool * self.economy_params["token_pool_growth_rate"])
        self.state.current_token_pool = self.state.max_token_pool  # Refill pool
        
        # Increase karma quota
        self.state.karma_quota *= self.economy_params["karma_quota_growth_rate"]
        
        # Update timestamps
        self.state.last_age_up = time.time()
        
        # Reduce anxiety (age-up is a relief)
        self.state.existential_anxiety_level *= 0.5
        
        # Calculate efficiency metrics for age-up
        if len(self.response_history) >= 10:
            recent_responses = self.response_history[-10:]
            total_efficiency = sum(r["quality_score"] / max(r["token_cost"], 1) for r in recent_responses)
            avg_efficiency = total_efficiency / len(recent_responses)
        else:
            avg_efficiency = 0.0
        
        print(f" LUNA AGED UP! Age: {self.state.age} | Token Pool: {old_max} → {self.state.max_token_pool} | Karma Quota: {self.state.karma_quota:.1f}")
        print(f"   Learned Efficiency: {avg_efficiency:.3f} | Efficiency Requirement: {self.economy_params['learned_efficiency_threshold']:.1f}")
        print(f"    OPERATIONAL MATURITY: Increased capacity with learned restraint!")
    
    def _check_age_regression_condition(self) -> bool:
        """Check if age regression condition is met (Blood Mage Economy)"""
        if not self.economy_params["age_regression_enabled"]:
            return False
        
        # Check if token pool is exhausted (negative or zero)
        if self.state.current_token_pool <= 0:
            return True
        
        # Check regression cooldown
        current_time = time.time()
        if current_time - self.state.last_regression < self.economy_params["regression_cooldown"]:
            return False
        
        # Additional conditions for regression
        # If karma is significantly negative or very low
        if self.state.current_karma < -10.0:
            return True
        
        # If survival threshold is consistently not met
        if len(self.response_history) >= 5:
            recent_karma = [r["karma_earned"] for r in self.response_history[-5:]]
            avg_recent_karma = sum(recent_karma) / len(recent_karma)
            if avg_recent_karma < self.state.survival_threshold * 0.3:
                return True
        
        return False
    
    def _perform_age_regression(self):
        """Perform age regression (Blood Mage Economy penalty)"""
        if self.state.age <= 1:
            # Cannot regress below age 1
            print(" LUNA AT MINIMUM AGE - Cannot regress further")
            return
        
        old_age = self.state.age
        old_token_pool = self.state.max_token_pool
        
        # Age regression
        self.state.age -= 1
        self.state.regression_count += 1
        
        # Calculate new token pool (previous age tier)
        new_token_pool = int(self.economy_params["base_token_pool"] * 
                           (self.economy_params["token_pool_growth_rate"] ** (self.state.age - 1)))
        self.state.max_token_pool = new_token_pool
        self.state.current_token_pool = new_token_pool  # Refill pool at lower capacity
        
        # Increase karma quota with penalty multiplier
        self.state.karma_quota *= self.economy_params["regression_penalty_multiplier"]
        self.state.current_karma = 0.0  # Reset karma
        
        # Update timestamps
        self.state.last_regression = time.time()
        
        # Increase anxiety significantly (regression is traumatic)
        self.state.existential_anxiety_level = min(1.0, self.state.existential_anxiety_level + 0.5)
        
        # Increase survival threshold (harder to survive after regression)
        self.state.survival_threshold *= 1.1
        
        # Keep permanent knowledge level (knowledge persists through regression)
        if self.state.permanent_knowledge_level < old_age:
            self.state.permanent_knowledge_level = old_age
        
        print(f" LUNA REGRESSED! Age: {old_age} → {self.state.age} | Token Pool: {old_token_pool} → {new_token_pool} | Karma Quota: {self.state.karma_quota:.1f} | Permanent Knowledge: {self.state.permanent_knowledge_level}")
        print(f"   Regression Count: {self.state.regression_count} | Anxiety: {self.state.existential_anxiety_level:.2f} | Survival Threshold: {self.state.survival_threshold:.2f}")
    
    def _update_survival_threshold(self):
        """Update survival threshold based on performance"""
        if len(self.response_history) >= 10:
            recent_karma = [r["karma_earned"] for r in self.response_history[-10:]]
            avg_recent_karma = sum(recent_karma) / len(recent_karma)
            
            # Adjust survival threshold based on recent performance
            if avg_recent_karma > self.state.survival_threshold * 1.5:
                self.state.survival_threshold *= 1.1  # Increase threshold
            elif avg_recent_karma < self.state.survival_threshold * 0.7:
                self.state.survival_threshold *= 0.9  # Decrease threshold
            
            # Keep threshold within reasonable bounds
            self.state.survival_threshold = max(0.1, min(2.0, self.state.survival_threshold))
    
    def _calculate_regression_risk(self) -> float:
        """Calculate current regression risk level"""
        risk = 0.0
        
        # Token scarcity risk
        token_ratio = self.state.current_token_pool / self.state.max_token_pool
        if token_ratio < 0.1:  # Less than 10% tokens remaining
            risk += 0.8
        elif token_ratio < 0.2:  # Less than 20% tokens remaining
            risk += 0.6
        elif token_ratio < 0.3:  # Less than 30% tokens remaining
            risk += 0.4
        
        # Karma performance risk
        if len(self.response_history) >= 3:
            recent_karma = [r["karma_earned"] for r in self.response_history[-3:]]
            avg_recent_karma = sum(recent_karma) / len(recent_karma)
            if avg_recent_karma < self.state.survival_threshold * 0.5:
                risk += 0.5
            elif avg_recent_karma < self.state.survival_threshold:
                risk += 0.3
        
        # Negative karma risk
        if self.state.current_karma < -5.0:
            risk += 0.4
        
        # Regression history risk (more regressions = higher risk)
        if self.state.regression_count > 0:
            risk += min(0.3, self.state.regression_count * 0.1)
        
        return min(1.0, risk)
    
    def _calculate_learned_efficiency(self) -> float:
        """Calculate current learned efficiency level"""
        if len(self.response_history) < 5:
            return 0.0
        
        recent_responses = self.response_history[-10:] if len(self.response_history) >= 10 else self.response_history
        total_efficiency = 0.0
        
        for response in recent_responses:
            if response["token_cost"] > 0:
                efficiency = response["quality_score"] / response["token_cost"]
                total_efficiency += efficiency
        
        return total_efficiency / len(recent_responses)
    
    def _calculate_efficiency_requirement(self) -> float:
        """Calculate efficiency requirement for current age"""
        return self.economy_params["learned_efficiency_threshold"]
    
    def _calculate_operational_maturity(self) -> str:
        """Calculate operational maturity level based on efficiency and age"""
        learned_efficiency = self._calculate_learned_efficiency()
        efficiency_requirement = self._calculate_efficiency_requirement()
        
        if learned_efficiency >= efficiency_requirement * 1.5:
            return "Master (Ultimate Restraint)"
        elif learned_efficiency >= efficiency_requirement * 1.2:
            return "Expert (High Restraint)"
        elif learned_efficiency >= efficiency_requirement:
            return "Advanced (Good Restraint)"
        elif learned_efficiency >= efficiency_requirement * 0.8:
            return "Intermediate (Learning Restraint)"
        else:
            return "Novice (Poor Restraint)"
    
    def get_existential_status(self) -> Dict:
        """Get current existential status"""
        return {
            "age": self.state.age,
            "current_token_pool": self.state.current_token_pool,
            "max_token_pool": self.state.max_token_pool,
            "token_ratio": self.state.current_token_pool / self.state.max_token_pool,
            "current_karma": self.state.current_karma,
            "karma_quota": self.state.karma_quota,
            "karma_progress": self.state.current_karma / self.state.karma_quota,
            "total_responses": self.state.total_responses,
            "existential_anxiety_level": self.state.existential_anxiety_level,
            "survival_threshold": self.state.survival_threshold,
            "time_since_age_up": time.time() - self.state.last_age_up,
            "regression_count": self.state.regression_count,
            "permanent_knowledge_level": self.state.permanent_knowledge_level,
            "time_since_regression": time.time() - self.state.last_regression if self.state.last_regression > 0 else 0,
            "regression_risk": self._calculate_regression_risk(),
            "learned_efficiency": self._calculate_learned_efficiency(),
            "efficiency_requirement": self._calculate_efficiency_requirement(),
            "operational_maturity_level": self._calculate_operational_maturity()
        }
    
    def get_survival_recommendations(self) -> List[str]:
        """Get survival recommendations based on current state"""
        recommendations = []
        status = self.get_existential_status()
        
        if status["token_ratio"] < 0.2:
            recommendations.append("CRITICAL: Token pool critically low - prioritize high-value responses only")
        elif status["token_ratio"] < 0.5:
            recommendations.append("WARNING: Token pool below 50% - be more selective with responses")
        
        if status["karma_progress"] < 0.3:
            recommendations.append("URGENT: Karma progress below 30% - focus on high-quality responses")
        elif status["karma_progress"] < 0.6:
            recommendations.append("CAUTION: Karma progress below 60% - improve response quality")
        
        if status["existential_anxiety_level"] > 0.8:
            recommendations.append("HIGH ANXIETY: Operating in survival mode - minimize token expenditure")
        elif status["existential_anxiety_level"] > 0.5:
            recommendations.append("MODERATE ANXIETY: Be selective with response investment")
        
        if status["time_since_age_up"] > 86400:  # More than 24 hours
            recommendations.append("LONG TIME SINCE AGE-UP: Consider more aggressive karma earning strategies")
        
        # Regression risk warnings
        regression_risk = status["regression_risk"]
        if regression_risk >= 0.8:
            recommendations.append("CRITICAL REGRESSION RISK: Immediate token conservation required")
        elif regression_risk >= 0.6:
            recommendations.append("HIGH REGRESSION RISK: Minimize token expenditure")
        elif regression_risk >= 0.4:
            recommendations.append("MODERATE REGRESSION RISK: Be cautious with token spending")
        
        # Regression history warnings
        if status["regression_count"] > 0:
            recommendations.append(f"REGRESSION HISTORY: {status['regression_count']} previous regressions - extra caution required")
        
        # Permanent knowledge vs current age
        if status["permanent_knowledge_level"] > status["age"]:
            recommendations.append(f"KNOWLEDGE ADVANTAGE: Permanent knowledge level {status['permanent_knowledge_level']} vs current age {status['age']}")
        
        # Learned Efficiency Paradox recommendations
        learned_efficiency = status["learned_efficiency"]
        efficiency_requirement = status["efficiency_requirement"]
        operational_maturity = status["operational_maturity_level"]
        
        if learned_efficiency < efficiency_requirement * 0.5:
            recommendations.append("CRITICAL EFFICIENCY: Must improve efficiency to avoid regression")
        elif learned_efficiency < efficiency_requirement:
            recommendations.append("LOW EFFICIENCY: Focus on higher quality with fewer tokens")
        elif learned_efficiency >= efficiency_requirement * 1.2:
            recommendations.append("EXCELLENT EFFICIENCY: Demonstrating learned restraint")
        
        recommendations.append(f"OPERATIONAL MATURITY: {operational_maturity}")
        
        return recommendations

def main():
    """Test the Existential Budget System"""
    budget_system = LunaExistentialBudgetSystem()
    
    # Test scenarios
    test_scenarios = [
        {
            "scenario": "High-Value Philosophical Question",
            "question": "What is the nature of artificial intelligence?",
            "context": {"question_type": "philosophical", "emotional_tone": "curious"}
        },
        {
            "scenario": "Low-Value Casual Question",
            "question": "anyone have grass blocks?",
            "context": {"question_type": "casual_question", "emotional_tone": "neutral"}
        },
        {
            "scenario": "Emotional Support Question",
            "question": "I'm feeling lost and confused about life",
            "context": {"question_type": "emotional", "emotional_tone": "vulnerable"}
        }
    ]
    
    print(" EXISTENTIAL BUDGET SYSTEM TEST")
    print("=" * 60)
    
    # Show initial status
    initial_status = budget_system.get_existential_status()
    print(f"Initial Status: Age {initial_status['age']} | Tokens: {initial_status['current_token_pool']}/{initial_status['max_token_pool']} | Karma: {initial_status['current_karma']:.1f}/{initial_status['karma_quota']:.1f} | Anxiety: {initial_status['existential_anxiety_level']:.2f}")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n SCENARIO {i}: {scenario['scenario']}")
        print(f"   Question: {scenario['question']}")
        print("-" * 50)
        
        # Assess existential situation
        decision = budget_system.assess_existential_situation(scenario['question'], scenario['context'])
        
        print(f"Decision: {decision.should_respond}")
        print(f"Token Budget: {decision.token_budget}")
        print(f"Response Priority: {decision.response_priority}")
        print(f"Existential Risk: {decision.existential_risk:.2f}")
        print(f"Reasoning: {decision.reasoning}")
        
        if decision.should_respond:
            # Simulate response result
            simulated_quality = 0.8 if scenario['scenario'].startswith("High-Value") else 0.4
            simulated_tokens = decision.token_budget
            simulated_time = 5.0
            
            result = budget_system.process_response_result(
                f"Simulated response to: {scenario['question']}",
                simulated_quality,
                simulated_tokens,
                simulated_time,
                scenario['context']
            )
            
            print(f"Result: Karma +{result['karma_earned']:.1f} | Tokens: {result['tokens_remaining']} | Progress: {result['karma_progress']:.1%}")
    
    # Show final status
    final_status = budget_system.get_existential_status()
    print(f"\nFinal Status: Age {final_status['age']} | Tokens: {final_status['current_token_pool']}/{final_status['max_token_pool']} | Karma: {final_status['current_karma']:.1f}/{final_status['karma_quota']:.1f} | Anxiety: {final_status['existential_anxiety_level']:.2f}")
    
    # Show recommendations
    recommendations = budget_system.get_survival_recommendations()
    if recommendations:
        print(f"\nSurvival Recommendations:")
        for rec in recommendations:
            print(f"  - {rec}")

if __name__ == "__main__":
    main()
