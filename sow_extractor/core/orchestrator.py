"""
Main SOW Processing Orchestrator

This module coordinates the entire SOW document processing workflow,
using the enhanced table extraction method as the primary approach.
"""

import logging
import time
from typing import Dict, Any
from pathlib import Path

from ..extractors.table_extractor import TableExtractor
from ..utils.models import SOWExtractionResponse

logger = logging.getLogger(__name__)

class SOWOrchestrator:
    """Main orchestrator for SOW document processing"""
    
    def __init__(self):
        self.table_extractor = TableExtractor()
    
    async def process_sow_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a SOW document and extract structured data
        
        Args:
            pdf_path: Path to the SOW PDF file
            
        Returns:
            Dictionary containing extracted milestones, deliverables, and payments
        """
        start_time = time.time()
        
        logger.info(f"Starting SOW processing for: {pdf_path}")
        
        try:
            # Validate file exists
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Extract data using enhanced table extraction
            result = await self.table_extractor.extract_from_pdf(pdf_path)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update metadata
            result["metadata"].update({
                "processing_time": round(processing_time, 2),
                "milestones_extracted": len(result["milestones"]),
                "deliverables_extracted": len(result["deliverables"]),
                "extraction_method": "enhanced_table_extraction"
            })
            
            # Log completion
            logger.info(f"SOW processing completed:")
            logger.info(f"  - Tables found: {result['metadata']['tables_found']}")
            logger.info(f"  - Milestone tables identified: {result['metadata']['milestone_tables_identified']}")
            logger.info(f"  - Milestones extracted: {len(result['milestones'])}")
            logger.info(f"  - Deliverables extracted: {len(result['deliverables'])}")
            logger.info(f"  - Processing time: {processing_time:.2f}s")
            logger.info(f"  - Confidence: {result['metadata']['processing_confidence']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing SOW document: {e}")
            raise
    
    async def get_debug_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get debug information about document processing
        
        Args:
            pdf_path: Path to the SOW PDF file
            
        Returns:
            Debug information dictionary
        """
        try:
            # Extract basic table information
            tables_data = self.table_extractor._extract_tables_from_pdf(pdf_path)
            milestone_tables = self.table_extractor._identify_milestone_tables(tables_data)
            
            return {
                "total_tables": len(tables_data),
                "milestone_tables": len(milestone_tables),
                "table_details": [
                    {
                        "page": table["page"],
                        "index": table["table_index"],
                        "content_preview": table["text_content"][:200] + "..." if len(table["text_content"]) > 200 else table["text_content"]
                    }
                    for table in milestone_tables
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting debug info: {e}")
            return {"error": str(e)}