"""
MARC21 Field Generator
Generate MARC21 650 fields from authority terms
"""
import logging
from typing import List, Dict

from .config import MARC_650_INDICATORS

logger = logging.getLogger(__name__)


class MARCFieldGenerator:
    """Generate MARC21 fields from authority terms"""
    
    @staticmethod
    def create_marc21_650_field(authorities: List[Dict]) -> List[Dict]:
        """
        Create MARC21 650 fields from authority terms
        
        MARC21 650 - Subject Added Entry - Topical Term
        Indicators:
          First - Level of subject (blank = No information provided)
          Second - Thesaurus
            0 = Library of Congress Subject Headings (LCSH)
            1 = LC subject headings for children's literature
            2 = Medical Subject Headings (MeSH)
            3 = National Agricultural Library subject authority file
            4 = Source not specified
            5 = Canadian Subject Headings
            6 = Répertoire de vedettes-matière
            7 = Source specified in subfield $2
        
        Subfields:
          $a - Topical term or geographic name entry element (NR)
          $v - Form subdivision (R)
          $x - General subdivision (R)
          $y - Chronological subdivision (R)
          $z - Geographic subdivision (R)
          $0 - Authority record control number or standard number (R)
          $2 - Source of heading or term (NR)
          
        Args:
            authorities: List of authority term dictionaries
            
        Returns:
            List of MARC21 650 field dictionaries
        """
        marc_fields = []
        
        for authority in authorities:
            source = authority.get('source', 'UNCONTROLLED')
            term = authority.get('term', '')
            authority_id = authority.get('authority_id', '')
            
            if not term:
                logger.warning("Skipping authority with no term")
                continue
                
            # Get indicators based on source
            indicators = MARC_650_INDICATORS.get(source, {'ind1': ' ', 'ind2': '4'})
            
            # Build subfields
            subfields = []
            
            # $a - Topical term (required)
            subfields.append({
                'code': 'a',
                'value': term
            })
            
            # $2 - Source of heading (for non-LCSH/MeSH)
            if source not in ['LCSH', 'LCC'] and source != 'UNCONTROLLED':
                subfields.append({
                    'code': '2',
                    'value': source.lower()
                })
                
            # $0 - Authority record control number
            if authority_id:
                # Format authority ID based on source
                if source == 'MESH':
                    control_number = f"(DNLM){authority_id}"
                elif source in ['LCSH', 'LCC']:
                    control_number = f"(DLC){authority_id}"
                else:
                    control_number = authority_id
                    
                subfields.append({
                    'code': '0',
                    'value': control_number
                })
                
            # Add URI if available in metadata
            metadata = authority.get('metadata', {})
            if 'uri' in metadata and metadata['uri']:
                subfields.append({
                    'code': '1',
                    'value': metadata['uri']
                })
                
            # Create MARC field
            marc_field = {
                'field': '650',
                'ind1': indicators['ind1'],
                'ind2': indicators['ind2'],
                'subfields': subfields
            }
            
            marc_fields.append(marc_field)
            
        logger.info(f"Generated {len(marc_fields)} MARC21 650 fields")
        return marc_fields
        
    @staticmethod
    def create_marc21_classification_field(classification: str, source: str = 'LCC') -> Dict:
        """
        Create MARC21 classification field (050 or 060)
        
        050 - Library of Congress Call Number
        060 - National Library of Medicine Call Number
        
        Args:
            classification: Classification number
            source: Classification source (LCC or NLM)
            
        Returns:
            MARC21 classification field dictionary
        """
        if source == 'NLM':
            # 060 - NLM Call Number
            field = {
                'field': '060',
                'ind1': ' ',
                'ind2': '4',  # No call number assigned by NLM
                'subfields': [
                    {'code': 'a', 'value': classification}
                ]
            }
        else:
            # 050 - LC Call Number
            field = {
                'field': '050',
                'ind1': ' ',
                'ind2': '4',  # No call number assigned by LC
                'subfields': [
                    {'code': 'a', 'value': classification}
                ]
            }
            
        return field
        
    @staticmethod
    def format_marc_field_display(field: Dict) -> str:
        """
        Format MARC field for display
        
        Args:
            field: MARC field dictionary
            
        Returns:
            Formatted string representation
        """
        tag = field.get('field', '???')
        ind1 = field.get('ind1', ' ')
        ind2 = field.get('ind2', ' ')
        
        subfield_str = ' '.join([
            f"${sf['code']} {sf['value']}"
            for sf in field.get('subfields', [])
        ])
        
        return f"{tag} {ind1}{ind2} {subfield_str}"
        
    @staticmethod
    def validate_marc_field(field: Dict) -> bool:
        """
        Validate MARC field structure
        
        Args:
            field: MARC field dictionary
            
        Returns:
            True if valid
        """
        required_keys = ['field', 'ind1', 'ind2', 'subfields']
        
        # Check required keys
        if not all(key in field for key in required_keys):
            logger.error("MARC field missing required keys")
            return False
            
        # Check field tag
        if not field['field'].isdigit() or len(field['field']) != 3:
            logger.error(f"Invalid MARC field tag: {field['field']}")
            return False
            
        # Check indicators
        if len(field['ind1']) != 1 or len(field['ind2']) != 1:
            logger.error("Invalid MARC field indicators")
            return False
            
        # Check subfields
        if not isinstance(field['subfields'], list) or len(field['subfields']) == 0:
            logger.error("MARC field must have at least one subfield")
            return False
            
        for subfield in field['subfields']:
            if 'code' not in subfield or 'value' not in subfield:
                logger.error("Invalid subfield structure")
                return False
            if not isinstance(subfield['code'], str) or len(subfield['code']) != 1:
                logger.error(f"Invalid subfield code: {subfield['code']}")
                return False
                
        return True
