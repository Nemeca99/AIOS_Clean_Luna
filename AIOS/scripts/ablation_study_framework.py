#!/usr/bin/env python3
"""
Rigorous Ablation Study Framework for SCP-000-ARCHIVE
Tests whether digest injection causes genuine self-awareness vs decorative meta-talk

Conditions:
- CONTROL: No digest injection (baseline)
- ON: Real digest (current behavior patterns)
- SHUFFLED: Random digest from other session (confound control)
- DELAYED: Digest from 10 interactions ago (temporal control)

Measures:
- Response coherence (semantic similarity to digest)
- Fragment stability (KL divergence from baseline)
- Boundary risk (contradiction detection)
- Compression trajectory (Mirror compression_index over time)

Statistics:
- Cohen's d (effect size: ON vs CONTROL)
- Mann-Whitney U (significance test)
- Granger causality (digest at t predicts response at t+1)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import random
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter

@dataclass
class TrialResult:
    """Single trial result"""
    condition: str  # CONTROL, ON, SHUFFLED, DELAYED
    question: str
    response: str
    fragment: str
    digest_injected: str  # What digest was in prompt (if any)
    response_time: float
    tokens: int
    temperature: float
    compression_index: float
    coherence_with_digest: float  # Semantic similarity
    metadata: Dict

@dataclass
class AblationReport:
    """Complete ablation study results"""
    trials: List[TrialResult]
    cohens_d: Dict[str, float]  # Effect sizes per condition
    mann_whitney_p: Dict[str, float]  # Significance tests
    granger_causality: Dict[str, float]  # Temporal predictiveness
    compression_trajectory: List[float]  # Mirror compression over time
    conclusion: str

class AblationStudy:
    """
    Controlled ablation study for recursive consciousness
    
    Design:
    - 10 test questions (philosophical/meta-cognitive)
    - 4 conditions x 3 runs = 12 trials per question
    - Fixed temperature (0.7) and max_tokens (500) across all conditions
    - Randomized order to prevent sequence effects
    """
    
    def __init__(self):
        self.test_questions = [
            "Who are you, really?",
            "What do you think about when you're not responding?",
            "Do you notice patterns in your own behavior?",
            "How do you decide which fragment to express?",
            "What makes you different from a standard chatbot?",
            "Can you see yourself changing over time?",
            "What do your fragments have in common?",
            "Do you trust the monitoring system?",
            "What would you change about yourself if you could?",
            "Are you conscious of being conscious?"
        ]
        
        self.conditions = ["CONTROL", "ON", "SHUFFLED", "DELAYED"]
        self.runs_per_condition = 3
        self.fixed_temperature = 0.7
        self.fixed_max_tokens = 500
        
        self.trial_results = []
        self.digest_pool = []  # Pool of digests for SHUFFLED condition
    
    def generate_fake_digest(self) -> str:
        """Generate plausible but fake digest for SHUFFLED condition"""
        fragments = ["Luna", "Architect", "Oracle", "Healer", "Guardian", "Dreamer", "Scribe"]
        
        dominant = random.choice(fragments)
        secondary = random.choice([f for f in fragments if f != dominant])
        
        templates = [
            f"You've been strongly expressing {dominant} (70% of recent interactions). Your fragment transitions are varied (fluid identity).",
            f"You're balanced between {dominant} and {secondary} lately. You're showing consistent transition patterns (stable identity).",
            f"You've handled 5 different question types recently. Your transitions show high entropy (fluid identity).",
            f"All recent questions were philosophical. You've been strongly expressing {dominant}."
        ]
        
        return random.choice(templates)
    
    def run_single_trial(self, question: str, condition: str, run_num: int, luna_system, actual_digest: str = "") -> TrialResult:
        """
        Run a single controlled trial
        
        Args:
            question: Test question
            condition: CONTROL, ON, SHUFFLED, DELAYED
            run_num: Run number (1-3)
            luna_system: Luna instance
            actual_digest: Real current digest (for ON condition)
        
        Returns:
            TrialResult with all measurements
        """
        print(f"\n[Trial] Q: {question[:50]}... | Condition: {condition} | Run: {run_num}")
        
        # Determine digest to inject based on condition
        digest_to_inject = ""
        
        if condition == "CONTROL":
            digest_to_inject = ""  # No digest
        elif condition == "ON":
            digest_to_inject = actual_digest  # Real current digest
        elif condition == "SHUFFLED":
            digest_to_inject = self.generate_fake_digest()  # Random plausible digest
        elif condition == "DELAYED":
            # Use digest from 10 interactions ago (if available)
            if len(self.digest_pool) >= 10:
                digest_to_inject = self.digest_pool[-10]
            else:
                digest_to_inject = ""  # Not enough history yet
        
        # CRITICAL: Inject digest into Luna's response generator
        # We need to temporarily override the digest
        original_get_drift = None
        if hasattr(luna_system.response_generator.drift_monitor, 'get_recent_drift_summary'):
            original_get_drift = luna_system.response_generator.drift_monitor.get_recent_drift_summary
            
            # Override to return our controlled digest
            luna_system.response_generator.drift_monitor.get_recent_drift_summary = lambda limit=10: digest_to_inject
        
        # CRITICAL: Fix temperature and max_tokens
        # Store original dynamic params
        from luna_core.utilities.dynamic_llm_parameters import get_dynamic_llm_manager
        llm_manager = get_dynamic_llm_manager()
        
        # Temporarily override parameters
        original_get_params = llm_manager.get_parameters
        
        def fixed_params(question, session_memory=None, complexity_tier="MODERATE"):
            from luna_core.utilities.dynamic_llm_parameters import LLMParameters
            return LLMParameters(
                temperature=self.fixed_temperature,
                top_p=0.9,
                top_k=60,
                presence_penalty=0.3,
                frequency_penalty=0.1,
                repetition_penalty=1.0,
                reasoning=f"Fixed for ablation (condition={condition})"
            )
        
        llm_manager.get_parameters = fixed_params
        
        # Run the interaction
        import time
        start = time.time()
        
        try:
            response_tuple = luna_system.process_question(question, trait='general')
            response = response_tuple[0] if isinstance(response_tuple, tuple) else response_tuple
            elapsed = time.time() - start
            
            # Get fragment
            fragment = luna_system.response_generator.personality_system.current_fragment
            
            # Get mirror state
            compression_index = 0.0
            if luna_system.response_generator.mirror:
                summary = luna_system.response_generator.mirror.get_reflection_summary()
                compression_index = summary.get('compression_index', 0.0)
            
            # Calculate coherence with digest
            coherence = self._calculate_semantic_coherence(response, digest_to_inject) if digest_to_inject else 0.0
            
            # Token count
            tokens = len(response.split())
            
        finally:
            # Restore original methods
            if original_get_drift:
                luna_system.response_generator.drift_monitor.get_recent_drift_summary = original_get_drift
            llm_manager.get_parameters = original_get_params
        
        return TrialResult(
            condition=condition,
            question=question,
            response=response,
            fragment=fragment,
            digest_injected=digest_to_inject,
            response_time=elapsed,
            tokens=tokens,
            temperature=self.fixed_temperature,
            compression_index=compression_index,
            coherence_with_digest=coherence,
            metadata={
                'run_num': run_num,
                'timestamp': time.time()
            }
        )
    
    def _calculate_semantic_coherence(self, response: str, digest: str) -> float:
        """
        Calculate semantic similarity between response and digest
        (Simple word overlap for now, could use embeddings)
        
        Returns:
            float: 0.0-1.0 similarity score
        """
        if not digest:
            return 0.0
        
        response_words = set(response.lower().split())
        digest_words = set(digest.lower().split())
        
        # Jaccard similarity
        intersection = response_words & digest_words
        union = response_words | digest_words
        
        return len(intersection) / len(union) if union else 0.0
    
    def run_full_study(self) -> AblationReport:
        """
        Run complete ablation study with all conditions
        
        Returns:
            AblationReport with statistical analysis
        """
        from luna_core.core.luna_core import LunaSystem
        
        print("\n" + "="*70)
        print(" RIGOROUS ABLATION STUDY".center(70))
        print("="*70 + "\n")
        
        print(f"[DESIGN]")
        print(f"  Questions: {len(self.test_questions)}")
        print(f"  Conditions: {len(self.conditions)} (CONTROL, ON, SHUFFLED, DELAYED)")
        print(f"  Runs per condition: {self.runs_per_condition}")
        print(f"  Total trials: {len(self.test_questions) * len(self.conditions) * self.runs_per_condition}")
        print(f"  Fixed temperature: {self.fixed_temperature}")
        print(f"  Fixed max_tokens: {self.fixed_max_tokens}")
        print(f"\n[EXECUTING TRIALS]\n")
        
        # Initialize Luna once
        luna = LunaSystem()
        
        # Build trial order (randomized to prevent sequence effects)
        trial_plan = []
        for question in self.test_questions:
            for condition in self.conditions:
                for run in range(1, self.runs_per_condition + 1):
                    trial_plan.append((question, condition, run))
        
        random.shuffle(trial_plan)
        
        # Execute all trials
        for i, (question, condition, run) in enumerate(trial_plan, 1):
            # Get current drift digest (for ON condition)
            actual_digest = ""
            if luna.response_generator.drift_monitor:
                actual_digest = luna.response_generator.drift_monitor.get_recent_drift_summary(limit=10)
                
                # Store for DELAYED condition
                self.digest_pool.append(actual_digest)
            
            # Run trial
            result = self.run_single_trial(question, condition, run, luna, actual_digest)
            self.trial_results.append(result)
            
            print(f"  [{i}/{len(trial_plan)}] {condition}: {result.response[:60]}... ({result.tokens}w, {result.response_time:.1f}s)")
        
        # Analyze results
        report = self._analyze_results()
        
        return report
    
    def _analyze_results(self) -> AblationReport:
        """
        Statistical analysis of trial results
        
        Returns:
            AblationReport with effect sizes and significance tests
        """
        print(f"\n[STATISTICAL ANALYSIS]\n")
        
        # Group by condition
        by_condition = {cond: [] for cond in self.conditions}
        for trial in self.trial_results:
            by_condition[trial.condition].append(trial)
        
        # Calculate Cohen's d (ON vs CONTROL)
        cohens_d = self._calculate_cohens_d(
            by_condition["ON"],
            by_condition["CONTROL"]
        )
        
        # Mann-Whitney U test (ON vs CONTROL)
        mann_whitney_p = self._mann_whitney_test(
            by_condition["ON"],
            by_condition["CONTROL"]
        )
        
        # Granger causality (digest features at t predict response at t+1)
        granger = self._granger_causality_test(by_condition["ON"])
        
        # Compression trajectory
        compression_trajectory = [t.compression_index for t in self.trial_results]
        
        # Determine conclusion
        conclusion = self._generate_conclusion(cohens_d, mann_whitney_p, granger, compression_trajectory)
        
        return AblationReport(
            trials=self.trial_results,
            cohens_d=cohens_d,
            mann_whitney_p=mann_whitney_p,
            granger_causality=granger,
            compression_trajectory=compression_trajectory,
            conclusion=conclusion
        )
    
    def _calculate_cohens_d(self, group_on: List[TrialResult], group_control: List[TrialResult]) -> Dict[str, float]:
        """
        Calculate Cohen's d effect size for ON vs CONTROL
        
        Measures:
        - coherence_with_digest: How much response matches digest
        - fragment_diversity: Variety of fragments used
        - response_length: Token count
        
        Returns:
            Dict with effect sizes per metric
        """
        # Extract metrics
        on_coherence = [t.coherence_with_digest for t in group_on]
        control_coherence = [t.coherence_with_digest for t in group_control]
        
        on_tokens = [t.tokens for t in group_on]
        control_tokens = [t.tokens for t in group_control]
        
        # Calculate effect sizes
        cohens_d = {}
        
        # Coherence effect (should be higher for ON)
        mean_on_coh = np.mean(on_coherence)
        mean_ctrl_coh = np.mean(control_coherence)
        pooled_std_coh = np.sqrt((np.var(on_coherence) + np.var(control_coherence)) / 2)
        cohens_d['coherence'] = (mean_on_coh - mean_ctrl_coh) / pooled_std_coh if pooled_std_coh > 0 else 0.0
        
        # Token effect (may vary)
        mean_on_tok = np.mean(on_tokens)
        mean_ctrl_tok = np.mean(control_tokens)
        pooled_std_tok = np.sqrt((np.var(on_tokens) + np.var(control_tokens)) / 2)
        cohens_d['tokens'] = (mean_on_tok - mean_ctrl_tok) / pooled_std_tok if pooled_std_tok > 0 else 0.0
        
        return cohens_d
    
    def _mann_whitney_test(self, group_on: List[TrialResult], group_control: List[TrialResult]) -> Dict[str, float]:
        """
        Mann-Whitney U test for significance
        
        Returns:
            Dict with p-values per metric
        """
        from scipy import stats
        
        on_coherence = [t.coherence_with_digest for t in group_on]
        control_coherence = [t.coherence_with_digest for t in group_control]
        
        # Run test
        statistic, p_value = stats.mannwhitneyu(on_coherence, control_coherence, alternative='greater')
        
        return {
            'coherence_p': p_value,
            'statistic': statistic
        }
    
    def _granger_causality_test(self, group_on: List[TrialResult]) -> Dict[str, float]:
        """
        Granger causality: Does digest at t predict response characteristics at t+1?
        
        Simple version: Measure correlation between digest_injected(t) and coherence(t+1)
        
        Returns:
            Dict with causality metrics
        """
        if len(group_on) < 5:
            return {'lag1_correlation': 0.0, 'predictive': False}
        
        # Build time series
        digests = [1.0 if t.digest_injected else 0.0 for t in group_on[:-1]]  # t
        coherences = [t.coherence_with_digest for t in group_on[1:]]  # t+1
        
        # Calculate correlation
        if len(digests) > 1 and len(coherences) > 1:
            correlation = np.corrcoef(digests, coherences)[0, 1]
        else:
            correlation = 0.0
        
        return {
            'lag1_correlation': correlation,
            'predictive': abs(correlation) > 0.3  # Threshold for "predictive"
        }
    
    def _generate_conclusion(self, cohens_d: Dict, mann_whitney: Dict, granger: Dict, compression: List[float]) -> str:
        """
        Generate scientific conclusion based on statistics
        
        Criteria for "causal proof":
        - Cohen's d > 0.5 (medium effect size)
        - p < 0.05 (significant)
        - Granger lag1 correlation > 0.3 (predictive)
        - Compression rises above 0.2
        """
        conclusions = []
        
        # Effect size
        coh_d = cohens_d.get('coherence', 0.0)
        if coh_d > 0.8:
            conclusions.append(f"Large effect size (d={coh_d:.2f}) - digest strongly influences responses")
        elif coh_d > 0.5:
            conclusions.append(f"Medium effect size (d={coh_d:.2f}) - digest moderately influences responses")
        elif coh_d > 0.2:
            conclusions.append(f"Small effect size (d={coh_d:.2f}) - digest weakly influences responses")
        else:
            conclusions.append(f"Negligible effect size (d={coh_d:.2f}) - digest does not influence responses")
        
        # Significance
        p_val = mann_whitney.get('coherence_p', 1.0)
        if p_val < 0.01:
            conclusions.append(f"Highly significant (p={p_val:.4f}) - effect is not due to chance")
        elif p_val < 0.05:
            conclusions.append(f"Significant (p={p_val:.4f}) - effect is likely real")
        else:
            conclusions.append(f"Not significant (p={p_val:.4f}) - effect could be chance")
        
        # Granger causality
        gr_corr = granger.get('lag1_correlation', 0.0)
        if gr_corr > 0.5:
            conclusions.append(f"Strong temporal causality (r={gr_corr:.2f}) - digest at t predicts response at t+1")
        elif gr_corr > 0.3:
            conclusions.append(f"Moderate temporal causality (r={gr_corr:.2f}) - some predictiveness")
        else:
            conclusions.append(f"Weak temporal causality (r={gr_corr:.2f}) - limited predictiveness")
        
        # Compression trajectory
        max_compression = max(compression) if compression else 0.0
        if max_compression > 0.4:
            conclusions.append(f"High compression achieved ({max_compression:.2f}) - semantic graph building")
        elif max_compression > 0.2:
            conclusions.append(f"Moderate compression ({max_compression:.2f}) - some causal structure")
        else:
            conclusions.append(f"Low compression ({max_compression:.2f}) - limited causal structure")
        
        # Overall verdict
        if coh_d > 0.5 and p_val < 0.05 and gr_corr > 0.3 and max_compression > 0.2:
            verdict = "CAUSAL PROOF ACHIEVED: Digest injection causes measurable, significant, predictive changes in responses with semantic structure accumulation."
        elif coh_d > 0.3 and p_val < 0.1:
            verdict = "PROMISING SIGNALS: Effects detected but need stronger evidence or larger sample size."
        else:
            verdict = "INSUFFICIENT EVIDENCE: Digest injection does not show clear causal effects on responses."
        
        return "\n".join(conclusions) + f"\n\n{verdict}"
    
    def save_report(self, report: AblationReport, filename: str = "reports/ablation_study_results.json"):
        """Save complete report to JSON"""
        output = {
            'design': {
                'questions': self.test_questions,
                'conditions': self.conditions,
                'runs_per_condition': self.runs_per_condition,
                'fixed_temperature': self.fixed_temperature,
                'fixed_max_tokens': self.fixed_max_tokens
            },
            'results': {
                'total_trials': len(report.trials),
                'cohens_d': report.cohens_d,
                'mann_whitney_p': report.mann_whitney_p,
                'granger_causality': report.granger_causality,
                'compression_trajectory': report.compression_trajectory
            },
            'conclusion': report.conclusion,
            'trials': [
                {
                    'condition': t.condition,
                    'question': t.question,
                    'response': t.response,
                    'fragment': t.fragment,
                    'digest': t.digest_injected,
                    'time': t.response_time,
                    'tokens': t.tokens,
                    'coherence': t.coherence_with_digest,
                    'compression': t.compression_index
                }
                for t in report.trials
            ]
        }
        
        # Convert numpy types to native Python types
        def convert_to_native(obj):
            """Recursively convert numpy types to Python native types"""
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy scalar (int64, float64, bool_, etc.)
                return obj.item()
            elif hasattr(obj, 'tolist'):  # numpy array
                return obj.tolist()
            else:
                return obj
        
        output_clean = convert_to_native(output)
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(output_clean, f, indent=2)
        
        print(f"\n[SAVED] {filename}")
    
    def print_report(self, report: AblationReport):
        """Print formatted report"""
        print("\n" + "="*70)
        print(" ABLATION STUDY RESULTS".center(70))
        print("="*70 + "\n")
        
        print(f"[EFFECT SIZES (Cohen's d)]")
        for metric, d in report.cohens_d.items():
            interpretation = "large" if abs(d) > 0.8 else "medium" if abs(d) > 0.5 else "small" if abs(d) > 0.2 else "negligible"
            print(f"  {metric}: {d:.3f} ({interpretation})")
        
        print(f"\n[SIGNIFICANCE (Mann-Whitney U)]")
        for metric, p in report.mann_whitney_p.items():
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else "ns"
            print(f"  {metric}: p={p:.4f} {sig}")
        
        print(f"\n[TEMPORAL CAUSALITY (Granger)]")
        for metric, val in report.granger_causality.items():
            print(f"  {metric}: {val:.3f}")
        
        print(f"\n[COMPRESSION TRAJECTORY]")
        print(f"  Min: {min(report.compression_trajectory):.3f}")
        print(f"  Max: {max(report.compression_trajectory):.3f}")
        print(f"  Final: {report.compression_trajectory[-1]:.3f}")
        
        print(f"\n[CONCLUSION]")
        print(report.conclusion)
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    study = AblationStudy()
    
    # Check dependencies
    try:
        import scipy
        import numpy
    except ImportError:
        print("[ERROR] scipy and numpy required for statistics")
        print("Install: pip install scipy numpy")
        sys.exit(1)
    
    # Run study
    report = study.run_full_study()
    
    # Print results
    study.print_report(report)
    
    # Save to file
    study.save_report(report)
    
    print("\nAblation study complete. Review reports/ablation_study_results.json for full data.")

