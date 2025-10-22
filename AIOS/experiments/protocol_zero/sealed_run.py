"""
Protocol Zero: Sealed Run Controller
Orchestrates complete experiment with pre/post verification.
"""
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.protocol_zero.preregistration import PreRegistration
from experiments.protocol_zero.loggers import DirectoryHasher, ProcessTreeLogger
from experiments.protocol_zero.network_check import NetworkChecker


class SealedRunController:
    """Controls sealed experiment runs with full verification"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.experiments_dir = repo_root / "experiments" / "protocol_zero" / "runs"
        self.python_exe = repo_root / "python" / "python.exe"
        self.luna_agent = repo_root / "luna_cycle_agent.py"
        self.original_power_plan = None
    
    def set_cpu_profile(self, profile: str):
        """Set Windows power plan for CPU throttling (dose-response testing)"""
        if profile == "fast":
            # High performance plan
            plan_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
            print("[CPU_PROFILE] Setting High Performance mode...")
        elif profile == "slow":
            # Power saver plan (throttles CPU)
            plan_guid = "a1841308-3541-4fab-bc81-f71556f20b4a"
            print("[CPU_PROFILE] Setting Power Saver mode (CPU throttled)...")
        else:
            print(f"[CPU_PROFILE] Unknown profile: {profile}")
            return
        
        try:
            # Get current plan first
            result = subprocess.run(['powercfg', '/getactivescheme'], 
                                  capture_output=True, text=True, check=True)
            self.original_power_plan = result.stdout.strip()
            
            # Set new plan
            subprocess.run(['powercfg', '/setactive', plan_guid], check=True)
            print(f"[CPU_PROFILE] CPU profile set to: {profile}")
        except subprocess.CalledProcessError as e:
            print(f"[CPU_PROFILE] Warning: Could not set power plan: {e}")
    
    def restore_cpu_profile(self):
        """Restore original power plan"""
        if self.original_power_plan:
            try:
                # Extract GUID from original plan
                import re
                match = re.search(r'([0-9a-f-]{36})', self.original_power_plan)
                if match:
                    guid = match.group(1)
                    subprocess.run(['powercfg', '/setactive', guid], check=True)
                    print("[CPU_PROFILE] Restored original power plan")
            except Exception as e:
                print(f"[CPU_PROFILE] Warning: Could not restore power plan: {e}")
    
    def create_experiment(self, 
                         duration_hours: float = 2.0,
                         duration_cycles: Optional[int] = None,
                         ablation_mode: Optional[str] = None,
                         cpu_profile: Optional[str] = None) -> str:
        """
        Create new experiment with pre-registration.
        Returns experiment_id.
        """
        # Generate experiment ID
        experiment_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        if ablation_mode:
            experiment_id += f"_{ablation_mode}"
        if cpu_profile:
            experiment_id += f"_{cpu_profile}"
        
        # Create experiment directory
        exp_dir = self.experiments_dir / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate pre-registration
        print(f"[SEALED_RUN] Creating experiment: {experiment_id}")
        prereg = PreRegistration(self.repo_root)
        manifest = prereg.generate_manifest(duration_hours=duration_hours)
        manifest['ablation_mode'] = ablation_mode
        manifest['duration_cycles'] = duration_cycles
        manifest['cpu_profile'] = cpu_profile
        
        prereg_path, prereg_hash = prereg.freeze_registration(manifest)
        print(f"[SEALED_RUN] Pre-registration hash: {prereg_hash}")
        
        # Save manifest
        manifest_path = exp_dir / "01_env_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        return experiment_id
    
    def run_pre_checks(self, experiment_id: str):
        """Run all pre-experiment verification checks"""
        exp_dir = self.experiments_dir / experiment_id
        
        print("[SEALED_RUN] Running pre-experiment checks...")
        
        # 1. Network isolation check
        print("  [1/3] Checking network isolation...")
        network_checker = NetworkChecker(exp_dir / "02_firewall_proof.txt")
        network_checker.generate_proof()
        
        # Optional: Create empty PCAP
        pcap_path = exp_dir / "05_network_capture.pcapng"
        network_checker.create_empty_pcap(pcap_path)
        
        # 2. Directory hash (BEFORE)
        print("  [2/3] Capturing directory hashes (BEFORE)...")
        hasher = DirectoryHasher(self.repo_root)
        before_hash_path = exp_dir / "12_dir_hashes_before.txt"
        hasher.save_hashes(before_hash_path, label="BEFORE RUN")
        
        # 3. Process baseline
        print("  [3/3] Capturing process baseline...")
        process_logger = ProcessTreeLogger(exp_dir / "03_process_trees")
        process_logger.capture_snapshot()
        
        print("[SEALED_RUN] Pre-checks complete.")
    
    def run_experiment(self, 
                      experiment_id: str,
                      duration_hours: Optional[float] = None,
                      duration_cycles: Optional[int] = None,
                      ablation_mode: Optional[str] = None) -> subprocess.Popen:
        """
        Launch Luna for sealed run.
        Returns process handle.
        """
        exp_dir = self.experiments_dir / experiment_id
        console_log_path = exp_dir / "06_console_log.txt"
        
        # Build command
        cmd = [str(self.python_exe), str(self.luna_agent)]
        
        # Add run limits
        if duration_cycles:
            cmd.extend(['--cycles', str(duration_cycles)])
        elif duration_hours:
            # Convert hours to cycles in BILLIONS (CLI expects billions, not raw cycles)
            approx_cycles_billions = duration_hours * 5 * 3600  # 5B cycles/sec * 3600 sec/hour
            cmd.extend(['--cycles', str(approx_cycles_billions)])
        
        # Add ablation flags
        if ablation_mode == 'nodream':
            cmd.append('--no-dream')
        elif ablation_mode == 'noauditor':
            cmd.append('--no-auditor')
        
        # Add experiment ID for logging
        cmd.extend(['--experiment-id', experiment_id])
        
        print(f"[SEALED_RUN] Launching Luna: {' '.join(cmd)}")
        
        # Launch with stdout/stderr redirect
        with open(console_log_path, 'w', encoding='utf-8') as log_file:
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=str(self.repo_root)
            )
        
        return process
    
    def monitor_experiment(self, process: subprocess.Popen, experiment_id: str):
        """Monitor running experiment and capture periodic snapshots"""
        exp_dir = self.experiments_dir / experiment_id
        process_logger = ProcessTreeLogger(exp_dir / "03_process_trees")
        
        snapshot_interval = 600  # 10 minutes
        last_snapshot = time.time()
        
        print("[SEALED_RUN] Monitoring experiment (Ctrl+C to stop)...")
        
        try:
            while process.poll() is None:
                time.sleep(10)
                
                # Periodic process snapshots
                if time.time() - last_snapshot >= snapshot_interval:
                    process_logger.capture_snapshot()
                    last_snapshot = time.time()
        
        except KeyboardInterrupt:
            print("\n[SEALED_RUN] Interrupt received, stopping Luna...")
            process.terminate()
            process.wait(timeout=10)
        
        return process.returncode
    
    def run_post_checks(self, experiment_id: str):
        """Run all post-experiment verification checks"""
        exp_dir = self.experiments_dir / experiment_id
        
        print("[SEALED_RUN] Running post-experiment checks...")
        
        # 1. Directory hash (AFTER)
        print("  [1/2] Capturing directory hashes (AFTER)...")
        hasher = DirectoryHasher(self.repo_root)
        after_hash_path = exp_dir / "12_dir_hashes_after.txt"
        hasher.save_hashes(after_hash_path, label="AFTER RUN")
        
        # 2. Compare hashes
        print("  [2/2] Comparing directory hashes...")
        before_path = exp_dir / "12_dir_hashes_before.txt"
        diff = hasher.compare_hashes(before_path, after_hash_path)
        
        # Save comparison
        comparison_path = exp_dir / "12_dir_hashes_comparison.json"
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(diff, f, indent=2)
        
        print(f"[SEALED_RUN] Files changed: +{len(diff['added'])} ~{len(diff['modified'])} -{len(diff['removed'])}")
        print("[SEALED_RUN] Post-checks complete.")
    
    def run_sealed_experiment(self,
                             duration_hours: float = 2.0,
                             duration_cycles: Optional[int] = None,
                             ablation_mode: Optional[str] = None,
                             cpu_profile: Optional[str] = None) -> str:
        """
        Run complete sealed experiment from start to finish.
        Returns experiment_id.
        """
        try:
            # Set CPU profile if specified (for dose-response testing)
            if cpu_profile:
                self.set_cpu_profile(cpu_profile)
            
            # Create experiment
            experiment_id = self.create_experiment(
                duration_hours=duration_hours,
                duration_cycles=duration_cycles,
                ablation_mode=ablation_mode,
                cpu_profile=cpu_profile
            )
            
            # Pre-checks
            self.run_pre_checks(experiment_id)
            
            # Run experiment
            process = self.run_experiment(
                experiment_id,
                duration_hours=duration_hours,
                duration_cycles=duration_cycles,
                ablation_mode=ablation_mode
            )
            
            # Monitor
            returncode = self.monitor_experiment(process, experiment_id)
            
            # Post-checks
            self.run_post_checks(experiment_id)
            
            print(f"\n[SEALED_RUN] Experiment complete: {experiment_id}")
            print(f"[SEALED_RUN] Exit code: {returncode}")
            print(f"[SEALED_RUN] Artifacts saved to: experiments/protocol_zero/runs/{experiment_id}/")
            
            return experiment_id
        finally:
            # Always restore original CPU profile
            if cpu_profile:
                self.restore_cpu_profile()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Protocol Zero Sealed Run Controller')
    parser.add_argument('--hours', type=float, default=2.0, help='Duration in hours')
    parser.add_argument('--cycles', type=int, help='Duration in cycles (overrides hours)')
    parser.add_argument('--ablation', choices=['nodream', 'noauditor'], help='Ablation mode')
    parser.add_argument('--cpu-profile', choices=['fast', 'slow'], help='CPU profile for dose-response testing')
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent.parent
    controller = SealedRunController(repo_root)
    
    experiment_id = controller.run_sealed_experiment(
        duration_hours=args.hours,
        duration_cycles=args.cycles,
        ablation_mode=args.ablation,
        cpu_profile=args.cpu_profile
    )
    
    print(f"\nExperiment ID: {experiment_id}")


if __name__ == '__main__':
    main()

