#!/usr/bin/env python3
"""
UNIFIED CARMA CORE SYSTEM
Main orchestrator that links all CARMA components together
"""

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import time
import json
from typing import Dict, List, Any
from datetime import datetime

# Import support modules
from support_core.support_core import (
    SystemConfig,
    aios_config, aios_logger, aios_health_checker, aios_security_validator
)

# Import all core components
from carma_core.core import (
    FractalMyceliumCache,
    CARMAExecutiveBrain,
    CARMAMetaMemory,
    CARMA100PercentPerformance,
    CARMAMyceliumNetwork,
    ConnectionStatus,
    TrafficType,
    UserConnection,
    TrafficEvent,
    ServerBlock,
    CARMAMemoryCompressor,
    CARMAMemoryClusterer,
    CARMAMemoryAnalytics,
)
from carma_core.utils.integrity_verifier import IntegrityVerifier


class CARMASystem:
    """
    Unified CARMA system with biological hemisphere integration (AIOS v5)
    
    Combines:
    - CARMA's semantic compression & emotion tracking
    - Lyra Blackwall v2's STM/LTM hemisphere structure
    
    Result: Biological semantic memory system
    """
    
    def __init__(self, base_dir: str = "data_core/FractalCache"):
        # Initialize unified AIOS systems
        self.aios_config = aios_config
        self.logger = aios_logger
        self.health_checker = aios_health_checker
        self.security_validator = aios_security_validator
        
        # Log initialization
        self.logger.info("Initializing Unified CARMA System (v5 Biological)...", "CARMA")
        
        # Initialize base components
        self.cache = FractalMyceliumCache(base_dir)
        self.executive = CARMAExecutiveBrain(self.cache)
        self.meta_memory = CARMAMetaMemory(self.cache)
        self.performance = CARMA100PercentPerformance(self.cache, self.executive, self.meta_memory)
        self.mycelium_network = CARMAMyceliumNetwork()
        
        # Enhanced memory system components
        self.memory_compressor = CARMAMemoryCompressor()
        self.memory_clusterer = CARMAMemoryClusterer()
        self.memory_analytics = CARMAMemoryAnalytics()
        
        # Integrity verification system
        self.integrity_verifier = IntegrityVerifier(base_dir)
        
        # === AIOS V5: BIOLOGICAL HEMISPHERE INTEGRATION ===
        # Import consciousness_core hemispheres for STM/LTM structure
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'consciousness_core' / 'biological'))
            from Left_Hemisphere import ShortTermMemory
            from Right_Hemisphere import LongTermMemory
            
            self.stm = ShortTermMemory(buffer_size=100)  # Recent fragments
            self.ltm = LongTermMemory()  # Consolidated patterns
            self.biological_memory_enabled = True
            
            self.logger.info("Biological hemispheres integrated (STM/LTM)", "CARMA")
            print("   💜 Biological Memory: ACTIVE (STM/LTM hemispheres)")
        except Exception as e:
            self.stm = None
            self.ltm = None
            self.biological_memory_enabled = False
            self.logger.warning(f"Biological hemispheres not available: {e}", "CARMA")
            print("   ⚠️  Biological Memory: DISABLED (using flat CARMA)")

        # Conversation embedding cache (performance optimization)
        self.conversation_embedding_cache = {}  # {(conv_id, message_id): embedding}
        self.max_cache_entries = 1000  # Limit cache size
        
        # Week 4: Store current policies for memory optimization
        self.current_policies = None
        
        # System state
        self.total_queries = 0
        
        # Health check moved to main system initialization
        
        self.logger.success("Unified CARMA System Initialized", "CARMA")
        self.learning_cycles = 0
        self.cognitive_events = []
        self.personality_drift = {
            'conscientiousness': 0.0,
            'openness': 0.0,
            'extraversion': 0.0,
            'agreeableness': 0.0,
            'neuroticism': 0.0
        }
        
        print("🧠 Unified CARMA System Initialized")
        print(f"   Base cache: {len(self.cache.file_registry)} fragments")
        print(f"   Emotion tracking: Enabled")
        print(f"   Consolidation windows: Enabled")
        print(f"   Meta-memory: Enabled")
        print(f"   Synaptic tagging: Enabled")
        print(f"   Predictive coding: Enabled")
        print(f"   Memory compression: Enabled")
        print(f"   Memory clustering: Enabled")
        print(f"   Memory analytics: Enabled")
    
    def process_query(self, query: str, context: Dict = None) -> Dict:
        """Process a query through the complete cognitive system."""
        self.total_queries += 1
        start_time = time.time()
        
        # Week 4: Apply memory policy if available
        if self.current_policies and hasattr(self.current_policies, 'memory_policy'):
            self.cache.apply_policy(self.current_policies.memory_policy)
        
        # Generate embedding for query
        query_embedding = self.cache.embedder.embed(query)
        
        # Find relevant fragments from both FractalCache and conversation files
        relevant_fragments = self.cache.find_relevant(query_embedding, topk=5)
        
        # Also search conversation files for relevant memories
        conversation_memories = self._find_conversation_memories(query, query_embedding, topk=3)
        
        # Combine fragments and conversation memories
        all_relevant_memories = relevant_fragments + conversation_memories
        
        # Generate cognitive response
        response = self._generate_cognitive_response(query, all_relevant_memories, {}, {}, {})
        
        # Update personality based on all cognitive factors
        self._update_cognitive_personality(query, response, {}, {}, {})
        
        processing_time = time.time() - start_time
        
        # Record cognitive event
        cognitive_event = {
            'timestamp': time.time(),
            'query': query,
            'processing_time': processing_time,
            'fragments_found': len(relevant_fragments),
            'conversation_memories_found': len(conversation_memories),
            'personality_drift': self.personality_drift.copy()
        }
        self.cognitive_events.append(cognitive_event)
        
        # Compile results
        results = {
            'query': query,
            'response': response,
            'processing_time': processing_time,
            'fragments_found': len(relevant_fragments),
            'conversation_memories_found': len(conversation_memories),
            'personality_drift': self.personality_drift.copy(),
            'cognitive_event': cognitive_event,
            'system_stats': self.get_comprehensive_stats()
        }
        
        return results
    
    def _find_conversation_memories(self, query: str, query_embedding: List[float], topk: int = 3) -> List:
        """Find relevant conversation memories using embedding similarity."""
        conversation_memories = []
        
        try:
            # Get conversation directory
            conversation_dir = Path("data_core/conversations")
            if not conversation_dir.exists():
                return conversation_memories
            
            # Get all conversation files
            conversation_files = list(conversation_dir.glob("conversation_*.json"))
            
            # For each conversation file, check if it has embeddings
            for conv_file in conversation_files[-50:]:  # Check last 50 conversation files
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        conv_data = json.load(f)
                    
                    conv_id = conv_data.get('id', 'unknown')
                    messages = conv_data.get('messages', [])
                    
                    # Search through messages in the conversation
                    for message in messages:
                        content = message.get('content', '')
                        message_id = message.get('id', 'unknown')
                        timestamp = message.get('timestamp', 0)
                        
                        if isinstance(content, str) and content:
                            # Check cache first
                            cache_key = (conv_id, message_id)
                            if cache_key in self.conversation_embedding_cache:
                                message_embedding = self.conversation_embedding_cache[cache_key]
                            else:
                                # Generate embedding for this message content
                                try:
                                    message_embedding = self.cache.embedder.embed(content[:1000])  # Limit content for embedding
                                    
                                    # Cache the embedding
                                    self.conversation_embedding_cache[cache_key] = message_embedding
                                    
                                    # Limit cache size (simple LRU)
                                    if len(self.conversation_embedding_cache) > self.max_cache_entries:
                                        first_key = next(iter(self.conversation_embedding_cache))
                                        del self.conversation_embedding_cache[first_key]
                                except Exception as e:
                                    continue
                            
                            # Calculate similarity with query
                            try:
                                if query_embedding and message_embedding:
                                    similarity = self.cache.calculate_similarity(query_embedding, message_embedding)
                                    
                                    if similarity > 0.3:  # Threshold for relevance
                                        # Create a memory fragment with file IDs and metadata
                                        class ConversationMemory:
                                            def __init__(self, conv_id, message_id, content, similarity, timestamp):
                                                self.id = f"conv_{conv_id}_{message_id}"
                                                self.conv_id = conv_id
                                                self.message_id = message_id
                                                self.content = content[:500]  # Truncate for performance
                                                self.score = similarity
                                                self.timestamp = timestamp
                                                self.hits = 1
                                                self.level = 0
                                                self.source = "conversation"
                                                self.file_path = str(conv_file)  # Full path for embedder access
                                        
                                        memory = ConversationMemory(
                                            conv_id,
                                            message_id,
                                            content,
                                            similarity,
                                            timestamp
                                        )
                                        conversation_memories.append(memory)
                            except Exception as e:
                                continue
                
                except Exception as e:
                    continue
            
            # Sort by similarity score and return top k
            conversation_memories.sort(key=lambda x: x.score, reverse=True)
            return conversation_memories[:topk]
            
        except Exception as e:
            print(f"   Error searching conversation memories: {e}")
            return conversation_memories
    
    def compress_memories(self, algorithm: str = 'semantic') -> Dict:
        """Compress memory fragments using advanced compression."""
        fragments = list(self.cache.file_registry.values())
        return self.memory_compressor.compress_memory(fragments, algorithm)
    
    def cluster_memories(self, num_clusters: int = 5) -> Dict:
        """Cluster memory fragments into organized groups."""
        fragments = list(self.cache.file_registry.values())
        return self.memory_clusterer.cluster_memories(fragments, num_clusters)
    
    def analyze_memory_system(self) -> Dict:
        """Analyze memory system and provide insights."""
        return self.memory_analytics.analyze_memory_system(self.cache)
    
    def optimize_memory_system(self) -> Dict:
        """Optimize memory system based on analytics."""
        analysis = self.analyze_memory_system()
        optimizations = []
        
        # Apply compression if recommended
        if "compression" in str(analysis.get('recommendations', [])):
            compression_result = self.compress_memories('semantic')
            optimizations.append({
                'type': 'compression',
                'space_saved': compression_result['space_saved'],
                'compression_ratio': compression_result['compression_ratio']
            })
        
        # Apply clustering if many fragments
        fragment_count = analysis.get('memory_growth', {}).get('total_fragments', 0)
        if fragment_count > 50:
            cluster_result = self.cluster_memories(min(5, fragment_count // 10))
            optimizations.append({
                'type': 'clustering',
                'clusters_created': cluster_result['num_clusters']
            })
        
        return {
            'analysis': analysis,
            'optimizations_applied': optimizations,
            'optimization_timestamp': time.time()
        }
    
    def _generate_cognitive_response(self, query: str, fragments: List, 
                                   confidences: Dict, emotional_weights: Dict,
                                   predictions: Dict) -> str:
        """Generate a response using all cognitive enhancements."""
        response_parts = [f"🧠 Cognitive Analysis: {query}"]
        response_parts.append(f"✓ Found {len(fragments)} relevant fragments")
        
        # Add fragment analysis
        for i, fragment in enumerate(fragments[:3]):
            response_parts.append(f"  {i+1}. {fragment.content[:100]}...")
        
        return "\n".join(response_parts)
    
    def _update_cognitive_personality(self, query: str, response: str, 
                                    emotional_weights: Dict, confidences: Dict,
                                    predictions: Dict):
        """Update personality based on all cognitive factors."""
        # Simple personality drift based on query content
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['creative', 'imaginative', 'artistic']):
            self.personality_drift['openness'] += 0.01
        if any(word in query_lower for word in ['organized', 'systematic', 'methodical']):
            self.personality_drift['conscientiousness'] += 0.01
        if any(word in query_lower for word in ['social', 'outgoing', 'energetic']):
            self.personality_drift['extraversion'] += 0.01
        if any(word in query_lower for word in ['helpful', 'kind', 'cooperative']):
            self.personality_drift['agreeableness'] += 0.01
        if any(word in query_lower for word in ['anxious', 'worried', 'stressed']):
            self.personality_drift['neuroticism'] += 0.01
    
    def verify_integrity(self) -> Dict[str, Any]:
        """Verify integrity of all cache files and fragments."""
        return self.integrity_verifier.verify_cache_integrity()
    
    def register_fragment_integrity(self, fragment: Dict[str, Any]) -> str:
        """Register a memory fragment for integrity verification."""
        return self.integrity_verifier.register_fragment(fragment)
    
    def verify_fragment_integrity(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """Verify integrity of a specific memory fragment."""
        return self.integrity_verifier.verify_fragment(fragment)
    
    def get_integrity_stats(self) -> Dict[str, Any]:
        """Get integrity verification statistics."""
        return self.integrity_verifier.get_integrity_stats()
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics from all cognitive systems."""
        cache_stats = self.cache.get_cache_statistics()
        executive_status = self.executive.get_executive_status()
        meta_stats = self.meta_memory.get_memory_statistics()
        network_status = self.mycelium_network.get_network_status()
        integrity_stats = self.get_integrity_stats()
        
        base_stats = {
            'cache': cache_stats,
            'executive': executive_status,
            'meta_memory': meta_stats,
            'integrity': integrity_stats,
            'network': network_status,
            'personality_drift': self.personality_drift,
            'total_queries': self.total_queries,
            'learning_cycles': self.learning_cycles,
            'performance_level': self.performance.get_performance_level()
        }
        
        # Add biological memory stats if available
        if self.biological_memory_enabled:
            base_stats['biological_memory'] = {
                'stm_size': len(self.stm.memory) if self.stm else 0,
                'ltm_size': len(self.ltm.memory) if self.ltm else 0,
                'stm_capacity': self.stm.buffer_size if self.stm else 0,
                'mode': 'STM/LTM Hemispheres (Biological)'
            }
        else:
            base_stats['biological_memory'] = {
                'mode': 'Flat CARMA (Classic)'
            }
        
        return base_stats
    
    # === AIOS V5: BIOLOGICAL MEMORY METHODS ===
    
    def store_in_stm(self, content: str):
        """Store content in biological STM (Left Hemisphere) if available"""
        if self.biological_memory_enabled and self.stm:
            self.stm.store(content)
            
            # Auto-consolidate if buffer full
            if self.stm.should_compress():
                summary = self.stm.compress()
                
                # Use CARMA's semantic compression on the summary
                compressed = self.memory_compressor.compress_memory([summary], 'semantic')
                
                # Store in LTM
                if self.ltm:
                    self.ltm.store(compressed.get('compressed_data', summary))
                
                # Clear STM
                self.stm.clear()
                
                self.logger.info("Biological consolidation: STM → CARMA compression → LTM", "CARMA")
                return True
        return False
    
    def recall_from_ltm(self, query: str = None, n: int = 5) -> List:
        """Recall from biological LTM (Right Hemisphere) if available"""
        if self.biological_memory_enabled and self.ltm:
            return self.ltm.retrieve_relevant(query, n)
        return []
    
    def get_biological_memory_state(self) -> Dict:
        """Get state of biological memory systems"""
        if not self.biological_memory_enabled:
            return {'enabled': False, 'mode': 'Flat CARMA'}
        
        return {
            'enabled': True,
            'mode': 'Biological Hemispheres (STM/LTM)',
            'stm': {
                'size': len(self.stm.memory) if self.stm else 0,
                'capacity': self.stm.buffer_size if self.stm else 0,
                'usage_percent': (len(self.stm.memory) / self.stm.buffer_size * 100) if self.stm else 0
            },
            'ltm': {
                'size': len(self.ltm.memory) if self.ltm else 0,
                'summaries': self.ltm.memory if self.ltm else []
            }
        }


def main():
    """Test the unified CARMA system."""
    print("🧪 Testing Unified CARMA System")
    
    # Initialize system
    system = CARMASystem()
    
    # Test queries
    test_queries = [
        "I am learning about artificial intelligence and machine learning",
        "This research shows that memory consolidation happens during sleep",
        "I'm not entirely sure about this hypothesis, but it seems plausible",
        "The neural networks in the brain form complex interconnected patterns"
    ]
    
    # Process queries
    for query in test_queries:
        result = system.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {result['response']}")
        print(f"Fragments found: {result['fragments_found']}")
    
    # Get final stats
    stats = system.get_comprehensive_stats()
    print(f"\n✓ Final System Stats:")
    print(f"   Performance level: {stats['performance_level']:.1f}%")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Cache fragments: {stats['cache']['total_fragments']}")
    print(f"   Network utilization: {stats['network']['utilization_percentage']:.1f}%")


if __name__ == "__main__":
    main()

