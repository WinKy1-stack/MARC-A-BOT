# MARC-A-BOT Project Structure

## 📁 Cấu trúc Dự án (Cleaned & Organized)

```
MARC-A-BOT/
│
├── 📄 README.md                        # Main documentation
├── 📄 AI_AGENT_WITH_TOOLS.md          # AI framework integration guide
├── 📄 QUICK_START_AGENT.md            # Quick setup guide
├── 📄 .gitignore                      # Git ignore rules
├── 📄 package.json                    # Frontend dependencies
├── 📄 vite.config.ts                  # Vite configuration
├── 📄 tsconfig.json                   # TypeScript config
├── 📄 tailwind.config.js              # Tailwind config
├── 📄 index.html                      # Entry HTML
│
├── 📁 backend/                        # Python Backend
│   ├── 📄 app.py                      # Flask application entry
│   ├── 📄 requirements.txt            # Python dependencies
│   ├── 📄 DEPLOYMENT_GUIDE.md         # Deployment instructions
│   ├── 📄 .env.example                # Environment variables template
│   │
│   ├── 📁 api/                        # API Routes
│   │   └── authority_routes.py        # 8 authority endpoints
│   │
│   ├── 📁 services/                   # Business Logic
│   │   │
│   │   ├── 📁 agents/                 # OCR Extraction Agents
│   │   │   ├── agent_1_title.py       # Title extraction
│   │   │   ├── agent_2_author.py      # Author extraction
│   │   │   ├── agent_3_isbn_year.py   # ISBN/Year extraction
│   │   │   ├── agent_5_doctype.py     # Document type classifier
│   │   │   ├── ai_agent_with_tools.py # AI agent wrapper (6 tools)
│   │   │   ├── marc_integration.py    # Combine all agents → MARC21
│   │   │   └── __init__.py
│   │   │
│   │   └── 📁 authority/              # Agent 4 - Authority Control
│   │       ├── authority_service.py   # Main orchestrator
│   │       ├── tools.py               # 6 tools for AI agents
│   │       ├── config.py              # Configuration
│   │       ├── marc_generator.py      # MARC field generator
│   │       │
│   │       ├── 📁 clients/            # External API clients
│   │       │   ├── mesh_client.py     # MESH (Medical)
│   │       │   ├── loc_client.py      # LCSH + LCC
│   │       │   ├── z3950_client.py    # Z39.50 (NLM, LOC)
│   │       │   └── __init__.py
│   │       │
│   │       ├── 📁 cache/              # Caching System
│   │       │   ├── cache_manager.py   # SQLite + fuzzy matching
│   │       │   ├── authority_cache.db # Cache database
│   │       │   └── __init__.py
│   │       │
│   │       └── 📁 mappers/            # Keyword Mapping
│   │           ├── authority_mapper.py # Map keywords → authorities
│   │           └── __init__.py
│   │
│   ├── 📁 tests/                      # Unit Tests
│   │   ├── __init__.py
│   │   └── 📁 authority/
│   │       └── test_authority_mapper.py
│   │
│   └── 📁 docs/                       # Additional docs (if needed)
│
├── 📁 src/                            # React Frontend
│   ├── 📄 main.tsx                    # Entry point
│   ├── 📄 App.tsx                     # Main App component
│   ├── 📄 App.css                     # App styles
│   ├── 📄 index.css                   # Global styles
│   │
│   ├── 📁 components/                 # React Components
│   │   ├── Dropzone.tsx               # File upload
│   │   ├── Header.tsx                 # Navigation
│   │   ├── ImagePreview.tsx           # Image preview
│   │   ├── MARCViewer.tsx            # MARC record display
│   │   ├── ToastProvider.tsx          # Notifications
│   │   │
│   │   ├── 📁 layout/
│   │   │   └── MainLayout.tsx         # Page layout
│   │   │
│   │   └── 📁 ui/                     # UI Components
│   │       ├── DropzoneEmpty.tsx
│   │       ├── ImageGrid.tsx
│   │       └── ProcessButton.tsx
│   │
│   ├── 📁 hooks/                      # Custom React Hooks
│   │   ├── useAppHandlers.ts          # Main app logic
│   │   ├── useDropzone.ts             # Upload handling
│   │   ├── useFilePreview.ts          # File preview
│   │   ├── useImagePreview.ts         # Image preview
│   │   ├── useImageUploader.ts        # Image upload
│   │   └── useMARC.ts                 # MARC handling
│   │
│   ├── 📁 types/                      # TypeScript Types
│   │   └── index.ts                   # Type definitions
│   │
│   ├── 📁 constants/                  # Constants
│   │   ├── fileConfig.ts              # Upload config
│   │   └── marc.ts                    # MARC definitions
│   │
│   └── 📁 assets/                     # Static Assets
│       └── react.svg
│
├── 📁 public/                         # Public Assets
│
└── 📁 venv/                           # Python Virtual Environment (gitignored)
```

## 🎯 Core Modules

### Backend Services

#### 1. OCR Agents (5 agents)
```
services/agents/
├── agent_1_title.py      → Extract title
├── agent_2_author.py     → Extract author(s)
├── agent_3_isbn_year.py  → Extract ISBN + year
├── agent_5_doctype.py    → Classify document type
└── marc_integration.py   → Combine → MARC21
```

#### 2. Authority Control (Agent 4)
```
services/authority/
├── authority_service.py  → Orchestrator
├── tools.py              → 6 AI tools
├── clients/              → 4 external APIs (MESH, LCSH, LCC, NLM)
├── cache/                → SQLite caching
├── mappers/              → Keyword mapping
└── marc_generator.py     → MARC field generation
```

#### 3. AI Agent Wrapper
```
services/agents/ai_agent_with_tools.py
- KeywordProcessorAgent class
- 6 tools for CrewAI/LangGraph/LangChain/Gemini
- Standalone usage support
```

### Frontend Components

```
src/
├── components/          → UI components (10+)
├── hooks/              → Custom hooks (6)
├── types/              → TypeScript definitions
└── constants/          → Configuration
```

## 📡 API Endpoints (8)

```
POST   /api/authority/search                    # Search authority terms
POST   /api/authority/map                       # Map keywords + MARC
POST   /api/authority/classification-keywords   # Get frameworks + keywords
POST   /api/authority/validate                  # Validate term
POST   /api/authority/generate-marc            # Generate MARC fields
GET    /api/authority/health                   # Health check
GET    /api/authority/cache/stats              # Cache statistics
POST   /api/authority/cache/clear              # Clear cache
```

## 🔧 Dependencies

### Backend (Python)
```
Flask==3.0.0              # Web framework
requests==2.31.0          # HTTP client
rapidfuzz==3.5.2          # Fuzzy matching
pymarc==4.2.2             # MARC processing
pytest==7.4.3             # Testing
```

### Frontend (Node.js)
```
react@18                  # UI framework
typescript@5              # Type safety
vite@5                    # Build tool
tailwindcss@3             # Styling
```

## 📚 Documentation Files

1. **README.md** - Main project guide
2. **AI_AGENT_WITH_TOOLS.md** - AI framework integration (CrewAI, LangGraph, LangChain, Gemini)
3. **QUICK_START_AGENT.md** - Quick setup for AI agents
4. **backend/DEPLOYMENT_GUIDE.md** - Deployment instructions

## 🎯 Key Features

✅ 5 OCR extraction agents  
✅ Authority Control with 4 libraries (MESH, LCSH, LCC, NLM)  
✅ 6 AI tools (framework compatible)  
✅ MARC21 compliant output  
✅ SQLite cache with fuzzy matching  
✅ 8 RESTful API endpoints  
✅ Modern React UI with TypeScript  
✅ Production ready

---

**Project:** MARC-A-BOT  
**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Updated:** November 2024
