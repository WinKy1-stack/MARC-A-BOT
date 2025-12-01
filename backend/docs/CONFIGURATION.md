# Configuration Guide

Hướng dẫn chi tiết về các tùy chọn cấu hình cho MARC-A-BOT Backend.

## Tổng quan

Có 2 cách cấu hình:

1. **File `.env`** - Environment variables (khuyến nghị cho production)
2. **File `app/config.py`** - Python config class

---

## Environment Variables (.env)

### Server Configuration

```env
# Flask server
HOST=0.0.0.0          # 0.0.0.0 cho production, localhost cho dev
PORT=5001             # Port number
DEBUG=True            # True cho development, False cho production
FLASK_ENV=development # development hoặc production
```

### OCR Configuration

```env
# GPU Settings
USE_GPU=True                    # True/False - Sử dụng GPU hay không

# Model Settings
OCR_MODEL=paddleocr-vl         # Model name
OCR_LANG=en,vi                 # Languages (comma-separated)
OCR_DET_ALGORITHM=DB           # Detection algorithm
OCR_REC_ALGORITHM=CRNN         # Recognition algorithm

# Processing Limits
MAX_FILE_SIZE=10485760         # 10MB in bytes
MAX_BATCH_SIZE=10              # Max files per batch request
BATCH_WORKERS=3                # ThreadPoolExecutor workers
```

### Queue Configuration

```env
# Request Queue
ENABLE_REQUEST_QUEUE=True      # Bật/tắt queue system
MAX_CONCURRENT_REQUESTS=5      # Số request xử lý đồng thời
QUEUE_MAX_SIZE=50              # Kích thước queue tối đa
QUEUE_TIMEOUT=60               # Timeout trong queue (seconds)
```

### Model Auto-Unload

```env
# Auto unload model khi idle
ENABLE_MODEL_AUTO_UNLOAD=True  # Bật/tắt auto-unload
MODEL_IDLE_TIMEOUT=600         # Thời gian idle trước khi unload (seconds)
```

### Logging

```env
# Logging Configuration
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log          # Log file path
LOG_MAX_BYTES=10485760         # 10MB - Max log file size
LOG_BACKUP_COUNT=5             # Số file backup
LOG_FORMAT=json                # json hoặc text
```

### Storage Paths

```env
# Directories
UPLOAD_FOLDER=uploads          # Temporary uploads
OUTPUT_FOLDER=outputs          # Processed outputs
LOG_FOLDER=logs                # Log files
```

---

## Config Class (app/config.py)

### Basic Structure

```python
import os
from pathlib import Path

class Config:
    """Cấu hình toàn hệ thống"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    OUTPUT_FOLDER = BASE_DIR / 'outputs'
    LOG_FOLDER = BASE_DIR / 'logs'
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # OCR Settings
    USE_GPU = os.getenv('USE_GPU', 'True') == 'True'
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 10))
    
    # Queue
    ENABLE_REQUEST_QUEUE = True
    MAX_CONCURRENT_REQUESTS = 5
    QUEUE_MAX_SIZE = 50
    QUEUE_TIMEOUT = 60
    
    # Auto-unload
    ENABLE_MODEL_AUTO_UNLOAD = True
    MODEL_IDLE_TIMEOUT = 600
```

---

## Detailed Configuration Options

### 1. GPU Configuration

```python
# Sử dụng GPU hay không
USE_GPU = True

# GPU device ID (nếu có nhiều GPU)
GPU_DEVICE_ID = 0

# GPU memory fraction (0.0 - 1.0)
GPU_MEMORY_FRACTION = 0.8  # Dùng 80% VRAM
```

**Khi nào dùng GPU:**
- ✅ Có NVIDIA GPU với CUDA
- ✅ VRAM >= 4GB
- ✅ Xử lý nhiều file/batch
- ✅ Cần tốc độ cao

**Khi nào dùng CPU:**
- ❌ Không có GPU
- ❌ Testing/Development
- ❌ Xử lý ít file, không cần tốc độ cao

### 2. File Processing Limits

```python
# Kích thước file tối đa (bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Số file tối đa mỗi batch
MAX_BATCH_SIZE = 10

# Định dạng file được phép
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

# Timeout cho mỗi file (seconds)
PROCESSING_TIMEOUT = 30
```

**Recommendations:**
- Ảnh nhỏ (< 2MB): `MAX_BATCH_SIZE = 10`
- Ảnh lớn (> 5MB): `MAX_BATCH_SIZE = 5`
- PDF nhiều trang: `MAX_BATCH_SIZE = 3`

### 3. Queue Management

```python
# Bật queue system
ENABLE_REQUEST_QUEUE = True

# Số request xử lý đồng thời
MAX_CONCURRENT_REQUESTS = 5

# Kích thước queue
QUEUE_MAX_SIZE = 50

# Timeout request trong queue
QUEUE_TIMEOUT = 60  # seconds
```

**Tuning Guide:**

| Server Capacity | MAX_CONCURRENT | QUEUE_MAX_SIZE |
|-----------------|----------------|----------------|
| Small (4 cores, 8GB RAM) | 2-3 | 20 |
| Medium (8 cores, 16GB RAM) | 5-7 | 50 |
| Large (16+ cores, 32GB+ RAM) | 10-15 | 100 |

**With GPU:**
- VRAM 4GB: `MAX_CONCURRENT = 2-3`
- VRAM 8GB: `MAX_CONCURRENT = 5-7`
- VRAM 16GB+: `MAX_CONCURRENT = 10+`

### 4. Model Auto-Unload

```python
# Bật auto-unload
ENABLE_MODEL_AUTO_UNLOAD = True

# Thời gian idle trước khi unload (seconds)
MODEL_IDLE_TIMEOUT = 600  # 10 phút

# Force unload sau khi xử lý N requests
AUTO_UNLOAD_AFTER_REQUESTS = 100  # Optional
```

**Scenarios:**

| Use Case | ENABLE | TIMEOUT |
|----------|--------|---------|
| Continuous high traffic | False | - |
| Sporadic requests | True | 300-600 |
| Limited VRAM | True | 60-300 |
| Development/Testing | True | 60 |

### 5. Batch Processing

```python
# Số worker threads cho batch
BATCH_WORKERS = 3

# Max concurrent batches
MAX_CONCURRENT_BATCHES = 2

# Batch timeout
BATCH_TIMEOUT = 120  # seconds
```

**Worker Tuning:**

| CPU Cores | BATCH_WORKERS | MAX_CONCURRENT_BATCHES |
|-----------|---------------|------------------------|
| 4 cores | 2-3 | 1 |
| 8 cores | 3-5 | 2 |
| 16+ cores | 5-8 | 3-4 |

### 6. Logging Configuration

```python
# Log level
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log file
LOG_FILE = 'logs/app.log'

# Rotating file handler
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Log format
LOG_FORMAT = 'json'  # 'json' hoặc 'text'

# Console logging
LOG_TO_CONSOLE = True

# Metrics logging
ENABLE_METRICS_LOGGING = True
METRICS_RETENTION_HOURS = 168  # 7 days
```

**Log Levels:**
- `DEBUG`: Mọi thông tin chi tiết (development)
- `INFO`: Thông tin quan trọng (production default)
- `WARNING`: Warnings và errors
- `ERROR`: Chỉ errors
- `CRITICAL`: Chỉ critical errors

### 7. OCR Engine Settings

```python
# PaddleOCR-VL settings
OCR_CONFIG = {
    'use_angle_cls': True,      # Detect text rotation
    'lang': 'en',               # Language
    'det_algorithm': 'DB',      # Detection algorithm
    'rec_algorithm': 'CRNN',    # Recognition algorithm
    'use_space_char': True,     # Recognize spaces
    'drop_score': 0.5,          # Min confidence score
    'det_limit_side_len': 960,  # Max detection side length
    'rec_batch_num': 6,         # Batch size for recognition
}

# Text processing
TEXT_CLEANING = {
    'remove_special_chars': True,
    'normalize_whitespace': True,
    'fix_encoding': True,
}
```

### 8. Performance Tuning

```python
# Threading
MAX_THREADS = 8

# Caching
ENABLE_RESULT_CACHE = True
CACHE_EXPIRY_SECONDS = 3600  # 1 hour

# Prefetch
ENABLE_PREFETCH = False
PREFETCH_SIZE = 2
```

---

## Configuration Examples

### Development Configuration

```python
# .env.development
DEBUG=True
LOG_LEVEL=DEBUG
USE_GPU=False
MAX_CONCURRENT_REQUESTS=2
ENABLE_MODEL_AUTO_UNLOAD=True
MODEL_IDLE_TIMEOUT=60
LOG_TO_CONSOLE=True
```

### Production Configuration

```python
# .env.production
DEBUG=False
LOG_LEVEL=INFO
USE_GPU=True
MAX_CONCURRENT_REQUESTS=10
ENABLE_REQUEST_QUEUE=True
QUEUE_MAX_SIZE=100
ENABLE_MODEL_AUTO_UNLOAD=False
LOG_TO_CONSOLE=False
LOG_FORMAT=json
```

### High-Traffic Configuration

```python
# .env.high-traffic
USE_GPU=True
GPU_MEMORY_FRACTION=0.9
MAX_CONCURRENT_REQUESTS=15
QUEUE_MAX_SIZE=200
BATCH_WORKERS=8
ENABLE_MODEL_AUTO_UNLOAD=False
ENABLE_RESULT_CACHE=True
```

### Low-Resource Configuration

```python
# .env.low-resource
USE_GPU=False
MAX_CONCURRENT_REQUESTS=2
QUEUE_MAX_SIZE=20
BATCH_WORKERS=2
ENABLE_MODEL_AUTO_UNLOAD=True
MODEL_IDLE_TIMEOUT=180
MAX_BATCH_SIZE=3
```

---

## Environment-Specific Loading

```python
# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment-specific .env
env = os.getenv('FLASK_ENV', 'development')
env_file = Path(__file__).parent.parent / f'.env.{env}'

if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # Load .env default

class Config:
    # ... config như trên
    pass
```

**Usage:**
```bash
# Development
export FLASK_ENV=development
python app.py

# Production
export FLASK_ENV=production
python app.py
```

---

## Validating Configuration

```python
# app/config.py
class Config:
    # ... config
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        # Check GPU
        if cls.USE_GPU:
            import paddle
            if paddle.device.cuda.device_count() == 0:
                errors.append("USE_GPU=True but no GPU detected")
        
        # Check paths
        for path in [cls.UPLOAD_FOLDER, cls.OUTPUT_FOLDER, cls.LOG_FOLDER]:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
        
        # Check limits
        if cls.MAX_BATCH_SIZE > 20:
            errors.append("MAX_BATCH_SIZE too large (max 20)")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

# Validate on startup
Config.validate()
```

---

## Dynamic Configuration

Thay đổi config runtime (không khuyến nghị cho production):

```python
from app.config import Config

# Change config
Config.MAX_CONCURRENT_REQUESTS = 10
Config.MODEL_IDLE_TIMEOUT = 300

# Reload service
from app.services.ocr_service import OCRService
OCRService._instance = None  # Reset singleton
```

---

## Configuration Best Practices

1. **Sử dụng .env cho sensitive data**
   - API keys, secrets
   - Database credentials
   - Không commit .env vào git

2. **Có config riêng cho từng environment**
   - `.env.development`
   - `.env.testing`
   - `.env.production`

3. **Validate config on startup**
   - Check GPU availability
   - Check paths exist
   - Check limits reasonable

4. **Document mọi config option**
   - Giải thích ý nghĩa
   - Giá trị mặc định
   - Giá trị khuyến nghị

5. **Monitor config impact**
   - Log config values on startup
   - Track performance metrics
   - A/B test config changes

---

## Troubleshooting

### Config không load

```bash
# Check .env file exists
ls -la .env

# Check environment variables
printenv | grep FLASK

# Load explicitly
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('USE_GPU'))"
```

### GPU config issues

```python
# Test GPU
import paddle
print(f"GPU available: {paddle.device.cuda.device_count() > 0}")
print(f"GPU devices: {paddle.device.cuda.device_count()}")

# If GPU not working
Config.USE_GPU = False
```

---

## Next Steps

- [Performance Tuning](PERFORMANCE.md) - Tối ưu hiệu suất
- [API Documentation](API.md) - Sử dụng API
- [Testing Guide](TESTING.md) - Testing configuration
