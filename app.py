from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import base64
from typing import Dict, Any

from sow_extractor.core.orchestrator import SOWOrchestrator
from sow_extractor.core.config import get_settings
from sow_extractor.utils.models import SOWExtractionResponse, Base64PDFRequest
from sow_extractor.services.targetprocess_client import TargetProcessClient

app = FastAPI(
    title="SOW AI Extraction API",
    description="Extract structured data from Statement of Work (SOW) PDFs using AI",
    version="1.0.0"
)

settings = get_settings()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "SOW AI Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "extract_multipart": "/extract-sow",
            "extract_base64": "/extract-sow-base64"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SOW AI Extraction"}

@app.post("/debug-request")
async def debug_request(request: Request):
    """Debug endpoint to see what Salesforce is sending"""
    try:
        body = await request.body()
        json_data = await request.json() if body else {}
        return {
            "headers": dict(request.headers),
            "content_type": request.headers.get("content-type"),
            "body_raw": body.decode('utf-8')[:500] if body else None,
            "body_parsed": json_data,
            "has_filename": "filename" in json_data if json_data else False,
            "has_file_content": "file_content" in json_data if json_data else False,
            "json_keys": list(json_data.keys()) if json_data else []
        }
    except Exception as e:
        return {"error": str(e), "body": body.decode('utf-8')[:500] if body else None}

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

@app.post("/test-targetprocess")
async def test_targetprocess(milestone_data: Dict[str, Any] = None):
    """
    Test endpoint to debug TargetProcess API connection

    Send a test milestone to TargetProcess to verify connectivity and API format
    """
    try:
        tp_client = TargetProcessClient()

        if not tp_client.domain or not tp_client.access_token:
            return {
                "status": "error",
                "message": "TargetProcess credentials not configured",
                "config": {
                    "domain_set": bool(tp_client.domain),
                    "token_set": bool(tp_client.access_token)
                }
            }

        # Use provided data or create test milestone
        test_milestone = milestone_data or {
            "name": "Test Milestone",
            "description": "This is a test milestone from API",
            "due_date": "2024-12-31",
            "payment_amount": "$1000"
        }

        result = await tp_client.send_milestone(test_milestone)

        return {
            "status": "success",
            "message": "Successfully sent milestone to TargetProcess",
            "request": test_milestone,
            "response": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)