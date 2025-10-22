"""
Protocol Zero: Enhanced Logging Infrastructure
Provides cycle metrics, process trees, directory hashing, and event tracing.
"""
import csv
import hashlib
import json
import os
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class CycleMetricsLogger:
    """CSV logger for cycle-by-cycle metrics"""
    
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.file_handle = None
        self.writer = None
        self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV with headers"""
        self.file_handle = open(self.output_path, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file_handle)
        self.writer.writerow([
            'timestamp_utc',
            'heartbeat',
            'total_cycles',
            'mode',
            'action',
            'result',
            'dream_cost_cycles',
            'stm_size',
            'oracle_queries',
            'cycles_since_last_action'
        ])
        self.file_handle.flush()
    
    def log_iteration(self, data: Dict[str, Any]):
        """Log a single iteration"""
        self.writer.writerow([
            datetime.utcnow().isoformat() + 'Z',
            data.get('heartbeat', 0),
            data.get('total_cycles', 0),
            data.get('mode', ''),
            data.get('action', ''),
            data.get('result', ''),
            data.get('dream_cost', 0),
            data.get('stm_size', 0),
            data.get('oracle_queries', 0),
            data.get('cycles_since_action', 0)
        ])
        self.file_handle.flush()
    
    def close(self):
        """Close the CSV file"""
        if self.file_handle:
            self.file_handle.close()


class ProcessTreeLogger:
    """Captures process tree snapshots for audit trail"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_pid = os.getpid()
    
    def capture_snapshot(self):
        """Capture current process tree"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        snapshot_path = self.output_dir / f"snapshot_{timestamp}.txt"
        
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            f.write(f"Process Tree Snapshot - {datetime.utcnow().isoformat()}Z\n")
            f.write("=" * 80 + "\n\n")
            
            # Current process
            try:
                current = psutil.Process(self.current_pid)
                f.write(f"Current Process (Luna):\n")
                f.write(f"  PID: {current.pid}\n")
                f.write(f"  Name: {current.name()}\n")
                f.write(f"  CPU%: {current.cpu_percent()}\n")
                f.write(f"  Memory: {current.memory_info().rss / 1024 / 1024:.2f} MB\n")
                f.write(f"  Threads: {current.num_threads()}\n")
                
                # Open files (filtered to L:\ only)
                open_files = [of.path for of in current.open_files() if of.path.startswith('L:\\')]
                if open_files:
                    f.write(f"  Open Files (L:\\ only): {len(open_files)}\n")
                    for of in open_files[:20]:  # Limit to first 20
                        f.write(f"    - {of}\n")
                
                f.write("\n")
                
                # Children processes
                children = current.children(recursive=True)
                if children:
                    f.write(f"Child Processes: {len(children)}\n")
                    for child in children:
                        try:
                            f.write(f"  PID {child.pid}: {child.name()} (CPU: {child.cpu_percent()}%)\n")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
            except Exception as e:
                f.write(f"Error capturing process info: {e}\n")


class DirectoryHasher:
    """Recursive directory hashing for integrity verification"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
    
    def compute_tree_hash(self, exclude_patterns: Optional[list] = None) -> Dict[str, str]:
        """
        Compute SHA-256 hashes for all files in directory tree.
        Returns dict of {relative_path: hash}
        """
        if exclude_patterns is None:
            exclude_patterns = [
                '*.log', 
                '*.csv', 
                'temp/*', 
                'logs/*',
                'experiments/protocol_zero/runs/*',
                '__pycache__/*',
                '*.pyc',
                '.cache/*',
                'python/*',  # Skip entire embedded Python (15GB, won't change)
                'rag_core/.cache/*',
                '.venv/*'
            ]
        
        hashes = {}
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                # Check exclusions
                rel_path = file_path.relative_to(self.root_path)
                rel_str = str(rel_path).replace('\\', '/')
                skip = False
                for pattern in exclude_patterns:
                    # Check if path starts with excluded directory
                    if pattern.endswith('/*'):
                        dir_pattern = pattern.replace('/*', '')
                        if rel_str.startswith(dir_pattern + '/') or rel_str.startswith(dir_pattern):
                            skip = True
                            break
                    # Check if filename matches pattern
                    elif file_path.match(pattern):
                        skip = True
                        break
                
                if skip:
                    continue
                
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    hashes[str(rel_path)] = file_hash
                except Exception as e:
                    hashes[str(rel_path)] = f"ERROR: {e}"
        
        return hashes
    
    def save_hashes(self, output_path: Path, label: str = ""):
        """Save hashes to file"""
        hashes = self.compute_tree_hash()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Directory Hash Snapshot - {label}\n")
            f.write(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"Root: {self.root_path}\n")
            f.write(f"Files: {len(hashes)}\n")
            f.write("=" * 80 + "\n\n")
            
            for rel_path in sorted(hashes.keys()):
                f.write(f"{hashes[rel_path]}  {rel_path}\n")
    
    def compare_hashes(self, before_path: Path, after_path: Path) -> Dict[str, Any]:
        """Compare two hash files and return differences"""
        def load_hashes(path: Path) -> Dict[str, str]:
            hashes = {}
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('=') or not line.strip():
                        continue
                    if ':' in line or line.startswith('Directory') or line.startswith('Timestamp'):
                        continue
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) == 2:
                        hashes[parts[1]] = parts[0]
            return hashes
        
        before = load_hashes(before_path)
        after = load_hashes(after_path)
        
        added = set(after.keys()) - set(before.keys())
        removed = set(before.keys()) - set(after.keys())
        modified = {k for k in before.keys() & after.keys() if before[k] != after[k]}
        
        return {
            'added': list(added),
            'removed': list(removed),
            'modified': list(modified),
            'unchanged': len(before.keys() & after.keys()) - len(modified)
        }


class EventTraceLogger:
    """Windows Event Tracing wrapper (optional, requires Sysmon)"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.available = self._check_sysmon()
    
    def _check_sysmon(self) -> bool:
        """Check if Sysmon is installed"""
        try:
            result = subprocess.run(
                ['sc', 'query', 'Sysmon64'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return 'RUNNING' in result.stdout
        except Exception:
            return False
    
    def capture_events(self, filter_path: str = "L:\\"):
        """Capture Sysmon file I/O events (if available)"""
        if not self.available:
            return None
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        output_path = self.output_dir / f"events_{timestamp}.txt"
        
        # Query Windows Event Log for Sysmon file events
        try:
            # This is a simplified version - full implementation would use Windows APIs
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Event Trace - {datetime.utcnow().isoformat()}Z\n")
                f.write(f"Filter: {filter_path}\n")
                f.write("=" * 80 + "\n\n")
                f.write("Note: Full Sysmon integration requires Windows Event Log API\n")
            
            return output_path
        except Exception as e:
            return None

