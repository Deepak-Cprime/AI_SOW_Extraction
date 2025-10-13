from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import base64
from typing import Dict, Any

from sow_extractor.core.orchestrator import SOWOrchestrator
from sow_extractor.core.config import get_settings
from sow_extractor.utils.models import SOWExtractionResponse, Base64PDFRequest

app = FastAPI(
    title="SOW AI Extraction API",
    description="Extract structured data from Statement of Work (SOW) PDFs using AI",
    version="1.0.0"
)

settings = get_settings()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SOW AI Extraction"}

@app.post("/extract-sow", response_model=SOWExtractionResponse)
async def extract_sow(file: UploadFile = File(...)):
    """Extract structured data from SOW PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    temp_file_path = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the document
        orchestrator = SOWOrchestrator()
        result = await orchestrator.process_sow_document(temp_file_path)
        
        return SOWExtractionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/extract-sow-base64", response_model=SOWExtractionResponse)
async def extract_sow_base64(request: Base64PDFRequest):
    """Extract structured data from base64-encoded SOW PDF"""
    # Validate filename extension
    if not request.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    temp_file_path = None
    try:
        # Decode base64 content
        try:
            pdf_content = base64.b64decode(request.file_content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 encoding: {str(e)}")

        # Validate PDF content (check PDF magic number)
        if not pdf_content.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="Invalid PDF file: file does not appear to be a PDF")

        # Save decoded content to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name

        # Process the document
        orchestrator = SOWOrchestrator()
        result = await orchestrator.process_sow_document(temp_file_path)

        return SOWExtractionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)