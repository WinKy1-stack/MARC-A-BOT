# MARC-A-BOT Backend

Backend API cho MARC-A-BOT - Hệ thống AI tự động tạo MARC21 records.

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt

# Run
python app.py
# → http://localhost:5000
```

## 📁 Structure

```
backend/
├── app.py              # Entry point
├── api/                # REST endpoints
├── services/           # Business logic
│   └── authority/     # Authority Control Service
├── tests/             # Tests
└── scripts/           # Utilities
```

## 🎓 Authority Control Service

**Chức năng**: Chuẩn hóa keywords → MARC21 fields

- **Sources**: MESH, LCSH, LCC, NLM
- **Cache**: SQLite + fuzzy matching (80% threshold)
- **Output**: MARC 650, 050, 060 fields

## 📡 API Endpoints

Base: `http://localhost:5000/api/authority`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/search` | POST | Search authority terms |
| `/map` | POST | Map keywords |
| `/generate-marc` | POST | Generate MARC fields |
| `/validate` | POST | Validate MARC field |
| `/cache/stats` | GET | Cache statistics |
| `/tools` | GET | List agent tools |

## 🧪 Testing

```bash
# Quick test
python test_authority_quick.py

# Full suite
python scripts/run_full_tests.py

# API tests (server must be running)
python scripts/test_endpoints.py
```

## ⚙️ Configuration

Edit `services/authority/config.py`:

```python
MESH_API_URL = "https://meshb.nlm.nih.gov/api"
FUZZY_MATCH_THRESHOLD = 80
CACHE_TTL_DAYS = 30
```

## 📚 Documentation

- `docs/ARCHITECTURE.md` - System architecture
- `CONTRIBUTING.md` - Development guide

## 🔧 Troubleshooting

**PyZ3950 warning**: Optional dependency, system works without it.

**Import errors**: Run from `backend/` directory with activated venv.

## 📝 License

MIT
