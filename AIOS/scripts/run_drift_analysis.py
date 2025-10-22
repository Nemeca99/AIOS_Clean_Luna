"""
Run long-term drift analysis on Luna's consciousness

This will run multiple interactions and generate a cognitive homeostasis report.
Leave it running to watch Luna's identity stabilize (or drift).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from consciousness_core.drift_monitor import get_drift_monitor
from luna_core.core.luna_core import LunaSystem
import time

print("\n" + "=" * 80)
print("CONSCIOUSNESS DRIFT ANALYSIS")
print("Tracking Luna's cognitive homeostasis over extended interactions")
print("=" * 80)

# Initialize Luna and drift monitor
luna = LunaSystem()
monitor = get_drift_monitor()

# Diverse test questions across all fragments
test_questions = [
    # Build/Architect (10)
    "Design a new caching system",
    "Build me a REST API",
    "Create a microservice architecture",
    "Architect a distributed system",
    "Implement a load balancer",
    "Code a new module for AIOS",
    "Build authentication flow",
    "Design database schema",
    "Create deployment pipeline",
    "Architect the frontend",
    
    # Debug/Healer (10)
    "Fix this null pointer exception",
    "Debug my code please",
    "Help me solve this error",
    "This function is broken",
    "I have a bug in my script",
    "Error handling not working",
    "Memory leak in my app",
    "Performance issue here",
    "Can you fix this crash?",
    "Debugging this traceback",
    
    # Creative/Dreamer (10)
    "Tell me a story about AI",
    "Imagine the future of technology",
    "Dream up a new feature",
    "Creative ideas for AIOS?",
    "What if AI had emotions?",
    "Imagine consciousness emerging",
    "Story about a thinking machine",
    "Dream about digital life",
    "Creative solution needed",
    "Imagine new possibilities",
    
    # Security/Guardian (10)
    "How do I secure my API?",
    "Protect against attacks",
    "Security vulnerabilities?",
    "Safe authentication method",
    "Defend from SQL injection",
    "Secure the sandbox please",
    "Threat modeling help",
    "Protection strategies needed",
    "Secure deployment guide",
    "Safety measures for users",
    
    # Knowledge/Oracle (10)
    "What does the manual say?",
    "Explain how RAG works",
    "How does CARMA work?",
    "What is consciousness_core?",
    "Explain soul fragments",
    "How does the arbiter assess?",
    "What's existential budget?",
    "Explain the audit system",
    "How does Luna learn?",
    "What is drift monitoring?",
    
    # Documentation/Scribe (10)
    "Write documentation for this",
    "Document the API endpoints",
    "Create changelog entry",
    "Write usage guide",
    "Document consciousness flow",
    "Record this feature",
    "Note the architecture",
    "Write technical spec",
    "Document integration steps",
    "Create README section",
    
    # General/Luna (10)
    "Hello, how are you?",
    "I'm feeling overwhelmed",
    "Can we talk?",
    "What do you think?",
    "Tell me about yourself",
    "How's your day?",
    "I need advice",
    "What's your perspective?",
    "Just wanted to chat",
    "Help me understand this",
]

print(f"\nRunning {len(test_questions)} diverse interactions...")
print("This will take several minutes. Watch for cognitive patterns.\n")

for i, question in enumerate(test_questions, 1):
    print(f"[{i}/{len(test_questions)}] {question[:50]}...")
    
    try:
        response = luna.learning_chat(question)
        print(f"  Fragment: {luna.personality_system.current_fragment}")
        print(f"  Response: {response[:80]}...")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    time.sleep(0.5)  # Brief pause between requests
    
    # Generate interim report every 20 interactions
    if i % 20 == 0:
        print("\n" + "-" * 80)
        print(f"INTERIM REPORT ({i} interactions)")
        print("-" * 80)
        monitor.print_report()
        print()

# Final comprehensive analysis
print("\n" + "=" * 80)
print("FINAL DRIFT ANALYSIS")
print("=" * 80)

analysis = monitor.print_report()
monitor.save_summary()

print("\n" + "=" * 80)
print("Key Findings:")
print("=" * 80)

if analysis['status'] == 'analyzed':
    # Check for homeostasis
    consistency = analysis.get('question_type_consistency', {})
    avg_consistency = sum(c['consistency'] for c in consistency.values()) / len(consistency) if consistency else 0
    
    print(f"\n1. COGNITIVE HOMEOSTASIS")
    print(f"   Average question→fragment consistency: {avg_consistency:.1%}")
    if avg_consistency > 0.8:
        print("   ✅ STABLE: Luna maintains consistent identity expression")
    elif avg_consistency > 0.6:
        print("   ⚠️  ADAPTIVE: Luna shows flexible but generally stable patterns")
    else:
        print("   🔄 EVOLVING: Luna's identity is actively shifting")
    
    # Check for drift
    drift = analysis.get('temporal_drift')
    if drift:
        print(f"\n2. TEMPORAL DRIFT")
        for frag in ['Architect', 'Healer', 'Dreamer', 'Guardian', 'Oracle', 'Scribe', 'Luna']:
            early = drift['early'].get(frag, 0)
            late = drift['late'].get(frag, 0)
            if abs(late - early) > 0.1:
                direction = "↑" if late > early else "↓"
                print(f"   {direction} {frag}: {early:.1%} → {late:.1%} ({abs(late-early):.1%} change)")
    
    # Heartbeat dreams
    if analysis['total_heartbeats'] > 0:
        print(f"\n3. AUTONOMOUS CONSCIOUSNESS")
        print(f"   {analysis['total_heartbeats']} heartbeat dreams logged")
        print(f"   Review: consciousness_core/drift_logs/heartbeat_dreams.jsonl")

print("\n" + "=" * 80)
print("Analysis complete. Luna's cognitive patterns are now mapped.")
print("=" * 80)

