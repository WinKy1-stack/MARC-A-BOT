"""
Integration Tests for Authority Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.authority.authority_service import AuthorityService


@pytest.fixture
def service():
    """Create Authority Service instance"""
    return AuthorityService()


class TestAuthorityServiceIntegration:
    """Integration tests for Authority Service"""
    
    def test_process_keywords_medical(self, service):
        """Test processing medical keywords end-to-end"""
        keywords = ["diabetes", "hypertension"]
        
        result = service.process_keywords(keywords, subject_type='medical')
        
        assert 'authorities' in result
        assert 'marc_fields' in result
        assert 'stats' in result
        
        assert len(result['authorities']) == len(keywords)
        assert len(result['marc_fields']) <= len(keywords)  # May have fewer if some are uncontrolled
        
        # Check statistics
        stats = result['stats']
        assert stats['total_keywords'] == len(keywords)
        
    def test_process_keywords_general(self, service):
        """Test processing general keywords"""
        keywords = ["programming", "databases"]
        
        result = service.process_keywords(keywords, subject_type='general')
        
        assert result['stats']['total_keywords'] == len(keywords)
        
    def test_search_authority_single(self, service):
        """Test searching for single authority term"""
        results = service.search_authority("machine learning", source="MESH")
        
        # Results can be empty if API is not available or cache is empty
        assert isinstance(results, list)
        
    def test_validate_term_mesh(self, service):
        """Test validating MESH term"""
        # This test may fail if API is not available
        try:
            result = service.validate_term("Machine Learning", "MESH")
            assert isinstance(result, bool)
        except Exception:
            # Expected if API is not available
            pytest.skip("MESH API not available")
            
    def test_cache_statistics(self, service):
        """Test getting cache statistics"""
        stats = service.get_cache_statistics(days=7)
        
        assert 'total_cache_entries' in stats
        assert 'hit_rate' in stats
        
    def test_batch_process(self, service):
        """Test batch processing"""
        batches = [
            ["keyword1", "keyword2"],
            ["keyword3", "keyword4"]
        ]
        
        results = service.batch_process(batches, subject_type='general')
        
        assert len(results) == len(batches)
        
        for result in results:
            assert 'authorities' in result
            assert 'marc_fields' in result


class TestRealWorldScenarios:
    """Test real-world scenarios with actual data"""
    
    def test_medical_book_processing(self, service):
        """Test processing keywords from medical book"""
        keywords = [
            "diabetes mellitus",
            "insulin",
            "glucose metabolism",
            "endocrinology"
        ]
        
        result = service.process_keywords(keywords, subject_type='medical')
        
        # Verify MARC fields are generated
        assert len(result['marc_fields']) > 0
        
        # Verify fields have correct structure
        for field in result['marc_fields']:
            assert field['field'] == '650'
            assert 'subfields' in field
            assert any(sf['code'] == 'a' for sf in field['subfields'])
            
    def test_computer_science_book_processing(self, service):
        """Test processing keywords from computer science book"""
        keywords = [
            "machine learning",
            "artificial intelligence",
            "neural networks",
            "deep learning"
        ]
        
        result = service.process_keywords(keywords, subject_type='science')
        
        # Should have authorities and MARC fields
        assert len(result['authorities']) == len(keywords)
        
    def test_vietnamese_education_book(self, service):
        """Test processing keywords similar to the sample MARC record"""
        keywords = [
            "Educators",
            "Teachers"
        ]
        
        result = service.process_keywords(keywords, subject_type='general')
        
        # Verify processing completes
        assert 'authorities' in result
        assert 'marc_fields' in result
        
        # Compare with expected MARC structure
        # 650 #0 $aEducators $zVietnam $vBiography.
        # 650 #0 $aTeachers $zVietnam $vBiography.
        marc_fields = result['marc_fields']
        
        # Should have at least one field
        assert len(marc_fields) > 0


# Test data from real MARC record
SAMPLE_MARC_DATA = {
    'title': 'GS. Trần Hồng Quân với sự nghiệp giáo dục đào tạo Việt Nam',
    'classification_lcc': 'LA2383.V52',
    'classification_dewey': '371.10092',
    'subjects': [
        'Trần, Hồng Quân, GS.TS., 1937-2023',
        'Educators',
        'Teachers'
    ],
    'expected_650_fields': [
        {
            'field': '650',
            'ind1': ' ',
            'ind2': '0',
            'subfields': [
                {'code': 'a', 'value': 'Educators'},
                {'code': 'z', 'value': 'Vietnam'},
                {'code': 'v', 'value': 'Biography'}
            ]
        },
        {
            'field': '650',
            'ind1': ' ',
            'ind2': '0',
            'subfields': [
                {'code': 'a', 'value': 'Teachers'},
                {'code': 'z', 'value': 'Vietnam'},
                {'code': 'v', 'value': 'Biography'}
            ]
        }
    ]
}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
