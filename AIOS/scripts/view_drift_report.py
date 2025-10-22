"""
View current consciousness drift analysis
Shows cognitive homeostasis metrics from real interactions
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from consciousness_core.drift_monitor import get_drift_monitor

print("\n" + "=" * 80)
print("CONSCIOUSNESS DRIFT ANALYSIS - CURRENT STATE")
print("=" * 80)

monitor = get_drift_monitor()

# Generate and display report
analysis = monitor.print_report()

# If we have heartbeat dreams, show them
if monitor.heartbeat_dreams:
    print("\n" + "=" * 80)
    print("AUTONOMOUS HEARTBEAT DREAMS")
    print("=" * 80)
    print(f"\nTotal dreams: {len(monitor.heartbeat_dreams)}\n")
    
    for i, dream in enumerate(monitor.heartbeat_dreams[-5:], 1):  # Last 5
        print(f"[Dream {dream['heartbeat_num']}] {dream['timestamp']}")
        print(f"  {dream['dream']}")
        print()

# Save updated summary
monitor.save_summary()

print("\n" + "=" * 80)
print("Files saved:")
print(f"  Session log: {monitor.session_file}")
print(f"  Summary: {monitor.summary_file}")
if monitor.heartbeat_dreams:
    print(f"  Heartbeat dreams: {monitor.log_dir}/heartbeat_dreams.jsonl")
print("=" * 80)

