Markdown
# 🤖 Enterprise Multi-Agent Data Extraction & Workflow Automation System

> Hệ thống tự động hóa trích xuất, phân loại và chuẩn hóa dữ liệu từ tài liệu/hình ảnh không cấu trúc dựa trên kiến trúc **Multi-Agent (CrewAI / Gemini API)** kết hợp **OCR Pipeline** và **Smart Caching Layer**.

## 🎯 Tổng quan & Tính năng Cốt lõi

Hệ thống được thiết kế nhằm giải quyết bài toán tự động hóa quy trình xử lý dữ liệu đầu vào phức tạp, giảm bớt 90% thao tác thủ công trong công tác nhập liệu, phân loại và chuẩn hóa dữ liệu doanh nghiệp/trường học:

- 🤖 **5-Agent Autonomous AI Workflow:** Phân chia 5 Agent AI chuyên biệt đảm nhận từng công đoạn (Đọc hiểu OCR, Trích xuất thông tin chính, Phân tích thực thể, Phân loại dữ liệu, Tự động gán Tag/Metadata).
- 📄 **Multi-Format OCR Processing Engine:** Tự động quét và đọc hiểu dữ liệu từ hình ảnh, biểu mẫu (Forms), tài liệu bằng PaddleOCR kết hợp AI Vision.
- 🔍 **Smart Classification & Entity Matching:** Tích hợp thuật toán Fuzzy Matching (RapidFuzz) và Caching Layer (SQLite) giúp chuẩn hóa danh mục dữ liệu, giảm 80% độ trễ API.
- ⚡ **RESTful API & Automation Tools:** Cung cấp 8 Endpoints RESTful và 6 Tools Interface tương thích trực tiếp với CrewAI, LangGraph, n8n và LangChain.
- 💻 **Interactive Dashboard:** Giao diện React 18 + TailwindCSS hỗ trợ Drag & Drop tài liệu, kiểm tra dữ liệu trích xuất và hiển thị cấu trúc dữ liệu theo thời gian thực.

## 🎨 Ngăn xếp Công nghệ (Tech Stack)

### AI & Automation Engine
- **Multi-Agent Frameworks:** CrewAI, LangChain, LangGraph, Google Gemini API
- **OCR & Computer Vision:** PaddleOCR, OpenCV, Pillow, PDF2Image
- **Backend Logic:** Python 3.11, Flask, RapidFuzz (Fuzzy String Matching)
- **Caching & Storage:** SQLite (Smart Cache Layer)

### Frontend & Integration
- React 18, TypeScript 5, Vite, TailwindCSS
- RESTful API Interface (8 Endpoints)

## 🏗 Kiến trúc Hệ thống (System Architecture)

[Unstructured Data / Images / Forms]
│
▼
[OCR Processing Engine]
│
▼
┌──────────────────────────────────────────┐
│     Multi-Agent AI Workflow (5 Agents)   │
│  - Agent 1: Title & Header Extraction    │
│  - Agent 2: Entity & Attribute Parsing   │
│  - Agent 3: Timestamp & ID Validation    │
│  - Agent 4: Authority & Metadata Match   │
│  - Agent 5: Document Type Classification │
└──────────────────────────────────────────┘
│
▼
[Smart Cache Layer (Fuzzy Matching + SQLite)]
│
▼
[Structured JSON Output / CRM & Database Sync]


## 🚀 Hướng dẫn Cài đặt & Vận hành (Quick Start)

```bash
# 1. Khởi chạy Backend Services
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # Flask server (http://localhost:5000)

# 2. Khởi chạy Frontend UI
cd ../
npm install
npm run dev  # React UI (http://localhost:5173)
🤖 AI Framework & Tool Integrations
Cung cấp 6 Custom Tools sẵn sàng kết nối vào hệ thống tự động hóa qua CrewAI hoặc Gemini Function Calling:

Python
# Tích hợp CrewAI Tool Example
from crewai import Agent
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

keyword_agent = KeywordProcessorAgent()
automation_agent = Agent(
    role='Data Automation Specialist',
    tools=keyword_agent.get_available_tools()
)
📖 Tài liệu Hệ thống
AI Agent Integration Guide: Hướng dẫn kết nối Tools với CrewAI & LangChain.

Quick Start Guide: Hướng dẫn thiết lập nhanh 6 AI Tools interface.
