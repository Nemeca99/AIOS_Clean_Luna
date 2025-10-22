#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Luna Token-Time Econometric System
Implements Hard Constraint Econometric Model with Expiring Reward Function
"""

import time
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ResponseMetrics:
    """Metrics for a single response"""
    quality_score: float
    token_count: int
    generation_time: float
    timestamp: float
    response_text: str
    context: Dict

class LunaTokenTimeEconometricSystem:
    """
    Token-Time Econometric System for Hard Constraint Optimization
    
    Implements the Reward Function:
    Reward Score ∝ Quality Score / (Token Count × Generation Time)
    
    With Expiring Reward that decays over time to simulate attention span/fatigue
    """
    
    def __init__(self):
        # Reward function parameters
        self.reward_params = {
            "base_quality_weight": 1.0,
            "token_penalty_factor": 0.1,  # Penalty per token
            "time_penalty_factor": 0.05,  # Penalty per second
            "min_reward_threshold": 0.1,  # Minimum viable reward
            "max_reward_cap": 10.0  # Maximum possible reward
        }
        
        # Expiring reward parameters
        self.expiring_reward_params = {
            "decay_rate": 0.8,  # How fast reward decays (higher = faster decay)
            "attention_window": 5.0,  # Seconds before significant decay
            "fatigue_threshold": 10.0,  # Seconds before severe penalty
            "max_attention_span": 15.0  # Maximum attention before complete decay
        }
        
        # Token efficiency targets
        self.token_targets = {
            "casual_question": 8,  # Target tokens for casual questions
            "social_question": 12,  # Target tokens for social questions
            "philosophical_question": 20,  # Target tokens for philosophical questions
            "emotional_question": 15,  # Target tokens for emotional questions
            "direct_challenge": 10  # Target tokens for direct challenges
        }
        
        # Time efficiency targets
        self.time_targets = {
            "casual_question": 3.0,  # Target seconds for casual questions
            "social_question": 5.0,  # Target seconds for social questions
            "philosophical_question": 8.0,  # Target seconds for philosophical questions
            "emotional_question": 6.0,  # Target seconds for emotional questions
            "direct_challenge": 4.0  # Target seconds for direct challenges
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            "minimum_acceptable": 0.3,  # Below this = punishment
            "good": 0.6,  # Good quality threshold
            "high": 0.8,  # High quality threshold
            "maximum": 0.95  # Maximum quality threshold
        }
        
        # Learning parameters
        self.learning_params = {
            "reward_history_size": 100,  # Keep last 100 responses for learning
            "adaptation_rate": 0.1,  # How fast to adapt based on performance
            "exploration_rate": 0.05  # Random exploration to avoid local optima
        }
        
        # Response history for learning
        self.response_history: List[ResponseMetrics] = []
        
        # Performance tracking
        self.performance_metrics = {
            "total_responses": 0,
            "average_reward": 0.0,
            "average_quality": 0.0,
            "average_efficiency": 0.0,
            "reward_trend": 0.0  # Positive = improving, negative = declining
        }
    
    def calculate_reward_score(self, metrics: ResponseMetrics) -> float:
        """
        Calculate reward score using Token-Time Econometric Model
        
        Reward Score ∝ Quality Score / (Token Count × Generation Time)
        """
        quality = metrics.quality_score
        tokens = metrics.token_count
        time_taken = metrics.generation_time
        
        # Base reward calculation
        if tokens == 0 or time_taken == 0:
            return 0.0
        
        # Token-Time efficiency (TPS - Tokens Per Second)
        tps = tokens / time_taken
        
        # Base reward: Quality / Token-Time cost
        base_reward = quality / (tokens * time_taken)
        
        # Apply token penalty (prefer fewer tokens)
        token_penalty = 1.0 - (tokens * self.reward_params["token_penalty_factor"])
        token_penalty = max(0.1, token_penalty)  # Minimum penalty
        
        # Apply time penalty (prefer faster responses)
        time_penalty = 1.0 - (time_taken * self.reward_params["time_penalty_factor"])
        time_penalty = max(0.1, time_penalty)  # Minimum penalty
        
        # Calculate final reward
        final_reward = base_reward * token_penalty * time_penalty
        
        # Apply expiring reward based on time taken
        expiring_factor = self._calculate_expiring_reward_factor(time_taken)
        final_reward *= expiring_factor
        
        # Apply quality gates (prevent reward hacking)
        if quality < self.quality_thresholds["minimum_acceptable"]:
            final_reward *= 0.1  # Severe penalty for low quality
        
        # Cap the reward
        final_reward = min(final_reward, self.reward_params["max_reward_cap"])
        
        return max(final_reward, 0.0)
    
    def _calculate_expiring_reward_factor(self, time_taken: float) -> float:
        """Calculate expiring reward factor based on response time"""
        if time_taken <= self.expiring_reward_params["attention_window"]:
            # Within attention window - full reward
            return 1.0
        elif time_taken <= self.expiring_reward_params["fatigue_threshold"]:
            # Attention fading - exponential decay
            decay_time = time_taken - self.expiring_reward_params["attention_window"]
            decay_factor = math.exp(-self.expiring_reward_params["decay_rate"] * decay_time)
            return max(0.3, decay_factor)  # Minimum 30% reward
        else:
            # Severe fatigue - linear decay to zero
            fatigue_time = time_taken - self.expiring_reward_params["fatigue_threshold"]
            max_fatigue = self.expiring_reward_params["max_attention_span"] - self.expiring_reward_params["fatigue_threshold"]
            fatigue_factor = max(0.0, 1.0 - (fatigue_time / max_fatigue))
            return fatigue_factor * 0.3  # Maximum 30% of base reward
    
    def evaluate_response(self, response_text: str, quality_score: float, 
                         generation_time: float, context: Dict) -> Dict:
        """
        Evaluate a response using the Token-Time Econometric Model
        """
        # Count tokens (approximate)
        token_count = len(response_text.split())
        
        # Create metrics
        metrics = ResponseMetrics(
            quality_score=quality_score,
            token_count=token_count,
            generation_time=generation_time,
            timestamp=time.time(),
            response_text=response_text,
            context=context
        )
        
        # Calculate reward score
        reward_score = self.calculate_reward_score(metrics)
        
        # Get context-specific targets
        question_type = context.get('question_type', 'standard')
        token_target = self.token_targets.get(question_type, 15)
        time_target = self.time_targets.get(question_type, 6.0)
        
        # Calculate efficiency scores
        token_efficiency = max(0.0, 1.0 - abs(token_count - token_target) / token_target)
        time_efficiency = max(0.0, 1.0 - abs(generation_time - time_target) / time_target)
        overall_efficiency = (token_efficiency + time_efficiency) / 2.0
        
        # Calculate quality grade
        if quality_score >= self.quality_thresholds["maximum"]:
            quality_grade = "Maximum"
        elif quality_score >= self.quality_thresholds["high"]:
            quality_grade = "High"
        elif quality_score >= self.quality_thresholds["good"]:
            quality_grade = "Good"
        elif quality_score >= self.quality_thresholds["minimum_acceptable"]:
            quality_grade = "Acceptable"
        else:
            quality_grade = "Poor"
        
        # Calculate performance indicators
        performance_indicators = self._calculate_performance_indicators(metrics)
        
        # Update response history and performance metrics
        self._update_performance_tracking(metrics, reward_score)
        
        return {
            "reward_score": reward_score,
            "token_count": token_count,
            "generation_time": generation_time,
            "quality_score": quality_score,
            "quality_grade": quality_grade,
            "token_efficiency": token_efficiency,
            "time_efficiency": time_efficiency,
            "overall_efficiency": overall_efficiency,
            "token_target": token_target,
            "time_target": time_target,
            "expiring_factor": self._calculate_expiring_reward_factor(generation_time),
            "performance_indicators": performance_indicators,
            "recommendations": self._generate_recommendations(metrics, reward_score)
        }
    
    def _calculate_performance_indicators(self, metrics: ResponseMetrics) -> Dict:
        """Calculate performance indicators for learning"""
        question_type = metrics.context.get('question_type', 'standard')
        token_target = self.token_targets.get(question_type, 15)
        time_target = self.time_targets.get(question_type, 6.0)
        
        # Token performance
        token_deviation = abs(metrics.token_count - token_target)
        token_performance = "Optimal" if token_deviation <= 2 else "Suboptimal" if token_deviation <= 5 else "Poor"
        
        # Time performance
        time_deviation = abs(metrics.generation_time - time_target)
        time_performance = "Optimal" if time_deviation <= 1.0 else "Suboptimal" if time_deviation <= 2.0 else "Poor"
        
        # Quality performance
        quality_performance = "High" if metrics.quality_score >= 0.8 else "Good" if metrics.quality_score >= 0.6 else "Acceptable" if metrics.quality_score >= 0.3 else "Poor"
        
        # Overall performance
        if token_performance == "Optimal" and time_performance == "Optimal" and quality_performance in ["High", "Good"]:
            overall_performance = "Optimal"
        elif token_performance != "Poor" and time_performance != "Poor" and quality_performance != "Poor":
            overall_performance = "Good"
        else:
            overall_performance = "Needs Improvement"
        
        return {
            "token_performance": token_performance,
            "time_performance": time_performance,
            "quality_performance": quality_performance,
            "overall_performance": overall_performance,
            "token_deviation": token_deviation,
            "time_deviation": time_deviation
        }
    
    def _generate_recommendations(self, metrics: ResponseMetrics, reward_score: float) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        question_type = metrics.context.get('question_type', 'standard')
        token_target = self.token_targets.get(question_type, 15)
        time_target = self.time_targets.get(question_type, 6.0)
        
        # Token recommendations
        if metrics.token_count > token_target * 1.5:
            recommendations.append(f"Reduce verbosity: {metrics.token_count} tokens vs target {token_target}")
        elif metrics.token_count < token_target * 0.5:
            recommendations.append(f"Increase detail: {metrics.token_count} tokens vs target {token_target}")
        
        # Time recommendations
        if metrics.generation_time > time_target * 1.5:
            recommendations.append(f"Improve speed: {metrics.generation_time:.1f}s vs target {time_target:.1f}s")
        
        # Quality recommendations
        if metrics.quality_score < self.quality_thresholds["good"]:
            recommendations.append(f"Improve quality: {metrics.quality_score:.2f} vs target 0.6+")
        
        # Reward recommendations
        if reward_score < 1.0:
            recommendations.append("Optimize Token-Time efficiency for higher reward")
        
        return recommendations
    
    def _update_performance_tracking(self, metrics: ResponseMetrics, reward_score: float):
        """Update performance tracking and learning"""
        # Add to history
        self.response_history.append(metrics)
        
        # Keep only recent history
        if len(self.response_history) > self.learning_params["reward_history_size"]:
            self.response_history = self.response_history[-self.learning_params["reward_history_size"]:]
        
        # Update performance metrics
        self.performance_metrics["total_responses"] += 1
        
        # Calculate running averages
        total_rewards = sum(self.calculate_reward_score(m) for m in self.response_history)
        total_qualities = sum(m.quality_score for m in self.response_history)
        total_efficiencies = sum(
            (max(0.0, 1.0 - abs(m.token_count - self.token_targets.get(m.context.get('question_type', 'standard'), 15)) / 15) +
             max(0.0, 1.0 - abs(m.generation_time - self.time_targets.get(m.context.get('question_type', 'standard'), 6.0)) / 6.0)) / 2
            for m in self.response_history
        )
        
        self.performance_metrics["average_reward"] = total_rewards / len(self.response_history)
        self.performance_metrics["average_quality"] = total_qualities / len(self.response_history)
        self.performance_metrics["average_efficiency"] = total_efficiencies / len(self.response_history)
        
        # Calculate trend (last 10 vs previous 10)
        if len(self.response_history) >= 20:
            recent_rewards = [self.calculate_reward_score(m) for m in self.response_history[-10:]]
            previous_rewards = [self.calculate_reward_score(m) for m in self.response_history[-20:-10]]
            
            recent_avg = sum(recent_rewards) / len(recent_rewards)
            previous_avg = sum(previous_rewards) / len(previous_rewards)
            
            self.performance_metrics["reward_trend"] = recent_avg - previous_avg
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary"""
        return {
            "total_responses": self.performance_metrics["total_responses"],
            "average_reward": self.performance_metrics["average_reward"],
            "average_quality": self.performance_metrics["average_quality"],
            "average_efficiency": self.performance_metrics["average_efficiency"],
            "reward_trend": self.performance_metrics["reward_trend"],
            "performance_grade": self._calculate_performance_grade(),
            "optimization_status": self._get_optimization_status()
        }
    
    def _calculate_performance_grade(self) -> str:
        """Calculate overall performance grade"""
        avg_reward = self.performance_metrics["average_reward"]
        avg_quality = self.performance_metrics["average_quality"]
        avg_efficiency = self.performance_metrics["average_efficiency"]
        
        if avg_reward >= 2.0 and avg_quality >= 0.8 and avg_efficiency >= 0.8:
            return "A+ (Optimal)"
        elif avg_reward >= 1.5 and avg_quality >= 0.7 and avg_efficiency >= 0.7:
            return "A (High)"
        elif avg_reward >= 1.0 and avg_quality >= 0.6 and avg_efficiency >= 0.6:
            return "B (Good)"
        elif avg_reward >= 0.5 and avg_quality >= 0.4 and avg_efficiency >= 0.4:
            return "C (Acceptable)"
        else:
            return "D (Needs Improvement)"
    
    def _get_optimization_status(self) -> str:
        """Get optimization status and recommendations"""
        trend = self.performance_metrics["reward_trend"]
        
        if trend > 0.1:
            return "Improving - Continue current approach"
        elif trend > 0.0:
            return "Stable - Minor optimizations needed"
        elif trend > -0.1:
            return "Declining - Review token/time targets"
        else:
            return "Poor - Major optimization required"

def main():
    """Test the Token-Time Econometric System"""
    econometric_system = LunaTokenTimeEconometricSystem()
    
    # Test cases with different scenarios
    test_cases = [
        {
            "scenario": "Optimal Response",
            "response": "Obviously.",
            "quality_score": 0.8,
            "generation_time": 2.0,
            "context": {"question_type": "casual_question"}
        },
        {
            "scenario": "Verbose Response",
            "response": "I think that's a really interesting question, and I suppose it makes me feel curious about the nature of existence.",
            "quality_score": 0.9,
            "generation_time": 8.0,
            "context": {"question_type": "philosophical"}
        },
        {
            "scenario": "Fast but Poor Quality",
            "response": "Yes.",
            "quality_score": 0.2,
            "generation_time": 1.0,
            "context": {"question_type": "philosophical"}
        },
        {
            "scenario": "Slow but High Quality",
            "response": "The nature of artificial intelligence represents a profound intersection of computational architecture and emergent complexity.",
            "quality_score": 0.95,
            "generation_time": 12.0,
            "context": {"question_type": "philosophical"}
        }
    ]
    
    print(" TOKEN-TIME ECONOMETRIC SYSTEM TEST")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n TEST {i}: {test['scenario']}")
        print("-" * 50)
        
        evaluation = econometric_system.evaluate_response(
            test['response'],
            test['quality_score'],
            test['generation_time'],
            test['context']
        )
        
        print(f"Response: {test['response']}")
        print(f"Quality: {test['quality_score']:.2f} ({evaluation['quality_grade']})")
        print(f"Tokens: {evaluation['token_count']} (target: {evaluation['token_target']})")
        print(f"Time: {evaluation['generation_time']:.1f}s (target: {evaluation['time_target']:.1f}s)")
        print(f"Reward Score: {evaluation['reward_score']:.3f}")
        print(f"Token Efficiency: {evaluation['token_efficiency']:.2f}")
        print(f"Time Efficiency: {evaluation['time_efficiency']:.2f}")
        print(f"Overall Efficiency: {evaluation['overall_efficiency']:.2f}")
        print(f"Expiring Factor: {evaluation['expiring_factor']:.2f}")
        
        if evaluation['recommendations']:
            print("Recommendations:")
            for rec in evaluation['recommendations']:
                print(f"  - {rec}")
    
    # Performance summary
    print(f"\n PERFORMANCE SUMMARY")
    print("=" * 60)
    summary = econometric_system.get_performance_summary()
    print(f"Total Responses: {summary['total_responses']}")
    print(f"Average Reward: {summary['average_reward']:.3f}")
    print(f"Average Quality: {summary['average_quality']:.2f}")
    print(f"Average Efficiency: {summary['average_efficiency']:.2f}")
    print(f"Reward Trend: {summary['reward_trend']:+.3f}")
    print(f"Performance Grade: {summary['performance_grade']}")
    print(f"Optimization Status: {summary['optimization_status']}")

if __name__ == "__main__":
    main()
