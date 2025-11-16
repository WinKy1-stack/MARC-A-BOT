# MARC-A-BOT

OCR metadata extraction và authority control system cho thư viện số - Tự động trích xuất metadata từ ảnh tài liệu và chuẩn hóa theo MARC21.

## 🎯 Tính năng chính

- **OCR Extraction**: 5 agents tự động trích xuất metadata (title, authors, ISBN, keywords, document type)
- **Authority Control**: Kết nối MESH, LCSH, LCC, NLM để chuẩn hóa từ khóa
- **MARC21 Generation**: Tạo bản ghi MARC21 đầy đủ từ OCR text
- **Image Processing**: Upload và xử lý ảnh với giao diện hiện đại
- **RESTful API**: 8 endpoints cho authority control và metadata extraction

## 🏗️ Kiến trúc

### Frontend
- **React 18 + TypeScript** - UI hiện đại với type safety
- **Vite** - Build tool nhanh
- **TailwindCSS** - Styling

### Backend
- **Flask 3.0** - Web framework
- **5 OCR Agents** - Extraction pipeline
- **Authority Service** - 4 external library integrations (MESH, LCSH, LCC, NLM)
- **SQLite Cache** - Fuzzy matching cache
- **MARC21 Generator** - Compliant output

## 📦 Cài đặt

### Prerequisites
```bash
Node.js 18+
Python 3.11+
```

### 1. Clone repository
```bash
git clone https://github.com/LockMan04/MARC-A-BOT.git
cd MARC-A-BOT
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
python app.py
```

Backend chạy tại: `http://localhost:5000`

### 3. Frontend Setup
```bash
cd ..  # Back to root
npm install
npm run dev
```

Frontend chạy tại: `http://localhost:5173`

## 🚀 Sử dụng

### Basic Usage - OCR Extraction

```python
from backend.services.agents import MARCIntegration

# Extract metadata from OCR text
integration = MARCIntegration()
marc_record = integration.agents_output_to_marc21(
    ocr_text="""
    Introduction to Clinical Medicine
    By Dr. John Smith, MD
    ISBN: 978-0-123-45678-9
    Copyright © 2024
    """,
    keywords=['Clinical Medicine'],
    classification_frameworks=[
        {'type': 'LCC', 'number': 'R729'}
    ]
)

# Output: Complete MARC21 record
print(integration.format_marc_display(marc_record))
```

### Authority Control

```python
from backend.services.authority.tools import AuthorityTools

tools = AuthorityTools()

# Get classification frameworks and controlled keywords
result = tools.get_classification_and_keywords(
    keywords=['diabetes', 'insulin'],
    subject_type='medical'
)

# Separated output
frameworks = result['output']['classification_framework']  # LCC/NLM numbers
keywords = result['output']['controlled_keywords']         # MESH/LCSH terms
```

### API Endpoints

```bash
# Authority Control
POST /api/authority/search
POST /api/authority/map
POST /api/authority/classification-keywords

# Health Check
GET /api/authority/health
GET /api/authority/cache/stats
```

## 📊 Agents Overview

| Agent | Purpose | Output | MARC Field |
|-------|---------|--------|------------|
| **Agent 1** | Title extraction | "Clinical Medicine" | 245 |
| **Agent 2** | Author normalization | ["Doe, John"] | 100, 700 |
| **Agent 3** | ISBN & year | "978-X-XX-X", 2024 | 020, 260 |
| **Agent 4** | Keywords → authorities | MESH/LCSH terms | 050, 060, 650 |
| **Agent 5** | Document classification | "textbook" | Leader |

## 🧪 Testing

```bash
# Test all agents
python demo_agents.py --mode all

# Test individual components
python backend/services/agents/agent_1_title.py
python backend/services/agents/agent_2_author.py
```

## 📁 Cấu trúc

```
MARC-A-BOT/
├── backend/
│   ├── services/
│   │   ├── agents/              # 5 OCR extraction agents
│   │   │   ├── agent_1_title.py
│   │   │   ├── agent_2_author.py
│   │   │   ├── agent_3_isbn_year.py
│   │   │   ├── agent_5_doctype.py
│   │   │   └── marc_integration.py
│   │   └── authority/           # Authority control service
│   │       ├── clients/         # MESH, LOC, Z39.50 clients
│   │       ├── tools.py         # 6 tools for agents
│   │       └── authority_service.py
│   ├── api/
│   │   └── authority_routes.py  # 8 API endpoints
│   └── app.py
├── src/                         # React frontend
├── demo_agents.py               # Demo script
├── requirements.txt
└── package.json
```

## 📚 Documentation

- **[Authority Quick Reference](AUTHORITY_QUICK_REFERENCE.md)** - API documentation
- **[Agents Implementation](AGENTS_IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[Quick Start Guide](AGENTS_QUICK_START.md)** - Usage examples
- **[Backend Deployment](backend/DEPLOYMENT_GUIDE.md)** - Deployment guide

## 🔧 Requirements

### Python
- Flask 3.0.0
- requests 2.31.0
- rapidfuzz 3.5.2
- pymarc 4.2.2
- pytest 7.4.3

### Node.js
- React 18
- TypeScript 5
- Vite 5
- TailwindCSS 3

## 🌟 Key Features

✅ **Complete OCR Pipeline** - 5 specialized agents  
✅ **Authority Control** - 4 external library integrations  
✅ **MARC21 Compliant** - Standard bibliographic format  
✅ **Multilingual** - English + Vietnamese support  
✅ **Cache System** - SQLite with fuzzy matching  
✅ **Production Ready** - 70+ test cases

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributors

- LockMan04 - Initial work

## 🔗 Links

- GitHub: https://github.com/LockMan04/MARC-A-BOT
- Branch: feature/lib-protocols-integration

---

**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Updated:** Nov 2024
