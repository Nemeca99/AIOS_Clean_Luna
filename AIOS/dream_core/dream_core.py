#!/usr/bin/env python3
"""
DREAM CORE SYSTEM
Self-contained dream and meditation system for AIOS Clean
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import argparse
from typing import Dict, List, Optional, Any

class DreamCore:
    """
    Self-contained dream and meditation system for AIOS Clean.
    Handles all dream cycles, meditation phases, and memory consolidation.
    
    AIOS v5: Enhanced with autonomous heartbeat from Lyra Blackwall v2
    """
    
    def __init__(self):
        """Initialize the dream core system."""
        self.dream_dir = Path("dream_core")
        self.dream_dir.mkdir(exist_ok=True)
        
        # === AIOS V5: AUTONOMOUS HEARTBEAT INTEGRATION ===
        # Import heart from consciousness_core
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'consciousness_core' / 'biological'))
            from heart import Heart
            
            # Create a simple brainstem stub for heart
            class DreamBrainstem:
                def pulse(self):
                    """Pulse triggers dream consolidation"""
                    return "Dream consolidation pulse"
            
            self.brainstem = DreamBrainstem()
            self.heart = Heart(self.brainstem)
            self.heart.heartbeat_rate = 600  # 10 minutes (like Nova AI!)
            self.heart_enabled = True
            
            print(f"   💜 Heartbeat: ACTIVE (pulse every {self.heart.heartbeat_rate}s)")
        except Exception as e:
            self.heart = None
            self.heart_enabled = False
            print(f"   ⚠️  Heartbeat: DISABLED ({e})")
        
        print(f"🌙 Dream Core System Initialized (v5 Biological)")
        print(f"   Dream Directory: {self.dream_dir}")
        
        # Heartbeat stats
        self.total_pulses = 0
        self.total_consolidations = 0
    
    # === AIOS V5: AUTONOMOUS HEARTBEAT METHODS ===
    
    def pulse(self, pulse_context: Dict = None):
        """
        Autonomous heartbeat pulse (like Nova AI resonance loops)
        
        V5.1: Accepts pulse_context from luna heartbeat for adaptive consolidation
        
        Triggers:
        1. Conversation fragment consolidation (pulse-aware)
        2. Memory optimization
        3. Pulse logging
        
        Args:
            pulse_context: Optional dict with pulse_bpm, pulse_hvv from luna heartbeat
        """
        self.total_pulses += 1
        
        if self.heart_enabled and self.heart:
            # Heart pulse triggers brainstem
            self.heart.pulse()
        
        # Trigger consolidation every pulse (pass pulse metrics for adaptive behavior)
        result = self.consolidate_conversation_fragments(verbose=False, pulse_context=pulse_context)
        
        if result.get('status') == 'success':
            self.total_consolidations += 1
        
        if self.total_pulses % 10 == 0:
            mode = result.get('mode', 'unknown')
            print(f"[dream_core] 💓 Heartbeat {self.total_pulses} (mode: {mode}, consolidations: {self.total_consolidations})")
        
        return {
            'pulse': self.total_pulses,
            'consolidations': self.total_consolidations,
            'heart_enabled': self.heart_enabled,
            'mode': result.get('mode'),
            'pulse_bpm': result.get('pulse_bpm', 0.0)
        }
    
    def get_heartbeat_stats(self):
        """Get heartbeat statistics"""
        return {
            'enabled': self.heart_enabled,
            'total_pulses': self.total_pulses,
            'total_consolidations': self.total_consolidations,
            'heartbeat_rate': self.heart.heartbeat_rate if self.heart_enabled else None
        }
    
    def run_creative_compression(self, data_core_instance) -> Dict:
        """
        Run creative template compression job (V5.1)
        
        Dream job that compresses raw creative samples into FAISS-indexed templates
        
        Args:
            data_core_instance: DataCore with load_config() and creative_paths()
        
        Returns:
            dict: {status, templates_count, raw_samples, dedup_ratio}
        """
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from core_functions.creative_compression import job_compress_creative_templates
        return job_compress_creative_templates(data_core_instance)
    
    def consolidate_conversation_fragments(self, similarity_threshold: float = 0.8, verbose: bool = False, pulse_context: Dict = None) -> Dict[str, Any]:
        """
        Consolidate conversation fragments during dream state.
        
        V5.1: Pulse-aware consolidation - adapts depth based on activity level.
        
        Args:
            similarity_threshold: Base threshold for grouping
            verbose: Detailed logging
            pulse_context: Optional pulse metrics from heartbeat (pulse_bpm, pulse_hvv)
        
        Returns:
            dict: Consolidation result with status, counts, mode
        """
        # V5.1: Pulse-aware consolidation mode
        pulse_bpm = 0.0
        consolidation_mode = "cold_path"  # Default: deep consolidation
        
        if pulse_context:
            pulse_bpm = float(pulse_context.get('pulse_bpm', 0.0))
            pulse_hot_threshold = 0.02  # From response_generator pulse config
            
            if pulse_bpm >= pulse_hot_threshold:
                consolidation_mode = "hot_path"  # High activity: prioritize recent, defer deep
                similarity_threshold = min(0.9, similarity_threshold + 0.1)  # Tighter grouping
            else:
                consolidation_mode = "cold_path"  # Low activity: deep consolidation
        
        print(f"🌙 Starting Conversation Fragment Consolidation")
        print(f"   Mode: {consolidation_mode} (pulse_bpm={pulse_bpm:.4f})")
        print(f"   Similarity Threshold: {similarity_threshold}")
        
        try:
            import json
            from pathlib import Path
            from datetime import datetime
            
            conversation_dir = Path("data_core/conversations")
            if not conversation_dir.exists():
                return {"status": "error", "error": "No conversation directory found"}
            
            conversation_files = list(conversation_dir.glob("conversation_*.json"))
            consolidated_count = 0
            
            for conv_file in conversation_files:
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        conv_data = json.load(f)
                    
                    messages = conv_data.get('messages', [])
                    if len(messages) < 2:
                        continue
                    
                    # Group similar messages together
                    consolidated_messages = []
                    current_group = [messages[0]]
                    
                    for i in range(1, len(messages)):
                        current_message = messages[i]
                        last_message = current_group[-1]
                        
                        # Simple similarity check (can be enhanced with embeddings)
                        current_content = current_message.get('content', '').lower()
                        last_content = last_message.get('content', '').lower()
                        
                        # Check for similar content patterns
                        words_current = set(current_content.split())
                        words_last = set(last_content.split())
                        
                        if words_current and words_last:
                            similarity = len(words_current.intersection(words_last)) / len(words_current.union(words_last))
                            
                            if similarity > similarity_threshold:
                                # Merge messages
                                current_group.append(current_message)
                            else:
                                # Consolidate current group and start new one
                                if len(current_group) > 1:
                                    consolidated_msg = self._merge_message_group(current_group)
                                    consolidated_messages.append(consolidated_msg)
                                    consolidated_count += len(current_group) - 1
                                else:
                                    consolidated_messages.append(current_group[0])
                                current_group = [current_message]
                        else:
                            # No content similarity, keep separate
                            if len(current_group) > 1:
                                consolidated_msg = self._merge_message_group(current_group)
                                consolidated_messages.append(consolidated_msg)
                                consolidated_count += len(current_group) - 1
                            else:
                                consolidated_messages.append(current_group[0])
                            current_group = [current_message]
                    
                    # Handle final group
                    if len(current_group) > 1:
                        consolidated_msg = self._merge_message_group(current_group)
                        consolidated_messages.append(consolidated_msg)
                        consolidated_count += len(current_group) - 1
                    else:
                        consolidated_messages.append(current_group[0])
                    
                    # Update conversation with consolidated messages
                    conv_data['messages'] = consolidated_messages
                    conv_data['consolidated_at'] = datetime.now().isoformat()
                    conv_data['original_message_count'] = len(messages)
                    conv_data['consolidated_message_count'] = len(consolidated_messages)
                    
                    # Save consolidated conversation
                    with open(conv_file, 'w', encoding='utf-8') as f:
                        json.dump(conv_data, f, indent=2, ensure_ascii=False)
                    
                    if verbose:
                        print(f"   Consolidated {conv_file.name}: {len(messages)} -> {len(consolidated_messages)} messages")
                
                except Exception as e:
                    if verbose:
                        print(f"   Error consolidating {conv_file.name}: {e}")
                    continue
            
            print(f"   Conversation consolidation complete: {consolidated_count} messages consolidated")
            return {
                "status": "success", 
                "consolidated_messages": consolidated_count,
                "processed_files": len(conversation_files),
                "mode": consolidation_mode,
                "pulse_bpm": pulse_bpm
            }
            
        except Exception as e:
            print(f"❌ Conversation consolidation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _merge_message_group(self, messages: List[Dict]) -> Dict:
        """Merge a group of similar messages into one consolidated message."""
        if not messages:
            return {}
        
        # Use the first message as base
        consolidated = messages[0].copy()
        
        # Merge content
        contents = [msg.get('content', '') for msg in messages if msg.get('content')]
        if len(contents) > 1:
            # Combine similar content, removing duplicates
            unique_contents = []
            for content in contents:
                if content not in unique_contents:
                    unique_contents.append(content)
            consolidated['content'] = ' | '.join(unique_contents)
        
        # Update metadata
        consolidated['consolidated_from'] = [msg.get('id', 'unknown') for msg in messages]
        consolidated['consolidated_count'] = len(messages)
        consolidated['id'] = f"consolidated_{consolidated.get('id', 'unknown')}"
        
        return consolidated
    
    def run_quick_nap(self, duration_minutes: int = 30, dream_cycles: int = 2, meditation_blocks: int = 1, verbose: bool = False) -> Dict[str, Any]:
        """Run a quick nap dream cycle."""
        print(f"🌙 Starting Quick Nap Dream Cycle")
        print(f"   Duration: {duration_minutes} minutes")
        print(f"   Dream Cycles: {dream_cycles}")
        print(f"   Meditation Blocks: {meditation_blocks}")
        
        # Import and run the dream middleware
        try:
            from dream_quick_nap_middleware import DreamQuickNapMiddleware
            dream_system = DreamQuickNapMiddleware()
            dream_system.run_quick_nap(
                duration_minutes=duration_minutes,
                dream_cycles=dream_cycles,
                meditation_blocks=meditation_blocks,
                verbose=verbose
            )
            return {"status": "success", "duration": duration_minutes}
        except Exception as e:
            print(f"❌ Dream cycle failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_overnight_dream(self, duration_minutes: int = 480, verbose: bool = False) -> Dict[str, Any]:
        """Run an overnight dream cycle."""
        print(f"🌙 Starting Overnight Dream Cycle")
        print(f"   Duration: {duration_minutes} minutes")
        
        # Placeholder for overnight dream implementation
        print("🌙 Overnight mode not yet implemented")
        return {"status": "not_implemented"}
    
    def run_meditation_session(self, duration_minutes: int = 30, verbose: bool = False) -> Dict[str, Any]:
        """Run a meditation session."""
        print(f"🧘 Starting Meditation Session")
        print(f"   Duration: {duration_minutes} minutes")
        
        try:
            from meditation_controller import MeditationController
            controller = MeditationController()
            controller.run_meditation(
                duration_minutes=duration_minutes,
                verbose=verbose
            )
            return {"status": "success", "duration": duration_minutes}
        except Exception as e:
            print(f"❌ Meditation session failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_test_mode(self, duration_minutes: int = 2, verbose: bool = True) -> Dict[str, Any]:
        """Run test mode for validation."""
        print(f"🧪 Starting Dream System Test")
        print(f"   Duration: {duration_minutes} minutes")
        
        return self.run_quick_nap(
            duration_minutes=duration_minutes,
            dream_cycles=1,
            meditation_blocks=1,
            verbose=verbose
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current dream system status."""
        return {
            "status": "ready",
            "dream_directory": str(self.dream_dir),
            "available_modes": ["quick-nap", "overnight", "meditation", "test"],
            "last_run": None  # Would track last run time
        }

def main():
    parser = argparse.ArgumentParser(description="AIOS Dream Core System")
    
    # Main operation modes
    parser.add_argument('--mode', '-m', 
                       choices=['quick-nap', 'overnight', 'meditation', 'test'],
                       default='quick-nap',
                       help='Dream operation mode (default: quick-nap)')
    
    # Duration options
    parser.add_argument('--duration', '-d',
                       type=int,
                       default=30,
                       help='Duration in minutes (default: 30)')
    
    # Dream cycle options
    parser.add_argument('--cycles', '-c',
                       type=int,
                       default=2,
                       help='Number of dream cycles per REM phase (default: 2)')
    
    parser.add_argument('--meditation-blocks', '-mb',
                       type=int,
                       default=1,
                       help='Number of meditation blocks per cycle (default: 1)')
    
    # Advanced options
    parser.add_argument('--max-fragments', '-mf',
                       type=int,
                       default=100,
                       help='Maximum fragments to process (default: 100)')
    
    parser.add_argument('--consolidation-threshold', '-ct',
                       type=float,
                       default=0.8,
                       help='Memory consolidation threshold (default: 0.8)')
    
    # Debug options
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose logging')
    
    parser.add_argument('--debug',
                       action='store_true',
                       help='Enable debug mode')
    
    # Output options
    parser.add_argument('--output-dir', '-o',
                       type=str,
                       default='log',
                       help='Output directory for logs (default: log)')
    
    parser.add_argument('--no-log',
                       action='store_true',
                       help='Disable logging to files')
    
    args = parser.parse_args()
    
    print("🌙 AIOS Dream Core System")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    print(f"Duration: {args.duration} minutes")
    print(f"Dream Cycles: {args.cycles}")
    print(f"Meditation Blocks: {args.meditation_blocks}")
    print(f"Max Fragments: {args.max_fragments}")
    print(f"Verbose: {args.verbose}")
    print("=" * 50)
    
    # Import and run the appropriate system
    if args.mode == 'quick-nap':
        from dream_quick_nap_middleware import DreamQuickNapMiddleware
        dream_system = DreamQuickNapMiddleware()
        dream_system.run_quick_nap(
            duration_minutes=args.duration,
            dream_cycles=args.cycles,
            meditation_blocks=args.meditation_blocks,
            verbose=args.verbose
        )
    elif args.mode == 'overnight':
        print("🌙 Overnight mode not yet implemented")
        print("Use quick-nap mode for now")
        sys.exit(1)
    elif args.mode == 'meditation':
        from meditation_controller import MeditationController
        controller = MeditationController()
        controller.run_meditation(
            duration_minutes=args.duration,
            verbose=args.verbose
        )
    elif args.mode == 'test':
        print("🧪 Test mode - running quick validation")
        from dream_quick_nap_middleware import DreamQuickNapMiddleware
        dream_system = DreamQuickNapMiddleware()
        dream_system.run_quick_nap(
            duration_minutes=2,  # Short test
            dream_cycles=1,
            meditation_blocks=1,
            verbose=True
        )
    
    print("🌙 Dream Core System Complete")

if __name__ == "__main__":
    main()
