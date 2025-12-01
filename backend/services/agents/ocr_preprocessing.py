"""
OCR Text Preprocessing
Hàm tiền xử lý text từ kết quả OCR trước khi đưa vào các agents
"""
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def clean_ocr_text(ocr_json: Dict) -> str:
    """
    Làm sạch text từ kết quả OCR:
    - Nối các dòng bị xuống dòng giữa từ (vd: 'photo-\ncopying' → 'photocopying')
    - Loại bỏ dòng trống thừa
    - Trả về 1 chuỗi text gọn gàng
    
    Args:
        ocr_json: Dictionary chứa kết quả OCR từ PaddleOCR, có thể có các key:
                  - 'text': str - Text đã được extract
                  - 'ocr_text': str - Text đã được extract (alias)
                  - 'confidence': float
                  - 'lines_processed': int
                  - 'lines_with_text': int
    
    Returns:
        Chuỗi text đã được làm sạch
    """
    # Lấy text từ ocr_json
    text = ocr_json.get('text') or ocr_json.get('ocr_text', '')
    
    if not text or not isinstance(text, str):
        logger.warning("OCR JSON không chứa text hoặc text không hợp lệ")
        return ""
    
    # Bước 1: Nối các dòng bị xuống dòng giữa từ
    # Pattern: ký tự cuối dòng là dấu gạch nối '-' hoặc một số ký tự đặc biệt
    # và dòng tiếp theo bắt đầu bằng chữ cái thường
    lines = text.split('\n')
    cleaned_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()  # Bỏ khoảng trắng bên phải
        
        # Kiểm tra nếu dòng này kết thúc bằng dấu gạch nối và dòng sau bắt đầu bằng chữ thường
        if i < len(lines) - 1:
            next_line = lines[i + 1].lstrip()  # Bỏ khoảng trắng bên trái
            
            # Nối nếu dòng hiện tại kết thúc bằng '-' và dòng sau là chữ
            if line.endswith('-') and next_line and next_line[0].isalnum():
                # Bỏ dấu gạch nối và nối với dòng tiếp theo
                line = line[:-1] + next_line
                i += 2  # Bỏ qua dòng tiếp theo vì đã nối
                continue
            # Nối nếu dòng hiện tại kết thúc bằng khoảng trắng và dòng sau bắt đầu chữ thường
            # (có thể là xuống dòng giữa từ do OCR nhầm)
            elif (line and next_line and 
                  line[-1].isalnum() and next_line[0].islower() and
                  len(line) > 20):  # Chỉ xử lý nếu dòng đủ dài (tránh false positive)
                # Nối với dòng tiếp theo (không thêm space)
                line = line + next_line
                i += 2
                continue
        
        # Thêm dòng vào danh sách (nếu không rỗng)
        if line.strip():
            cleaned_lines.append(line)
        
        i += 1
    
    # Bước 2: Nối lại các dòng
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Bước 3: Loại bỏ nhiều dòng trống liên tiếp (giữ lại tối đa 2 dòng trống)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Bước 4: Loại bỏ khoảng trắng thừa ở đầu/cuối mỗi dòng
    lines = cleaned_text.split('\n')
    lines = [line.strip() for line in lines]
    cleaned_text = '\n'.join(lines)
    
    # Bước 5: Loại bỏ dòng trống ở đầu và cuối
    cleaned_text = cleaned_text.strip()
    
    logger.debug(f"Đã làm sạch OCR text: {len(text)} ký tự → {len(cleaned_text)} ký tự")
    
    return cleaned_text

