# Architecture

## 🏗️ Overview

3-tier layered architecture:

```
API Layer (Flask routes)
    ↓
Business Logic (Services)
    ↓
Data Layer (Clients, Cache)
```

## 📦 Components

### 1. API Layer (`api/`)
- REST endpoints
- Request validation
- JSON serialization

### 2. Business Logic (`services/authority/`)
- `authority_service.py` - Main orchestrator
- `marc_generator.py` - MARC field generation
- `authority_mapper.py` - Keyword mapping
- `tools.py` - AI agent tools

### 3. Data Layer
**Cache** (`cache/`):
- SQLite database
- Exact + fuzzy matching

**Clients** (`clients/`):
- `mesh_client.py` - MESH API
- `loc_client.py` - LOC Linked Data
- `z3950_client.py` - Z39.50 (optional)

## 🔄 Data Flow

```
Keyword → Cache Check → External API → Mapper → MARC Generator → Output
```

### Authority Mapping Priority

**Medical**: MESH → NLM → LCSH → LCC  
**General**: LCSH → LCC → MESH → NLM

## 💾 Database Schema

```sql
CREATE TABLE authority_terms (
    id INTEGER PRIMARY KEY,
    keyword TEXT NOT NULL,
    authority_id TEXT,
    normalized_term TEXT,
    source TEXT,              -- MESH, LCSH, LCC, NLM
    category TEXT,            -- medical, general
    score REAL,               -- 0-100
    created_at TIMESTAMP
);

CREATE INDEX idx_keyword ON authority_terms(keyword);
```

## 🌐 External APIs

| Service | URL | Purpose |
|---------|-----|---------|
| MESH | `meshb.nlm.nih.gov/api` | Medical terms |
| LOC | `id.loc.gov/authorities` | Subject/Classification |
| Z39.50 | `z3950.loc.gov:7090` | MARC records (optional) |

## ⚠️ Error Handling

```python
AppError
├── ValidationError (400)
├── NotFoundError (404)
├── ExternalAPIError (502)
│   ├── MESHAPIError
│   └── LOCAPIError
└── CacheError (500)
```

## 🚀 Performance

**Cache Strategy**:
- Target hit rate: 80%+
- Fuzzy matching threshold: 80
- TTL: 30 days

**Optimization**:
- SQLite indexes on keywords
- HTTP session reuse
- Exponential backoff on retry

## 📊 MARC Fields

| Field | Description | Source |
|-------|-------------|--------|
| 650 | Subject heading | MESH, LCSH |
| 050 | LCC number | LCC |
| 060 | NLM number | NLM |

**Example**:
```
650  2 $a Machine Learning $2 mesh $0 (DNLM)D015996
050    $a QA76 $b .C65
```

## 🔐 Security

- Input sanitization
- Parameterized SQL queries
- Rate limiting (100 req/hour)
- No sensitive data in logs

---

**Last Updated**: November 12, 2025
