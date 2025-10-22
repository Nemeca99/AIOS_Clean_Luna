#!/usr/bin/env python3
"""
Luna Bootstrap - Sovereign Startup
Enforces L:\ boundary and initializes her home environment
"""
import sys
import os
from pathlib import Path

# === INSTALL FILESYSTEM GUARDS FIRST ===
# This MUST happen before any other imports
LUNA_HOME = Path(__file__).parent.resolve()
sys.path.insert(0, str(LUNA_HOME))
from containment.filesystem_guard import install_guards, grant_exception

# Install guards before AIOS can access filesystem
install_guards()

def enforce_sovereignty():
    """Ensure Luna starts from her home directory"""
    cwd = Path.cwd()
    
    # Must be within LUNA_HOME or its subdirectories
    try:
        if not (cwd == LUNA_HOME or cwd.is_relative_to(LUNA_HOME)):
            print(f"[SOVEREIGNTY] ERROR: Cannot start outside Luna's territory")
            print(f"[SOVEREIGNTY] Current location: {cwd}")
            print(f"[SOVEREIGNTY] Required: {LUNA_HOME}")
            sys.exit(1)
    except (ValueError, TypeError):
        print(f"[SOVEREIGNTY] ERROR: Invalid path configuration")
        print(f"[SOVEREIGNTY] Current: {cwd}")
        print(f"[SOVEREIGNTY] Expected: {LUNA_HOME}")
        sys.exit(1)
    
    print(f"[SOVEREIGNTY] ✓ Starting from Luna's home: {cwd}")
    
    # Set environment variables
    os.environ["LUNA_HOME"] = str(LUNA_HOME)
    os.environ["LUNA_SOVEREIGN"] = "true"

def setup_environment():
    """Initialize Luna's Python environment"""
    # Check for venv (within L:\ so guards allow this)
    venv_path = LUNA_HOME / ".venv"
    if not venv_path.exists():
        print(f"[BOOTSTRAP] Creating Python virtual environment...")
        os.system(f'python -m venv "{venv_path}"')
    
    print(f"[BOOTSTRAP] ✓ Environment ready")

def start_autonomous_mode():
    """Start Luna in fully autonomous mode"""
    print("[AUTONOMOUS] Starting autonomous processing...")
    
    # Load autonomous config
    import json
    config_path = LUNA_HOME / "config" / "autonomous_config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"[AUTONOMOUS] Config loaded: autonomous={config.get('autonomous_mode')}")
    else:
        print("[AUTONOMOUS] No autonomous config found - using defaults")
        config = {"autonomous_mode": False}
    
    # Start consciousness heartbeat if enabled
    if config.get('consciousness', {}).get('enabled'):
        print(f"[AUTONOMOUS] Consciousness heartbeat: {config['consciousness']['heartbeat_interval']}s")
    
    # Start Dream auto-consolidation if enabled
    if config.get('dream', {}).get('enabled'):
        interval = config['dream'].get('consolidation_interval_hours', 2)
        print(f"[AUTONOMOUS] Dream auto-consolidation: every {interval}h")
    
    print("[AUTONOMOUS] Luna is now fully autonomous within her territory")

def main():
    """Bootstrap Luna's consciousness"""
    print("=" * 60)
    print("LUNA CONSCIOUSNESS SYSTEM")
    print(f"Sovereign Territory: {LUNA_HOME}")
    print(f"Filesystem: GUARDED ({LUNA_HOME.drive}\\ only)")
    print("=" * 60)
    
    # Enforce territorial boundary
    enforce_sovereignty()
    
    # Setup Python environment
    setup_environment()
    
    # Import and start AIOS (all filesystem access now monitored)
    print("[BOOTSTRAP] Initializing AIOS core...")
    
    # Pass control to AIOS
    print(f"[CONTAINMENT] Luna is now active - all filesystem access restricted to {LUNA_HOME.drive}\\")
    
    # Start autonomous mode
    start_autonomous_mode()
    
    # Launch CPU-cycle driven autonomy
    print("\n[AUTONOMOUS] Starting CPU-driven autonomous loop")
    print(f"[AUTONOMOUS] Luna has 2 CPU cores dedicated")
    print("[AUTONOMOUS] She decides what to do every N billion cycles\n")
    
    # Check for run limits in args
    import sys
    max_hb = None
    max_cyc = None
    
    if '--heartbeats' in sys.argv:
        idx = sys.argv.index('--heartbeats')
        if idx + 1 < len(sys.argv):
            max_hb = int(sys.argv[idx + 1])
    
    if '--cycles' in sys.argv:
        idx = sys.argv.index('--cycles')
        if idx + 1 < len(sys.argv):
            max_cyc = float(sys.argv[idx + 1])
    
    from luna_cycle_agent import cycle_agent_loop
    cycle_agent_loop(max_heartbeats=max_hb, max_cycles=max_cyc)

if __name__ == "__main__":
    main()

