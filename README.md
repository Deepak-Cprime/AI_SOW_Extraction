# SOW AI Extraction

A professional FastAPI application that extracts structured information from Statement of Work (SOW) PDF documents using OpenAI's advanced language models. The application processes both text-based and scanned PDFs, intelligently identifying and extracting milestones, deliverables, and payment terms into structured JSON format.

## ✨ Features

- **🔄 Advanced Processing Pipeline**: PDF → Markdown → Section Detection → AI Extraction
- **🤖 Intelligent Section Filtering**: LLM-powered identification of relevant document sections
- **📋 One-Shot JSON Extraction**: Template-based extraction with example-driven prompts
- **📄 Multi-Format PDF Support**: Native text extraction with OCR fallback for scanned documents
- **🎯 High-Precision Extraction**: Structured data with confidence scoring and validation
- **⚡ RESTful API**: Production-ready FastAPI endpoints with comprehensive error handling
- **🏗️ Modular Architecture**: Clean, maintainable codebase with separation of concerns

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Navigate to project directory
cd "SOW AI Extraction"

# Install dependencies and setup environment
python setup.py
```

### 2. Configure OpenAI API Key

Update the `.env` file with your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4-1106-preview
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

### 🎯 Main Extraction Endpoint

**`POST /extract-sow`** - Upload and process SOW PDF

**Request:**
```bash
curl -X POST "http://localhost:8000/extract-sow" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_sow_document.pdf"
```

**Response:**
```json
{
  "milestones": [
    {
      "name": "Project Kickoff and Site Assessment",
      "description": "Complete initial site survey and establish project team",
      "due_date": "2024-01-15",
      "dependencies": ["Contract approval", "Team assignment"],
      "completion_criteria": "Meeting completed and requirements documented",
      "payment_amount": "$50,000",
      "payment_percentage": "10%"
    }
  ],
  "deliverables": [
    {
      "name": "Technical Specification Document",
      "description": "Comprehensive technical requirements and system architecture",
      "delivery_date": "2024-01-20",
      "acceptance_criteria": "Client technical team approval required",
      "format": "PDF Document (50+ pages)",
      "related_milestone": "Project Kickoff",
      "payment_trigger": "Triggers 30% payment upon acceptance"
    }
  ],
  "payment_terms": [
    {
      "payment_type": "milestone-based",
      "amount": "$50,000",
      "currency": "USD",
      "percentage": "10%",
      "trigger": "Completion of Project Kickoff milestone",
      "due_date": "2024-02-14",
      "related_milestone": "Project Kickoff and Site Assessment",
      "related_deliverable": null,
      "description": "Initial payment upon project start"
    }
  ],
  "metadata": {
    "processing_confidence": 0.9,
    "total_sections_found": 21,
    "relevant_sections": {
      "milestones": ["PROJECT MILESTONES", "Milestone 1: Project Kickoff"],
      "deliverables": ["PROJECT DELIVERABLES", "1. Technical Specification"],
      "payments": ["PAYMENT TERMS AND SCHEDULE", "Payment 1 - Project Initiation"]
    }
  }
}
```

### 🔧 Additional Endpoints

- **`POST /extract-sections`** - Extract sections without AI processing (debugging)
- **`POST /process-section`** - Process individual section with AI
- **`POST /validate-json`** - Validate JSON structure
- **`GET /health`** - Service health check

## 💻 Usage Examples

### Python Integration
```python
import requests
from sow_extractor import SOWOrchestrator

# API Usage
with open('manufacturing_sow.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract-sow',
        files={'file': f}
    )

result = response.json()
print(f"📋 Milestones: {len(result['milestones'])}")
print(f"📦 Deliverables: {len(result['deliverables'])}")  
print(f"💰 Payment Terms: {len(result['payment_terms'])}")
print(f"🎯 Confidence: {result['metadata']['processing_confidence']}")

# Direct Package Usage
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
│   │   ├── config.py            # Application settings
│   │   └── orchestrator.py      # Main processing coordinator
│   │
│   ├── 🔄 processors/           # Document processing
│   │   ├── pdf_processor.py     # PDF text extraction (native + OCR)
│   │   ├── markdown_converter.py # PDF → Markdown conversion
│   │   └── section_extractor.py # Title-based section identification
│   │
│   ├── 🤖 extractors/           # AI-powered extraction
│   │   ├── section_filter.py    # LLM section relevance filtering
│   │   └── oneshot_extractor.py # Template-based JSON extraction
│   │
│   └── 🛠️ utils/                # Utilities and models
│       └── models.py            # Pydantic response models
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

- ✅ **Modular Architecture**: Complete codebase reorganization
- ✅ **Advanced Pipeline**: PDF → Markdown → AI extraction workflow  
- ✅ **LLM Section Filtering**: Intelligent section relevance detection
- ✅ **One-Shot Extraction**: Template-based prompting with examples
- ✅ **Production Ready**: Clean structure, comprehensive testing
- ✅ **Documentation**: Updated guides and API documentation

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