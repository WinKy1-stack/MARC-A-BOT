"""
Agent 3: ISBN & Publication Year Extractor
Extract ISBN và năm xuất bản - MARC21 Fields 020 & 260
"""
import re
import logging
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ISBNYearExtractor:
    """
    Agent 3: Extract ISBN and publication year from OCR text
    MARC21 Fields: 020 (ISBN), 260 (Publication info)
    """
    
    def extract_isbn(self, ocr_text: str) -> Dict[str, Any]:
        """
        Trích xuất ISBN từ OCR text
        
        Args:
            ocr_text: Raw OCR text (đã được clean)
            
        Returns:
            Dict với format:
            {
                "primary": <isbn 13 ký tự hoặc 10 ký tự> hoặc None,
                "all": [<danh sách isbn tìm được>],
                "confidence": <float 0-1>
            }
            
        Rules:
        - Tìm pattern ISBN (10 hoặc 13 ký tự) gồm số + X/x + - hoặc space
        - Chuẩn hóa: bỏ dấu - và space
        - Ưu tiên 13-digit (prefix 978/979)
        - Kiểm tra check digit ISBN-10 & ISBN-13
        - Loại bỏ duplicate
        """
        if not ocr_text:
            return {
                "primary": None,
                "all": [],
                "confidence": 0.0
            }
        
        # Tìm tất cả các ISBN tiềm năng
        isbns = self._find_isbn_patterns(ocr_text)
        
        if not isbns:
            logger.warning("No ISBN found")
            return {
                "primary": None,
                "all": [],
                "confidence": 0.0
            }
        
        # Validate và chuẩn hóa
        valid_isbns = []
        for isbn in isbns:
            normalized = self._normalize_isbn(isbn)
            if self._validate_isbn(normalized):
                # Chuẩn hóa lại (bỏ dấu -)
                clean_isbn = re.sub(r'[-\s]', '', normalized)
                if clean_isbn not in valid_isbns:
                    valid_isbns.append(clean_isbn)
        
        if not valid_isbns:
            logger.warning("No valid ISBN found")
            return {
                "primary": None,
                "all": [],
                "confidence": 0.0
            }
        
        # Ưu tiên ISBN-13
        isbn_13_list = [isbn for isbn in valid_isbns if len(isbn) == 13]
        primary_isbn = isbn_13_list[0] if isbn_13_list else valid_isbns[0]
        
        # Confidence dựa trên số lượng ISBN hợp lệ và độ dài
        confidence = 0.98 if len(valid_isbns) > 0 else 0.0
        if len(isbn_13_list) > 0:
            confidence = 0.98  # ISBN-13 có confidence cao
        elif len(valid_isbns) > 1:
            confidence = 0.95  # Nhiều ISBN hợp lệ
        
        logger.info(f"Extracted ISBN: primary={primary_isbn}, all={valid_isbns} (confidence: {confidence:.2f})")
        return {
            "primary": primary_isbn,
            "all": valid_isbns,
            "confidence": round(confidence, 2)
        }
    
    def extract_pub_year(self, ocr_text: str) -> Dict[str, Any]:
        """
        Trích xuất năm xuất bản từ OCR text
        
        Args:
            ocr_text: Raw OCR text (đã được clean)
            
        Returns:
            Dict với format:
            {
                "value": <năm dạng int hoặc None>,
                "confidence": <float 0-1>
            }
            
        Rules:
        - Tìm các đoạn chứa: ©, Copyright, First edition, First printing, Published
        - Từ đó trích năm có pattern \\b(19|20)\\d{2}\\b
        - Nếu nhiều năm: ưu tiên năm gần cụm ©, Copyright
        """
        if not ocr_text:
            return {
                "value": None,
                "confidence": 0.0
            }
        
        # Tìm các năm gần keywords
        years = self._find_year_patterns(ocr_text)
        
        if not years:
            logger.warning("No publication year found")
            return {
                "value": None,
                "confidence": 0.0
            }
        
        # Validate và lọc
        valid_years = [y for y in years if self._validate_year(y)]
        
        if not valid_years:
            logger.warning("No valid year found")
            return {
                "value": None,
                "confidence": 0.0
            }
        
        # Ưu tiên năm gần nhất (thường là copyright year)
        result_year = max(valid_years)
        
        # Confidence dựa trên số lượng năm hợp lệ và cách tìm thấy
        confidence = 0.96 if len(valid_years) > 0 else 0.0
        if len(valid_years) > 1:
            confidence = 0.96  # Nhiều năm hợp lệ
        elif '©' in ocr_text or 'copyright' in ocr_text.lower():
            confidence = 0.98  # Có ký hiệu copyright
        
        logger.info(f"Extracted publication year: {result_year} (confidence: {confidence:.2f})")
        return {
            "value": result_year,
            "confidence": round(confidence, 2)
        }
    
    def extract_both(self, ocr_text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Trích xuất cả ISBN và năm xuất bản
        
        Returns:
            Tuple (isbn_dict, year_dict)
        """
        isbn_dict = self.extract_isbn(ocr_text)
        year_dict = self.extract_pub_year(ocr_text)
        return isbn_dict, year_dict
    
    def _find_isbn_patterns(self, text: str) -> list:
        """
        Find all potential ISBN patterns in text
        """
        isbns = []
        
        # Pattern 1: ISBN with hyphens (978-X-XXX-XXXXX-X)
        pattern1 = r'(?:ISBN[:\s-]*)?(\d{3}[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d{1})'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        isbns.extend(matches1)
        
        # Pattern 2: ISBN without hyphens (9781234567890)
        pattern2 = r'(?:ISBN[:\s-]*)?(\d{13})'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        isbns.extend(matches2)
        
        # Pattern 3: ISBN-10 (10 digits)
        pattern3 = r'(?:ISBN[:\s-]*)?(\d{9}[\dXx])'
        matches3 = re.findall(pattern3, text, re.IGNORECASE)
        isbns.extend(matches3)
        
        return isbns
    
    def _normalize_isbn(self, isbn: str) -> str:
        """
        Remove hyphens and spaces, convert to uppercase
        """
        isbn = re.sub(r'[-\s]', '', isbn)
        return isbn.upper()
    
    def _validate_isbn(self, isbn: str) -> bool:
        """
        Validate ISBN check digit
        """
        if not isbn:
            return False
        
        # Remove any non-digit/X characters
        isbn = re.sub(r'[^0-9X]', '', isbn.upper())
        
        if len(isbn) == 13:
            return self._validate_isbn13(isbn)
        elif len(isbn) == 10:
            return self._validate_isbn10(isbn)
        else:
            return False
    
    def _validate_isbn13(self, isbn: str) -> bool:
        """
        Validate ISBN-13 check digit
        """
        if len(isbn) != 13 or not isbn[:12].isdigit():
            return False
        
        # Check prefix (must be 978 or 979)
        if not isbn.startswith(('978', '979')):
            return False
        
        try:
            # Calculate check digit
            total = sum(int(isbn[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
            check = (10 - (total % 10)) % 10
            return check == int(isbn[12])
        except:
            return False
    
    def _validate_isbn10(self, isbn: str) -> bool:
        """
        Validate ISBN-10 check digit
        """
        if len(isbn) != 10:
            return False
        
        try:
            # Calculate check digit
            total = sum(int(isbn[i]) * (10 - i) for i in range(9))
            check_digit = isbn[9]
            check = (11 - (total % 11)) % 11
            
            if check == 10:
                return check_digit == 'X'
            else:
                return check == int(check_digit)
        except:
            return False
    
    def _format_isbn(self, isbn: str) -> str:
        """
        Format ISBN with hyphens
        For ISBN-13: 978-X-XXX-XXXXX-X (simplified format)
        """
        isbn = re.sub(r'[-\s]', '', isbn)
        
        if len(isbn) == 13:
            # Simple format: 978-X-XXXXXX-XX-X
            return f"{isbn[:3]}-{isbn[3]}-{isbn[4:10]}-{isbn[10:12]}-{isbn[12]}"
        elif len(isbn) == 10:
            # ISBN-10: X-XXX-XXXXX-X
            return f"{isbn[0]}-{isbn[1:4]}-{isbn[4:9]}-{isbn[9]}"
        else:
            return isbn
    
    def _find_year_patterns(self, text: str) -> list:
        """
        Find all potential publication years in text
        """
        years = []
        
        # Pattern 1: Near copyright symbol
        pattern1 = r'[©℗Ⓒ]\s*(\d{4})'
        matches1 = re.findall(pattern1, text)
        years.extend([int(y) for y in matches1])
        
        # Pattern 2: Near "Copyright" keyword
        pattern2 = r'copyright[:\s]+(\d{4})'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        years.extend([int(y) for y in matches2])
        
        # Pattern 3: Near "Published" keyword
        pattern3 = r'published[:\s]+(\d{4})'
        matches3 = re.findall(pattern3, text, re.IGNORECASE)
        years.extend([int(y) for y in matches3])
        
        # Pattern 4: Near "Năm xuất bản" (Vietnamese)
        pattern4 = r'năm\s+xuất\s+bản[:\s]*(\d{4})'
        matches4 = re.findall(pattern4, text, re.IGNORECASE)
        years.extend([int(y) for y in matches4])
        
        # Pattern 5: Standalone 4-digit year (last resort)
        if not years:
            pattern5 = r'\b(19\d{2}|20\d{2})\b'
            matches5 = re.findall(pattern5, text)
            years.extend([int(y) for y in matches5])
        
        return years
    
    def _validate_year(self, year: int) -> bool:
        """
        Validate publication year is in reasonable range
        """
        current_year = datetime.now().year
        return 1000 <= year <= current_year + 1


# Example usage
if __name__ == "__main__":
    extractor = ISBNYearExtractor()
    
    test_cases = [
        # Case 1: ISBN-13 with hyphens and copyright
        """
        Machine Learning Handbook
        ISBN: 978-0-123456-78-9
        © 2024 Medical Press
        """,
        
        # Case 2: ISBN-10 without hyphens
        """
        Clinical Guidelines
        ISBN 0123456789
        Published: 2023
        """,
        
        # Case 3: Vietnamese format
        """
        Hướng dẫn điều trị tiểu đường
        ISBN: 978-604-0-12345-6-7
        Năm xuất bản: 2024
        """,
        
        # Case 4: Multiple dates
        """
        Medical Textbook
        ISBN 9780123456789
        First published 2020
        Reprinted 2022
        Copyright © 2024
        """,
        
        # Case 5: No clear keywords
        """
        Advanced Surgery
        9781234567890
        Medical Press 2024
        """,
    ]
    
    print("="*80)
    print("AGENT 3: ISBN & YEAR EXTRACTOR - TEST RESULTS")
    print("="*80)
    
    for i, ocr_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-" * 40)
        isbn, year = extractor.extract_both(ocr_text)
        print(f"ISBN: {isbn}")
        print(f"Year: {year}")
