#!/usr/bin/env python3
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

AIOS JSON STANDARD FORMAT
Official AIOS Data Standard - September 21, 2025

This module defines the standard JSON formats for all AIOS data structures.
All AIOS data must use JSON arrays as the primary structure for consistency.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class AIOSDataType(Enum):
    """AIOS Data Types for JSON standardization"""
    CONVERSATION = "conversation"
    CAR_CACHE = "car_cache"
    TEST_RESULTS = "test_results"
    CONFIG = "config"
    PERSONALITY = "personality"
    MEMORY = "memory"
    LEARNING_HISTORY = "learning_history"

class AIOSJSONStandards:
    """AIOS JSON Standard Format Constants and Validators"""
    
    # Standard field names
    ID_FIELD = "id"
    CONVERSATION_ID_FIELD = "conversation_id"
    ROLE_FIELD = "role"
    CONTENT_FIELD = "content"
    TIMESTAMP_FIELD = "timestamp"
    METADATA_FIELD = "metadata"
    
    # Standard roles
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"
    
    # Standard timestamp format
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    
    # Standard sources
    SOURCE_GAMING_CHAOS = "gaming_chaos"
    SOURCE_TRAVIS = "travis"
    SOURCE_SYNTHETIC = "synthetic"
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a standard UUID string"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate a standard timestamp"""
        return datetime.now().strftime(AIOSJSONStandards.TIMESTAMP_FORMAT)
    
    @staticmethod
    def validate_json_array(data: Any) -> bool:
        """Validate that data is a JSON array"""
        return isinstance(data, list)
    
    @staticmethod
    def validate_conversation_format(conversation_data: List[Dict]) -> bool:
        """Validate conversation data format"""
        if not isinstance(conversation_data, list):
            return False
        
        required_fields = [
            AIOSJSONStandards.ID_FIELD,
            AIOSJSONStandards.CONVERSATION_ID_FIELD,
            AIOSJSONStandards.ROLE_FIELD,
            AIOSJSONStandards.CONTENT_FIELD,
            AIOSJSONStandards.TIMESTAMP_FIELD,
            AIOSJSONStandards.METADATA_FIELD
        ]
        
        for item in conversation_data:
            if not isinstance(item, dict):
                return False
            
            for field in required_fields:
                if field not in item:
                    return False
            
            # Validate role
            if item[AIOSJSONStandards.ROLE_FIELD] not in [
                AIOSJSONStandards.USER_ROLE,
                AIOSJSONStandards.ASSISTANT_ROLE,
                AIOSJSONStandards.SYSTEM_ROLE
            ]:
                return False
        
        return True
    
    @staticmethod
    def validate_car_cache_format(cache_data: List[Dict]) -> bool:
        """Validate CAR cache data format"""
        if not isinstance(cache_data, list):
            return False
        
        required_fields = [
            "pattern",
            "embedding",
            "frequency",
            "last_used",
            "similarity_threshold",
            "compression"
        ]
        
        for item in cache_data:
            if not isinstance(item, dict):
                return False
            
            for field in required_fields:
                if field not in item:
                    return False
        
        return True

@dataclass
class ConversationMessage:
    """Standard conversation message format"""
    id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.id:
            self.id = AIOSJSONStandards.generate_uuid()
        if not self.timestamp:
            self.timestamp = AIOSJSONStandards.generate_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def create_message(cls, conversation_id: str, role: str, content: str, 
                      metadata: Optional[Dict] = None) -> 'ConversationMessage':
        """Create a new conversation message"""
        return cls(
            id=AIOSJSONStandards.generate_uuid(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=AIOSJSONStandards.generate_timestamp(),
            metadata=metadata or {}
        )

@dataclass
class CARCacheEntry:
    """Standard CAR cache entry format"""
    pattern: str
    embedding: List[float]
    frequency: int
    last_used: str
    similarity_threshold: float
    compression: Dict[str, Any]
    id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = AIOSJSONStandards.generate_uuid()
        if not self.last_used:
            self.last_used = AIOSJSONStandards.generate_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class TestResult:
    """Standard test result format"""
    test_id: str
    timestamp: str
    mode: str
    model: str
    questions: List[Dict[str, Any]]
    performance: Dict[str, Any]
    
    def __post_init__(self):
        if not self.test_id:
            self.test_id = AIOSJSONStandards.generate_uuid()
        if not self.timestamp:
            self.timestamp = AIOSJSONStandards.generate_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class ConfigEntry:
    """Standard configuration format"""
    config_name: str
    version: str
    parameters: Dict[str, Any]
    models: Dict[str, str]
    id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = AIOSJSONStandards.generate_uuid()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class AIOSJSONHandler:
    """Handler for AIOS JSON standard operations"""
    
    @staticmethod
    def load_json_array(file_path: str) -> List[Dict]:
        """Load JSON array from file with validation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not AIOSJSONStandards.validate_json_array(data):
                raise ValueError(f"File {file_path} does not contain a valid JSON array")
            
            return data
        except Exception as e:
            raise ValueError(f"Error loading JSON array from {file_path}: {e}")
    
    @staticmethod
    def save_json_array(data: List[Dict], file_path: str) -> None:
        """Save data as JSON array to file"""
        if not AIOSJSONStandards.validate_json_array(data):
            raise ValueError("Data must be a valid JSON array")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Error saving JSON array to {file_path}: {e}")
    
    @staticmethod
    def convert_to_aios_standard(data: Any, data_type: AIOSDataType) -> List[Dict]:
        """Convert legacy data to AIOS standard format"""
        if data_type == AIOSDataType.CONVERSATION:
            return AIOSJSONHandler._convert_conversation_data(data)
        elif data_type == AIOSDataType.CAR_CACHE:
            return AIOSJSONHandler._convert_cache_data(data)
        elif data_type == AIOSDataType.CONFIG:
            return AIOSJSONHandler._convert_config_data(data)
        else:
            raise ValueError(f"Conversion not implemented for data type: {data_type}")
    
    @staticmethod
    def _convert_conversation_data(data: Any) -> List[Dict]:
        """Convert conversation data to AIOS standard"""
        if isinstance(data, list):
            converted = []
            for item in data:
                if isinstance(item, dict):
                    # Ensure it has required fields
                    converted_item = {
                        "id": item.get("id", AIOSJSONStandards.generate_uuid()),
                        "conversation_id": item.get("conversation_id", AIOSJSONStandards.generate_uuid()),
                        "role": item.get("role", "user"),
                        "content": item.get("content", ""),
                        "timestamp": item.get("timestamp", AIOSJSONStandards.generate_timestamp()),
                        "metadata": item.get("metadata", {})
                    }
                    converted.append(converted_item)
            return converted
        elif isinstance(data, dict):
            # Single conversation item
            return [{
                "id": data.get("id", AIOSJSONStandards.generate_uuid()),
                "conversation_id": data.get("conversation_id", AIOSJSONStandards.generate_uuid()),
                "role": data.get("role", "user"),
                "content": data.get("content", ""),
                "timestamp": data.get("timestamp", AIOSJSONStandards.generate_timestamp()),
                "metadata": data.get("metadata", {})
            }]
        else:
            raise ValueError("Invalid conversation data format")
    
    @staticmethod
    def _convert_cache_data(data: Any) -> List[Dict]:
        """Convert cache data to AIOS standard"""
        if isinstance(data, dict):
            # Legacy cache format: {"pattern1": {"freq": 5}, "pattern2": {"freq": 3}}
            converted = []
            for pattern, info in data.items():
                # Handle case where info might be a string instead of dict
                if isinstance(info, str):
                    info = {"content": info, "frequency": 1}
                elif not isinstance(info, dict):
                    info = {"content": str(info), "frequency": 1}
                
                converted_item = {
                    "id": AIOSJSONStandards.generate_uuid(),
                    "pattern": pattern,
                    "embedding": info.get("embedding", []),
                    "frequency": info.get("freq", info.get("frequency", 1)),
                    "last_used": info.get("last_used", AIOSJSONStandards.generate_timestamp()),
                    "timestamp": AIOSJSONStandards.generate_timestamp(),
                    "similarity_threshold": info.get("similarity_threshold", 0.8),
                    "compression": info.get("compression", {
                        "ratio": 1.0,
                        "ris_importance": 0.0,
                        "warp_stable": True,
                        "tfid_anchor": 0.618034
                    }),
                    "metadata": {
                        "migrated_from": "legacy_format",
                        "original_type": "cache_entry",
                        "migration_date": AIOSJSONStandards.generate_timestamp()
                    }
                }
                converted.append(converted_item)
            return converted
        elif isinstance(data, list):
            # Already in array format, validate and ensure completeness
            converted = []
            for item in data:
                if isinstance(item, dict):
                    converted_item = {
                        "id": item.get("id", AIOSJSONStandards.generate_uuid()),
                        "pattern": item.get("pattern", ""),
                        "embedding": item.get("embedding", []),
                        "frequency": item.get("frequency", 1),
                        "last_used": item.get("last_used", AIOSJSONStandards.generate_timestamp()),
                        "timestamp": item.get("timestamp", AIOSJSONStandards.generate_timestamp()),
                        "similarity_threshold": item.get("similarity_threshold", 0.8),
                        "compression": item.get("compression", {
                            "ratio": 1.0,
                            "ris_importance": 0.0,
                            "warp_stable": True,
                            "tfid_anchor": 0.618034
                        }),
                        "metadata": item.get("metadata", {
                            "migrated_from": "array_format",
                            "original_type": "cache_entry"
                        })
                    }
                    converted.append(converted_item)
                else:
                    # Handle non-dict items in list (strings, numbers, etc.)
                    converted_item = {
                        "id": AIOSJSONStandards.generate_uuid(),
                        "pattern": str(item),
                        "embedding": [],
                        "frequency": 1,
                        "last_used": AIOSJSONStandards.generate_timestamp(),
                        "timestamp": AIOSJSONStandards.generate_timestamp(),
                        "similarity_threshold": 0.8,
                        "compression": {
                            "ratio": 1.0,
                            "ris_importance": 0.0,
                            "warp_stable": True,
                            "tfid_anchor": 0.618034
                        },
                        "metadata": {
                            "migrated_from": "list_item",
                            "original_type": type(item).__name__,
                            "original_content": str(item)
                        }
                    }
                    converted.append(converted_item)
            return converted
        elif isinstance(data, str):
            # Handle string data - wrap in cache entry format
            return [{
                "id": AIOSJSONStandards.generate_uuid(),
                "pattern": data,
                "embedding": [],
                "frequency": 1,
                "last_used": AIOSJSONStandards.generate_timestamp(),
                "timestamp": AIOSJSONStandards.generate_timestamp(),
                "similarity_threshold": 0.8,
                "compression": {
                    "ratio": 1.0,
                    "ris_importance": 0.0,
                    "warp_stable": True,
                    "tfid_anchor": 0.618034
                },
                "metadata": {
                    "migrated_from": "string_format",
                    "original_type": "plain_text",
                    "original_content": data,
                    "migration_date": AIOSJSONStandards.generate_timestamp()
                }
            }]
        else:
            # Handle other data types (numbers, booleans, etc.)
            return [{
                "id": AIOSJSONStandards.generate_uuid(),
                "pattern": str(data),
                "embedding": [],
                "frequency": 1,
                "last_used": AIOSJSONStandards.generate_timestamp(),
                "timestamp": AIOSJSONStandards.generate_timestamp(),
                "similarity_threshold": 0.8,
                "compression": {
                    "ratio": 1.0,
                    "ris_importance": 0.0,
                    "warp_stable": True,
                    "tfid_anchor": 0.618034
                },
                "metadata": {
                    "migrated_from": "other_format",
                    "original_type": type(data).__name__,
                    "original_content": str(data),
                    "migration_date": AIOSJSONStandards.generate_timestamp()
                }
            }]
    
    @staticmethod
    def _convert_config_data(data: Any) -> List[Dict]:
        """Convert config data to AIOS standard"""
        if isinstance(data, dict):
            # Single config object
            return [{
                "id": AIOSJSONStandards.generate_uuid(),
                "config_name": data.get("config_name", "default_config"),
                "version": data.get("version", "1.0"),
                "parameters": data.get("parameters", {}),
                "models": data.get("models", {})
            }]
        elif isinstance(data, list):
            # Already in array format
            converted = []
            for item in data:
                if isinstance(item, dict):
                    converted_item = {
                        "id": item.get("id", AIOSJSONStandards.generate_uuid()),
                        "config_name": item.get("config_name", "default_config"),
                        "version": item.get("version", "1.0"),
                        "parameters": item.get("parameters", {}),
                        "models": item.get("models", {})
                    }
                    converted.append(converted_item)
            return converted
        else:
            raise ValueError("Invalid config data format")

def main():
    """Test the AIOS JSON Standards"""
    print("🔧 Testing AIOS JSON Standards")
    print("="*50)
    
    # Test conversation message creation
    msg = ConversationMessage.create_message(
        conversation_id="test-conv-123",
        role="user",
        content="Hello, world!",
        metadata={"model": "test-model", "tokens": 5}
    )
    
    print(f"✅ Created conversation message: {msg.id}")
    
    # Test cache entry creation
    cache_entry = CARCacheEntry(
        pattern="test pattern",
        embedding=[0.1, 0.2, 0.3],
        frequency=5,
        last_used="",
        similarity_threshold=0.8,
        compression={"ratio": 4.10, "ris_importance": 119.9, "warp_stable": True, "tfid_anchor": 0.618034}
    )
    
    print(f"✅ Created cache entry: {cache_entry.id}")
    
    # Test data conversion
    legacy_cache = {"pattern1": {"freq": 5}, "pattern2": {"freq": 3}}
    converted_cache = AIOSJSONHandler.convert_to_aios_standard(legacy_cache, AIOSDataType.CAR_CACHE)
    print(f"✅ Converted legacy cache: {len(converted_cache)} entries")
    
    print("\n🎯 AIOS JSON Standards initialized successfully!")

if __name__ == "__main__":
    main()
