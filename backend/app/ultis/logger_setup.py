"""
Logger Setup và Configuration

Module này cung cấp cấu hình logging cho toàn bộ ứng dụng.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from app.config import Config
from app.ultis.formatters import StructuredFormatter, ColoredFormatter


def setup_logging(
    log_level: int = logging.INFO,
    log_dir: Optional[Path] = None,
    enable_json: bool = False,
    enable_colors: bool = True
) -> logging.Logger:
    """
    Cấu hình logging cho ứng dụng
    
    Args:
        log_level: Mức log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Thư mục chứa log files
        enable_json: Có sử dụng JSON format không
        enable_colors: Có sử dụng màu sắc cho console không
        
    Returns:
        Configured logger instance
    """
    log_dir = log_dir or Config.LOG_DIR
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Tạo logger
    logger = logging.getLogger('ocr_service')
    logger.setLevel(log_level)
    
    # Xóa handlers cũ nếu có
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    if enable_json:
        console_formatter = StructuredFormatter()
    elif enable_colors:
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler với rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'ocr_service.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    if enable_json:
        file_formatter = StructuredFormatter()
    else:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'ocr_errors.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # Debug file handler (chỉ khi log level là DEBUG)
    if log_level == logging.DEBUG:
        debug_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'ocr_debug.log',
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=2,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(file_formatter)
        logger.addHandler(debug_handler)
    
    logger.info("Logging system initialized")
    logger.info("Log directory: %s", log_dir)
    logger.info("Log level: %s", logging.getLevelName(log_level))
    
    return logger


def get_logger(name: str = 'ocr_service') -> logging.Logger:
    """
    Lấy logger instance
    
    Args:
        name: Tên logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
