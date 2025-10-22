#!/usr/bin/env python3
"""
Secrets and sensitive data scanning check.
Detects API keys, tokens, private keys, and high-entropy strings.
"""

import re
import math
import logging
from pathlib import Path
from typing import Dict, List
from collections import Counter

from main_core.audit_core.checks.base_check import BaseCheck

logger = logging.getLogger(__name__)


class SecretsCheck(BaseCheck):
    """
    Scan for secrets, tokens, and sensitive data.
    
    Features:
    - Pattern-based detection (API keys, tokens, private keys)
    - Entropy-based detection (high-entropy strings)
    - Configurable severity levels
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.secrets_config = config.get('secrets_scanning', {})
        self.patterns = self.secrets_config.get('patterns', [])
        self.entropy_threshold = self.secrets_config.get('entropy_threshold', 4.5)
        self.enabled = self.secrets_config.get('enabled', True)
    
    def run(self, core_path: Path) -> Dict:
        """Run secrets scan on core."""
        if not self.enabled:
            return {'passed': True, 'secrets_found': []}
        
        logger.debug(f"Scanning {core_path} for secrets...")
        
        secrets_found = []
        
        # Scan all Python files
        for py_file in core_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Pattern-based detection
                for pattern_def in self.patterns:
                    pattern_id = pattern_def.get('id')
                    pattern = pattern_def.get('pattern')
                    severity = pattern_def.get('severity', 'medium')
                    
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        secrets_found.append({
                            'file': str(py_file.relative_to(core_path)),
                            'line': line_num,
                            'type': pattern_id,
                            'severity': severity,
                            'preview': self._safe_preview(match.group(0))
                        })
                
                # Entropy-based detection (high-entropy strings)
                high_entropy = self._find_high_entropy_strings(content, py_file, core_path)
                secrets_found.extend(high_entropy)
                
            except Exception as e:
                logger.debug(f"Failed to scan {py_file}: {e}")
        
        passed = len(secrets_found) == 0
        
        return {
            'passed': passed,
            'secrets_found': secrets_found,
            'secret_count': len(secrets_found)
        }
    
    def _calculate_entropy(self, string: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not string:
            return 0.0
        
        # Count character frequencies
        char_counts = Counter(string)
        length = len(string)
        
        # Calculate entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _find_high_entropy_strings(self, content: str, file_path: Path, core_path: Path) -> List[Dict]:
        """Find suspiciously high-entropy strings (potential secrets)."""
        high_entropy_strings = []
        
        # Look for long strings with high entropy (potential secrets)
        # Pattern: strings in quotes that are at least 20 chars
        string_pattern = r'["\']([A-Za-z0-9+/=_-]{20,})["\']'
        
        for match in re.finditer(string_pattern, content):
            string_value = match.group(1)
            entropy = self._calculate_entropy(string_value)
            
            if entropy >= self.entropy_threshold:
                line_num = content[:match.start()].count('\n') + 1
                high_entropy_strings.append({
                    'file': str(file_path.relative_to(core_path)),
                    'line': line_num,
                    'type': 'high-entropy-string',
                    'severity': 'medium',
                    'entropy': round(entropy, 2),
                    'preview': self._safe_preview(string_value)
                })
        
        return high_entropy_strings
    
    def _safe_preview(self, secret: str, max_len: int = 40) -> str:
        """Create a safe preview of a potential secret (redacted)."""
        if len(secret) <= 10:
            return "***REDACTED***"
        
        # Show first 4 and last 4 chars only
        preview = f"{secret[:4]}...{secret[-4:]}"
        if len(preview) > max_len:
            preview = preview[:max_len] + "..."
        
        return preview

