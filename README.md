# SOW AI Extraction

A professional FastAPI application that extracts structured information from Statement of Work (SOW) PDF documents using OpenAI's advanced language models. The application processes both text-based and scanned PDFs, intelligently identifying and extracting milestones, deliverables, and payment terms into structured JSON format.

## ✨ Features

- **🔄 Advanced Processing Pipeline**: PDF → Markdown → Table & Text Extraction → AI Analysis
- **🤖 AI-Powered Extraction**: GPT-4 powered extraction of milestones and deliverables
- **📋 Structured Output**: Milestones with payment terms, due dates, and descriptions
- **📄 Multi-Format PDF Support**: Native text extraction with table detection using pdfplumber
- **🎯 TargetProcess Integration**: Automatic sync of milestones to TargetProcess KeyMilestones API
- **⚡ RESTful API**: Production-ready FastAPI endpoints with comprehensive error handling
- **🏗️ Modular Architecture**: Clean, maintainable codebase with separation of concerns
- **📊 Base64 Support**: Accept PDFs as base64-encoded content for Salesforce integration

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Navigate to project directory
cd "SOW AI Extraction"

# Install dependencies and setup environment
python setup.py
```

### 2. Configure Environment Variables

Create a `.env` file from the example and update with your credentials:

```bash
cp .env.example .env
```

Update the `.env` file with your credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4-1106-preview

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# TargetProcess Configuration (optional - for milestone sync)
TARGETPROCESS_DOMAIN=https://your-instance.tpondemand.com
TARGETPROCESS_ACCESS_TOKEN=your_access_token_here
```

### 3. Choose Your Processing Method

#### Option A: Batch Processing (Recommended) 📁
Process multiple PDFs from a folder:

```bash
# 1. Add PDF files to the input directory
cp your_sow_files/*.pdf input_pdfs/

# 2. Run batch processing
python run_batch.py

# Results will be saved in output_results/ directory
```

#### Option B: API Server 🌐
For integration with other applications:

```bash
# Start the API server
python app.py

# The API will be available at http://localhost:8000
# Visit http://localhost:8000/docs for interactive documentation
```

## 📡 API Endpoints

### 🎯 Main Extraction Endpoints

**`POST /extract-sow`** - Upload and process SOW PDF (multipart/form-data)

**Request:**
```bash
curl -X POST "http://localhost:8000/extract-sow" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_sow_document.pdf"
```

**`POST /extract-sow-base64`** - Process base64-encoded PDF (for Salesforce integration)

**Request:**
```bash
curl -X POST "http://localhost:8000/extract-sow-base64" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "sample_sow.pdf",
    "file_content": "JVBERi0xLjQKJeLjz9MK..."
  }'
```

**Response:**
```json
{
  "milestones": [
    {
      "name": "Phase 1",
      "description": "Requirements Analysis: Initial Review and Planning",
      "due_date": "2024-07-05",
      "payment_amount": "$5,000"
    },
    {
      "name": "Phase 2",
      "description": "Requirements Analysis: Final Documentation & Sign-off",
      "due_date": "2024-07-15",
      "payment_amount": "$5,000"
    }
  ],
  "deliverables": [
    {
      "name": "Technical Specification Document",
      "description": "Comprehensive technical requirements documentation",
      "delivery_date": "2024-07-20",
      "related_milestone": "Phase 1"
    }
  ],
  "metadata": {
    "processing_confidence": 0.95,
    "tables_found": 5,
    "milestone_tables_identified": 3,
    "milestones_extracted": 2,
    "deliverables_extracted": 1,
    "extraction_method": "enhanced_table_extraction",
    "processing_time": 23.45,
    "targetprocess_sync_status": "success",
    "targetprocess_milestones_sent": 2
  }
}
```

### 🎯 TargetProcess Integration

When TargetProcess credentials are configured, milestones are automatically synced:

**What Gets Sent to TargetProcess:**
```json
{
  "Name": "Phase 1 - Requirements Analysis: Initial Review and Planning",
  "Date": "2024-07-05",
  "Payment": "$5,000",
  "SOW": true
}
```

**Note:**
- Milestone `name` and `description` are combined for the TargetProcess `Name` field
- Deliverables are NOT sent to TargetProcess (only returned in API response)
- Sync status is included in response metadata

### 🔧 Additional Endpoints

- **`POST /test-targetprocess`** - Test TargetProcess API connectivity
- **`GET /health`** - Service health check
- **`GET /`** - API information and available endpoints

## 💻 Usage Examples

### Python Integration
```python
import requests
import base64

# API Usage - Multipart Upload
with open('sample_sow.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract-sow',
        files={'file': f}
    )

result = response.json()
print(f"📋 Milestones: {len(result['milestones'])}")
print(f"📦 Deliverables: {len(result['deliverables'])}")
print(f"🎯 Confidence: {result['metadata']['processing_confidence']}")
print(f"🔄 TargetProcess Sync: {result['metadata']['targetprocess_sync_status']}")

# API Usage - Base64 Upload (Salesforce Integration)
with open('sample_sow.pdf', 'rb') as f:
    pdf_content = base64.b64encode(f.read()).decode('utf-8')

payload = {
    "filename": "sample_sow.pdf",
    "file_content": pdf_content
}

response = requests.post(
    'http://localhost:8000/extract-sow-base64',
    json=payload
)

result = response.json()
print(f"✅ Milestones sent to TargetProcess: {result['metadata']['targetprocess_milestones_sent']}")

# Direct Package Usage
from sow_extractor.core.orchestrator import SOWOrchestrator

orchestrator = SOWOrchestrator()
result = await orchestrator.process_sow_document('path/to/sow.pdf')
```

### Batch Processing
```bash
# Simple batch processing
python run_batch.py

# Advanced batch processing with options
python batch_process.py --max-workers 3 --continue-on-error

# Process specific directories
python batch_process.py --input-dir /path/to/pdfs --output-dir /path/to/results

# Reprocess existing files
python batch_process.py --reprocess
```

### Testing
```bash
# Run API tests
python tests/test_api.py

# Test with sample document (API mode)
curl -X POST "http://localhost:8000/extract-sow" \
  -F "file=@samples/sample_manufacturing_sow.pdf"

# Test batch processing
cp samples/sample_manufacturing_sow.pdf input_pdfs/
python run_batch.py
```

## 🏗️ Architecture & Project Structure

### Processing Pipeline
```
PDF Document → Text Extraction → Markdown Conversion → 
Section Detection → LLM Filtering → One-Shot Extraction → JSON Response
```

### Directory Structure
```
SOW AI Extraction/
├── 📄 app.py                    # FastAPI application entry point
├── 🔄 batch_process.py          # Advanced batch processing script
├── ▶️ run_batch.py               # Simple batch processing runner
├── 📋 requirements.txt          # Python dependencies  
├── ⚙️ setup.py                  # Automated setup script
├── 📚 README.md                 # This documentation
├── 📊 STRUCTURE.md              # Detailed architecture guide
├── 🔧 .env.example              # Environment template
│
├── 📦 sow_extractor/            # Main package
│   ├── 🎯 core/                 # Core orchestration
│   │   ├── config.py            # Application settings & environment config
│   │   └── orchestrator.py      # Main processing coordinator + TargetProcess sync
│   │
│   ├── 🤖 extractors/           # AI-powered extraction
│   │   └── table_extractor.py   # Enhanced table & milestone extraction
│   │
│   ├── 🔗 services/             # External integrations
│   │   └── targetprocess_client.py # TargetProcess API client
│   │
│   └── 🛠️ utils/                # Utilities and models
│       └── models.py            # Pydantic request/response models
│
├── 📥 input_pdfs/               # Input directory for batch processing
│   └── README.md                # Usage instructions
│
├── 📤 output_results/           # Output directory for batch results
│   ├── successful/              # Successfully processed files
│   ├── failed/                  # Failed processing attempts  
│   ├── logs/                    # Processing summaries
│   └── README.md                # Results documentation
│
├── 📊 logs/                     # Application logs
│
├── 🧪 tests/                    # Test suite
│   └── test_api.py             # Comprehensive API tests
│
└── 📁 samples/                  # Sample documents and results
    ├── sample_manufacturing_sow.pdf
    ├── test_result.json
    └── converted_markdown.md
```

## ⚙️ Configuration

Environment variables in `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | GPT model to use | `gpt-4-1106-preview` |
| `API_HOST` | Host to bind the API | `0.0.0.0` |
| `API_PORT` | Port to bind the API | `8000` |
| `DEBUG` | Enable debug mode | `True` |
| `TESSERACT_PATH` | Tesseract executable path | Auto-detect |
| `TARGETPROCESS_DOMAIN` | TargetProcess instance URL (optional) | - |
| `TARGETPROCESS_ACCESS_TOKEN` | TargetProcess API token (optional) | - |

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **OpenAI API Key**: Required for AI processing
- **Tesseract OCR**: Optional, for scanned PDF processing
- **Memory**: Minimum 2GB RAM recommended
- **Storage**: ~100MB for dependencies

## 🛡️ Error Handling & Reliability

The application includes comprehensive error handling:

- **📄 PDF Processing**: Invalid files, corruption, unsupported formats
- **🔍 Section Detection**: Missing sections, unclear document structure
- **🤖 AI Processing**: API timeouts, rate limits, malformed responses  
- **✅ Validation**: JSON structure validation, data type checking
- **🔄 Retry Logic**: Automatic retry for transient failures

All errors return structured JSON responses with:
- HTTP status codes
- Detailed error messages
- Suggested troubleshooting steps

## 🎯 Performance & Accuracy

- **Processing Time**: ~30-60 seconds per document
- **Accuracy**: 90%+ confidence for well-structured SOW documents
- **Supported Formats**: PDF (text-based and scanned)
- **Document Size**: Up to 50 pages recommended
- **Concurrent Processing**: Thread-safe, supports multiple requests

## 📈 Recent Improvements

- ✅ **TargetProcess Integration**: Automatic milestone sync to TargetProcess KeyMilestones API
- ✅ **XML Response Parsing**: Handle TargetProcess XML responses correctly
- ✅ **Base64 PDF Support**: Accept base64-encoded PDFs for Salesforce integration
- ✅ **Enhanced Table Extraction**: Improved milestone extraction from PDF tables using pdfplumber
- ✅ **Modular Architecture**: Clean separation of concerns with services layer
- ✅ **Comprehensive Error Handling**: Graceful fallbacks and detailed logging
- ✅ **Production Ready**: Deployed on Render with environment-based configuration

## 🤝 Contributing

The codebase follows Python best practices:
- Modular design with separation of concerns
- Type hints and comprehensive docstrings  
- Error handling and logging
- Unit tests and integration tests

## 📄 License

This project is designed for SOW document processing and AI-powered data extraction.

---

**🚀 Ready to extract structured data from your SOW documents? Get started in minutes!**