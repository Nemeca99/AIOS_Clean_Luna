"""
Oracle-Enhanced Audit Check
Uses the Manual Oracle to provide bulletproof citations for audit findings.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add rag_core to path for oracle import
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

try:
    from rag_core.manual_oracle import ManualOracle
except ImportError:
    ManualOracle = None

from .base_check import BaseCheck


class OracleCheck(BaseCheck):
    """
    Audit check that uses the Manual Oracle for bulletproof citations.
    
    This check doesn't find new issues - it enhances existing findings
    with proper manual citations and proof commands.
    """
    
    def __init__(self):
        super().__init__("oracle_check")
        self.oracle = None
        self._init_oracle()
    
    def _init_oracle(self):
        """Initialize the manual oracle"""
        if ManualOracle is None:
            print("Warning: Manual Oracle not available - citations will be disabled")
            return
        
        try:
            # Find repo root by going up from current file
            current_file = Path(__file__).resolve()
            repo_root = None
            
            # Try different parent levels to find repo root
            for level in range(1, 8):
                candidate = current_file.parents[level]
                if (candidate / "AIOS_MANUAL.md").exists():
                    repo_root = candidate
                    break
            
            if repo_root:
                self.oracle = ManualOracle(str(repo_root))
                print(f"Oracle initialized: {len(self.oracle.oracle_index)} sections available")
            else:
                print("Warning: Could not find repo root with AIOS_MANUAL.md")
                self.oracle = None
        except Exception as e:
            print(f"Warning: Could not initialize oracle: {e}")
            self.oracle = None
    
    def run(self, core_path: str, core_name: str) -> Dict[str, Any]:
        """
        Enhance existing audit findings with oracle citations.
        
        This check works by taking findings from other checks and adding
        bulletproof citations from the manual.
        """
        if self.oracle is None:
            return {
                'passed': True,
                'issues': [],
                'warnings': ['Oracle not available - citations disabled'],
                'score_impact': 0
            }
        
        issues = []
        warnings = []
        
        try:
            # Get subsystem sections for this core
            subsystem = self._map_core_to_subsystem(core_name)
            relevant_sections = self.oracle.get_subsystem_sections(subsystem)
            
            if not relevant_sections:
                warnings.append(f"No manual sections found for subsystem: {subsystem}")
            
            # Test oracle functionality
            oracle_stats = self.oracle.get_oracle_stats()
            
            return {
                'passed': True,
                'issues': issues,
                'warnings': warnings,
                'score_impact': 0,
                'oracle_stats': {
                    'total_sections': oracle_stats['total_sections'],
                    'subsystem_sections': len(relevant_sections),
                    'memory_mapped': oracle_stats['memory_mapped'],
                    'integrity_verified': oracle_stats['integrity_verified']
                }
            }
        
        except Exception as e:
            return {
                'passed': False,
                'issues': [f"Oracle check failed: {str(e)}"],
                'warnings': [],
                'score_impact': -5
            }
    
    def _map_core_to_subsystem(self, core_name: str) -> str:
        """Map core name to subsystem name"""
        core_mapping = {
            'luna_core': 'luna_core',
            'carma_core': 'carma_core', 
            'fractal_core': 'fractal_core',
            'dream_core': 'dream_core',
            'data_core': 'data_core',
            'streamlit_core': 'streamlit_core',
            'main_core': 'main_core',
            'support_core': 'support_core',
            'utils_core': 'utils_core',
            'infra_core': 'infra_core',
            'music_core': 'music_core',
            'rag_core': 'rag_core',
            'privacy_core': 'privacy_core',
            'enterprise_core': 'enterprise_core',
            'marketplace_core': 'marketplace_core',
            'template_core': 'template_core',
            'game_core': 'game_core',
            'backup_core': 'backup_core',
            'archive_dev_core': 'archive_dev_core'
        }
        
        return core_mapping.get(core_name, 'general')
    
    def enhance_finding_with_citation(self, finding: Dict[str, Any], core_name: str) -> Dict[str, Any]:
        """
        Enhance an audit finding with oracle citations.
        
        Args:
            finding: Audit finding from another check
            core_name: Name of the core being audited
            
        Returns:
            Enhanced finding with citations and proof commands
        """
        if self.oracle is None:
            finding['citations'] = []
            finding['proof_commands'] = []
            finding['citation_status'] = 'oracle_unavailable'
            return finding
        
        try:
            subsystem = self._map_core_to_subsystem(core_name)
            
            # Generate citation using oracle
            citation = self.oracle.generate_audit_citation(finding, subsystem)
            
            # Add citation data to finding
            finding['citations'] = citation['citations']
            finding['proof_commands'] = citation['proof_commands']
            finding['manual_sha256'] = citation['manual_sha256']
            finding['citation_status'] = 'oracle_verified'
            
            return finding
        
        except Exception as e:
            finding['citations'] = []
            finding['proof_commands'] = []
            finding['citation_status'] = f'oracle_error: {str(e)}'
            return finding
    
    def search_manual_for_guidance(self, query: str, core_name: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the manual for guidance on a specific topic.
        
        Args:
            query: Search query
            core_name: Core being audited
            top_k: Number of results to return
            
        Returns:
            List of relevant manual sections with content
        """
        if self.oracle is None:
            return []
        
        try:
            subsystem = self._map_core_to_subsystem(core_name)
            results = self.oracle.search_sections(query, subsystem, top_k)
            
            # Add content to results
            for result in results:
                if 'content' not in result:
                    section_data = self.oracle.lookup_section(result['anchor'])
                    if section_data:
                        result['content'] = section_data.get('content', '')
            
            return results
        
        except Exception as e:
            print(f"Error searching manual: {e}")
            return []
    
    def get_core_guidelines(self, core_name: str) -> List[Dict[str, Any]]:
        """
        Get all manual guidelines relevant to a core.
        
        Args:
            core_name: Name of the core
            
        Returns:
            List of relevant manual sections
        """
        if self.oracle is None:
            return []
        
        try:
            subsystem = self._map_core_to_subsystem(core_name)
            sections = self.oracle.get_subsystem_sections(subsystem)
            
            # Add content to sections
            for section in sections:
                section_data = self.oracle.lookup_section(section['anchor'])
                if section_data:
                    section['content'] = section_data.get('content', '')
            
            return sections
        
        except Exception as e:
            print(f"Error getting core guidelines: {e}")
            return []
    
    def close(self):
        """Clean up oracle resources"""
        if self.oracle:
            self.oracle.close()
