"""
AIOS Hypothesis Tester (Adapted from QEC)
Test hypotheses about the Mathematical Conversation System and CARMA learning
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime

@dataclass
class AIOSHypothesis:
    """Hypothesis definition for AIOS testing"""
    id: str
    name: str
    prediction: str
    data_needed: List[str]
    metric: str
    threshold: float
    status: str = "untested"
    
@dataclass
class AIOSHypothesisData:
    """Data collected for AIOS hypothesis testing"""
    # Basic conversation info
    conversation_id: str
    timestamp: str
    total_messages: int
    duration_seconds: float
    
    # Mathematical Conversation System metrics
    weight_calculations: List[float]
    routing_decisions: List[str]  # 'embedder' or 'main_model'
    response_times_ms: List[float]
    complexity_scores: List[float]
    engagement_scores: List[float]
    
    # CARMA metrics
    fragments_retrieved: List[int]
    context_sizes: List[int]
    memory_hits: int
    memory_misses: int
    
    # Hypothesis-specific data
    hypothesis_data: Dict[str, Any]
    
    # Per-message data
    per_message_data: List[Dict[str, Any]]

class AIOSHypothesisTester:
    """
    Test hypotheses about AIOS Mathematical Conversation System
    Adapted from QEC's battle-tested hypothesis testing framework
    """
    
    def __init__(self, logs_dir: str = "results/aios_hypotheses"):
        self.logs_dir = logs_dir
        self.results = []
        self.hypothesis_metrics = {}
        
        # Create logs directory
        os.makedirs(logs_dir, exist_ok=True)
        
        # Define AIOS hypotheses
        self.hypotheses = self._define_aios_hypotheses()
        
        # Initialize hypothesis tracking
        for hyp in self.hypotheses:
            self.hypothesis_metrics[hyp.id] = {
                "status": "untested",
                "data_collected": 0,
                "metrics_calculated": 0,
                "last_updated": None,
                "results": []
            }
    
    def _define_aios_hypotheses(self) -> List[AIOSHypothesis]:
        """Define testable hypotheses for AIOS"""
        return [
            AIOSHypothesis(
                id="H_AIOS_1",
                name="Weight-Quality Correlation",
                prediction="Higher calculated weight correlates with better response quality",
                data_needed=["calculated_weight", "response_quality_score"],
                metric="Pearson correlation coefficient",
                threshold=0.7  # Strong positive correlation expected
            ),
            AIOSHypothesis(
                id="H_AIOS_2",
                name="Context Pressure Effect",
                prediction="More context messages increases response time",
                data_needed=["context_message_count", "response_time_ms"],
                metric="Linear regression slope",
                threshold=0.5  # Moderate positive correlation expected
            ),
            AIOSHypothesis(
                id="H_AIOS_3",
                name="Embedder Efficiency",
                prediction="Embedder responses are >= 2x faster than main model",
                data_needed=["response_time_embedder", "response_time_main"],
                metric="Speed ratio",
                threshold=2.0  # 2x faster expected
            ),
            AIOSHypothesis(
                id="H_AIOS_4",
                name="Dynamic Weight Accumulation",
                prediction="Same question + different context yields different routing",
                data_needed=["question_text", "context_messages", "routing_decision"],
                metric="Routing variance per question",
                threshold=0.3  # 30% variance expected
            ),
            AIOSHypothesis(
                id="H_AIOS_5",
                name="CARMA Memory Advantage",
                prediction="More CARMA fragments retrieved improves response quality",
                data_needed=["fragments_retrieved", "response_quality_score"],
                metric="Pearson correlation coefficient",
                threshold=0.6  # Moderate-strong positive correlation expected
            ),
            AIOSHypothesis(
                id="H_AIOS_6",
                name="Dreaming Weight Equilibrium",
                prediction="Dreaming system converges to equilibrium weight (0.495)",
                data_needed=["dreaming_average_weights"],
                metric="Convergence to 0.495",
                threshold=0.01  # Within 0.01 of 0.495
            )
        ]
    
    def test_hypothesis(self, hypothesis_id: str, conversation_data: List[AIOSHypothesisData]) -> Dict[str, Any]:
        """Test a specific hypothesis with collected data"""
        hypothesis = self._get_hypothesis(hypothesis_id)
        
        if not hypothesis:
            return {"error": f"Hypothesis {hypothesis_id} not found"}
        
        print(f"\n=== Testing {hypothesis.id}: {hypothesis.name} ===")
        print(f"Prediction: {hypothesis.prediction}")
        print(f"Metric: {hypothesis.metric}")
        print(f"Threshold: {hypothesis.threshold}")
        print(f"Data points: {len(conversation_data)}")
        
        # Extract data based on hypothesis needs
        test_data = self._extract_hypothesis_data(hypothesis, conversation_data)
        
        # Calculate metric
        metric_result = self._calculate_metric(hypothesis, test_data)
        
        # Determine if hypothesis is supported
        is_supported = self._evaluate_hypothesis(hypothesis, metric_result)
        
        # Update tracking
        self.hypothesis_metrics[hypothesis_id]["status"] = "tested"
        self.hypothesis_metrics[hypothesis_id]["data_collected"] = len(conversation_data)
        self.hypothesis_metrics[hypothesis_id]["last_updated"] = datetime.now().isoformat()
        self.hypothesis_metrics[hypothesis_id]["results"].append({
            "timestamp": datetime.now().isoformat(),
            "metric_value": metric_result,
            "is_supported": is_supported,
            "data_points": len(conversation_data)
        })
        
        result = {
            "hypothesis_id": hypothesis_id,
            "hypothesis_name": hypothesis.name,
            "prediction": hypothesis.prediction,
            "metric": hypothesis.metric,
            "threshold": hypothesis.threshold,
            "metric_value": metric_result,
            "is_supported": is_supported,
            "data_points": len(conversation_data),
            "confidence": self._calculate_confidence(test_data, metric_result),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save result
        self._save_hypothesis_result(hypothesis_id, result)
        
        # Print result
        self._print_hypothesis_result(result)
        
        return result
    
    def _get_hypothesis(self, hypothesis_id: str) -> Optional[AIOSHypothesis]:
        """Get hypothesis by ID"""
        for hyp in self.hypotheses:
            if hyp.id == hypothesis_id:
                return hyp
        return None
    
    def _extract_hypothesis_data(self, hypothesis: AIOSHypothesis, 
                                 conversation_data: List[AIOSHypothesisData]) -> Dict[str, List]:
        """Extract relevant data for hypothesis testing"""
        extracted = {field: [] for field in hypothesis.data_needed}
        
        for conv_data in conversation_data:
            # Extract data based on field names
            if "calculated_weight" in hypothesis.data_needed:
                extracted["calculated_weight"].extend(conv_data.weight_calculations)
            
            if "response_quality_score" in hypothesis.data_needed:
                # Calculate quality score from multiple factors
                quality_scores = self._calculate_quality_scores(conv_data)
                extracted["response_quality_score"].extend(quality_scores)
            
            if "context_message_count" in hypothesis.data_needed:
                extracted["context_message_count"].extend(conv_data.context_sizes)
            
            if "response_time_ms" in hypothesis.data_needed:
                extracted["response_time_ms"].extend(conv_data.response_times_ms)
            
            if "response_time_embedder" in hypothesis.data_needed:
                embedder_times = [rt for rt, rd in zip(conv_data.response_times_ms, conv_data.routing_decisions) if rd == 'embedder']
                extracted["response_time_embedder"].extend(embedder_times)
            
            if "response_time_main" in hypothesis.data_needed:
                main_times = [rt for rt, rd in zip(conv_data.response_times_ms, conv_data.routing_decisions) if rd == 'main_model']
                extracted["response_time_main"].extend(main_times)
            
            if "fragments_retrieved" in hypothesis.data_needed:
                extracted["fragments_retrieved"].extend(conv_data.fragments_retrieved)
            
            if "dreaming_average_weights" in hypothesis.data_needed:
                if "dreaming_average" in conv_data.hypothesis_data:
                    extracted["dreaming_average_weights"].append(conv_data.hypothesis_data["dreaming_average"])
        
        return extracted
    
    def _calculate_quality_scores(self, conv_data: AIOSHypothesisData) -> List[float]:
        """Calculate response quality scores from conversation data"""
        # Simple quality scoring based on available metrics
        quality_scores = []
        
        for i in range(len(conv_data.response_times_ms)):
            # Quality factors:
            # - Response time (faster is better, but not too fast)
            # - Complexity (appropriate complexity is better)
            # - Engagement (higher engagement is better)
            
            time_score = 1.0 - min(conv_data.response_times_ms[i] / 10000.0, 1.0)  # Normalize to 0-1
            complexity_score = conv_data.complexity_scores[i] if i < len(conv_data.complexity_scores) else 0.5
            engagement_score = conv_data.engagement_scores[i] if i < len(conv_data.engagement_scores) else 0.5
            
            # Weighted average
            quality = (time_score * 0.3 + complexity_score * 0.35 + engagement_score * 0.35)
            quality_scores.append(quality)
        
        return quality_scores
    
    def _calculate_metric(self, hypothesis: AIOSHypothesis, test_data: Dict[str, List]) -> float:
        """Calculate the metric for hypothesis testing"""
        metric_name = hypothesis.metric.lower()
        
        if "correlation" in metric_name:
            # Pearson correlation
            x = test_data[hypothesis.data_needed[0]]
            y = test_data[hypothesis.data_needed[1]]
            
            if len(x) == 0 or len(y) == 0:
                return 0.0
            
            # Ensure same length
            min_len = min(len(x), len(y))
            x = x[:min_len]
            y = y[:min_len]
            
            correlation = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0.0
            return float(correlation)
        
        elif "slope" in metric_name or "regression" in metric_name:
            # Linear regression slope
            x = test_data[hypothesis.data_needed[0]]
            y = test_data[hypothesis.data_needed[1]]
            
            if len(x) == 0 or len(y) == 0:
                return 0.0
            
            min_len = min(len(x), len(y))
            x = x[:min_len]
            y = y[:min_len]
            
            if len(x) > 1:
                slope, _ = np.polyfit(x, y, 1)
                return float(slope)
            return 0.0
        
        elif "ratio" in metric_name:
            # Calculate ratio
            x = test_data[hypothesis.data_needed[0]]
            y = test_data[hypothesis.data_needed[1]]
            
            if len(x) == 0 or len(y) == 0:
                return 0.0
            
            avg_x = np.mean(x)
            avg_y = np.mean(y)
            
            if avg_x == 0:
                return 0.0
            
            ratio = avg_y / avg_x
            return float(ratio)
        
        elif "convergence" in metric_name:
            # Check convergence to target value
            values = test_data[hypothesis.data_needed[0]]
            
            if len(values) == 0:
                return 1.0  # Max deviation
            
            target = 0.495  # Target equilibrium weight
            avg_deviation = np.mean([abs(v - target) for v in values])
            return float(avg_deviation)
        
        elif "variance" in metric_name:
            # Calculate variance
            values = test_data[hypothesis.data_needed[0]]
            
            if len(values) == 0:
                return 0.0
            
            variance = np.var(values)
            return float(variance)
        
        return 0.0
    
    def _evaluate_hypothesis(self, hypothesis: AIOSHypothesis, metric_result: float) -> bool:
        """Evaluate if hypothesis is supported by metric result"""
        metric_name = hypothesis.metric.lower()
        
        if "correlation" in metric_name or "slope" in metric_name:
            # For correlations and slopes, check if above threshold
            return abs(metric_result) >= hypothesis.threshold
        
        elif "ratio" in metric_name:
            # For ratios, check if meets or exceeds threshold
            return metric_result >= hypothesis.threshold
        
        elif "convergence" in metric_name:
            # For convergence, check if deviation is below threshold
            return metric_result <= hypothesis.threshold
        
        elif "variance" in metric_name:
            # For variance, check if above threshold (we expect variance)
            return metric_result >= hypothesis.threshold
        
        return False
    
    def _calculate_confidence(self, test_data: Dict[str, List], metric_result: float) -> float:
        """Calculate confidence level in the result"""
        # Simple confidence based on data points
        total_points = sum(len(v) for v in test_data.values())
        
        if total_points < 10:
            return 0.1
        elif total_points < 50:
            return 0.5
        elif total_points < 100:
            return 0.7
        elif total_points < 500:
            return 0.85
        else:
            return 0.95
    
    def _save_hypothesis_result(self, hypothesis_id: str, result: Dict[str, Any]):
        """Save hypothesis test result to file"""
        filename = os.path.join(self.logs_dir, f"{hypothesis_id}_results.json")
        
        # Load existing results
        existing_results = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_results = json.load(f)
        
        # Append new result
        existing_results.append(result)
        
        # Save
        with open(filename, 'w') as f:
            json.dump(existing_results, f, indent=2)
    
    def _print_hypothesis_result(self, result: Dict[str, Any]):
        """Print hypothesis test result"""
        print(f"\n{'='*60}")
        print(f"HYPOTHESIS TEST RESULT: {result['hypothesis_id']}")
        print(f"{'='*60}")
        print(f"Name: {result['hypothesis_name']}")
        print(f"Prediction: {result['prediction']}")
        print(f"\nMETRIC: {result['metric']}")
        print(f"  Threshold: {result['threshold']}")
        print(f"  Measured:  {result['metric_value']:.4f}")
        print(f"\nRESULT: {'✅ SUPPORTED' if result['is_supported'] else '❌ NOT SUPPORTED'}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Data Points: {result['data_points']}")
        print(f"{'='*60}\n")
    
    def generate_hypothesis_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive hypothesis testing report"""
        report = []
        report.append("# AIOS Hypothesis Testing Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        report.append(f"\n## Summary")
        report.append(f"Total Hypotheses: {len(self.hypotheses)}")
        
        tested = sum(1 for h in self.hypothesis_metrics.values() if h["status"] == "tested")
        report.append(f"Tested: {tested}")
        report.append(f"Untested: {len(self.hypotheses) - tested}")
        
        report.append(f"\n## Hypothesis Status\n")
        
        for hyp in self.hypotheses:
            metrics = self.hypothesis_metrics[hyp.id]
            report.append(f"### {hyp.id}: {hyp.name}")
            report.append(f"- **Status**: {metrics['status']}")
            report.append(f"- **Prediction**: {hyp.prediction}")
            report.append(f"- **Metric**: {hyp.metric}")
            report.append(f"- **Threshold**: {hyp.threshold}")
            report.append(f"- **Data Collected**: {metrics['data_collected']} points")
            
            if metrics["results"]:
                latest = metrics["results"][-1]
                report.append(f"- **Latest Result**: {'✅ SUPPORTED' if latest['is_supported'] else '❌ NOT SUPPORTED'}")
                report.append(f"  - Metric Value: {latest['metric_value']:.4f}")
                report.append(f"  - Timestamp: {latest['timestamp']}")
            
            report.append("")
        
        report_text = "\n".join(report)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text
    
    def get_hypothesis_status(self) -> Dict[str, Any]:
        """Get current status of all hypotheses"""
        return {
            "total_hypotheses": len(self.hypotheses),
            "tested": sum(1 for h in self.hypothesis_metrics.values() if h["status"] == "tested"),
            "untested": sum(1 for h in self.hypothesis_metrics.values() if h["status"] == "untested"),
            "hypotheses": self.hypothesis_metrics
        }

def main():
    """Example usage"""
    print("=== AIOS Hypothesis Tester ===")
    print("Adapted from QEC's battle-tested hypothesis testing framework\n")
    
    tester = AIOSHypothesisTester()
    
    print(f"Defined {len(tester.hypotheses)} testable hypotheses:")
    for hyp in tester.hypotheses:
        print(f"  - {hyp.id}: {hyp.name}")
    
    print("\n✅ AIOS Hypothesis Tester initialized and ready!")
    print("   Link this to CARMA's learning system for continuous hypothesis testing!")

if __name__ == "__main__":
    main()

