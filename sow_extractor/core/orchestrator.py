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
from ..services.targetprocess_client import TargetProcessClient

logger = logging.getLogger(__name__)

class SOWOrchestrator:
    """Main orchestrator for SOW document processing"""

    def __init__(self):
        self.table_extractor = TableExtractor()
        self.tp_client = TargetProcessClient()
    
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

            # Send milestones to TargetProcess
            tp_sync_status = "not_configured"
            tp_milestones_sent = 0

            try:
                if self.tp_client.domain and self.tp_client.access_token:
                    logger.info("Sending milestones to TargetProcess...")
                    tp_results = await self.tp_client.send_milestones_batch(result["milestones"])
                    tp_milestones_sent = sum(1 for r in tp_results if r is not None)
                    tp_sync_status = "success" if tp_milestones_sent > 0 else "failed"
                    logger.info(f"Sent {tp_milestones_sent}/{len(result['milestones'])} milestones to TargetProcess")
                else:
                    logger.info("TargetProcess not configured, skipping sync")
            except Exception as e:
                logger.error(f"Error syncing to TargetProcess: {e}")
                tp_sync_status = "error"

            # Update metadata
            result["metadata"].update({
                "processing_time": round(processing_time, 2),
                "milestones_extracted": len(result["milestones"]),
                "deliverables_extracted": len(result.get("deliverables", [])),
                "extraction_method": "enhanced_table_extraction",
                "targetprocess_sync_status": tp_sync_status,
                "targetprocess_milestones_sent": tp_milestones_sent
            })

            # Log completion
            logger.info(f"SOW processing completed:")
            logger.info(f"  - Tables found: {result['metadata']['tables_found']}")
            logger.info(f"  - Milestone tables identified: {result['metadata']['milestone_tables_identified']}")
            logger.info(f"  - Milestones extracted: {len(result['milestones'])}")
            logger.info(f"  - Deliverables extracted: {len(result.get('deliverables', []))}")
            logger.info(f"  - TargetProcess sync: {tp_sync_status} ({tp_milestones_sent} sent)")
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