"""
Provenance Logging System
Atomic NDJSON writer for conversation and hypothesis tracking

Schema Version: 1.0
"""

import json
import os
import threading
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# NDJSON Schema Version
SCHEMA_VERSION = "1.0"

# Privacy settings
AUTO_HASH_CONV_ID = True  # Automatically hash conversation IDs for privacy

def hash_conv_id(conv_id: str) -> str:
    """Hash conversation ID for privacy while preserving grouping"""
    if conv_id.startswith('hashed_'):
        return conv_id  # Already hashed
    return f"hashed_{hashlib.sha256(f'aios_conv:{conv_id}'.encode()).hexdigest()[:16]}"

class ProvenanceLogger:
    """
    Atomic NDJSON appender for provenance tracking
    Thread-safe logging for conversation events and hypothesis results
    """
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.lock = threading.Lock()
        
        # Ensure directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self.log_file.exists():
            self.log_file.touch()
    
    def append(self, event: Dict[str, Any]):
        """Atomically append event to NDJSON log"""
        with self.lock:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    def read_all(self) -> list:
        """Read all events from log"""
        events = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        return events
    
    def read_recent(self, n: int = 100) -> list:
        """Read last N events"""
        all_events = self.read_all()
        return all_events[-n:] if len(all_events) > n else all_events

# Global logger instance
_hypothesis_logger = None

def get_hypothesis_logger(log_file: str = 'data_core/analytics/hypotheses.ndjson') -> ProvenanceLogger:
    """Get or create global hypothesis logger"""
    global _hypothesis_logger
    if _hypothesis_logger is None:
        _hypothesis_logger = ProvenanceLogger(log_file)
    return _hypothesis_logger

def log_response_event(logger: ProvenanceLogger,
                      conv_id: str,
                      msg_id: int,
                      question: str,
                      trait: str,
                      response: str,
                      meta: Dict[str, Any],
                      carma: Dict[str, Any],
                      math_weights: Optional[Dict[str, Any]] = None):
    """
    Log a response event to provenance log
    
    Args:
        logger: ProvenanceLogger instance
        conv_id: Conversation ID
        msg_id: Message ID within conversation
        question: User question
        trait: Personality trait
        response: AI response
        meta: Metadata (source, tier, response_type)
        carma: CARMA data (fragments_found, etc.)
        math_weights: Mathematical weight data (optional)
    """
    # Hash conv_id for privacy if enabled
    if AUTO_HASH_CONV_ID:
        conv_id = hash_conv_id(conv_id)
    
    event = {
        'schema_version': SCHEMA_VERSION,
        'event_type': 'response',
        'ts': datetime.now().isoformat(),
        'conv_id': conv_id,
        'msg_id': msg_id,
        'question': question,
        'trait': trait,
        'response': response,
        'meta': meta,
        'carma': carma
    }
    
    # Add math weights if available
    if math_weights:
        event['math_weights'] = math_weights
    
    logger.append(event)

def log_hypothesis_event(logger: ProvenanceLogger,
                        conv_id: str,
                        hypo_id: str,
                        status: str,
                        metric: float,
                        p_value: Optional[float] = None,
                        effect_size: Optional[float] = None,
                        rec: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None):
    """
    Log a hypothesis test event to provenance log
    
    Args:
        logger: ProvenanceLogger instance
        conv_id: Conversation ID
        hypo_id: Hypothesis ID (e.g., H_AIOS_1)
        status: Test status (supported, not_supported, error)
        metric: Measured metric value
        p_value: Statistical p-value (optional)
        effect_size: Effect size measurement (optional)
        rec: Recommendation based on result (optional)
        metadata: Additional metadata (optional)
    """
    # Hash conv_id for privacy if enabled
    if AUTO_HASH_CONV_ID:
        conv_id = hash_conv_id(conv_id)
    
    event = {
        'schema_version': SCHEMA_VERSION,
        'event_type': 'hypothesis_test',
        'ts': datetime.now().isoformat(),
        'conv_id': conv_id,
        'hypo_id': hypo_id,
        'status': status,
        'metric': metric
    }
    
    # Add optional fields
    if p_value is not None:
        event['p_value'] = p_value
    
    if effect_size is not None:
        event['effect_size'] = effect_size
    
    if rec is not None:
        event['rec'] = rec
    
    if metadata:
        event['metadata'] = metadata
    
    logger.append(event)

def log_carma_test_result(logger: ProvenanceLogger,
                         test_id: str,
                         hypo_id: str,
                         result: Dict[str, Any]):
    """
    Log CARMA hypothesis test result
    
    Args:
        logger: ProvenanceLogger instance
        test_id: Test run ID
        hypo_id: Hypothesis ID
        result: Test result dictionary
    """
    event = {
        'ts': datetime.now().isoformat(),
        'test_id': test_id,
        'hypo_id': hypo_id,
        'status': 'supported' if result.get('is_supported', False) else 'not_supported',
        'metric': result.get('metric_value', 0.0),
        'confidence': result.get('confidence', 0.0),
        'data_points': result.get('data_points', 0),
        'rec': self._generate_recommendation(hypo_id, result)
    }
    
    logger.append(event)

def _generate_recommendation(hypo_id: str, result: Dict[str, Any]) -> str:
    """Generate recommendation based on hypothesis result"""
    if result.get('is_supported', False):
        recommendations = {
            'H_AIOS_1': 'Continue using dynamic weighting - quality correlation confirmed',
            'H_AIOS_2': 'Context pressure confirmed - optimize for speed',
            'H_AIOS_3': 'Embedder efficiency confirmed - increase simple query routing',
            'H_AIOS_4': 'Dynamic accumulation working - maintain current logic',
            'H_AIOS_5': 'CARMA advantage confirmed - prioritize fragment retrieval',
            'H_AIOS_6': 'Dreaming equilibrium achieved - maintain dreaming logic'
        }
    else:
        recommendations = {
            'H_AIOS_1': 'Weight-quality correlation weak - recalibrate weight formula',
            'H_AIOS_2': 'Context pressure not significant - review context handling',
            'H_AIOS_3': 'Embedder not fast enough - optimize embedder calls',
            'H_AIOS_4': 'Dynamic accumulation not working - review accumulation logic',
            'H_AIOS_5': 'CARMA not improving quality - improve fragment selection',
            'H_AIOS_6': 'Dreaming not converging - adjust dreaming algorithm'
        }
    
    return recommendations.get(hypo_id, 'No specific recommendation')

def test_provenance_logger():
    """Test provenance logger"""
    print("=== Provenance Logger Test ===\n")
    
    # Create logger
    logger = ProvenanceLogger('data_core/analytics/test_provenance.ndjson')
    
    # Log response event
    print("Logging response event...")
    log_response_event(
        logger,
        conv_id='test_conv_001',
        msg_id=1,
        question='What is AI?',
        trait='general',
        response='AI is artificial intelligence...',
        meta={'source': 'main_model', 'tier': 'moderate_high', 'response_type': 'full_generation'},
        carma={'fragments_found': 3}
    )
    
    # Log hypothesis event
    print("Logging hypothesis event...")
    log_hypothesis_event(
        logger,
        conv_id='test_conv_001',
        hypo_id='H_AIOS_1',
        status='supported',
        metric=0.85,
        p_value=0.01,
        effect_size=0.75,
        rec='Continue using dynamic weighting'
    )
    
    # Read back
    print("\nReading events...")
    events = logger.read_all()
    print(f"Total events: {len(events)}")
    
    for i, event in enumerate(events, 1):
        print(f"\nEvent {i}:")
        print(f"  Type: {event.get('hypo_id', event.get('question', 'Unknown'))}")
        print(f"  Timestamp: {event['ts']}")
    
    print("\n✅ Provenance logger test complete!")

if __name__ == "__main__":
    test_provenance_logger()

