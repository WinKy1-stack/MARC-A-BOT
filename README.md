# MARC-A-BOT

Ứng dụng web xử lý ảnh và dữ liệu MARC với giao diện hiện đại và backend API.

## 📋 Mô tả dự án

MARC-A-BOT là một ứng dụng full-stack cho phép người dùng:
- Upload và xử lý ảnh
- Xem trước ảnh với giao diện grid hiện đại
- Xử lý dữ liệu MARC (Machine-Readable Cataloging)
- Tương tác với API backend để xử lý dữ liệu

## 🛠️ Ngăn xếp công nghệ

### Frontend
- **React 18** - Thư viện UI
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool và dev server nhanh
- **TailwindCSS** - Utility-first CSS framework
- **React Hooks** - Quản lý state và side effects

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Python 3.x** - Ngôn ngữ lập trình backend

### Dev Tools
- **ESLint** - Code linting
- **PostCSS** - CSS processing
- **TypeScript Compiler** - Type checking

## 📁 Cấu trúc dự án

```
MARC-A-BOT/
├── backend/              # Flask API server
│   ├── app.py           # Main Flask application
│   ├── requirements.txt # Python dependencies
│   └── README.md        # Backend documentation
│
├── src/                 # Frontend source code
│   ├── components/      # React components
│   ├── hooks/          # Custom React hooks
│   ├── types/          # TypeScript type definitions
│   ├── constants/      # Constants and configs
│   └── assets/         # Static assets
│
├── public/             # Public assets
├── index.html          # HTML entry point
├── package.json        # Node dependencies
└── vite.config.ts      # Vite configuration
```

## 🚀 Hướng dẫn cài đặt

### Prerequisites
- Node.js (v18 trở lên)
- Python 3.8 trở lên
- npm hoặc yarn

### Cài đặt Frontend

1. Clone repository:
```bash
git clone https://github.com/LockMan04/MARC-A-BOT.git
cd MARC-A-BOT
```

2. Cài đặt dependencies:
```bash
npm install
```

3. Chạy development server:
```bash
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:5173`

### Cài đặt Backend

1. Di chuyển vào thư mục backend:
```bash
cd backend
```

2. Tạo virtual environment:
```bash
python -m venv venv
```

3. Kích hoạt virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

5. Chạy Flask server:
```bash
python app.py
```

Backend sẽ chạy tại: `http://localhost:5000`

## 📝 Scripts

### Frontend
```bash
npm run dev          # Chạy development server
npm run build        # Build production
npm run preview      # Preview production build
npm run lint         # Chạy ESLint
```

### Backend
```bash
python app.py        # Chạy Flask server
```

## 🔌 API Endpoints

- `GET /` - API home
- `GET /api/health` - Health check
- `POST /api/process` - Xử lý dữ liệu

Chi tiết API xem tại [backend/README.md](backend/README.md)

## 🎨 Features

- ✅ Drag & drop upload ảnh
- ✅ Preview ảnh với grid layout
- ✅ Xử lý dữ liệu MARC
- ✅ Toast notifications
- ✅ Responsive design
- ✅ RESTful API backend
