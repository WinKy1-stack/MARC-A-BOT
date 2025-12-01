# API Documentation

Tài liệu chi tiết về các API endpoints của MARC-A-BOT OCR Service.

## Base URL

```
http://localhost:5001/api/ocr
```

---

## Endpoints

### 1. Process Single File

Xử lý một file ảnh hoặc PDF để OCR.

**Endpoint:** `POST /api/ocr` hoặc `POST /api/ocr/process`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file` (required): File ảnh hoặc PDF

**Response Success (200):**
```json
{
  "status": "success",
  "file_id": "abc-123-def-456",
  "extracted_text": "Full extracted text content...",
  "markdown": "# Formatted markdown\n\n...",
  "sections": {
    "title": "Python Programming Guide",
    "author": "John Doe",
    "publisher": "Tech Books Inc.",
    "isbn": "978-1234567890",
    "year": "2024"
  },
  "confidence": 0.95,
  "processing_time": 1.23,
  "timestamp": "2024-11-13T10:30:00"
}
```

**Response Queued (202):**
```json
{
  "status": "queued",
  "request_id": "abc-123-def-456",
  "queue_position": 3,
  "estimated_wait_time": 6,
  "message": "Request queued. Check status with /api/ocr/status/<request_id>"
}
```

**Response Error (400):**
```json
{
  "status": "error",
  "error_code": "NO_FILE",
  "message": "No file provided"
}
```

**Các error codes:**
- `NO_FILE`: Không có file trong request
- `EMPTY_FILENAME`: Tên file rỗng
- `INVALID_FORMAT`: Format file không hỗ trợ
- `FILE_TOO_LARGE`: File vượt quá kích thước cho phép
- `QUEUE_FULL`: Queue đầy, không thể nhận request mới
- `INTERNAL_ERROR`: Lỗi server

**Example:**
```bash
# Với curl
curl -X POST http://localhost:5001/api/ocr \
  -F "file=@/path/to/book_cover.jpg"

# Với Python requests
import requests

with open('book_cover.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:5001/api/ocr',
        files=files
    )
    print(response.json())
```

---

### 2. Process Batch Files

Xử lý nhiều file cùng lúc (tối đa 10 files).

**Endpoint:** `POST /api/ocr/batch`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `files` (required): Multiple files (max 10)

**Response (200):**
```json
{
  "status": "success",
  "total_files": 3,
  "results": [
    {
      "status": "success",
      "file_id": "file-1",
      "extracted_text": "...",
      "sections": {...}
    },
    {
      "status": "success",
      "file_id": "file-2",
      "extracted_text": "...",
      "sections": {...}
    },
    {
      "status": "error",
      "file_id": "file-3",
      "error": "OCR processing failed"
    }
  ]
}
```

**Response Error (400):**
```json
{
  "status": "error",
  "error_code": "BATCH_TOO_LARGE",
  "message": "Maximum 10 files allowed per batch"
}
```

**Example:**
```bash
# Với curl
curl -X POST http://localhost:5001/api/ocr/batch \
  -F "files=@book1.jpg" \
  -F "files=@book2.jpg" \
  -F "files=@book3.pdf"

# Với Python
import requests

files = [
    ('files', open('book1.jpg', 'rb')),
    ('files', open('book2.jpg', 'rb')),
    ('files', open('book3.pdf', 'rb'))
]
response = requests.post(
    'http://localhost:5001/api/ocr/batch',
    files=files
)
print(response.json())
```

---

### 3. Get Service Status

Lấy trạng thái service hoặc request cụ thể.

**Endpoint:** `GET /api/ocr/status[/<request_id>]`

**Request:**
- Method: `GET`
- Params: 
  - `request_id` (optional): ID của request cần check

**Response - Service Status (200):**
```json
{
  "status": "ok",
  "pipeline": {
    "initialized": true,
    "model_loaded": true,
    "last_used": "2024-11-13T10:30:00",
    "auto_unload_enabled": true,
    "will_unload_in_seconds": 450
  },
  "gpu": {
    "available": true,
    "device_count": 1,
    "current_device": 0,
    "memory_used_mb": 2048,
    "memory_total_mb": 8192
  },
  "queue": {
    "queue_size": 2,
    "active_requests": 5,
    "max_concurrent": 5,
    "max_queue_size": 50,
    "total_queued": 150,
    "total_processed": 145,
    "total_failed": 3,
    "total_timeout": 2
  },
  "config": {
    "use_gpu": true,
    "max_batch_size": 10,
    "max_file_size_mb": 10,
    "supported_formats": ["jpg", "jpeg", "png", "pdf"]
  }
}
```

**Response - Request Status (200):**
```json
{
  "request_id": "abc-123",
  "status": "processing",
  "created_at": 1699876200.5,
  "wait_time": 3.2,
  "result": null,
  "error": null
}
```

**Request Status Values:**
- `pending`: Đang chờ trong queue
- `processing`: Đang xử lý
- `completed`: Hoàn thành
- `failed`: Thất bại
- `timeout`: Timeout trong queue

**Example:**
```bash
# Service status
curl http://localhost:5001/api/ocr/status

# Request status
curl http://localhost:5001/api/ocr/status/abc-123-def-456
```

---

### 4. Get Metrics

Lấy metrics và thống kê OCR.

**Endpoint:** `GET /api/ocr/metrics`

**Request:**
- Method: `GET`
- Query Params:
  - `hours` (optional, default=24): Số giờ để lấy metrics

**Response (200):**
```json
{
  "status": "success",
  "metrics": {
    "total_requests": 150,
    "total_success": 145,
    "total_failed": 5,
    "success_rate": 96.67,
    "avg_processing_time": 1.23,
    "avg_confidence": 0.94,
    "total_files_processed": 145,
    "total_batch_requests": 20,
    "period_hours": 24,
    "timestamp": "2024-11-13T10:30:00"
  },
  "batch_stats": {
    "total_batches": 20,
    "total_files": 180,
    "avg_batch_size": 9.0,
    "avg_time_per_batch": 8.5,
    "success_rate": 97.22
  },
  "timestamp": "2024-11-13T10:30:00"
}
```

**Example:**
```bash
# Metrics 24h gần nhất
curl http://localhost:5001/api/ocr/metrics

# Metrics 1 tuần (168h)
curl http://localhost:5001/api/ocr/metrics?hours=168
```

---

### 5. Download Result

Tải file kết quả đã xử lý (JSON hoặc Markdown).

**Endpoint:** `GET /api/ocr/download/<file_id>/<file_type>`

**Request:**
- Method: `GET`
- URL Params:
  - `file_id`: ID của file
  - `file_type`: `json` hoặc `markdown`

**Response:**
- Content-Type: `application/json` hoặc `text/markdown`
- File download

**Example:**
```bash
# Download JSON
curl http://localhost:5001/api/ocr/download/abc-123/json -o result.json

# Download Markdown
curl http://localhost:5001/api/ocr/download/abc-123/markdown -o result.md
```

---

## Rate Limiting & Queue

Khi số lượng request đồng thời vượt quá `MAX_CONCURRENT_REQUESTS` (default: 5):

1. Request sẽ được đưa vào queue
2. Response trả về status code `202` với thông tin:
   - `queue_position`: Vị trí trong queue
   - `estimated_wait_time`: Thời gian chờ ước tính (giây)
   - `request_id`: ID để check status

3. Client có thể polling status bằng endpoint `/api/ocr/status/<request_id>`

**Queue Limits:**
- `QUEUE_MAX_SIZE`: 50 requests
- `QUEUE_TIMEOUT`: 60 seconds
- Request timeout sẽ bị reject với status `timeout`

---

## File Limits

| Giới hạn | Giá trị mặc định |
|----------|------------------|
| Max file size | 10 MB |
| Max batch size | 10 files |
| Supported formats | jpg, jpeg, png, pdf |

---

## Error Handling

Tất cả errors đều trả về format chuẩn:

```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message"
}
```

**HTTP Status Codes:**
- `200` - Success
- `202` - Accepted (queued)
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (queue full)

---

## Python Client Example

```python
import requests
from pathlib import Path

class OCRClient:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
    
    def process_file(self, file_path):
        """Xử lý single file"""
        url = f"{self.base_url}/api/ocr"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        return response.json()
    
    def process_batch(self, file_paths):
        """Xử lý batch files"""
        url = f"{self.base_url}/api/ocr/batch"
        
        files = [('files', open(fp, 'rb')) for fp in file_paths]
        response = requests.post(url, files=files)
        
        # Close files
        for _, f in files:
            f.close()
        
        return response.json()
    
    def get_status(self, request_id=None):
        """Lấy status"""
        if request_id:
            url = f"{self.base_url}/api/ocr/status/{request_id}"
        else:
            url = f"{self.base_url}/api/ocr/status"
        
        response = requests.get(url)
        return response.json()
    
    def get_metrics(self, hours=24):
        """Lấy metrics"""
        url = f"{self.base_url}/api/ocr/metrics"
        response = requests.get(url, params={'hours': hours})
        return response.json()

# Usage
client = OCRClient()

# Single file
result = client.process_file('book_cover.jpg')
print(result['extracted_text'])

# Batch
results = client.process_batch(['book1.jpg', 'book2.jpg'])
print(f"Processed {results['total_files']} files")

# Status
status = client.get_status()
print(f"Queue size: {status['queue']['queue_size']}")
```

---

## JavaScript/TypeScript Client Example

```typescript
class OCRClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:5001') {
    this.baseUrl = baseUrl;
  }

  async processFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/ocr`, {
      method: 'POST',
      body: formData
    });

    return await response.json();
  }

  async processBatch(files: File[]): Promise<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await fetch(`${this.baseUrl}/api/ocr/batch`, {
      method: 'POST',
      body: formData
    });

    return await response.json();
  }

  async getStatus(requestId?: string): Promise<any> {
    const url = requestId 
      ? `${this.baseUrl}/api/ocr/status/${requestId}`
      : `${this.baseUrl}/api/ocr/status`;

    const response = await fetch(url);
    return await response.json();
  }

  async getMetrics(hours: number = 24): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/ocr/metrics?hours=${hours}`
    );
    return await response.json();
  }
}

// Usage
const client = new OCRClient();

// Single file
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
const result = await client.processFile(file);
console.log(result.extracted_text);
```

---

## WebSocket Support (Future)

Hiện tại API chỉ hỗ trợ HTTP REST. WebSocket cho real-time updates đang trong roadmap.

---

## Changelog

### v1.0.0 (2024-11-13)
- Initial release
- Basic OCR endpoints
- Batch processing
- Queue management
- Metrics tracking
