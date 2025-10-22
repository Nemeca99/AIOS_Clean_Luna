#!/usr/bin/env python3
"""
RAG CORE - Manual Oracle System
Repurposed as a bulletproof manual lookup system for audit citations.

The RAG core now serves as the "truth engine" that provides exact citations
from the AIOS manual for all audit findings, with byte-offset lookups and
integrity verification.
"""

# CRITICAL: Import Unicode safety layer FIRST
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils_core.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import json
import time
from typing import Dict, List, Any, Optional
from rag_core.manual_oracle import ManualOracle
from rag_core.simple_rag import SimpleRAGSystem


class RAGCore:
    """
    RAG Core System - Manual Oracle for Audit Citations
    
    Provides bulletproof manual lookups with:
    - Byte-offset based lookups (no line number drift)
    - Section checksums for integrity verification
    - Anchor-based citations with subsystem mapping
    - Sparse embeddings for ambiguous queries only
    - Graceful ABSTAIN on hash mismatches
    """
    
    def __init__(self, base_dir: str = "rag_core"):
        self.version = "2.0.0"
        self.base_dir = Path(base_dir)
        
        # Initialize Manual Oracle (primary system)
        try:
            repo_root = Path(__file__).resolve().parents[1]
            self.oracle = ManualOracle(str(repo_root))
            self.oracle_available = True
            print(f"RAG Core initialized: Oracle with {len(self.oracle.oracle_index)} sections")
        except Exception as e:
            print(f"Warning: Oracle not available: {e}")
            self.oracle = None
            self.oracle_available = False
        
        # Initialize Simple RAG (fallback/legacy) - silent init
        try:
            self.simple_rag = SimpleRAGSystem(base_dir, silent=True)
            self.simple_rag_available = True
        except Exception as e:
            # Silent failure - Oracle is primary
            self.simple_rag = None
            self.simple_rag_available = False
        
        # Usage statistics
        self.oracle_queries = 0
        self.simple_rag_queries = 0
        self.start_time = time.time()
    
    def get_manual_citation(self, finding: Dict[str, Any], subsystem: str) -> Dict[str, Any]:
        """
        Get bulletproof manual citation for an audit finding.
        
        Args:
            finding: Audit finding with file path and issue type
            subsystem: Subsystem being audited
            
        Returns:
            Citation with anchor references and proof commands
        """
        if not self.oracle_available:
            return {
                'citations': [],
                'proof_commands': [],
                'manual_sha256': '',
                'citation_status': 'oracle_unavailable'
            }
        
        try:
            citation = self.oracle.generate_audit_citation(finding, subsystem)
            self.oracle_queries += 1
            return citation
        except Exception as e:
            return {
                'citations': [],
                'proof_commands': [],
                'manual_sha256': '',
                'citation_status': f'oracle_error: {str(e)}'
            }
    
    def search_manual(self, query: str, subsystem: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the manual for relevant sections.
        
        Args:
            query: Search query
            subsystem: Core being searched
            top_k: Number of results to return
            
        Returns:
            List of relevant manual sections with content
        """
        if not self.oracle_available:
            return []
        
        try:
            results = self.oracle.search_sections(query, subsystem, top_k)
            self.oracle_queries += 1
            return results
        except Exception as e:
            print(f"Error searching manual: {e}")
            return []
    
    def get_subsystem_guidelines(self, subsystem: str) -> List[Dict[str, Any]]:
        """
        Get all manual guidelines relevant to a subsystem.
        
        Args:
            subsystem: Name of the subsystem
            
        Returns:
            List of relevant manual sections
        """
        if not self.oracle_available:
            return []
        
        try:
            sections = self.oracle.get_subsystem_sections(subsystem)
            self.oracle_queries += 1
            return sections
        except Exception as e:
            print(f"Error getting subsystem guidelines: {e}")
            return []
    
    def lookup_section(self, anchor: str) -> Optional[Dict[str, Any]]:
        """
        Lookup a specific manual section by anchor.
        
        Args:
            anchor: Section anchor ID
            
        Returns:
            Section data with content if found
        """
        if not self.oracle_available:
            return None
        
        try:
            section = self.oracle.lookup_section(anchor)
            self.oracle_queries += 1
            return section
        except Exception as e:
            print(f"Error looking up section {anchor}: {e}")
            return None
    
    def process_query(self, query: str, use_simple_rag: bool = False) -> Dict[str, Any]:
        """
        Process a query using either Oracle or Simple RAG.
        
        Args:
            query: Search query
            use_simple_rag: Force use of simple RAG instead of oracle
            
        Returns:
            Query results
        """
        # Use Oracle by default (primary system)
        if self.oracle_available and not use_simple_rag:
            try:
                results = self.oracle.search_sections(query, top_k=5)
                self.oracle_queries += 1
                return {
                    'query': query,
                    'results': results,
                    'source': 'oracle',
                    'fragments_found': len(results)
                }
            except Exception as e:
                print(f"Oracle query failed: {e}")
        
        # Fallback to Simple RAG
        if self.simple_rag_available:
            try:
                result = self.simple_rag.process_query(query)
                self.simple_rag_queries += 1
                result['source'] = 'simple_rag'
                return result
            except Exception as e:
                print(f"Simple RAG query failed: {e}")
        
        # No systems available
        return {
            'query': query,
            'results': [],
            'source': 'none',
            'fragments_found': 0,
            'error': 'No RAG systems available'
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            'version': self.version,
            'uptime_seconds': time.time() - self.start_time,
            'oracle_available': self.oracle_available,
            'simple_rag_available': self.simple_rag_available,
            'oracle_queries': self.oracle_queries,
            'simple_rag_queries': self.simple_rag_queries,
            'total_queries': self.oracle_queries + self.simple_rag_queries
        }
        
        # Add oracle stats if available
        if self.oracle_available:
            oracle_stats = self.oracle.get_oracle_stats()
            stats['oracle'] = oracle_stats
        
        # Add simple RAG stats if available
        if self.simple_rag_available:
            simple_stats = self.simple_rag.get_stats()
            stats['simple_rag'] = simple_stats
        
        return stats
    
    def close(self):
        """Clean up resources"""
        if self.oracle:
            self.oracle.close()


def handle_command(args: List[str]) -> bool:
    """
    Handle RAG core commands.
    
    Commands:
    - --rag search <query> [--subsystem <name>] [--top-k <number>]
    - --rag guidelines <subsystem>
    - --rag lookup <anchor>
    - --rag citation <file_path> <issue_type> <subsystem>
    - --rag stats
    - --rag test
    
    Returns:
        True if command was handled, False otherwise
    """
    if not args or args[0] != '--rag':
        return False
    
    try:
        # Initialize RAG core
        rag = RAGCore()
        
        if len(args) < 2:
            print("RAG Core Commands:")
            print("  --rag search <query> [--subsystem <name>] [--top-k <number>]")
            print("  --rag guidelines <subsystem>")
            print("  --rag lookup <anchor>")
            print("  --rag citation <file_path> <issue_type> <subsystem>")
            print("  --rag stats")
            print("  --rag test")
            return True
        
        command = args[1]
        
        if command == 'search':
            # Parse search command
            query = args[2] if len(args) > 2 else ""
            subsystem = None
            top_k = 5
            
            # Parse optional arguments
            i = 3
            while i < len(args):
                if args[i] == '--subsystem' and i + 1 < len(args):
                    subsystem = args[i + 1]
                    i += 2
                elif args[i] == '--top-k' and i + 1 < len(args):
                    top_k = int(args[i + 1])
                    i += 2
                else:
                    i += 1
            
            # Parse flags
            limit = top_k
            min_score = 0.0
            
            for j, arg in enumerate(args):
                if arg == '--limit' and j + 1 < len(args):
                    try:
                        limit = int(args[j + 1])
                    except ValueError:
                        pass
                elif arg == '--min-score' and j + 1 < len(args):
                    try:
                        min_score = float(args[j + 1])
                    except ValueError:
                        pass
            
            # Print search header with oracle stats
            if rag.oracle_available and rag.oracle:
                oracle = rag.oracle
                manual_sha = oracle.manual_sha256[:8] if oracle.manual_sha256 else "unknown"
                toc_sha = oracle.toc_sha256[:8] if oracle.toc_sha256 else "unknown"
                chunks = len(oracle.oracle_index)
                
                # Calculate average chunk length
                if oracle.oracle_index and oracle.manual_mmap:
                    total_bytes = sum(
                        s.get('byte_end', 0) - s.get('byte_start', 0) 
                        for s in oracle.oracle_index 
                        if s.get('byte_start') and s.get('byte_end')
                    )
                    avg_len = total_bytes / chunks if chunks > 0 else 0
                    avg_tokens = int(avg_len / 4)  # Rough estimate: 4 chars per token
                else:
                    avg_tokens = 0
                
                embedder_info = f"{oracle.embedding_model} ({oracle.embedding_dim}d)" if oracle.embedder else "none"
                print(f"Embedder: {embedder_info}")
                print(f"Manual: sha={manual_sha}  TOC: sha={toc_sha}  Chunks={chunks}  avg_len={avg_tokens}t")
                print()
            
            results = rag.search_manual(query, subsystem, limit)
            
            # Filter by minimum score
            if min_score > 0:
                results = [r for r in results if r.get('search_score', 0) >= min_score]
            
            print(f"Query: '{query}'" + (f"  subsystem={subsystem}" if subsystem else ""))
            print(f"Found {len(results)} results:\n")
            
            for i, result in enumerate(results, 1):
                score = result.get('search_score', 0.0)
                title = result.get('title', 'Unknown')
                anchor = result.get('anchor', 'no-anchor')
                line_start = result.get('line_number', 0)
                
                # Calculate line range from content
                content = result.get('content', '')
                line_count = len(content.split('\n')) if content else 0
                line_end = line_start + line_count
                
                # Extract snippet (first 100 chars)
                snippet = content[:100].replace('\n', ' ').strip() if content else "..."
                
                print(f"[{i}]  score={score:.4f}  anchor={anchor}  lines={line_start}-{line_end}")
                print(f'     "{snippet}..."')
                print()
            
            return True  # Command handled
        
        elif command == 'guidelines':
            if len(args) < 3:
                print("Usage: --rag guidelines <subsystem>")
                return True
            
            subsystem = args[2]
            print(f"Getting guidelines for subsystem: {subsystem}")
            
            guidelines = rag.get_subsystem_guidelines(subsystem)
            print(f"Found {len(guidelines)} guidelines:")
            
            for i, guideline in enumerate(guidelines, 1):
                print(f"  {i}. {guideline.get('title', 'Unknown')} (line {guideline.get('line_number', '?')})")
        
        elif command == 'lookup':
            if len(args) < 3:
                print("Usage: --rag lookup <anchor>")
                return True
            
            anchor = args[2]
            print(f"Looking up section: {anchor}")
            
            section = rag.lookup_section(anchor)
            if section:
                print(f"Found: {section.get('title', 'Unknown')}")
                print(f"Line: {section.get('line_number', '?')}")
                content = section.get('content', '')
                if content:
                    print(f"Content preview: {content[:200]}...")
            else:
                print("Section not found")
        
        elif command == 'citation':
            if len(args) < 5:
                print("Usage: --rag citation <file_path> <issue_type> <subsystem>")
                return True
            
            file_path = args[2]
            issue_type = args[3]
            subsystem = args[4]
            
            finding = {
                'file_path': file_path,
                'issue_type': issue_type,
                'verdict': 'FAIL',
                'issue_id': 'TEST_CITATION'
            }
            
            print(f"Generating citation for: {issue_type}")
            print(f"File: {file_path}")
            print(f"Subsystem: {subsystem}")
            
            citation = rag.get_manual_citation(finding, subsystem)
            print(f"Citations: {citation.get('citations', [])}")
            print(f"Proof commands: {citation.get('proof_commands', [])}")
            print(f"Status: {citation.get('citation_status', 'unknown')}")
        
        elif command == 'stats':
            stats = rag.get_stats()
            print("RAG Core Statistics:")
            print(f"  Version: {stats['version']}")
            print(f"  Uptime: {stats['uptime_seconds']:.1f}s")
            print(f"  Oracle available: {stats['oracle_available']}")
            print(f"  Simple RAG available: {stats['simple_rag_available']}")
            print(f"  Oracle queries: {stats['oracle_queries']}")
            print(f"  Simple RAG queries: {stats['simple_rag_queries']}")
            print(f"  Total queries: {stats['total_queries']}")
            
            if stats.get('oracle'):
                oracle_stats = stats['oracle']
                print(f"  Oracle sections: {oracle_stats['total_sections']}")
                print(f"  Memory mapped: {oracle_stats['memory_mapped']}")
                print(f"  Integrity verified: {oracle_stats['integrity_verified']}")
        
        elif command == 'test':
            print("Testing RAG Core functionality...")
            
            # Test oracle search
            if rag.oracle_available:
                print("✅ Oracle available")
                results = rag.search_manual("timeout requests", "luna_core", top_k=3)
                print(f"✅ Search test: {len(results)} results")
            else:
                print("❌ Oracle not available")
            
            # Test simple RAG
            if rag.simple_rag_available:
                print("✅ Simple RAG available")
                result = rag.process_query("test query", use_simple_rag=True)
                print(f"✅ Simple RAG test: {result['source']}")
            else:
                print("❌ Simple RAG not available")
            
            print("RAG Core test completed")
        
        else:
            print(f"Unknown command: {command}")
            print("Use --rag without arguments to see available commands")
        
        # Clean up
        rag.close()
        return True
    
    except Exception as e:
        print(f"RAG Core error: {e}")
        return True


def main():
    """Main function for testing RAG core"""
    print("RAG Core - Manual Oracle System")
    print("=" * 40)
    
    # Test the core
    rag = RAGCore()
    
    # Test oracle functionality
    if rag.oracle_available:
        print(f"Oracle initialized with {len(rag.oracle.oracle_index)} sections")
        
        # Test search
        results = rag.search_manual("timeout requests", "luna_core", top_k=3)
        print(f"Search test: {len(results)} results")
        
        # Test citation
        test_finding = {
            'file_path': 'luna_core/test.py',
            'issue_type': 'requests_no_timeout',
            'verdict': 'FAIL',
            'issue_id': 'TEST'
        }
        citation = rag.get_manual_citation(test_finding, 'luna_core')
        print(f"Citation test: {len(citation.get('citations', []))} citations")
    
    # Get stats
    stats = rag.get_stats()
    print(f"\nStats: {stats['total_queries']} total queries")
    
    # Clean up
    rag.close()
    print("RAG Core test completed")


if __name__ == "__main__":
    main()
