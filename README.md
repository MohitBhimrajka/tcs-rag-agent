# TCS Annual Report RAG Agent

An intelligent, multi-modal document extraction system that uses advanced RAG (Retrieval-Augmented Generation) techniques and autonomous agents to extract structured financial data from financial reports. Built with LangGraph, FastAPI, React, and modern AI technologies.

## 🧠 System Architecture

### High-Level Overview

The system implements a sophisticated **LangGraph-based autonomous agent** with **asynchronous processing** and **real-time tracking** that follows a **Plan-Execute-Validate** workflow:

#### Agent State Flow
```
Job Submission → Background Processing → Task Queue → Planner → Tool Selection → Tool Execution → Validation → Database Storage → Real-time Status Updates
```

#### Core Components

1. **🎯 Planner Agent (`planner_node`)**
   - Uses Google Gemini to select appropriate tools
   - Processes structured task queue
   - Makes intelligent decisions about which RAG tool to use
   - Generates precise queries for maximum extraction accuracy

2. **🛠️ Tool Executor (`tool_node`)**
   - Executes selected RAG tools asynchronously
   - Handles both text and table search operations
   - Manages tool responses and error handling

3. **✅ Validator Agent (`validation_node`)**
   - Uses structured output parsing with Pydantic models
   - Validates and transforms raw tool outputs
   - Maps parsed data to final schema structures
   - Handles parsing errors gracefully

4. **🗄️ Database Layer**
   - SQLite database with Alembic migrations
   - Tracks extraction runs, audit trails, and results
   - Real-time current task updates
   - Structured JSON storage for extracted data

5. **🔄 File Management System**
   - Dynamic PDF upload with validation
   - Duplicate detection and error handling
   - Multi-document support with selection interface

### 🔍 Multi-Modal RAG System

#### Dual Vector Store Architecture
- **Text Vector Store**: Processes narrative content, management discussions, qualitative insights
- **Table Vector Store**: Extracts structured financial data, quantitative metrics, tabular information

#### RAG Tools
1. **TextSearchTool**
   - Optimized for qualitative information
   - Management risks, business outlook, utilization rates
   - Uses prose-based document chunks

2. **TableSearchTool**
   - Specialized for quantitative data
   - Financial figures, revenue breakdowns, segment contributions
   - Uses structured table representations in markdown format

## 🏗️ Technical Stack

### Backend Technologies
- **FastAPI**: High-performance Python web framework with async support
- **LangGraph**: Advanced agent orchestration and workflow management
- **LangChain**: RAG pipeline and document processing
- **Google Gemini**: Large language model for planning and validation
- **HuggingFace Transformers**: Embedding models (`all-MiniLM-L6-v2`)
- **FAISS**: Vector similarity search and storage
- **Pydantic**: Data validation and structured parsing
- **SQLAlchemy**: Database ORM with async support
- **Alembic**: Database migration management
- **Python Multipart**: File upload handling

### Document Processing
- **PyMuPDF**: PDF text extraction
- **Camelot**: Advanced table detection and extraction
- **Recursive Character Text Splitter**: Intelligent document chunking

### Infrastructure
- **Docker & Docker Compose**: Containerized deployment
- **Gunicorn**: Production WSGI server
- **Multi-stage Docker builds**: Optimized container images

### Frontend (Next.js)
- **Next.js 15**: React-based frontend framework
- **TypeScript**: Type-safe development
- **React Hooks**: State management with useState, useEffect, useCallback
- **Real-time Polling**: Live progress updates and status monitoring
- **Modern CSS**: Custom styling with CSS variables
- **File Management UI**: Drag-and-drop upload and document selection

## 📁 Project Structure

```
tcs-rag-agent/
├── app/                          # Main application directory
│   ├── agent/                    # Autonomous agent system
│   │   ├── graph.py             # LangGraph agent workflow definition
│   │   ├── tools.py             # RAG tools (Text/Table search)
│   │   └── parsers.py           # Structured output parsers
│   ├── api/                     # FastAPI application
│   │   └── v1/
│   │       └── endpoints.py     # Enhanced API endpoints with async processing
│   ├── core/                    # Core business logic
│   │   └── document_processor.py # Multi-modal document processing
│   ├── data/                    # Data storage
│   │   ├── audit.db             # SQLite database for tracking
│   │   └── vector_stores/       # FAISS vector databases
│   │       ├── *_text/          # Text chunks for each document
│   │       └── *_tables/        # Table structures for each document
│   ├── db/                      # Database layer
│   │   ├── database.py          # Database connection and sessions
│   │   ├── models.py            # SQLAlchemy models with enhanced schema
│   │   └── crud.py              # Database operations
│   ├── schemas/                 # Pydantic data models
│   │   └── extraction.py        # Structured output schemas
│   └── main.py                  # FastAPI application entry point
├── alembic/                     # Database migrations
│   ├── versions/                # Migration files
│   └── env.py                   # Alembic configuration
├── alembic.ini                  # Alembic settings
├── documents/                   # Input documents directory
│   └── TCS_Annual_report.pdf    # Source document (and uploaded files)
├── frontend/                    # Enhanced Next.js frontend
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx         # Enhanced UI with file management
│   │       ├── layout.tsx       # Application layout
│   │       └── globals.css      # Modern styling
│   ├── package.json            # Frontend dependencies
│   └── Dockerfile              # Frontend container
├── tests/                       # Test scripts and utilities
│   └── comprehensive_system_demo.sh  # Full system demonstration
├── packages/
│   └── requirements.txt        # Python dependencies (with new packages)
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile                  # Backend container
└── Makefile                   # Development commands
```

### 📊 Data Extraction Pipeline

#### Document Processing Workflow
```
File Upload/Selection → Background Job Creation → PDF Processing → Vector Store Generation → Task Queue Processing → Real-time Status Updates → Results Storage
```

#### Asynchronous Extraction Flow
```
1. Job Submission (immediate response with run_id)
2. Background Agent Execution
3. Real-time Task Progress Updates
4. Database Storage of Results
5. Complete Audit Trail Generation
```

#### Supported Extraction Tasks
- **Consolidated Revenue** (USD Billion)
- **Consolidated Net Income** (Profit After Tax)
- **Diluted Earnings Per Share** (EPS in INR)
- **Top 3 Segment Contributions** (Percentage breakdown)
- **Employee Utilization Rate** (Excluding trainees)
- **Key Management Risks** (Top 2-3 critical risks)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key
- Python 3.9+ (for local development)

### Environment Setup

**Create environment file:**
```bash
# Create .env in project root
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_URL=http://localhost:3000
NODE_ENV=development
EOF
```

**Create frontend environment:**
```bash
# Create frontend/.env.local
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

### Quick Launch

**Start all services:**
```bash
docker-compose up --build -d
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Health Check: http://localhost:8000/api/health
- API Documentation: http://localhost:8000/docs

**View logs:**
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs  
docker-compose logs -f frontend
```

## 📡 Enhanced API Endpoints

### File Management

#### `GET /api/v1/documents`
**List available PDF documents for processing**

**Response:**
```json
{
  "filenames": [
    "TCS_Annual_report.pdf",
    "company_annual_report_2023.pdf"
  ]
}
```

#### `POST /api/v1/documents/upload`
**Upload new PDF documents with validation**

**Request:** Multipart form data with PDF file
**Response:**
```json
{
  "filename": "uploaded_document.pdf",
  "message": "File uploaded successfully",
  "size_mb": 2.3
}
```

### Asynchronous Extraction System

#### `POST /api/v1/extract`
**Start asynchronous extraction job (Enhanced)**

**Request Body:**
```json
{
  "filename": "TCS_Annual_report.pdf"
}
```

**Response (Immediate):**
```json
{
  "run_id": 1,
  "filename": "TCS_Annual_report.pdf",
  "status": "in_progress",
  "message": "Extraction job has been started in the background."
}
```

#### `GET /api/v1/extractions/{run_id}/status`
**Get real-time job status with current task details**

**Response:**
```json
{
  "run_id": 1,
  "status": "in_progress",
  "current_task": "Processing: Consolidated Revenue (USD Billion)",
  "start_time": "2025-10-03T08:40:58.614069",
  "end_time": null
}
```

**Status Values:**
- `in_progress` - Agent actively processing tasks
- `completed` - All tasks finished successfully  
- `failed` - Processing encountered errors

#### `GET /api/v1/extractions/{run_id}/results`
**Retrieve complete results and audit trail**

**Response:**
```json
{
  "run_id": 1,
  "status": "completed",
  "filename": "TCS_Annual_report.pdf",
  "results": {
    "consolidated_revenue": {
      "value": 27.9,
      "unit": "USD Billion", 
      "source_page": 142
    },
    "consolidated_net_income": {
      "value": 4.84,
      "unit": "USD Billion",
      "source_page": 142
    },
    "diluted_eps": {
      "value": 131.0,
      "unit": "INR",
      "source_page": 143
    },
    "top_3_segment_contributions": [
      {
        "segment": "BFSI",
        "percentage": 30.2
      },
      {
        "segment": "Retail and CPG",
        "percentage": 15.8
      }
    ],
    "employee_utilization": {
      "value": 86.1,
      "unit": "percentage",
      "source_page": 28
    },
    "key_management_risks": [
      {
        "risk": "Global economic uncertainty",
        "description": "Impact on client spending patterns"
      }
    ]
  },
  "trace_logs": [
    {
      "timestamp": "2025-10-03T08:41:01.808008",
      "node_name": "Planner",
      "log_message": "Task: 'Consolidated Revenue'. Decision: Use tool 'TableSearchTool'."
    },
    {
      "timestamp": "2025-10-03T08:41:04.879206", 
      "node_name": "ToolExecutor",
      "log_message": "Executed tool 'TableSearchTool'. Raw Output: 27.9 USD Billion"
    }
  ]
}
```

### Health & Monitoring

#### `GET /api/health`
**System health check**

**Response:**
```json
{
  "status": "ok"
}
```

## 🔧 Data Schemas

### Core Models

```python
class FinancialReportData(BaseModel):
    """Complete financial report extraction results"""
    consolidated_revenue: Optional[ConsolidatedRevenue] = None
    consolidated_net_income: Optional[ConsolidatedNetIncome] = None  
    diluted_eps: Optional[DilutedEPS] = None
    top_3_segment_contributions: List[SegmentContribution] = []
    employee_utilization: Optional[EmployeeUtilization] = None
    key_management_risks: List[KeyManagementRisk] = []

class ConsolidatedRevenue(BaseMetric):
    """Revenue with metadata"""
    value: Optional[float] = None
    unit: Optional[str] = None  # e.g., "USD Billion"
    source_page: Optional[int] = None
    reasoning: Optional[str] = None
```

### Parser Models
Specialized models for LLM structured output parsing:
- `ParsedRevenue`, `ParsedNetIncome`, `ParsedEPS`
- `ParsedSegmentContribution`, `ParsedUtilization` 
- `ParsedKeyRisks`

## 🧪 Testing the Enhanced System

### 🚀 Quick System Demo

Run the comprehensive system demonstration:

```bash
# Execute the full system demo
./tests/comprehensive_system_demo.sh
```

This demo showcases:
- **File management** capabilities
- **Real-time progress tracking** 
- **Asynchronous processing** workflow
- **Complete audit trail** generation
- **Enhanced frontend** features

### 🔧 Manual API Testing

#### 1. Test File Management
```bash
# List available documents
curl -s http://localhost:8000/api/v1/documents | jq .

# Upload a new document (multipart form)
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@/path/to/your/document.pdf"
```

#### 2. Test Asynchronous Extraction
```bash
# Start extraction job (immediate response)
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{"filename": "TCS_Annual_report.pdf"}')

echo $RESPONSE | jq .
RUN_ID=$(echo $RESPONSE | jq -r .run_id)
```

#### 3. Monitor Real-time Progress
```bash
# Check status with current task details
curl -s "http://localhost:8000/api/v1/extractions/$RUN_ID/status" | jq .

# Expected responses show specific tasks:
# "Processing: Consolidated Revenue (USD Billion)"
# "Processing: Employee Utilization Rate (excluding trainees)" 
# etc.
```

#### 4. Retrieve Complete Results
```bash
# Get final results and audit trail (after completion)
curl -s "http://localhost:8000/api/v1/extractions/$RUN_ID/results" | jq .
```

### 🌐 Frontend Testing

1. **Open the enhanced UI**: http://localhost:3000
2. **Test file selection**: Choose from available documents
3. **Test file upload**: Drag and drop new PDF files
4. **Monitor real-time progress**: Watch live task updates
5. **Review complete results**: Structured data + audit trail

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain RAG Guide](https://python.langchain.com/docs/use_cases/question_answering/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://ai.google.dev/docs)
- [FAISS Vector Database](https://faiss.ai/)

---

## 🎉 System Overview

This **Enhanced TCS RAG Agent** represents a production-ready, enterprise-grade solution for automated financial document analysis. The system has evolved from a basic proof-of-concept to a sophisticated platform that combines:

### 🧠 **Intelligent Agent Architecture**
- **LangGraph-based autonomous agents** with sophisticated planning and validation
- **Multi-modal RAG processing** for both text and structured data extraction
- **Real-time progress tracking** with granular task visibility

### ⚡ **Modern Technical Stack**
- **Asynchronous FastAPI backend** with background job processing
- **React-based frontend** with real-time updates and file management
- **Database-backed persistence** with complete audit trails
- **Containerized deployment** ready for production scaling

### 🎯 **Enterprise Features**
- **Multi-document support** with upload and validation
- **Concurrent user handling** with isolated job tracking
- **Comprehensive error handling** and user feedback
- **Production-ready monitoring** and health checks

The system demonstrates how modern AI can transform traditional document processing workflows into intelligent, self-managing extraction pipelines that provide transparency, auditability, and scalability for enterprise financial analysis needs.

**Ready for production deployment with multi-user support and enterprise-grade reliability!** 🚀
