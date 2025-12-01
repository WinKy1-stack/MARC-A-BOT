"""
Agent 2: Author Extractor
Nhận diện và chuẩn hóa tác giả - MARC21 Field 100/700
"""
import re
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthorExtractor:
    """
    Agent 2: Extract and normalize author names from OCR text
    MARC21 Fields: 100 (Main Author), 700 (Additional Authors)
    """
    
    # Keywords indicating author (ordered by specificity - longer patterns first!)
    AUTHOR_KEYWORDS = [
        r'\bco-author[s]?:?\s+',     # Check "co-author" before "author"
        r'\bwritten\s+by\s+',
        r'\bauthor[s]?:?\s+',
        r'\bby\s+',
        r'\btác\s+giả:?\s+',
        r'\bbiên\s+soạn:?\s+',
        r'\bchủ\s+biên:?\s+',
    ]
    
    # Suffixes to handle
    SUFFIXES = ['Jr.', 'Sr.', 'Ph.D.', 'M.D.', 'Dr.', 'Prof.', 
                'GS.', 'PGS.', 'TS.', 'ThS.', 'BS.']
    
    # Publishers/Editors to exclude
    EXCLUDE_PATTERNS = [
        r'publisher',
        r'nhà\s+xuất\s+bản',
        r'editor',
        r'edited\s+by',
        r'press',
    ]
    
    def extract_authors(self, ocr_text: str) -> Dict[str, Any]:
        """
        Trích xuất tác giả từ OCR text
        
        Args:
            ocr_text: Raw OCR text (đã được clean)
            
        Returns:
            Dict với format:
            {
                "main": <tác giả chính dạng 'Họ, Tên'> hoặc None,
                "others": [<tác giả phụ dạng 'Họ, Tên'>, ...],
                "confidence": <float 0-1>
            }
            
        Rules:
        - Tìm tác giả bằng keywords: 'by', 'author', 'written by', 'tác giả', 'biên soạn'
        - Thường nằm 1-2 dòng dưới title
        - Parse danh sách tác giả: tách bởi ';', '&', 'và'
        - Chuẩn hóa format: "John Doe" → "Doe, John"
        - Xử lý suffix: "John Doe Jr.", "Ph.D." (giữ ở phần sau tên)
        - Loại bỏ các dòng liên quan nhà xuất bản, editor
        """
        if not ocr_text or not ocr_text.strip():
            logger.warning("Empty OCR text")
            return {
                "main": None,
                "others": [],
                "confidence": 0.0
            }
        
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        
        authors = []
        confidence = 0.85  # Confidence mặc định
        found_via_keyword = False
        
        # Chiến lược 1: Tìm dòng có keywords tác giả
        for i, line in enumerate(lines):
            # Kiểm tra keywords tác giả
            for keyword in self.AUTHOR_KEYWORDS:
                if re.search(keyword, line, re.IGNORECASE):
                    # Trích xuất tác giả từ dòng này
                    author_text = re.sub(keyword, '', line, flags=re.IGNORECASE).strip()
                    
                    # Kiểm tra không phải publisher/editor
                    if not self._is_excluded(author_text):
                        extracted = self._parse_authors(author_text)
                        authors.extend(extracted)
                        found_via_keyword = True
                    break
        
        # Chiến lược 2: Nếu không tìm thấy, kiểm tra các dòng sau title
        if not authors:
            # Giả định title ở 3 dòng đầu, tác giả ở dòng tiếp theo
            for line in lines[1:6]:
                # Bỏ qua nếu quá ngắn hoặc giống publisher
                if len(line) < 5 or self._is_excluded(line):
                    continue
                
                # Kiểm tra có vẻ như tên người (có chữ in hoa)
                if self._looks_like_name(line):
                    extracted = self._parse_authors(line)
                    authors.extend(extracted)
                    if authors:  # Tìm thấy ít nhất 1 tác giả
                        confidence = 0.7  # Confidence thấp hơn vì không có keyword
                        break
        
        # Validate và chuẩn hóa
        normalized = []
        for author in authors:
            norm = self._normalize_author(author)
            if self._validate_author(norm):
                normalized.append(norm)
        
        # Loại bỏ duplicate
        normalized = list(dict.fromkeys(normalized))
        
        # Xác định tác giả chính và tác giả phụ
        main_author = normalized[0] if normalized else None
        other_authors = normalized[1:] if len(normalized) > 1 else []
        
        # Điều chỉnh confidence dựa trên số lượng và cách tìm thấy
        if not main_author:
            confidence = 0.0
        elif not found_via_keyword:
            confidence = max(0.5, confidence - 0.15)
        elif len(normalized) > 3:
            confidence = min(0.95, confidence + 0.05)  # Nhiều tác giả = confidence cao hơn
        
        logger.info(f"Extracted {len(normalized)} authors: main={main_author}, others={other_authors} (confidence: {confidence:.2f})")
        return {
            "main": main_author,
            "others": other_authors,
            "confidence": round(confidence, 2)
        }
    
    def _parse_authors(self, text: str) -> List[str]:
        """
        Parse multiple authors from text
        Handle separators: ";" and "&" 
        Be careful with commas - they can be part of names (Last, First)
        """
        # First, handle clear separators
        text = text.replace(' and ', '|AUTHOR_SEP|')
        text = text.replace(' & ', '|AUTHOR_SEP|')
        
        # Split by semicolon or our marker
        if ';' in text:
            authors = [a.strip() for a in text.split(';') if a.strip()]
        elif '|AUTHOR_SEP|' in text:
            authors = [a.strip() for a in text.split('|AUTHOR_SEP|') if a.strip()]
        else:
            # Single author
            authors = [text.strip()]
        
        return authors
    
    def _normalize_author(self, author: str) -> str:
        """
        Normalize author name to "Last, First" format
        
        Examples:
        - "John Doe" → "Doe, John"
        - "John M. Doe" → "Doe, John M."
        - "Doe, John Jr." → "Doe, John Jr."
        """
        if not author:
            return ""
        
        # Clean up
        author = author.strip()
        
        # If already in "Last, First" format
        if ',' in author:
            parts = [p.strip() for p in author.split(',', 1)]
            if len(parts) == 2:
                return f"{parts[0]}, {parts[1]}"
            return author
        
        # Parse "First Middle Last" format
        # Handle suffixes
        suffix = ""
        for suf in self.SUFFIXES:
            if author.endswith(suf):
                author = author[:-len(suf)].strip()
                suffix = suf
                break
        
        # Split into parts
        parts = author.split()
        
        if len(parts) == 0:
            return ""
        elif len(parts) == 1:
            # Single name (just last name)
            return parts[0]
        elif len(parts) == 2:
            # First Last
            first, last = parts
            result = f"{last}, {first}"
        else:
            # First Middle... Last
            last = parts[-1]
            first_middle = ' '.join(parts[:-1])
            result = f"{last}, {first_middle}"
        
        # Add suffix back
        if suffix:
            result = f"{result} {suffix}"
        
        return result
    
    def _looks_like_name(self, text: str) -> bool:
        """
        Check if text looks like a person's name
        """
        # Should have capital letters
        if not re.search(r'[A-ZÀ-Ỹ]', text):
            return False
        
        # Should not be too long
        if len(text) > 100:
            return False
        
        # Should not have numbers (except suffixes like "John Doe 2nd")
        if re.search(r'\d{2,}', text):
            return False
        
        # Should have at least 2 words
        words = text.split()
        if len(words) < 2:
            return False
        
        return True
    
    def _is_excluded(self, text: str) -> bool:
        """
        Check if text is publisher/editor (should be excluded)
        """
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _validate_author(self, author: str) -> bool:
        """
        Validate author name
        """
        if not author or len(author) < 2:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-ZÀ-ỹ]', author):
            return False
        
        return True


# Example usage
if __name__ == "__main__":
    extractor = AuthorExtractor()
    
    test_cases = [
        # Case 1: Single author with keyword
        """
        Machine Learning for Healthcare
        by John Doe
        Medical Press, 2024
        """,
        
        # Case 2: Multiple authors
        """
        Clinical Guidelines for Diabetes
        Authors: John Smith; Mary Johnson & Peter Brown
        Published 2024
        """,
        
        # Case 3: Vietnamese authors with titles
        """
        Hướng dẫn lâm sàng điều trị tiểu đường
        Tác giả: PGS.TS. Nguyễn Văn An, TS. Trần Thị Bình
        Nhà xuất bản Y học, 2024
        """,
        
        # Case 4: Author with suffix
        """
        Medical Textbook
        Written by John Doe Jr., Ph.D.
        University Press
        """,
        
        # Case 5: Already in Last, First format
        """
        Advanced Surgery Techniques
        Smith, John M.D.
        Johnson, Mary Ph.D.
        """,
    ]
    
    print("="*80)
    print("AGENT 2: AUTHOR EXTRACTOR - TEST RESULTS")
    print("="*80)
    
    for i, ocr_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-" * 40)
        authors = extractor.extract_authors(ocr_text)
        print(f"Extracted Authors ({len(authors)}):")
        for j, author in enumerate(authors, 1):
            print(f"  {j}. {author}")
