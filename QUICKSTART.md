# Quick Start Guide - Authority Control Service

## Cài đặt nhanh

### 1. Install dependencies

```powershell
cd c:\Workspace\Bien_muc\MARC-A-BOT\backend
pip install -r requirements.txt
```

### 2. Chạy Flask server

```powershell
python app.py
```

Server sẽ chạy tại: http://localhost:5000

### 3. Test API

**Kiểm tra health:**
```powershell
curl http://localhost:5000/api/authority/health
```

**Search authority term:**
```powershell
curl -X POST http://localhost:5000/api/authority/search `
  -H "Content-Type: application/json" `
  -d '{\"keyword\": \"diabetes\", \"source\": \"MESH\"}'
```

**Map keywords:**
```powershell
curl -X POST http://localhost:5000/api/authority/map `
  -H "Content-Type: application/json" `
  -d '{\"keywords\": [\"diabetes\", \"hypertension\"], \"subject_type\": \"medical\"}'
```

## Sử dụng trong Python

### Basic Usage

```python
from services.authority.authority_service import AuthorityService

# Initialize
service = AuthorityService()

# Process keywords
result = service.process_keywords(
    keywords=["diabetes", "hypertension"],
    subject_type="medical"
)

# Print results
for auth in result['authorities']:
    print(f"{auth['term']} ({auth['source']}) - {auth['authority_id']}")

for field in result['marc_fields']:
    print(f"{field['field']} {field['ind1']}{field['ind2']} {field['subfields']}")
```

### Run Examples

```powershell
cd c:\Workspace\Bien_muc\MARC-A-BOT\backend
python examples/authority_examples.py
```

## Sử dụng cho AI Agent

### 1. Get Tool Definitions

```python
from services.authority.tools import AuthorityTools

tools = AuthorityTools()
tool_defs = tools.get_tool_definitions()

for tool in tool_defs:
    print(f"{tool['name']}: {tool['description']}")
```

### 2. Use Tools

```python
# Search
result = tools.search_authority_terms("diabetes", "MESH")

# Map keywords
result = tools.map_keywords_to_authorities(
    keywords=["diabetes", "hypertension"],
    subject_type="medical"
)

# Validate
result = tools.validate_authority_term("Machine Learning", "MESH")

# Generate MARC fields
result = tools.generate_marc21_650_fields(authorities)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/authority/search` | POST | Search authority terms |
| `/api/authority/map` | POST | Map keywords to authorities |
| `/api/authority/validate` | POST | Validate authority term |
| `/api/authority/generate-marc` | POST | Generate MARC21 fields |
| `/api/authority/cache/stats` | GET | Cache statistics |
| `/api/authority/tools` | GET | Get tool definitions |
| `/api/authority/health` | GET | Health check |

## Authority Sources

| Source | Description | Best For |
|--------|-------------|----------|
| MESH | Medical Subject Headings | Medical/health topics |
| LCSH | LC Subject Headings | General topics |
| LCC | LC Classification | Classification numbers |
| NLM | NLM Classification | Medical classification |

## MARC21 Field Indicators

### 650 - Subject Added Entry

| Indicator 2 | Source |
|-------------|--------|
| 0 | Library of Congress (LCSH) |
| 2 | Medical Subject Headings (MESH) |
| 4 | Source not specified |

## Common Tasks

### Task 1: Process Medical Book Keywords

```python
service = AuthorityService()
result = service.process_keywords(
    keywords=["diabetes mellitus", "insulin", "blood glucose"],
    subject_type="medical"
)
```

### Task 2: Generate MARC Record Fragment

```python
from services.authority.marc_generator import MARCFieldGenerator

# Subject headings (650)
marc_650 = MARCFieldGenerator.create_marc21_650_field(authorities)

# Classification (050)
marc_050 = MARCFieldGenerator.create_marc21_classification_field(
    "QA76.9.A25", 
    "LCC"
)
```

### Task 3: Validate Subject Heading

```python
service = AuthorityService()
is_valid = service.validate_term("Machine Learning", "MESH")
```

### Task 4: Check Cache Performance

```python
service = AuthorityService()
stats = service.get_cache_statistics(days=7)
print(f"Hit Rate: {stats['hit_rate']}%")
```

## Troubleshooting

### Problem: No results from MESH API

**Check internet connection:**
```python
import requests
response = requests.get("https://meshb.nlm.nih.gov/api")
print(response.status_code)
```

### Problem: Import errors

**Install dependencies:**
```powershell
pip install -r requirements.txt
```

### Problem: Database locked

**Clear cache:**
```python
service = AuthorityService()
service.clear_cache()
```

## Next Steps

1. Read full documentation: `backend/services/authority/README.md`
2. Run examples: `python examples/authority_examples.py`
3. Run tests: `pytest tests/authority/ -v`
4. Integrate with your agent workflow

## Support

- Documentation: `backend/services/authority/README.md`
- Examples: `backend/examples/authority_examples.py`
- Tests: `backend/tests/authority/`
