# Performance Tuning Guide

Hướng dẫn tối ưu hiệu suất cho MARC-A-BOT Backend.

## Quick Wins

### 1. Enable GPU

```python
# app/config.py
USE_GPU = True
```

**Impact:** 5-10x faster processing

### 2. Tune Concurrent Requests

```python
MAX_CONCURRENT_REQUESTS = <số cores CPU>
```

**Recommendations:**
- 4 cores: `MAX_CONCURRENT = 3-4`
- 8 cores: `MAX_CONCURRENT = 6-8`
- 16+ cores: `MAX_CONCURRENT = 12-16`

### 3. Adjust Batch Size

```python
# Cho ảnh nhỏ
MAX_BATCH_SIZE = 10
BATCH_WORKERS = 5

# Cho ảnh lớn/PDF
MAX_BATCH_SIZE = 3
BATCH_WORKERS = 2
```

### 4. Model Auto-Unload

```python
# High traffic: Disable
ENABLE_MODEL_AUTO_UNLOAD = False

# Low traffic: Enable với timeout ngắn
ENABLE_MODEL_AUTO_UNLOAD = True
MODEL_IDLE_TIMEOUT = 300
```

---

## Performance Metrics

### Measure Performance

```bash
# API metrics
curl http://localhost:5001/api/ocr/metrics

# Với Python
import requests
import time

start = time.time()
response = requests.post(
    'http://localhost:5001/api/ocr',
    files={'file': open('test.jpg', 'rb')}
)
end = time.time()

print(f"Time: {end - start:.2f}s")
```

### Expected Performance

| Hardware | Single Image | Batch (10 files) |
|----------|--------------|------------------|
| CPU only | 2-4s | 20-40s |
| GPU (4GB VRAM) | 0.5-1s | 5-10s |
| GPU (8GB+ VRAM) | 0.3-0.7s | 3-7s |

---

## Optimization Checklist

### Hardware

- [ ] GPU với CUDA 11.8+
- [ ] 16GB+ RAM
- [ ] SSD storage
- [ ] Gigabit network

### Software

- [ ] Latest PaddlePaddle GPU version
- [ ] Python 3.11+
- [ ] Gunicorn với multiple workers (production)

### Configuration

- [ ] `USE_GPU = True`
- [ ] `MAX_CONCURRENT_REQUESTS` tuned
- [ ] `BATCH_WORKERS` optimized
- [ ] Queue enabled cho high traffic

### Application

- [ ] Model caching (singleton)
- [ ] Auto-unload cho low traffic
- [ ] Logging level = INFO (not DEBUG)

---

## Troubleshooting Slow Performance

### GPU not used

```bash
# Check
python -c "import paddle; print(paddle.device.cuda.device_count())"

# Fix
USE_GPU=True in config
```

### Out of memory

```python
# Reduce batch size
MAX_BATCH_SIZE = 3
MAX_CONCURRENT_REQUESTS = 2

# Enable auto-unload
ENABLE_MODEL_AUTO_UNLOAD = True
MODEL_IDLE_TIMEOUT = 300
```

### Queue bottleneck

```python
# Increase limits
MAX_CONCURRENT_REQUESTS = 10
QUEUE_MAX_SIZE = 100

# Add more workers
BATCH_WORKERS = 8
```

---

## Production Deployment

### Gunicorn Configuration

```bash
gunicorn -w 4 \
  -b 0.0.0.0:5001 \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  app:app
```

### Nginx Load Balancing

```nginx
upstream backend {
    server localhost:5001;
    server localhost:5002;
    server localhost:5003;
    server localhost:5004;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

---

## Monitoring

### Key Metrics to Track

1. **Processing Time** - Thời gian xử lý mỗi request
2. **Queue Size** - Số request đang chờ
3. **Success Rate** - Tỷ lệ thành công
4. **GPU/CPU Usage** - Resource utilization
5. **Memory Usage** - RAM/VRAM consumption

### Tools

- `/api/ocr/metrics` endpoint
- `nvidia-smi` cho GPU
- `htop` cho CPU/RAM
- Application logs

---

## Benchmarking

```bash
# Apache Bench
ab -n 100 -c 10 \
  -p test.jpg \
  -T multipart/form-data \
  http://localhost:5001/api/ocr

# Locust
locust -f locustfile.py --host=http://localhost:5001
```

---

## Best Practices

1. **Profile trước khi optimize**
2. **Monitor metrics continuously**
3. **Test mỗi thay đổi**
4. **Document performance tuning**
5. **Set up alerts cho slowdown**

---

## Next Steps

- [Configuration Guide](CONFIGURATION.md)
- [API Documentation](API.md)
- [Monitoring Setup](MONITORING.md)
