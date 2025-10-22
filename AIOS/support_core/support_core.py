#!/usr/bin/env python3
"""
UNIFIED SUPPORT CORE SYSTEM
Complete support system with all utilities integrated.
Refactored to use modular core components.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup Unicode safety
try:
    from utils_core.unicode_safe_output import setup_unicode_safe_output
    setup_unicode_safe_output()
except ImportError:
    print("Warning: Unicode safety layer not available")

# Import all core modules
from .core.config import AIOSConfig, AIOSConfigError, aios_config
from .core.logger import AIOSLogger, AIOSLoggerError
from .core.health_checker import AIOSHealthChecker, AIOSHealthError
from .core.security import AIOSSecurityValidator
from .core.cache_operations import CacheStatus, CacheMetrics, CacheOperations, CacheRegistry, CacheBackup
from .core.embedding_operations import EmbeddingStatus, EmbeddingMetrics, SimpleEmbedder, EmbeddingCache, FAISSOperations, EmbeddingSimilarity
from .core.recovery_operations import RecoveryStatus, RecoveryOperations, SemanticReconstruction, ProgressiveHealing, RecoveryAssessment
from .core.system_classes import SystemConfig, FilePaths, SystemMessages


class SupportSystem:
    """Unified support system with all utilities integrated"""
    
    def __init__(self, cache_dir: str = None):
        print("🔧 Initializing Unified Support System")
        print("=" * 80)
        
        # Initialize core components
        self.cache_ops = CacheOperations(cache_dir)
        self.registry = CacheRegistry(self.cache_ops.cache_dir)
        self.backup = CacheBackup(self.cache_ops.cache_dir)
        self.embedder = SimpleEmbedder()
        self.embedding_cache = EmbeddingCache()
        self.faiss_ops = FAISSOperations()
        self.recovery_ops = RecoveryOperations(self.cache_ops.cache_dir)
        self.assessment = RecoveryAssessment(self.cache_ops.cache_dir)
        
        # Initialize health checker and security validator
        self.health_checker = AIOSHealthChecker()
        self.security_validator = AIOSSecurityValidator()
        
        # Initialize logger
        self.logger = AIOSLogger("SupportSystem")
        
        print("✅ Unified Support System Initialized")
        print(f"   Cache directory: {self.cache_ops.cache_dir}")
        print(f"   Embedder: {self.embedder.embedding_model}")
        print(f"   FAISS: {'Available' if self.faiss_ops else 'Not available'}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        cache_stats = self.cache_ops.get_cache_stats()
        registry_stats = self.registry.get_registry_stats()
        embedding_stats = self.embedding_cache.get_cache_stats()
        faiss_stats = self.faiss_ops.get_index_stats()
        health_assessment = self.assessment.assess_system_health()
        
        return {
            'cache': cache_stats,
            'registry': registry_stats,
            'embeddings': embedding_stats,
            'faiss': faiss_stats,
            'health': health_assessment,
            'system_ready': health_assessment['status'] == 'healthy'
        }
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        print("🏥 Running System Health Check")
        print("=" * 50)
        
        status = self.get_system_status()
        
        # Display health status
        health = status['health']
        print(f"Health Score: {health['health_score']}/100")
        print(f"Status: {health['status'].upper()}")
        
        if health['issues']:
            print(f"Issues Found: {len(health['issues'])}")
            for issue in health['issues']:
                print(f"  • {issue}")
        
        if health['recommendations']:
            print("Recommendations:")
            for rec in health['recommendations']:
                print(f"  • {rec}")
        
        return status
    
    def create_system_backup(self, backup_name: str = None) -> str:
        """Create complete system backup"""
        print(f"💾 Creating System Backup: {backup_name or 'auto'}")
        
        backup_id = self.backup.create_backup(backup_name)
        if backup_id:
            print(f"✅ Backup created successfully: {backup_id}")
        else:
            print("❌ Backup creation failed")
        
        return backup_id
    
    def restore_system_backup(self, backup_name: str) -> bool:
        """Restore system from backup"""
        print(f"📥 Restoring System from Backup: {backup_name}")
        
        success = self.backup.restore_backup(backup_name)
        if success:
            print(f"✅ System restored successfully from {backup_name}")
        else:
            print(f"❌ System restore failed from {backup_name}")
        
        return success


# === HELPER FUNCTIONS ===

def ensure_directories():
    """Ensure required directories exist"""
    # Create required directories directly
    from pathlib import Path
    
    directories = [
        'data_core/FractalCache',
        'data_core/ArbiterCache',
        'data_core/conversations',
        'log',
        'temp',
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


# === MAIN ENTRY POINT ===

def main():
    """Test the unified support system"""
    print("🧪 Testing Unified Support System")
    
    # Initialize system
    support = SupportSystem()
    
    # Run health check
    health_status = support.run_health_check()
    
    # Create backup
    backup_id = support.create_system_backup("test_backup")
    
    # Get system status
    status = support.get_system_status()
    
    print(f"\n📊 System Status Summary:")
    print(f"   Cache fragments: {status['cache']['total_fragments']}")
    print(f"   Embeddings cached: {status['embeddings']['total_embeddings']}")
    print(f"   Health score: {status['health']['health_score']}/100")
    print(f"   System ready: {status['system_ready']}")


# === SINGLETON INSTANCES FOR MODULE-LEVEL ACCESS ===
# These are imported by other modules like luna_core, carma_core, etc.

# Create singleton logger instance
aios_logger = AIOSLogger("AIOS")

# Create singleton health checker
aios_health_checker = AIOSHealthChecker()

# Create singleton security validator  
aios_security_validator = AIOSSecurityValidator()


if __name__ == "__main__":
    main()

