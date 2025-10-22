"""
RAG Core Module
Manual Oracle System for Audit Citations
V5.1: Creative template retrieval
"""

from .rag_core import handle_command, RAGCore
from .simple_rag import SimpleRAGSystem
from .manual_oracle import ManualOracle
from . import creative_retriever

__all__ = ['handle_command', 'RAGCore', 'SimpleRAGSystem', 'ManualOracle', 'creative_retriever']
