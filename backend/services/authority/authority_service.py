"""
Authority Service - Main Service Class
Orchestrates authority control operations
"""
import logging
from typing import List, Dict, Optional

from .cache.cache_manager import AuthorityCacheManager
from .mappers.authority_mapper import AuthorityMapper
from .marc_generator import MARCFieldGenerator
from .config import CACHE_DB_PATH

logger = logging.getLogger(__name__)


class AuthorityService:
    """
    Main Authority Control Service
    Provides unified interface for authority control operations
    """
    
    def __init__(self):
        """Initialize Authority Service"""
        self.cache_manager = AuthorityCacheManager(str(CACHE_DB_PATH))
        self.mapper = AuthorityMapper(self.cache_manager)
        self.marc_generator = MARCFieldGenerator()
        
    def process_keywords(self, keywords: List[str], subject_type: str = 'general') -> Dict:
        """
        Process keywords and return authority terms with MARC fields
        
        Args:
            keywords: List of raw keywords
            subject_type: Subject type (medical, general, science)
            
        Returns:
            Dictionary containing:
                - authorities: List of mapped authority terms
                - marc_fields: List of MARC21 650 fields
                - stats: Processing statistics
        """
        try:
            # Map keywords to authorities
            authorities = self.mapper.map_keyword_to_authorities(keywords, subject_type)
            
            # Generate MARC21 650 fields
            marc_fields = self.marc_generator.create_marc21_650_field(authorities)
            
            # Collect statistics
            stats = {
                'total_keywords': len(keywords),
                'total_authorities': len(authorities),
                'total_marc_fields': len(marc_fields),
                'sources_used': list(set(a['source'] for a in authorities)),
                'uncontrolled_terms': sum(1 for a in authorities if a['source'] == 'UNCONTROLLED')
            }
            
            logger.info(f"Processed {len(keywords)} keywords -> {len(authorities)} authorities")
            
            return {
                'authorities': authorities,
                'marc_fields': marc_fields,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error processing keywords: {e}")
            return {
                'authorities': [],
                'marc_fields': [],
                'stats': {},
                'error': str(e)
            }
            
    def search_authority(self, keyword: str, source: str = None) -> List[Dict]:
        """
        Search for authority terms for a single keyword
        
        Args:
            keyword: Keyword to search
            source: Specific authority source (optional)
            
        Returns:
            List of authority terms
        """
        return self.mapper.find_authority_terms(keyword, source)
        
    def validate_term(self, term: str, source: str) -> bool:
        """
        Validate if a term is valid in an authority source
        
        Args:
            term: Term to validate
            source: Authority source
            
        Returns:
            True if valid
        """
        return self.mapper.validate_authority_term(term, source)
        
    def get_cache_statistics(self, days: int = 7) -> Dict:
        """
        Get cache performance statistics
        
        Args:
            days: Number of days for statistics
            
        Returns:
            Cache statistics dictionary
        """
        return self.cache_manager.get_cache_stats(days)
        
    def clear_cache(self) -> bool:
        """
        Clear the authority cache
        
        Returns:
            True if successful
        """
        return self.cache_manager.clear_cache()
        
    def batch_process(self, keyword_batches: List[List[str]], 
                     subject_type: str = 'general') -> List[Dict]:
        """
        Process multiple batches of keywords
        
        Args:
            keyword_batches: List of keyword lists
            subject_type: Subject type
            
        Returns:
            List of processing results for each batch
        """
        results = []
        
        for i, keywords in enumerate(keyword_batches):
            logger.info(f"Processing batch {i+1}/{len(keyword_batches)}")
            result = self.process_keywords(keywords, subject_type)
            results.append(result)
            
        return results
