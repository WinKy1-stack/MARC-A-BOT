# Development Guide

Hướng dẫn phát triển MARC-A-BOT Backend.

## Development Setup

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/MARC-A-BOT.git
cd MARC-A-BOT/backend
```

### 2. Setup Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 3. Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py           # App factory
│   ├── config.py             # Configuration
│   ├── routes/               # API endpoints
│   │   └── ocr_routes.py
│   ├── services/             # Business logic
│   │   ├── ocr_service.py
│   │   ├── base_ocr_service.py
│   │   ├── batch_processor.py
│   │   ├── image_processor.py
│   │   ├── pdf_processor.py
│   │   └── ocr_utils.py
│   ├── ultis/                # Utilities
│   │   ├── request_queue.py
│   │   ├── logger_setup.py
│   │   ├── formatters.py
│   │   ├── metrics_logger.py
│   │   ├── decorators.py
│   │   ├── gpu_utils.py
│   │   └── validators.py
│   └── test/                 # Tests
│       ├── test_ocr_service.py
│       ├── test_ocr_routes.py
│       └── test_performance.py
├── docs/                     # Documentation
├── logs/                     # Log files
├── uploads/                  # Temp uploads
├── outputs/                  # Processed outputs
├── app.py                    # Entry point
├── requirements.txt          # Dependencies
└── README.md
```

---

## Coding Standards

### Python Style

- **PEP 8** compliance
- **Type hints** cho functions
- **Docstrings** bằng tiếng Việt
- **Maximum line length:** 100 characters

### Naming Conventions

```python
# Classes: PascalCase
class OCRService:
    pass

# Functions/Methods: snake_case
def process_image():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024

# Private: prefix with _
def _internal_method():
    pass
```

### Docstring Format

```python
def process_image(file_path: str, file_id: str) -> Dict[str, Any]:
    """
    Xử lý một file ảnh để OCR
    
    Args:
        file_path: Đường dẫn đến file ảnh
        file_id: ID định danh của file
        
    Returns:
        Dictionary chứa kết quả OCR
        
    Raises:
        ValueError: Nếu file không tồn tại
        RuntimeError: Nếu OCR thất bại
    """
    pass
```

---

## Adding New Features

### 1. Create Feature Branch

```bash
git checkout -b feature/new-feature-name
```

### 2. Write Code

Follow structure:
- Services trong `app/services/`
- Routes trong `app/routes/`
- Utilities trong `app/ultis/`

### 3. Write Tests

```python
# app/test/test_new_feature.py
def test_new_feature():
    """Test new feature"""
    assert True
```

### 4. Update Documentation

- Update docstrings
- Update `docs/` nếu cần
- Update `README.md` nếu có API mới

### 5. Commit & Push

```bash
git add .
git commit -m "feat: Add new feature description"
git push origin feature/new-feature-name
```

### 6. Create Pull Request

- Mô tả changes
- Reference issues
- Add screenshots nếu có UI changes

---

## Debugging

### Enable Debug Mode

```python
# .env
DEBUG=True
LOG_LEVEL=DEBUG
```

### VS Code Debug Configuration

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "app.py",
        "FLASK_ENV": "development"
      },
      "args": ["run", "--no-debugger", "--no-reload"],
      "jinja": true
    }
  ]
}
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## Testing Guidelines

### Run Tests Before Commit

```bash
# All tests
pytest app/test/

# With coverage
pytest app/test/ --cov=app

# Fast tests only
pytest -m "not slow"
```

### Test Coverage Target

- **Minimum:** 80%
- **Target:** 90%+

### Writing Good Tests

1. **Test one thing per test**
2. **Use descriptive names**
3. **Setup/Teardown with fixtures**
4. **Mock external dependencies**
5. **Test edge cases**

---

## Common Tasks

### Add New API Endpoint

```python
# app/routes/ocr_routes.py
@ocr_bp.route('/new-endpoint', methods=['POST'])
def new_endpoint():
    """Docstring mô tả endpoint"""
    try:
        # Logic here
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'status': 'error'}), 500
```

### Add New Service Method

```python
# app/services/ocr_service.py
class OCRService:
    def new_method(self, param: str) -> Dict:
        """
        Mô tả method mới
        
        Args:
            param: Tham số
            
        Returns:
            Kết quả
        """
        # Implementation
        return result
```

### Add New Configuration

```python
# app/config.py
class Config:
    NEW_CONFIG = os.getenv('NEW_CONFIG', 'default_value')
```

```env
# .env
NEW_CONFIG=custom_value
```

---

## Code Review Checklist

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] Docstrings có đầy đủ
- [ ] No secrets trong code
- [ ] Error handling đầy đủ
- [ ] Logging appropriate
- [ ] Documentation updated

---

## Release Process

### 1. Update Version

```python
# app/__init__.py
__version__ = '1.1.0'
```

### 2. Update CHANGELOG

```markdown
## [1.1.0] - 2024-11-13
### Added
- New feature X
- New endpoint Y

### Fixed
- Bug Z
```

### 3. Tag Release

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

---

## Troubleshooting Development

### Import Errors

```bash
# Ensure in virtual environment
which python  # Should point to .venv

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# Linux
lsof -i :5001
kill -9 <PID>
```

### Tests Failing

```bash
# Clean pytest cache
pytest --cache-clear

# Reinstall test dependencies
pip install -r requirements-dev.txt
```

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

---

## Getting Help

1. Check [docs/](../docs/)
2. Search [GitHub Issues](https://github.com/LockMan04/MARC-A-BOT/issues)
3. Create new issue với template
4. Ask in Discussions

---

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Write tests
5. Update documentation
6. Submit Pull Request

Xem [CONTRIBUTING.md](../CONTRIBUTING.md) để biết chi tiết.
