# SOW AI Extraction - Clean Project Structure

## Overview
A streamlined FastAPI application for extracting structured data from Statement of Work (SOW) PDFs using AI.

## Directory Structure

```
SOW AI Extraction/
├── app.py                          # 🚀 Main FastAPI application
├── requirements.txt                # 📦 Python dependencies
├── gunicorn.conf.py               # 🔧 Production server config
├── render.yaml                    # ☁️ Render deployment config
├── .env.example                   # 🔑 Environment template
├── README.md                      # 📖 Documentation
├── PROJECT_STRUCTURE.md           # 🏗️ This file
│
├── sow_extractor/                 # 📁 Main application package
│   ├── __init__.py               # Package initialization
│   │
│   ├── core/                     # 🎯 Core orchestration
│   │   ├── __init__.py
│   │   ├── config.py            # ⚙️ Settings & configuration
│   │   └── orchestrator.py      # 🎪 Main processing coordinator
│   │
│   ├── extractors/              # 🤖 AI-powered extraction
│   │   ├── __init__.py
│   │   └── table_extractor.py   # 📊 PDF table & text extraction
│   │
│   └── utils/                   # 🛠️ Utilities & models
│       ├── __init__.py
│       └── models.py            # 📋 Pydantic data models
│
└── tests/                       # 🧪 Test suite
    ├── __init__.py
    └── test_api.py              # 🔍 API endpoint tests
```

## Key Components

### 🚀 FastAPI Application (`app.py`)
- **Health Check**: `GET /health`
- **SOW Extraction**: `POST /extract-sow` (accepts PDF uploads)
- **OpenAPI Documentation**: Auto-generated at `/docs` and `/redoc`

### 🎪 SOW Orchestrator (`sow_extractor.core.orchestrator`)
- Coordinates the entire extraction workflow
- Manages PDF processing and AI extraction
- Handles error recovery and logging
- Returns structured JSON with milestones and deliverables

### 📊 Table Extractor (`sow_extractor.extractors.table_extractor`)
- Extracts tables and text from PDFs using `pdfplumber`
- Identifies milestone-related content intelligently
- Uses OpenAI GPT for structured data extraction
- Converts PDFs to markdown for better readability

### ⚙️ Configuration (`sow_extractor.core.config`)
- Environment-based settings management
- OpenAI API configuration
- Deployment-ready with Pydantic settings

### 📋 Data Models (`sow_extractor.utils.models`)
- Pydantic models for API responses
- Type-safe data structures
- JSON schema validation

## Features

### ✨ Core Capabilities
- **PDF Processing**: Extract text and tables from SOW documents
- **AI Extraction**: Use OpenAI GPT to identify milestones and deliverables
- **Structured Output**: Return JSON with validated data structures
- **Markdown Conversion**: Generate readable markdown from PDFs
- **Error Handling**: Robust error recovery and logging

### 🔧 Technical Features
- **FastAPI**: Modern, async Python web framework
- **Pydantic**: Data validation and settings management
- **OpenAI Integration**: GPT-powered content analysis
- **PDF Processing**: Advanced table and text extraction
- **Production Ready**: Gunicorn, environment configs, health checks

## API Endpoints

### Health Check
```http
GET /health
```
Returns service status and health information.

### Extract SOW Data
```http
POST /extract-sow
Content-Type: multipart/form-data

{
  "file": "sow_document.pdf"
}
```

Returns structured JSON with:
- **milestones**: Project phases and tasks
- **deliverables**: Work products and outputs
- **metadata**: Processing information and confidence scores

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your OpenAI API key

# Start development server
python app.py
```

### Testing
```bash
# Run tests
python tests/test_api.py

# Test import structure
python -c "from sow_extractor.core.orchestrator import SOWOrchestrator"
```

### Deployment
Deploy to Render using the included `render.yaml` configuration:
1. Connect your GitHub repository
2. Set `OPENAI_API_KEY` environment variable
3. Deploy as a web service

## Architecture Benefits

### 🎯 Clean Separation of Concerns
- **Core**: Business logic and orchestration
- **Extractors**: AI processing and data extraction
- **Utils**: Shared models and utilities
- **App**: API layer and request handling

### 🚀 Production Ready
- Environment-based configuration
- Proper error handling and logging
- Health checks and monitoring
- Async request processing

### 🔧 Maintainable
- Clear module boundaries
- Type hints throughout
- Pydantic for data validation
- Comprehensive documentation

### 📈 Scalable
- Async/await for concurrency
- Modular extractor design
- Configurable AI models
- Cloud deployment ready

## Future Extensions

The clean architecture supports easy additions:
- **New Extractors**: Add specialized document processors
- **Multiple AI Providers**: Support additional LLM services
- **Batch Processing**: Handle multiple documents
- **Advanced Analytics**: Document classification and insights
- **Webhook Integration**: Salesforce and other system integrations

---

**Ready for production deployment with comprehensive SOW extraction capabilities! 🚀**