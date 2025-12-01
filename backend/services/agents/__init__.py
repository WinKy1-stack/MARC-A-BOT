"""
OCR Extraction Agents Package
5 agents để trích xuất metadata từ OCR text thành MARC21

Agents:
- Agent 1: Title Extractor (MARC 245)
- Agent 2: Author Extractor (MARC 100/700)
- Agent 3: ISBN & Year Extractor (MARC 020/260)
- Agent 4: Keywords Extractor (MARC 650) - see examples/agent_4_integration.py
- Agent 5: Document Type Classifier (MARC Leader)

Integration:
- MARCIntegration: Combine all agents into complete MARC21 record
"""

from .agent_1_title import TitleExtractor
from .agent_2_author import AuthorExtractor
from .agent_3_isbn_year import ISBNYearExtractor
from .agent_4_keywords import KeywordExtractor
from .agent_5_doctype import DocumentTypeClassifier
from .marc_integration import MARCIntegration
from .ocr_preprocessing import clean_ocr_text

__all__ = [
    'TitleExtractor',
    'AuthorExtractor',
    'ISBNYearExtractor',
    'KeywordExtractor',
    'DocumentTypeClassifier',
    'MARCIntegration',
    'clean_ocr_text',
]
