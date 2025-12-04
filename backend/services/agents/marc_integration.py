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
    from .agent_4_keywords import KeywordExtractor
    from .agent_5_doctype import DocumentTypeClassifier
    from .ocr_preprocessing import clean_ocr_text
except ImportError:
    # Fallback for direct execution
    from agent_1_title import TitleExtractor
    from agent_2_author import AuthorExtractor
    from agent_3_isbn_year import ISBNYearExtractor
    from agent_4_keywords import KeywordExtractor
    from agent_5_doctype import DocumentTypeClassifier
    from ocr_preprocessing import clean_ocr_text

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
        self.keyword_extractor = KeywordExtractor()
        self.doctype_classifier = DocumentTypeClassifier()
    
    def run_all_agents(self, ocr_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy tất cả 5 agents từ OCR JSON và trả về dict output
        
        Args:
            ocr_json: Dict từ OCR service, có thể có:
                     - 'text' hoặc 'ocr_text': str
                     - 'confidence': float
                     - các field khác
                     
        Returns:
            Dict output từ tất cả agents, format:
            {
                "title": {"value": "...", "confidence": 0.9},
                "authors": {"main": "...", "others": [], "confidence": 0.85},
                "isbn": {"primary": "...", "all": [...], "confidence": 0.98},
                "pub_year": {"value": 2024, "confidence": 0.96},
                "keywords": [...],
                "subjects": [...],
                "classification": {...},
                "doc_type": {"type": "book", "leader_6_7": "am", "confidence": 0.9}
            }
        """
        logger.info("Chạy tất cả 5 agents...")
        
        # Tiền xử lý OCR text
        ocr_text = clean_ocr_text(ocr_json)
        
        if not ocr_text:
            logger.warning("OCR text rỗng sau khi clean")
            return {}
        
        # Agent 1: Title
        title_result = self.title_extractor.extract_title(ocr_text)
        
        # Agent 2: Authors
        authors_result = self.author_extractor.extract_authors(ocr_text)
        
        # Agent 3: ISBN & Year
        isbn_result = self.isbn_year_extractor.extract_isbn(ocr_text)
        pub_year_result = self.isbn_year_extractor.extract_pub_year(ocr_text)
        
        # Agent 4: Keywords & Subjects
        keywords_list = self.keyword_extractor.extract_keywords(ocr_text, title_result.get("value"))
        
        # Xác định subject_type dựa trên keywords và metadata
        subject_type = 'general'
        if any('medical' in kw['keyword'].lower() or 'medicine' in kw['keyword'].lower() 
               for kw in keywords_list[:5]):
            subject_type = 'medical'
        
        mapping_result = self.keyword_extractor.map_keyword_to_authorities(keywords_list, subject_type)
        
        # Agent 5: Document Type
        metadata = {
            'has_isbn': isbn_result.get("primary") is not None,
            'isbn': isbn_result.get("primary"),
            'has_chapters': 'chapter' in ocr_text.lower(),
            'has_exercises': 'exercise' in ocr_text.lower(),
            'has_volume_issue': 'vol.' in ocr_text.lower() or 'issue' in ocr_text.lower(),
        }
        doc_type_result = self.doctype_classifier.classify_document_type(ocr_text, metadata)
        
        # Tổng hợp kết quả
        agents_output = {
            "title": title_result,
            "authors": authors_result,
            "isbn": isbn_result,
            "pub_year": pub_year_result,
            "keywords": keywords_list,
            "subjects": mapping_result.get("subjects", []),
            "classification": mapping_result.get("classification", {}),
            "doc_type": doc_type_result
        }
        
        logger.info("Hoàn thành chạy tất cả agents")
        return agents_output
    
    def process_ocr_to_marc21(self, ocr_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pipeline đầy đủ: OCR JSON → Agents → MARC21
        
        Args:
            ocr_json: Dict từ OCR service
            
        Returns:
            MARC21 JSON format
        """
        # Chạy tất cả agents
        agents_output = self.run_all_agents(ocr_json)
        
        # Tạo MARC21
        marc21 = self.agents_output_to_marc21(agents_output)
        
        return marc21
    
    def agents_output_to_marc21(self, agents_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dùng output từ 5 agent để tạo cấu trúc MARC21 dạng JSON
        
        Args:
            agents_output: Dict chứa output từ tất cả agents, format:
            {
                "title": {"value": "...", "confidence": 0.9},
                "authors": {"main": "Trần, Xuân Nhĩ", "others": [], "confidence": 0.85},
                "isbn": {"primary": "9786048083328", "all": ["9786048083328"], "confidence": 0.98},
                "pub_year": {"value": 2024, "confidence": 0.96},
                "keywords": [...],
                "subjects": [...],
                "classification": {...},
                "doc_type": {"type": "book", "leader_6_7": "am", "confidence": 0.9}
            }
            
        Returns:
            MARC21 JSON format:
            {
                "leader": "00000nam a2200000 a 4500",
                "fields": [
                    {
                        "tag": "020",
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [{"code": "a", "value": "9786048083328"}]
                    },
                    ...
                ]
            }
        """
        logger.info("Bắt đầu tạo MARC21 từ agents_output...")
        
        fields = []
        
        # Build leader
        leader_6_7 = agents_output.get("doc_type", {}).get("leader_6_7", "am")
        leader = self._build_leader_from_type(leader_6_7)
        
        # 020: ISBN
        isbn_data = agents_output.get("isbn", {})
        if isbn_data.get("primary"):
            fields.append({
                "tag": "020",
                "ind1": " ",
                "ind2": " ",
                "subfields": [
                    {"code": "a", "value": isbn_data["primary"]}
                ]
            })
        
        # 100: Main Author
        authors_data = agents_output.get("authors", {})
        if authors_data.get("main"):
            fields.append({
                "tag": "100",
                "ind1": "1",
                "ind2": " ",
                "subfields": [
                    {"code": "a", "value": authors_data["main"]}
                ]
            })
        
        # 700: Additional Authors
        if authors_data.get("others"):
            for author in authors_data["others"]:
                fields.append({
                    "tag": "700",
                    "ind1": "1",
                    "ind2": " ",
                    "subfields": [
                        {"code": "a", "value": author}
                    ]
                })
        
        # 245: Title
        title_data = agents_output.get("title", {})
        if title_data.get("value"):
            title_field = {
                "tag": "245",
                "ind1": "1" if authors_data.get("main") else "0",
                "ind2": "0",
                "subfields": [
                    {"code": "a", "value": title_data["value"]}
                ]
            }
            fields.append(title_field)
        
        # 260/264: Publication Year
        pub_year_data = agents_output.get("pub_year", {})
        if pub_year_data.get("value"):
            fields.append({
                "tag": "260",
                "ind1": " ",
                "ind2": " ",
                "subfields": [
                    {"code": "c", "value": str(pub_year_data["value"])}
                ]
            })
        
        # 050: LCC Classification
        classification = agents_output.get("classification", {})
        if classification.get("lcc"):
            fields.append({
                "tag": "050",
                "ind1": "0",
                "ind2": "0",
                "subfields": [
                    {"code": "a", "value": classification["lcc"]}
                ]
            })
        
        # 060: NLM Classification
        if classification.get("nlm"):
            fields.append({
                "tag": "060",
                "ind1": "0",
                "ind2": "0",
                "subfields": [
                    {"code": "a", "value": classification["nlm"]}
                ]
            })
        
        # 650: Subject Headings
        subjects = agents_output.get("subjects", [])
        for subject in subjects:
            marc_650 = subject.get("marc_650", {})
            if marc_650:
                fields.append({
                    "tag": "650",
                    "ind1": marc_650.get("ind1", " "),
                    "ind2": marc_650.get("ind2", "0"),
                    "subfields": marc_650.get("subfields", [])
                })
        
        logger.info(f"Đã tạo {len(fields)} fields cho MARC21")
        
        return {
            "leader": leader,
            "fields": fields
        }
    
    def _build_leader_from_type(self, leader_6_7: str) -> str:
        """
        Build MARC21 Leader từ leader_6_7
        
        Args:
            leader_6_7: String 2 ký tự (vd: "am")
            
        Returns:
            Leader string 24 ký tự
        """
        if len(leader_6_7) < 2:
            leader_6_7 = "am"  # Default
        
        type_char = leader_6_7[0]  # Position 6
        level_char = leader_6_7[1] if len(leader_6_7) > 1 else 'm'  # Position 7
        
        # Template: 00000n_ _m a2200000 i 4500
        leader = f"00000n{type_char}{level_char} a2200000 i 4500"
        
        logger.debug(f"Built Leader: {leader} (từ {leader_6_7})")
        return leader
    
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
