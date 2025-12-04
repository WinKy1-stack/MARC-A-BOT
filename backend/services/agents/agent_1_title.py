"""
Agent 1: Title Extractor
Extract tiêu đề sách từ OCR text - MARC21 Field 245
"""
import re
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TitleExtractor:
    """
    Agent 1: Extract title from OCR text
    MARC21 Field: 245 (Title Statement)
    """
    
    # Common library logos/headers to skip
    SKIP_PATTERNS = [
        r'thư viện',
        r'library',
        r'university',
        r'đại học',
        r'trường',
        r'logo',
        r'stamp',
    ]
    
    # Subtitle separators
    SUBTITLE_SEPARATORS = [':', '—', '–', '-']
    
    def extract_title(self, ocr_text: str) -> dict:
        """
        Trích xuất tiêu đề sách từ OCR text
        
        Args:
            ocr_text: Raw OCR text từ document (đã được clean)
            
        Returns:
            Dict với format:
            {
                "value": <tiêu đề sách dạng string>,
                "confidence": <float 0-1>
            }
            
        Rules:
        - Tìm tiêu đề ở dòng đầu tiên hoặc dòng lớn/cô đọng nhất
        - Loại bỏ subtitle nếu có (sau ":" hoặc "-")
        - Xử lý tiêu đề IN HOA TOÀN BỘ → chuyển về Title Case
        - Giữ số hoặc số La Mã (Vol. I, Part 2)
        - Validate: độ dài > 5 ký tự, < 500 ký tự
        """
        if not ocr_text or not ocr_text.strip():
            logger.warning("Empty OCR text")
            return {
                "value": "",
                "confidence": 0.0
            }
        
        # Split vào các dòng
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        
        if not lines:
            return {
                "value": "",
                "confidence": 0.0
            }
        
        # Tìm tiêu đề (bỏ qua headers thư viện)
        title_line = None
        confidence = 0.9  # Confidence mặc định
        
        for i, line in enumerate(lines[:10]):  # Kiểm tra 10 dòng đầu
            # Bỏ qua logo/header thư viện
            if any(re.search(pattern, line.lower()) for pattern in self.SKIP_PATTERNS):
                continue
            
            # Bỏ qua dòng quá ngắn (không phải tiêu đề)
            if len(line) < 5:
                continue
            
            # Bỏ qua dòng chỉ có số hoặc ký tự đặc biệt
            if re.match(r'^[\d\W]+$', line):
                continue
            
            # Đây có thể là tiêu đề
            title_line = line
            # Confidence giảm dần nếu ở dòng sau
            if i > 0:
                confidence = max(0.7, 0.9 - (i * 0.05))
            break
        
        if not title_line:
            # Fallback: dùng dòng đầu tiên không rỗng
            title_line = lines[0] if lines else ""
            confidence = 0.5  # Confidence thấp vì không chắc chắn
        
        # Chuẩn hóa tiêu đề
        title = self._normalize_title(title_line)
        
        # Validate và điều chỉnh confidence
        if not self._validate_title(title):
            logger.warning(f"Invalid title: {title}")
            return {
                "value": "",
                "confidence": 0.0
            }
        
        # Giảm confidence nếu độ dài không hợp lý
        if len(title) < 10 or len(title) > 200:
            confidence *= 0.8
        
        logger.info(f"Extracted title: {title} (confidence: {confidence:.2f})")
        return {
            "value": title,
            "confidence": round(confidence, 2)
        }
    
    def _normalize_title(self, title: str) -> str:
        """
        Normalize title text
        """
        # Remove leading/trailing whitespace
        title = title.strip()
        
        # Handle subtitle (remove after separator)
        for separator in self.SUBTITLE_SEPARATORS:
            if separator in title:
                # Keep only main title
                parts = title.split(separator, 1)
                title = parts[0].strip()
                break
        
        # Handle ALL CAPS -> Title Case
        if title.isupper() and len(title) > 10:
            title = title.title()
        
        # Clean up whitespace (multiple spaces -> single space)
        title = re.sub(r'\s+', ' ', title)
        
        # Handle special characters (normalize quotes)
        title = title.replace('"', '"').replace('"', '"')
        title = title.replace(''', "'").replace(''', "'")
        
        # Remove trailing punctuation (except period for abbreviations)
        title = re.sub(r'[,;:!?]+$', '', title)
        
        return title.strip()
    
    def _validate_title(self, title: str) -> bool:
        """
        Validate title meets requirements
        """
        if not title:
            return False
        
        # Length check: 5 < length < 500
        if len(title) < 5 or len(title) > 500:
            return False
        
        # Must contain at least some letters
        if not re.search(r'[a-zA-ZÀ-ỹ]', title):
            return False
        
        return True
    
    def extract_title_with_subtitle(self, ocr_text: str) -> dict:
        """
        Extract title and subtitle separately
        
        Returns:
            {
                'main_title': str,
                'subtitle': str,
                'full_title': str
            }
        """
        if not ocr_text or not ocr_text.strip():
            return {'main_title': '', 'subtitle': '', 'full_title': ''}
        
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        
        # Find title line
        title_line = None
        for line in lines[:10]:
            if any(re.search(pattern, line.lower()) for pattern in self.SKIP_PATTERNS):
                continue
            if len(line) >= 5:
                title_line = line
                break
        
        if not title_line:
            return {'main_title': '', 'subtitle': '', 'full_title': ''}
        
        # Split main title and subtitle
        main_title = title_line
        subtitle = ""
        
        for separator in self.SUBTITLE_SEPARATORS:
            if separator in title_line:
                parts = title_line.split(separator, 1)
                main_title = parts[0].strip()
                subtitle = parts[1].strip() if len(parts) > 1 else ""
                break
        
        # Normalize both
        main_title = self._normalize_title(main_title)
        subtitle = self._normalize_title(subtitle) if subtitle else ""
        
        return {
            'main_title': main_title,
            'subtitle': subtitle,
            'full_title': f"{main_title}: {subtitle}" if subtitle else main_title
        }


# Example usage
if __name__ == "__main__":
    extractor = TitleExtractor()
    
    # Test cases
    test_cases = [
        # Case 1: Simple title
        """
        Thư viện Đại học Y Dược TP.HCM
        
        Machine Learning for Healthcare
        
        By John Doe
        2024
        """,
        
        # Case 2: ALL CAPS with subtitle
        """
        CLINICAL GUIDELINES FOR DIABETES MELLITUS: A COMPREHENSIVE REVIEW
        
        Published by Medical Press
        """,
        
        # Case 3: Title with special characters
        """
        The Doctor's Guide to "Modern Medicine"
        A Practical Approach
        """,
        
        # Case 4: Title with volume
        """
        History of Ancient Rome - Vol. I: The Republic
        """,
    ]
    
    print("="*80)
    print("AGENT 1: TITLE EXTRACTOR - TEST RESULTS")
    print("="*80)
    
    for i, ocr_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-" * 40)
        
        # Extract simple title
        title = extractor.extract_title(ocr_text)
        print(f"Simple Title: {title}")
        
        # Extract with subtitle
        detailed = extractor.extract_title_with_subtitle(ocr_text)
        print(f"Main Title: {detailed['main_title']}")
        print(f"Subtitle: {detailed['subtitle']}")
        print(f"Full Title: {detailed['full_title']}")
