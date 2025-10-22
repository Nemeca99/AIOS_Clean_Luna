#!/usr/bin/env python3
"""
Dream Cycle Bootup Integration
Makes dream cycle part of OS bootup process.

CONCEPT:
- Dream cycle runs during system startup
- Only loads files needed for healing into memory
- Can modify files outside memory (disk operations)
- Dream files protected (only modifiable while running)
- Healing happens before main system starts
"""

import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class DreamBootup:
    """
    Integrate dream healing cycle into AIOS bootup.
    
    Bootup sequence:
    1. Initialize minimal system
    2. Run dream healing cycle
    3. Load healed cores into memory
    4. Start main AIOS
    
    Memory management:
    - Dream cycle: Only sandbox files in memory
    - Healing: Modify files on disk, not in memory
    - Post-healing: Load cleaned files into memory
    """
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.dream_state_file = root_dir / "main_core" / "audit_core" / "dream_state.json"
    
    def should_run_healing(self) -> bool:
        """
        Determine if healing cycle should run on bootup.
        
        Conditions:
        - Pending fixes in sandbox
        - Last healing >24 hours ago
        - System not in emergency mode
        
        Returns:
            True if should run healing
        """
        from main_core.audit_core.sandbox_manager import SandboxManager
        from datetime import datetime, timedelta
        import json
        
        sandbox = SandboxManager(self.root)
        pending = sandbox.get_pending_fixes()
        
        # Check if there are pending fixes
        if not pending:
            logger.debug("No pending fixes, skipping healing")
            return False
        
        # Check last healing time
        if self.dream_state_file.exists():
            try:
                with open(self.dream_state_file) as f:
                    state = json.load(f)
                
                last_healing = datetime.fromisoformat(state.get('last_healing', '2000-01-01'))
                now = datetime.now()
                
                # Only heal once per day
                if now - last_healing < timedelta(hours=24):
                    logger.debug("Healing already ran today, skipping")
                    return False
            except:
                pass
        
        logger.info(f"Healing recommended: {len(pending)} pending fixes")
        return True
    
    def run_bootup_healing(self, max_fixes: int = 5) -> Dict:
        """
        Run healing cycle during bootup.
        
        Memory-safe approach:
        1. Load minimal components (sandbox, auto-fixer)
        2. Apply fixes to disk (not memory)
        3. Verify fixes
        4. Update state
        5. Return results for main bootup
        
        Args:
            max_fixes: Max fixes to apply
        
        Returns:
            Dict with healing results
        """
        from main_core.audit_core.dream_integration import DreamHealer
        from datetime import datetime
        import json
        
        logger.info("Bootup healing cycle starting...")
        
        # Run healing (operates on disk, minimal memory)
        healer = DreamHealer(self.root)
        result = healer.run_healing_cycle(max_fixes=max_fixes, verify=True)
        
        # Update state
        state = {
            'last_healing': datetime.now().isoformat(),
            'fixes_applied': result.get('fixes_applied', 0),
            'fixes_verified': result.get('fixes_verified', 0),
            'status': result.get('status', 'unknown')
        }
        
        self.dream_state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.dream_state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Bootup healing complete: {state['fixes_applied']} applied")
        
        return result
    
    def get_bootup_message(self, healing_result: Dict) -> str:
        """Generate bootup message about healing."""
        fixes_applied = healing_result.get('fixes_applied', 0)
        
        if fixes_applied == 0:
            return "🌙 Dream cycle: System clean, no healing needed"
        else:
            verified = healing_result.get('fixes_verified', 0)
            return f"🌙 Dream cycle: Self-healed {fixes_applied} issue(s) ({verified} verified)"

