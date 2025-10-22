#!/usr/bin/env python3
"""
Configuration Management - Backup system configuration
Handles configuration loading, saving, and validation
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class BackupConfig:
    """
    Manages backup system configuration
    """
    
    DEFAULT_CONFIG = {
        'version': 1,
        'repository': {
            'name': 'AIOS Backup',
            'type': 'git-like',
            'compression': True,
            'default_branch': 'main'
        },
        'author': {
            'name': 'AIOS',
            'email': 'aios@local'
        },
        'backup': {
            'auto_backup': False,
            'auto_commit': False,
            'include_patterns': ['*.py', '*.json', '*.md', '*.txt'],
            'exclude_patterns': [
                '__pycache__',
                '*.pyc',
                '*.log',
                '.git',
                '.aios_backup',
                'node_modules'
            ]
        },
        'storage': {
            'compression_level': 6,
            'deduplicate': True,
            'max_history': None  # None = unlimited
        },
        'ui': {
            'colored_output': True,
            'verbose': False
        }
    }
    
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.config_file = repo_dir / "config"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults
                config = self.DEFAULT_CONFIG.copy()
                self._deep_merge(config, loaded_config)
                return config
            except Exception as e:
                print(f"⚠️ Warning: Could not load config: {e}")
                print(f"   Using default configuration")
        
        return self.DEFAULT_CONFIG.copy()
    
    def _deep_merge(self, base: Dict, updates: Dict):
        """Deep merge updates into base dictionary"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save config: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path
        Example: config.get('author.name')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value by dot-separated path
        Example: config.set('author.name', 'Travis')
        """
        keys = key_path.split('.')
        target = self.config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Set value
        target[keys[-1]] = value
        self.save()
    
    def get_author_name(self) -> str:
        """Get author name for commits"""
        return self.get('author.name', 'AIOS')
    
    def get_author_email(self) -> str:
        """Get author email for commits"""
        return self.get('author.email', 'aios@local')
    
    def get_default_branch(self) -> str:
        """Get default branch name"""
        return self.get('repository.default_branch', 'main')
    
    def is_compression_enabled(self) -> bool:
        """Check if compression is enabled"""
        return self.get('repository.compression', True)
    
    def is_deduplication_enabled(self) -> bool:
        """Check if deduplication is enabled"""
        return self.get('storage.deduplicate', True)
    
    def get_exclude_patterns(self) -> list:
        """Get list of exclude patterns"""
        return self.get('backup.exclude_patterns', [])
    
    def get_include_patterns(self) -> list:
        """Get list of include patterns"""
        return self.get('backup.include_patterns', [])
    
    def is_verbose(self) -> bool:
        """Check if verbose output is enabled"""
        return self.get('ui.verbose', False)
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration"""
        return self.config.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Basic validation
        required_keys = ['version', 'repository', 'author']
        
        for key in required_keys:
            if key not in self.config:
                print(f"❌ Invalid config: missing '{key}'")
                return False
        
        return True
    
    def format_config(self) -> str:
        """Format configuration as readable string"""
        return json.dumps(self.config, indent=2)

