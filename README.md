# MARC-A-BOT

Hệ thống OCR metadata extraction và authority control cho thư viện số - Tự động trích xuất metadata từ ảnh và chuẩn hóa theo MARC21.

## 🎯 Tính năng

- **5 OCR Agents**: Title, Author, ISBN/Year, Keywords, Document Type
- **Authority Control**: MESH, LCSH, LCC, NLM integration với cache
- **6 AI Tools**: Compatible với CrewAI, LangGraph, LangChain, Gemini
- **MARC21 Standard**: Complete bibliographic records
- **RESTful API**: 8 endpoints
- **Modern UI**: React + TypeScript + TailwindCSS

## 🏗️ Tech Stack

**Frontend:** React 18, TypeScript, Vite, TailwindCSS  
**Backend:** Python 3.11, Flask 3.0, SQLite  
**APIs:** MESH, LCSH, LCC, NLM (external authorities)

## 📦 Cài đặt

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py  # → http://localhost:5000
```

### Frontend

```bash
npm install
npm run dev  # → http://localhost:5173
```

## 🚀 Sử dụng

### 1. OCR Pipeline - Extract Metadata

```python
from backend.services.agents import MARCIntegration

integration = MARCIntegration()
marc_record = integration.agents_output_to_marc21(
    ocr_text="""
    Clinical Medicine Handbook
    By Dr. John Smith
    ISBN: 978-0-123-45678-9
    © 2024
    """,
    keywords=['clinical medicine']
)
```

### 2. AI Agent - Process Keywords

```python
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

agent = KeywordProcessorAgent()
result = agent.process_keywords(
    keywords=['diabetes', 'insulin'],
    subject_type='medical'
)

# Output: classification_framework (LCC/NLM) + controlled_keywords (MESH/LCSH)
```

### 3. Authority API - Map Keywords

```bash
curl -X POST http://localhost:5000/api/authority/classification-keywords \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["diabetes"], "subject_type": "medical"}'
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/authority/search` | POST | Search authority terms |
| `/api/authority/map` | POST | Map keywords + MARC |
| `/api/authority/classification-keywords` | POST | Get frameworks + keywords |
| `/api/authority/validate` | POST | Validate term |
| `/api/authority/generate-marc` | POST | Generate MARC21 fields |
| `/api/authority/health` | GET | Health check |
| `/api/authority/cache/stats` | GET | Cache statistics |
| `/api/authority/cache/clear` | POST | Clear cache |

## 🤖 AI Framework Integration

Compatible với CrewAI, LangGraph, LangChain, Gemini - Xem chi tiết tại:
- **[AI Agent Guide](AI_AGENT_WITH_TOOLS.md)** - Hướng dẫn chi tiết
- **[Quick Start](QUICK_START_AGENT.md)** - Setup nhanh

```python
# CrewAI Example
from crewai import Agent
agent = Agent(role='Cataloger', tools=keyword_agent.get_available_tools())

# Gemini Example
import google.generativeai as genai
model.generate_content("Process keywords", tools=agent.get_available_tools())
```

## 🎯 5 OCR Agents

| Agent | Input | Output | MARC |
|-------|-------|--------|------|
| Agent 1 | OCR text | Title | 245 |
| Agent 2 | OCR text | Author(s) | 100, 700 |
| Agent 3 | OCR text | ISBN + Year | 020, 260 |
| Agent 4 | Keywords | MESH/LCSH terms | 050, 060, 650 |
| Agent 5 | OCR text | Document type | Leader |

**Agent 4** = `backend/services/authority/` (toàn bộ module)

## 📁 Cấu trúc

```
MARC-A-BOT/
├── backend/
│   ├── services/
│   │   ├── agents/                    # OCR agents
│   │   │   ├── agent_1_title.py
│   │   │   ├── agent_2_author.py
│   │   │   ├── agent_3_isbn_year.py
│   │   │   ├── agent_5_doctype.py
│   │   │   ├── ai_agent_with_tools.py # 6 AI tools
│   │   │   └── marc_integration.py    # Combine agents
│   │   └── authority/                 # Agent 4 - Authority Control
│   │       ├── clients/               # MESH, LOC, Z39.50
│   │       ├── cache/                 # SQLite cache
│   │       ├── mappers/               # Keyword mapping
│   │       ├── tools.py               # 6 tools interface
│   │       └── authority_service.py
│   ├── api/authority_routes.py        # 8 endpoints
│   ├── app.py                         # Flask app
│   └── requirements.txt
├── src/                               # React frontend
│   ├── components/
│   ├── hooks/
│   └── types/
├── AI_AGENT_WITH_TOOLS.md             # AI integration guide
├── QUICK_START_AGENT.md               # Quick setup
└── package.json
```

## 🔧 Dependencies

```
# Backend
Flask==3.0.0
requests==2.31.0
rapidfuzz==3.5.2
pymarc==4.2.2
pytest==7.4.3

# Frontend
react@18
typescript@5
vite@5
```

## 🌟 Features

✅ Complete OCR pipeline (5 agents)  
✅ Authority control (MESH, LCSH, LCC, NLM)  
✅ MARC21 compliant output  
✅ SQLite cache with fuzzy matching  
✅ 6 AI tools (CrewAI/LangGraph compatible)  
✅ 8 RESTful API endpoints  
✅ Production ready

## 📚 Documentation

- **[AI Agent with Tools](AI_AGENT_WITH_TOOLS.md)** - Framework integration guide
- **[Quick Start Agent](QUICK_START_AGENT.md)** - Quick setup guide
- **[Deployment Guide](backend/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Architecture](backend/docs/ARCHITECTURE.md)** - System architecture

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Test authority service
python -m services.authority.tools

# Test AI agent
python services/agents/ai_agent_with_tools.py
```

## 📝 License

MIT License

## 👥 Contributors

LockMan04 - [@LockMan04](https://github.com/LockMan04)

## 🔗 Repository

**GitHub:** [LockMan04/MARC-A-BOT](https://github.com/LockMan04/MARC-A-BOT)  
**Branch:** feature/lib-protocols-integration

---

**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Updated:** November 2024
