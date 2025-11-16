"""
Agent 2: Author Extractor
Nhận diện và chuẩn hóa tác giả - MARC21 Field 100/700
"""
import re
import logging
from typing import List

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
    
    def extract_authors(self, ocr_text: str) -> List[str]:
        """
        Extract and normalize author names from OCR text
        
        Args:
            ocr_text: Raw OCR text
            
        Returns:
            List of normalized author names in format "Last, First"
            
        Rules:
        - Find author near keywords "by", "Author", "Written by"
        - Usually below title
        - Handle multiple authors (separated by ";" or "&")
        - Normalize: "John Doe" → "Doe, John"
        - Handle middle name/initial
        - Handle suffixes (Jr., Sr., Ph.D.)
        - Exclude publishers, editors
        - Validate: non-empty, at least 2 characters
        """
        if not ocr_text or not ocr_text.strip():
            logger.warning("Empty OCR text")
            return []
        
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        
        authors = []
        
        # Strategy 1: Find lines with author keywords
        for i, line in enumerate(lines):
            # Check for author keywords
            for keyword in self.AUTHOR_KEYWORDS:
                if re.search(keyword, line, re.IGNORECASE):
                    # Extract author from this line
                    author_text = re.sub(keyword, '', line, flags=re.IGNORECASE).strip()
                    
                    # Check if it's not a publisher/editor
                    if not self._is_excluded(author_text):
                        extracted = self._parse_authors(author_text)
                        authors.extend(extracted)
                    break
        
        # Strategy 2: If no authors found, check lines after title
        if not authors:
            # Assume title is in first 3 lines, author in next 3 lines
            for line in lines[1:6]:
                # Skip if too short or looks like publisher
                if len(line) < 5 or self._is_excluded(line):
                    continue
                
                # Check if looks like a name (has capital letters)
                if self._looks_like_name(line):
                    extracted = self._parse_authors(line)
                    authors.extend(extracted)
                    if authors:  # Found at least one author
                        break
        
        # Validate and normalize
        normalized = []
        for author in authors:
            norm = self._normalize_author(author)
            if self._validate_author(norm):
                normalized.append(norm)
        
        # Remove duplicates
        normalized = list(dict.fromkeys(normalized))
        
        logger.info(f"Extracted {len(normalized)} authors: {normalized}")
        return normalized
    
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
