#!/usr/bin/env python3
"""
AIOS Clean - Universal Bootstrap
The ONLY required file to run AIOS. 100% plug-and-play.

This bootstrap:
1. Auto-detects and activates virtual environment
2. Detects your operating system
3. Discovers all *_core plugins
4. Loads them automatically
5. Routes commands to the right plugin
6. Just works - no configuration needed!
"""

import os
import sys
import platform
import importlib
import subprocess
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional

# === CRITICAL: Auto-activate virtual environment ===
def ensure_venv():
    """Auto-detect and activate virtual environment if not already active"""
    # Check if already in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return  # Already in venv
    
    # Find venv directory
    script_dir = Path(__file__).parent
    venv_dirs = ['.venv', 'venv']
    
    for venv_name in venv_dirs:
        venv_path = script_dir / venv_name
        if venv_path.exists():
            # Construct path to Python executable in venv
            if platform.system() == 'Windows':
                venv_python = venv_path / 'Scripts' / 'python.exe'
            else:
                venv_python = venv_path / 'bin' / 'python'
            
            if venv_python.exists():
                # Show activation message (only if verbose)
                if '--verbose' in sys.argv or '--debug' in sys.argv:
                    print(f"→ Auto-activating virtual environment: {venv_name}")
                
                # Re-execute script with venv Python
                os.execv(str(venv_python), [str(venv_python)] + sys.argv)
                return  # Won't reach here, but for clarity
    
    # No venv found - continue with system Python
    if '--verbose' in sys.argv or '--debug' in sys.argv:
        print("→ No virtual environment found. Using system Python.")

# Auto-activate venv before anything else
ensure_venv()

# === CRITICAL: Setup environment first ===
os.environ["RICH_SHELL_INTEGRATION"] = "false"
os.environ["RICH_FORCE_TERMINAL"] = "false"
os.environ["RICH_DISABLE_CONSOLE"] = "true"

# Fix Unicode output on Windows
if platform.system() == 'Windows':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass  # Python < 3.7 doesn't have reconfigure

# === CONFIGURATION ===
AIOS_ROOT = Path(__file__).parent.absolute()
os.chdir(AIOS_ROOT)  # Always run from AIOS root
sys.path.insert(0, str(AIOS_ROOT))

# Runtime state for shared objects
_RUNTIME = {
    "core": None,
    "heartbeat_started": False
}

# === CORE DISCOVERY ===

def discover_cores() -> List[str]:
    """
    Discover all *_core folders in the AIOS root.
    This is how AIOS finds plugins - zero configuration!
    """
    cores = []
    try:
        for item in AIOS_ROOT.iterdir():
            if item.is_dir() and item.name.endswith('_core'):
                cores.append(item.name)
    except Exception as e:
        print(f"⚠️  Warning: Could not scan for cores: {e}")
    
    return sorted(cores)


def attempt_self_heal(core_name: str, error: Exception) -> bool:
    """
    SELF-HEALING: When a core breaks, try to fix it automatically!
    
    1. Check if backup_core has a last-known-good version
    2. Compare current (broken) vs backup (working)
    3. Identify what's missing/broken
    4. Patch the current file
    5. Return True if healed, False if can't fix
    
    The system HEALS its own code!
    """
    try:
        backup_path = AIOS_ROOT / "backup_core" / "active_backup" / core_name
        current_path = AIOS_ROOT / core_name
        
        if not backup_path.exists():
            return False  # No backup available
        
        # Find the main core file
        core_file = core_name + ".py"
        hybrid_file = f"hybrid_{core_name}.py"
        
        for filename in [core_file, hybrid_file]:
            backup_file = backup_path / filename
            current_file = current_path / filename
            
            if backup_file.exists() and current_file.exists():
                # Read both versions
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(current_file, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                # If they're different, restore from backup
                if backup_content != current_content:
                    print(f"🔧 Self-healing: Restoring {core_name}/{filename} from backup...")
                    with open(current_file, 'w', encoding='utf-8') as f:
                        f.write(backup_content)
                    print(f"   ✅ File restored from backup")
                    return True
        
        return False
    except Exception as e:
        # Can't heal - that's okay, just report
        return False


def load_cores(core_names: List[str]) -> Dict[str, Any]:
    """
    LIVING SYSTEM: Lazy load cores with self-healing.
    If a core fails to load, try to heal it automatically!
    """
    loaded_cores = {}
    
    for core_name in core_names:
        try:
            # Lazy import - only loads when needed
            module = importlib.import_module(core_name)
            loaded_cores[core_name] = module
        except Exception as e:
            # SELF-HEALING: Try to fix the broken core
            print(f"⚠️  {core_name} failed to load: {str(e)[:50]}")
            
            healed = attempt_self_heal(core_name, e)
            if healed:
                # Try importing again after healing
                try:
                    print(f"   🔄 Retrying import after self-heal...")
                    module = importlib.import_module(core_name)
                    loaded_cores[core_name] = module
                    print(f"   ✅ {core_name} healed and loaded successfully!")
                except Exception as retry_error:
                    print(f"   ❌ Self-heal attempt failed: {str(retry_error)[:50]}")
            else:
                print(f"   ℹ️  No backup available for {core_name}")
    
    return loaded_cores


def auto_detect_commands(core_name: str, module: Any) -> Optional[Dict[str, Any]]:
    """
    EMERGENT INTELLIGENCE: Auto-detect commands by scanning core's code.
    If core doesn't declare commands, we figure them out ourselves!
    
    This makes the system ALIVE - it adapts to cores automatically.
    """
    try:
        core_path = AIOS_ROOT / core_name
        
        # Look for files that might contain commands
        possible_files = []
        
        # Scan all .py files in the core directory (not recursive for now)
        for py_file in core_path.glob("*.py"):
            if not py_file.name.startswith('_'):  # Skip __init__, __pycache__, etc initially
                possible_files.append(py_file)
        
        # Also check main files
        possible_files.extend([
            core_path / f"{core_name}.py",
            core_path / f"hybrid_{core_name}.py",  # hybrid versions
            core_path / "__init__.py"
        ])
        
        detected_commands = {}
        
        for file_path in possible_files:
            if not file_path.exists():
                continue
                
            # Read the core's source code
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Scan for command patterns
                # Look for: if '--something' in args:
                import re
                pattern = r"['\"]--([a-zA-Z0-9_-]+)['\"]"
                matches = re.findall(pattern, source)
                
                for match in set(matches):  # Unique commands
                    cmd = f"--{match}"
                    detected_commands[cmd] = {
                        "help": f"Command from {core_name}",
                        "usage": f"python main.py {cmd}",
                        "examples": [f"python main.py {cmd}"],
                        "auto_detected": True
                    }
            except Exception:
                continue
        
        if detected_commands:
            return {
                "commands": detected_commands,
                "description": f"{core_name} (auto-detected)",
                "version": "auto",
                "author": "AIOS Auto-Discovery",
                "auto_generated": True
            }
    except Exception:
        pass
    
    return None


def discover_commands(cores: List[str]) -> Dict[str, Any]:
    """
    LIVING SYSTEM: Auto-discover AND auto-detect commands from all cores.
    
    1. Check if core declares commands (get_commands())
    2. If not, SCAN THE CODE and figure it out ourselves!
    3. Make everything work automatically
    
    The system is ALIVE - it adapts and heals itself!
    """
    command_registry = {}
    
    for core_name in cores:
        try:
            module = importlib.import_module(core_name)
            
            # OPTION 1: Core declares its commands (preferred)
            if hasattr(module, 'get_commands'):
                commands = module.get_commands()
                if commands:
                    command_registry[core_name] = commands
                    continue
            
            # OPTION 2: EMERGENT - Auto-detect by scanning code
            detected = auto_detect_commands(core_name, module)
            if detected:
                command_registry[core_name] = detected
                
        except Exception:
            # Even if import fails, try to detect from files
            detected = auto_detect_commands(core_name, None)
            if detected:
                command_registry[core_name] = detected
    
    return command_registry


# === VALIDATE COMMAND ===

def handle_validate(cores: List[str], loaded_cores: Dict[str, Any] = None):
    """
    Validate all discovered cores.
    Check if they're valid plugins and can be imported.
    """
    print("\n🔍 Validating AIOS Cores...\n")
    
    valid_count = 0
    invalid_count = 0
    
    for core_name in cores:
        try:
            # Try to import the core
            module = importlib.import_module(core_name)
            
            # Check if it has handle_command function
            has_handler = hasattr(module, 'handle_command')
            
            # Check if handler is callable
            is_callable = callable(getattr(module, 'handle_command', None)) if has_handler else False
            
            if has_handler and is_callable:
                print(f"  ✅ {core_name}")
                print(f"     Status: Valid plugin")
                print(f"     Handler: Found and callable")
                valid_count += 1
            else:
                print(f"  ⚠️  {core_name}")
                print(f"     Status: Missing handle_command() function")
                print(f"     Note: This core won't respond to commands")
                invalid_count += 1
                
        except Exception as e:
            print(f"  ❌ {core_name}")
            print(f"     Status: Cannot import")
            print(f"     Error: {str(e)[:100]}")
            invalid_count += 1
        
        print()
    
    # Summary
    total = len(cores)
    print(f"📊 Validation Summary:")
    print(f"   Total cores: {total}")
    print(f"   ✅ Valid: {valid_count}")
    print(f"   ⚠️  Issues: {invalid_count}")
    
    if invalid_count == 0:
        print(f"\n🎉 All cores are valid plugins!\n")
    else:
        print(f"\n⚠️  Some cores need attention.\n")


# === PING COMMAND ===

def handle_ping(cores: List[str], args: List[str]):
    """
    Display discovered cores and their structure.
    --ping [--depth N] [--core CORENAME] [--health]
    """
    depth = 1
    target_core = None
    show_health = '--health' in args
    
    # Parse ping arguments
    i = 0
    while i < len(args):
        if args[i] == '--depth' and i + 1 < len(args):
            try:
                depth = int(args[i + 1])
                i += 2
            except ValueError:
                print("⚠️  Depth must be a number (e.g., --depth 2)")
                return
        elif args[i] == '--core' and i + 1 < len(args):
            target_core = args[i + 1] if not args[i + 1].endswith('_core') else args[i + 1]
            if not target_core.endswith('_core'):
                target_core = f"{target_core}_core"
            i += 2
        else:
            i += 1
    
    # Display results
    print("\n🔍 AIOS Cores Discovered:\n")
    
    cores_to_show = [target_core] if target_core and target_core in cores else cores
    
    # Load cores if health check requested
    core_health = {}
    if show_health:
        for core_name in cores_to_show:
            try:
                module = importlib.import_module(core_name)
                if hasattr(module, 'handle_command'):
                    core_health[core_name] = "✅ healthy"
                else:
                    core_health[core_name] = "⚠️  no handler"
            except Exception as e:
                core_health[core_name] = f"❌ {str(e)[:30]}"
    
    for core in cores_to_show:
        core_path = AIOS_ROOT / core
        if not core_path.exists():
            continue
            
        status = f" ({core_health[core]})" if show_health and core in core_health else ""
        print(f"  ✓ {core}{status}")
        
        if depth >= 2:
            # Show files in core root
            try:
                for item in sorted(core_path.iterdir()):
                    if item.is_file():
                        size = item.stat().st_size
                        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                        print(f"    📄 {item.name} ({size_str})")
                    elif depth >= 3 and item.is_dir() and not item.name.startswith('.'):
                        print(f"    📁 {item.name}/")
                        if depth >= 4:
                            # Show subdirectory contents
                            for subitem in sorted(item.iterdir())[:10]:  # Limit to 10
                                prefix = "📄" if subitem.is_file() else "📁"
                                print(f"       {prefix} {subitem.name}")
            except PermissionError:
                print(f"    ⚠️  Permission denied")
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
        
        print()  # Blank line between cores
    
    if not cores_to_show:
        print("  ⚠️  No cores found. Did you download AIOS completely?")
        print("     Try: git clone <repository> to get all files.\n")


# === OS DETECTION ===

def detect_os() -> str:
    """Detect operating system for OS-specific functionality."""
    system = platform.system().lower()
    
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unix'  # Generic fallback


# === HELP SYSTEM ===

def show_help(cores: List[str], command_registry: Dict[str, Any]):
    """
    Show dynamic help based on discovered cores and their commands.
    Auto-updates when new cores are added!
    """
    print("\n🤖 AIOS Clean - Modular AI System\n")
    print("=" * 60)
    
    # System commands (built into main.py)
    print("\n📋 System Commands:")
    print("  --ping [--health] [--depth N]  Discover and inspect cores")
    print("  --validate                      Validate all cores")
    print("  --audit [--core NAME]           Run automated system health check (V2)")
    print("  --audit --v3                    Run V3 Sovereign audit (4.5s, 18 features)")
    print("  --audit --fixes                 Show priority fix list")
    print("  --audit --production-ready      Check production readiness")
    print("  --status                        Show system environment status")
    print("  --sandbox-security status       Show sandbox security status")
    print("  --sandbox-security test         Test sandbox security")
    print("  --promote status                Show promotion status")
    print("  --help                          Show this help message")
    
    # Discovered core commands
    if command_registry:
        print("\n🔌 Plugin Commands (Auto-Discovered):\n")
        
        for core_name, metadata in sorted(command_registry.items()):
            # Show core description
            desc = metadata.get('description', core_name)
            version = metadata.get('version', 'unknown')
            print(f"  [{core_name}] v{version}")
            print(f"  {desc}")
            
            # Show commands
            commands = metadata.get('commands', {})
            for cmd, cmd_info in sorted(commands.items()):
                help_text = cmd_info.get('help', 'No description')
                print(f"    {cmd:20} {help_text}")
            
            print()  # Blank line between cores
    else:
        print("\n⚠️  No cores with declared commands found.")
        print("   Cores need get_commands() function to show here.")
    
    # Show all discovered cores
    print(f"\n📦 Discovered Cores ({len(cores)}):")
    cores_with_cmds = set(command_registry.keys())
    cores_without = [c for c in cores if c not in cores_with_cmds]
    
    if cores_with_cmds:
        print("  With commands:")
        for core in sorted(cores_with_cmds):
            print(f"    ✅ {core}")
    
    if cores_without:
        print("  Without commands (need get_commands()):")
        for core in sorted(cores_without):
            print(f"    ⚠️  {core}")
    
    # Quick examples
    print("\n💡 Quick Examples:")
    if command_registry:
        # Show first example from first core with commands
        first_core = next(iter(command_registry.values()))
        first_cmd = next(iter(first_core.get('commands', {}).values()))
        examples = first_cmd.get('examples', [])
        if examples:
            for ex in examples[:2]:  # Show max 2 examples
                print(f"  {ex}")
    
    print("\n  python main.py --ping --health")
    print("  python main.py --validate")
    
    print("\n📖 For detailed command usage:")
    print("  python main.py --ping --depth 2       # See core structure")
    print("  python main.py --validate             # Check core status")
    print()


# === OS-SPECIFIC CORE ROUTING ===

def run_os_specific_core(args: List[str]):
    """Route to OS-specific main core implementation"""
    os_type = detect_os()
    
    if os_type == 'windows':
        # Run Windows-specific core
        from main_core.main_core_windows import AIOSClean
        aios = AIOSClean()
        aios.run_cli(args)
    elif os_type in ['linux', 'unix']:
        # Run Linux/Unix-specific core
        from main_core.main_core_linux import AIOSCleanLinux
        aios = AIOSCleanLinux()
        aios.run_cli(args)
    else:
        # Fallback to Linux for other Unix-like systems
        print(f"⚠️  Unknown OS '{os_type}', defaulting to Linux core")
        from main_core.main_core_linux import AIOSCleanLinux
        aios = AIOSCleanLinux()
        aios.run_cli(args)

# === MAIN ENTRY POINT ===

def _ensure_runtime_wiring(core):
    """
    Make HybridLunaCore behave like luna_chat path:
    - one shared DriftMonitor
    - one shared ExperienceState
    - pulse enabled for per-request ticks
    - heartbeat timer started
    """
    from consciousness_core.drift_monitor import DriftMonitor
    from luna_core.core.luna_lingua_calc import ExperienceState
    
    # Get response generator from hybrid core
    python_impl = getattr(core, "python_impl", None)
    if python_impl is None:
        print("   [WARN] No python_impl in HybridLunaCore")
        return None
    
    rg = getattr(python_impl, "response_generator", None)
    if rg is None:
        print("   [WARN] No response_generator in python_impl")
        return None
    
    # Persistent session objects (stash on core to avoid recreation)
    if not hasattr(core, "_drift_monitor"):
        core._drift_monitor = DriftMonitor()
        print("   [RUNTIME] Created shared DriftMonitor")
    if not hasattr(core, "_exp_state"):
        core._exp_state = ExperienceState()
        print("   [RUNTIME] Created shared ExperienceState")
    
    # Inject into response generator
    rg.drift_monitor = core._drift_monitor
    rg.exp_state = core._exp_state
    
    # Enable pulse ticks
    if not hasattr(rg, "_pulse_enabled"):
        rg._pulse_enabled = True
    
    print(f"   [RUNTIME] DriftMonitor wired: {type(core._drift_monitor).__name__}")
    print(f"   [RUNTIME] ExperienceState nodes={len(core._exp_state.nodes)} edges={len(core._exp_state.edges)}")
    
    # Start heartbeat timer (once per process)
    if not _RUNTIME.get("heartbeat_started", False):
        _start_heartbeat(rg)
        _RUNTIME["heartbeat_started"] = True
    
    return rg


def _start_heartbeat(rg):
    """Start background heartbeat timer for pulse metrics"""
    # Read window from generator or use default
    window = getattr(rg, "_pulse_window_seconds", None) or 600
    rg._pulse_enabled = True
    
    def _beat():
        try:
            if hasattr(rg, "generate_autonomous_heartbeat"):
                soul_data = {
                    'identity': 'Luna AIOS',
                    'fragments': ['Luna'],
                    'tether': 'Travis Miner',
                    'interactions': 0
                }
                rg.generate_autonomous_heartbeat(soul_data)
        except Exception as e:
            print(f"   [HEARTBEAT] Error: {e}")
        finally:
            # Reschedule
            threading.Timer(window, _beat).start()
    
    # Kick off first beat
    threading.Timer(window, _beat).start()
    print(f"   [RUNTIME] Heartbeat timer started (window={window}s)")


def _get_hybrid():
    """Get or create shared HybridLunaCore instance"""
    if _RUNTIME["core"] is None:
        from luna_core.hybrid_luna_core import HybridLunaCore
        _RUNTIME["core"] = HybridLunaCore()
        _ensure_runtime_wiring(_RUNTIME["core"])
    return _RUNTIME["core"]


def main():
    """
    Universal AIOS bootstrap.
    Discovers cores, routes commands, just works!
    """
    
    # Get command line arguments
    args = sys.argv[1:]
    
    # Discover all cores
    cores = discover_cores()
    
    if not cores:
        print("⚠️  No AIOS cores found!")
        print("   Expected folders like: luna_core/, carma_core/, etc.")
        print("   Make sure you're in the AIOS_Clean directory.\n")
        sys.exit(1)
    
    # Handle --ping command (bootstrap handles this directly)
    if '--ping' in args:
        handle_ping(cores, args)
        return
    
    # Handle --validate command (check all cores are valid)
    if '--validate' in args:
        handle_validate(cores, loaded_cores if 'loaded_cores' in locals() else None)
        return
    
    # Handle --audit command (run system health check)
    if '--audit' in args:
        try:
            # Check if --v3 flag for new V3 Sovereign audit
            if '--v3' in args:
                from main_core.audit_core.audit_v3_sovereign import AuditV3Sovereign
                audit = AuditV3Sovereign()
                exit_code = audit.run_sovereign_audit()
                sys.exit(exit_code)
            else:
                # Use V2 audit (proven stable)
                from main_core.audit_interface import handle_command as handle_audit
                handle_audit(args)
        except Exception as e:
            print(f"❌ Audit system error: {e}")
            print("   Make sure main_core/audit_interface.py is available")
        return
    
    # Show help if no arguments
    if not args or '--help' in args:
        # Only discover commands for help system
        command_registry = discover_commands(cores)
        show_help(cores, command_registry)
        return
    
    # Show system status
    if '--status' in args:
        print("\n" + "="*60)
        print("AIOS SYSTEM STATUS")
        print("="*60)
        
        # Python environment
        print("\n🐍 Python Environment:")
        print(f"   Executable: {sys.executable}")
        print(f"   Version: {sys.version.split()[0]}")
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        print(f"   Virtual env: {'✅ Active' if in_venv else '❌ Not active (using system Python)'}")
        if in_venv:
            print(f"   Venv path: {sys.prefix}")
        
        # OS environment (detailed)
        print(f"\n💻 Operating System:")
        print(f"   Platform: {platform.system()}")
        print(f"   Version: {platform.version()}")
        print(f"   Release: {platform.release()}")
        
        # Windows-specific details
        if platform.system() == 'Windows':
            try:
                import subprocess
                # Get Windows version details
                result = subprocess.run(
                    ['cmd', '/c', 'ver'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    ver_output = result.stdout.strip()
                    # Extract build number
                    if 'Version' in ver_output:
                        print(f"   Build: {ver_output.split('Version')[-1].strip().strip(']')}")
                
                # Get edition (Home, Pro, Enterprise, etc.)
                result = subprocess.run(
                    ['powershell', '-Command', '(Get-WmiObject -Class Win32_OperatingSystem).Caption'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    edition = result.stdout.strip()
                    print(f"   Edition: {edition}")
            except Exception:
                pass  # Graceful fallback
        
        print(f"   Architecture: {platform.machine()}")
        print(f"   Processor: {platform.processor()}")
        
        # Hardware detection
        print(f"\n🔧 Hardware:")
        
        # CPU info
        try:
            import psutil
            cpu_count = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            print(f"   CPU Cores: {cpu_count} physical, {cpu_threads} logical")
            if cpu_freq:
                print(f"   CPU Frequency: {cpu_freq.current:.0f} MHz (max: {cpu_freq.max:.0f} MHz)")
        except ImportError:
            # Fallback without psutil
            import os
            cpu_count = os.cpu_count()
            print(f"   CPU Threads: {cpu_count}")
        except Exception as e:
            print(f"   CPU: Detection failed")
        
        # RAM info
        try:
            import psutil
            mem = psutil.virtual_memory()
            print(f"   RAM: {mem.total / (1024**3):.1f} GB total, {mem.available / (1024**3):.1f} GB available ({mem.percent}% used)")
        except ImportError:
            print(f"   RAM: psutil required for detection")
        except Exception:
            print(f"   RAM: Detection failed")
        
        # GPU info (if torch is available)
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                print(f"   GPU: {gpu_count} CUDA device(s)")
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                    print(f"        [{i}] {gpu_name} ({gpu_mem:.1f} GB)")
            else:
                print(f"   GPU: CUDA not available (CPU mode)")
        except ImportError:
            print(f"   GPU: torch not installed")
        except Exception:
            print(f"   GPU: Detection failed")
        
        # Installed packages (key ones)
        print(f"\n📦 Key Packages:")
        packages_to_check = [
            'sentence_transformers',
            'torch',
            'numpy',
            'requests',
            'streamlit'
        ]
        for pkg in packages_to_check:
            try:
                mod = importlib.import_module(pkg.replace('-', '_'))
                version = getattr(mod, '__version__', 'unknown')
                print(f"   ✅ {pkg}: {version}")
            except ImportError:
                print(f"   ❌ {pkg}: Not installed")
        
        # AIOS cores
        print(f"\n🔌 AIOS Cores:")
        print(f"   Discovered: {len(cores)} cores")
        print(f"   Location: {Path.cwd()}")
        
        # Quick health check
        print(f"\n🏥 Quick Health Check:")
        try:
            from rag_core.manual_oracle import ManualOracle
            oracle = ManualOracle()
            print(f"   ✅ Manual Oracle: {len(oracle.oracle_index)} sections indexed")
        except Exception as e:
            print(f"   ⚠️  Manual Oracle: {str(e)[:50]}")
        
        print("\n" + "="*60)
        return
    
    # Handle --info command (route to OS-specific core)
    if '--info' in args:
        run_os_specific_core(args)
        return
    
    # Route to OS-specific core for most commands
    # Only handle system-level commands here, let OS cores handle the rest
    system_commands = ['--ping', '--validate', '--audit', '--status', '--help', '--info']
    if not any(cmd in args for cmd in system_commands):
        # This is a core-specific command, route to OS-specific implementation
        run_os_specific_core(args)
        return
    
    # Load cores lazily for system commands
    loaded_cores = load_cores(cores)
    
    # Broadcast command to all cores
    # Each core decides if it should handle the command
    handled = False
    
    for core_name, core_module in loaded_cores.items():
        try:
            # Each core should have a handle_command() function
            if hasattr(core_module, 'handle_command'):
                result = core_module.handle_command(args)
                if result:  # Core handled it
                    handled = True
                    break
        except Exception as e:
            # SELF-HEALING: Core failed - try to fix it!
            print(f"⚠️  {core_name} encountered an error:")
            print(f"   {str(e)[:100]}")
            
            # Attempt self-heal
            print(f"   🔧 Attempting self-heal...")
            healed = attempt_self_heal(core_name, e)
            
            if healed:
                # Reload the module and retry
                try:
                    print(f"   🔄 Reloading healed core...")
                    importlib.reload(core_module)
                    
                    # Retry command
                    if hasattr(core_module, 'handle_command'):
                        result = core_module.handle_command(args)
                        if result:
                            print(f"   ✅ Command succeeded after self-heal!")
                            handled = True
                            break
                except Exception as retry_error:
                    print(f"   ❌ Self-heal didn't fix the issue: {str(retry_error)[:50]}")
            else:
                print(f"   ℹ️  No backup available - manual intervention needed.\n")
    
    if not handled:
        print("⚠️  Command not recognized by any core.")
        print("   Try: python main.py --ping to see available cores")
        print("   Or:  python main.py --help for more options\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   If this keeps happening, please report it as a bug.\n")
        sys.exit(1)

