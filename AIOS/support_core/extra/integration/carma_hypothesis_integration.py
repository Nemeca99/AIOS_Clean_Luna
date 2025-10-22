"""
CARMA Hypothesis Integration
Links QEC-inspired hypothesis testing to CARMA's learning and Luna's conversation system
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Add qec_integration to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'qec_integration'))

# Add provenance logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils_core'))
try:
    from provenance import get_hypothesis_logger, log_hypothesis_event
    PROVENANCE_AVAILABLE = True
except ImportError:
    PROVENANCE_AVAILABLE = False

try:
    from aios_hypothesis_tester import AIOSHypothesisTester, AIOSHypothesisData
    HYPOTHESIS_TESTER_AVAILABLE = True
except ImportError:
    HYPOTHESIS_TESTER_AVAILABLE = False
    print("⚠️ AIOS Hypothesis Tester not available")
    # Define stub classes for when hypothesis tester isn't available
    class AIOSHypothesisData:
        """Stub class for when hypothesis tester module is not available"""
        pass
    
    class AIOSHypothesisTester:
        """Stub class for when hypothesis tester module is not available"""
        def __init__(self, *args, **kwargs):
            pass

class CARMAHypothesisIntegration:
    """
    Integration layer between CARMA/Luna and hypothesis testing system
    Continuously validates Mathematical Conversation System hypotheses
    """
    
    def __init__(self, output_dir: str = "results/carma_hypotheses"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize hypothesis tester
        if HYPOTHESIS_TESTER_AVAILABLE:
            self.tester = AIOSHypothesisTester(logs_dir=str(self.output_dir))
            self.enabled = True
            print("✅ CARMA Hypothesis Integration initialized")
            print(f"   Testing {len(self.tester.hypotheses)} hypotheses")
        else:
            self.tester = None
            self.enabled = False
            print("⚠️ CARMA Hypothesis Integration disabled (tester not available)")
        
        # Conversation data buffer
        self.conversation_buffer = []
        self.buffer_size = 100  # Test after every 100 messages
        
        # Test results
        self.test_results = {}
        self.last_test_time = None
    
    def log_conversation_data(self, conversation_id: str, message_data: Dict[str, Any]):
        """
        Log conversation data for hypothesis testing
        Called by Luna's learning system after each message
        """
        if not self.enabled:
            return
        
        # Extract relevant data from message
        hypothesis_data = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "calculated_weight": message_data.get("calculated_weight", 0.495),
            "routing_decision": message_data.get("source", "main_model"),
            "response_time_ms": message_data.get("response_time_ms", 0),
            "complexity_score": message_data.get("question_complexity", 0.5),
            "engagement_score": message_data.get("user_engagement", 0.5),
            "fragments_retrieved": message_data.get("fragments_found", 0),
            "context_size": len(message_data.get("context_messages", [])),
            "quality_score": message_data.get("response_quality", 0.5)
        }
        
        # Add to buffer
        self.conversation_buffer.append(hypothesis_data)
        
        # Test hypotheses if buffer is full
        if len(self.conversation_buffer) >= self.buffer_size:
            self.run_hypothesis_tests()
    
    def run_hypothesis_tests(self) -> Dict[str, Any]:
        """
        Run all hypothesis tests on buffered conversation data
        """
        if not self.enabled or len(self.conversation_buffer) == 0:
            return {"status": "No data to test"}
        
        print(f"\n🧪 CARMA Hypothesis Testing - {len(self.conversation_buffer)} messages buffered")
        
        # Convert buffer to AIOSHypothesisData format
        hypothesis_data = self._convert_buffer_to_hypothesis_data()
        
        # Get provenance logger if available
        prov_logger = None
        if PROVENANCE_AVAILABLE:
            prov_logger = get_hypothesis_logger()
        
        # Test each hypothesis
        all_results = {}
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for hyp in self.tester.hypotheses:
            try:
                result = self.tester.test_hypothesis(hyp.id, hypothesis_data)
                all_results[hyp.id] = result
                
                # Store in CARMA for learning
                self._store_in_carma(hyp.id, result)
                
                # EMIT TO PROVENANCE LOG (CARMA EMITTER)
                if prov_logger:
                    log_hypothesis_event(
                        prov_logger,
                        conv_id=test_id,
                        hypo_id=hyp.id,
                        status='supported' if result.get('is_supported', False) else 'not_supported',
                        metric=result.get('metric_value', 0.0),
                        p_value=None,  # Can be calculated later
                        effect_size=result.get('confidence', 0.0),
                        rec=self._get_recommendation(hyp.id, result),
                        metadata={
                            'data_points': result.get('data_points', 0),
                            'threshold': result.get('threshold', 0.0),
                            'hypothesis_name': result.get('hypothesis_name', 'Unknown')
                        }
                    )
                
            except Exception as e:
                print(f"⚠️ Failed to test {hyp.id}: {e}")
                all_results[hyp.id] = {"error": str(e)}
        
        # Clear buffer after testing
        self.conversation_buffer = []
        self.last_test_time = datetime.now()
        
        # Save results
        self.test_results = all_results
        self._save_test_results(all_results)
        
        # Generate summary report
        self._print_hypothesis_summary(all_results)
        
        return all_results
    
    def _convert_buffer_to_hypothesis_data(self) -> List[AIOSHypothesisData]:
        """Convert conversation buffer to AIOSHypothesisData format"""
        # Group messages by conversation
        conversations = {}
        
        for msg in self.conversation_buffer:
            conv_id = msg["conversation_id"]
            if conv_id not in conversations:
                conversations[conv_id] = {
                    "messages": [],
                    "start_time": msg["timestamp"],
                    "end_time": msg["timestamp"]
                }
            conversations[conv_id]["messages"].append(msg)
            conversations[conv_id]["end_time"] = msg["timestamp"]
        
        # Convert to AIOSHypothesisData
        hypothesis_data = []
        
        for conv_id, conv in conversations.items():
            messages = conv["messages"]
            
            # Calculate duration
            start = datetime.fromisoformat(conv["start_time"])
            end = datetime.fromisoformat(conv["end_time"])
            duration = (end - start).total_seconds()
            
            data = AIOSHypothesisData(
                conversation_id=conv_id,
                timestamp=conv["start_time"],
                total_messages=len(messages),
                duration_seconds=duration,
                
                # Extract lists of metrics
                weight_calculations=[m["calculated_weight"] for m in messages],
                routing_decisions=[m["routing_decision"] for m in messages],
                response_times_ms=[m["response_time_ms"] for m in messages],
                complexity_scores=[m["complexity_score"] for m in messages],
                engagement_scores=[m["engagement_score"] for m in messages],
                
                # CARMA metrics
                fragments_retrieved=[m["fragments_retrieved"] for m in messages],
                context_sizes=[m["context_size"] for m in messages],
                memory_hits=sum(1 for m in messages if m["fragments_retrieved"] > 0),
                memory_misses=sum(1 for m in messages if m["fragments_retrieved"] == 0),
                
                # Hypothesis-specific data
                hypothesis_data={
                    "dreaming_average": sum(m["calculated_weight"] for m in messages) / len(messages) if messages else 0.495,
                    "avg_complexity": sum(m["complexity_score"] for m in messages) / len(messages) if messages else 0.5,
                    "avg_engagement": sum(m["engagement_score"] for m in messages) / len(messages) if messages else 0.5
                },
                
                # Per-message data
                per_message_data=messages
            )
            
            hypothesis_data.append(data)
        
        return hypothesis_data
    
    def _store_in_carma(self, hypothesis_id: str, result: Dict[str, Any]):
        """
        Store hypothesis test results in CARMA for learning
        This allows CARMA to adapt based on which hypotheses are supported
        """
        # Create CARMA fragment for hypothesis result
        fragment_data = {
            "fragment_type": "hypothesis_test_result",
            "hypothesis_id": hypothesis_id,
            "hypothesis_name": result.get("hypothesis_name", "Unknown"),
            "is_supported": result.get("is_supported", False),
            "metric_value": result.get("metric_value", 0.0),
            "confidence": result.get("confidence", 0.0),
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
            "data_points": result.get("data_points", 0)
        }
        
        # Save as CARMA-compatible fragment
        fragment_file = self.output_dir / f"carma_fragment_{hypothesis_id}.json"
        with open(fragment_file, 'w') as f:
            json.dump(fragment_data, f, indent=2)
        
        print(f"   📦 Stored {hypothesis_id} result in CARMA fragment")
    
    def _save_test_results(self, results: Dict[str, Any]):
        """Save hypothesis test results"""
        results_file = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _print_hypothesis_summary(self, results: Dict[str, Any]):
        """Print summary of hypothesis testing"""
        print(f"\n{'='*70}")
        print(f"CARMA HYPOTHESIS TESTING SUMMARY")
        print(f"{'='*70}")
        
        supported = sum(1 for r in results.values() if isinstance(r, dict) and r.get("is_supported", False))
        not_supported = sum(1 for r in results.values() if isinstance(r, dict) and not r.get("is_supported", False))
        errors = sum(1 for r in results.values() if isinstance(r, dict) and "error" in r)
        
        print(f"Total Hypotheses Tested: {len(results)}")
        print(f"  ✅ Supported: {supported}")
        print(f"  ❌ Not Supported: {not_supported}")
        print(f"  ⚠️ Errors: {errors}")
        print(f"\nDetailed Results:")
        
        for hyp_id, result in results.items():
            if isinstance(result, dict) and "is_supported" in result:
                status = "✅" if result["is_supported"] else "❌"
                metric_val = result.get("metric_value", 0.0)
                threshold = result.get("threshold", 0.0)
                confidence = result.get("confidence", 0.0)
                
                print(f"  {status} {hyp_id}: {result.get('hypothesis_name', 'Unknown')}")
                print(f"     Metric: {metric_val:.4f} (threshold: {threshold})")
                print(f"     Confidence: {confidence:.1%}")
        
        print(f"{'='*70}\n")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get learning insights from hypothesis testing for CARMA
        Returns actionable insights based on which hypotheses are supported
        """
        if not self.test_results:
            return {"status": "No hypothesis tests run yet"}
        
        insights = {
            "timestamp": datetime.now().isoformat(),
            "hypotheses_tested": len(self.test_results),
            "supported_hypotheses": [],
            "unsupported_hypotheses": [],
            "recommendations": []
        }
        
        for hyp_id, result in self.test_results.items():
            if isinstance(result, dict) and "is_supported" in result:
                if result["is_supported"]:
                    insights["supported_hypotheses"].append(hyp_id)
                    
                    # Generate recommendations based on supported hypotheses
                    if hyp_id == "H_AIOS_1":
                        insights["recommendations"].append("Weight-Quality correlation confirmed - continue using dynamic weighting")
                    elif hyp_id == "H_AIOS_3":
                        insights["recommendations"].append("Embedder is faster - increase embedder usage for simple queries")
                    elif hyp_id == "H_AIOS_5":
                        insights["recommendations"].append("CARMA fragments improve quality - prioritize fragment retrieval")
                    elif hyp_id == "H_AIOS_6":
                        insights["recommendations"].append("Dreaming equilibrium achieved - maintain current dreaming logic")
                else:
                    insights["unsupported_hypotheses"].append(hyp_id)
                    
                    # Generate recommendations based on unsupported hypotheses
                    if hyp_id == "H_AIOS_1":
                        insights["recommendations"].append("⚠️ Weight-Quality correlation weak - recalibrate weight calculation")
                    elif hyp_id == "H_AIOS_3":
                        insights["recommendations"].append("⚠️ Embedder not faster enough - optimize embedder calls")
                    elif hyp_id == "H_AIOS_5":
                        insights["recommendations"].append("⚠️ CARMA fragments not improving quality - improve fragment selection")
                    elif hyp_id == "H_AIOS_6":
                        insights["recommendations"].append("⚠️ Dreaming not converging - adjust dreaming algorithm")
        
        return insights
    
    def create_carma_learning_fragment(self) -> Dict[str, Any]:
        """
        Create a CARMA fragment from hypothesis testing results
        This allows CARMA to learn from hypothesis validation
        """
        insights = self.get_learning_insights()
        
        fragment = {
            "fragment_id": f"hypothesis_learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "fragment_type": "hypothesis_learning",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "hypotheses_tested": insights["hypotheses_tested"],
                "supported_count": len(insights["supported_hypotheses"]),
                "unsupported_count": len(insights["unsupported_hypotheses"]),
                "supported_hypotheses": insights["supported_hypotheses"],
                "unsupported_hypotheses": insights["unsupported_hypotheses"],
                "recommendations": insights["recommendations"]
            },
            "metadata": {
                "source": "carma_hypothesis_integration",
                "confidence": 0.95,  # High confidence in hypothesis test results
                "importance": "high",
                "learning_signal": True
            }
        }
        
        # Save fragment
        fragment_file = self.output_dir / f"{fragment['fragment_id']}.json"
        with open(fragment_file, 'w') as f:
            json.dump(fragment, f, indent=2)
        
        print(f"📦 Created CARMA learning fragment: {fragment['fragment_id']}")
        
        return fragment
    
    def _get_recommendation(self, hypo_id: str, result: Dict[str, Any]) -> str:
        """Generate recommendation based on hypothesis result"""
        if result.get('is_supported', False):
            recommendations = {
                'H_AIOS_1': 'Continue using dynamic weighting - quality correlation confirmed',
                'H_AIOS_2': 'Context pressure confirmed - optimize for speed',
                'H_AIOS_3': 'Embedder efficiency confirmed - increase simple query routing',
                'H_AIOS_4': 'Dynamic accumulation working - maintain current logic',
                'H_AIOS_5': 'CARMA advantage confirmed - prioritize fragment retrieval',
                'H_AIOS_6': 'Dreaming equilibrium achieved - maintain dreaming logic'
            }
        else:
            recommendations = {
                'H_AIOS_1': 'Weight-quality correlation weak - recalibrate weight formula',
                'H_AIOS_2': 'Context pressure not significant - review context handling',
                'H_AIOS_3': 'Embedder not fast enough - optimize embedder calls',
                'H_AIOS_4': 'Dynamic accumulation not working - review accumulation logic',
                'H_AIOS_5': 'CARMA not improving quality - improve fragment selection',
                'H_AIOS_6': 'Dreaming not converging - adjust dreaming algorithm'
            }
        
        return recommendations.get(hypo_id, 'No specific recommendation')

def integrate_with_luna_learning(luna_learning_system):
    """
    Integrate hypothesis testing with Luna's learning system
    Call this during Luna initialization
    """
    if not HYPOTHESIS_TESTER_AVAILABLE:
        print("⚠️ Cannot integrate hypothesis testing - tester not available")
        return None
    
    # Create CARMA hypothesis integration
    carma_hyp = CARMAHypothesisIntegration()
    
    # Add to Luna's learning system
    luna_learning_system.hypothesis_integration = carma_hyp
    
    print("✅ Hypothesis testing integrated with Luna's learning system")
    print("   Will automatically test hypotheses during conversations")
    
    return carma_hyp

def test_carma_hypothesis_integration():
    """Test CARMA hypothesis integration"""
    print("=== CARMA Hypothesis Integration Test ===\n")
    
    # Initialize integration
    carma_hyp = CARMAHypothesisIntegration()
    
    # Simulate conversation data
    print("\n📊 Simulating conversation data...")
    for i in range(10):
        message_data = {
            "calculated_weight": 0.495 + (i * 0.0001),  # Simulate weight variation
            "source": "main_model" if i % 3 == 0 else "embedder",
            "response_time_ms": 2000 if i % 3 == 0 else 500,  # Main model slower
            "question_complexity": 0.5 + (i * 0.05),
            "user_engagement": 0.4 + (i * 0.04),
            "fragments_found": i % 5,
            "context_messages": ["msg_" + str(j) for j in range(i % 3)],
            "response_quality": 0.6 + (i * 0.03)
        }
        
        carma_hyp.log_conversation_data(f"test_conv_{i // 3}", message_data)
    
    # Run hypothesis tests
    print("\n🧪 Running hypothesis tests...")
    results = carma_hyp.run_hypothesis_tests()
    
    # Get learning insights
    print("\n🧠 Generating learning insights for CARMA...")
    insights = carma_hyp.get_learning_insights()
    
    print("\n📦 Recommendations for CARMA:")
    for rec in insights.get("recommendations", []):
        print(f"   - {rec}")
    
    # Create CARMA learning fragment
    print("\n📦 Creating CARMA learning fragment...")
    fragment = carma_hyp.create_carma_learning_fragment()
    
    print("\n✅ CARMA Hypothesis Integration test complete!")
    print(f"   Tested {len(results)} hypotheses")
    print(f"   Generated {len(insights.get('recommendations', []))} recommendations")
    print(f"   Created learning fragment: {fragment['fragment_id']}")

if __name__ == "__main__":
    test_carma_hypothesis_integration()

