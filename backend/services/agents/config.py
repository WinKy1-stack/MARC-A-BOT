"""
Configuration cho Agents
Cấu hình cho các agents xử lý OCR và MARC21
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Gemini API Configuration
# Lấy API key từ environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')  # gemini-1.5-pro, gemini-1.5-flash, gemini-pro

# Agent Configuration
AGENT_TIMEOUT = int(os.getenv('AGENT_TIMEOUT', '30'))  # Timeout cho mỗi agent (giây)
AGENT_MAX_RETRIES = int(os.getenv('AGENT_MAX_RETRIES', '3'))  # Số lần retry tối đa

# Keyword Extraction Configuration
KEYWORD_MIN_SCORE = float(os.getenv('KEYWORD_MIN_SCORE', '0.5'))  # Score tối thiểu cho keywords
KEYWORD_MAX_COUNT = int(os.getenv('KEYWORD_MAX_COUNT', '10'))  # Số keywords tối đa

# Authority Service Configuration
AUTHORITY_SUBJECT_TYPE = os.getenv('AUTHORITY_SUBJECT_TYPE', 'general')  # medical, general, science
AUTHORITY_USE_CACHE = os.getenv('AUTHORITY_USE_CACHE', 'True').lower() == 'true'

# Logging
AGENT_LOG_LEVEL = os.getenv('AGENT_LOG_LEVEL', 'INFO')

# Validation
def validate_config():
    """
    Kiểm tra cấu hình có hợp lệ không
    """
    errors = []
    
    # Kiểm tra Gemini API key (nếu cần dùng AI)
    # Không bắt buộc vì agents có thể chạy không cần Gemini
    if not GEMINI_API_KEY:
        # Chỉ cảnh báo, không báo lỗi
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "GEMINI_API_KEY không được cấu hình. "
            "Các agents vẫn có thể chạy, nhưng không thể sử dụng Gemini AI."
        )
    
    if KEYWORD_MIN_SCORE < 0 or KEYWORD_MIN_SCORE > 1:
        errors.append(f"KEYWORD_MIN_SCORE phải trong khoảng [0, 1], hiện tại: {KEYWORD_MIN_SCORE}")
    
    if KEYWORD_MAX_COUNT < 1:
        errors.append(f"KEYWORD_MAX_COUNT phải >= 1, hiện tại: {KEYWORD_MAX_COUNT}")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

