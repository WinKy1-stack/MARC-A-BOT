"""
Cache initialization and update script
Script khởi tạo và cập nhật cache database
"""
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.authority.cache.cache_manager import AuthorityCacheManager
from services.authority.clients.mesh_client import MESHClient
from services.authority.clients.loc_client import LCSHClient, LCCClient
from services.authority.config import CACHE_DB_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_cache():
    """Initialize cache database"""
    logger.info("Initializing cache database...")
    cache = AuthorityCacheManager(str(CACHE_DB_PATH))
    logger.info(f"Cache database initialized at {CACHE_DB_PATH}")
    return cache


def populate_common_medical_terms(cache: AuthorityCacheManager):
    """Populate cache with common medical terms"""
    logger.info("Populating common medical terms...")
    
    mesh_client = MESHClient()
    
    common_terms = [
        "diabetes mellitus",
        "hypertension",
        "insulin",
        "blood glucose",
        "cardiovascular disease",
        "obesity",
        "cancer",
        "infection",
        "antibiotics",
        "vaccination",
        "immunology",
        "genetics",
        "metabolism",
        "nutrition",
        "exercise"
    ]
    
    count = 0
    for term in common_terms:
        try:
            results = mesh_client.search_descriptor(term, limit=1)
            if results:
                result = results[0]
                cache.add_term(
                    keyword=term,
                    authority_id=result['descriptor_ui'],
                    normalized_term=result['descriptor_name'],
                    source='MESH',
                    category='medical',
                    score=100.0,
                    metadata={
                        'tree_numbers': result.get('tree_numbers', []),
                        'scope_note': result.get('scope_note', '')
                    }
                )
                count += 1
                logger.info(f"  Added: {term} -> {result['descriptor_name']}")
        except Exception as e:
            logger.warning(f"  Failed to add {term}: {e}")
    
    logger.info(f"Added {count} medical terms to cache")


def populate_common_general_terms(cache: AuthorityCacheManager):
    """Populate cache with common general terms"""
    logger.info("Populating common general terms...")
    
    lcsh_client = LCSHClient()
    
    common_terms = [
        "education",
        "teaching",
        "learning",
        "technology",
        "computer programming",
        "artificial intelligence",
        "machine learning",
        "database management",
        "software engineering",
        "web development"
    ]
    
    count = 0
    for term in common_terms:
        try:
            results = lcsh_client.search(term, limit=1)
            if results:
                result = results[0]
                cache.add_term(
                    keyword=term,
                    authority_id=result['authority_id'],
                    normalized_term=result['term'],
                    source='LCSH',
                    category='general',
                    score=100.0,
                    metadata={
                        'uri': result.get('uri', '')
                    }
                )
                count += 1
                logger.info(f"  Added: {term} -> {result['term']}")
        except Exception as e:
            logger.warning(f"  Failed to add {term}: {e}")
    
    logger.info(f"Added {count} general terms to cache")


def show_cache_stats(cache: AuthorityCacheManager):
    """Display cache statistics"""
    logger.info("Cache statistics:")
    stats = cache.get_cache_stats(days=365)
    
    print("\n" + "="*50)
    print("CACHE STATISTICS")
    print("="*50)
    print(f"Total Cache Entries: {stats.get('total_cache_entries', 0)}")
    print(f"Total Queries: {stats.get('total_queries', 0)}")
    print(f"Cache Hits: {stats.get('cache_hits', 0)}")
    print(f"Cache Misses: {stats.get('cache_misses', 0)}")
    print(f"Hit Rate: {stats.get('hit_rate', 0):.2f}%")
    print(f"Exact Matches: {stats.get('exact_matches', 0)}")
    print(f"Fuzzy Matches: {stats.get('fuzzy_matches', 0)}")
    print("="*50 + "\n")


def main():
    """Main function"""
    print("="*50)
    print("Authority Cache Initialization")
    print("="*50 + "\n")
    
    # Initialize cache
    cache = initialize_cache()
    
    # Option to clear existing cache
    clear = input("Clear existing cache? (y/n): ").lower()
    if clear == 'y':
        cache.clear_cache()
        logger.info("Cache cleared")
    
    # Populate cache
    populate_option = input("\nPopulate cache with common terms? (y/n): ").lower()
    if populate_option == 'y':
        # Medical terms
        medical = input("  - Add medical terms? (y/n): ").lower()
        if medical == 'y':
            populate_common_medical_terms(cache)
        
        # General terms
        general = input("  - Add general terms? (y/n): ").lower()
        if general == 'y':
            populate_common_general_terms(cache)
    
    # Show statistics
    show_cache_stats(cache)
    
    print("Cache initialization completed!")


if __name__ == '__main__':
    main()
