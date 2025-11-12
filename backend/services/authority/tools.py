"""
Authority Tools for AI Agent
Provides tools interface for agent to use authority services
"""
import logging
from typing import List, Dict, Any, Optional

from .authority_service import AuthorityService

logger = logging.getLogger(__name__)


class AuthorityTools:
    """
    Tools interface for AI Agent to interact with authority services
    """
    
    def __init__(self):
        """Initialize Authority Tools"""
        self.service = AuthorityService()
        
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for AI Agent
        
        Returns:
            List of tool definition dictionaries
        """
        return [
            {
                'name': 'search_authority_terms',
                'description': 'Tìm kiếm authority terms (MESH, LCSH, LCC, NLM) cho một keyword',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'keyword': {
                            'type': 'string',
                            'description': 'Từ khóa cần tìm authority terms'
                        },
                        'source': {
                            'type': 'string',
                            'enum': ['MESH', 'LCSH', 'LCC', 'NLM', 'ALL'],
                            'description': 'Nguồn authority cụ thể hoặc ALL cho tất cả'
                        }
                    },
                    'required': ['keyword']
                },
                'function': self.search_authority_terms
            },
            {
                'name': 'map_keywords_to_authorities',
                'description': 'Map nhiều keywords thành authority terms và tạo MARC21 650 fields',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'keywords': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Danh sách keywords cần map'
                        },
                        'subject_type': {
                            'type': 'string',
                            'enum': ['medical', 'general', 'science'],
                            'description': 'Loại chủ đề để xác định priority của sources'
                        }
                    },
                    'required': ['keywords']
                },
                'function': self.map_keywords_to_authorities
            },
            {
                'name': 'validate_authority_term',
                'description': 'Kiểm tra xem một term có phải là authority term hợp lệ không',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'term': {
                            'type': 'string',
                            'description': 'Term cần validate'
                        },
                        'source': {
                            'type': 'string',
                            'enum': ['MESH', 'LCSH', 'LCC'],
                            'description': 'Authority source để validate'
                        }
                    },
                    'required': ['term', 'source']
                },
                'function': self.validate_authority_term
            },
            {
                'name': 'generate_marc21_650_fields',
                'description': 'Tạo MARC21 650 fields từ authority terms',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'authorities': {
                            'type': 'array',
                            'items': {'type': 'object'},
                            'description': 'Danh sách authority terms'
                        }
                    },
                    'required': ['authorities']
                },
                'function': self.generate_marc21_650_fields
            },
            {
                'name': 'get_cache_statistics',
                'description': 'Lấy thống kê performance của cache',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'days': {
                            'type': 'integer',
                            'description': 'Số ngày để thống kê (default: 7)'
                        }
                    }
                },
                'function': self.get_cache_statistics
            }
        ]
        
    def search_authority_terms(self, keyword: str, source: str = 'ALL') -> Dict[str, Any]:
        """
        Tool: Search authority terms for a keyword
        
        Args:
            keyword: Keyword to search
            source: Authority source (MESH, LCSH, LCC, NLM, ALL)
            
        Returns:
            Dictionary with search results
        """
        try:
            source_param = None if source == 'ALL' else source
            results = self.service.search_authority(keyword, source_param)
            
            return {
                'success': True,
                'keyword': keyword,
                'source': source,
                'results': results,
                'count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error in search_authority_terms: {e}")
            return {
                'success': False,
                'error': str(e),
                'keyword': keyword,
                'results': []
            }
            
    def map_keywords_to_authorities(self, keywords: List[str], 
                                   subject_type: str = 'general') -> Dict[str, Any]:
        """
        Tool: Map keywords to authorities and generate MARC fields
        
        Args:
            keywords: List of keywords
            subject_type: Subject type (medical, general, science)
            
        Returns:
            Dictionary with mapping results and MARC fields
        """
        try:
            result = self.service.process_keywords(keywords, subject_type)
            
            return {
                'success': True,
                'input_keywords': keywords,
                'subject_type': subject_type,
                'authorities': result['authorities'],
                'marc_fields': result['marc_fields'],
                'statistics': result['stats']
            }
            
        except Exception as e:
            logger.error(f"Error in map_keywords_to_authorities: {e}")
            return {
                'success': False,
                'error': str(e),
                'input_keywords': keywords,
                'authorities': [],
                'marc_fields': []
            }
            
    def validate_authority_term(self, term: str, source: str) -> Dict[str, Any]:
        """
        Tool: Validate authority term
        
        Args:
            term: Term to validate
            source: Authority source
            
        Returns:
            Validation result
        """
        try:
            is_valid = self.service.validate_term(term, source)
            
            return {
                'success': True,
                'term': term,
                'source': source,
                'is_valid': is_valid
            }
            
        except Exception as e:
            logger.error(f"Error in validate_authority_term: {e}")
            return {
                'success': False,
                'error': str(e),
                'term': term,
                'is_valid': False
            }
            
    def generate_marc21_650_fields(self, authorities: List[Dict]) -> Dict[str, Any]:
        """
        Tool: Generate MARC21 650 fields
        
        Args:
            authorities: List of authority terms
            
        Returns:
            MARC21 fields
        """
        try:
            marc_fields = self.service.marc_generator.create_marc21_650_field(authorities)
            
            return {
                'success': True,
                'marc_fields': marc_fields,
                'count': len(marc_fields),
                'formatted_display': [
                    self.service.marc_generator.format_marc_field_display(field)
                    for field in marc_fields
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in generate_marc21_650_fields: {e}")
            return {
                'success': False,
                'error': str(e),
                'marc_fields': []
            }
            
    def get_cache_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Tool: Get cache statistics
        
        Args:
            days: Number of days for statistics
            
        Returns:
            Cache statistics
        """
        try:
            stats = self.service.get_cache_statistics(days)
            
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Error in get_cache_statistics: {e}")
            return {
                'success': False,
                'error': str(e),
                'statistics': {}
            }
