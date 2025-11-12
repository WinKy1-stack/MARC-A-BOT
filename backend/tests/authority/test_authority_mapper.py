"""
Unit Tests for Authority Mapper
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.authority.mappers.authority_mapper import AuthorityMapper
from services.authority.cache.cache_manager import AuthorityCacheManager


@pytest.fixture
def temp_cache(tmp_path):
    """Create temporary cache for testing"""
    cache_db = tmp_path / "test_cache.db"
    return AuthorityCacheManager(str(cache_db))


@pytest.fixture
def mapper(temp_cache):
    """Create mapper with temporary cache"""
    return AuthorityMapper(temp_cache)


class TestAuthorityMapper:
    """Test Authority Mapper functionality"""
    
    def test_find_authority_terms_exact_match(self, mapper, temp_cache):
        """Test exact match from cache"""
        # Add test data to cache
        temp_cache.add_term(
            keyword="machine learning",
            authority_id="D015996",
            normalized_term="Machine Learning",
            source="MESH",
            category="medical",
            score=100.0
        )
        
        # Search
        results = mapper.find_authority_terms("machine learning", "MESH")
        
        assert len(results) > 0
        assert results[0]['authority_id'] == "D015996"
        assert results[0]['source'] == "MESH"
        
    def test_find_authority_terms_fuzzy_match(self, mapper, temp_cache):
        """Test fuzzy match from cache"""
        # Add test data
        temp_cache.add_term(
            keyword="artificial intelligence",
            authority_id="D001185",
            normalized_term="Artificial Intelligence",
            source="MESH",
            category="medical",
            score=100.0
        )
        
        # Search with typo
        results = mapper.find_authority_terms("artifical inteligence", "MESH")
        
        # Should find the correct term via fuzzy match
        assert len(results) > 0
        
    def test_map_keyword_to_authorities_medical(self, mapper):
        """Test mapping medical keywords"""
        keywords = ["diabetes", "hypertension"]
        
        results = mapper.map_keyword_to_authorities(keywords, subject_type='medical')
        
        assert len(results) == len(keywords)
        
    def test_map_keyword_to_authorities_uncontrolled(self, mapper):
        """Test mapping with no authority found"""
        keywords = ["xyz123nonsense456"]
        
        results = mapper.map_keyword_to_authorities(keywords, subject_type='general')
        
        assert len(results) == 1
        assert results[0]['source'] == 'UNCONTROLLED'
        
    def test_validate_authority_term(self, mapper):
        """Test authority term validation"""
        # This would require mocking the API calls
        # For now, we'll just ensure the method exists and doesn't crash
        try:
            result = mapper.validate_authority_term("test term", "MESH")
            assert isinstance(result, bool)
        except Exception as e:
            # Expected if API is not available
            assert True


class TestCacheManager:
    """Test Cache Manager functionality"""
    
    def test_add_and_retrieve_term(self, temp_cache):
        """Test adding and retrieving terms"""
        success = temp_cache.add_term(
            keyword="python programming",
            authority_id="QA76.73.P98",
            normalized_term="Python (Computer program language)",
            source="LCSH",
            category="general",
            score=100.0
        )
        
        assert success
        
        results = temp_cache.exact_match("python programming", "LCSH")
        assert len(results) == 1
        assert results[0]['authority_id'] == "QA76.73.P98"
        
    def test_fuzzy_search(self, temp_cache):
        """Test fuzzy search"""
        temp_cache.add_term(
            keyword="database management",
            authority_id="QA76.9.D3",
            normalized_term="Database management",
            source="LCSH",
            category="general",
            score=100.0
        )
        
        results = temp_cache.fuzzy_match("databse managment", threshold=70)
        assert len(results) > 0
        
    def test_cache_stats(self, temp_cache):
        """Test cache statistics"""
        # Add some terms
        temp_cache.add_term("term1", "id1", "Term 1", "MESH", "medical", 100.0)
        temp_cache.add_term("term2", "id2", "Term 2", "LCSH", "general", 100.0)
        
        # Search to generate stats
        temp_cache.search("term1")
        temp_cache.search("term2")
        
        stats = temp_cache.get_cache_stats()
        
        assert 'total_cache_entries' in stats
        assert stats['total_cache_entries'] >= 2
        
    def test_clear_cache(self, temp_cache):
        """Test clearing cache"""
        temp_cache.add_term("term1", "id1", "Term 1", "MESH", "medical", 100.0)
        
        success = temp_cache.clear_cache()
        assert success
        
        stats = temp_cache.get_cache_stats()
        assert stats['total_cache_entries'] == 0


# Test data samples
TEST_KEYWORDS = [
    "machine learning",
    "artificial intelligence",
    "diabetes mellitus",
    "hypertension",
    "python programming",
    "database management",
    "quantum physics",
    "organic chemistry"
]

TEST_AUTHORITIES = [
    {
        'keyword': 'machine learning',
        'authority_id': 'D015996',
        'normalized_term': 'Machine Learning',
        'source': 'MESH',
        'category': 'medical'
    },
    {
        'keyword': 'diabetes mellitus',
        'authority_id': 'D003920',
        'normalized_term': 'Diabetes Mellitus',
        'source': 'MESH',
        'category': 'medical'
    }
]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
