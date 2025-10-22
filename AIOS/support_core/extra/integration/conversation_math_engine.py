"""
CONVERSATION MATHEMATICAL ENGINE
================================

Mathematical system for conversation weight calculations using UML Calculator and RIS.
Implements the adaptive conversation system where weights determine embedder vs main model routing.

Based on Travis Miner's UML Calculator and RIS (Recursive Integration System).
"""

import sys
import os
import math
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

# Add UML Calculator to path
uml_path = os.path.join(os.path.dirname(__file__), 'Failed_Research', '03_UML', 'Jetbrains_Pycharm')
sys.path.insert(0, uml_path)

try:
    from uml_core import letter_to_number, parse_value, ris_meta_operator, recursive_compress
    UML_AVAILABLE = True
except ImportError:
    UML_AVAILABLE = False
    print("⚠️ UML Calculator not available - using fallback functions")

class ConversationMode(Enum):
    """Conversation modes based on mathematical weights"""
    DIRECT = "direct"        # ≤0.49 - Embedder (blunt, no-BS responses)
    ENGAGING = "engaging"    # >0.50 - Main Model (creative, dismissive approval)

@dataclass
class MessageWeight:
    """Mathematical weight for a single message"""
    question_complexity: float      # 0-1 scale
    response_quality: float         # 0-1 scale  
    user_engagement: float          # 0-1 scale
    calculated_weight: float        # Final weight (0.49-0.50 range)
    mode: ConversationMode          # Determined mode
    metadata: Dict[str, Any]        # Additional data

@dataclass
class ConversationContext:
    """Mathematical context for entire conversation"""
    message_weights: List[MessageWeight]
    current_weight: float            # Running average weight
    depth_preference: float          # User's preferred depth (0.001-0.0000000001)
    conversation_mode: ConversationMode
    total_messages: int
    engagement_trend: float          # Trend in engagement over time

class ConversationMathEngine:
    """
    Mathematical engine for conversation weight calculations.
    Uses UML Calculator and RIS for text quantification and weight processing.
    """
    
    def __init__(self, base_depth: float = 0.001):
        self.base_depth = base_depth  # Base adjustment amount
        self.context = ConversationContext(
            message_weights=[],
            current_weight=0.495,  # Start at midpoint
            depth_preference=base_depth,
            conversation_mode=ConversationMode.DIRECT,
            total_messages=0,
            engagement_trend=0.0
        )
        
    def calculate_question_complexity(self, question: str) -> float:
        """Calculate question complexity using UML letter-to-number conversion"""
        if not UML_AVAILABLE:
            # Fallback: simple word count and character analysis
            words = len(question.split())
            chars = len(question)
            technical_terms = sum(1 for word in question.lower().split() 
                                if word in ['how', 'why', 'what', 'explain', 'analyze', 'compare'])
            return min(1.0, (words * 0.3 + chars * 0.1 + technical_terms * 0.4) / 10)
        
        try:
            # Use UML Calculator to quantify text
            question_lower = question.lower().replace(' ', '')
            
            # Convert letters to numbers and calculate complexity
            letter_values = []
            for char in question_lower:
                if char.isalpha():
                    letter_values.append(letter_to_number(char))
            
            if not letter_values:
                return 0.1  # Default for non-alphabetic
            
            # Calculate complexity using RIS meta-operator
            complexity_sum = 0
            for i in range(len(letter_values) - 1):
                result, _ = ris_meta_operator(letter_values[i], letter_values[i + 1])
                if isinstance(result, (int, float)):
                    complexity_sum += result
            
            # Normalize to 0-1 scale
            complexity = min(1.0, complexity_sum / (len(letter_values) * 10))
            return complexity
            
        except Exception as e:
            print(f"Error calculating complexity: {e}")
            return 0.5  # Default complexity
    
    def calculate_response_quality(self, response: str, user_followup: Optional[str] = None) -> float:
        """Calculate response quality based on user engagement indicators"""
        if not user_followup:
            return 0.5  # Default quality if no followup
        
        # Analyze user followup for engagement indicators
        followup_lower = user_followup.lower()
        
        # Positive engagement indicators
        positive_indicators = [
            'yes', 'yeah', 'right', 'exactly', 'continue', 'more', 'tell me',
            'interesting', 'good', 'thanks', 'thank you', 'helpful'
        ]
        
        # Negative engagement indicators  
        negative_indicators = [
            'no', 'wrong', 'stop', 'enough', 'boring', 'confusing', 'unclear'
        ]
        
        # Calculate engagement score
        positive_score = sum(1 for indicator in positive_indicators if indicator in followup_lower)
        negative_score = sum(1 for indicator in negative_indicators if indicator in followup_lower)
        
        # Response length indicates engagement
        length_score = min(1.0, len(user_followup) / 50)  # Longer responses = more engagement
        
        # Combine scores
        quality = (positive_score * 0.4 + length_score * 0.3 - negative_score * 0.3 + 0.5)
        return max(0.0, min(1.0, quality))
    
    def calculate_user_engagement(self, message: str, message_history: List[str]) -> float:
        """Calculate user engagement based on message characteristics"""
        # Message length indicates engagement
        length_score = min(1.0, len(message) / 100)
        
        # Question marks indicate curiosity
        question_score = min(1.0, message.count('?') * 0.3)
        
        # Exclamation marks indicate enthusiasm
        enthusiasm_score = min(1.0, message.count('!') * 0.2)
        
        # Continuation probability based on history
        continuation_score = 0.5
        if message_history:
            recent_lengths = [len(msg) for msg in message_history[-3:]]
            avg_recent_length = sum(recent_lengths) / len(recent_lengths)
            if len(message) > avg_recent_length * 1.2:
                continuation_score = 0.8  # Increasing engagement
            elif len(message) < avg_recent_length * 0.8:
                continuation_score = 0.2  # Decreasing engagement
        
        # Combine engagement factors
        engagement = (length_score * 0.3 + question_score * 0.3 + 
                     enthusiasm_score * 0.2 + continuation_score * 0.2)
        
        return max(0.0, min(1.0, engagement))
    
    def calculate_message_weight(self, question: str, response: str = "", 
                               user_followup: str = "", message_history: List[str] = None) -> MessageWeight:
        """Calculate mathematical weight for a single message"""
        if message_history is None:
            message_history = []
        
        # Calculate component scores
        complexity = self.calculate_question_complexity(question)
        quality = self.calculate_response_quality(response, user_followup)
        engagement = self.calculate_user_engagement(question, message_history)
        
        # Calculate raw weight using RIS meta-operator
        if UML_AVAILABLE:
            try:
                # Use RIS to combine complexity and quality
                combined_score, _ = ris_meta_operator(complexity, quality)
                if isinstance(combined_score, (int, float)):
                    raw_weight = (combined_score + engagement) / 2
                else:
                    raw_weight = (complexity + quality + engagement) / 3
            except Exception as e:
                raw_weight = (complexity + quality + engagement) / 3
        else:
            raw_weight = (complexity + quality + engagement) / 3
        
        # Apply depth preference and ensure bounds
        # Scale the raw weight to fit in the 0.49-0.50 range
        # Map 0-1 scale to 0.49-0.50 range with more sensitivity to complexity
        calculated_weight = 0.49 + (raw_weight * 0.01) + (complexity * 0.005)
        
        # Apply small adjustment based on quality and complexity
        adjustment = self.base_depth * quality * complexity
        
        # Apply adjustment but keep within bounds
        calculated_weight += adjustment
        if calculated_weight > 0.50:
            calculated_weight = 0.495  # Reset to middle
        elif calculated_weight < 0.49:
            calculated_weight = 0.495  # Reset to middle
        
        # Determine conversation mode
        mode = ConversationMode.ENGAGING if calculated_weight > 0.495 else ConversationMode.DIRECT
        
        return MessageWeight(
            question_complexity=complexity,
            response_quality=quality,
            user_engagement=engagement,
            calculated_weight=calculated_weight,
            mode=mode,
            metadata={
                'raw_weight': raw_weight,
                'adjustment': adjustment,
                'question_length': len(question),
                'response_length': len(response)
            }
        )
    
    def update_conversation_context(self, message_weight: MessageWeight):
        """Update the conversation context with new message weight"""
        self.context.message_weights.append(message_weight)
        self.context.total_messages += 1
        
        # Calculate running average weight
        weights = [mw.calculated_weight for mw in self.context.message_weights]
        self.context.current_weight = sum(weights) / len(weights)
        
        # Determine overall conversation mode
        if self.context.current_weight > 0.495:
            self.context.conversation_mode = ConversationMode.ENGAGING
        else:
            self.context.conversation_mode = ConversationMode.DIRECT
        
        # Calculate engagement trend
        if len(weights) >= 3:
            recent_weights = weights[-3:]
            older_weights = weights[-6:-3] if len(weights) >= 6 else weights[:-3]
            if older_weights:
                self.context.engagement_trend = (sum(recent_weights) / len(recent_weights)) - (sum(older_weights) / len(older_weights))
    
    def should_use_main_model(self, question: str, custom_boundary: float = 0.5) -> Tuple[bool, MessageWeight]:
        """
        Determine if question should use main model or embedder
        
        Args:
            question: The question to evaluate
            custom_boundary: Custom routing boundary (default 0.5, can be adjusted by adaptive routing)
        
        Returns:
            Tuple of (use_main_model, message_weight)
        """
        message_weight = self.calculate_message_weight(question)
        self.update_conversation_context(message_weight)
        
        # Use custom boundary for adaptive routing (default 0.5)
        # Adjust threshold slightly below boundary to account for floating point precision
        threshold = custom_boundary - 0.005
        use_main_model = message_weight.calculated_weight > threshold
        
        return use_main_model, message_weight
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get mathematical summary of conversation"""
        if not self.context.message_weights:
            return {"status": "No messages yet"}
        
        weights = [mw.calculated_weight for mw in self.context.message_weights]
        
        return {
            "total_messages": self.context.total_messages,
            "current_weight": self.context.current_weight,
            "conversation_mode": self.context.conversation_mode.value,
            "weight_range": f"{min(weights):.6f} - {max(weights):.6f}",
            "engagement_trend": self.context.engagement_trend,
            "depth_preference": self.context.depth_preference,
            "recent_mode_changes": len([mw for mw in self.context.message_weights[-5:] 
                                      if mw.mode != self.context.conversation_mode])
        }

def test_conversation_math_engine():
    """Test the conversation mathematical engine"""
    print("=== CONVERSATION MATHEMATICAL ENGINE TEST ===")
    
    engine = ConversationMathEngine(base_depth=0.001)
    
    # Test questions
    test_questions = [
        "hi",  # Simple greeting
        "How are you?",  # Moderate complexity
        "Explain quantum computing in simple terms",  # High complexity
        "What's your name?",  # Simple question
        "Can you help me understand machine learning algorithms?",  # High complexity
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n--- Message {i+1}: '{question}' ---")
        
        use_main_model, weight = engine.should_use_main_model(question)
        
        print(f"Question Complexity: {weight.question_complexity:.3f}")
        print(f"User Engagement: {weight.user_engagement:.3f}")
        print(f"Calculated Weight: {weight.calculated_weight:.6f}")
        print(f"Mode: {weight.mode.value}")
        print(f"Use Main Model: {use_main_model}")
        
        # Show conversation summary
        summary = engine.get_conversation_summary()
        print(f"Current Weight: {summary['current_weight']:.6f}")
        print(f"Conversation Mode: {summary['conversation_mode']}")
    
    print(f"\n=== FINAL CONVERSATION SUMMARY ===")
    final_summary = engine.get_conversation_summary()
    for key, value in final_summary.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_conversation_math_engine()
