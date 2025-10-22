#!/usr/bin/env python3
"""
CARMA Fractal Mycelium Cache
Extends fractal_core.FractalCache with Psycho-Semantic RAG Loop integration

Week 3: Now extends base FractalCache from fractal_core
Adds psychological features, Ava integration, Big5 analysis
"""

import sys
from pathlib import Path
import time
import json
import random
import hashlib
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))
from support_core.support_core import SystemConfig, SimpleEmbedder
from fractal_core.core import FractalCache


class FractalMyceliumCache(FractalCache):
    """
    Fractal Mycelium Cache with Psycho-Semantic RAG Loop integration.
    
    Extends base FractalCache with:
    - Ava psychological patterns
    - Big 5 personality analysis
    - Tool-augmented retrieval
    - Dynamic prompt generation
    """
    
    def __init__(self, base_dir: str = "data_core/FractalCache"):
        # Initialize base FractalCache
        super().__init__(base_dir)
        
        # Add CARMA-specific psychological features
        # Initialize tool-enabled embedder (Llama-3.2-1B for psychological sensing + tools)
        self.tool_embedder = self._initialize_tool_embedder()
        
        # Embedder already initialized by super(), but keep reference
        # self.embedder from parent
        
        # Registry and links already initialized by super()
        # self.file_registry from parent
        # self.semantic_links from parent
        
        # Psycho-Semantic RAG Loop components
        self.ava_raw_matches_path = Path("ava_raw_matches.txt")
        self.big5_training_path = Path("big5_training_data.json")
        self.ava_progression_path = Path("ava_psychological_progression_analysis.json")
        self.minecraft_chat_path = Path("Data/Minecraft-Server-Chat/clean.json")
        self.psychological_cache = {}
        self.triple_point_matches = []
        self.dynamic_prompt_cache = {}
        self.minecraft_chat_cache = {}
        self.big5_knowledge_base = {}
        self.ava_progression_analysis = {}
        self.hit_weights = {}
        self.path_weights = {}
        self.metrics = {
            'total_fragments': 0,
            'total_hits': 0,
            'cache_hit_rate': 0.0,
            'avg_similarity': 0.0,
            'cross_links': 0
        }
        
        # Base cache already loaded by super()
        # Adding psychological enhancements
        
        print("    + Psycho-Semantic RAG Loop enabled")
        print(f"    + Tool-Enabled Embedder: Llama-3.2-1B-Instruct (Tool-Augmented Retrieval)")
        print(f"    + Big 5 personality analysis")
        print(f"    + Ava behavioral patterns")
    
    def _initialize_tool_embedder(self):
        """Initialize the tool-enabled embedder (Llama-3.2-1B)."""
        return {
            'model_name': 'Llama-3.2-1B-Instruct-GGUF',
            'model_file': 'Llama-3.2-1B-Instruct-Q8_0.gguf',
            'lm_studio_url': 'http://localhost:1234/v1/chat/completions',
            'tools_enabled': True,
            'size_gb': 1.32
        }
    
    def add_content(self, content: str, parent_id: str = None) -> str:
        """Add content to the cache."""
        file_id = self.create_file_id(content, parent_id)
        
        fragment_data = {
            'file_id': file_id,
            'content': content,
            'parent_id': parent_id,
            'level': 0,
            'hits': 0,
            'created': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'specialization': 'general',
            'tags': [],
            'analysis': self.analyze_content(content)
        }
        
        # Generate embedding
        try:
            embedding = self.embedder.embed(content)
            fragment_data['embedding'] = embedding
        except Exception as e:
            print(f"  Embedding failed: {e}")
            fragment_data['embedding'] = None
        
        self.file_registry[file_id] = fragment_data
        self.save_registry()
        
        return file_id
    
    def create_file_id(self, content: str = None, parent_id: str = None, generation_number: int = None, generation_seed: int = None) -> str:
        """Create unique file ID using Generational Architecture format: GEN_X_Y_Z"""
        # Get generation info from CFIA if not provided
        if generation_number is None or generation_seed is None:
            try:
                from luna_cfia_system import LunaCFIASystem
                cfia = LunaCFIASystem()
                generation_number = generation_number or cfia.state.aiiq
                generation_seed = generation_seed or cfia.state.generation_seed
            except ImportError:
                # Fallback if luna_cfia_system is not available
                generation_number = generation_number or 2
                generation_seed = generation_seed or random.randint(1000, 9999)
            except Exception:
                # Fallback for any other error
                generation_number = generation_number or 2
                generation_seed = generation_seed or random.randint(1000, 9999)
        
        # Create fragment index (A, B, C, etc.)
        fragment_index = self._get_next_fragment_index(generation_number, generation_seed)
        
        return f"GEN{generation_number}_{generation_seed}_{fragment_index}"
    
    def _get_next_fragment_index(self, generation_number: int, generation_seed: int) -> str:
        """Get next fragment index for the generation/seed combination"""
        # Count existing fragments for this generation/seed
        pattern = f"GEN{generation_number}_{generation_seed}_"
        existing_fragments = []
        
        for file_path in self.base_dir.glob("GEN*.json"):
            if file_path.stem.startswith(pattern):
                existing_fragments.append(file_path.stem)
        
        # Return next letter in sequence (A, B, C, D, etc.)
        if not existing_fragments:
            return "A"
        
        # Find highest letter and increment
        letters = [frag.split("_")[-1] for frag in existing_fragments]
        if letters:
            last_letter = max(letters)
            next_letter = chr(ord(last_letter) + 1)
            return next_letter
        
        return "A"
    
    def analyze_content(self, content: str) -> Dict:
        """Analyze content for metadata."""
        words = content.split()
        return {
            'word_count': len(words),
            'char_count': len(content),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'sentiment': self.score_valence(content),
            'complexity': len(set(words)) / len(words) if words else 0
        }
    
    def score_valence(self, text: str) -> float:
        """Simple sentiment scoring."""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.0
        
        return (pos_count - neg_count) / (pos_count + neg_count)
    
    def find_relevant(self, query_embedding, topk=3):
        """Find relevant fragments using embedding similarity."""
        if not query_embedding:
            return []
        
        similarities = []
        for frag_id, frag_data in self.file_registry.items():
            if 'embedding' in frag_data and frag_data['embedding']:
                try:
                    similarity = self.calculate_similarity(query_embedding, frag_data['embedding'])
                    similarities.append((frag_id, similarity, frag_data))
                except Exception:
                    continue
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return FragmentResult objects
        class FragmentResult:
            def __init__(self, frag_id, frag_data, score):
                self.id = frag_id
                self.content = frag_data.get('content', '')
                self.score = score
                self.hits = frag_data.get('hits', 0)
                self.level = frag_data.get('level', 0)
        
        return [FragmentResult(fid, data, sim) for fid, sim, data in similarities[:topk]]
    
    def calculate_similarity(self, emb1, emb2):
        """Calculate cosine similarity between embeddings."""
        if not emb1 or not emb2:
            return 0.0
        
        try:
            emb1 = np.array(emb1)
            emb2 = np.array(emb2)
            
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    # === PSYCHO-SEMANTIC RAG LOOP METHODS ===
    
    def load_ava_raw_matches(self):
        """Load Ava raw matches for psychological pattern analysis."""
        if not self.ava_raw_matches_path.exists():
            print(f"  Ava raw matches file not found: {self.ava_raw_matches_path}")
            return []
        
        matches = []
        current_match = {}
        
        with open(self.ava_raw_matches_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith("MATCH"):
                    if current_match:
                        matches.append(current_match)
                    current_match = {
                        'match_id': line,
                        'before': [],
                        'ava_match': '',
                        'after': [],
                        'page': 0,
                        'line': 0
                    }
                elif line.startswith("Page"):
                    # Extract page and line info
                    parts = line.split()
                    if len(parts) >= 2:
                        current_match['page'] = int(parts[1].rstrip(','))
                        current_match['line'] = int(parts[3])
                elif line.startswith("BEFORE:"):
                    current_match['reading_before'] = True
                    current_match['reading_after'] = False
                elif line.startswith("AFTER:"):
                    current_match['reading_before'] = False
                    current_match['reading_after'] = True
                elif line.startswith("AVA MATCH:"):
                    current_match['ava_match'] = line.replace("AVA MATCH:", "").strip()
                    current_match['reading_before'] = False
                    current_match['reading_after'] = False
                elif line and not line.startswith("=") and not line.startswith("-"):
                    if current_match.get('reading_before'):
                        current_match['before'].append(line)
                    elif current_match.get('reading_after'):
                        current_match['after'].append(line)
        
        if current_match:
            matches.append(current_match)
        
        print(f" Loaded {len(matches)} Ava raw matches for psychological analysis")
        return matches
    
    def load_minecraft_chat_patterns(self, sample_size: int = 1000):
        """Load and sample Minecraft chat patterns for efficiency training."""
        if not self.minecraft_chat_path.exists():
            print(f"  Minecraft chat file not found: {self.minecraft_chat_path}")
            return []
        
        # Check cache first
        cache_key = f"minecraft_chat_{sample_size}"
        if cache_key in self.minecraft_chat_cache:
            return self.minecraft_chat_cache[cache_key]
        
        try:
            print(f" Loading Minecraft chat patterns (sampling {sample_size} messages)...")
            
            # Sample from the massive JSON file efficiently
            import random
            chat_patterns = []
            
            with open(self.minecraft_chat_path, 'r', encoding='utf-8') as f:
                # Read first few lines to get structure
                first_line = f.readline().strip()
                if first_line != '[':
                    print("  Invalid JSON structure")
                    return []
                
                # Sample messages efficiently
                message_count = 0
                current_message = ""
                brace_count = 0
                in_content = False
                
                for line in f:
                    current_message += line
                    
                    # Count braces to find complete messages
                    brace_count += line.count('{') - line.count('}')
                    
                    # Check if we have a complete message
                    if brace_count == 0 and current_message.strip().endswith('},'):
                        try:
                            # Remove trailing comma and parse
                            message_json = current_message.rstrip(',\n').strip()
                            if message_json.endswith('}'):
                                parsed_msg = json.loads(message_json)
                                
                                # Extract content for pattern analysis
                                if 'content' in parsed_msg and parsed_msg['content']:
                                    content = parsed_msg['content'].strip()
                                    word_count = len(content.split())
                                    
                                    # Focus on efficient patterns (1-10 words)
                                    if 1 <= word_count <= 10:
                                        chat_patterns.append({
                                            'content': content,
                                            'word_count': word_count,
                                            'username': parsed_msg.get('username', 'unknown'),
                                            'date': parsed_msg.get('date', 'unknown')
                                        })
                                
                                message_count += 1
                                if message_count >= sample_size:
                                    break
                                    
                        except json.JSONDecodeError as e:
                            # Skip malformed JSON entries and continue processing
                            print(f"Warning: Skipping malformed JSON in conversation: {e}")
                        
                        current_message = ""
                        brace_count = 0
            
            # Cache the results
            self.minecraft_chat_cache[cache_key] = chat_patterns
            
            print(f" Loaded {len(chat_patterns)} Minecraft chat patterns for efficiency training")
            print(f" Word count distribution: {self._analyze_word_distribution(chat_patterns)}")
            
            return chat_patterns
            
        except Exception as e:
            print(f" Error loading Minecraft chat patterns: {e}")
            return []
    
    def _analyze_word_distribution(self, patterns):
        """Analyze word count distribution in Minecraft chat patterns."""
        if not patterns:
            return "No patterns"
        
        word_counts = [p['word_count'] for p in patterns]
        avg_words = sum(word_counts) / len(word_counts)
        
        # Count by ranges
        ultra_short = len([w for w in word_counts if w <= 3])
        short = len([w for w in word_counts if 4 <= w <= 6])
        medium = len([w for w in word_counts if 7 <= w <= 10])
        
        return f"avg: {avg_words:.1f}, ultra-short (≤3): {ultra_short}, short (4-6): {short}, medium (7-10): {medium}"
    
    def load_big5_training_data(self):
        """Load Big 5 personality training data for embedder enhancement."""
        if not self.big5_training_path.exists():
            print(f"  Big 5 training data not found: {self.big5_training_path}")
            return {}
        
        try:
            import json
            with open(self.big5_training_path, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            # Extract training examples for embedder
            self.big5_knowledge_base = training_data[0] if training_data else {}
            
            print(f" Loaded Big 5 training data: {self.big5_knowledge_base.get('total_questions', 0)} questions")
            print(f"    Categories: {list(self.big5_knowledge_base.get('categories', {}).keys())}")
            
            return self.big5_knowledge_base
            
        except Exception as e:
            print(f"  Failed to load Big 5 training data: {e}")
            return {}
    
    def load_ava_psychological_progression(self):
        """Load Ava's psychological progression analysis for enhanced behavioral understanding."""
        if not self.ava_progression_path.exists():
            print(f"  Ava psychological progression analysis not found: {self.ava_progression_path}")
            return {}
        
        try:
            import json
            with open(self.ava_progression_path, 'r', encoding='utf-8') as f:
                progression_data = json.load(f)
            
            # Extract progression analysis
            self.ava_progression_analysis = progression_data[0] if progression_data else {}
            
            print(f" Loaded Ava psychological progression analysis")
            print(f"    Behavioral categories: {list(self.ava_progression_analysis.get('behavioral_categories', {}).keys())}")
            print(f"    Training examples: {len(self.ava_progression_analysis.get('training_examples', []))}")
            
            return self.ava_progression_analysis
            
        except Exception as e:
            print(f"  Failed to load Ava psychological progression analysis: {e}")
            return {}
    
    def create_big5_enhanced_prompt(self, user_query: str, matches: List[Dict], minecraft_patterns: List[Dict] = None) -> str:
        """Create Big 5 enhanced prompt with Ava psychological progression analysis and Minecraft chat efficiency patterns."""
        big5_data = self.big5_knowledge_base
        progression_data = self.ava_progression_analysis
        
        if not big5_data and not progression_data:
            # Fallback to basic prompt
            return f"""
Analyze the user query for psychological patterns and match it to Ava behavioral triplets.

USER QUERY: "{user_query}"

AVA MATCHES AVAILABLE: {len(matches)} matches

For each match, analyze the psychological relevance:
- BEFORE: {matches[0]['before'] if matches else 'No matches'}
- AVA MATCH: {matches[0]['ava_match'] if matches else 'No matches'}  
- AFTER: {matches[0]['after'] if matches else 'No matches'}

Return the top 3 most psychologically relevant matches with:
1. Match ID
2. Page number
3. Line number
4. Psychological similarity score (0.0-1.0)
5. Behavioral context analysis

Format as JSON array.
"""
        
        # Create Big 5 enhanced prompt
        big5_context = f"""
You are a Big 5 personality expert analyzing user queries. Use this knowledge base:

BIG 5 PERSONALITY TRAITS:
"""
        
        for trait, info in big5_data.get('categories', {}).items():
            big5_context += f"""
- {trait.upper()}: {info.get('description', '')}
  Sample questions: {', '.join(info.get('sample_questions', [])[:3])}
"""
        
        big5_context += f"""

TRAINING EXAMPLES:
"""
        
        for example in big5_data.get('training_examples', [])[:5]:
            big5_context += f"""
- Question: "{example.get('question', '')}"
  Big 5 Trait: {example.get('big5_trait', '')} (strength: {example.get('trait_strength', 0)})
  Psychological Patterns: {', '.join(example.get('psychological_patterns', []))}
  Luna Response Style: {example.get('luna_response_style', '')}
"""
        
        big5_context += f"""

AVA PSYCHOLOGICAL PROGRESSION ANALYSIS:
"""
        
        if progression_data:
            big5_context += f"""
AVA'S BEHAVIORAL CATEGORIES:
"""
            for category, info in progression_data.get('behavioral_categories', {}).items():
                big5_context += f"""
- {category.upper()}: {info.get('description', '')}
"""
            
            big5_context += f"""

PSYCHOLOGICAL PROGRESSION EXAMPLES:
"""
            for example in progression_data.get('training_examples', [])[:3]:
                big5_context += f"""
- Query: "{example.get('user_query', '')}"
  Big 5 Trait: {example.get('big5_trait', '')}
  Ava Category: {example.get('ava_behavioral_category', '')}
  Scene Context: {example.get('scene_context', '')}
  Dialogue Style: {example.get('dialogue_style', '')}
  Luna Guidance: {example.get('luna_response_guidance', '')}
"""
        
        big5_context += f"""

CURRENT ANALYSIS TASK:
USER QUERY: "{user_query}"

AVA MATCHES AVAILABLE: {len(matches)} matches

Analyze the user query using Big 5 personality knowledge and Ava's psychological progression patterns.

Return JSON with:
- big5_trait: The primary Big 5 trait detected
- trait_strength: Strength score (0.0-1.0)
- psychological_patterns: Array of detected patterns
- ava_behavioral_category: Which Ava category (scene_context, dialogue_style, psychological_progression)
- scene_context: Visual/emotional context
- dialogue_style: Speaking patterns and tactics
- matches: Array of top 3 Ava behavioral matches with psychological_similarity and behavioral_context
- behavioral_synthesis: How to blend multiple matches for complete response
- luna_response_guidance: How Luna should respond based on this analysis

BEHAVIORAL SYNTHESIS INSTRUCTIONS:
When multiple relevant matches are found, synthesize them instead of just selecting the best one:
- Primary Triplet (Dialogue): Best verbal response template
- Secondary Triplet (Action): Most relevant non-verbal action or scene-setting
- Blended Tag: How to combine them (e.g., "[BLENDED_ACTION: Preceded by observing subject]")
- Synthesis Guidance: How Luna should blend verbal and non-verbal elements

Example format:
{{
  "big5_trait": "conscientiousness",
  "trait_strength": 0.85,
  "psychological_patterns": ["task_completion", "organization"],
  "matches": [
    {{
      "match_id": "MATCH 1",
      "psychological_similarity": 0.95,
      "behavioral_context": "Curious questioning pattern"
    }}
  ],
  "luna_response_guidance": "Show direct curiosity about their methods and systems"
}}

EFFICIENCY GUIDANCE:
Target: Concise, intelligent communication style.
Examples of efficient responses:"""
        
        # Add efficiency patterns if available
        if minecraft_patterns:
            # Sample a few examples
            sample_patterns = minecraft_patterns[:10]
            for pattern in sample_patterns:
                big5_context += f"""
- "{pattern['content']}" ({pattern['word_count']} words)"""
        else:
            big5_context += """
- "Machine learning uses algorithms to learn from data." (10 words)
- "AI systems process information to make decisions." (8 words)  
- "be yourself." (2 words)
- "finding your groove, everything clicks." (5 words)
- "nice vibes!" (2 words)"""
        
        big5_context += """
"""
        
        return big5_context
    
    def find_psychological_patterns_tar(self, user_query: str, matches: List[Dict], minecraft_patterns: List[Dict] = None) -> List[Dict]:
        """Find psychological patterns using Big 5 enhanced Tool-Augmented Retrieval (TAR)."""
        # Load Big 5 training data if not already loaded
        if not self.big5_knowledge_base:
            self.load_big5_training_data()
        
        # Load Ava psychological progression analysis if not already loaded
        if not self.ava_progression_analysis:
            self.load_ava_psychological_progression()
        
        # Use Big 5 enhanced prompt with psychological progression analysis and Minecraft patterns
        tool_prompt = self.create_big5_enhanced_prompt(user_query, matches, minecraft_patterns)
        
        try:
            # Call the tool-enabled embedder (Llama-3.2-1B)
            response = self._call_tool_embedder(tool_prompt)
            psychological_matches = self._parse_tar_response(response, matches)
            
            # Sort by psychological similarity
            psychological_matches.sort(key=lambda x: x['psychological_similarity'], reverse=True)
            
            return psychological_matches[:3]
            
        except Exception as e:
            print(f"  TAR analysis failed: {e}")
            # Fallback to simple matching
            return self._fallback_psychological_matching(user_query, matches)
    
    def _call_tool_embedder(self, prompt: str) -> str:
        """Call the tool-enabled embedder (Llama-3.2-1B) for psychological analysis."""
        import requests
        
        payload = {
            "model": "llama-3.2-1b-instruct-abliterated",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a psychological pattern analyzer with behavioral synthesis capabilities. You MUST respond with ONLY valid JSON format. Analyze user queries using Big 5 personality knowledge and Ava's psychological progression patterns. Return JSON with: big5_trait, trait_strength, psychological_patterns, matches array, and behavioral_synthesis object containing primary_triplet, secondary_triplet, blended_tag, and synthesis_guidance. Example: {\"big5_trait\": \"neuroticism\", \"trait_strength\": 0.75, \"psychological_patterns\": [\"anxiety\"], \"matches\": [{\"match_id\": \"MATCH 1\", \"psychological_similarity\": 0.75}], \"behavioral_synthesis\": {\"primary_triplet\": \"Best dialogue\", \"secondary_triplet\": \"Best action\", \"blended_tag\": \"[BLENDED_ACTION: Combined elements]\", \"synthesis_guidance\": \"How to blend them\"}}"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                self.tool_embedder['lm_studio_url'],
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content']
            print(f" LLM Response: {result[:200]}...")
            return result
        except Exception as e:
            print(f"  Tool embedder call failed: {e}")
            return ""
    
    def _parse_tar_response(self, response: str, matches: List[Dict]) -> List[Dict]:
        """Parse the TAR response and extract psychological matches."""
        psychological_matches = []
        
        try:
            import json
            import re
            
            # Clean up the response - remove markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            # Try to extract JSON from the response - handle multiple JSON objects
            json_matches = re.findall(r'\{[^{}]*\}', cleaned_response)
            if not json_matches:
                # Fallback to single JSON object
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    json_matches = [json_match.group(0)]
            
            for json_str in json_matches:
                # Try to parse the JSON
                try:
                    parsed_response = json.loads(json_str)
                    
                    # Handle different response formats
                    if isinstance(parsed_response, dict):
                        if 'matches' in parsed_response:
                            # Format: {"matches": [...]}
                            items = parsed_response['matches']
                        else:
                            # Format: {"match_id": "...", ...}
                            items = [parsed_response]
                    elif isinstance(parsed_response, list):
                        # Format: [...]
                        items = parsed_response
                    else:
                        items = []
                    
                    # Handle Big 5 enhanced response format
                    if 'big5_trait' in parsed_response:
                        # Big 5 enhanced format
                        big5_trait = parsed_response.get('big5_trait', '')
                        trait_strength = parsed_response.get('trait_strength', 0.0)
                        psychological_patterns = parsed_response.get('psychological_patterns', [])
                        luna_guidance = parsed_response.get('luna_response_guidance', '')
                        behavioral_synthesis = parsed_response.get('behavioral_synthesis', {})
                        matches_array = parsed_response.get('matches', [])
                        
                        # Process matches from Big 5 response
                        print(f" DEBUG: Processing {len(matches_array)} matches from LLM response")
                        print(f" DEBUG: Available original matches:")
                        for i, match in enumerate(matches[:3]):  # Show first 3
                            print(f"   {i}: '{match['match_id']}'")
                        for i, item in enumerate(matches_array):
                            if isinstance(item, dict) and 'match_id' in item and 'psychological_similarity' in item:
                                # Find the corresponding match - handle partial matching
                                match_id = item['match_id']
                                print(f" DEBUG: Looking for LLM match_id '{match_id}' in {len(matches)} available matches")
                                
                                match_found = False
                                matched_original = None
                                
                                for match in matches:
                                    # Check if the match_id is contained in the actual match ID
                                    # Handle cases like "MATCH 2" vs "MATCH 3 (Page 21, Line 14)"
                                    if match_id in match['match_id'] or match['match_id'] in match_id:
                                        match_found = True
                                        matched_original = match
                                        print(f" DEBUG: Direct match found: '{match_id}' -> '{match['match_id']}'")
                                        break
                                    elif len(match_id.split()) > 1:
                                        # Extract number from "MATCH 2" and check if it's in the full match ID
                                        match_num = match_id.split()[1]
                                        if match_num in match['match_id']:
                                            match_found = True
                                            matched_original = match
                                            print(f" DEBUG: Number match found: '{match_num}' -> '{match['match_id']}'")
                                            break
                                
                                if match_found and matched_original:
                                        psychological_match = {
                                            'match_id': match['match_id'],
                                            'page': match['page'],
                                            'line': match['line'],
                                            'ava_match': match['ava_match'],
                                            'before_context': match['before'],
                                            'after_context': match['after'],
                                            'psychological_similarity': float(item['psychological_similarity']),
                                            'document_id': f"page_{match['page']}",
                                            'line_number': match['line'],
                                            'behavioral_analysis': item.get('behavioral_context', ''),
                                            'big5_trait': big5_trait,
                                            'trait_strength': trait_strength,
                                            'psychological_patterns': psychological_patterns,
                                            'luna_response_guidance': luna_guidance,
                                            'ava_behavioral_category': parsed_response.get('ava_behavioral_category', ''),
                                            'scene_context': parsed_response.get('scene_context', ''),
                                            'dialogue_style': parsed_response.get('dialogue_style', ''),
                                            'behavioral_synthesis': behavioral_synthesis,
                                            'synthesis_guidance': behavioral_synthesis.get('synthesis_guidance', '') if behavioral_synthesis else '',
                                            'primary_triplet': behavioral_synthesis.get('primary_triplet', '') if behavioral_synthesis else '',
                                            'secondary_triplet': behavioral_synthesis.get('secondary_triplet', '') if behavioral_synthesis else '',
                                            'blended_tag': behavioral_synthesis.get('blended_tag', '') if behavioral_synthesis else ''
                                        }
                                        psychological_matches.append(psychological_match)
                                        break
                    else:
                        # Standard format
                        for item in items:
                            if isinstance(item, dict) and 'match_id' in item and 'psychological_similarity' in item:
                                # Find the corresponding match - handle partial matching
                                match_id = item['match_id']
                                for match in matches:
                                    # Check if the match_id is contained in the actual match ID
                                    # Handle cases like "MATCH 2" vs "MATCH 3 (Page 21, Line 14)"
                                    match_found = False
                                    if match_id in match['match_id'] or match['match_id'] in match_id:
                                        match_found = True
                                    elif len(match_id.split()) > 1:
                                        # Extract number from "MATCH 2" and check if it's in the full match ID
                                        match_num = match_id.split()[1]
                                        if match_num in match['match_id']:
                                            match_found = True
                                    
                                    if match_found:
                                        psychological_match = {
                                            'match_id': match['match_id'],
                                            'page': match['page'],
                                            'line': match['line'],
                                            'ava_match': match['ava_match'],
                                            'before_context': match['before'],
                                            'after_context': match['after'],
                                            'psychological_similarity': float(item['psychological_similarity']),
                                            'document_id': f"page_{match['page']}",
                                            'line_number': match['line'],
                                            'behavioral_analysis': item.get('behavioral_context', '')
                                        }
                                        psychological_matches.append(psychological_match)
                                        break
                
                except json.JSONDecodeError as je:
                    print(f"  JSON decode error: {je}")
                    print(f"   Raw response: {response[:200]}...")
                    # Continue processing other matches even if one fails
                    continue
            
        except Exception as e:
            print(f"  Failed to parse TAR response: {e}")
        
        return psychological_matches
    
    def _fallback_psychological_matching(self, user_query: str, matches: List[Dict]) -> List[Dict]:
        """Fallback psychological matching when TAR fails."""
        psychological_matches = []
        
        # Simple keyword-based matching as fallback
        query_lower = user_query.lower()
        
        for match in matches:
            # Create context for analysis
            context = " ".join(match['before']) + " " + match['ava_match'] + " " + " ".join(match['after'])
            context_lower = context.lower()
            
            # Simple similarity based on keyword overlap
            query_words = set(query_lower.split())
            context_words = set(context_lower.split())
            
            if query_words and context_words:
                similarity = len(query_words.intersection(context_words)) / len(query_words.union(context_words))
                
                if similarity > 0.1:  # Lower threshold for fallback
                    psychological_match = {
                        'match_id': match['match_id'],
                        'page': match['page'],
                        'line': match['line'],
                        'ava_match': match['ava_match'],
                        'before_context': match['before'],
                        'after_context': match['after'],
                        'psychological_similarity': similarity,
                        'document_id': f"page_{match['page']}",
                        'line_number': match['line'],
                        'behavioral_analysis': 'Fallback matching'
                    }
                    psychological_matches.append(psychological_match)
        
        return psychological_matches
    
    def create_dynamic_prompt(self, user_query: str, top_matches: List[Dict]) -> str:
        """Create dynamic prompt for the main model using psychological context."""
        if not top_matches:
            return user_query
        
        # Use the best match for full context
        best_match = top_matches[0]
        
        # Build enhanced psychological context with Big 5 information and behavioral synthesis
        big5_info = ""
        if 'big5_trait' in best_match:
            big5_info = f"""
BIG 5 PERSONALITY ANALYSIS:
- Primary Trait: {best_match['big5_trait'].upper()} (strength: {best_match['trait_strength']:.2f})
- Psychological Patterns: {', '.join(best_match.get('psychological_patterns', []))}
- Luna Response Guidance: {best_match.get('luna_response_guidance', '')}
"""
        
        # Add behavioral synthesis information
        synthesis_info = ""
        if 'behavioral_synthesis' in best_match and best_match.get('behavioral_synthesis'):
            synthesis = best_match['behavioral_synthesis']
            synthesis_info = f"""
BEHAVIORAL SYNTHESIS:
- Primary Triplet (Dialogue): {synthesis.get('primary_triplet', '')}
- Secondary Triplet (Action): {synthesis.get('secondary_triplet', '')}
- Blended Tag: {synthesis.get('blended_tag', '')}
- Synthesis Guidance: {synthesis.get('synthesis_guidance', '')}
"""
        
        psychological_context = f"""
PSYCHOLOGICAL CONTEXT:
- Document: {best_match['document_id']} (Page {best_match['page']}, Line {best_match['line']})
- Ava Pattern: "{best_match['ava_match']}"
- Before Context: {" ".join(best_match['before_context'][-2:])}
- After Context: {" ".join(best_match['after_context'][:2])}
- Psychological Similarity: {best_match['psychological_similarity']:.3f}
{big5_info}{synthesis_info}
LUNA PERSONALITY GUIDANCE (Ava-inspired):
- Use Luna's direct, curious communication style inspired by Ava
- Ask probing questions with genuine curiosity like Ava
- Show emotional intelligence and vulnerability as Luna
- Maintain simple, effective language patterns
- Express college student perspective with philosophical depth
- Incorporate gothic aesthetic with intellectual curiosity
- Apply Big 5 personality insights for more targeted responses
- Blend verbal and non-verbal elements for complete, human-like responses
- Synthesize multiple behavioral patterns for authentic personality expression

USER QUERY: {user_query}
"""
        
        # Cache the dynamic prompt
        prompt_id = hashlib.md5(user_query.encode()).hexdigest()[:8]
        self.dynamic_prompt_cache[prompt_id] = {
            'original_query': user_query,
            'dynamic_prompt': psychological_context,
            'matches_used': top_matches,
            'timestamp': datetime.now().isoformat()
        }
        
        return psychological_context
    
    def retrieve_full_document_context(self, document_id: str, line_number: int) -> Dict:
        """Retrieve full document context and add behavioral tags."""
        try:
            # This would load the actual document page
            # For now, we'll simulate the full document retrieval
            full_document = self._load_document_page(document_id)
            
            # Add behavioral tags using the tool-enabled embedder
            tagged_context = self._add_behavioral_tags(full_document, line_number)
            
            return {
                'document_id': document_id,
                'line_number': line_number,
                'full_context': full_document,
                'tagged_context': tagged_context,
                'retrieval_success': True
            }
            
        except Exception as e:
            print(f"  Document retrieval failed: {e}")
            return {
                'document_id': document_id,
                'line_number': line_number,
                'full_context': '',
                'tagged_context': '',
                'retrieval_success': False,
                'error': str(e)
            }
    
    def _load_document_page(self, document_id: str) -> str:
        """Load the full document page from cache or file system."""
        try:
            # Check if document is in cache
            if document_id in self.file_registry:
                return self.file_registry[document_id].get('content', '')
            
            # Try to load from file system
            doc_path = Path(f"Data/Documents/{document_id}.txt")
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Fallback to generating content based on document_id
            return f"Document {document_id} content loaded from system cache."
        except Exception as e:
            print(f"Error loading document {document_id}: {e}")
            return f"Error loading document {document_id}"
    
    def _add_behavioral_tags(self, document_content: str, line_number: int) -> str:
        """Add behavioral tags to the document content using tool-enabled embedder."""
        tagging_prompt = f"""
Analyze this document content and add behavioral tags for Ava's character.

DOCUMENT CONTENT:
{document_content}

LINE NUMBER: {line_number}

Add the following tags:
- [EMOTION: emotion_name]
- [BEHAVIOR: behavior_type]  
- [CONTEXT: scene_context]
- [TENSION: tension_level]
- [AVA_PATTERN: specific_ava_action]

Return the tagged content with embedded tags.
"""
        
        try:
            response = self._call_tool_embedder(tagging_prompt)
            return response
        except Exception as e:
            print(f"  Behavioral tagging failed: {e}")
            return f"[EMOTION: Neutral] [BEHAVIOR: Dialogue] [CONTEXT: General] {document_content}"
    
    def execute_psycho_semantic_rag_loop(self, user_query: str) -> Dict:
        """Execute the complete Psycho-Semantic RAG Loop."""
        print(f" Executing Psycho-Semantic RAG Loop for: {user_query[:50]}...")
        
        # Stage 1: Load Ava raw matches
        ava_matches = self.load_ava_raw_matches()
        if not ava_matches:
            print("  No Ava matches available, falling back to standard retrieval")
            return {'dynamic_prompt': user_query, 'matches': [], 'stage': 'fallback'}
        
        # Stage 1.5: Load Minecraft chat patterns for efficiency training - DISABLED FOR TESTING
        # minecraft_patterns = self.load_minecraft_chat_patterns(sample_size=500)
        minecraft_patterns = None  # Disable Minecraft patterns
        
        # Stage 2: Find psychological patterns using Tool-Augmented Retrieval
        psychological_matches = self.find_psychological_patterns_tar(user_query, ava_matches, minecraft_patterns)
        print(f" Found {len(psychological_matches)} psychological matches")
        
        # Stage 3: Create dynamic prompt
        dynamic_prompt = self.create_dynamic_prompt(user_query, psychological_matches)
        
        # Stage 4: Extract Big 5 data from psychological matches
        big5_data = {}
        if psychological_matches:
            # Get Big 5 data from the first match (they should all have the same Big 5 analysis)
            first_match = psychological_matches[0]
            if 'big5_trait' in first_match:
                big5_data = {
                    'big5_trait': first_match['big5_trait'],
                    'trait_strength': first_match.get('trait_strength', 0.0),
                    'psychological_patterns': first_match.get('psychological_patterns', []),
                    'luna_response_guidance': first_match.get('luna_response_guidance', ''),
                    'behavioral_synthesis': first_match.get('behavioral_synthesis', {}),
                    'ava_behavioral_category': first_match.get('ava_behavioral_category', ''),
                    'scene_context': first_match.get('scene_context', ''),
                    'dialogue_style': first_match.get('dialogue_style', '')
                }
        
        # Stage 5: Prepare for main model
        result = {
            'dynamic_prompt': dynamic_prompt,
            'matches': psychological_matches,
            'stage': 'psycho_semantic',
            'best_document': psychological_matches[0]['document_id'] if psychological_matches else None,
            'ava_personality_applied': True,
            **big5_data  # Include all Big 5 data at the top level
        }
        
        print(f" Psycho-Semantic RAG Loop complete - Best document: {result['best_document']}")
        return result
    
    def load_registry(self):
        """Load registry from disk."""
        registry_file = self.base_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    self.file_registry = data.get('file_registry', {})
                    self.semantic_links = data.get('semantic_links', {})
                    self.hit_weights = data.get('hit_weights', {})
                    self.path_weights = data.get('path_weights', {})
                    self.metrics = data.get('metrics', self.metrics)
            except Exception as e:
                print(f"  Error loading registry: {e}")
    
    def save_registry(self):
        """Save registry to disk."""
        registry_file = self.base_dir / "registry.json"
        try:
            # Ensure directory exists
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            data = {
                'file_registry': self.file_registry,
                'semantic_links': self.semantic_links,
                'hit_weights': self.hit_weights,
                'path_weights': self.path_weights,
                'metrics': self.metrics
            }
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  Error saving registry: {e}")
            # Log error but don't crash - registry saves are non-critical
            from support_core.support_core import aios_logger
            aios_logger.error(f"Registry save failed: {e}", "CARMA")
    
    def get_cache_statistics(self) -> Dict:
        """Get cache statistics."""
        return {
            'total_fragments': len(self.file_registry),
            'cross_links': len(self.semantic_links),
            'cache_hit_rate': self.metrics.get('cache_hit_rate', 0.0),
            'avg_similarity': self.metrics.get('avg_similarity', 0.0)
        }

