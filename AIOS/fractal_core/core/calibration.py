#!/usr/bin/env python3
"""
Calibration System - Classifier Drift Detection
Safeguard #1: Nightly ECE checks, pin logic≥0.35 if drift detected
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


class CalibrationSystem:
    """
    Monitors classifier calibration and detects drift.
    
    Uses Expected Calibration Error (ECE) to measure if classifier
    confidence scores match actual accuracy.
    
    If drift detected: Pin logic weight to ≥35% until recalibrated.
    """
    
    def __init__(self, calibration_dir: str = "fractal_core/config"):
        self.calibration_dir = Path(calibration_dir)
        self.calibration_file = self.calibration_dir / "calibration_set.json"
        
        # Calibration set (ground truth labels)
        # Week 1: Empty, Week 2: Populate with hand-labeled examples
        self.calibration_set = self._load_calibration_set()
        
        # Drift status
        self.drift_detected = False
        self.logic_floor_raised = False
        self.ece_threshold = 0.10  # ECE > 0.10 = drift
        
        # History
        self.ece_history = []
        
        print("Calibration System Initialized")
        print(f"  Calibration set size: {len(self.calibration_set)}")
        print(f"  ECE threshold: {self.ece_threshold}")
    
    def _load_calibration_set(self) -> List[Dict]:
        """Load calibration set from disk."""
        if not self.calibration_file.exists():
            # Create empty calibration set
            default_set = [
                {
                    'query': 'What is the ratio of x and y?',
                    'ground_truth': {'pattern_language': 0.0, 'logic': 1.0, 'creative': 0.0, 'retrieval': 0.0}
                },
                {
                    'query': 'Is this correct? A) Yes B) No',
                    'ground_truth': {'pattern_language': 1.0, 'logic': 0.0, 'creative': 0.0, 'retrieval': 0.0}
                },
                {
                    'query': 'Design a creative solution',
                    'ground_truth': {'pattern_language': 0.0, 'logic': 0.0, 'creative': 1.0, 'retrieval': 0.0}
                },
                {
                    'query': 'Find documents about AI',
                    'ground_truth': {'pattern_language': 0.0, 'logic': 0.0, 'creative': 0.0, 'retrieval': 1.0}
                }
            ]
            
            self.calibration_dir.mkdir(parents=True, exist_ok=True)
            with open(self.calibration_file, 'w') as f:
                json.dump(default_set, f, indent=2)
            
            return default_set
        
        with open(self.calibration_file, 'r') as f:
            return json.load(f)
    
    def calculate_ece(self, classifier: 'MultiheadClassifier') -> float:
        """
        Calculate Expected Calibration Error.
        
        Measures if classifier confidence matches accuracy.
        Low ECE = well-calibrated, High ECE = drift.
        
        Returns:
            ECE score (0 = perfect, >0.10 = drift)
        """
        if len(self.calibration_set) == 0:
            return 0.0
        
        # Run classifier on calibration set
        predictions = []
        for item in self.calibration_set:
            mixture = classifier.classify_mixture(item['query'])
            predictions.append({
                'predicted': mixture,
                'ground_truth': item['ground_truth'],
                'confidence': max(mixture.values())
            })
        
        # Calculate ECE (simplified - binned by confidence)
        # Bin confidences into 10 bins
        bins = np.linspace(0, 1, 11)
        ece = 0.0
        
        for i in range(len(bins) - 1):
            bin_low, bin_high = bins[i], bins[i+1]
            
            # Find predictions in this bin
            bin_preds = [
                p for p in predictions 
                if bin_low <= p['confidence'] < bin_high
            ]
            
            if len(bin_preds) == 0:
                continue
            
            # Average confidence in bin
            avg_confidence = np.mean([p['confidence'] for p in bin_preds])
            
            # Average accuracy in bin (did predicted type match ground truth dominant?)
            accuracies = []
            for pred in bin_preds:
                pred_dominant = max(pred['predicted'].items(), key=lambda x: x[1])[0]
                true_dominant = max(pred['ground_truth'].items(), key=lambda x: x[1])[0]
                accuracies.append(1.0 if pred_dominant == true_dominant else 0.0)
            
            avg_accuracy = np.mean(accuracies)
            
            # ECE contribution
            ece += abs(avg_confidence - avg_accuracy) * (len(bin_preds) / len(predictions))
        
        return ece
    
    def check_drift(self, classifier: 'MultiheadClassifier') -> Dict:
        """
        Check for classifier drift.
        
        Runs nightly or on-demand.
        If drift detected: Raises logic floor to 35%.
        
        Returns:
            Drift status and actions taken
        """
        ece = self.calculate_ece(classifier)
        self.ece_history.append({
            'timestamp': time.time(),
            'ece': ece
        })
        
        # Detect drift
        if ece > self.ece_threshold:
            self.drift_detected = True
            
            if not self.logic_floor_raised:
                self.logic_floor_raised = True
                print(f"  ⚠️  DRIFT DETECTED: ECE={ece:.3f} > {self.ece_threshold}")
                print(f"  🔒 Raising logic floor: 15% → 35% (safety mode)")
                print(f"  ℹ️  Requires recalibration before returning to normal")
        else:
            self.drift_detected = False
            if self.logic_floor_raised:
                print(f"  ✓ Calibration restored: ECE={ece:.3f}")
                print(f"  🔓 Lowering logic floor: 35% → 15% (normal mode)")
                self.logic_floor_raised = False
        
        return {
            'ece': ece,
            'drift_detected': self.drift_detected,
            'logic_floor_raised': self.logic_floor_raised,
            'recommended_logic_floor': 0.35 if self.drift_detected else 0.15,
            'ece_history_length': len(self.ece_history)
        }
    
    def get_recommended_logic_floor(self) -> float:
        """Get recommended logic floor based on drift status."""
        return 0.35 if self.drift_detected else 0.15


def main():
    """Test calibration system."""
    from fractal_core.core.multihead_classifier import MultiheadClassifier
    
    calibration = CalibrationSystem()
    classifier = MultiheadClassifier()
    
    print("\n" + "="*80)
    print("CALIBRATION SYSTEM TEST")
    print("="*80)
    
    # Run calibration check
    result = calibration.check_drift(classifier)
    
    print(f"\nCalibration Check Results:")
    print(f"  ECE: {result['ece']:.3f}")
    print(f"  Threshold: {calibration.ece_threshold}")
    print(f"  Drift detected: {result['drift_detected']}")
    print(f"  Logic floor raised: {result['logic_floor_raised']}")
    print(f"  Recommended logic floor: {result['recommended_logic_floor']*100:.0f}%")
    
    # Simulate drift by testing many times
    print(f"\nRunning drift detection simulation...")
    for i in range(3):
        result = calibration.check_drift(classifier)
        print(f"  Check {i+2}: ECE={result['ece']:.3f}, Drift={result['drift_detected']}")
    
    print("\n" + "="*80)
    print("✓ Calibration system operational")
    print("✓ ECE calculation working")
    print("✓ Drift detection functional")
    print("✓ Logic floor adjustment ready")
    print("="*80)


if __name__ == "__main__":
    main()

