# AI-Powered Command Center Template

A production-ready template for building AI-powered business process automation systems. This template follows the **Supervity Command Center Playbook** - our methodology for creating intelligent systems that don't just help users perform tasks, but give users and AI the oversight and control to manage entire business processes.

**📖 [Read the Complete Playbook →](docs/command_center_guide.md)**

Perfect for building Command Centers across any business domain: Procurement, HR, ITSM, Customer Service, Accounts Payable, and more.

## 🏗️ Tech Stack

**Backend (AI-Ready):**
- FastAPI (Python web framework) - Perfect for AI model integration
- Gunicorn (WSGI server for production)
- Uvicorn (ASGI server)
- Background task support (for AI processing)
- AI Model Abstraction Layer (swap between OpenAI, Gemini, Anthropic)

**Frontend (Command Center UI):**
- Next.js 15 with React 19
- TypeScript
- Tailwind CSS
- Radix UI components
- Built for Dashboard + Workbench + AI Chat interfaces

**Infrastructure:**
- Docker & Docker Compose
- Multi-stage Docker builds for optimized production images
- Ready for PostgreSQL, Redis, and other AI-supporting services

## 🧠 Command Center Architecture

This template implements the **Three Pillars of a Command Center**:

1. **🎯 The Dashboard ("The Eyes")** - Strategic overview with role-based insights
2. **🛠️ The Workbench ("The Hands")** - Tactical workspace for handling AI exceptions  
3. **⚡ The AI Engine ("The Brain")** - Configurable policies and autonomous decision-making

**Core Operational Loop:** Ingest → Link/Enrich → Analyze/Decide → Act → Learn

## 📁 Project Structure

```
├── app/                    # FastAPI backend application
│   ├── main.py            # Main FastAPI app with health checks & CORS
│   └── modules/           # Your Command Center modules go here
│       └── ai_service/    # AI model abstraction layer
├── docs/                  # Documentation & design decisions
│   └── command_center_guide.md  # The complete playbook
├── frontend/              # Next.js Command Center UI
│   ├── src/               # Dashboard, Workbench, AI Chat components
│   ├── Dockerfile         # Frontend container config
│   └── package.json       # Dependencies & scripts
├── gunicorn/              # Gunicorn server configurations
│   ├── dev.py             # Development settings (hot reload)
│   └── prod.py            # Production settings (optimized)
├── packages/              # Python dependencies
│   └── requirements.txt   # Backend packages (add AI SDKs here)
├── docker-compose.yml     # Multi-container orchestration
├── Dockerfile             # Backend container config (multi-stage)
├── Makefile              # Development workflow automation
└── README.md             # This file
```

## 🎯 Getting Started with Command Centers

**New to AI-Powered Command Centers?** Start here:

1. **📖 Read the Playbook** - [Complete Command Center Guide](docs/command_center_guide.md)
2. **🧠 Choose Your Domain** - Procurement? HR? ITSM? Customer Service?
3. **🔍 Identify the Process** - Use the "5 Whys" technique from the playbook
4. **⚡ Define Your Loop** - Map your process to: Ingest → Link → Analyze → Act → Learn
5. **🏗️ Build Your Pillars** - Dashboard, Workbench, and AI Engine

**Example Command Centers You Can Build:**
- **Procurement Command Center** - Automate Purchase Request approvals and vendor management
- **HR Onboarding Command Center** - Orchestrate new hire workflows across departments  
- **ITSM Command Center** - Intelligent ticket routing and resolution automation
- **AP Command Center** - 3-way matching and invoice processing automation

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Make (optional, for convenient commands)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   ```

2. **Set up environment files:**
   
   **Root `.env` file:**
   ```bash
   # Create .env in project root
   cat > .env << EOF
   FRONTEND_URL=http://localhost:3000
   NODE_ENV=development
   EOF
   ```
   
   **Frontend `.env.local` file:**
   ```bash
   # Create .env.local in frontend directory
   cat > frontend/.env.local << EOF
   NEXT_PUBLIC_API_URL=http://localhost:8000
   EOF
   ```

3. **Start services:**
   ```bash
   make up
   ```
   
   Or without Make:
   ```bash
   docker-compose up --build -d
   ```

4. **Access your application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/api/health

5. **View logs:**
   ```bash
   make logs-fe    # Frontend logs
   make logs-be    # Backend logs
   ```

6. **Stop services:**
   ```bash
   make down
   ```

## 🛠️ Available Commands

The Makefile provides convenient shortcuts for common development tasks:

```bash
make help           # Show all available commands
make up             # Start all services
make down           # Stop all services
make logs-be        # View backend logs
make logs-fe        # View frontend logs
```

### Database Migration Commands (when database is configured)
```bash
make migrate-create MSG='description'   # Create new migration
make migrate-up                         # Apply pending migrations
make migrate-down                       # Rollback one migration
make migrate-history                    # Show migration history
make reset-db                           # Clean & reinitialize database
```

## 🌐 Environment Configuration

### Development
The template works out-of-the-box for local development with sensible defaults.

### Production
Configure environment variables in `docker-compose.yml` or use a `.env` file:

```bash
# Example production environment variables
NODE_ENV=production
FRONTEND_URL=https://your-domain.com
GUNICORN_LOG_LEVEL=info
WEB_CONCURRENCY=2
WORKER_CONNECTIONS=1000
GUNICORN_TIMEOUT=120

# Database (uncomment in docker-compose.yml when ready)
# PG_USER=your_db_user
# PG_PASSWORD=your_db_password
# PG_HOST=your_db_host
# PG_PORT=5432
# PG_DB_NAME=your_db_name

# Add other service-specific variables as needed
```

## 🚢 Deployment

### Local Production Testing
```bash
# Use production gunicorn config
docker-compose up --build -d
# Backend will use gunicorn/dev.py by default
# For production testing, modify docker-compose.yml to use gunicorn/prod.py
```

### Production Deployment
1. Set environment variables for your production environment
2. Use the production Gunicorn configuration
3. Configure reverse proxy (nginx/traefik) if needed
4. Set up SSL certificates
5. Configure monitoring and logging

## 🔧 Building Your Command Center

### Step 1: Set Up AI Integration

**Add AI SDKs to your backend:**
```bash
# Add to packages/requirements.txt
echo "new-package==1.0.0" >> packages/requirements.txt
# Rebuild containers
make down && make up
```

**Create your AI Service abstraction:**
```python
# app/modules/ai_service/main.py
async def get_recommendation(data: dict) -> dict:
    """Your AI logic here - swap between models easily"""
    pass
```

### Step 2: Build the Three Pillars

**Dashboard (`frontend/src/app/dashboard`):**
- Role-based views for managers vs operators
- Key metrics and performance indicators
- Strategic insights, not just data dumps

**Workbench (`frontend/src/app/workbench`):**
- Single-record focused workspace
- All context for human decisions
- **Critical:** Feedback mechanisms to teach the AI

**AI Policies (`frontend/src/app/policies`):**
- Rule builder interface for admins
- Visual policy management
- Real-time rule testing and validation

### Step 3: Implement the Learning Loop

**Audit Everything:**
```python
# Store raw inputs, AI outputs, and final outcomes
# Create feedback tables linked to specific records
```

**Background Learning Jobs:**
```python
# Scan audit logs for patterns
# Generate automation suggestions
# Process explicit user feedback
```

## 🔍 Command Center Features

**AI-First Architecture:**
- **AI Model Abstraction**: Swap between OpenAI, Gemini, Anthropic without code changes
- **Background AI Processing**: Non-blocking AI calls keep the UI responsive
- **Learning Loop Integration**: Built-in feedback mechanisms and audit trails

**Production-Ready Foundation:**
- **Hot Reload**: Backend code changes trigger automatic reloads in development
- **Health Checks**: Docker health checks ensure services are running correctly
- **CORS Configuration**: Pre-configured for frontend-backend communication
- **Multi-stage Builds**: Optimized Docker images for production
- **Flexible Configuration**: Environment-based settings for different deployment scenarios

**Command Center Specific:**
- **Three Pillars Architecture**: Dashboard, Workbench, and AI Policies structure
- **Role-Based Access**: Different views for managers, operators, and admins
- **Audit Trail**: Every decision tracked for AI learning and compliance
- **Real-Time Updates**: WebSocket support for live status updates

## 📝 Development Notes

- The backend runs on port 8000, frontend on port 3000
- CORS is configured to allow frontend communication
- Database configuration is commented out but ready to uncomment when needed
- Migration tools are set up for future database schema management
- Both services restart automatically unless stopped

## 🆘 Troubleshooting

**Services won't start:**
- **First, check environment files exist:**
  - Root `.env` file with `FRONTEND_URL` and `NODE_ENV`
  - Frontend `.env.local` file with `NEXT_PUBLIC_API_URL`
- Ensure ports 3000 and 8000 are available
- Check Docker daemon is running
- View logs: `make logs-be` or `make logs-fe`

**CORS errors:**
- Verify `FRONTEND_URL` in root `.env` matches your frontend URL
- Ensure `NEXT_PUBLIC_API_URL` in `frontend/.env.local` points to your backend
- Check browser network tab for actual request URLs

**Frontend can't connect to backend:**
- Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`
- Check that backend is running on port 8000
- Test backend directly: `curl http://localhost:8000/api/health`

**Database connection issues:**
- Uncomment and configure database settings in `docker-compose.yml`
- Ensure database service is running and accessible

---

## 🚀 Ready to Build Intelligence?

This template isn't just about building software—it's about creating **intelligent systems that become partners to your business**. 

**Next Steps:**
1. 📖 **Study the Playbook**: [Complete Command Center Guide](docs/command_center_guide.md)
2. 🎯 **Identify Your Process**: What business process needs AI-powered automation?
3. 🏗️ **Start Building**: Use this template as your launchpad
4. 🧠 **Think AI-First**: Every feature should enable AI autonomy or human oversight
5. 📚 **Document Everything**: Record your design decisions in `/docs`

**Remember the Supervity Philosophy**: We don't just solve today's problems—we build systems that learn and become indispensable tomorrow.

Happy building! 🎉 ⚡ 🧠
