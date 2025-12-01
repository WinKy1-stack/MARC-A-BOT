# Hướng Dẫn Triển Khai Authority Control Service

## 📋 Tổng Quan

Authority Control Service đã được xây dựng hoàn chỉnh với các tính năng:
- ✅ Kết nối MESH, LCSH, LCC, NLM
- ✅ Caching thông minh với SQLite + Fuzzy Matching
- ✅ 7 API Endpoints cho Agent sử dụng
- ✅ 4 Tools cho AI Agent
- ✅ MARC21 Field Generator (650, 050, 060)
- ✅ 40+ Tests

## 🚀 Bước 1: Cài Đặt và Khởi Động

### 1.1. Cài đặt dependencies

```powershell
# Kích hoạt virtual environment
.\venv\Scripts\Activate.ps1

# Cài đặt packages
pip install -r requirements.txt
```

### 1.2. Khởi động Flask Server

```powershell
# Từ thư mục backend
cd backend
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

## 🔧 Bước 2: Test Các API Endpoints

### 2.1. Health Check

```powershell
curl http://localhost:5000/api/authority/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Authority Control Service",
  "version": "1.0.0"
}
```

### 2.2. Search Authority Terms

```powershell
curl -X POST http://localhost:5000/api/authority/search `
  -H "Content-Type: application/json" `
  -d '{\"keyword\": \"machine learning\", \"source\": \"ALL\"}'
```

### 2.3. Map Keywords to Authorities

```powershell
curl -X POST http://localhost:5000/api/authority/map `
  -H "Content-Type: application/json" `
  -d '{\"keywords\": [\"diabetes\", \"insulin\", \"glucose\"], \"subject_type\": \"medical\"}'
```

Response sẽ bao gồm:
- `mapping_results`: Kết quả mapping cho từng keyword
- `marc21_fields`: MARC21 650 fields đã generate
- `statistics`: Thống kê (cache hits, API calls)

### 2.4. Generate MARC21 Fields

```powershell
curl -X POST http://localhost:5000/api/authority/generate-marc `
  -H "Content-Type: application/json" `
  -d '{\"keywords\": [\"artificial intelligence\", \"neural networks\"]}'
```

## 🤖 Bước 3: Sử Dụng Tools Cho AI Agent

### 3.1. Lấy Tool Definitions

```powershell
curl http://localhost:5000/api/authority/tools
```

Response:
```json
{
  "tools": [
    {
      "name": "search_authority_terms",
      "description": "Tìm kiếm authority terms (MESH, LCSH, LCC, NLM) cho một keyword",
      "parameters": {
        "type": "object",
        "properties": {
          "keyword": {
            "type": "string",
            "description": "Từ khóa cần tìm authority terms"
          },
          "source": {
            "type": "string",
            "enum": ["MESH", "LCSH", "LCC", "NLM", "ALL"]
          }
        },
        "required": ["keyword"]
      }
    },
    // ... 3 tools khác
  ]
}
```

### 3.2. Tích Hợp Với AI Agent (Python)

```python
import requests

# Lấy tool definitions
response = requests.get('http://localhost:5000/api/authority/tools')
tools = response.json()['tools']

# Sử dụng tool trong agent
def agent_process_keywords(keywords):
    """Agent function để xử lý keywords"""
    # Map keywords sang authorities
    result = requests.post(
        'http://localhost:5000/api/authority/map',
        json={
            'keywords': keywords,
            'subject_type': 'medical'
        }
    ).json()
    
    # Lấy MARC21 fields
    marc_fields = result['marc21_fields']
    
    return {
        'authorities': result['mapping_results'],
        'marc21': marc_fields
    }

# Example usage
keywords = ["diabetes", "hypertension", "cardiovascular disease"]
output = agent_process_keywords(keywords)
print(output)
```

## 📊 Bước 4: Monitoring và Performance

### 4.1. Kiểm Tra Cache Statistics

```powershell
curl http://localhost:5000/api/authority/cache/stats
```

Response:
```json
{
  "cache_hits": 125,
  "cache_misses": 23,
  "hit_rate": 84.5,
  "total_entries": 148,
  "cache_size_mb": 2.3
}
```

### 4.2. Kiểm Tra Performance Benchmarks

```powershell
# Chạy benchmark tests
pytest backend/tests/authority/test_integration.py -v -s
```

Expected performance:
- ✅ Cache hit: < 50ms
- ✅ API call with cache: < 500ms
- ✅ Cache hit rate: > 80%
- ✅ Batch processing: < 2s cho 10 keywords

## 🎯 Bước 5: Workflow Thực Tế Cho Agent 4

### Workflow: OCR Text → Keywords → Authorities → MARC21

```python
# Agent 4: Keywords Extractor
def agent_4_extract_keywords(ocr_text):
    """Extract keywords from OCR text"""
    # ... AI logic to extract keywords
    keywords = ["machine learning", "neural networks", "deep learning"]
    return keywords

# Authority Service Integration
def standardize_keywords(keywords):
    """Standardize keywords thành authority terms"""
    response = requests.post(
        'http://localhost:5000/api/authority/map',
        json={
            'keywords': keywords,
            'subject_type': 'science'
        }
    ).json()
    
    return {
        'original_keywords': keywords,
        'authority_terms': [
            result['term'] 
            for result in response['mapping_results'] 
            if result['is_valid']
        ],
        'marc21_650_fields': response['marc21_fields'],
        'confidence_scores': [
            result['confidence'] 
            for result in response['mapping_results']
        ]
    }

# Complete Pipeline
def complete_pipeline(ocr_text):
    """Complete pipeline từ OCR đến MARC21"""
    # Step 1: Extract keywords
    keywords = agent_4_extract_keywords(ocr_text)
    
    # Step 2: Standardize với authority control
    result = standardize_keywords(keywords)
    
    # Step 3: Generate final MARC21
    marc_record = generate_marc21_record(result)
    
    return marc_record
```

## 📝 Bước 6: Examples Thực Tế

### Example 1: Medical Document

```python
keywords = ["diabetes mellitus", "insulin resistance", "glucose metabolism"]

response = requests.post(
    'http://localhost:5000/api/authority/map',
    json={
        'keywords': keywords,
        'subject_type': 'medical'
    }
)

result = response.json()
# Output:
# - MESH terms: D003920 (Diabetes Mellitus), D007333 (Insulin Resistance)
# - MARC 650 _0 $a Diabetes Mellitus
# - MARC 650 _0 $a Insulin Resistance
```

### Example 2: Computer Science Document

```python
keywords = ["artificial intelligence", "machine learning", "computer vision"]

response = requests.post(
    'http://localhost:5000/api/authority/generate-marc',
    json={'keywords': keywords}
)

marc_fields = response.json()['marc21_fields']
# Output:
# - 650 _0 $a Artificial intelligence
# - 650 _0 $a Machine learning
# - 650 _0 $a Computer vision
```

### Example 3: Validate Authority Term

```powershell
curl -X POST http://localhost:5000/api/authority/validate `
  -H "Content-Type: application/json" `
  -d '{\"term\": \"Diabetes Mellitus\", \"source\": \"MESH\"}'
```

Response:
```json
{
  "is_valid": true,
  "term": "Diabetes Mellitus",
  "source": "MESH",
  "mesh_id": "D003920",
  "confidence": 1.0
}
```

## 🧪 Bước 7: Testing và Validation

### 7.1. Run All Tests

```powershell
# Chạy tất cả tests
pytest backend/tests/authority/ -v

# Chạy specific test
pytest backend/tests/authority/test_integration.py::test_complete_workflow -v
```

### 7.2. Quick Test Script

```powershell
# Chạy quick test
python backend/test_authority_quick.py
```

## 🔍 Bước 8: Troubleshooting

### Issue 1: Z39.50 Connection Error

Nếu không cần Z39.50 (NLM), comment out trong `requirements.txt`:
```
# PyZ3950==3.0.1
```

### Issue 2: Cache Not Working

Kiểm tra SQLite database:
```python
import sqlite3
conn = sqlite3.connect('backend/cache/authority_cache.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM authority_cache")
print(f"Cache entries: {cursor.fetchone()[0]}")
```

### Issue 3: API Timeout

Tăng timeout trong `config.py`:
```python
API_TIMEOUT = 10  # seconds
```

## 📚 Tài Liệu Bổ Sung

- **API Reference**: `backend/docs/API_REFERENCE.md`
- **Architecture**: `backend/docs/ARCHITECTURE.md`
- **Examples**: `backend/examples/`
- **Tests**: `backend/tests/authority/`

## 🎉 Kết Luận

Hệ thống đã sẵn sàng để:
1. ✅ Agent 4 gọi API để standardize keywords
2. ✅ Generate MARC21 650 fields tự động
3. ✅ Cache thông minh với 80%+ hit rate
4. ✅ Support 4 authority sources (MESH, LCSH, LCC, NLM)
5. ✅ Tools definitions cho AI Agent integration

**Next Steps:**
1. Khởi động service: `python backend/app.py`
2. Test với curl commands ở trên
3. Integrate vào Agent 4 pipeline
4. Monitor cache statistics
