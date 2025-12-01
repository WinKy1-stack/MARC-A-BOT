"""
Custom Formatters cho Logging

Module này chứa các formatter tùy chỉnh cho logging system.
"""

import logging
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """
    Formatter cho structured logging với JSON format
    
    Format log thành JSON để dễ dàng parse và phân tích
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record thành JSON
        
        Args:
            record: Log record cần format
            
        Returns:
            JSON string của log record
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Thêm exception info nếu có
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Thêm extra fields nếu có
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Formatter với màu sắc cho console output
    
    Thêm màu sắc vào log messages để dễ đọc hơn
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record với màu sắc
        
        Args:
            record: Log record cần format
            
        Returns:
            Colored log string
        """
        # Lấy màu cho level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format message cơ bản
        formatted = super().format(record)
        
        # Thêm màu vào level name
        colored = formatted.replace(
            record.levelname,
            f"{color}{record.levelname}{reset}"
        )
        
        return colored
