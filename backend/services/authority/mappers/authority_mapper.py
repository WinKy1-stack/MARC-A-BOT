"""
Authority Mapper
Map keywords to authority terms from various sources
"""
import logging
from typing import List, Dict, Optional
from rapidfuzz import fuzz

from ..cache.cache_manager import AuthorityCacheManager
from ..clients.mesh_client import MESHClient
from ..clients.loc_client import LCSHClient, LCCClient
from ..clients.z3950_client import NLMClient, LOCClient
from ..config import (
    FUZZY_MATCH_THRESHOLD, 
    MAX_SUGGESTIONS, 
    AUTHORITY_PRIORITY,
    CACHE_DB_PATH
)

logger = logging.getLogger(__name__)


class AuthorityMapper:
    """Map keywords to authority terms"""
    
    def __init__(self, cache_manager: AuthorityCacheManager = None):
        """
        Initialize Authority Mapper
        
        Args:
            cache_manager: Cache manager instance (optional)
        """
        self.cache = cache_manager or AuthorityCacheManager(str(CACHE_DB_PATH))
        
        # Initialize clients
        self.mesh_client = MESHClient()
        self.lcsh_client = LCSHClient()
        self.lcc_client = LCCClient()
        
        # Note: Z39.50 clients are optional (require connection)
        self.nlm_client = None
        self.loc_z3950_client = None
        
    def find_authority_terms(self, keyword: str, source: str = None, 
                            use_fuzzy: bool = True) -> List[Dict]:
        """
        Find authority terms for a keyword
        
        Args:
            keyword: Keyword to search
            source: Specific source (MESH, LCSH, LCC, NLM) or None for all
            use_fuzzy: Enable fuzzy matching
            
        Returns:
            List of authority terms with metadata
        """
        results = []
        
        # Try cache first
        cached_results = self.cache.search(
            keyword, 
            source, 
            fuzzy_threshold=FUZZY_MATCH_THRESHOLD,
            limit=MAX_SUGGESTIONS
        )
        
        if cached_results:
            logger.info(f"Cache hit for keyword: {keyword} ({len(cached_results)} results)")
            return cached_results
            
        # Cache miss - query online sources
        logger.info(f"Cache miss for keyword: {keyword}, querying online sources")
        
        if source:
            results = self._query_source(keyword, source, use_fuzzy)
        else:
            # Query all sources
            for src in ['MESH', 'LCSH', 'LCC']:
                results.extend(self._query_source(keyword, src, use_fuzzy))
                
        # Cache the results
        for result in results:
            self.cache.add_term(
                keyword=keyword,
                authority_id=result.get('authority_id', ''),
                normalized_term=result.get('term', result.get('descriptor_name', keyword)),
                source=result['source'],
                category=result.get('category', 'general'),
                score=result.get('score', 100.0),
                metadata=result.get('metadata', {})
            )
            
        # Log cache miss
        self.cache._log_cache_stat(keyword, source, cache_hit=False, match_type='online')
        
        return results
        
    def _query_source(self, keyword: str, source: str, use_fuzzy: bool = True) -> List[Dict]:
        """
        Query a specific authority source
        
        Args:
            keyword: Keyword to search
            source: Authority source (MESH, LCSH, LCC, NLM)
            use_fuzzy: Enable fuzzy matching
            
        Returns:
            List of authority terms from the source
        """
        results = []
        
        try:
            if source == 'MESH':
                # Try exact match first
                mesh_results = self.mesh_client.search_descriptor(keyword, limit=MAX_SUGGESTIONS)
                
                if not mesh_results and use_fuzzy:
                    # Try fuzzy search
                    mesh_results = self.mesh_client.fuzzy_search(keyword, limit=MAX_SUGGESTIONS)
                    
                for item in mesh_results:
                    results.append({
                        'term': item['descriptor_name'],
                        'authority_id': item['descriptor_ui'],
                        'source': 'MESH',
                        'category': 'medical',
                        'score': 100.0 if item.get('match_type') != 'fuzzy' else 80.0,
                        'metadata': {
                            'tree_numbers': item.get('tree_numbers', []),
                            'scope_note': item.get('scope_note', ''),
                            'terms': item.get('terms', [])
                        }
                    })
                    
            elif source == 'LCSH':
                lcsh_results = self.lcsh_client.search(keyword, limit=MAX_SUGGESTIONS)
                
                for item in lcsh_results:
                    results.append({
                        'term': item['term'],
                        'authority_id': item['authority_id'],
                        'source': 'LCSH',
                        'category': 'subject',
                        'score': 100.0,
                        'metadata': {
                            'uri': item.get('uri', '')
                        }
                    })
                    
            elif source == 'LCC':
                lcc_results = self.lcc_client.search(keyword, limit=MAX_SUGGESTIONS)
                
                for item in lcc_results:
                    results.append({
                        'term': item['term'],
                        'authority_id': item['authority_id'],
                        'source': 'LCC',
                        'category': 'classification',
                        'score': 100.0,
                        'metadata': {
                            'uri': item.get('uri', '')
                        }
                    })
                    
            elif source == 'NLM':
                # Z39.50 query (requires connection)
                if not self.nlm_client:
                    self.nlm_client = NLMClient()
                    
                if self.nlm_client.connect():
                    nlm_results = self.nlm_client.search_mesh_heading(keyword, max_records=MAX_SUGGESTIONS)
                    
                    for item in nlm_results:
                        # Extract 650 fields from MARC record
                        for field in item.get('data_fields', []):
                            if field['tag'] == '650':
                                subfield_a = next((sf['value'] for sf in field['subfields'] if sf['code'] == 'a'), '')
                                if subfield_a:
                                    results.append({
                                        'term': subfield_a,
                                        'authority_id': '',
                                        'source': 'NLM',
                                        'category': 'medical',
                                        'score': 100.0,
                                        'metadata': {}
                                    })
                                    
        except Exception as e:
            logger.error(f"Error querying {source}: {e}")
            
        return results
        
    def map_keyword_to_authorities(self, keywords: List[str], 
                                   subject_type: str = 'general') -> List[Dict]:
        """
        Map multiple keywords to authority terms
        
        Args:
            keywords: List of keywords to map
            subject_type: Subject type (medical, general, science)
            
        Returns:
            List of mapped authorities with scores
        """
        all_results = []
        
        # Get source priority based on subject type
        sources = AUTHORITY_PRIORITY.get(subject_type, AUTHORITY_PRIORITY['general'])
        
        for keyword in keywords:
            keyword_results = []
            
            # Try each source in priority order
            for source in sources:
                results = self.find_authority_terms(keyword, source, use_fuzzy=True)
                
                if results:
                    # Add priority score based on source order
                    priority_score = (len(sources) - sources.index(source)) / len(sources) * 20
                    
                    for result in results:
                        result['priority_score'] = priority_score
                        result['final_score'] = result['score'] + priority_score
                        keyword_results.append(result)
                        
                    # If we found good matches, stop trying other sources
                    if any(r['score'] >= 90 for r in results):
                        break
                        
            # If no authority found, mark as uncontrolled term
            if not keyword_results:
                logger.warning(f"No authority found for keyword: {keyword}")
                keyword_results.append({
                    'term': keyword,
                    'authority_id': '',
                    'source': 'UNCONTROLLED',
                    'category': 'uncontrolled',
                    'score': 0,
                    'priority_score': 0,
                    'final_score': 0,
                    'metadata': {}
                })
                
            # Sort by final score
            keyword_results.sort(key=lambda x: x['final_score'], reverse=True)
            
            # Take top result
            all_results.append(keyword_results[0])
            
        return all_results
        
    def validate_authority_term(self, term: str, source: str) -> bool:
        """
        Validate if a term is valid in the authority source
        
        Args:
            term: Term to validate
            source: Authority source (MESH, LCSH, LCC)
            
        Returns:
            True if valid authority term
        """
        try:
            if source == 'MESH':
                return self.mesh_client.validate_descriptor(term)
            elif source == 'LCSH':
                return self.lcsh_client.validate(term)
            elif source == 'LCC':
                return self.lcc_client.validate(term)
            else:
                logger.warning(f"Unknown source for validation: {source}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating term: {e}")
            return False
