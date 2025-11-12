import os
from pathlib import Path

class Config:
    # Đường dẫn cơ sở
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MODEL_DIR = BASE_DIR / 'models'
    LOG_DIR = BASE_DIR / 'logs'
    OUTPUT_FOLDER = BASE_DIR / 'output'  # Cho JSON/Markdown output
    
    # Cài đặt OCR VL
    USE_GPU = True
    GPU_MEM = 500  # MB
    
    # Tính năng PaddleOCR-VL
    USE_LAYOUT_DETECTION = True      # Nhận diện layout
    USE_DOC_ORIENTATION = True       # Nhận diện hướng trang
    USE_DOC_UNWARPING = True         # Làm phẳng ảnh cong
    
    # Model Management
    MODEL_IDLE_TIMEOUT = 600  # Giải phóng model sau 10 phút idle (giây)
    ENABLE_MODEL_AUTO_UNLOAD = True  # Tự động giải phóng model khi idle
    
    # Cài đặt API
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'}  # Thêm PDF
    MAX_BATCH_SIZE = 10
    REQUEST_TIMEOUT = 30
    
    # Queue Management
    ENABLE_REQUEST_QUEUE = True  # Kích hoạt queue khi quá tải
    MAX_CONCURRENT_REQUESTS = 5  # Số request xử lý đồng thời tối đa
    QUEUE_MAX_SIZE = 50  # Kích thước queue tối đa
    QUEUE_TIMEOUT = 60  # Timeout cho request trong queue (giây)
    
    # Định dạng output
    ENABLE_JSON_OUTPUT = True
    ENABLE_MARKDOWN_OUTPUT = True
    
    # Ngưỡng độ tin cậy
    MIN_CONFIDENCE = 0.5
    
    @staticmethod
    def init_app():
        """Tạo các thư mục cần thiết"""
        for folder in [Config.UPLOAD_FOLDER, Config.MODEL_DIR, 
                       Config.LOG_DIR, Config.OUTPUT_FOLDER]:
            folder.mkdir(exist_ok=True, parents=True)