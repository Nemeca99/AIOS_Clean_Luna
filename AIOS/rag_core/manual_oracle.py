"""
Manual Oracle System
Repurposes RAG core as a bulletproof manual lookup system for the audit system.
Provides exact citations and byte-offset lookups with integrity verification.
"""

import json
import hashlib
import mmap
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
import numpy as np

# Configure ALL cache/temp directories inside L:\ BEFORE torch/transformers import
ORACLE_CACHE = Path(__file__).parent / '.cache'
ORACLE_CACHE.mkdir(exist_ok=True)
TEMP_DIR = Path(__file__).parent.parent / 'temp'
TEMP_DIR.mkdir(exist_ok=True)

os.environ['HF_HOME'] = str(ORACLE_CACHE)
os.environ['TORCH_HOME'] = str(ORACLE_CACHE)
os.environ['TEMP'] = str(TEMP_DIR)
os.environ['TMP'] = str(TEMP_DIR)
# Disable CUDA to avoid pynvml warnings
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Lazy imports for heavy dependencies
# from sentence_transformers import SentenceTransformer
# import faiss


class ManualOracle:
    """
    Bulletproof manual lookup system that serves as the "truth" for audit findings.
    
    Features:
    - Byte-offset based lookups (no line number drift)
    - Section checksums for integrity verification
    - Anchor-based citations with subsystem mapping
    - Sparse embeddings for ambiguous queries only
    - Graceful ABSTAIN on hash mismatches
    """
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.manual_path = self.repo_root / "AIOS_MANUAL.md"
        self.toc_path = self.repo_root / "MANUAL_TOC.md"
        
        # Oracle database paths
        self.oracle_dir = self.repo_root / "rag_core" / "manual_oracle"
        self.oracle_dir.mkdir(exist_ok=True)
        
        self.index_file = self.oracle_dir / "oracle_index.json"
        self.embeddings_file = self.oracle_dir / "section_embeddings.json"
        
        # Memory-mapped manual for O(1) lookups
        self.manual_mmap = None
        self.manual_file = None
        
        # Oracle data
        self.oracle_index = []
        self.section_embeddings = {}
        self.embedder = None
        
        print("Initializing Manual Oracle System...")
        self._initialize_oracle()
    
    def _initialize_oracle(self):
        """Initialize the oracle system with integrity checks"""
        # Check if manual files exist
        if not self.manual_path.exists():
            raise FileNotFoundError(f"Manual not found: {self.manual_path}")
        if not self.toc_path.exists():
            raise FileNotFoundError(f"TOC not found: {self.toc_path}")
        
        # Load oracle index
        self._load_oracle_index()
        
        # Verify manual integrity
        if not self._verify_manual_integrity():
            print("Manual integrity check failed - rebuilding oracle...")
            self._rebuild_oracle()
        
        # Initialize memory mapping
        self._init_memory_mapping()
        
        # Initialize embedding model (lightweight)
        self._init_embedder()
        
        print(f"Oracle initialized: {len(self.oracle_index)} sections indexed")
    
    def _load_oracle_index(self):
        """Load the oracle index with integrity metadata"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.oracle_index = data.get('sections', [])
                self.manual_sha256 = data.get('manual_sha256', '')
                self.toc_sha256 = data.get('toc_sha256', '')
            except Exception as e:
                print(f"Error loading oracle index: {e}")
                self.oracle_index = []
                self.manual_sha256 = ''
                self.toc_sha256 = ''
        else:
            self.oracle_index = []
            self.manual_sha256 = ''
            self.toc_sha256 = ''
    
    def _save_oracle_index(self):
        """Save the oracle index with integrity metadata"""
        try:
            # Calculate current hashes
            manual_hash = self._calculate_file_hash(self.manual_path)
            toc_hash = self._calculate_file_hash(self.toc_path)
            
            data = {
                'manual_sha256': manual_hash,
                'toc_sha256': toc_hash,
                'sections': self.oracle_index,
                'generated_at': str(Path().cwd())  # Simple timestamp
            }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving oracle index: {e}")
    
    def _verify_manual_integrity(self) -> bool:
        """Verify that manual and TOC haven't changed since last indexing"""
        if not self.oracle_index:
            return False
        
        # Load stored hashes from index
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stored_manual_hash = data.get('manual_sha256')
            stored_toc_hash = data.get('toc_sha256')
            
            if not stored_manual_hash or not stored_toc_hash:
                return False
            
            # Calculate current hashes
            current_manual_hash = self._calculate_file_hash(self.manual_path)
            current_toc_hash = self._calculate_file_hash(self.toc_path)
            
            return (stored_manual_hash == current_manual_hash and 
                   stored_toc_hash == current_toc_hash)
        
        except Exception:
            return False
    
    def _rebuild_oracle(self):
        """Rebuild the oracle index from current manual and TOC"""
        print("Rebuilding oracle index...")
        
        # Parse TOC to extract section information
        self._parse_toc_sections()
        
        # Extract anchors and calculate byte offsets
        self._extract_manual_anchors()
        
        # Calculate section checksums
        self._calculate_section_checksums()
        
        # Save the rebuilt index
        self._save_oracle_index()
        
        print(f"Oracle rebuilt: {len(self.oracle_index)} sections indexed")
    
    def _parse_toc_sections(self):
        """Parse TOC to extract section structure"""
        if not self.toc_path.exists():
            return
        
        try:
            with open(self.toc_path, 'r', encoding='utf-8') as f:
                toc_content = f.read()
            
            # Parse table format: | Line | Section | Topic |
            in_table = False
            for line in toc_content.split('\n'):
                line = line.strip()
                
                # Skip empty lines and headers
                if not line or line.startswith('#') or line.startswith('**'):
                    continue
                
                # Detect table start
                if '| Line |' in line and '| Section |' in line:
                    in_table = True
                    continue
                
                # Skip table separator
                if line.startswith('|---') or line.startswith('|------'):
                    continue
                
                # Parse table rows
                if in_table and line.startswith('|'):
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4 and parts[1].isdigit():
                        line_num = int(parts[1])
                        section_num = parts[2]
                        section_title = parts[3]
                        
                        # Skip if section title is empty or just formatting
                        if not section_title or section_title in ['**PART 1**', '**PART 2**', '**PART 3**']:
                            continue
                        
                        # Generate anchor ID from section title
                        anchor_id = self._generate_anchor_id(section_title)
                        
                        # Map to subsystems based on section content
                        subsystems = self._map_section_to_subsystems(section_title, section_num)
                        
                        self.oracle_index.append({
                            'anchor': anchor_id,
                            'section_number': section_num,
                            'title': section_title,
                            'line_number': line_num,
                            'subsystems': subsystems,
                            'byte_start': None,  # Will be calculated
                            'byte_end': None,    # Will be calculated
                            'section_sha256': None,  # Will be calculated
                            'manual_sha256': None    # Will be calculated
                        })
                
                # Stop at end of table
                if in_table and line.startswith('---') and '|' not in line:
                    in_table = False
        
        except Exception as e:
            print(f"Error parsing TOC: {e}")
    
    def _generate_anchor_id(self, title: str) -> str:
        """Generate kebab-case anchor ID from section title"""
        # Convert to lowercase, replace spaces/special chars with dots
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '.', anchor)
        anchor = anchor.strip('.')
        
        # Add subsystem prefix for better organization
        if 'luna' in anchor:
            return f"luna.{anchor}"
        elif 'carma' in anchor:
            return f"carma.{anchor}"
        elif 'fractal' in anchor:
            return f"fractal.{anchor}"
        elif 'audit' in anchor:
            return f"audit.{anchor}"
        elif 'dream' in anchor:
            return f"dream.{anchor}"
        else:
            return anchor
    
    def _map_section_to_subsystems(self, title: str, section_num: str) -> List[str]:
        """Map section to relevant subsystems"""
        subsystems = []
        title_lower = title.lower()
        section_lower = section_num.lower()
        
        # Map based on content
        if any(word in title_lower for word in ['luna', 'personality', 'inference', 'arbiter']):
            subsystems.extend(['luna_core'])
        if any(word in title_lower for word in ['carma', 'memory', 'fractal', 'cache']):
            subsystems.extend(['carma_core'])
        if any(word in title_lower for word in ['fractal', 'routing', 'allocation', 'knapsack']):
            subsystems.extend(['fractal_core'])
        if any(word in title_lower for word in ['audit', 'v3', 'sovereign', 'self-healing']):
            subsystems.extend(['main_core'])
        if any(word in title_lower for word in ['dream', 'consolidation', 'cycle']):
            subsystems.extend(['dream_core'])
        if any(word in title_lower for word in ['data', 'storage', 'database']):
            subsystems.extend(['data_core'])
        if any(word in title_lower for word in ['streamlit', 'ui', 'dashboard']):
            subsystems.extend(['streamlit_core'])
        
        # Default to general if no specific mapping
        if not subsystems:
            subsystems = ['general']
        
        return subsystems
    
    def _extract_manual_anchors(self):
        """Extract anchor positions and calculate byte offsets"""
        if not self.manual_path.exists():
            return
        
        try:
            with open(self.manual_path, 'r', encoding='utf-8') as f:
                manual_content = f.read()
            
            # Find heading positions and calculate byte offsets
            for section in self.oracle_index:
                anchor = section['anchor']
                line_num = section['line_number']
                
                # Calculate byte offset for this line
                byte_start = self._line_to_byte_offset(manual_content, line_num)
                byte_end = self._find_section_end_byte(manual_content, byte_start)
                
                section['byte_start'] = byte_start
                section['byte_end'] = byte_end
        
        except Exception as e:
            print(f"Error extracting manual anchors: {e}")
    
    def _line_to_byte_offset(self, content: str, line_num: int) -> int:
        """Convert line number to byte offset (UTF-8 aware)"""
        lines = content.split('\n')
        if line_num <= 0 or line_num > len(lines):
            return 0
        
        # Calculate bytes for lines before target line (UTF-8 aware)
        bytes_before = 0
        for i in range(line_num - 1):
            bytes_before += len(lines[i].encode('utf-8')) + 1  # +1 for newline
        
        return bytes_before
    
    def _find_section_end_byte(self, content: str, start_byte: int) -> int:
        """Find the end byte of a section (next heading or end of file)"""
        # Look for next heading pattern after start position
        heading_pattern = r'^#{1,6}\s+'
        
        # Split content into lines and find the section
        lines = content.split('\n')
        start_line = content[:start_byte].count('\n')
        
        # Find next heading at same or higher level
        for i in range(start_line + 1, len(lines)):
            if re.match(heading_pattern, lines[i]):
                # Calculate byte offset for this line
                return self._line_to_byte_offset(content, i + 1)
        
        # If no next heading, use end of file
        return len(content)
    
    def _calculate_section_checksums(self):
        """Calculate SHA256 checksums for each section"""
        if not self.manual_path.exists():
            return
        
        try:
            with open(self.manual_path, 'r', encoding='utf-8') as f:
                manual_content = f.read()
            
            # Calculate overall manual hash
            manual_hash = hashlib.sha256(manual_content.encode('utf-8')).hexdigest()
            
            for section in self.oracle_index:
                if section['byte_start'] is not None and section['byte_end'] is not None:
                    # Extract section content
                    section_content = manual_content[section['byte_start']:section['byte_end']]
                    
                    # Calculate section hash
                    section_hash = hashlib.sha256(section_content.encode('utf-8')).hexdigest()
                    
                    section['section_sha256'] = section_hash
                    section['manual_sha256'] = manual_hash
        
        except Exception as e:
            print(f"Error calculating section checksums: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except Exception:
            return ""
    
    def _init_memory_mapping(self):
        """Initialize memory mapping for fast lookups"""
        try:
            self.manual_file = open(self.manual_path, 'rb')
            self.manual_mmap = mmap.mmap(self.manual_file.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception as e:
            print(f"Warning: Could not initialize memory mapping: {e}")
            self.manual_file = None
            self.manual_mmap = None
    
    def _init_embedder(self):
        """Initialize lightweight embedding model for ambiguous queries"""
        # Embedder disabled - Oracle uses regex-only search (faster, no heavy dependencies)
        self.embedder = None
        self.embedding_dim = None
        self.embedding_model = None
        self.embedding_device = None
    
    def lookup_section(self, anchor: str, verify_integrity: bool = True) -> Optional[Dict[str, Any]]:
        """
        Lookup a section by anchor with integrity verification
        
        Returns:
        - Section data with content if found and verified
        - None if not found or integrity check fails
        """
        # Find section in index
        section = None
        for s in self.oracle_index:
            if s['anchor'] == anchor:
                section = s
                break
        
        if not section:
            return None
        
        # Verify integrity if requested
        if verify_integrity:
            if not self._verify_section_integrity(section):
                print(f"Integrity check failed for section: {anchor}")
                return None
        
        # Extract section content using byte offsets
        if self.manual_mmap and section['byte_start'] is not None:
            try:
                content = self.manual_mmap[section['byte_start']:section['byte_end']].decode('utf-8')
                section_copy = section.copy()
                section_copy['content'] = content
                return section_copy
            except Exception as e:
                print(f"Error reading section content: {e}")
        
        return None
    
    def _verify_section_integrity(self, section: Dict[str, Any]) -> bool:
        """Verify that a section's content matches its stored checksum"""
        if not self.manual_mmap or section['byte_start'] is None:
            return False
        
        try:
            # Extract current section content
            current_content = self.manual_mmap[section['byte_start']:section['byte_end']].decode('utf-8')
            
            # Calculate current hash
            current_hash = hashlib.sha256(current_content.encode('utf-8')).hexdigest()
            
            # Compare with stored hash
            return current_hash == section.get('section_sha256')
        
        except Exception:
            return False
    
    def get_subsystem_sections(self, subsystem: str) -> List[Dict[str, Any]]:
        """Get all sections relevant to a subsystem"""
        sections = []
        for section in self.oracle_index:
            if subsystem in section.get('subsystems', []):
                sections.append(section)
        return sections
    
    def search_sections(self, query: str, subsystem: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search sections using exact matching first, embeddings second
        
        Returns sections with content and relevance scores
        """
        # First pass: exact text matching
        exact_matches = self._exact_text_search(query, subsystem)
        if exact_matches:
            return exact_matches[:top_k]
        
        # Second pass: embedding search (if embedder available)
        if self.embedder:
            return self._embedding_search(query, subsystem, top_k)
        
        return []
    
    def _exact_text_search(self, query: str, subsystem: str = None) -> List[Dict[str, Any]]:
        """Exact text search in section titles and content"""
        matches = []
        query_lower = query.lower()
        
        for section in self.oracle_index:
            # Filter by subsystem if specified
            if subsystem and subsystem not in section.get('subsystems', []):
                continue
            
            # Check title match
            title_match = query_lower in section['title'].lower()
            
            # Check content match and extract content
            content_match = False
            content = ""
            if self.manual_mmap and section.get('byte_start') is not None and section.get('byte_end') is not None:
                try:
                    content = self.manual_mmap[section['byte_start']:section['byte_end']].decode('utf-8')
                    content_match = query_lower in content.lower()
                except Exception:
                    pass
            
            if title_match or content_match:
                score = 1.0 if title_match else 0.8  # Title matches get higher score
                section_copy = section.copy()
                section_copy['content'] = content  # ADD CONTENT!
                section_copy['search_score'] = score
                section_copy['match_type'] = 'title' if title_match else 'content'
                matches.append(section_copy)
        
        # Sort by score
        matches.sort(key=lambda x: x['search_score'], reverse=True)
        return matches
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text using local SentenceTransformers"""
        if not self.embedder:
            return None
        
        try:
            # Local embedding (6ms vs 2000ms for API!)
            embedding = self.embedder.encode(text[:512], convert_to_numpy=True, show_progress_bar=False)
            return embedding / np.linalg.norm(embedding)  # Normalize
        except Exception as e:
            return None
    
    def _embedding_search(self, query: str, subsystem: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Embedding-based search for ambiguous queries"""
        if not self.embedder:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                return []
            
            # Search through relevant sections
            candidates = []
            for section in self.oracle_index:
                if subsystem and subsystem not in section.get('subsystems', []):
                    continue
                
                try:
                    # Use cached embedding if available (instant!)
                    if 'embedding' in section:
                        section_embedding = np.array(section['embedding'])
                    else:
                        # Fallback: generate embedding on-the-fly
                        if not self.manual_mmap or section['byte_start'] is None:
                            continue
                        content = self.manual_mmap[section['byte_start']:section['byte_end']].decode('utf-8')
                        section_embedding = self._get_embedding(content)
                        if section_embedding is None:
                            continue
                    
                    # Calculate similarity
                    similarity = np.dot(query_embedding, section_embedding)
                    
                    # Get content for result (ALWAYS extract content)
                    content = ""
                    if self.manual_mmap and section.get('byte_start') is not None and section.get('byte_end') is not None:
                        try:
                            content = self.manual_mmap[section['byte_start']:section['byte_end']].decode('utf-8')
                        except Exception as decode_err:
                            # Fallback: try reading from file directly
                            pass
                    
                    section_copy = section.copy()
                    section_copy['content'] = content
                    section_copy['search_score'] = float(similarity)
                    section_copy['match_type'] = 'embedding'
                    candidates.append(section_copy)
                
                except Exception as e:
                    print(f"Warning: Error processing section {section.get('title', 'unknown')}: {e}")
                    continue
            
            # Sort by similarity score
            candidates.sort(key=lambda x: x['search_score'], reverse=True)
            return candidates[:top_k]
        
        except Exception as e:
            print(f"Error in embedding search: {e}")
            return []
    
    def generate_audit_citation(self, finding: Dict[str, Any], subsystem: str) -> Dict[str, Any]:
        """
        Generate a bulletproof citation for an audit finding
        
        Args:
            finding: Audit finding with file path and issue type
            subsystem: Subsystem being audited
        
        Returns:
            Citation with anchor references and proof commands
        """
        citations = []
        proof_commands = []
        
        # Map finding type to relevant manual sections
        issue_type = finding.get('issue_type', '').lower()
        file_path = finding.get('file_path', '')
        
        # Find relevant sections
        relevant_sections = self.get_subsystem_sections(subsystem)
        
        # Add specific rule sections based on issue type
        if 'timeout' in issue_type or 'requests' in issue_type:
            # Look for timeout/HTTP rules
            timeout_sections = self.search_sections('timeout requests HTTP', subsystem)
            citations.extend([s['anchor'] for s in timeout_sections])
            proof_commands.append(f"rg -n 'requests\\.(get|post|put|delete)\\(' {file_path} | rg -v 'timeout\\s*='")
        
        elif 'except' in issue_type:
            # Look for exception handling rules
            except_sections = self.search_sections('exception handling bare except', subsystem)
            citations.extend([s['anchor'] for s in except_sections])
            proof_commands.append(f"rg -n '^\\s*except\\s*:\\s*$' {file_path}")
        
        elif 'print' in issue_type:
            # Look for logging rules
            logging_sections = self.search_sections('logging print statements', subsystem)
            citations.extend([s['anchor'] for s in logging_sections])
            proof_commands.append(f"rg -n '\\bprint\\(' {file_path}")
        
        elif 'import' in issue_type:
            # Look for import rules
            import_sections = self.search_sections('imports dependencies', subsystem)
            citations.extend([s['anchor'] for s in import_sections])
            proof_commands.append(f"rg -n '^import\\s+' {file_path}")
        
        # Ensure we have at least one citation
        if not citations and relevant_sections:
            citations = [relevant_sections[0]['anchor']]
        
        # Get manual hash for verification
        manual_hash = ""
        if self.oracle_index:
            manual_hash = self.oracle_index[0].get('manual_sha256', '')
        
        return {
            'path': file_path,
            'verdict': finding.get('verdict', 'FAIL'),
            'issue_id': finding.get('issue_id', 'UNKNOWN'),
            'citations': citations,
            'proof_commands': proof_commands,
            'manual_sha256': manual_hash,
            'oracle_version': '1.0.0'
        }
    
    def close(self):
        """Clean up resources"""
        if self.manual_mmap:
            self.manual_mmap.close()
        if self.manual_file:
            self.manual_file.close()
    
    def get_oracle_stats(self) -> Dict[str, Any]:
        """Get oracle system statistics"""
        return {
            'total_sections': len(self.oracle_index),
            'manual_path': str(self.manual_path),
            'toc_path': str(self.toc_path),
            'oracle_index_file': str(self.index_file),
            'memory_mapped': self.manual_mmap is not None,
            'embedder_available': self.embedder is not None,
            'integrity_verified': self._verify_manual_integrity()
        }
