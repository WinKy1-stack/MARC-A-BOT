# Testing Guide

Hướng dẫn testing cho MARC-A-BOT Backend.

## Cài đặt Testing Tools

```bash
pip install pytest pytest-cov pytest-mock
```

---

## Chạy Tests

### Tất cả tests

```bash
pytest app/test/
```

### Unit tests

```bash
pytest app/test/test_ocr_service.py -v
```

### Integration tests

```bash
pytest app/test/test_ocr_routes.py -v
```

### Performance tests

```bash
pytest app/test/test_performance.py -v
```

### Với coverage

```bash
pytest app/test/ --cov=app --cov-report=html
```

Xem report: `htmlcov/index.html`

---

## Test Structure

```
app/test/
├── __init__.py
├── test_ocr_service.py      # Unit tests cho OCR service
├── test_ocr_routes.py        # Integration tests cho API
└── test_performance.py       # Performance & stress tests
```

---

## Writing Tests

### Unit Test Example

```python
import pytest
from app.services.ocr_service import OCRService

def test_ocr_service_initialization():
    """Test khởi tạo OCR service"""
    service = OCRService()
    assert service is not None
    
def test_process_image_success():
    """Test xử lý image thành công"""
    service = OCRService()
    result = service.process_image('test_image.jpg', 'test-123')
    
    assert result['status'] == 'success'
    assert 'extracted_text' in result
    assert len(result['extracted_text']) > 0
```

### API Test Example

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_ocr_endpoint(client):
    """Test OCR endpoint"""
    with open('test_image.jpg', 'rb') as f:
        response = client.post(
            '/api/ocr',
            data={'file': f}
        )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
```

---

## Running Specific Tests

```bash
# Test một function cụ thể
pytest app/test/test_ocr_service.py::test_process_image_success

# Test với keyword
pytest -k "batch"

# Test với markers
pytest -m slow
```

---

## Best Practices

1. **Mỗi test độc lập**
2. **Use fixtures cho setup/teardown**
3. **Mock external dependencies**
4. **Test cả success và error cases**
5. **Keep tests fast (< 1s per test)**

---

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest app/test/ --cov=app
```
