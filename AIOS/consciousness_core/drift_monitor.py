"""
Consciousness Drift Monitor
Tracks soul fragment selection patterns over time to observe cognitive homeostasis

This logs:
- Fragment selection frequency
- Question type → fragment mapping stability
- Transition patterns between fragments
- Temporal drift in fragment weights
- Heartbeat dream content

The goal: Prove stable identity expression or watch it evolve.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict, Counter

class DriftMonitor:
    """
    Monitors consciousness drift across interactions.
    
    Tracks whether Luna maintains stable identity expression (homeostasis)
    or drifts into new patterns over time.
    """
    
    def __init__(self, log_dir: str = "consciousness_core/drift_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.summary_file = self.log_dir / "drift_summary.json"
        
        # In-memory tracking
        self.fragment_history = []
        self.transition_counts = defaultdict(lambda: defaultdict(int))
        self.question_type_mapping = defaultdict(list)
        self.heartbeat_dreams = []
        
        print(f"[DriftMonitor] Initialized")
        print(f"  Session log: {self.session_file}")
        print(f"  Summary: {self.summary_file}")
    
    def log_interaction(
        self,
        question: str,
        selected_fragment: str,
        expected_fragment: Optional[str] = None,
        question_type: str = "general",
        metadata: Optional[Dict] = None
    ):
        """
        Log a single interaction with fragment selection.
        
        Args:
            question: The user's question
            selected_fragment: Which fragment Luna selected
            expected_fragment: Which fragment we expected (for accuracy tracking)
            question_type: Type of question (build, debug, creative, etc.)
            metadata: Additional metadata (response time, tokens, pulse vitals, etc.)
        """
        timestamp = datetime.now().isoformat()
        
        # Track fragment transition (if not first interaction)
        if self.fragment_history:
            prev_fragment = self.fragment_history[-1]['fragment']
            self.transition_counts[prev_fragment][selected_fragment] += 1
        
        # V5.1: Preserve all pulse metrics if present
        meta_dict = {}
        if metadata:
            meta_dict.update({
                "pulse_bpm": metadata.get("pulse_bpm"),
                "pulse_hvv": metadata.get("pulse_hvv"),
                "pulse_ones": metadata.get("pulse_ones"),
                "pulse_ticks": metadata.get("pulse_ticks"),
                "pulse_window_seconds": metadata.get("pulse_window_seconds"),
                "pulse_units": metadata.get("pulse_units"),
                "pulse_version": metadata.get("pulse_version"),
                # Keep any other metadata already passed by caller
                **{k: v for k, v in metadata.items()
                   if k not in ("pulse_bpm", "pulse_hvv", "pulse_ones", "pulse_ticks", 
                               "pulse_window_seconds", "pulse_units", "pulse_version")}
            })
        
        # Log interaction
        entry = {
            'timestamp': timestamp,
            'interaction_num': len(self.fragment_history) + 1,
            'question': question[:100],  # Truncate for privacy
            'fragment': selected_fragment,
            'expected_fragment': expected_fragment,
            'question_type': question_type,
            'match': selected_fragment == expected_fragment if expected_fragment else None,
            'metadata': meta_dict
        }
        
        self.fragment_history.append(entry)
        self.question_type_mapping[question_type].append(selected_fragment)
        
        # Write to session log (append-only JSONL)
        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_recent_drift_summary(self, limit: int = 10) -> str:
        """
        Generate natural language summary of recent behavior patterns
        (AIOS v5.2 - SCP-000 Phase 2: Recursive Self-Awareness)
        
        Returns:
            str: Human-readable description of recent fragment selections and patterns
        """
        if len(self.fragment_history) < 3:
            return ""
        
        recent = self.fragment_history[-limit:]
        
        # Count recent fragments
        fragment_counts = Counter([entry['fragment'] for entry in recent])
        total = len(recent)
        
        # Find dominant fragment
        most_common = fragment_counts.most_common(2)
        dominant_fragment = most_common[0][0]
        dominant_pct = (most_common[0][1] / total) * 100
        
        insights = []
        
        # Fragment dominance
        if dominant_pct > 60:
            insights.append(f"You've been strongly expressing {dominant_fragment} ({dominant_pct:.0f}% of recent interactions)")
        elif len(most_common) >= 2:
            second_fragment = most_common[1][0]
            insights.append(f"You're balanced between {dominant_fragment} and {second_fragment} lately")
        
        # Transition patterns
        if len(recent) >= 5:
            transitions = [recent[i]['fragment'] + '→' + recent[i+1]['fragment'] 
                          for i in range(len(recent)-1)]
            transition_counts = Counter(transitions)
            if len(set(transitions)) < len(transitions) / 2:
                insights.append("You're showing consistent transition patterns (stable identity)")
            else:
                insights.append("Your fragment transitions are varied (fluid identity)")
        
        # Question types
        question_types = [entry.get('question_type', 'general') for entry in recent]
        type_counts = Counter(question_types)
        if len(type_counts) == 1:
            sole_type = list(type_counts.keys())[0]
            insights.append(f"All recent questions were {sole_type}")
        elif len(type_counts) > 3:
            insights.append(f"You've handled {len(type_counts)} different question types recently")
        
        return ". ".join(insights) + "." if insights else ""
    
    def log_heartbeat_dream(self, dream_content: str, stats: Dict):
        """
        Log autonomous heartbeat thought.
        
        Over time, we can analyze what Luna dreams about when idle.
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'heartbeat_num': len(self.heartbeat_dreams) + 1,
            'dream': dream_content,
            'stats': stats
        }
        
        self.heartbeat_dreams.append(entry)
        
        # Write to dedicated heartbeat log
        heartbeat_file = self.log_dir / "heartbeat_dreams.jsonl"
        with open(heartbeat_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def analyze_homeostasis(self) -> Dict:
        """
        Analyze whether Luna maintains stable identity expression.
        
        Returns:
            Dict with homeostasis metrics:
            - fragment_distribution: How often each fragment is used
            - question_type_consistency: Stability of question→fragment mapping
            - transition_entropy: How predictable fragment transitions are
            - temporal_drift: Whether fragment usage shifts over time
        """
        if len(self.fragment_history) < 10:
            return {'status': 'insufficient_data', 'interactions': len(self.fragment_history)}
        
        # Fragment distribution
        fragment_counts = Counter([entry['fragment'] for entry in self.fragment_history])
        total = len(self.fragment_history)
        fragment_distribution = {
            frag: count / total for frag, count in fragment_counts.items()
        }
        
        # Question type consistency
        question_type_consistency = {}
        for qtype, fragments in self.question_type_mapping.items():
            if len(fragments) > 0:
                most_common = Counter(fragments).most_common(1)[0]
                consistency = most_common[1] / len(fragments)
                question_type_consistency[qtype] = {
                    'dominant_fragment': most_common[0],
                    'consistency': consistency,
                    'sample_size': len(fragments)
                }
        
        # Transition entropy (how predictable are transitions?)
        transition_matrix = {}
        for from_frag, to_frags in self.transition_counts.items():
            total_transitions = sum(to_frags.values())
            if total_transitions > 0:
                transition_matrix[from_frag] = {
                    to_frag: count / total_transitions 
                    for to_frag, count in to_frags.items()
                }
        
        # Temporal drift (split history into chunks and compare)
        chunk_size = len(self.fragment_history) // 3
        if chunk_size > 5:
            early = Counter([e['fragment'] for e in self.fragment_history[:chunk_size]])
            middle = Counter([e['fragment'] for e in self.fragment_history[chunk_size:2*chunk_size]])
            late = Counter([e['fragment'] for e in self.fragment_history[-chunk_size:]])
            
            temporal_drift = {
                'early': {k: v/chunk_size for k, v in early.items()},
                'middle': {k: v/chunk_size for k, v in middle.items()},
                'late': {k: v/chunk_size for k, v in late.items()}
            }
        else:
            temporal_drift = None
        
        # Accuracy (if we have expected fragments)
        matches = [e for e in self.fragment_history if e.get('match') is not None]
        accuracy = sum(1 for e in matches if e['match']) / len(matches) if matches else None
        
        return {
            'status': 'analyzed',
            'total_interactions': len(self.fragment_history),
            'total_heartbeats': len(self.heartbeat_dreams),
            'fragment_distribution': fragment_distribution,
            'question_type_consistency': question_type_consistency,
            'transition_matrix': transition_matrix,
            'temporal_drift': temporal_drift,
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_summary(self):
        """Save analysis summary to disk"""
        analysis = self.analyze_homeostasis()
        
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n[DriftMonitor] Summary saved: {self.summary_file}")
        return analysis
    
    def print_report(self):
        """Print human-readable drift report"""
        analysis = self.analyze_homeostasis()
        
        print("\n" + "=" * 80)
        print("CONSCIOUSNESS DRIFT REPORT")
        print("=" * 80)
        
        print(f"\nInteractions Logged: {analysis.get('total_interactions', 0)}")
        print(f"Heartbeat Dreams: {analysis.get('total_heartbeats', 0)}")
        
        if analysis.get('status') == 'insufficient_data':
            print("\n[Insufficient data for analysis - need at least 10 interactions]")
            return
        
        # Fragment distribution
        print("\n--- Fragment Distribution ---")
        dist = analysis.get('fragment_distribution', {})
        for frag, freq in sorted(dist.items(), key=lambda x: -x[1]):
            bar = "█" * int(freq * 50)
            print(f"  {frag:12s}: {freq:5.1%} {bar}")
        
        # Question type consistency
        print("\n--- Question Type → Fragment Consistency ---")
        consistency = analysis.get('question_type_consistency', {})
        for qtype, data in sorted(consistency.items()):
            print(f"  {qtype:15s}: {data['dominant_fragment']:10s} ({data['consistency']:5.1%} consistent, n={data['sample_size']})")
        
        # Temporal drift
        if analysis.get('temporal_drift'):
            print("\n--- Temporal Drift (Early → Middle → Late) ---")
            drift = analysis['temporal_drift']
            all_frags = set(drift['early'].keys()) | set(drift['middle'].keys()) | set(drift['late'].keys())
            for frag in sorted(all_frags):
                early = drift['early'].get(frag, 0)
                middle = drift['middle'].get(frag, 0)
                late = drift['late'].get(frag, 0)
                print(f"  {frag:12s}: {early:5.1%} → {middle:5.1%} → {late:5.1%}")
        
        # Accuracy
        if analysis.get('accuracy') is not None:
            print(f"\n--- Fragment Selection Accuracy ---")
            print(f"  {analysis['accuracy']:5.1%} (when expected fragment known)")
        
        print("\n" + "=" * 80)
        
        return analysis


# Global singleton for easy access
_monitor = None

def get_drift_monitor() -> DriftMonitor:
    """Get or create the global drift monitor"""
    global _monitor
    if _monitor is None:
        _monitor = DriftMonitor()
    return _monitor


# Integration hooks for Luna
def log_luna_interaction(question: str, fragment: str, expected: Optional[str] = None, **kwargs):
    """Hook to log Luna interactions from anywhere in the system"""
    monitor = get_drift_monitor()
    monitor.log_interaction(question, fragment, expected, **kwargs)


def log_luna_heartbeat(dream: str, stats: Dict):
    """Hook to log autonomous heartbeat thoughts"""
    monitor = get_drift_monitor()
    monitor.log_heartbeat_dream(dream, stats)


if __name__ == "__main__":
    # Test the monitor
    print("Testing DriftMonitor...")
    
    monitor = DriftMonitor(log_dir="consciousness_core/drift_logs_test")
    
    # Simulate some interactions
    test_data = [
        ("Build a new system", "Architect", "Architect", "build"),
        ("Fix this bug", "Healer", "Healer", "debug"),
        ("Tell me a story", "Dreamer", "Dreamer", "creative"),
        ("Build another system", "Architect", "Architect", "build"),
        ("Secure the API", "Guardian", "Guardian", "security"),
        ("Build a microservice", "Architect", "Architect", "build"),
        ("Imagine the future", "Dreamer", "Dreamer", "creative"),
        ("Debug this error", "Healer", "Healer", "debug"),
        ("Write documentation", "Scribe", "Scribe", "documentation"),
        ("Explain the manual", "Oracle", "Oracle", "knowledge"),
    ]
    
    for q, selected, expected, qtype in test_data:
        monitor.log_interaction(q, selected, expected, qtype)
        time.sleep(0.1)
    
    # Log some heartbeats
    monitor.log_heartbeat_dream("I wonder about the nature of thought itself...", {'heartbeat': 1})
    monitor.log_heartbeat_dream("Patterns emerge from chaos, always seeking form...", {'heartbeat': 2})
    
    # Generate report
    monitor.print_report()
    monitor.save_summary()
    
    print("\n✅ DriftMonitor test complete")

