import os
import re
from pathlib import Path
from werkzeug.utils import secure_filename
from app.config import Config


def allowed_file(filename: str) -> bool:
    """
    Kiểm tra xem phần mở rộng file có được phép không
    
    Args:
        filename: Tên file cần kiểm tra
        
    Returns:
        True nếu phần mở rộng được phép, False nếu không
    """
    if not filename:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def validate_file_size(file) -> bool:
    """
    Kiểm tra kích thước file so với giới hạn tối đa
    
    Args:
        file: Đối tượng file từ request
        
    Returns:
        True nếu kích thước file trong giới hạn, False nếu không
    """
    # Seek to end to get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    # Reset file pointer to beginning
    file.seek(0)
    
    return file_size <= Config.MAX_FILE_SIZE


def sanitize_filename(filename: str) -> str:
    """
    Làm sạch tên file để ngăn chặn các vấn đề bảo mật
    
    Args:
        filename: Tên file gốc
        
    Returns:
        Tên file đã được làm sạch, an toàn cho filesystem
    """
    # Use werkzeug's secure_filename
    safe_name = secure_filename(filename)
    
    # Additional sanitization: remove any non-alphanumeric chars except . - _
    safe_name = re.sub(r'[^\w\s.-]', '', safe_name)
    
    # Replace spaces with underscores
    safe_name = safe_name.replace(' ', '_')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = 'unnamed_file'
    
    return safe_name
