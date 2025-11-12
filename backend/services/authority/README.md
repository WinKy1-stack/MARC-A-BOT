# Authority Control Service - Documentation

## Tổng quan

Authority Control Service cung cấp kết nối với các thư viện authority control bên ngoài (MESH, LCC, LCSH, NLM) để chuẩn hóa keywords thành các thuật ngữ chuẩn và tạo MARC21 fields.

## Cấu trúc Dự án

```
backend/
├── services/
│   └── authority/
│       ├── __init__.py
│       ├── config.py                 # Configuration
│       ├── authority_service.py      # Main service
│       ├── marc_generator.py         # MARC field generator
│       ├── tools.py                  # Agent tools interface
│       ├── cache/
│       │   └── cache_manager.py      # Cache management
│       ├── clients/
│       │   ├── mesh_client.py        # MESH API client
│       │   ├── loc_client.py         # LOC Linked Data client
│       │   └── z3950_client.py       # Z39.50 client
│       └── mappers/
│           └── authority_mapper.py   # Keyword mapping
├── api/
│   └── authority_routes.py           # Flask API routes
└── tests/
    └── authority/
        ├── test_authority_mapper.py
        ├── test_marc_generator.py
        └── test_integration.py
```

## Cài đặt

### 1. Cài đặt Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Khởi tạo Database

Database SQLite sẽ được tự động khởi tạo khi service chạy lần đầu tại:
- `backend/services/authority/cache/authority_cache.db`

### 3. Cấu hình (Optional)

Chỉnh sửa `backend/services/authority/config.py` nếu cần:
- API URLs
- Z39.50 connection settings
- Cache thresholds
- Rate limits

## Sử dụng

### A. Sử dụng qua API Endpoints

#### 1. Search Authority Terms

**Endpoint:** `POST /api/authority/search`

**Request:**
```json
{
  "keyword": "machine learning",
  "source": "MESH"
}
```

**Response:**
```json
{
  "success": true,
  "keyword": "machine learning",
  "source": "MESH",
  "results": [
    {
      "term": "Machine Learning",
      "authority_id": "D015996",
      "source": "MESH",
      "category": "medical",
      "score": 100.0,
      "metadata": {
        "tree_numbers": ["L01.224.050.375"],
        "scope_note": "..."
      }
    }
  ],
  "count": 1
}
```

#### 2. Map Keywords to Authorities

**Endpoint:** `POST /api/authority/map`

**Request:**
```json
{
  "keywords": ["diabetes", "hypertension", "insulin"],
  "subject_type": "medical"
}
```

**Response:**
```json
{
  "success": true,
  "input_keywords": ["diabetes", "hypertension", "insulin"],
  "subject_type": "medical",
  "authorities": [
    {
      "term": "Diabetes Mellitus",
      "authority_id": "D003920",
      "source": "MESH",
      "category": "medical",
      "score": 100.0,
      "final_score": 115.0,
      "metadata": {}
    }
  ],
  "marc_fields": [
    {
      "field": "650",
      "ind1": " ",
      "ind2": "2",
      "subfields": [
        {"code": "a", "value": "Diabetes Mellitus"},
        {"code": "2", "value": "mesh"},
        {"code": "0", "value": "(DNLM)D003920"}
      ]
    }
  ],
  "statistics": {
    "total_keywords": 3,
    "total_authorities": 3,
    "total_marc_fields": 3,
    "sources_used": ["MESH"],
    "uncontrolled_terms": 0
  }
}
```

#### 3. Validate Authority Term

**Endpoint:** `POST /api/authority/validate`

**Request:**
```json
{
  "term": "Machine Learning",
  "source": "MESH"
}
```

**Response:**
```json
{
  "success": true,
  "term": "Machine Learning",
  "source": "MESH",
  "is_valid": true
}
```

#### 4. Generate MARC21 650 Fields

**Endpoint:** `POST /api/authority/generate-marc`

**Request:**
```json
{
  "authorities": [
    {
      "term": "Machine Learning",
      "authority_id": "D015996",
      "source": "MESH",
      "category": "medical",
      "score": 100.0,
      "metadata": {}
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "marc_fields": [
    {
      "field": "650",
      "ind1": " ",
      "ind2": "2",
      "subfields": [
        {"code": "a", "value": "Machine Learning"},
        {"code": "2", "value": "mesh"},
        {"code": "0", "value": "(DNLM)D015996"}
      ]
    }
  ],
  "count": 1,
  "formatted_display": [
    "650  2 $a Machine Learning $2 mesh $0 (DNLM)D015996"
  ]
}
```

#### 5. Cache Statistics

**Endpoint:** `GET /api/authority/cache/stats?days=7`

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_cache_entries": 150,
    "total_queries": 200,
    "cache_hits": 160,
    "cache_misses": 40,
    "hit_rate": 80.0,
    "exact_matches": 120,
    "fuzzy_matches": 40,
    "period_days": 7
  }
}
```

### B. Sử dụng qua Python Code

```python
from services.authority.authority_service import AuthorityService

# Initialize service
service = AuthorityService()

# Process keywords
result = service.process_keywords(
    keywords=["diabetes", "hypertension"],
    subject_type="medical"
)

print(f"Authorities: {result['authorities']}")
print(f"MARC Fields: {result['marc_fields']}")
print(f"Statistics: {result['stats']}")

# Search single authority
results = service.search_authority("machine learning", source="MESH")

# Validate term
is_valid = service.validate_term("Diabetes Mellitus", "MESH")

# Get cache stats
stats = service.get_cache_statistics(days=7)
```

### C. Sử dụng cho AI Agent

```python
from services.authority.tools import AuthorityTools

# Initialize tools
tools = AuthorityTools()

# Get tool definitions for agent
tool_defs = tools.get_tool_definitions()

# Use tools
result = tools.search_authority_terms(
    keyword="diabetes",
    source="MESH"
)

result = tools.map_keywords_to_authorities(
    keywords=["diabetes", "hypertension"],
    subject_type="medical"
)
```

## Authority Sources

### 1. MESH (Medical Subject Headings)

- **Sử dụng cho:** Medical/health-related topics
- **API:** https://meshb.nlm.nih.gov/api
- **Indicator trong MARC21:** `ind2 = "2"`
- **Authority ID format:** D015996 (Descriptor UI)

### 2. LCSH (Library of Congress Subject Headings)

- **Sử dụng cho:** General topics
- **API:** http://id.loc.gov/authorities/subjects
- **Indicator trong MARC21:** `ind2 = "0"`
- **Authority ID format:** sh2009007992

### 3. LCC (Library of Congress Classification)

- **Sử dụng cho:** Classification numbers
- **API:** http://id.loc.gov/authorities/classification
- **MARC Field:** 050 (LC Call Number)
- **Format:** QA76.9.A25

### 4. NLM (National Library of Medicine Classification)

- **Sử dụng cho:** Medical classification
- **Protocol:** Z39.50
- **MARC Field:** 060 (NLM Call Number)
- **Format:** WZ 100

## MARC21 Field Structure

### 650 - Subject Added Entry - Topical Term

**Indicators:**
- **First Indicator:** Level of subject
  - `" "` = No information provided
- **Second Indicator:** Thesaurus
  - `"0"` = Library of Congress Subject Headings
  - `"2"` = Medical Subject Headings
  - `"4"` = Source not specified

**Subfields:**
- `$a` - Topical term (Required)
- `$v` - Form subdivision
- `$x` - General subdivision
- `$y` - Chronological subdivision
- `$z` - Geographic subdivision
- `$0` - Authority record control number
- `$1` - Real World Object URI
- `$2` - Source of heading

**Ví dụ:**
```
650  2 $a Machine Learning $2 mesh $0 (DNLM)D015996
650  0 $a Python (Computer program language) $0 (DLC)sh2009007992
```

## Cache Strategy

### Local Cache (SQLite)

1. **Exact Match:** Tìm keyword chính xác trong cache
2. **Fuzzy Match:** Nếu không có exact match, sử dụng fuzzy matching (RapidFuzz)
3. **Online Fallback:** Nếu không tìm thấy trong cache, query API

### Performance Metrics

- **Target Hit Rate:** 80%+
- **Fuzzy Match Threshold:** 80/100
- **Max Suggestions:** 10 per keyword

### Cache Update

```python
# Clear cache
service.clear_cache()

# Cache statistics
stats = service.get_cache_statistics(days=7)
```

## Testing

### Run Unit Tests

```powershell
cd backend
pytest tests/authority/test_authority_mapper.py -v
pytest tests/authority/test_marc_generator.py -v
```

### Run Integration Tests

```powershell
pytest tests/authority/test_integration.py -v
```

### Run All Tests with Coverage

```powershell
pytest tests/authority/ -v --cov=services.authority --cov-report=html
```

## Error Handling

Service xử lý các lỗi sau:

1. **API Timeout:** Retry logic với exponential backoff
2. **No Authority Found:** Mark as "UNCONTROLLED" term
3. **Ambiguous Match:** Return multiple candidates, sorted by score
4. **Cache Error:** Log error, fallback to online query

## Logging

Logs được lưu tại: `backend/logs/authority_service.log`

**Log Levels:**
- `INFO`: Normal operations, cache hits/misses
- `WARNING`: No authority found, fallback operations
- `ERROR`: API failures, parsing errors

## Best Practices

### 1. Subject Type Selection

- **medical:** Prioritize MESH, NLM
- **general:** Prioritize LCSH, LCC
- **science:** Prioritize LCSH, LCC, then MESH

### 2. Keyword Preprocessing

- Lowercase normalization
- Remove special characters
- Handle Vietnamese diacritics

### 3. Batch Processing

Sử dụng batch processing cho nhiều keywords:

```python
batches = [
    ["keyword1", "keyword2"],
    ["keyword3", "keyword4"]
]
results = service.batch_process(batches, subject_type='general')
```

## Troubleshooting

### Issue: No results from MESH API

**Solution:** Check internet connection, API availability
```python
# Test MESH connection
from services.authority.clients.mesh_client import MESHClient
client = MESHClient()
results = client.search_descriptor("diabetes", limit=1)
```

### Issue: Z39.50 connection failed

**Solution:** Z39.50 requires network access and may be blocked by firewall
```python
# Test Z39.50 connection
from services.authority.clients.z3950_client import NLMClient
client = NLMClient()
connected = client.connect()
```

### Issue: Low cache hit rate

**Solution:** 
1. Increase cache entries by processing more keywords
2. Adjust fuzzy match threshold in config
3. Check cache statistics for insights

## API Reference

Xem file `API_REFERENCE.md` để biết chi tiết về các endpoints và parameters.

## Roadmap

- [ ] Support thêm authority sources (DDC, UDC)
- [ ] Improve fuzzy matching algorithm
- [ ] Add support cho Vietnamese subject headings
- [ ] API rate limiting và caching layers
- [ ] Web interface cho manual QA review
- [ ] Export/import cache data

## License

Copyright © 2025 MARC-A-BOT Team
