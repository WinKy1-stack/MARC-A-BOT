"""
Agent 5: Document Type Classifier
Phân loại loại tài liệu - MARC21 Leader byte 6-7
"""
import re
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentTypeClassifier:
    """
    Agent 5: Classify document type from OCR text
    MARC21 Leader: byte 6-7 (Type of Record)
    """
    
    # Type indicators
    TYPE_INDICATORS = {
        'book': {
            'keywords': ['isbn', 'chapter', 'edition', 'hardcover', 'paperback'],
            'patterns': [r'\bchapter\s+\d+\b', r'\bedition\b', r'\bisbn\b'],
            'weight': 1.0
        },
        'journal': {
            'keywords': ['volume', 'issue', 'vol.', 'no.', 'issn', 'quarterly', 'monthly'],
            'patterns': [r'vol\.\s*\d+', r'issue\s+\d+', r'no\.\s*\d+'],
            'weight': 1.2
        },
        'magazine': {
            'keywords': ['magazine', 'monthly', 'weekly', 'cover story', 'subscription'],
            'patterns': [r'\d{1,2}\s+\w+\s+\d{4}'],  # Date format
            'weight': 0.9
        },
        'textbook': {
            'keywords': ['textbook', 'exercise', 'homework', 'problem set', 'instructor', 'student'],
            'patterns': [r'exercise\s+\d+', r'chapter\s+\d+:\s+exercises'],
            'weight': 1.1
        },
        'proceeding': {
            'keywords': ['conference', 'proceedings', 'symposium', 'workshop', 'congress'],
            'patterns': [r'\d+(st|nd|rd|th)\s+\w+\s+conference', r'proceedings\s+of'],
            'weight': 1.3
        },
        'thesis': {
            'keywords': ['thesis', 'dissertation', 'master', 'phd', 'doctoral', 'supervisor'],
            'patterns': [r'thesis\s+submitted', r'dissertation\s+presented'],
            'weight': 1.2
        },
        'report': {
            'keywords': ['report', 'technical report', 'research report', 'annual report'],
            'patterns': [r'report\s+no\.', r'technical\s+report'],
            'weight': 1.0
        }
    }
    
    def classify_document_type(self, ocr_text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Classify document type from OCR text and metadata
        
        Args:
            ocr_text: Raw OCR text
            metadata: Optional metadata (e.g., {'has_isbn': True, 'has_chapters': True})
            
        Returns:
            Document type: 'book', 'journal', 'magazine', 'textbook', 'proceeding', 'thesis', 'report'
            
        Rules:
        - Check keyword indicators (ISBN → book, Vol. → journal)
        - Check format/layout patterns
        - Use metadata if available
        - Default fallback: 'book'
        """
        if not ocr_text or not ocr_text.strip():
            logger.warning("Empty OCR text, defaulting to 'book'")
            return 'book'
        
        # Calculate scores for each type
        scores = {}
        text_lower = ocr_text.lower()
        
        for doc_type, indicators in self.TYPE_INDICATORS.items():
            score = 0
            
            # Check keywords
            for keyword in indicators['keywords']:
                if keyword in text_lower:
                    score += 1
            
            # Check patterns
            for pattern in indicators['patterns']:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            
            # Apply weight
            scores[doc_type] = score * indicators['weight']
        
        # Check metadata
        if metadata:
            if metadata.get('has_isbn'):
                scores['book'] = scores.get('book', 0) + 2
                scores['textbook'] = scores.get('textbook', 0) + 1
            
            if metadata.get('has_issn'):
                scores['journal'] = scores.get('journal', 0) + 3
                scores['magazine'] = scores.get('magazine', 0) + 2
            
            if metadata.get('has_chapters'):
                scores['book'] = scores.get('book', 0) + 1
                scores['textbook'] = scores.get('textbook', 0) + 2
            
            if metadata.get('has_exercises'):
                scores['textbook'] = scores.get('textbook', 0) + 3
            
            if metadata.get('has_volume_issue'):
                scores['journal'] = scores.get('journal', 0) + 3
        
        # Get type with highest score
        if scores:
            result = max(scores.items(), key=lambda x: x[1])
            doc_type = result[0]
            confidence = result[1]
            
            # If confidence is too low, default to book
            if confidence < 1.0:
                logger.info(f"Low confidence ({confidence}), defaulting to 'book'")
                return 'book'
            
            logger.info(f"Classified as '{doc_type}' with confidence {confidence}")
            return doc_type
        else:
            # Default
            logger.info("No indicators found, defaulting to 'book'")
            return 'book'
    
    def classify_with_details(self, ocr_text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify with detailed scores for all types
        
        Returns:
            {
                'type': str,
                'confidence': float,
                'scores': dict,
                'indicators_found': list
            }
        """
        if not ocr_text or not ocr_text.strip():
            return {
                'type': 'book',
                'confidence': 0,
                'scores': {},
                'indicators_found': []
            }
        
        scores = {}
        indicators_found = []
        text_lower = ocr_text.lower()
        
        # Calculate scores
        for doc_type, indicators in self.TYPE_INDICATORS.items():
            score = 0
            type_indicators = []
            
            # Check keywords
            for keyword in indicators['keywords']:
                if keyword in text_lower:
                    score += 1
                    type_indicators.append(f"keyword:{keyword}")
            
            # Check patterns
            for pattern in indicators['patterns']:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches)
                    type_indicators.append(f"pattern:{pattern}")
            
            # Apply weight
            scores[doc_type] = score * indicators['weight']
            
            if type_indicators:
                indicators_found.append({
                    'type': doc_type,
                    'indicators': type_indicators
                })
        
        # Apply metadata
        if metadata:
            if metadata.get('has_isbn'):
                scores['book'] = scores.get('book', 0) + 2
                scores['textbook'] = scores.get('textbook', 0) + 1
            
            if metadata.get('has_issn'):
                scores['journal'] = scores.get('journal', 0) + 3
            
            if metadata.get('has_chapters'):
                scores['textbook'] = scores.get('textbook', 0) + 2
        
        # Get best match
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            doc_type = best_type[0]
            confidence = best_type[1]
            
            # Fallback if confidence too low
            if confidence < 1.0:
                doc_type = 'book'
                confidence = 0.5
        else:
            doc_type = 'book'
            confidence = 0
        
        return {
            'type': doc_type,
            'confidence': confidence,
            'scores': scores,
            'indicators_found': indicators_found
        }
    
    def get_marc_leader_code(self, doc_type: str) -> str:
        """
        Get MARC21 Leader Type of Record code
        
        Returns:
            Type of Record code for Leader position 6
        """
        codes = {
            'book': 'a',        # Language material (books)
            'journal': 'a',     # Language material (serials use 's' in position 7)
            'magazine': 'a',    # Language material
            'textbook': 'a',    # Language material
            'proceeding': 'a',  # Language material
            'thesis': 'a',      # Language material
            'report': 'a',      # Language material
            'map': 'e',         # Cartographic material
            'music': 'c',       # Notated music
            'sound': 'i',       # Nonmusical sound recording
            'video': 'g',       # Projected medium
        }
        return codes.get(doc_type, 'a')


# Example usage
if __name__ == "__main__":
    classifier = DocumentTypeClassifier()
    
    test_cases = [
        # Case 1: Textbook
        ("""
        Introduction to Machine Learning
        Third Edition
        ISBN: 978-0-123456-78-9
        
        Chapter 1: Introduction
        Chapter 2: Linear Regression
        
        Exercises at the end of each chapter
        Includes problem sets and solutions for instructors
        """, {'has_isbn': True, 'has_chapters': True, 'has_exercises': True}),
        
        # Case 2: Journal
        ("""
        Journal of Medical Research
        Vol. 45, No. 3, July 2024
        ISSN: 1234-5678
        
        Original Articles
        Research Papers
        """, {'has_issn': True, 'has_volume_issue': True}),
        
        # Case 3: Conference Proceeding
        ("""
        Proceedings of the 15th International Conference on Machine Learning
        IEEE Computer Society
        June 15-17, 2024
        San Francisco, USA
        """, None),
        
        # Case 4: Simple book
        ("""
        The Great Gatsby
        by F. Scott Fitzgerald
        ISBN: 978-0-7432-7356-5
        Paperback Edition
        """, {'has_isbn': True}),
        
        # Case 5: Thesis
        ("""
        Machine Learning Approaches for Medical Diagnosis
        A Dissertation Presented to the Faculty of Computer Science
        In Partial Fulfillment of the Requirements for the Degree of Doctor of Philosophy
        
        Supervisor: Prof. John Doe
        PhD Candidate: Jane Smith
        """, None),
    ]
    
    print("="*80)
    print("AGENT 5: DOCUMENT TYPE CLASSIFIER - TEST RESULTS")
    print("="*80)
    
    for i, (ocr_text, metadata) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-" * 40)
        
        # Simple classification
        doc_type = classifier.classify_document_type(ocr_text, metadata)
        print(f"Type: {doc_type}")
        
        # Detailed classification
        details = classifier.classify_with_details(ocr_text, metadata)
        print(f"Confidence: {details['confidence']:.2f}")
        print(f"Scores: {details['scores']}")
        
        # MARC code
        marc_code = classifier.get_marc_leader_code(doc_type)
        print(f"MARC Leader Type: {marc_code}")
