"""
SOW AI Extraction - A FastAPI application for extracting structured data from SOW PDFs using OpenAI.
"""

__version__ = "1.0.0"
__author__ = "SOW AI Extraction Team"

from .core.orchestrator import SOWOrchestrator
from .extractors.table_extractor import TableExtractor

__all__ = [
    "SOWOrchestrator",
    "TableExtractor"
]