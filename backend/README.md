# MARC-A-BOT Backend - OCR Service

Backend API cho hệ thống OCR sách sử dụng PaddleOCR-VL để trích xuất metadata phục vụ cataloging MARC21.

##  Tính năng chính

- **OCR chính xác cao** với PaddleOCR-VL
- **Xử lý batch** với ThreadPoolExecutor
- **Queue management** tự động khi quá tải
- **GPU acceleration** với CUDA
- **Auto-unload model** khi idle để tiết kiệm memory
- **Metrics & Monitoring** với logging chi tiết
- **RESTful API** với Flask

##  Yêu cầu hệ thống

- Python 3.11.9+
- CUDA 11.8+ (cho GPU)
- 8GB RAM (16GB khuyến nghị)
- 4GB VRAM (cho GPU)

##  Quick Start

\\\ash
cd MARC-A-BOT/backend

python -m venv .venv
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

python app.py
\\\`n
Server sẽ chạy tại http://localhost:5001

##  Documentation

Chi tiết đầy đủ xem trong thư mục **docs/**:

- [API Documentation](docs/API.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Configuration](docs/CONFIGURATION.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Testing](docs/TESTING.md)
- [Performance Tuning](docs/PERFORMANCE.md)

##  Ví dụ API

\\\ash
curl -X POST http://localhost:5001/api/ocr -F 'file=@book.jpg'
\\\`n
##  Kiến trúc

\\\	ext
backend/
 app/
    config.py
    routes/
    services/
    ultis/
    test/
 docs/
 app.py
\\\`n
##  Testing

\\\ash
pytest app/test/
\\\`n
##  License

MIT License
