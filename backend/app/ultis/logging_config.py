"""
Logging Configuration - Main Entry Point

Module này là điểm truy cập chính cho logging system.
Import và re-export tất cả các components từ các module con.

Sử dụng:
    from app.ultis.logging_config import setup_logging, metrics_logger
    from app.ultis.logging_config import log_execution_time, log_api_request
"""

# Import từ các module con
from app.ultis.formatters import StructuredFormatter, ColoredFormatter
from app.ultis.metrics_logger import OCRMetricsLogger, metrics_logger
from app.ultis.decorators import (
    log_execution_time,
    log_api_request,
    log_ocr_operation
)
from app.ultis.logger_setup import setup_logging, get_logger

# Export tất cả để dễ import
__all__ = [
    # Formatters
    'StructuredFormatter',
    'ColoredFormatter',
    
    # Metrics Logger
    'OCRMetricsLogger',
    'metrics_logger',
    
    # Decorators
    'log_execution_time',
    'log_api_request',
    'log_ocr_operation',
    
    # Setup
    'setup_logging',
    'get_logger',
]
