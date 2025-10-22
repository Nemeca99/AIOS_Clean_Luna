#!/usr/bin/env python3
"""
Timestamp validation utilities for AIOS system
"""

import time
from datetime import datetime
from typing import Any, Dict, Union

def validate_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and fix timestamps in data to prevent future timestamps
    
    Args:
        data: Dictionary containing timestamp fields
        
    Returns:
        Dictionary with validated timestamps
    """
    current_time = time.time()
    
    # Common timestamp field names
    timestamp_fields = [
        'timestamp', 'create_time', 'update_time', 'last_updated', 
        'created_at', 'updated_at', 'last_accessed', 'start_time', 
        'end_time', 'created', 'modified'
    ]
    
    for field in timestamp_fields:
        if field in data and data[field] is not None:
            try:
                # Convert to float if it's a string
                if isinstance(data[field], str):
                    data[field] = float(data[field])
                
                # Check if timestamp is in the future
                if data[field] > current_time:
                    print(f"WARNING: Future timestamp detected in field '{field}': {data[field]} -> {current_time}")
                    data[field] = current_time
                    
            except (ValueError, TypeError):
                # If conversion fails, set to current time
                print(f"WARNING: Invalid timestamp in field '{field}': {data[field]} -> {current_time}")
                data[field] = current_time
    
    return data

def validate_message_timestamps(messages: list) -> list:
    """
    Validate timestamps in a list of messages
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        List of messages with validated timestamps
    """
    current_time = time.time()
    
    for message in messages:
        if 'timestamp' in message and message['timestamp'] is not None:
            try:
                if isinstance(message['timestamp'], str):
                    message['timestamp'] = float(message['timestamp'])
                
                if message['timestamp'] > current_time:
                    print(f"WARNING: Future message timestamp: {message['timestamp']} -> {current_time}")
                    message['timestamp'] = current_time
                    
            except (ValueError, TypeError):
                print(f"WARNING: Invalid message timestamp: {message['timestamp']} -> {current_time}")
                message['timestamp'] = current_time
    
    return messages

def get_current_timestamp() -> float:
    """Get current Unix timestamp"""
    return time.time()

def get_current_iso_timestamp() -> str:
    """Get current ISO format timestamp"""
    return datetime.now().isoformat()

def format_timestamp(timestamp: Union[float, str]) -> str:
    """Format timestamp for display"""
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "Invalid timestamp"
