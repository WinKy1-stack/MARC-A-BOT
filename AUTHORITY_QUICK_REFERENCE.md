# Authority Control Service - Quick Reference

## 📋 Overview

Authority control service kết nối 4 thư viện chuẩn hóa từ khóa:
- **MESH** - Medical Subject Headings
- **LCSH** - Library of Congress Subject Headings  
- **LCC** - Library of Congress Classification
- **NLM** - National Library of Medicine

## 🚀 Quick Start

```bash
# Start service
cd backend
python app.py
# Service runs at http://localhost:5000
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/authority/health` | GET | Health check |
| `/api/authority/search` | POST | Search authority terms |
| `/api/authority/map` | POST | Map keywords to authorities |
| `/api/authority/classification-keywords` | POST | Get frameworks + keywords |
| `/api/authority/validate` | POST | Validate term |
| `/api/authority/generate-marc` | POST | Generate MARC21 |
| `/api/authority/cache/stats` | GET | Cache statistics |

## 💡 Usage Examples

### Search Authority Terms

```bash
curl -X POST http://localhost:5000/api/authority/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "diabetes", "source": "MESH"}'
```

### Map Keywords

```bash
curl -X POST http://localhost:5000/api/authority/map \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["diabetes", "insulin"],
    "subject_type": "medical"
  }'
```

### Get Classification & Keywords (Tool #6)

```bash
curl -X POST http://localhost:5000/api/authority/classification-keywords \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["diabetes", "clinical medicine"],
    "subject_type": "medical"
  }'
```

**Response:**
```json
{
  "classification_framework": [
    {
      "framework": "NLM",
      "classification_number": "WK 810",
      "marc_field": "060"
    }
  ],
  "controlled_keywords": [
    {
      "keyword": "Diabetes Mellitus",
      "vocabulary": "MESH",
      "term_id": "D003920",
      "marc_field": "650"
    }
  ]
}
```

## 🐍 Python Usage

### Using Tools

```python
from backend.services.authority.tools import AuthorityTools

tools = AuthorityTools()

# Get classification frameworks and keywords
result = tools.get_classification_and_keywords(
    keywords=['diabetes', 'insulin'],
    subject_type='medical'
)

# Access separated outputs
frameworks = result['output']['classification_framework']  # LCC/NLM
keywords = result['output']['controlled_keywords']         # MESH/LCSH
marc_050_060 = result['marc_fields']['classification']
marc_650 = result['marc_fields']['subjects']
```

### Using Service Directly

```python
from backend.services.authority.authority_service import AuthorityService

service = AuthorityService()

# Search single term
results = service.search_authority('diabetes', source='MESH')

# Process multiple keywords
result = service.process_keywords(
    keywords=['diabetes', 'insulin'],
    subject_type='medical'
)
```

## 🔧 Tool Definitions

6 tools available for AI agents:

1. **search_authority_terms** - Search single keyword
2. **map_keywords_to_authorities** - Batch mapping + MARC
3. **validate_authority_term** - Validate term
4. **generate_marc21_650_fields** - Generate MARC 650
5. **get_cache_statistics** - Performance stats
6. **get_classification_and_keywords** - Separated frameworks + keywords ⭐

## 📊 Output Structure

### Tool #6 Output (Classification + Keywords)

```python
{
  'classification_framework': [    # KHUNG PHÂN LOẠI
    {
      'framework': 'LCC' | 'NLM',
      'classification_number': 'R729',
      'description': 'Clinical medicine',
      'marc_field': '050' | '060'
    }
  ],
  'controlled_keywords': [          # TỪ KHÓA CHUẨN
    {
      'keyword': 'Diabetes Mellitus',
      'vocabulary': 'MESH' | 'LCSH',
      'term_id': 'D003920',
      'confidence': 0.95,
      'marc_field': '650'
    }
  ],
  'marc_fields': {
    'classification': ['050 _4 $a R729'],  # LCC/NLM
    'subjects': ['650 _0 $a Diabetes']     # MESH/LCSH
  }
}
```

## 🎯 Key Features

- **4 Authority Sources**: MESH, LCSH, LCC, NLM
- **Smart Caching**: SQLite + fuzzy matching (80%+ hit rate)
- **MARC21 Compliant**: Proper field generation
- **Separated Output**: Classification frameworks vs keywords
- **API Ready**: RESTful endpoints with Flask
- **Production Ready**: Error handling, logging, tests

## 📖 Documentation

- Full deployment guide: `backend/DEPLOYMENT_GUIDE.md`
- Technical details: `AGENTS_IMPLEMENTATION_SUMMARY.md`
- Tool documentation: `backend/docs/TOOL_CLASSIFICATION_KEYWORDS.md`

## 🔍 Cache Statistics

```bash
curl http://localhost:5000/api/authority/cache/stats
```

Response shows:
- Cache size
- Hit/miss rates
- Performance metrics
- Source usage statistics

---

**Updated:** November 2024 | **Status:** Production Ready
