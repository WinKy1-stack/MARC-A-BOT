"""
Demo script để showcase Authority Control Service
Minh họa các tính năng chính của hệ thống

Usage:
    python scripts/demo_authority_service.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.authority.authority_service import AuthorityService
from services.authority.marc_generator import MARCFieldGenerator
from services.authority.cache.cache_manager import AuthorityCacheManager

def print_header(title):
    """In header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def demo_cache_operations():
    """Demo 1: Cache operations"""
    print_header("DEMO 1: CACHE OPERATIONS")
    
    from services.authority.config import CACHE_DB_PATH
    cache = AuthorityCacheManager(CACHE_DB_PATH)
    
    # Thêm một số terms vào cache
    print("📝 Thêm authority terms vào cache...")
    cache.add_term(
        keyword="diabetes",
        authority_id="D003920",
        normalized_term="Diabetes Mellitus",
        source="MESH",
        category="medical",
        score=100.0
    )
    cache.add_term(
        keyword="python programming",
        authority_id="sh95008857",
        normalized_term="Python (Computer program language)",
        source="LCSH",
        category="general",
        score=100.0
    )
    cache.add_term(
        keyword="machine learning",
        authority_id="D015996",
        normalized_term="Machine Learning",
        source="MESH",
        category="medical",
        score=100.0
    )
    print("✅ Đã thêm 3 terms vào cache\n")
    
    # Exact match
    print("🔍 Test exact match: 'diabetes'")
    result = cache.exact_match("diabetes")
    if result:
        print(f"   ✅ Tìm thấy: {result['normalized_term']} ({result['source']})")
    else:
        print("   ❌ Không tìm thấy")
    
    # Fuzzy match
    print("\n🔍 Test fuzzy match: 'pyton programing' (có lỗi chính tả)")
    results = cache.fuzzy_match("pyton programing", threshold=70)
    if results:
        for r in results[:3]:
            print(f"   ✅ {r['normalized_term']} - Score: {r['score']:.2f}")
    else:
        print("   ❌ Không tìm thấy")
    
    # Search
    print("\n🔍 Search tất cả MESH terms:")
    results = cache.search("", source="MESH")
    print(f"   Tìm thấy {len(results)} MESH terms")
    for r in results:
        print(f"   - {r['normalized_term']}")
    
    # Stats
    print("\n📊 Cache Statistics:")
    stats = cache.get_cache_stats()
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Hit rate: {stats['hit_rate']:.2f}%")
    print(f"   Total hits: {stats['total_hits']}")
    print(f"   Total misses: {stats['total_misses']}")

def demo_marc_generation():
    """Demo 2: MARC field generation"""
    print_header("DEMO 2: MARC21 FIELD GENERATION")
    
    # Test authorities
    authorities = [
        {
            'term': 'Machine Learning',
            'source': 'MESH',
            'id': 'D015996',
            'subject_type': 'medical'
        },
        {
            'term': 'Python (Computer program language)',
            'source': 'LCSH',
            'id': 'sh95008857',
            'subject_type': 'general'
        },
        {
            'term': 'Education',
            'source': 'LCSH',
            'id': 'sh85040989',
            'subject_type': 'general'
        }
    ]
    
    print("📝 Generate MARC 650 fields (Subject Headings):\n")
    for auth in authorities:
        field = MARCFieldGenerator.create_marc21_650_field([auth])
        if field:
            print(f"   {field[0]}")
    
    # Classification fields
    print("\n📝 Generate Classification fields:")
    
    # LCC
    lcc_auth = {
        'term': 'Computer Science',
        'source': 'LCC',
        'id': 'QA76',
        'subject_type': 'general'
    }
    lcc_field = MARCFieldGenerator.create_marc21_classification_field([lcc_auth])
    if lcc_field:
        print(f"   050 (LCC): {lcc_field[0]}")
    
    # NLM
    nlm_auth = {
        'term': 'Diabetes Mellitus',
        'source': 'NLM',
        'id': 'WK 810',
        'subject_type': 'medical'
    }
    nlm_field = MARCFieldGenerator.create_marc21_classification_field([nlm_auth])
    if nlm_field:
        print(f"   060 (NLM): {nlm_field[0]}")
    
    # Validation
    print("\n✅ Validate MARC fields:")
    valid_field = "650  2 $a Machine Learning $2 mesh $0 (DNLM)D015996"
    invalid_field = "650 INVALID"
    
    print(f"   '{valid_field}'")
    print(f"   → Valid: {MARCFieldGenerator.validate_marc_field(valid_field)}")
    
    print(f"\n   '{invalid_field}'")
    print(f"   → Valid: {MARCFieldGenerator.validate_marc_field(invalid_field)}")

def demo_authority_service():
    """Demo 3: Authority Service"""
    print_header("DEMO 3: AUTHORITY SERVICE")
    
    service = AuthorityService()
    
    print("🔍 Process keywords (offline mode - dùng cache):\n")
    
    # Process với cache
    keywords = ["diabetes", "python programming", "machine learning"]
    
    for keyword in keywords:
        print(f"   Keyword: '{keyword}'")
        results = service.process_keywords([keyword], subject_type="general")
        
        if results and results[0].get('authorities'):
            for auth in results[0]['authorities'][:2]:  # Top 2
                print(f"      → {auth['term']} ({auth['source']}, score: {auth['score']:.2f})")
        else:
            print(f"      → Không tìm thấy (cần internet hoặc chưa có trong cache)")
        print()
    
    # Cache statistics
    print("📊 Final Cache Statistics:")
    stats = service.get_cache_statistics()
    print(f"   Total entries: {stats.get('total_entries', 0)}")
    print(f"   Hit rate: {stats.get('hit_rate', 0):.2f}%")

def demo_agent_tools():
    """Demo 4: Agent Tools"""
    print_header("DEMO 4: AGENT TOOLS INTERFACE")
    
    from services.authority.tools import (
        search_authority_terms,
        map_keywords_to_authorities,
        validate_authority_term,
        generate_marc21_650_fields,
        get_cache_statistics
    )
    
    print("🤖 Available tools for AI Agent:\n")
    
    tools = [
        search_authority_terms,
        map_keywords_to_authorities,
        validate_authority_term,
        generate_marc21_650_fields,
        get_cache_statistics
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool.__name__}")
        print(f"      {tool.__doc__.strip().split(chr(10))[0]}")
        print()
    
    # Demo search tool
    print("🔍 Demo: search_authority_terms('diabetes', 'MESH'):")
    results = search_authority_terms(keyword="diabetes", source="MESH")
    if results:
        print(f"   Tìm thấy {len(results)} results")
        for r in results[:2]:
            print(f"   - {r.get('term', 'N/A')} (score: {r.get('score', 0):.2f})")
    else:
        print("   Không tìm thấy (cần internet hoặc cache)")
    
    # Demo generate MARC tool
    print("\n📝 Demo: generate_marc21_650_fields(authorities):")
    test_authorities = [
        {
            'term': 'Diabetes Mellitus',
            'source': 'MESH',
            'id': 'D003920',
            'subject_type': 'medical'
        }
    ]
    marc_fields = generate_marc21_650_fields(authorities=test_authorities)
    for field in marc_fields:
        print(f"   {field}")
    
    # Demo cache stats
    print("\n📊 Demo: get_cache_statistics():")
    stats = get_cache_statistics()
    print(f"   Total entries: {stats.get('total_entries', 0)}")
    print(f"   Hit rate: {stats.get('hit_rate', 0):.2f}%")

def main():
    """Chạy tất cả demos"""
    print("\n" + "="*70)
    print("  AUTHORITY CONTROL SERVICE - DEMONSTRATION")
    print("="*70)
    print("\n📚 Hệ thống chuẩn hóa từ khóa và tạo MARC21 fields")
    print("   Kết nối với: MESH, LCSH, LCC, NLM")
    print("   Tính năng: Cache, Fuzzy matching, MARC generation")
    
    try:
        demo_cache_operations()
        demo_marc_generation()
        demo_authority_service()
        demo_agent_tools()
        
        print_header("DEMO HOÀN TẤT")
        print("✅ Tất cả tính năng đã được demo thành công!")
        print("\n📌 Bước tiếp theo:")
        print("   1. Chạy full tests: python scripts/run_full_tests.py")
        print("   2. Khởi động API server: python scripts/start_server.py")
        print("   3. Test API endpoints: python scripts/test_endpoints.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
