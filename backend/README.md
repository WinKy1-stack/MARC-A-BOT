# MARC-A-BOT Backend

Backend API đơn giản sử dụng Flask cho ứng dụng MARC-A-BOT.

## Cài đặt

1. Tạo môi trường ảo (virtual environment):
```bash
python -m venv venv
```

2. Kích hoạt môi trường ảo:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Tạo file `.env` từ `.env.example`:
```bash
copy .env.example .env
```

## Chạy ứng dụng

```bash
python app.py
```

Server sẽ chạy tại: http://localhost:5000

## API Endpoints

- `GET /` - Trang chủ
- `GET /api/health` - Kiểm tra trạng thái server
- `POST /api/process` - Xử lý dữ liệu

## Cấu trúc thư mục

```
backend/
├── app.py              # File chính của ứng dụng Flask
├── requirements.txt    # Dependencies
├── .env.example       # File cấu hình mẫu
└── README.md          # Tài liệu
```
