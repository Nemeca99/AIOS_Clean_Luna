#!/usr/bin/env python3
"""
Arbiter Export Utility
Exports internal arbiter logs for external Auditor GPT analysis

This creates the integration point between:
- Internal ARBITER (LunaArbiterSystem) - runtime response assessment
- External AUDITOR (ChatGPT GPT) - design-time architectural validation

KEY DISTINCTION:
- AUDITOR (external GPT) = Validates system designs and architecture
- ARBITER (this exports from) = Assesses Luna's responses and manages karma

Usage:
    from luna_core.systems.arbiter_export_util import export_arbiter_logs
    export_arbiter_logs(arbiter_system, output_path="arbiter_export.json")
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def export_arbiter_logs(
    arbiter_system,
    output_path: str = "data_core/ArbiterCache/arbiter_export.json",
    include_full_lessons: bool = False,
    max_lessons: int = 100
) -> Dict:
    """
    Export internal arbiter logs for external Auditor GPT analysis
    
    Args:
        arbiter_system: LunaArbiterSystem instance
        output_path: Where to write the export JSON
        include_full_lessons: If True, includes full text of responses
        max_lessons: Maximum number of recent lessons to export
    
    Returns:
        dict: Export summary
    """
    
    # Get current CFIA state
    cfia_state = arbiter_system.cfia_system.state
    
    # Build export structure
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "export_version": "1.0",
        "cfia_state": {
            "generation": cfia_state.aiiq,
            "karma_pool": cfia_state.karma_pool,
            "total_files": cfia_state.total_files,
            "generation_seed": cfia_state.generation_seed
        },
        "lessons": [],
        "summary": {
            "total_lessons": len(arbiter_system.cache_entries),
            "lessons_exported": 0,
            "avg_utility": 0.0,
            "avg_depth": 0.0,
            "avg_gain": 0.0,
            "depth_distribution": {},
            "gain_distribution": {}
        }
    }
    
    # Export recent lessons (most recent first)
    recent_lessons = sorted(
        arbiter_system.cache_entries,
        key=lambda e: e.timestamp,
        reverse=True
    )[:max_lessons]
    
    total_utility = 0.0
    total_depth = 0
    total_gain = 0.0
    depth_counts = {}
    gain_ranges = {
        "0.0": 0,      # No gain
        "0.1-0.3": 0,  # Low gain
        "0.3-0.5": 0,  # Medium gain
        "0.5+": 0      # High gain
    }
    
    for entry in recent_lessons:
        lesson_data = {
            "timestamp": datetime.fromtimestamp(entry.timestamp).isoformat(),
            "prompt_preview": entry.original_prompt[:100] + "..." if len(entry.original_prompt) > 100 else entry.original_prompt,
            "utility_score": entry.utility_score,
            "karma_delta": entry.karma_delta,
            "lingua_calc_depth": entry.lingua_calc_depth,
            "lingua_calc_gain": entry.lingua_calc_gain,
            "context_tags": entry.context_tags
        }
        
        # Include full text if requested
        if include_full_lessons:
            lesson_data["full_prompt"] = entry.original_prompt
            lesson_data["luna_response"] = entry.suboptimal_response
            lesson_data["gold_standard"] = entry.gold_standard
        
        export_data["lessons"].append(lesson_data)
        
        # Accumulate stats
        total_utility += entry.utility_score
        total_depth += entry.lingua_calc_depth
        total_gain += entry.lingua_calc_gain
        
        # Track distributions
        depth_counts[entry.lingua_calc_depth] = depth_counts.get(entry.lingua_calc_depth, 0) + 1
        
        if entry.lingua_calc_gain == 0.0:
            gain_ranges["0.0"] += 1
        elif entry.lingua_calc_gain < 0.3:
            gain_ranges["0.1-0.3"] += 1
        elif entry.lingua_calc_gain < 0.5:
            gain_ranges["0.3-0.5"] += 1
        else:
            gain_ranges["0.5+"] += 1
    
    # Compute summary stats
    lesson_count = len(recent_lessons)
    if lesson_count > 0:
        export_data["summary"]["lessons_exported"] = lesson_count
        export_data["summary"]["avg_utility"] = round(total_utility / lesson_count, 3)
        export_data["summary"]["avg_depth"] = round(total_depth / lesson_count, 2)
        export_data["summary"]["avg_gain"] = round(total_gain / lesson_count, 3)
        export_data["summary"]["depth_distribution"] = depth_counts
        export_data["summary"]["gain_distribution"] = gain_ranges
    
    # Write to file
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path_obj, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"[ArbiterExport] Exported {lesson_count} lessons to {output_path}")
    print(f"  Avg Utility: {export_data['summary']['avg_utility']:.3f}")
    print(f"  Avg Depth: {export_data['summary']['avg_depth']:.2f}")
    print(f"  Avg Gain: {export_data['summary']['avg_gain']:.3f}")
    
    return export_data["summary"]


def analyze_for_external_auditor(arbiter_system) -> str:
    """
    Generate a summary report for External Auditor GPT review
    
    Args:
        arbiter_system: LunaArbiterSystem instance
    
    Returns:
        str: Formatted report suitable for ChatGPT GPT analysis
    """
    
    # Export recent data
    export_data = export_arbiter_logs(
        arbiter_system,
        output_path="data_core/ArbiterCache/arbiter_export.json",
        include_full_lessons=False,
        max_lessons=50
    )
    
    # Build human-readable report
    report = f"""
# AIOS Internal Arbiter Report for External Auditor Review

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Generation:** {arbiter_system.cfia_system.state.aiiq}
**Karma Pool:** {arbiter_system.cfia_system.state.karma_pool:.1f}

**Note:** AUDITOR (validates designs) vs ARBITER (assesses responses)

## Summary Statistics (Last 50 Lessons)

- **Total Lessons:** {export_data['total_lessons']}
- **Average Utility Score:** {export_data['avg_utility']:.3f} (target: >0.75)
- **Average Linguistic Depth:** {export_data['avg_depth']:.2f} (higher = better reasoning)
- **Average Compression Gain:** {export_data['avg_gain']:.3f} (higher = more efficient)

## Depth Distribution

"""
    
    for depth, count in sorted(export_data['depth_distribution'].items()):
        report += f"- Depth {depth}: {count} lessons\n"
    
    report += "\n## Compression Gain Distribution\n\n"
    
    for gain_range, count in export_data['gain_distribution'].items():
        report += f"- {gain_range}: {count} lessons\n"
    
    report += """

## Questions for External Auditor

1. Is the average utility score acceptable for AIOS v5 standards?
2. Does the depth distribution indicate healthy reasoning patterns?
3. Are compression gains sufficient for linguistic calculus effectiveness?
4. What patterns suggest areas for improvement?

---

*Full export available in: data_core/ArbiterCache/arbiter_export.json*
*Send this to AIOS Auditor GPT (external validator), not the Internal Arbiter*
"""
    
    return report


# CLI interface
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from luna_core.systems.luna_arbiter_system import LunaArbiterSystem
    
    print("Loading Internal Arbiter...")
    arbiter = LunaArbiterSystem()
    
    print("\nGenerating export for External Auditor review...")
    report = analyze_for_external_auditor(arbiter)
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    
    print("\n✅ Export complete. Send arbiter_export.json to External Auditor GPT for architectural analysis.")

