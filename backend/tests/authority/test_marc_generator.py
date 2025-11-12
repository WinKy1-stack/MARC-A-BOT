"""
Unit Tests for MARC Field Generator
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.authority.marc_generator import MARCFieldGenerator


class TestMARCFieldGenerator:
    """Test MARC21 Field Generator"""
    
    def test_create_marc21_650_field_mesh(self):
        """Test creating 650 field for MESH"""
        authorities = [{
            'term': 'Machine Learning',
            'authority_id': 'D015996',
            'source': 'MESH',
            'category': 'medical',
            'score': 100.0,
            'metadata': {}
        }]
        
        fields = MARCFieldGenerator.create_marc21_650_field(authorities)
        
        assert len(fields) == 1
        field = fields[0]
        
        assert field['field'] == '650'
        assert field['ind2'] == '2'  # MeSH indicator
        
        # Check subfields
        subfields = field['subfields']
        assert any(sf['code'] == 'a' and sf['value'] == 'Machine Learning' for sf in subfields)
        assert any(sf['code'] == '2' and sf['value'] == 'mesh' for sf in subfields)
        assert any(sf['code'] == '0' and '(DNLM)' in sf['value'] for sf in subfields)
        
    def test_create_marc21_650_field_lcsh(self):
        """Test creating 650 field for LCSH"""
        authorities = [{
            'term': 'Python (Computer program language)',
            'authority_id': 'sh2009007992',
            'source': 'LCSH',
            'category': 'subject',
            'score': 100.0,
            'metadata': {
                'uri': 'http://id.loc.gov/authorities/subjects/sh2009007992'
            }
        }]
        
        fields = MARCFieldGenerator.create_marc21_650_field(authorities)
        
        assert len(fields) == 1
        field = fields[0]
        
        assert field['field'] == '650'
        assert field['ind2'] == '0'  # LCSH indicator
        
        # Check subfields
        subfields = field['subfields']
        assert any(sf['code'] == 'a' for sf in subfields)
        assert any(sf['code'] == '0' and '(DLC)' in sf['value'] for sf in subfields)
        assert any(sf['code'] == '1' for sf in subfields)  # URI
        
    def test_create_marc21_650_field_multiple(self):
        """Test creating multiple 650 fields"""
        authorities = [
            {
                'term': 'Machine Learning',
                'authority_id': 'D015996',
                'source': 'MESH',
                'category': 'medical',
                'score': 100.0,
                'metadata': {}
            },
            {
                'term': 'Artificial Intelligence',
                'authority_id': 'D001185',
                'source': 'MESH',
                'category': 'medical',
                'score': 95.0,
                'metadata': {}
            }
        ]
        
        fields = MARCFieldGenerator.create_marc21_650_field(authorities)
        
        assert len(fields) == 2
        
    def test_create_marc21_650_field_uncontrolled(self):
        """Test creating 650 field for uncontrolled term"""
        authorities = [{
            'term': 'Some random keyword',
            'authority_id': '',
            'source': 'UNCONTROLLED',
            'category': 'uncontrolled',
            'score': 0,
            'metadata': {}
        }]
        
        fields = MARCFieldGenerator.create_marc21_650_field(authorities)
        
        assert len(fields) == 1
        field = fields[0]
        
        assert field['field'] == '650'
        assert field['ind2'] == '4'  # No source specified
        
        # Should have $a but no $0 (no authority ID)
        subfields = field['subfields']
        assert any(sf['code'] == 'a' for sf in subfields)
        assert not any(sf['code'] == '0' for sf in subfields)
        
    def test_create_classification_field_lcc(self):
        """Test creating LCC classification field (050)"""
        field = MARCFieldGenerator.create_marc21_classification_field("QA76.9.A25", "LCC")
        
        assert field['field'] == '050'
        assert field['ind2'] == '4'
        
        subfields = field['subfields']
        assert any(sf['code'] == 'a' and sf['value'] == 'QA76.9.A25' for sf in subfields)
        
    def test_create_classification_field_nlm(self):
        """Test creating NLM classification field (060)"""
        field = MARCFieldGenerator.create_marc21_classification_field("WZ 100", "NLM")
        
        assert field['field'] == '060'
        
        subfields = field['subfields']
        assert any(sf['code'] == 'a' and sf['value'] == 'WZ 100' for sf in subfields)
        
    def test_format_marc_field_display(self):
        """Test formatting MARC field for display"""
        field = {
            'field': '650',
            'ind1': ' ',
            'ind2': '2',
            'subfields': [
                {'code': 'a', 'value': 'Machine Learning'},
                {'code': '2', 'value': 'mesh'},
                {'code': '0', 'value': '(DNLM)D015996'}
            ]
        }
        
        display = MARCFieldGenerator.format_marc_field_display(field)
        
        assert '650' in display
        assert 'Machine Learning' in display
        assert '$a' in display
        assert '$2' in display
        assert '$0' in display
        
    def test_validate_marc_field_valid(self):
        """Test validating a valid MARC field"""
        field = {
            'field': '650',
            'ind1': ' ',
            'ind2': '2',
            'subfields': [
                {'code': 'a', 'value': 'Machine Learning'}
            ]
        }
        
        assert MARCFieldGenerator.validate_marc_field(field) == True
        
    def test_validate_marc_field_invalid_tag(self):
        """Test validating MARC field with invalid tag"""
        field = {
            'field': 'ABC',
            'ind1': ' ',
            'ind2': '2',
            'subfields': [
                {'code': 'a', 'value': 'Test'}
            ]
        }
        
        assert MARCFieldGenerator.validate_marc_field(field) == False
        
    def test_validate_marc_field_no_subfields(self):
        """Test validating MARC field with no subfields"""
        field = {
            'field': '650',
            'ind1': ' ',
            'ind2': '2',
            'subfields': []
        }
        
        assert MARCFieldGenerator.validate_marc_field(field) == False
        
    def test_validate_marc_field_invalid_subfield(self):
        """Test validating MARC field with invalid subfield"""
        field = {
            'field': '650',
            'ind1': ' ',
            'ind2': '2',
            'subfields': [
                {'code': 'ab', 'value': 'Test'}  # Invalid: code must be 1 char
            ]
        }
        
        assert MARCFieldGenerator.validate_marc_field(field) == False


# Sample MARC records for testing
SAMPLE_MARC_RECORDS = [
    {
        'authorities': [
            {
                'term': 'Diabetes Mellitus',
                'authority_id': 'D003920',
                'source': 'MESH',
                'category': 'medical',
                'score': 100.0,
                'metadata': {}
            }
        ],
        'expected_650': {
            'field': '650',
            'ind1': ' ',
            'ind2': '2',
            'subfields': [
                {'code': 'a', 'value': 'Diabetes Mellitus'},
                {'code': '2', 'value': 'mesh'},
                {'code': '0', 'value': '(DNLM)D003920'}
            ]
        }
    }
]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
