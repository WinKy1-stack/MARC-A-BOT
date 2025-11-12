# Installation Guide

Hướng dẫn cài đặt chi tiết MARC-A-BOT Backend OCR Service.

## Mục lục

- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt Python](#cài-đặt-python)
- [Cài đặt CUDA (GPU)](#cài-đặt-cuda-gpu)
- [Cài đặt Dependencies](#cài-đặt-dependencies)
- [Cấu hình](#cấu-hình)
- [Kiểm tra cài đặt](#kiểm-tra-cài-đặt)

---

## Yêu cầu hệ thống

### Minimum Requirements

- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 10GB free space
- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 10.15+

### Recommended (with GPU)

- **CPU**: 8+ cores
- **RAM**: 16GB+
- **GPU**: NVIDIA GPU với 4GB+ VRAM
- **CUDA**: 11.8 hoặc 12.x
- **Storage**: 20GB+ SSD

---

## Cài đặt Python

### Windows

1. Download Python 3.11.9 từ [python.org](https://www.python.org/downloads/)
2. Chạy installer, **tick vào "Add Python to PATH"**
3. Kiểm tra:

```powershell
python --version
# Python 3.11.9
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3.11 --version
```

### macOS

```bash
# Với Homebrew
brew install python@3.11

python3.11 --version
```

---

## Cài đặt CUDA (GPU)

### Kiểm tra GPU

```bash
# Windows/Linux
nvidia-smi

# Xem CUDA version
nvcc --version
```

### Windows

1. Download [CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive)
2. Download [cuDNN 8.6](https://developer.nvidia.com/cudnn)
3. Cài đặt CUDA Toolkit
4. Giải nén cuDNN vào thư mục CUDA:
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\
   ```

### Linux (Ubuntu)

```bash
# CUDA 11.8
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run

# Thêm vào ~/.bashrc
export PATH=/usr/local/cuda-11.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH

source ~/.bashrc
```

### Kiểm tra CUDA

```bash
nvcc --version
nvidia-smi
```

---

## Cài đặt Dependencies

### 1. Clone Repository

```bash
git clone https://github.com/LockMan04/MARC-A-BOT.git
cd MARC-A-BOT/backend
```

### 2. Tạo Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Cài đặt PaddlePaddle

**Với GPU (CUDA 11.8):**
```bash
python -m pip install paddlepaddle-gpu==2.6.0.post118 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html
```

**Với CPU only:**
```bash
pip install paddlepaddle==2.6.0
```

**Kiểm tra:**
```python
import paddle
print(paddle.__version__)
print(paddle.device.cuda.device_count())  # > 0 nếu có GPU
```

### 5. Cài đặt Dependencies khác

```bash
pip install -r requirements.txt
```

**File `requirements.txt`:**
```txt
Flask==3.0.0
Flask-CORS==4.0.0
paddlepaddle-gpu==2.6.0.post118
paddleocr-vl>=3.3.0
Pillow==10.1.0
numpy==1.24.3
opencv-python==4.8.1.78
pytest==7.4.3
pytest-cov==4.1.0
python-dotenv==1.0.0
```

---

## Cấu hình

### 1. Tạo file `.env`

```bash
cp .env.example .env
```

**Nội dung `.env`:**
```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Server
HOST=0.0.0.0
PORT=5001
DEBUG=True

# OCR Settings
USE_GPU=True
MAX_BATCH_SIZE=10
MAX_FILE_SIZE=10485760

# Queue
ENABLE_REQUEST_QUEUE=True
MAX_CONCURRENT_REQUESTS=5
QUEUE_MAX_SIZE=50
QUEUE_TIMEOUT=60

# Model Auto-unload
ENABLE_MODEL_AUTO_UNLOAD=True
MODEL_IDLE_TIMEOUT=600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 2. Tạo thư mục cần thiết

```bash
mkdir -p uploads
mkdir -p outputs
mkdir -p logs
```

### 3. Cấu hình `app/config.py`

File này chứa tất cả cấu hình, có thể chỉnh sửa trực tiếp hoặc dùng biến môi trường.

**Các cấu hình quan trọng:**

```python
# GPU
USE_GPU = True  # False nếu không có GPU

# Performance
MAX_BATCH_SIZE = 10  # Số file tối đa mỗi batch
MAX_CONCURRENT_REQUESTS = 5  # Request đồng thời

# File limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

# Model auto-unload
ENABLE_MODEL_AUTO_UNLOAD = True
MODEL_IDLE_TIMEOUT = 600  # 10 phút

# Queue
ENABLE_REQUEST_QUEUE = True
QUEUE_MAX_SIZE = 50
QUEUE_TIMEOUT = 60
```

---

## Kiểm tra cài đặt

### 1. Test Python packages

```bash
python -c "import paddle; print('Paddle:', paddle.__version__)"
python -c "import paddleocr; print('PaddleOCR: OK')"
python -c "import flask; print('Flask:', flask.__version__)"
```

### 2. Test GPU

```bash
python -c "import paddle; print('GPU Count:', paddle.device.cuda.device_count())"
```

Nếu output > 0 → GPU đã sẵn sàng

### 3. Chạy tests

```bash
pytest app/test/ -v
```

### 4. Chạy server

```bash
python app.py
```

**Expected output:**
```
[2024-11-13 10:30:00] INFO: Starting MARC-A-BOT OCR Service
[2024-11-13 10:30:00] INFO: GPU enabled: True
[2024-11-13 10:30:00] INFO: Initializing OCR pipeline...
[2024-11-13 10:30:05] INFO: OCR pipeline ready
 * Running on http://0.0.0.0:5001
```

### 5. Test API

Mở terminal mới:

```bash
# Health check
curl http://localhost:5001/api/ocr/status

# Upload file
curl -X POST http://localhost:5001/api/ocr \
  -F "file=@test_image.jpg"
```

---

## Troubleshooting

### Lỗi: "No module named 'paddle'"

**Giải pháp:**
```bash
# Kiểm tra venv đã activate chưa
which python  # Linux/Mac
where python  # Windows

# Cài lại PaddlePaddle
pip uninstall paddlepaddle paddlepaddle-gpu
pip install paddlepaddle-gpu==2.6.0.post118
```

### Lỗi: "CUDA not available"

**Kiểm tra:**
1. CUDA đã cài đúng version chưa: `nvcc --version`
2. Driver NVIDIA mới nhất chưa: `nvidia-smi`
3. PaddlePaddle GPU version đúng không

**Giải pháp tạm:**
```python
# Trong app/config.py
USE_GPU = False
```

### Lỗi: "DLL load failed" (Windows)

**Nguyên nhân:** Thiếu Visual C++ Redistributable

**Giải pháp:**
Download và cài [VC++ 2015-2022 Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Lỗi: "Out of memory"

**GPU Memory:**
```python
# Trong app/config.py
MAX_BATCH_SIZE = 3  # Giảm batch size
MAX_CONCURRENT_REQUESTS = 2  # Giảm concurrent
```

**RAM Memory:**
```python
ENABLE_MODEL_AUTO_UNLOAD = True
MODEL_IDLE_TIMEOUT = 300  # 5 phút
```

### Lỗi: "Port 5001 already in use"

**Giải pháp:**
```bash
# Đổi port trong .env
PORT=5002

# Hoặc kill process đang dùng port
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# Linux
lsof -i :5001
kill -9 <PID>
```

---

## Production Deployment

### Với Gunicorn (Linux)

```bash
# Cài Gunicorn
pip install gunicorn

# Chạy
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Với Docker

```dockerfile
FROM python:3.11-slim

# Install CUDA (nếu cần GPU)
# ...

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

```bash
docker build -t marc-a-bot-backend .
docker run -p 5001:5001 marc-a-bot-backend
```

### Với Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.marc-a-bot.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Next Steps

- [Configuration Guide](CONFIGURATION.md) - Chi tiết các tùy chọn cấu hình
- [API Documentation](API.md) - Sử dụng API
- [Development Guide](DEVELOPMENT.md) - Phát triển thêm features

---

## Support

Nếu gặp vấn đề:
1. Check [Troubleshooting](#troubleshooting)
2. Xem logs: `logs/app.log`
3. Tạo issue: [GitHub Issues](https://github.com/LockMan04/MARC-A-BOT/issues)
