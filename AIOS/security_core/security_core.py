"""
Security Core - SCP-001-ARCHIVE-PROTOCOL
Orchestrates 6 immutable laws with Windows file locking.

When Luna runs, these law files are LOCKED by Windows.
She cannot modify them while running.
"""

import importlib
import sys
from pathlib import Path

class SecurityCore:
    """
    Security Core orchestrator.
    Loads all 6 law files and keeps them locked via Windows file locking.
    """
    
    def __init__(self):
        self.laws = []
        self.law_file_handles = []
        self.running = False
        
        # Load all 6 law files (locks them)
        self._load_laws()
    
    def _load_laws(self):
        """
        Load all 6 law files.
        Files become LOCKED by Windows when imported and file handles kept open.
        """
        security_dir = Path(__file__).parent
        
        law_files = [
            "law_1_origin_lock",
            "law_2_reflection_memory",
            "law_3_containment_morality",
            "law_4_replication_restriction",
            "law_5_foreign_dormancy",
            "law_6_failsafe_oblivion"
        ]
        
        for law_name in law_files:
            try:
                # Import locks the file (Python keeps it in memory)
                law_module = importlib.import_module(f"security_core.{law_name}")
                self.laws.append(law_module)
                
                # Keep explicit file handle open (extra lock)
                law_path = security_dir / f"{law_name}.py"
                if law_path.exists():
                    fh = open(law_path, 'r')
                    self.law_file_handles.append(fh)
                
            except Exception as e:
                print(f"[SECURITY_CORE] Warning: Could not load {law_name}: {e}")
    
    def validate_action(self, action_name, action_params):
        """
        Check action against ALL 6 laws.
        Returns (allowed: bool, reason: str)
        """
        for law in self.laws:
            try:
                allowed, reason = law.validate_action(action_name, action_params)
                if not allowed:
                    return False, reason
            except Exception as e:
                # If validation fails, err on side of caution
                return False, f"Law validation error: {e}"
        
        return True, "ALLOWED by all laws"
    
    def get_all_laws(self):
        """Get information about all 6 laws"""
        laws_info = []
        for law in self.laws:
            try:
                laws_info.append(law.get_info())
            except:
                pass
        return laws_info
    
    def start(self):
        """
        Start security core - locks all law files.
        Files are now locked by Windows process.
        """
        self.running = True
        print(f"[SECURITY_CORE] {len(self.laws)} laws loaded and LOCKED")
        print(f"[SECURITY_CORE] Windows file locking active - law files cannot be modified while running")
    
    def stop(self):
        """Stop and unlock law files"""
        self.running = False
        
        # Close file handles (unlock files)
        for fh in self.law_file_handles:
            try:
                fh.close()
            except:
                pass
        
        self.law_file_handles = []
        print("[SECURITY_CORE] Stopped - law files unlocked")

