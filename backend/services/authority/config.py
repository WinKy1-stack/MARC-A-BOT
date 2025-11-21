"""
Configuration cho Authority Services
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Cache configuration
CACHE_DIR = BASE_DIR / 'services' / 'authority' / 'cache'
CACHE_DB_PATH = CACHE_DIR / 'authority_cache.db'

# API Endpoints
MESH_API_URL = "https://meshb.nlm.nih.gov/api/records"
MESH_XML_DUMP_URL = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/"

# LOC Linked Data Service
LOC_AUTHORITIES_URL = "http://id.loc.gov/authorities"
LCSH_BASE_URL = f"{LOC_AUTHORITIES_URL}/subjects"
LCC_BASE_URL = f"{LOC_AUTHORITIES_URL}/classification"

# Z39.50 Configuration for NLM
Z3950_NLM_HOST = "locatorplus.gov"
Z3950_NLM_PORT = 210
Z3950_NLM_DATABASE = "LOCATORPLUS"

# Z39.50 Configuration for Library of Congress
Z3950_LOC_HOST = "lx2.loc.gov"
Z3950_LOC_PORT = 210
Z3950_LOC_DATABASE = "LCDB"

# Search/Matching Configuration
FUZZY_MATCH_THRESHOLD = 80  # Minimum score (0-100) for fuzzy matching
MAX_SUGGESTIONS = 10  # Maximum number of authority suggestions
CACHE_HIT_TARGET = 0.80  # Target cache hit rate (80%)

# Rate Limiting
API_RATE_LIMIT = 100  # requests per minute
API_TIMEOUT = 30  # seconds
API_RETRY_ATTEMPTS = 3

# Priority Order for Authority Sources (by subject type)
AUTHORITY_PRIORITY = {
    'medical': ['MESH', 'NLM', 'LCSH', 'LCC'],
    'general': ['LCSH', 'LCC', 'MESH', 'NLM'],
    'science': ['LCSH', 'LCC', 'MESH', 'NLM']
}

# MARC21 650 Field Configuration
MARC_650_INDICATORS = {
    'MESH': {'ind1': ' ', 'ind2': '2'},  # MeSH
    'LCSH': {'ind1': ' ', 'ind2': '0'},  # Library of Congress
    'NLM': {'ind1': ' ', 'ind2': '2'},   # NLM
    'LCC': {'ind1': ' ', 'ind2': '0'}    # Library of Congress
}

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = BASE_DIR / 'logs' / 'authority_service.log'
