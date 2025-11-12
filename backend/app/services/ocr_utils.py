import re
import json
import logging
from typing import Dict, Any
from pathlib import Path
from app.config import Config

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Làm sạch và chuẩn hóa text từ OCR
    
    Args:
        text: Text thô từ OCR
        
    Returns:
        Text đã được làm sạch và chuẩn hóa
    """
    if not text:
        return ""
    
    try:
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special control characters but keep newlines
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize common OCR errors
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O').replace('o', 'O')  # In some contexts
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Ensure UTF-8 encoding
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return text
        
    except Exception as e:
        logger.error("Error cleaning text: %s", e)
        return text


def extract_text_from_result(result) -> str:
    """
    Trích xuất plain text từ kết quả OCR-VL
    
    Args:
        result: Đối tượng kết quả từ OCR-VL
        
    Returns:
        Text đã được trích xuất và làm sạch
    """
    try:
        # PaddleOCR-VL result có attribute text hoặc markdown
        raw_text = ""
        
        if hasattr(result, 'text'):
            raw_text = result.text
        elif hasattr(result, 'markdown'):
            # Strip markdown formatting để lấy plain text
            raw_text = result.markdown
        else:
            logger.warning("Result object has no text or markdown attribute")
            return ""
        
        # Clean and normalize text
        return clean_text(raw_text)
        
    except Exception as e:
        logger.error("Error extracting text from result: %s", e)
        return ""


def extract_sections(text: str) -> Dict[str, str]:
    """
    Trích xuất các phần sơ bộ từ text OCR để chuẩn bị cho MARC21 parsing
    
    Đây là bước trích xuất ban đầu. Việc phân tích chi tiết hơn
    sẽ được thực hiện ở module trích xuất metadata MARC21.
    
    Args:
        text: Text OCR đã được làm sạch
        
    Returns:
        Dictionary chứa các phần đã trích xuất
    """
    sections = {
        'title': '',
        'author': '',
        'publisher': '',
        'isbn': '',
        'year': '',
        'other': text  # Full text as fallback
    }
    
    try:
        # Extract ISBN (10 or 13 digits with optional hyphens)
        isbn_match = re.search(r'ISBN[:\s]*([0-9-]{10,17})', text, re.IGNORECASE)
        if isbn_match:
            sections['isbn'] = isbn_match.group(1).replace('-', '')
        
        # Extract year (4 digits, likely between 1900-2099)
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            sections['year'] = year_match.group(0)
        
        # Extract potential title (usually first line or capitalized text)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and line[0].isupper():
                sections['title'] = line
                break
        
        # Extract publisher (common patterns: "Published by", "Publisher:")
        publisher_match = re.search(
            r'(?:Published by|Publisher|Press)[:\s]+([^\n]+)', 
            text, 
            re.IGNORECASE
        )
        if publisher_match:
            sections['publisher'] = publisher_match.group(1).strip()
        
        # Extract author (common patterns: "by", "Author:")
        author_match = re.search(r'(?:by|Author)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if author_match:
            sections['author'] = author_match.group(1).strip()
            
    except Exception as e:
        logger.error("Error extracting sections: %s", e)
    
    return sections


def save_result_outputs(result: Any, image_id: str) -> Dict[str, str]:
    """
    Lưu kết quả ra file JSON và Markdown
    
    Args:
        result: Đối tượng kết quả từ OCR-VL
        image_id: Mã định danh duy nhất cho ảnh
        
    Returns:
        Dictionary chứa đường dẫn đến các file đã lưu
    """
    output_paths = {}
    
    try:
        output_dir = Config.OUTPUT_FOLDER / image_id
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Save JSON
        if Config.ENABLE_JSON_OUTPUT:
            json_path = output_dir / "result.json"
            
            # Try using built-in save method
            try:
                result.save_to_json(save_path=str(output_dir))
            except AttributeError:
                # Fallback: manually create JSON
                result_dict = {
                    'text': extract_text_from_result(result),
                    'confidence': calculate_confidence(result),
                    'sections': extract_sections(extract_text_from_result(result))
                }
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result_dict, f, ensure_ascii=False, indent=2)
            
            output_paths['json'] = str(json_path)
            logger.info("JSON saved to %s", json_path)
        
        # Save Markdown
        if Config.ENABLE_MARKDOWN_OUTPUT:
            md_path = output_dir / "result.md"
            
            # Try using built-in save method
            try:
                result.save_to_markdown(save_path=str(output_dir))
            except AttributeError:
                # Fallback: manually create markdown
                text = extract_text_from_result(result)
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# OCR Result\n\n{text}\n")
            
            output_paths['markdown'] = str(md_path)
            logger.info("Markdown saved to %s", md_path)
            
    except Exception as e:
        logger.error("Error saving result outputs: %s", e)
    
    return output_paths


def calculate_confidence(result: Any) -> float:
    """
    Tính toán độ tin cậy từ kết quả OCR-VL
    
    Args:
        result: Đối tượng kết quả từ OCR-VL
        
    Returns:
        Điểm độ tin cậy (0.0 đến 1.0)
    """
    try:
        # OCR-VL result có thể có confidence score
        if hasattr(result, 'confidence'):
            return float(result.confidence)
        
        # Hoặc parse từ JSON output
        if hasattr(result, 'to_dict'):
            data = result.to_dict()
            # Extract confidence từ dict nếu có
            return float(data.get('confidence', 0.8))
        
        # Try to calculate from individual scores if available
        if hasattr(result, 'scores') and result.scores:
            scores = result.scores
            if isinstance(scores, list) and scores:
                return sum(scores) / len(scores)
        
        # Default confidence
        return 0.8
        
    except Exception as e:
        logger.error("Error calculating confidence: %s", e)
        return 0.8


def format_for_marc21(ocr_result: Dict) -> Dict:
    """
    Định dạng kết quả OCR để chuẩn bị cho MARC21 metadata parsing
    
    Hàm này chuẩn bị cấu trúc dữ liệu cho bước trích xuất MARC21 tiếp theo.
    
    Args:
        ocr_result: Dictionary chứa kết quả OCR
        
    Returns:
        Dictionary đã được định dạng sẵn sàng cho MARC21 parsing
    """
    text = ocr_result.get('ocr_text', '')
    sections = extract_sections(text)
    
    return {
        'raw_text': text,
        'cleaned_text': clean_text(text),
        'confidence': ocr_result.get('confidence', 0.0),
        'sections': sections,
        'metadata': {
            'image_id': ocr_result.get('image_id', ''),
            'processing_time_ms': ocr_result.get('processing_time_ms', 0),
            'layout_detected': ocr_result.get('layout_detected', False)
        },
        'ready_for_marc21': True
    }
