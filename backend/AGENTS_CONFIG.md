# Cấu hình Agents với Gemini API

## 📋 Tổng quan

File `env.example` chứa tất cả các biến môi trường cần thiết cho hệ thống MARC-A-BOT, bao gồm cấu hình cho các Agents và Gemini AI.

## 🚀 Cài đặt nhanh

### 1. Copy file env.example thành .env

**Linux/macOS:**
```bash
cd backend
cp env.example .env
```

**Windows PowerShell:**
```powershell
cd backend
Copy-Item env.example .env
```

**Windows CMD:**
```cmd
cd backend
copy env.example .env
```

### 2. Cấu hình Gemini API Key

Mở file `.env` và tìm dòng:
```env
GEMINI_API_KEY=your-gemini-api-key-here
```

#### Lấy Gemini API Key:

1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập với Google account
3. Click **"Create API Key"**
4. Copy API key và dán vào file `.env`

**Ví dụ:**
```env
GEMINI_API_KEY=AIzaSyD...your-actual-api-key-here
```

### 3. Kiểm tra cấu hình

```bash
# Kiểm tra Gemini API key đã được set chưa
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('GEMINI_API_KEY:', '✅ SET' if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your-gemini-api-key-here' else '❌ NOT SET')"

# Validate agents config
python -c "from services.agents.config import validate_config; validate_config(); print('✅ Config OK')"
```

## ⚙️ Các biến môi trường quan trọng

### Agents Configuration

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `GEMINI_API_KEY` | API key cho Gemini AI | `your-gemini-api-key-here` |
| `GEMINI_MODEL` | Model Gemini sử dụng | `gemini-1.5-pro` |
| `AGENT_TIMEOUT` | Timeout cho mỗi agent (giây) | `30` |
| `AGENT_MAX_RETRIES` | Số lần retry tối đa | `3` |
| `KEYWORD_MIN_SCORE` | Score tối thiểu cho keywords | `0.5` |
| `KEYWORD_MAX_COUNT` | Số keywords tối đa | `10` |
| `AUTHORITY_SUBJECT_TYPE` | Loại chủ đề (medical/general/science) | `general` |
| `AUTHORITY_USE_CACHE` | Sử dụng cache cho authority | `True` |

### OCR Configuration

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `USE_GPU` | Sử dụng GPU | `True` |
| `MAX_FILE_SIZE` | Kích thước file tối đa (bytes) | `10485760` (10MB) |
| `MAX_BATCH_SIZE` | Số file xử lý cùng lúc | `10` |

## 🔍 Gemini Models có sẵn

- `gemini-1.5-pro` - Model mạnh nhất (khuyến nghị)
- `gemini-1.5-flash` - Nhanh hơn, nhẹ hơn
- `gemini-pro` - Phiên bản cũ

## ⚠️ Lưu ý

1. **Nếu không có Gemini API key:**
   - Hệ thống vẫn hoạt động bình thường
   - Agent 4 sẽ dùng rule-based keyword extraction
   - Authority mapping vẫn hoạt động với LCSH/MeSH/LCC/NLM

2. **Bảo mật:**
   - ❌ **KHÔNG** commit file `.env` vào git
   - ✅ File `.env` đã được thêm vào `.gitignore`
   - ✅ Chỉ commit file `env.example`

3. **Production:**
   - Sử dụng environment variables trên server
   - Hoặc sử dụng secret management service
   - Không lưu API key trong code

## 📚 Tài liệu thêm

- [Configuration Guide](docs/CONFIGURATION.md) - Hướng dẫn cấu hình chi tiết
- [AI Agent Guide](../AI_AGENT_WITH_TOOLS.md) - Hướng dẫn sử dụng Agents với AI
- [Quick Start Agent](../QUICK_START_AGENT.md) - Hướng dẫn nhanh

## 🐛 Troubleshooting

### Gemini API key không hoạt động

```bash
# Kiểm tra API key có hợp lệ không
python -c "from services.agents.gemini_client import is_gemini_available; print('Gemini available:', is_gemini_available())"
```

### Agents không chạy

```bash
# Kiểm tra config
python -c "from services.agents.config import validate_config; validate_config()"
```

### Logs

Xem logs để debug:
```bash
tail -f logs/app.log
```

