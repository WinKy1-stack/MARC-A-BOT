"""
MESH API Client
Kết nối với MeSH (Medical Subject Headings) API
"""
import logging
import requests
from typing import List, Dict, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class MESHClient:
    """Client để tra cứu MeSH headings"""
    
    def __init__(self, api_url: str = "https://meshb.nlm.nih.gov/api", timeout: int = 30):
        """
        Initialize MESH client
        
        Args:
            api_url: MESH API base URL
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def search_descriptor(self, term: str, limit: int = 10) -> List[Dict]:
        """
        Search for MeSH descriptors
        
        Args:
            term: Search term
            limit: Maximum number of results
            
        Returns:
            List of MeSH descriptors
        """
        try:
            url = f"{self.api_url}/search"
            params = {
                'search': term,
                'searchType': 'exactMatch',
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'descriptor_ui': item.get('ui', ''),
                        'descriptor_name': item.get('name', ''),
                        'tree_numbers': item.get('treeNumbers', []),
                        'scope_note': item.get('scopeNote', ''),
                        'terms': item.get('terms', []),
                        'source': 'MESH'
                    })
                    
            logger.info(f"Found {len(results)} MeSH descriptors for term: {term}")
            return results
            
        except requests.RequestException as e:
            logger.error(f"MESH API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching MESH descriptor: {e}")
            return []
            
    def fuzzy_search(self, term: str, limit: int = 10) -> List[Dict]:
        """
        Fuzzy search for MeSH descriptors
        
        Args:
            term: Search term
            limit: Maximum number of results
            
        Returns:
            List of MeSH descriptors
        """
        try:
            url = f"{self.api_url}/search"
            params = {
                'search': term,
                'searchType': 'contains',
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'descriptor_ui': item.get('ui', ''),
                        'descriptor_name': item.get('name', ''),
                        'tree_numbers': item.get('treeNumbers', []),
                        'scope_note': item.get('scopeNote', ''),
                        'terms': item.get('terms', []),
                        'source': 'MESH',
                        'match_type': 'fuzzy'
                    })
                    
            logger.info(f"Found {len(results)} MeSH descriptors (fuzzy) for term: {term}")
            return results
            
        except requests.RequestException as e:
            logger.error(f"MESH API fuzzy search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in MESH fuzzy search: {e}")
            return []
            
    def get_descriptor_by_id(self, descriptor_ui: str) -> Optional[Dict]:
        """
        Get MeSH descriptor by UI (unique identifier)
        
        Args:
            descriptor_ui: MeSH descriptor UI (e.g., "D015996")
            
        Returns:
            MeSH descriptor details
        """
        try:
            url = f"{self.api_url}/record/ui"
            params = {'ui': descriptor_ui}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'descriptor_ui': data.get('ui', ''),
                'descriptor_name': data.get('name', ''),
                'tree_numbers': data.get('treeNumbers', []),
                'scope_note': data.get('scopeNote', ''),
                'terms': data.get('terms', []),
                'annotations': data.get('annotations', ''),
                'previous_indexing': data.get('previousIndexing', []),
                'source': 'MESH'
            }
            
        except requests.RequestException as e:
            logger.error(f"MESH API get descriptor failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting MESH descriptor: {e}")
            return None
            
    def validate_descriptor(self, term: str) -> bool:
        """
        Validate if a term is a valid MeSH descriptor
        
        Args:
            term: Term to validate
            
        Returns:
            True if valid MeSH descriptor
        """
        results = self.search_descriptor(term, limit=1)
        if results and results[0]['descriptor_name'].lower() == term.lower():
            return True
        return False
        
    def get_tree_hierarchy(self, tree_number: str) -> List[Dict]:
        """
        Get MeSH tree hierarchy for a tree number
        
        Args:
            tree_number: MeSH tree number (e.g., "C04.588.941")
            
        Returns:
            List of hierarchical descriptors
        """
        try:
            # Parse tree number to get hierarchy
            parts = tree_number.split('.')
            hierarchy = []
            
            current_path = []
            for part in parts:
                current_path.append(part)
                tree_num = '.'.join(current_path)
                
                # Query for descriptor at this level
                url = f"{self.api_url}/search"
                params = {
                    'search': f'treeNumber:{tree_num}',
                    'limit': 1
                }
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                if 'items' in data and data['items']:
                    item = data['items'][0]
                    hierarchy.append({
                        'tree_number': tree_num,
                        'descriptor_name': item.get('name', ''),
                        'descriptor_ui': item.get('ui', ''),
                        'level': len(current_path)
                    })
                    
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error getting MeSH tree hierarchy: {e}")
            return []
