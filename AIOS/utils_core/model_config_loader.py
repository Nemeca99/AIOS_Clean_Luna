#!/usr/bin/env python3
"""
Model Configuration Loader for AIOS Clean
Centralized model configuration management
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ModelConfigLoader:
    """Loads and manages model configuration from centralized config file"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the model config loader
        
        Args:
            config_path: Path to model config file. If None, uses default location.
        """
        if config_path is None:
            # Default to main directory model_config.json
            current_dir = Path(__file__).parent
            config_path = current_dir / "model_config.json"
        
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                # Silent success - only log in verbose mode
            else:
                # Silently use defaults - config files are optional
                self._config = self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file is missing"""
        return {
            "main_model": {
                "model_name": "cognitivecomputations-llama-3-8b-instruct-abliterated-v2-smashed@q8_0"
            },
            "embedder": {
                "model_name": "llama-3.2-1b-instruct-abliterated"
            },
            "auditor": {
                "model_name": "mistralai/mistral-nemo-instruct-2407"
            }
        }
    
    def get_main_model(self) -> str:
        """Get the main LLM model name"""
        try:
            # Try new standardized format first
            if "main_model" in self._config:
                return self._config["main_model"]["model_name"]
            # Fall back to old format
            return self._config["model_config"]["models"]["main_llm"]["name"]
        except (KeyError, TypeError):
            return "cognitivecomputations-llama-3-8b-instruct-abliterated-v2-smashed@q8_0"
    
    def get_embedder_model(self) -> str:
        """Get the embedder model name"""
        try:
            # Try new standardized format first
            if "embedder" in self._config:
                return self._config["embedder"]["model_name"]
            # Fall back to old format
            return self._config["model_config"]["models"]["embedder"]["name"]
        except (KeyError, TypeError):
            return "llama-3.2-1b-instruct-abliterated"
    
    def get_draft_model(self) -> Optional[str]:
        """Get the draft model name (if enabled)"""
        try:
            draft_config = self._config["model_config"]["models"]["draft_model"]
            if draft_config.get("enabled", False):
                return draft_config["name"]
            return None
        except (KeyError, TypeError):
            return None
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get full configuration for a specific model type"""
        try:
            return self._config["model_config"]["models"][model_type]
        except (KeyError, TypeError):
            return {}
    
    def get_alternative_model(self, alt_name: str) -> Optional[str]:
        """Get alternative model name"""
        try:
            return self._config["model_config"]["alternative_models"][alt_name]["name"]
        except (KeyError, TypeError):
            return None
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()
    
    def get_all_models(self) -> Dict[str, str]:
        """Get all active model names"""
        return {
            "main_llm": self.get_main_model(),
            "embedder": self.get_embedder_model(),
            "draft_model": self.get_draft_model()
        }
    
    def print_current_config(self):
        """Print current model configuration"""
        print("\n🤖 Current Model Configuration:")
        print("=" * 50)
        
        models = self.get_all_models()
        for model_type, model_name in models.items():
            if model_name:
                print(f"  {model_type}: {model_name}")
        
        print("=" * 50)

# Global instance for easy access
_model_config_loader = None

def get_model_config_loader() -> ModelConfigLoader:
    """Get global model config loader instance"""
    global _model_config_loader
    if _model_config_loader is None:
        _model_config_loader = ModelConfigLoader()
    return _model_config_loader

def get_main_model() -> str:
    """Convenience function to get main model name"""
    return get_model_config_loader().get_main_model()

def get_embedder_model() -> str:
    """Convenience function to get embedder model name"""
    return get_model_config_loader().get_embedder_model()

def get_draft_model() -> Optional[str]:
    """Convenience function to get draft model name"""
    return get_model_config_loader().get_draft_model()

if __name__ == "__main__":
    # Test the config loader
    loader = ModelConfigLoader()
    loader.print_current_config()
