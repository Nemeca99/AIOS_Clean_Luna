#!/usr/bin/env python3
"""
Documentation Loader
Loads all markdown documentation files into CARMA fragments so Luna has accurate context
"""

import os
from pathlib import Path
from typing import List, Dict

class DocumentationLoader:
    """Loads documentation files from the workspace"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs = []
        
    def load_all_documentation(self) -> List[Dict[str, str]]:
        """
        Load all .md files from the workspace
        Returns list of dicts with {source, content, category}
        """
        doc_files = []
        
        # Core documentation files to prioritize
        priority_docs = [
            "AIOS_CLEAN_PARADIGM.md",
            "AIOS_MASTER_DOCUMENTATION.md",
            "AIOS_MODULAR_ARCHITECTURE.md",
            "README.md",
            "data_core/docs/MAIN_README.md",
            "MATHEMATICAL_CONVERSATION_SYSTEM.md",
            "LANGUAGE_FIRST_ARCHITECTURE_REFACTOR.md",
            "QEC_INTEGRATION_SUMMARY.md",
            "COMPREHENSIVE_ASSESSMENT.md",
            "RUNBOOK.md",
            "SCHEMA.md",
        ]
        
        # Load priority docs first
        for doc in priority_docs:
            doc_path = self.base_dir / doc
            if doc_path.exists():
                try:
                    content = doc_path.read_text(encoding='utf-8')
                    doc_files.append({
                        'source': str(doc_path.relative_to(self.base_dir)),
                        'content': content,
                        'category': 'core_documentation',
                        'priority': 'high'
                    })
                except Exception as e:
                    print(f"Error loading {doc}: {e}")
        
        # Find all other markdown files
        for root, dirs, files in os.walk(self.base_dir):
            # Skip certain directories
            skip_dirs = {'venv', '__pycache__', 'node_modules', '.git', 'temp', 'backups', 
                        'backup_core', 'Portfolio', 'Profile-20251008T015804Z-1-001',
                        'drive-download-20251008T014919Z-1-001'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.base_dir)
                    
                    # Skip if already loaded in priority
                    if any(str(rel_path) == doc for doc in priority_docs):
                        continue
                    
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        
                        # Categorize by directory
                        category = 'general'
                        if 'luna_core' in str(rel_path):
                            category = 'luna_documentation'
                        elif 'carma_core' in str(rel_path):
                            category = 'carma_documentation'
                        elif 'data_core' in str(rel_path):
                            category = 'data_documentation'
                        elif 'support_core' in str(rel_path):
                            category = 'support_documentation'
                        
                        doc_files.append({
                            'source': str(rel_path),
                            'content': content,
                            'category': category,
                            'priority': 'normal'
                        })
                    except Exception as e:
                        print(f"Error loading {rel_path}: {e}")
        
        self.docs = doc_files
        return doc_files
    
    def get_documentation_fragments(self, max_chars: int = 2000) -> List[Dict[str, str]]:
        """
        Convert loaded docs into CARMA-ready fragments
        Splits large docs into chunks
        """
        fragments = []
        
        for doc in self.docs:
            content = doc['content']
            source = doc['source']
            category = doc['category']
            
            # If document is small enough, use as-is
            if len(content) <= max_chars:
                fragments.append({
                    'content': content,
                    'source': source,
                    'category': category,
                    'fragment_type': 'documentation'
                })
            else:
                # Split into chunks by paragraphs
                paragraphs = content.split('\n\n')
                current_chunk = []
                current_size = 0
                chunk_num = 1
                
                for para in paragraphs:
                    para_size = len(para)
                    
                    if current_size + para_size > max_chars and current_chunk:
                        # Save current chunk
                        fragments.append({
                            'content': '\n\n'.join(current_chunk),
                            'source': f"{source} (part {chunk_num})",
                            'category': category,
                            'fragment_type': 'documentation'
                        })
                        chunk_num += 1
                        current_chunk = [para]
                        current_size = para_size
                    else:
                        current_chunk.append(para)
                        current_size += para_size + 2  # +2 for \n\n
                
                # Save remaining chunk
                if current_chunk:
                    fragments.append({
                        'content': '\n\n'.join(current_chunk),
                        'source': f"{source} (part {chunk_num})" if chunk_num > 1 else source,
                        'category': category,
                        'fragment_type': 'documentation'
                    })
        
        return fragments
    
    def seed_carma_with_docs(self, carma_system) -> int:
        """
        Load all documentation into CARMA as fragments
        Returns number of fragments added
        """
        fragments = self.get_documentation_fragments()
        
        print(f"Loading {len(fragments)} documentation fragments into CARMA...")
        
        added = 0
        for frag in fragments:
            try:
                # Add to CARMA cache
                # This assumes CARMA has a method to add fragments directly
                # Adjust based on actual CARMA API
                if hasattr(carma_system, 'add_fragment'):
                    carma_system.add_fragment(frag['content'], metadata={
                        'source': frag['source'],
                        'category': frag['category'],
                        'type': 'documentation'
                    })
                    added += 1
            except Exception as e:
                print(f"Error adding fragment from {frag['source']}: {e}")
        
        return added


if __name__ == "__main__":
    # Test loading
    loader = DocumentationLoader(".")
    docs = loader.load_all_documentation()
    print(f"Loaded {len(docs)} documentation files")
    
    fragments = loader.get_documentation_fragments()
    print(f"Created {len(fragments)} documentation fragments")
    
    # Show categories
    categories = {}
    for frag in fragments:
        cat = frag['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nFragments by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

