#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

Constrained Factorial Intelligence Architecture (CFIA)
Governs Luna's memory growth, efficiency, and intelligence indexing through constrained strategic expansion
"""

import math
import json
import time
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path

@dataclass
class CFIAState:
    """Core state variables for CFIA"""
    aiiq: int  # Artificial Intelligence Quotient (Factorial Index) - Now Generation Number
    alpha: float  # Dampening Factor (Growth Handbrake)
    total_files: int  # Current linear count of files
    current_threshold: float  # Current file size threshold in KB
    last_aiiq_increment: float  # Timestamp of last AIIQ increment
    generation_seed: int  # Current Generation Seed (DNA) for all inference
    karma_pool: float  # Current Karma Pool (Health/Life Force)
    generation_birth_time: float  # When current generation was born
    
@dataclass
class FileInfo:
    """Information about a cache file"""
    file_id: str
    size_kb: float
    content_count: int
    last_accessed: float
    split_count: int

class LunaCFIASystem:
    """
    Constrained Factorial Intelligence Architecture
    Manages memory growth through factorial intelligence indexing and constrained expansion
    """
    
    def __init__(self, cache_path: str = "data_core/ArbiterCache"):
        """Initialize the CFIA system"""
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize core state variables
        current_time = time.time()
        self.state = CFIAState(
            aiiq=2,  # Initial learning phase (Generation 2)
            alpha=0.15,  # Recommended for PC-level efficiency
            total_files=1,  # The foundational file
            current_threshold=1000.0,  # Base threshold: 1,000 KB
            last_aiiq_increment=current_time,
            generation_seed=self._generate_generation_seed(),  # Random seed for this generation
            karma_pool=100.0,  # Full health at birth
            generation_birth_time=current_time
        )
        
        # File management
        self.file_registry = {}  # file_id -> FileInfo
        self._load_state()
        self._scan_existing_files()
        
        print(" Constrained Factorial Intelligence Architecture (CFIA) Initialized")
        print(f"    Generation: {self.state.aiiq} (AIIQ/Generation Number)")
        print(f"    Generation Seed: {self.state.generation_seed} (DNA)")
        print(f"     Karma Pool: {self.state.karma_pool:.1f} (Health/Life Force)")
        print(f"     Alpha: {self.state.alpha} (Dampening Factor)")
        print(f"    Total Files: {self.state.total_files}")
        print(f"    Current Threshold: {self.state.current_threshold:.1f} KB")
        print(f"    Target Files for Next Generation: {math.factorial(self.state.aiiq)}")
    
    def process_lesson_addition(self, lesson_kb: float, target_file: Optional[str] = None) -> Dict:
        """
        Process adding a new lesson with CFIA constraints
        Returns information about any splits or AIIQ increments
        """
        print(f" CFIA Processing: Adding {lesson_kb:.1f} KB lesson...")
        
        # Step 1: Determine target file
        if not target_file:
            target_file = self._select_target_file()
        
        # Step 2: Calculate granularity threshold
        granularity_threshold = self._calculate_granularity_threshold()
        
        # Step 3: Check if split is required
        current_file_size = self._get_file_size(target_file)
        projected_size = current_file_size + lesson_kb
        
        split_required = projected_size > granularity_threshold
        
        result = {
            "target_file": target_file,
            "current_size": current_file_size,
            "projected_size": projected_size,
            "granularity_threshold": granularity_threshold,
            "split_required": split_required,
            "aiiq_increment": False,
            "new_files_created": [],
            "files_deleted": []
        }
        
        if split_required:
            print(f" CFIA Split Required: {projected_size:.1f} KB > {granularity_threshold:.1f} KB threshold")
            
            # Perform file split
            split_result = self._perform_file_split(target_file, lesson_kb)
            result.update(split_result)
            
            # Check for AIIQ increment
            if self.state.total_files == math.factorial(self.state.aiiq):
                aiq_result = self._increment_aiiq()
                result.update(aiq_result)
        else:
            # Simple addition - update file info
            self._update_file_info(target_file, lesson_kb)
        
        # Save state
        self._save_state()
        
        return result
    
    def _select_target_file(self) -> str:
        """Select the target file for lesson addition"""
        if not self.file_registry:
            # Create initial file if none exist
            return self._create_new_file()
        
        # Select file with most available space
        best_file = None
        best_available_space = 0
        
        for file_id, file_info in self.file_registry.items():
            available_space = self.state.current_threshold - file_info.size_kb
            if available_space > best_available_space:
                best_available_space = available_space
                best_file = file_id
        
        return best_file or self._create_new_file()
    
    def _calculate_granularity_threshold(self) -> float:
        """Calculate the granularity threshold for current AIIQ"""
        n = self.state.aiiq
        
        # Granularity factors based on AIIQ
        granularity_factors = {
            2: 0.375,  # 75% / R_2 = 75% / 2 = 37.5%
            3: 0.167,  # 50% / R_3 = 50% / 3 = 16.7%
            4: 0.0625, # 25% / R_4 = 25% / 4 = 6.25%
        }
        
        # For higher AIIQ, use exponential formula: (1/n) * (1/n!)
        if n > 4:
            factor = (1.0 / n) * (1.0 / math.factorial(n))
        else:
            factor = granularity_factors.get(n, 0.0625)
        
        threshold = self.state.current_threshold * factor
        print(f" Granularity Threshold: {threshold:.1f} KB (Factor: {factor:.4f} for AIIQ {n})")
        
        return threshold
    
    def _perform_file_split(self, target_file: str, lesson_kb: float) -> Dict:
        """Perform file split operation"""
        print(f" Performing file split: {target_file}")
        
        # Read current file content
        file_path = self.cache_path / f"{target_file}.json"
        if not file_path.exists():
            return {"error": "Target file not found"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}
        
        # Add new lesson to content
        # (In a real implementation, this would be the actual lesson content)
        content.append({
            "lesson_kb": lesson_kb,
            "timestamp": time.time(),
            "aiiq_at_creation": self.state.aiiq
        })
        
        # Split content into two parts
        mid_point = len(content) // 2
        content_a = content[:mid_point]
        content_b = content[mid_point:]
        
        # Create new file IDs
        file_a_id = f"file_{self.state.total_files + 1}"
        file_b_id = f"file_{self.state.total_files + 2}"
        
        # Write split files
        try:
            # Write file A
            with open(self.cache_path / f"{file_a_id}.json", 'w', encoding='utf-8') as f:
                json.dump(content_a, f, indent=2, ensure_ascii=False)
            
            # Write file B
            with open(self.cache_path / f"{file_b_id}.json", 'w', encoding='utf-8') as f:
                json.dump(content_b, f, indent=2, ensure_ascii=False)
            
            # Delete original file
            file_path.unlink()
            
            # Update registry
            self._register_file(file_a_id, len(content_a))
            self._register_file(file_b_id, len(content_b))
            
            # Remove old file from registry
            if target_file in self.file_registry:
                del self.file_registry[target_file]
            
            # Update total files count
            self.state.total_files += 1
            
            print(f" Split Complete: {target_file} → {file_a_id} + {file_b_id}")
            print(f"    New Total Files: {self.state.total_files}")
            
            return {
                "files_deleted": [target_file],
                "new_files_created": [file_a_id, file_b_id],
                "split_successful": True
            }
            
        except Exception as e:
            return {"error": f"Failed to write split files: {e}"}
    
    def _increment_aiiq(self) -> Dict:
        """Increment AIIQ and recalculate thresholds"""
        old_aiiq = self.state.aiiq
        self.state.aiiq += 1
        self.state.last_aiiq_increment = time.time()
        
        # Recalculate threshold using the formula
        self.state.current_threshold = self._calculate_new_threshold()
        
        print(f" AIIQ INCREMENT: {old_aiiq} → {self.state.aiiq}")
        print(f"    Target Files for Next Level: {math.factorial(self.state.aiiq)}")
        print(f"    New Threshold: {self.state.current_threshold:.1f} KB")
        
        return {
            "aiiq_increment": True,
            "old_aiiq": old_aiiq,
            "new_aiiq": self.state.aiiq,
            "new_threshold": self.state.current_threshold,
            "next_target_files": math.factorial(self.state.aiiq)
        }
    
    def _calculate_new_threshold(self) -> float:
        """Calculate new threshold using the CFIA formula"""
        n = self.state.aiiq
        if n == 2:
            return 1000.0  # Base threshold
        
        # T_n = T_{n-1} + (T_{n-1} * (1/R_n) * alpha)
        # Where R_n = n (simple ratio of factorials)
        
        t_prev = self.state.current_threshold
        r_n = n
        increment = t_prev * (1.0 / r_n) * self.state.alpha
        
        new_threshold = t_prev + increment
        
        print(f" Threshold Calculation: {t_prev:.1f} + ({t_prev:.1f} * (1/{r_n}) * {self.state.alpha}) = {new_threshold:.1f}")
        
        return new_threshold
    
    def _create_new_file(self) -> str:
        """Create a new file and return its ID"""
        file_id = f"file_{self.state.total_files}"
        file_path = self.cache_path / f"{file_id}.json"
        
        # Create empty file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        
        self._register_file(file_id, 0)
        
        print(f" Created new file: {file_id}")
        return file_id
    
    def _register_file(self, file_id: str, content_count: int):
        """Register a file in the registry"""
        file_size = self._calculate_file_size_kb(file_id)
        
        self.file_registry[file_id] = FileInfo(
            file_id=file_id,
            size_kb=file_size,
            content_count=content_count,
            last_accessed=time.time(),
            split_count=0
        )
    
    def _update_file_info(self, file_id: str, lesson_kb: float):
        """Update file info after adding lesson"""
        if file_id in self.file_registry:
            self.file_registry[file_id].size_kb += lesson_kb
            self.file_registry[file_id].content_count += 1
            self.file_registry[file_id].last_accessed = time.time()
    
    def _get_file_size(self, file_id: str) -> float:
        """Get current file size in KB"""
        if file_id in self.file_registry:
            return self.file_registry[file_id].size_kb
        return 0.0
    
    def _calculate_file_size_kb(self, file_id: str) -> float:
        """Calculate actual file size from disk"""
        file_path = self.cache_path / f"{file_id}.json"
        if file_path.exists():
            return file_path.stat().st_size / 1024.0
        return 0.0
    
    def _scan_existing_files(self):
        """Scan existing files and populate registry"""
        for file_path in self.cache_path.glob("file_*.json"):
            file_id = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                self._register_file(file_id, len(content))
                
            except Exception as e:
                print(f" Error scanning file {file_id}: {e}")
    
    def _load_state(self):
        """Load CFIA state from disk"""
        state_file = self.cache_path / "cfia_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                self.state = CFIAState(
                    aiiq=state_data.get("aiiq", 2),
                    alpha=state_data.get("alpha", 0.15),
                    total_files=state_data.get("total_files", 1),
                    current_threshold=state_data.get("current_threshold", 1000.0),
                    last_aiiq_increment=state_data.get("last_aiiq_increment", time.time()),
                    generation_seed=state_data.get("generation_seed", self._generate_generation_seed()),
                    karma_pool=state_data.get("karma_pool", 100.0),
                    generation_birth_time=state_data.get("generation_birth_time", time.time())
                )
                
                print(f" Loaded CFIA state: AIIQ {self.state.aiiq}, Files {self.state.total_files}")
                
            except Exception as e:
                print(f" Error loading CFIA state: {e}")
    
    def _save_state(self):
        """Save CFIA state to disk"""
        state_file = self.cache_path / "cfia_state.json"
        
        state_data = {
            "aiiq": self.state.aiiq,
            "alpha": self.state.alpha,
            "total_files": self.state.total_files,
            "current_threshold": self.state.current_threshold,
            "last_aiiq_increment": self.state.last_aiiq_increment,
            "generation_seed": self.state.generation_seed,
            "karma_pool": self.state.karma_pool,
            "generation_birth_time": self.state.generation_birth_time,
            "timestamp": time.time()
        }
        
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f" Error saving CFIA state: {e}")
    
    def get_status(self) -> Dict:
        """Get current CFIA status"""
        return {
            "aiiq": self.state.aiiq,
            "alpha": self.state.alpha,
            "total_files": self.state.total_files,
            "current_threshold": self.state.current_threshold,
            "next_aiiq_target": math.factorial(self.state.aiiq),
            "files_until_next_aiiq": math.factorial(self.state.aiiq) - self.state.total_files,
            "granularity_threshold": self._calculate_granularity_threshold(),
            "file_registry_size": len(self.file_registry),
            "time_since_last_aiiq": time.time() - self.state.last_aiiq_increment
        }
    
    def _generate_generation_seed(self) -> int:
        """Generate a new random generation seed (DNA)"""
        return random.randint(1000, 9999)
    
    def get_current_generation_seed(self) -> int:
        """Get the current generation seed for all inference"""
        return self.state.generation_seed
    
    def update_karma_pool(self, karma_delta: float) -> Dict:
        """Update karma pool and check for generational death/reset"""
        old_karma = self.state.karma_pool
        self.state.karma_pool = max(0.0, self.state.karma_pool + karma_delta)
        
        result = {
            "old_karma": old_karma,
            "new_karma": self.state.karma_pool,
            "karma_delta": karma_delta,
            "generation_died": False,
            "generation_reset": False
        }
        
        # Check for generational death (Karma hits 0)
        if self.state.karma_pool <= 0.0:
            print(f" GENERATIONAL DEATH: Karma pool depleted ({old_karma:.1f} → {self.state.karma_pool:.1f})")
            result["generation_died"] = True
            result["generation_reset"] = self._perform_generational_reset()
        
        # Check for generational success (Target files reached)
        elif self.state.total_files >= math.factorial(self.state.aiiq):
            print(f" GENERATIONAL SUCCESS: Target files reached ({self.state.total_files} >= {math.factorial(self.state.aiiq)})")
            result["generation_success"] = True
            result["generation_reset"] = self._perform_generational_reset()
        
        return result
    
    def _perform_generational_reset(self) -> bool:
        """Perform generational reset: increment AIIQ, generate new seed, reset karma"""
        try:
            old_generation = self.state.aiiq
            old_seed = self.state.generation_seed
            
            # Increment generation
            self.state.aiiq += 1
            self.state.generation_seed = self._generate_generation_seed()
            self.state.karma_pool = 100.0
            self.state.generation_birth_time = time.time()
            self.state.last_aiiq_increment = time.time()
            
            # Recalculate threshold
            self.state.current_threshold = self._calculate_new_threshold()
            
            print(f" GENERATIONAL RESET: Gen {old_generation} → Gen {self.state.aiiq}")
            print(f"    New DNA: {old_seed} → {self.state.generation_seed}")
            print(f"     New Health: 100.0 Karma")
            print(f"    New Threshold: {self.state.current_threshold:.1f} KB")
            print(f"    New Target: {math.factorial(self.state.aiiq)} files")
            
            # Save state
            self._save_state()
            
            return True
            
        except Exception as e:
            print(f" Error during generational reset: {e}")
            return False
    
    def get_generation_status(self) -> Dict:
        """Get current generation status and health"""
        current_time = time.time()
        age_seconds = current_time - self.state.generation_birth_time
        
        return {
            "generation_number": self.state.aiiq,
            "generation_seed": self.state.generation_seed,
            "karma_pool": self.state.karma_pool,
            "age_seconds": age_seconds,
            "age_minutes": age_seconds / 60.0,
            "files_created": self.state.total_files,
            "target_files": math.factorial(self.state.aiiq),
            "files_remaining": math.factorial(self.state.aiiq) - self.state.total_files,
            "is_alive": self.state.karma_pool > 0.0,
            "is_successful": self.state.total_files >= math.factorial(self.state.aiiq)
        }

    def get_growth_analysis(self) -> Dict:
        """Get analysis of growth patterns"""
        return {
            "linear_growth_rate": self.state.total_files,  # Files grow linearly
            "exponential_growth_factor": 2 ** self.state.aiiq,  # Memory structure grows exponentially
            "efficiency_ratio": self.state.total_files / math.factorial(self.state.aiiq - 1) if self.state.aiiq > 1 else 1.0,
            "next_milestone": {
                "files_needed": math.factorial(self.state.aiiq) - self.state.total_files,
                "aiiq_level": self.state.aiiq,
                "threshold_at_milestone": self._calculate_new_threshold()
            }
        }
