"""
Enhanced Table-Based SOW Data Extractor

This module provides advanced table extraction capabilities for SOW documents,
specifically designed to parse milestone and payment information from structured tables.
"""

import pdfplumber
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import openai
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class TableExtractor:
    """Enhanced table extractor for SOW documents"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
    
    async def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured data from PDF tables
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted milestones, deliverables, and payments
        """
        logger.info(f"Step 1: Extracting content with enhanced table processing")
        
        # Step 1: Extract tables and text
        tables_data = self._extract_tables_from_pdf(pdf_path)
        
        # Step 2: Convert PDF to markdown and save
        markdown_content = self._convert_pdf_to_markdown(pdf_path)
        self._save_markdown(pdf_path, markdown_content)
        
        # Step 3: Identify milestone content (tables AND text)
        logger.info(f"Step 3: Identifying milestone content in tables and text")
        milestone_tables = self._identify_milestone_tables(tables_data)
        milestone_text = self._extract_milestone_text(pdf_path)
        
        # Step 4: Extract milestones from both tables and text
        logger.info(f"Step 4: Extracting milestones from tables and text")
        milestones = await self._extract_milestones_from_all_sources(milestone_tables, milestone_text)
        
        # Step 5: Extract deliverables from text content
        logger.info(f"Step 4: Extracting deliverables from text content")
        deliverables = await self._extract_deliverables_from_text(pdf_path)
        
        return {
            "milestones": milestones,
            "deliverables": deliverables,
            "metadata": {
                "processing_confidence": 0.95,
                "tables_found": len(tables_data),
                "milestone_tables_identified": len(milestone_tables),
                "markdown_saved": True
            }
        }
    
    def _extract_tables_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract all tables from PDF with robust error handling"""
        tables_data = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"PDF opened successfully. Pages: {len(pdf.pages)}")

                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Extract tables with error handling
                        tables = page.extract_tables()
                        logger.info(f"Page {page_num}: Found {len(tables) if tables else 0} tables")

                        if tables:
                            for table_index, table in enumerate(tables):
                                if table and len(table) > 1:  # Must have header + data
                                    tables_data.append({
                                        'page': page_num,
                                        'table_index': table_index,
                                        'data': table,
                                        'text_content': self._table_to_text(table)
                                    })

                        # If no tables found, try extracting text and look for table-like patterns
                        if not tables:
                            text = page.extract_text()
                            if text and self._looks_like_table_text(text):
                                logger.info(f"Page {page_num}: Found table-like text patterns")
                                tables_data.append({
                                    'page': page_num,
                                    'table_index': 0,
                                    'data': None,
                                    'text_content': text,
                                    'type': 'text_table'
                                })

                    except Exception as e:
                        logger.warning(f"Error processing page {page_num}: {e}")
                        # Try to extract just text as fallback
                        try:
                            text = page.extract_text()
                            if text:
                                tables_data.append({
                                    'page': page_num,
                                    'table_index': 0,
                                    'data': None,
                                    'text_content': text,
                                    'type': 'fallback_text'
                                })
                        except Exception as text_error:
                            logger.error(f"Failed to extract even text from page {page_num}: {text_error}")

        except Exception as e:
            logger.error(f"Critical error opening PDF: {e}")
            raise

        logger.info(f"Total tables/text blocks extracted: {len(tables_data)}")
        return tables_data

    def _looks_like_table_text(self, text: str) -> bool:
        """Check if text contains table-like patterns"""
        lines = text.split('\n')

        # Look for common table indicators
        table_indicators = [
            'milestone', 'phase', 'payment', 'deliverable',
            'amount', 'date', 'percentage', '$', '%'
        ]

        # Count lines that look like table rows (have multiple separated values)
        table_like_lines = 0
        for line in lines:
            line_lower = line.lower().strip()
            if (len(line_lower.split()) >= 3 and  # At least 3 words
                any(indicator in line_lower for indicator in table_indicators)):
                table_like_lines += 1

        return table_like_lines >= 2  # At least 2 table-like lines
    
    def _table_to_text(self, table: List[List[str]]) -> str:
        """Convert table data to readable text format"""
        if not table:
            return ""
        
        # Create formatted table text
        lines = []
        for row in table:
            if row:  # Skip empty rows
                cleaned_row = [cell.strip() if cell else "" for cell in row]
                lines.append(" | ".join(cleaned_row))
        
        return "\n".join(lines)
    
    def _identify_milestone_tables(self, tables_data: List[Dict]) -> List[Dict]:
        """Identify tables that contain milestone/payment information"""
        milestone_tables = []
        
        milestone_keywords = [
            'milestone', 'phase', 'payment', 'due date', 'amount', 
            'percentage', 'description', 'duration'
        ]
        
        for table_data in tables_data:
            table_text = table_data['text_content'].lower()
            
            # Check if table contains milestone-related keywords
            keyword_count = sum(1 for keyword in milestone_keywords if keyword in table_text)
            
            if keyword_count >= 3:  # Must contain at least 3 relevant keywords
                milestone_tables.append(table_data)
        
        return milestone_tables
    
    def _extract_milestone_text(self, pdf_path: str) -> str:
        """Extract text content that might contain milestones with robust error handling"""
        milestone_text = ""
        milestone_keywords = [
            'milestone', 'phase', 'task', 'deliverable', 'schedule',
            'timeline', 'completion', 'due', 'deadline', 'payment'
        ]

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            # Check if page contains milestone-related content
                            text_lower = text.lower()
                            if any(keyword in text_lower for keyword in milestone_keywords):
                                milestone_text += f"=== Page {page_num + 1} ===\n{text}\n\n"
                                logger.info(f"Found milestone content on page {page_num + 1}")
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {e}")
                        # Try alternative extraction methods
                        try:
                            # Extract text without layout
                            raw_text = page.extract_text(layout=False)
                            if raw_text and any(kw in raw_text.lower() for kw in milestone_keywords):
                                milestone_text += f"=== Page {page_num + 1} (Raw) ===\n{raw_text}\n\n"
                        except:
                            logger.warning(f"Alternative text extraction also failed for page {page_num}")

        except Exception as e:
            logger.error(f"Critical error extracting milestone text: {e}")

        logger.info(f"Extracted milestone text length: {len(milestone_text)} characters")
        return milestone_text
    
    async def _extract_milestones_from_all_sources(self, milestone_tables: List[Dict], milestone_text: str) -> List[Dict]:
        """Extract milestones from both tables and text content"""
        all_milestones = []
        
        # Process tables
        for table_data in milestone_tables:
            try:
                milestones = await self._process_milestone_content(table_data['text_content'], table_data)
                all_milestones.extend(milestones)
            except Exception as e:
                logger.warning(f"Failed to extract milestones from table: {e}")
        
        # Process text content if available and no table milestones found
        if milestone_text and len(all_milestones) < 5:  # If few milestones from tables
            try:
                text_milestones = await self._process_milestone_content(milestone_text)
                # Merge or supplement with text milestones
                all_milestones.extend(text_milestones)
            except Exception as e:
                logger.warning(f"Failed to extract milestones from text: {e}")
        
        # Remove duplicates based on name and due_date
        seen = set()
        unique_milestones = []
        for milestone in all_milestones:
            key = (milestone.get('name', ''), milestone.get('due_date', ''))
            if key not in seen:
                seen.add(key)
                unique_milestones.append(milestone)
        
        return unique_milestones
    
    async def _process_milestone_content(self, content_text: str, source_data: Dict = None) -> List[Dict]:
        """Process content (table or text) to extract milestones"""
        if not content_text:
            return []
        
        prompt = f"""
        Analyze the following content and extract ALL milestone information regardless of format. Return ONLY a valid JSON array.

        Content:
        {content_text}

        Extract every milestone, phase, task, or deliverable item you find. For each item, create a JSON object:
        {{
            "name": "milestone/phase/task name",
            "description": "description or title", 
            "due_date": "any date found or null",
            "payment_amount": "any payment amount found or null"
        }}

        Instructions:
        - Look for ANY format: tables, bullet points, numbered lists, headers
        - Extract ALL items that represent work phases, milestones, or tasks
        - Include payment amounts where available
        - Use EXACT values from the content
        - If information is missing, use null
        - Return ONLY the JSON array, no other text
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            milestones = json.loads(result_text)
            
            # Add source metadata
            for milestone in milestones:
                if source_data:
                    milestone["source_table"] = {
                        "page": source_data.get('page', 'unknown'),
                        "table_index": source_data.get('table_index', 'unknown'),
                        "confidence": 1.0
                    }
                else:
                    milestone["source_table"] = {
                        "page": "text_content",
                        "table_index": "text",
                        "confidence": 0.8
                    }
            
            return milestones
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse milestone JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing milestone content: {e}")
            return []
    
    
    
    async def _extract_deliverables_from_text(self, pdf_path: str) -> List[Dict]:
        """Extract deliverables from text sections"""
        
        # Extract text content from PDF
        deliverables_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and ("deliverables" in text.lower() or "phase" in text.lower()):
                    deliverables_text += text + "\n"
        
        if not deliverables_text:
            return []
        
        prompt = f"""
        Analyze the following document content and extract ALL deliverable information in any format. Return ONLY a valid JSON array.

        Document Content:
        {deliverables_text}  

        Find any deliverable, output, artifact, or work product mentioned. For each item, create a JSON object:
        {{
            "name": "deliverable name",
            "description": "description found",
            "delivery_date": "any date found or null",
            "related_milestone": "related phase/milestone or null"
        }}

        Instructions:
        - Look for ANY format: bullet points, numbered lists, tables, paragraphs
        - Extract items that represent deliverables, outputs, artifacts, reports, systems
        - Find associated dates and related milestones
        - Use EXACT values from the content
        - Return ONLY the JSON array, no other text
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response - remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            deliverables = json.loads(result_text)
            return deliverables
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse deliverables JSON: {e}")
            logger.error(f"Raw response: {result_text}")
            return []
        except Exception as e:
            logger.error(f"Error extracting deliverables: {e}")
            return []
    
    
    def _convert_pdf_to_markdown(self, pdf_path: str) -> str:
        """Convert PDF content to markdown format"""
        markdown_lines = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                if page_num == 0:
                    markdown_lines.append(f"# SOW Document - {Path(pdf_path).stem}")
                    markdown_lines.append("")
                
                markdown_lines.append(f"## Page {page_num + 1}")
                markdown_lines.append("")
                
                # Extract text content
                text = page.extract_text()
                if text:
                    # Clean and format text
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Convert headers (simple heuristic)
                            if line.isupper() and len(line) < 100:
                                markdown_lines.append(f"### {line}")
                            else:
                                markdown_lines.append(line)
                            markdown_lines.append("")
                
                # Extract tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 1:
                        markdown_lines.append(f"#### Table {table_idx + 1}")
                        markdown_lines.append("")
                        
                        # Create markdown table
                        headers = table[0]
                        markdown_lines.append("| " + " | ".join(str(h) if h else "" for h in headers) + " |")
                        markdown_lines.append("|" + "|".join(["---"] * len(headers)) + "|")
                        
                        for row in table[1:]:
                            if row and any(cell for cell in row):  # Skip empty rows
                                markdown_lines.append("| " + " | ".join(str(cell) if cell else "" for cell in row) + " |")
                        
                        markdown_lines.append("")
                
                markdown_lines.append("---")
                markdown_lines.append("")
        
        return "\n".join(markdown_lines)
    
    def _save_markdown(self, pdf_path: str, markdown_content: str):
        """Save markdown content to output directory"""
        try:
            # Create markdown filename
            pdf_name = Path(pdf_path).stem
            markdown_dir = Path("output_results/markdown")
            markdown_dir.mkdir(parents=True, exist_ok=True)
            
            markdown_file = markdown_dir / f"{pdf_name}.md"
            
            # Save markdown content
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown saved to: {markdown_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save markdown: {e}")