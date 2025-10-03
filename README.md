# TCS Annual Report RAG Agent

A production-ready, intelligent document extraction system that uses advanced Chain of Thought RAG (Retrieval-Augmented Generation) techniques to extract structured financial data from annual reports. Built with modern AI technologies including Gemini 2.5 models, FastAPI, React, and comprehensive production hardening.

## 🧠 System Architecture

### High-Level Overview

The system implements a **streamlined Chain of Thought RAG architecture** with **asynchronous processing**, **real-time tracking**, and **production-grade error handling**:

#### Processing Flow
```
Job Submission → Document Processing → Chain of Thought RAG → Structured Extraction → Database Storage → Real-time Status Updates → Complete Audit Trail
```

#### Core Architecture Components

1. **🎯 Chain of Thought RAG Pipeline**
   - **Stage 1**: Gemini 2.5 Flash contextualizes simple tasks into detailed, self-contained questions
   - **Stage 2**: Gemini 2.5 Pro analyzes combined text and table contexts for structured extraction
   - **Intelligent Question Generation**: Converts "Consolidated Revenue" → "What is the total Consolidated Revenue from operations in USD Billion for the most recent financial year?"
   - **Multi-Modal Context Analysis**: Combines textual and tabular information for comprehensive understanding

2. **🔄 Resilient Task Processing**
   - Individual task isolation prevents cascade failures
   - Robust error handling with graceful degradation
   - Maximum data recovery even with partial failures
   - Comprehensive trace logging for debugging

3. **🗄️ Production Database Layer**
   - SQLite database with auto-initialization
   - Complete audit trails with timestamps
   - Real-time current task tracking
   - Structured JSON storage for extracted data
   - Database consistency with atomic operations

4. **🔄 Enterprise File Management**
   - Dynamic PDF upload with validation and duplicate detection
   - Multi-document support with selection interface
   - Robust error handling for missing files

### 🔍 Advanced Multi-Modal RAG System

#### Dual Vector Store Architecture
- **Text Vector Store**: Narrative content, management discussions, qualitative insights
- **Table Vector Store**: Structured financial data, quantitative metrics, tabular information

#### Intelligent RAG Tools
1. **TextSearchTool**
   - Optimized for qualitative information extraction
   - Management risks, business outlook, utilization rates
   - Advanced context retrieval from prose content

2. **TableSearchTool**
   - Specialized for quantitative data extraction
   - Financial figures, revenue breakdowns, segment contributions
   - Structured table representations in markdown format

## 🏗️ Modern Technical Stack

### Backend Technologies
- **FastAPI**: High-performance async Python web framework
- **Gemini 2.5 Flash**: Lightweight, fast question contextualization
- **Gemini 2.5 Pro**: Advanced analysis and structured output generation
- **LangChain**: RAG pipeline orchestration and document processing
- **HuggingFace Transformers**: Embedding models (`all-MiniLM-L6-v2`)
- **FAISS**: High-performance vector similarity search
- **Pydantic**: Robust data validation and structured parsing
- **SQLAlchemy**: Database ORM with production features
- **Alembic**: Database migration management

### Document Processing Pipeline
- **PyMuPDF**: Advanced PDF text extraction
- **Camelot**: Sophisticated table detection and extraction
- **Recursive Character Text Splitter**: Intelligent document chunking

### Infrastructure & Production
- **Docker & Docker Compose**: Containerized deployment
- **Gunicorn**: Production WSGI server
- **Multi-stage Docker builds**: Optimized container images
- **Health checks**: Production monitoring endpoints
- **Error handling**: Comprehensive exception management

### Frontend (Next.js)
- **Next.js 15**: Modern React-based frontend framework
- **TypeScript**: Type-safe development
- **React Hooks**: Advanced state management
- **Real-time Polling**: Live progress updates
- **Modern UI/UX**: Responsive design with accessibility

## 📁 Project Structure

```
tcs-rag-agent/
├── app/                          # Main application directory
│   ├── agent/                    # Chain of Thought RAG system
│   │   ├── rag_chain.py         # Advanced RAG chain implementation
│   │   ├── tools.py             # RAG tools (Text/Table search)
│   │   └── parsers.py           # Structured output parsers
│   ├── api/                     # Production FastAPI application
│   │   └── v1/
│   │       └── endpoints.py     # Complete API endpoints with async processing
│   ├── core/                    # Core business logic
│   │   └── document_processor.py # Multi-modal document processing
│   ├── data/                    # Data storage
│   │   ├── audit.db             # SQLite database for tracking
│   │   └── vector_stores/       # FAISS vector databases
│   │       ├── *_text/          # Text chunks for each document
│   │       └── *_tables/        # Table structures for each document
│   ├── db/                      # Production database layer
│   │   ├── database.py          # Database connection and sessions
│   │   ├── models.py            # SQLAlchemy models with auto-initialization
│   │   └── crud.py              # Complete database operations
│   ├── schemas/                 # Pydantic data models
│   │   └── extraction.py        # Structured output schemas
│   └── main.py                  # FastAPI application with auto-initialization
├── alembic/                     # Database migrations
├── documents/                   # Input documents directory
├── frontend/                    # Production Next.js frontend
│   ├── src/app/
│   │   ├── page.tsx            # Enhanced UI with file management
│   │   ├── layout.tsx          # Application layout
│   │   └── globals.css         # Modern styling
│   └── Dockerfile              # Frontend container
├── tests/                       # Comprehensive test suite
│   └── comprehensive_system_demo.sh  # End-to-end validation script
├── packages/
│   └── requirements.txt        # Complete Python dependencies
├── docker-compose.yml          # Production container orchestration
├── Dockerfile                  # Optimized backend container
└── Makefile                   # Development commands
```

## 📊 Advanced Data Extraction Pipeline

### Document Processing Workflow
```
File Upload/Selection → Background Job Creation → PDF Processing → Vector Store Generation → Chain of Thought Processing → Real-time Status Updates → Results Storage → Complete Audit Trail
```

### Asynchronous Extraction Flow
```
1. Job Submission (immediate response with run_id)
2. Background Chain of Thought RAG Execution
3. Real-time Task Progress Updates with specific details
4. Resilient Individual Task Processing
5. Database Storage of Results with complete audit trail
6. Production-ready Error Handling and Recovery
```

### Supported Extraction Tasks
- **Consolidated Revenue** (USD Billion) - Advanced financial figure extraction
- **Consolidated Net Income** (Profit After Tax) - Comprehensive profit analysis
- **Diluted Earnings Per Share** (EPS in INR) - Precise per-share calculations
- **Top 3 Segment Contributions** (Percentage breakdown) - Business segment analysis
- **Employee Utilization Rate** (Excluding trainees) - Workforce efficiency metrics
- **Key Management Risks** (Top 2-3 critical risks) - Strategic risk assessment

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key (with access to Gemini 2.5 models)
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
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- ❤️ Health Check: http://localhost:8000/api/health
- 📚 API Documentation: http://localhost:8000/docs

**View logs:**
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs  
docker-compose logs -f frontend
```

## 📡 Complete Production API

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
  "status": "uploaded successfully"
}
```

### Advanced Asynchronous Extraction System

#### `POST /api/v1/extract`
**Start Chain of Thought RAG extraction job**

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
  "status": "processing_started"
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
- `in_progress` - Chain of Thought RAG actively processing tasks
- `completed` - All tasks finished successfully  
- `failed` - Processing encountered errors with proper error tracking

#### `GET /api/v1/extractions/{run_id}/results`
**Retrieve complete results and comprehensive audit trail**

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
        "segment_name": "BFSI",
        "percentage_contribution": 30.2
      },
      {
        "segment_name": "Retail and CPG",
        "percentage_contribution": 15.8
      }
    ],
    "employee_utilization": {
      "rate_percentage": 86.1,
      "source_page": 28
    },
    "key_management_risks": [
      {
        "risk_summary": "Global economic uncertainty impacting client spending patterns"
      }
    ]
  },
  "trace_logs": [
    {
      "timestamp": "2025-10-03T08:41:01.808008",
      "node_name": "RAGChain",
      "log_message": "Task: 'Consolidated Revenue'.\nSuccess.\nResult: {'value': 27.9, 'unit': 'USD Billion', 'source_page': 142}"
    }
  ]
}
```

### Health & Monitoring

#### `GET /api/health`
**Production system health check**

**Response:**
```json
{
  "status": "ok"
}
```

## 🔧 Advanced Data Schemas

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
    """Revenue with comprehensive metadata"""
    value: Optional[float] = None
    unit: Optional[str] = None  # e.g., "USD Billion"
    source_page: Optional[int] = None
    reasoning: Optional[str] = None
```

### Chain of Thought Parser Models
Specialized models for Gemini 2.5 structured output parsing:
- `ParsedRevenue`, `ParsedNetIncome`, `ParsedEPS`
- `ParsedSegmentContribution`, `ParsedUtilization` 
- `ParsedKeyRisks`

## 🧪 Comprehensive Testing

### 🚀 End-to-End System Validation

Run the complete production validation:

```bash
# Execute the comprehensive system validation
./tests/comprehensive_system_demo.sh
```

This production test suite validates:
- **Complete API endpoint functionality**
- **Asynchronous processing workflow** 
- **Real-time progress tracking with specific task details**
- **Error handling and recovery mechanisms**
- **Database consistency and audit trail generation**
- **File management capabilities**

### 🔧 Manual API Testing

#### 1. Test Production File Management
```bash
# List available documents
curl -s http://localhost:8000/api/v1/documents | jq .

# Upload a new document (multipart form)
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@/path/to/your/document.pdf"
```

#### 2. Test Chain of Thought RAG Extraction
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
# "Completed"
```

#### 4. Retrieve Complete Results
```bash
# Get final results and comprehensive audit trail
curl -s "http://localhost:8000/api/v1/extractions/$RUN_ID/results" | jq .
```

### 🌐 Frontend Testing

1. **Access the production UI**: http://localhost:3000
2. **Test file selection**: Choose from available documents
3. **Test file upload**: Drag and drop new PDF files with validation
4. **Monitor real-time progress**: Watch live Chain of Thought RAG processing
5. **Review complete results**: Structured data with comprehensive audit trail

## 🎯 Production Features

### 🛡️ Production Hardening
- **Robust Error Handling**: Individual task failures don't crash the system
- **Database Consistency**: Atomic operations with auto-initialization
- **Graceful Degradation**: Maximum data recovery with partial failures
- **Comprehensive Logging**: Complete audit trails for debugging and compliance

### ⚡ Performance Optimizations
- **Asynchronous Processing**: Non-blocking job execution
- **Efficient Model Usage**: Lightweight Gemini 2.5 Flash for contextualization, powerful Gemini 2.5 Pro for analysis
- **Vector Store Caching**: Reuse processed documents for multiple extractions
- **Optimized Docker Images**: Multi-stage builds for minimal deployment size

### 🔒 Enterprise Features
- **Multi-Document Support**: Handle multiple reports simultaneously
- **Concurrent User Support**: Isolated job tracking for multiple users
- **File Validation**: Comprehensive PDF upload validation with duplicate detection
- **Health Monitoring**: Production-ready health checks and status endpoints

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini 2.5 API](https://ai.google.dev/docs)
- [FAISS Vector Database](https://faiss.ai/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 🎉 Production-Ready System Overview

This **Advanced TCS RAG Agent** represents a **production-ready, enterprise-grade solution** for automated financial document analysis that has evolved through three major development phases:

### 🚀 **Phase 1: Stability & API Completeness**
- Database auto-initialization and complete API coverage
- Fixed critical crashes and implemented robust error handling
- Production-ready endpoint architecture

### 🧠 **Phase 2: Chain of Thought RAG Revolution**
- **Advanced AI Architecture**: Replaced complex graph-based agents with streamlined Chain of Thought processing
- **Gemini 2.5 Models**: Lightweight Flash for contextualization, powerful Pro for analysis
- **Higher Accuracy**: Two-stage processing with intelligent question generation and comprehensive context analysis

### 🛡️ **Phase 3: Production Hardening & Final Polish**
- **Enterprise Resilience**: Individual task isolation, graceful failure recovery, comprehensive audit trails
- **Production Testing**: Complete end-to-end validation with realistic usage scenarios
- **Database Consistency**: Atomic operations, auto-initialization, complete status tracking

### 🎯 **Key Innovations**

#### **Chain of Thought Processing**
- **Intelligent Contextualization**: Simple tasks become detailed, self-contained questions
- **Multi-Modal Analysis**: Combined text and table context for comprehensive understanding
- **Structured Output**: Direct mapping to business-ready schemas

#### **Production Architecture**
- **Resilient Processing**: Individual task failures don't cascade
- **Real-time Transparency**: Live progress updates with specific task details
- **Complete Auditability**: Comprehensive trace logs for compliance and debugging

#### **Enterprise Scalability**
- **Asynchronous Design**: Non-blocking processing for multiple concurrent users
- **Resource Optimization**: Efficient model usage and vector store caching
- **Container-ready**: Production Docker deployment with health monitoring

**The system demonstrates how modern AI can transform traditional document processing into intelligent, self-managing extraction pipelines that provide transparency, auditability, and enterprise-grade reliability.**

**🌟 Ready for immediate production deployment with multi-user support and enterprise-grade reliability!** 🚀