"""
Z39.50 Client for NLM and Library of Congress
Note: PyZ3950 is optional. If not installed, Z39.50 functionality will be disabled.
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Try to import PyZ3950, but make it optional
try:
    from PyZ3950 import zoom
    Z3950_AVAILABLE = True
except ImportError:
    logger.warning("PyZ3950 not installed. Z39.50 functionality disabled.")
    Z3950_AVAILABLE = False
    zoom = None


class Z3950Client:
    """Z39.50 Client để kết nối với NLM và LOC"""
    
    def __init__(self, host: str, port: int, database: str):
        """
        Initialize Z39.50 client
        
        Args:
            host: Z39.50 server host
            port: Z39.50 server port
            database: Database name
        """
        if not Z3950_AVAILABLE:
            raise ImportError("PyZ3950 is not installed. Please install it to use Z39.50 functionality.")
        
        self.host = host
        self.port = port
        self.database = database
        self.connection = None
        
    def connect(self):
        """Establish Z39.50 connection"""
        try:
            conn = zoom.Connection(self.host, self.port)
            conn.databaseName = self.database
            conn.preferredRecordSyntax = 'USMARC'
            self.connection = conn
            logger.info(f"Connected to Z39.50 server: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Z39.50 server: {e}")
            return False
            
    def disconnect(self):
        """Close Z39.50 connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Z39.50 connection closed")
            except Exception as e:
                logger.error(f"Error closing Z39.50 connection: {e}")
                
    def search(self, query: str, max_records: int = 10) -> List[Dict]:
        """
        Search using Z39.50
        
        Args:
            query: Search query (e.g., '@attr 1=21 "machine learning"')
            max_records: Maximum number of records to retrieve
            
        Returns:
            List of MARC records
        """
        if not self.connection:
            if not self.connect():
                return []
                
        try:
            # Perform search
            query_obj = zoom.Query('PQF', query)
            result_set = self.connection.search(query_obj)
            
            records = []
            for i in range(min(len(result_set), max_records)):
                try:
                    record = result_set[i]
                    # Parse MARC record
                    marc_data = self._parse_marc_record(record.data)
                    if marc_data:
                        records.append(marc_data)
                except Exception as e:
                    logger.warning(f"Error parsing record {i}: {e}")
                    continue
                    
            logger.info(f"Retrieved {len(records)} records for query: {query}")
            return records
            
        except Exception as e:
            logger.error(f"Z39.50 search error: {e}")
            return []
            
    def _parse_marc_record(self, record_data: bytes) -> Optional[Dict]:
        """
        Parse MARC record data
        
        Args:
            record_data: Raw MARC record bytes
            
        Returns:
            Parsed MARC record as dictionary
        """
        try:
            from pymarc import Record
            
            # Convert bytes to MARC record
            record = Record(data=record_data)
            
            # Extract relevant fields
            marc_dict = {
                'leader': str(record.leader),
                'control_fields': {},
                'data_fields': []
            }
            
            # Control fields (001-009)
            for field in record.get_fields('001', '002', '003', '005', '008'):
                marc_dict['control_fields'][field.tag] = str(field.data)
                
            # Data fields (010-999)
            for field in record.get_fields():
                if field.tag >= '010':
                    field_data = {
                        'tag': field.tag,
                        'indicators': [field.indicator1, field.indicator2],
                        'subfields': []
                    }
                    
                    for subfield in field.subfields:
                        if isinstance(subfield, str):
                            continue
                        field_data['subfields'].append({
                            'code': subfield[0],
                            'value': subfield[1]
                        })
                        
                    marc_dict['data_fields'].append(field_data)
                    
            return marc_dict
            
        except Exception as e:
            logger.error(f"Error parsing MARC record: {e}")
            return None
            
    def search_subject(self, subject: str, max_records: int = 10) -> List[Dict]:
        """
        Search by subject heading
        
        Args:
            subject: Subject term to search
            max_records: Maximum records to retrieve
            
        Returns:
            List of matching records
        """
        # Use attribute 21 for subject heading search
        query = f'@attr 1=21 "{subject}"'
        return self.search(query, max_records)
        
    def search_classification(self, classification: str, max_records: int = 10) -> List[Dict]:
        """
        Search by classification number
        
        Args:
            classification: Classification number (e.g., "QA76.9")
            max_records: Maximum records to retrieve
            
        Returns:
            List of matching records
        """
        # Use attribute 16 for call number search
        query = f'@attr 1=16 "{classification}"'
        return self.search(query, max_records)


class NLMClient(Z3950Client):
    """Z39.50 Client for National Library of Medicine"""
    
    def __init__(self):
        from ..config import Z3950_NLM_HOST, Z3950_NLM_PORT, Z3950_NLM_DATABASE
        super().__init__(Z3950_NLM_HOST, Z3950_NLM_PORT, Z3950_NLM_DATABASE)
        
    def search_mesh_heading(self, heading: str, max_records: int = 10) -> List[Dict]:
        """
        Search for MeSH heading in NLM catalog
        
        Args:
            heading: MeSH heading term
            max_records: Maximum records to retrieve
            
        Returns:
            List of matching MARC records
        """
        return self.search_subject(heading, max_records)


class LOCClient(Z3950Client):
    """Z39.50 Client for Library of Congress"""
    
    def __init__(self):
        from ..config import Z3950_LOC_HOST, Z3950_LOC_PORT, Z3950_LOC_DATABASE
        super().__init__(Z3950_LOC_HOST, Z3950_LOC_PORT, Z3950_LOC_DATABASE)
        
    def search_lcsh(self, subject: str, max_records: int = 10) -> List[Dict]:
        """
        Search for LCSH subject heading
        
        Args:
            subject: Subject heading term
            max_records: Maximum records to retrieve
            
        Returns:
            List of matching MARC records
        """
        return self.search_subject(subject, max_records)
        
    def search_lcc(self, classification: str, max_records: int = 10) -> List[Dict]:
        """
        Search for LCC classification
        
        Args:
            classification: LCC classification number
            max_records: Maximum records to retrieve
            
        Returns:
            List of matching MARC records
        """
        return self.search_classification(classification, max_records)
