"""
MARC Integration: Combine all 5 agents into complete MARC21 record
Kết hợp output từ 5 agents thành bản ghi MARC21 hoàn chỉnh
"""
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import all agents
try:
    from .agent_1_title import TitleExtractor
    from .agent_2_author import AuthorExtractor
    from .agent_3_isbn_year import ISBNYearExtractor
    from .agent_5_doctype import DocumentTypeClassifier
except ImportError:
    # Fallback for direct execution
    from agent_1_title import TitleExtractor
    from agent_2_author import AuthorExtractor
    from agent_3_isbn_year import ISBNYearExtractor
    from agent_5_doctype import DocumentTypeClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MARCIntegration:
    """
    Integrate outputs from all 5 agents into MARC21 format
    """
    
    def __init__(self):
        self.title_extractor = TitleExtractor()
        self.author_extractor = AuthorExtractor()
        self.isbn_year_extractor = ISBNYearExtractor()
        self.doctype_classifier = DocumentTypeClassifier()
    
    def agents_output_to_marc21(
        self, 
        ocr_text: str,
        keywords: List[str] = None,
        classification_frameworks: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Main integration function: Combine all agents into MARC21
        
        Args:
            ocr_text: Raw OCR text from document
            keywords: Controlled keywords from Agent 4 (optional, will use authority service)
            classification_frameworks: Classification numbers from Agent 4 (optional)
            
        Returns:
            MARC21 record dict with all fields:
            {
                'leader': str,
                'control_fields': {
                    '001': str,  # Control number
                    '003': str,  # Control number identifier
                    '005': str,  # Date and time of latest transaction
                    '008': str,  # Fixed-length data elements
                },
                'data_fields': {
                    '020': [],  # ISBN
                    '050': [],  # LCC classification
                    '060': [],  # NLM classification
                    '100': [],  # Main author
                    '245': [],  # Title
                    '260': [],  # Publication info
                    '650': [],  # Subject headings
                    '700': [],  # Additional authors
                }
            }
        """
        logger.info("Starting MARC21 integration...")
        
        # Extract data from all agents
        agents_data = self._extract_all_agents(ocr_text)
        
        # Build MARC21 record
        marc_record = {
            'leader': self._build_leader(agents_data),
            'control_fields': self._build_control_fields(agents_data),
            'data_fields': self._build_data_fields(agents_data, keywords, classification_frameworks)
        }
        
        logger.info("MARC21 integration completed")
        return marc_record
    
    def _extract_all_agents(self, ocr_text: str) -> Dict[str, Any]:
        """
        Run all 5 agents and collect results
        """
        logger.info("Extracting data from all agents...")
        
        # Agent 1: Title
        title = self.title_extractor.extract_title(ocr_text)
        title_with_subtitle = self.title_extractor.extract_title_with_subtitle(ocr_text)
        
        # Agent 2: Authors
        authors = self.author_extractor.extract_authors(ocr_text)
        
        # Agent 3: ISBN & Year
        isbn, pub_year = self.isbn_year_extractor.extract_both(ocr_text)
        
        # Agent 5: Document Type
        metadata = {
            'has_isbn': isbn is not None,
            'has_chapters': 'chapter' in ocr_text.lower(),
            'has_exercises': 'exercise' in ocr_text.lower(),
            'has_volume_issue': 'vol.' in ocr_text.lower() or 'issue' in ocr_text.lower(),
        }
        doc_type_details = self.doctype_classifier.classify_with_details(ocr_text, metadata)
        
        return {
            'title': title,
            'title_with_subtitle': title_with_subtitle,
            'authors': authors,
            'isbn': isbn,
            'pub_year': pub_year,
            'doc_type': doc_type_details['type'],
            'doc_type_confidence': doc_type_details['confidence'],
            'doc_type_marc_code': self.doctype_classifier.get_marc_leader_code(doc_type_details['type'])
        }
    
    def _build_leader(self, agents_data: Dict[str, Any]) -> str:
        """
        Build MARC21 Leader (24 characters)
        
        Format: 00000n_m_a2200000_i_4500
        Positions:
        - 00-04: Record length (00000 = system generated)
        - 05: Record status (n = new)
        - 06: Type of record (a = language material)
        - 07: Bibliographic level (m = monograph)
        - 08: Type of control (blank)
        - 09: Character coding scheme (a = UCS/Unicode)
        - 10: Indicator count (2)
        - 11: Subfield code count (2)
        - 12-16: Base address of data (00000 = system generated)
        - 17: Encoding level (blank = full level)
        - 18: Descriptive cataloging form (i = ISBD)
        - 19: Multipart resource record level (blank)
        - 20: Length of length-of-field portion (4)
        - 21: Length of starting-character-position portion (5)
        - 22: Length of implementation-defined portion (0)
        - 23: Undefined (0)
        """
        type_code = agents_data.get('doc_type_marc_code', 'a')
        
        # Basic leader template
        leader = f"00000n{type_code}m a2200000 i 4500"
        
        logger.info(f"Built Leader: {leader}")
        return leader
    
    def _build_control_fields(self, agents_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Build MARC21 control fields (001, 003, 005, 008)
        """
        now = datetime.now()
        
        control_fields = {
            '001': f"MARCABOT{now.strftime('%Y%m%d%H%M%S')}",  # Control number
            '003': 'MARCABOT',  # Control number identifier
            '005': now.strftime('%Y%m%d%H%M%S.0'),  # Timestamp
            '008': self._build_008_field(agents_data, now)  # Fixed-length data
        }
        
        logger.info(f"Built control fields: {list(control_fields.keys())}")
        return control_fields
    
    def _build_008_field(self, agents_data: Dict[str, Any], now: datetime) -> str:
        """
        Build 008 field (40 characters)
        
        Positions:
        - 00-05: Date entered (YYMMDD)
        - 06: Type of date (s = single date)
        - 07-10: Date 1 (publication year)
        - 11-14: Date 2 (blank)
        - 15-17: Place of publication (xxx = unknown)
        - 18-34: Various (blank for simplicity)
        - 35-37: Language (eng = English)
        - 38: Modified record (blank)
        - 39: Cataloging source (d = other)
        """
        date_entered = now.strftime('%y%m%d')
        pub_year = agents_data.get('pub_year', '    ')
        pub_year_str = str(pub_year) if pub_year else '    '
        
        field_008 = (
            f"{date_entered}"     # 00-05: Date entered
            f"s"                  # 06: Type of date
            f"{pub_year_str}"     # 07-10: Date 1
            f"    "               # 11-14: Date 2
            f"xx "                # 15-17: Place
            f"                "   # 18-34: Various
            f"eng"                # 35-37: Language
            f" "                  # 38: Modified
            f"d"                  # 39: Source
        )
        
        return field_008
    
    def _build_data_fields(
        self,
        agents_data: Dict[str, Any],
        keywords: List[str] = None,
        classification_frameworks: List[Dict[str, str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build MARC21 data fields from agents data
        """
        data_fields = {}
        
        # 020: ISBN
        if agents_data.get('isbn'):
            data_fields['020'] = [{
                'ind1': ' ',
                'ind2': ' ',
                'subfields': [
                    {'a': agents_data['isbn']}
                ]
            }]
        
        # 050: LCC Classification
        if classification_frameworks:
            lcc_numbers = [cf['number'] for cf in classification_frameworks if cf.get('type') == 'LCC']
            if lcc_numbers:
                data_fields['050'] = [{
                    'ind1': '0',
                    'ind2': '0',
                    'subfields': [
                        {'a': num}
                    ]
                } for num in lcc_numbers]
        
        # 060: NLM Classification
        if classification_frameworks:
            nlm_numbers = [cf['number'] for cf in classification_frameworks if cf.get('type') == 'NLM']
            if nlm_numbers:
                data_fields['060'] = [{
                    'ind1': '0',
                    'ind2': '0',
                    'subfields': [
                        {'a': num}
                    ]
                } for num in nlm_numbers]
        
        # 100: Main Author
        authors = agents_data.get('authors', [])
        if authors:
            data_fields['100'] = [{
                'ind1': '1',
                'ind2': ' ',
                'subfields': [
                    {'a': authors[0]}
                ]
            }]
        
        # 245: Title
        if agents_data.get('title'):
            title_field = {
                'ind1': '1' if authors else '0',  # Title added entry
                'ind2': '0',  # No nonfiling characters
                'subfields': [
                    {'a': agents_data['title']}
                ]
            }
            
            # Add subtitle if available
            if agents_data.get('title_with_subtitle', {}).get('subtitle'):
                title_field['subfields'].append({
                    'b': agents_data['title_with_subtitle']['subtitle']
                })
            
            data_fields['245'] = [title_field]
        
        # 260: Publication
        if agents_data.get('pub_year'):
            data_fields['260'] = [{
                'ind1': ' ',
                'ind2': ' ',
                'subfields': [
                    {'c': str(agents_data['pub_year'])}
                ]
            }]
        
        # 650: Subject Headings (from Agent 4)
        if keywords:
            data_fields['650'] = [{
                'ind1': ' ',
                'ind2': '0',  # LCSH
                'subfields': [
                    {'a': keyword}
                ]
            } for keyword in keywords]
        
        # 700: Additional Authors
        if len(authors) > 1:
            data_fields['700'] = [{
                'ind1': '1',
                'ind2': ' ',
                'subfields': [
                    {'a': author}
                ]
            } for author in authors[1:]]
        
        logger.info(f"Built data fields: {list(data_fields.keys())}")
        return data_fields
    
    def format_marc_display(self, marc_record: Dict[str, Any]) -> str:
        """
        Format MARC record for human-readable display
        """
        output = []
        output.append("="*80)
        output.append("MARC21 RECORD")
        output.append("="*80)
        
        # Leader
        output.append(f"\nLEADER: {marc_record['leader']}")
        
        # Control fields
        output.append("\n--- CONTROL FIELDS ---")
        for tag, value in marc_record['control_fields'].items():
            output.append(f"{tag}: {value}")
        
        # Data fields
        output.append("\n--- DATA FIELDS ---")
        for tag, fields in marc_record['data_fields'].items():
            for field in fields:
                ind1 = field.get('ind1', ' ')
                ind2 = field.get('ind2', ' ')
                subfields_str = ' '.join(
                    f"${code}{value}" 
                    for subfield in field.get('subfields', [])
                    for code, value in subfield.items()
                )
                output.append(f"{tag} {ind1}{ind2} {subfields_str}")
        
        output.append("="*80)
        return '\n'.join(output)


# Example usage
if __name__ == "__main__":
    integration = MARCIntegration()
    
    # Test case: Medical textbook
    ocr_text = """
    Introduction to Clinical Medicine
    Third Edition
    
    By Dr. John Smith, MD, PhD
    Co-author: Dr. Jane Doe, MD
    
    ISBN: 978-0-123-45678-9
    
    Published by Medical Press
    Copyright © 2024
    
    Chapter 1: Introduction to Medicine
    Chapter 2: Patient Assessment
    Chapter 3: Diagnostic Methods
    
    Exercises at the end of each chapter
    """
    
    # Mock keywords from Agent 4
    keywords = [
        "Clinical Medicine",
        "Medical Education",
        "Patient Care"
    ]
    
    # Mock classification frameworks from Agent 4
    classification_frameworks = [
        {'type': 'LCC', 'number': 'R729'},
        {'type': 'NLM', 'number': 'W 18'}
    ]
    
    # Generate MARC21 record
    print("Processing document...")
    marc_record = integration.agents_output_to_marc21(
        ocr_text=ocr_text,
        keywords=keywords,
        classification_frameworks=classification_frameworks
    )
    
    # Display result
    print("\n")
    print(integration.format_marc_display(marc_record))
    
    # Also print raw JSON for debugging
    print("\n--- RAW JSON ---")
    import json
    print(json.dumps(marc_record, indent=2, ensure_ascii=False))
