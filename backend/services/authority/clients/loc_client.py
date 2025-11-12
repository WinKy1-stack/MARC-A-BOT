"""
Library of Congress Client
Kết nối với LOC Linked Data Service cho LCSH và LCC
"""
import logging
import requests
from typing import List, Dict, Optional
from urllib.parse import quote
import time

logger = logging.getLogger(__name__)


class LOCLinkedDataClient:
    """Client cho Library of Congress Linked Data Service"""
    
    def __init__(self, base_url: str = "http://id.loc.gov", timeout: int = 30):
        """
        Initialize LOC client
        
        Args:
            base_url: LOC Linked Data base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json'
        })
        
    def search_subjects(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search LCSH (Library of Congress Subject Headings)
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of LCSH subject headings
        """
        try:
            url = f"{self.base_url}/authorities/subjects/suggest2/"
            params = {
                'q': query,
                'count': limit
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            # LOC suggest API returns [query, [labels], [ids], [uris]]
            if len(data) >= 4:
                labels = data[1]
                ids = data[2] if len(data) > 2 else []
                uris = data[3] if len(data) > 3 else []
                
                for i, label in enumerate(labels[:limit]):
                    authority_id = ids[i] if i < len(ids) else ''
                    uri = uris[i] if i < len(uris) else ''
                    
                    results.append({
                        'term': label,
                        'authority_id': authority_id,
                        'uri': uri,
                        'source': 'LCSH',
                        'category': 'subject'
                    })
                    
            logger.info(f"Found {len(results)} LCSH subjects for query: {query}")
            return results
            
        except requests.RequestException as e:
            logger.error(f"LCSH search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching LCSH: {e}")
            return []
            
    def search_classification(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search LCC (Library of Congress Classification)
        
        Args:
            query: Search query (classification number or topic)
            limit: Maximum number of results
            
        Returns:
            List of LCC classifications
        """
        try:
            url = f"{self.base_url}/authorities/classification/suggest2/"
            params = {
                'q': query,
                'count': limit
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            if len(data) >= 4:
                labels = data[1]
                ids = data[2] if len(data) > 2 else []
                uris = data[3] if len(data) > 3 else []
                
                for i, label in enumerate(labels[:limit]):
                    authority_id = ids[i] if i < len(ids) else ''
                    uri = uris[i] if i < len(uris) else ''
                    
                    results.append({
                        'term': label,
                        'authority_id': authority_id,
                        'uri': uri,
                        'source': 'LCC',
                        'category': 'classification'
                    })
                    
            logger.info(f"Found {len(results)} LCC classifications for query: {query}")
            return results
            
        except requests.RequestException as e:
            logger.error(f"LCC search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching LCC: {e}")
            return []
            
    def get_authority_details(self, uri: str) -> Optional[Dict]:
        """
        Get detailed information about an authority record
        
        Args:
            uri: Authority URI (e.g., "http://id.loc.gov/authorities/subjects/sh85082139")
            
        Returns:
            Authority record details
        """
        try:
            # Add .json extension to get JSON format
            json_uri = f"{uri}.json"
            
            response = self.session.get(json_uri, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information from RDF/JSON-LD
            details = {
                'uri': uri,
                'preferred_label': '',
                'alternative_labels': [],
                'broader_terms': [],
                'narrower_terms': [],
                'related_terms': [],
                'scope_note': '',
                'source': 'LOC'
            }
            
            # Parse JSON-LD structure
            if isinstance(data, list) and len(data) > 0:
                record = data[0]
                
                # Preferred label
                if 'http://www.loc.gov/mads/rdf/v1#authoritativeLabel' in record:
                    labels = record['http://www.loc.gov/mads/rdf/v1#authoritativeLabel']
                    if labels and len(labels) > 0:
                        details['preferred_label'] = labels[0].get('@value', '')
                        
                # Alternative labels
                if 'http://www.loc.gov/mads/rdf/v1#variantLabel' in record:
                    variants = record['http://www.loc.gov/mads/rdf/v1#variantLabel']
                    for variant in variants:
                        if '@value' in variant:
                            details['alternative_labels'].append(variant['@value'])
                            
                # Scope note
                if 'http://www.w3.org/2004/02/skos/core#scopeNote' in record:
                    notes = record['http://www.w3.org/2004/02/skos/core#scopeNote']
                    if notes and len(notes) > 0:
                        details['scope_note'] = notes[0].get('@value', '')
                        
            return details
            
        except requests.RequestException as e:
            logger.error(f"Failed to get authority details: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting authority details: {e}")
            return None
            
    def validate_subject(self, term: str) -> bool:
        """
        Validate if a term is a valid LCSH
        
        Args:
            term: Subject term to validate
            
        Returns:
            True if valid LCSH
        """
        results = self.search_subjects(term, limit=1)
        if results and results[0]['term'].lower() == term.lower():
            return True
        return False
        
    def validate_classification(self, classification: str) -> bool:
        """
        Validate if a classification is valid LCC
        
        Args:
            classification: Classification number to validate
            
        Returns:
            True if valid LCC
        """
        results = self.search_classification(classification, limit=1)
        return len(results) > 0


class LCSHClient:
    """Specialized client for LCSH (Library of Congress Subject Headings)"""
    
    def __init__(self):
        self.client = LOCLinkedDataClient()
        
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search LCSH"""
        return self.client.search_subjects(query, limit)
        
    def validate(self, term: str) -> bool:
        """Validate LCSH term"""
        return self.client.validate_subject(term)
        
    def get_details(self, uri: str) -> Optional[Dict]:
        """Get LCSH details"""
        return self.client.get_authority_details(uri)


class LCCClient:
    """Specialized client for LCC (Library of Congress Classification)"""
    
    def __init__(self):
        self.client = LOCLinkedDataClient()
        
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search LCC"""
        return self.client.search_classification(query, limit)
        
    def validate(self, classification: str) -> bool:
        """Validate LCC number"""
        return self.client.validate_classification(classification)
        
    def get_details(self, uri: str) -> Optional[Dict]:
        """Get LCC details"""
        return self.client.get_authority_details(uri)
