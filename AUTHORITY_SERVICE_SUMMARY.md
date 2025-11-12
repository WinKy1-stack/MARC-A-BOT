# Authority Control Service - Project Summary

## 📋 Tổng quan dự án

Hệ thống Authority Control Service đã được xây dựng hoàn chỉnh để kết nối với các thư viện phân loại/từ khóa ngoài (MESH, LCC, LCSH, NLM) nhằm chuẩn hóa keywords thành các thuật ngữ chuẩn và tạo MARC21 fields.

## ✅ Deliverables đã hoàn thành

### 1. Research & Documentation
- ✅ Research document về MESH, LCC, LCSH, NLM structure
- ✅ API endpoints và query examples
- ✅ Rate limit và licensing notes
- 📄 File: `backend/services/authority/README.md`

### 2. Cache Database & Schema
- ✅ SQLite database design
- ✅ Authority terms table với indexes
- ✅ Cache statistics table
- ✅ Full-text search và fuzzy matching support
- 📄 File: `backend/services/authority/cache/cache_manager.py`

### 3. API Clients

#### MESH Client
- ✅ Search descriptors (exact & fuzzy)
- ✅ Get descriptor by ID
- ✅ Validate descriptors
- ✅ Tree hierarchy navigation
- 📄 File: `backend/services/authority/clients/mesh_client.py`

#### LOC Linked Data Client (LCSH/LCC)
- ✅ Search LCSH subject headings
- ✅ Search LCC classifications
- ✅ Get authority details
- ✅ Validate terms
- 📄 File: `backend/services/authority/clients/loc_client.py`

#### Z39.50 Client (NLM/LOC)
- ✅ Z39.50 connection handling
- ✅ Search by subject/classification
- ✅ MARC record parsing
- 📄 File: `backend/services/authority/clients/z3950_client.py`

### 4. Mapping Functions

#### Authority Mapper
- ✅ `find_authority_terms()` - Search với cache & fuzzy match
- ✅ `map_keyword_to_authorities()` - Map keywords với priority
- ✅ `validate_authority_term()` - Validate authority terms
- 📄 File: `backend/services/authority/mappers/authority_mapper.py`

### 5. MARC21 Field Generator
- ✅ `create_marc21_650_field()` - Tạo 650 fields
- ✅ `create_marc21_classification_field()` - Tạo 050/060 fields
- ✅ `format_marc_field_display()` - Format display
- ✅ `validate_marc_field()` - Validate MARC structure
- 📄 File: `backend/services/authority/marc_generator.py`

### 6. Main Service & Tools

#### Authority Service
- ✅ `process_keywords()` - End-to-end processing
- ✅ `search_authority()` - Single keyword search
- ✅ `validate_term()` - Term validation
- ✅ `batch_process()` - Batch processing
- ✅ Cache statistics & management
- 📄 File: `backend/services/authority/authority_service.py`

#### Agent Tools Interface
- ✅ Tool definitions for AI Agent
- ✅ 5 tools: search, map, validate, generate, stats
- ✅ JSON schema cho từng tool
- 📄 File: `backend/services/authority/tools.py`

### 7. API Endpoints
- ✅ POST `/api/authority/search` - Search authority terms
- ✅ POST `/api/authority/map` - Map keywords
- ✅ POST `/api/authority/validate` - Validate term
- ✅ POST `/api/authority/generate-marc` - Generate MARC fields
- ✅ GET `/api/authority/cache/stats` - Cache statistics
- ✅ GET `/api/authority/tools` - Tool definitions
- ✅ GET `/api/authority/health` - Health check
- 📄 File: `backend/api/authority_routes.py`

### 8. Error Handling & Logging
- ✅ Comprehensive error handling
- ✅ Logging configuration
- ✅ Cache statistics tracking
- ✅ API timeout & retry logic

### 9. Testing

#### Unit Tests
- ✅ Authority Mapper tests (20+ test cases)
- ✅ MARC Generator tests (15+ test cases)
- ✅ Cache Manager tests
- 📄 Files: `backend/tests/authority/test_*.py`

#### Integration Tests
- ✅ End-to-end workflow tests
- ✅ Real-world scenario tests
- ✅ Batch processing tests

### 10. Documentation & Examples
- ✅ Comprehensive README
- ✅ Quick Start Guide
- ✅ API Reference
- ✅ 10 example scripts
- 📄 Files: `README.md`, `QUICKSTART.md`, `authority_examples.py`

## 📁 Cấu trúc File được tạo

```
MARC-A-BOT/
├── QUICKSTART.md                           # Quick start guide
├── backend/
│   ├── app.py                              # Updated với authority routes
│   ├── requirements.txt                    # Updated dependencies
│   ├── api/
│   │   └── authority_routes.py             # API endpoints
│   ├── services/
│   │   └── authority/
│   │       ├── __init__.py
│   │       ├── config.py                   # Configuration
│   │       ├── authority_service.py        # Main service
│   │       ├── marc_generator.py           # MARC field generator
│   │       ├── tools.py                    # Agent tools
│   │       ├── README.md                   # Full documentation
│   │       ├── cache/
│   │       │   ├── __init__.py
│   │       │   └── cache_manager.py        # Cache management
│   │       ├── clients/
│   │       │   ├── __init__.py
│   │       │   ├── mesh_client.py          # MESH API
│   │       │   ├── loc_client.py           # LOC LCSH/LCC
│   │       │   └── z3950_client.py         # Z39.50
│   │       └── mappers/
│   │           ├── __init__.py
│   │           └── authority_mapper.py     # Keyword mapping
│   ├── scripts/
│   │   └── init_cache.py                   # Cache initialization
│   ├── examples/
│   │   └── authority_examples.py           # 10 examples
│   └── tests/
│       └── authority/
│           ├── __init__.py
│           ├── test_authority_mapper.py    # Unit tests
│           ├── test_marc_generator.py      # Unit tests
│           └── test_integration.py         # Integration tests
```

## 🚀 Cách sử dụng

### 1. Cài đặt

```powershell
cd c:\Workspace\Bien_muc\MARC-A-BOT\backend
pip install -r requirements.txt
```

### 2. Khởi chạy server

```powershell
python app.py
```

### 3. Sử dụng API

```powershell
# Search authority
curl -X POST http://localhost:5000/api/authority/search -H "Content-Type: application/json" -d "{\"keyword\": \"diabetes\", \"source\": \"MESH\"}"

# Map keywords
curl -X POST http://localhost:5000/api/authority/map -H "Content-Type: application/json" -d "{\"keywords\": [\"diabetes\", \"hypertension\"], \"subject_type\": \"medical\"}"
```

### 4. Sử dụng trong Python

```python
from services.authority.authority_service import AuthorityService

service = AuthorityService()
result = service.process_keywords(
    keywords=["diabetes", "hypertension"],
    subject_type="medical"
)
```

### 5. Sử dụng cho Agent

```python
from services.authority.tools import AuthorityTools

tools = AuthorityTools()
tool_defs = tools.get_tool_definitions()

result = tools.map_keywords_to_authorities(
    keywords=["diabetes"],
    subject_type="medical"
)
```

## 🔧 Features chính

### 1. Multi-Source Authority Support
- MESH (Medical Subject Headings)
- LCSH (Library of Congress Subject Headings)
- LCC (Library of Congress Classification)
- NLM (National Library of Medicine)

### 2. Smart Caching
- SQLite local cache
- Exact match → Fuzzy match → Online query
- Automatic cache statistics tracking
- Target hit rate: 80%+

### 3. Intelligent Mapping
- Priority-based source selection
- Subject type awareness (medical/general/science)
- Confidence scoring
- Uncontrolled term handling

### 4. MARC21 Compliance
- Standard 650 field generation
- Proper indicators for each source
- Authority ID formatting
- Field validation

### 5. Agent Integration
- 5 tools cho AI Agent
- JSON schema definitions
- Easy integration với agent workflow

## 📊 Performance Metrics

- **Cache Performance:** 80%+ hit rate (target)
- **Fuzzy Match:** 80/100 threshold
- **API Timeout:** 30 seconds
- **Retry Logic:** 3 attempts
- **Max Suggestions:** 10 per keyword

## 🧪 Testing

```powershell
# Run all tests
pytest backend/tests/authority/ -v

# Run with coverage
pytest backend/tests/authority/ -v --cov=services.authority --cov-report=html

# Run specific test
pytest backend/tests/authority/test_authority_mapper.py -v
```

## 📖 Documentation

- **Full Documentation:** `backend/services/authority/README.md`
- **Quick Start:** `QUICKSTART.md`
- **Examples:** `backend/examples/authority_examples.py`
- **API Reference:** Trong README.md

## 🎯 Use Cases

### Use Case 1: Medical Book Processing
```python
service.process_keywords(
    ["diabetes mellitus", "insulin", "blood glucose"],
    subject_type="medical"
)
# → Returns MESH authorities + MARC 650 fields
```

### Use Case 2: General Subject Cataloging
```python
service.process_keywords(
    ["education", "teaching", "learning"],
    subject_type="general"
)
# → Returns LCSH authorities + MARC 650 fields
```

### Use Case 3: Vietnamese Book Example
Dựa trên MARC record mẫu:
```python
service.process_keywords(
    ["Educators", "Teachers"],
    subject_type="general"
)
# → Generates:
# 650  0 $aEducators $zVietnam $vBiography.
# 650  0 $aTeachers $zVietnam $vBiography.
```

## 🔍 Authority Sources Details

### MESH
- **URL:** https://meshb.nlm.nih.gov/api
- **Best for:** Medical/health topics
- **Example ID:** D015996
- **MARC Indicator:** ind2="2"

### LCSH
- **URL:** http://id.loc.gov/authorities/subjects
- **Best for:** General topics
- **Example ID:** sh2009007992
- **MARC Indicator:** ind2="0"

### LCC
- **URL:** http://id.loc.gov/authorities/classification
- **Best for:** Classification numbers
- **Example:** QA76.9.A25
- **MARC Field:** 050

### NLM
- **Protocol:** Z39.50
- **Host:** locatorplus.gov:210
- **Best for:** Medical classification
- **MARC Field:** 060

## 🛠️ Configuration

Edit `backend/services/authority/config.py` để thay đổi:
- API URLs
- Z39.50 settings
- Cache thresholds
- Rate limits
- Priority orders

## 📝 Notes

### Dependencies
- Flask 3.0.0
- requests 2.31.0
- rapidfuzz 3.5.2
- PyZ3950 3.0
- pymarc 4.2.2
- pytest 7.4.3

### Database
- SQLite database tự động được tạo tại `backend/services/authority/cache/`
- Có thể clear cache bằng `service.clear_cache()`

### Network Requirements
- Internet connection để truy cập MESH API và LOC Linked Data
- Z39.50 port 210 không bị firewall block (optional)

## 🎓 Next Steps

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Initialize cache:** `python backend/scripts/init_cache.py`
3. **Run examples:** `python backend/examples/authority_examples.py`
4. **Start server:** `python backend/app.py`
5. **Run tests:** `pytest backend/tests/authority/ -v`
6. **Integrate với Agent workflow**

## 💡 Tips

- Sử dụng `subject_type="medical"` cho sách y khoa
- Sử dụng `subject_type="general"` cho sách giáo dục, công nghệ
- Check cache stats thường xuyên để monitor performance
- Batch processing cho nhiều keywords để tối ưu performance
- Validate MARC fields trước khi export

## 🤝 Support

- Documentation: `backend/services/authority/README.md`
- Examples: 10 examples trong `authority_examples.py`
- Tests: 40+ test cases trong `tests/authority/`

---

**Project Status:** ✅ COMPLETED

**Date:** November 12, 2025

**Team:** MARC-A-BOT Development Team
