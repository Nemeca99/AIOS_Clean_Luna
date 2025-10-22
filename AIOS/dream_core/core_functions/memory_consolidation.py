#!/usr/bin/env python3
"""
Memory Consolidation - Core memory consolidation functionality
Handles conversation fragment consolidation and memory merging
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class MemoryConsolidationManager:
    """Manages memory consolidation operations"""
    
    def __init__(self, aios_system=None):
        self.aios_system = aios_system
        self.consolidated_count = 0
        self.processed_files = 0
    
    def consolidate_conversation_fragments(self, similarity_threshold: float = 0.8, 
                                          verbose: bool = False) -> Dict[str, Any]:
        """
        Consolidate conversation fragments during dream state.
        
        Args:
            similarity_threshold: Similarity threshold for grouping (0.0-1.0)
            verbose: Enable verbose output
            
        Returns:
            Dictionary with consolidation results
        """
        print(f"🌙 Starting Conversation Fragment Consolidation")
        print(f"   Similarity Threshold: {similarity_threshold}")
        
        try:
            conversation_dir = Path("data_core/conversations")
            if not conversation_dir.exists():
                return {"status": "error", "error": "No conversation directory found"}
            
            conversation_files = list(conversation_dir.glob("conversation_*.json"))
            consolidated_count = 0
            
            for conv_file in conversation_files:
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        conv_data = json.load(f)
                    
                    messages = conv_data.get('messages', [])
                    if len(messages) < 2:
                        continue
                    
                    # Group similar messages together
                    consolidated_messages = []
                    current_group = [messages[0]]
                    
                    for i in range(1, len(messages)):
                        current_message = messages[i]
                        last_message = current_group[-1]
                        
                        # Simple similarity check
                        current_content = current_message.get('content', '').lower()
                        last_content = last_message.get('content', '').lower()
                        
                        # Check for similar content patterns
                        words_current = set(current_content.split())
                        words_last = set(last_content.split())
                        
                        if words_current and words_last:
                            similarity = len(words_current.intersection(words_last)) / len(words_current.union(words_last))
                            
                            if similarity > similarity_threshold:
                                # Merge messages
                                current_group.append(current_message)
                            else:
                                # Consolidate current group and start new one
                                if len(current_group) > 1:
                                    consolidated_msg = self.merge_message_group(current_group)
                                    consolidated_messages.append(consolidated_msg)
                                    consolidated_count += len(current_group) - 1
                                else:
                                    consolidated_messages.append(current_group[0])
                                current_group = [current_message]
                        else:
                            # No content similarity, keep separate
                            if len(current_group) > 1:
                                consolidated_msg = self.merge_message_group(current_group)
                                consolidated_messages.append(consolidated_msg)
                                consolidated_count += len(current_group) - 1
                            else:
                                consolidated_messages.append(current_group[0])
                            current_group = [current_message]
                    
                    # Handle final group
                    if len(current_group) > 1:
                        consolidated_msg = self.merge_message_group(current_group)
                        consolidated_messages.append(consolidated_msg)
                        consolidated_count += len(current_group) - 1
                    else:
                        consolidated_messages.append(current_group[0])
                    
                    # Update conversation with consolidated messages
                    conv_data['messages'] = consolidated_messages
                    conv_data['consolidated_at'] = datetime.now().isoformat()
                    conv_data['original_message_count'] = len(messages)
                    conv_data['consolidated_message_count'] = len(consolidated_messages)
                    
                    # Save consolidated conversation
                    with open(conv_file, 'w', encoding='utf-8') as f:
                        json.dump(conv_data, f, indent=2, ensure_ascii=False)
                    
                    if verbose:
                        print(f"   Consolidated {conv_file.name}: {len(messages)} -> {len(consolidated_messages)} messages")
                
                except Exception as e:
                    if verbose:
                        print(f"   Error consolidating {conv_file.name}: {e}")
                    continue
            
            print(f"   Conversation consolidation complete: {consolidated_count} messages consolidated")
            
            self.consolidated_count = consolidated_count
            self.processed_files = len(conversation_files)
            
            return {
                "status": "success",
                "consolidated_messages": consolidated_count,
                "processed_files": len(conversation_files)
            }
            
        except Exception as e:
            print(f"❌ Conversation consolidation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def merge_message_group(self, messages: List[Dict]) -> Dict:
        """
        Merge a group of similar messages into one consolidated message.
        
        Args:
            messages: List of message dictionaries to merge
            
        Returns:
            Consolidated message dictionary
        """
        if not messages:
            return {}
        
        # Use the first message as base
        consolidated = messages[0].copy()
        
        # Merge content
        contents = [msg.get('content', '') for msg in messages if msg.get('content')]
        if len(contents) > 1:
            # Combine similar content, removing duplicates
            unique_contents = []
            for content in contents:
                if content not in unique_contents:
                    unique_contents.append(content)
            consolidated['content'] = ' | '.join(unique_contents)
        
        # Update metadata
        consolidated['consolidated_from'] = [msg.get('id', 'unknown') for msg in messages]
        consolidated['consolidated_count'] = len(messages)
        consolidated['id'] = f"consolidated_{consolidated.get('id', 'unknown')}"
        
        return consolidated
    
    def consolidate_carma_fragments(self, max_superfrags: int = 10,
                                   min_component_size: int = 1,
                                   summary_tokens: int = 200,
                                   crosslink_threshold: float = 0.0) -> Dict[str, Any]:
        """
        Consolidate CARMA memory fragments into super-fragments.
        
        Args:
            max_superfrags: Maximum super-fragments to create
            min_component_size: Minimum fragments per super-fragment
            summary_tokens: Tokens for summary generation
            crosslink_threshold: Similarity threshold for cross-linking
            
        Returns:
            Dictionary with consolidation results
        """
        try:
            if not self.aios_system or not hasattr(self.aios_system, 'carma_system'):
                return {"status": "error", "error": "CARMA system not available"}
            
            # Perform dream cycle consolidation
            result = self.aios_system.carma_system.performance.perform_dream_cycle(
                max_superfrags=max_superfrags,
                min_component_size=min_component_size,
                summary_tokens=summary_tokens,
                crosslink_threshold=crosslink_threshold
            )
            
            return {
                "status": "success",
                "superfrags_created": result.get('superfrags_created', 0),
                "fragments_processed": result.get('fragments_processed', 0),
                "time_taken": result.get('time', 0.0)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_consolidation_stats(self) -> Dict[str, Any]:
        """Get consolidation statistics."""
        stats = {
            "consolidated_count": self.consolidated_count,
            "processed_files": self.processed_files
        }
        
        # Add CARMA fragment count if available
        if self.aios_system and hasattr(self.aios_system, 'carma_system'):
            try:
                fragment_count = len(self.aios_system.carma_system.cache.file_registry)
                stats["carma_fragments"] = fragment_count
            except AttributeError as e:
                # CARMA system may not be initialized or have cache
                stats["carma_fragments"] = 0
                print(f"Note: CARMA fragments not available: {e}")
        
        return stats
    
    def analyze_memory_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in memory fragments.
        
        Returns:
            Dictionary with pattern analysis
        """
        try:
            if not self.aios_system or not hasattr(self.aios_system, 'carma_system'):
                return {"status": "error", "error": "CARMA system not available"}
            
            fragments = self.aios_system.carma_system.cache.file_registry
            
            # Analyze specializations
            specializations = {}
            tags = {}
            levels = {}
            
            for _, frag_data in fragments.items():
                # Count specializations
                spec = frag_data.get('specialization', 'unknown')
                specializations[spec] = specializations.get(spec, 0) + 1
                
                # Count tags
                for tag in frag_data.get('tags', []):
                    tags[tag] = tags.get(tag, 0) + 1
                
                # Count levels
                level = frag_data.get('level', 0)
                levels[level] = levels.get(level, 0) + 1
            
            return {
                "status": "success",
                "total_fragments": len(fragments),
                "specializations": specializations,
                "top_tags": sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10],
                "levels": levels
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_memory_health(self) -> Dict[str, Any]:
        """
        Get memory system health metrics.
        
        Returns:
            Dictionary with health metrics
        """
        try:
            if not self.aios_system or not hasattr(self.aios_system, 'carma_system'):
                return {"status": "error", "error": "CARMA system not available"}
            
            fragments = self.aios_system.carma_system.cache.file_registry
            
            # Calculate metrics
            total_fragments = len(fragments)
            base_fragments = sum(1 for f in fragments.values() if f.get('level', 0) == 0)
            super_fragments = sum(1 for f in fragments.values() if f.get('level', 0) > 0)
            
            # Calculate average access count
            access_counts = [f.get('access_count', 0) for f in fragments.values()]
            avg_access = sum(access_counts) / max(len(access_counts), 1)
            
            # Calculate consolidation ratio
            consolidation_ratio = super_fragments / max(total_fragments, 1)
            
            return {
                "status": "healthy",
                "total_fragments": total_fragments,
                "base_fragments": base_fragments,
                "super_fragments": super_fragments,
                "average_access_count": avg_access,
                "consolidation_ratio": consolidation_ratio,
                "needs_consolidation": base_fragments > 100
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

