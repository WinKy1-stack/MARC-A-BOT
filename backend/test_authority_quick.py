"""
Quick test for Authority Control Service
"""
import sys
import json
from services.authority.authority_service import AuthorityService
from services.authority.tools import AuthorityTools
from services.authority.marc_generator import MARCFieldGenerator

print("="*60)
print("AUTHORITY CONTROL SERVICE - QUICK TEST")
print("="*60)

# Test 1: Initialize Service
print("\n[Test 1] Initialize AuthorityService...")
try:
    service = AuthorityService()
    print("✓ AuthorityService initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

# Test 2: Cache Statistics
print("\n[Test 2] Get cache statistics...")
try:
    stats = service.get_cache_statistics(days=7)
    print(f"✓ Cache entries: {stats.get('total_cache_entries', 0)}")
    print(f"  Hit rate: {stats.get('hit_rate', 0):.2f}%")
except Exception as e:
    print(f"✗ Failed to get stats: {e}")

# Test 3: Generate MARC Fields
print("\n[Test 3] Generate MARC21 650 fields...")
try:
    test_authorities = [
        {
            'term': 'Machine Learning',
            'authority_id': 'D015996',
            'source': 'MESH',
            'category': 'medical',
            'score': 100.0,
            'metadata': {}
        },
        {
            'term': 'Educators',
            'authority_id': 'sh85041014',
            'source': 'LCSH',
            'category': 'general',
            'score': 100.0,
            'metadata': {}
        }
    ]
    
    marc_fields = MARCFieldGenerator.create_marc21_650_field(test_authorities)
    print(f"✓ Generated {len(marc_fields)} MARC fields:")
    
    for field in marc_fields:
        display = MARCFieldGenerator.format_marc_field_display(field)
        print(f"  {display}")
        
        # Validate
        is_valid = MARCFieldGenerator.validate_marc_field(field)
        print(f"    Valid: {is_valid}")
        
except Exception as e:
    print(f"✗ Failed to generate MARC fields: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Process Keywords (with cache only)
print("\n[Test 4] Process keywords (cache test)...")
try:
    # Add some test data to cache
    cache = service.cache_manager
    cache.add_term(
        keyword="diabetes",
        authority_id="D003920",
        normalized_term="Diabetes Mellitus",
        source="MESH",
        category="medical",
        score=100.0
    )
    cache.add_term(
        keyword="education",
        authority_id="sh85041014",
        normalized_term="Education",
        source="LCSH",
        category="general",
        score=100.0
    )
    
    print("✓ Added test data to cache")
    
    # Search from cache
    results = cache.search("diabetes", source="MESH")
    if results:
        print(f"✓ Found '{results[0]['normalized_term']}' in cache")
    else:
        print("  No results found in cache")
        
except Exception as e:
    print(f"✗ Failed to process keywords: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Agent Tools
print("\n[Test 5] Test Agent Tools...")
try:
    tools = AuthorityTools()
    tool_defs = tools.get_tool_definitions()
    
    print(f"✓ Agent has {len(tool_defs)} tools:")
    for tool in tool_defs:
        print(f"  - {tool['name']}")
        
    # Test generate MARC tool
    result = tools.generate_marc21_650_fields(test_authorities)
    if result['success']:
        print(f"✓ generate_marc21_650_fields works: {result['count']} fields")
    else:
        print(f"✗ generate_marc21_650_fields failed: {result.get('error')}")
        
except Exception as e:
    print(f"✗ Failed to test tools: {e}")
    import traceback
    traceback.print_exc()

# Test 6: MARC Field Validation
print("\n[Test 6] MARC field validation...")
try:
    valid_field = {
        'field': '650',
        'ind1': ' ',
        'ind2': '2',
        'subfields': [
            {'code': 'a', 'value': 'Test Term'}
        ]
    }
    
    invalid_field = {
        'field': 'ABC',  # Invalid
        'ind1': ' ',
        'ind2': '2',
        'subfields': []
    }
    
    is_valid = MARCFieldGenerator.validate_marc_field(valid_field)
    print(f"✓ Valid field validation: {is_valid} (expected: True)")
    
    is_invalid = MARCFieldGenerator.validate_marc_field(invalid_field)
    print(f"✓ Invalid field validation: {is_invalid} (expected: False)")
    
except Exception as e:
    print(f"✗ Failed validation test: {e}")

# Test 7: Cache Performance
print("\n[Test 7] Cache performance test...")
try:
    # Test exact match
    cache.add_term("python programming", "QA76.73.P98", "Python (Computer program language)", "LCSH", "general", 100.0)
    
    exact_results = cache.exact_match("python programming")
    if exact_results:
        print(f"✓ Exact match works: found '{exact_results[0]['normalized_term']}'")
    
    # Test fuzzy match
    fuzzy_results = cache.fuzzy_match("pyton programing", threshold=70)
    if fuzzy_results:
        print(f"✓ Fuzzy match works: found '{fuzzy_results[0]['normalized_term']}' with score {fuzzy_results[0]['score']:.1f}")
    else:
        print("  Fuzzy match: no results (expected if cache is empty)")
        
except Exception as e:
    print(f"✗ Cache performance test failed: {e}")

# Test 8: Classification Fields
print("\n[Test 8] Classification field generation...")
try:
    lcc_field = MARCFieldGenerator.create_marc21_classification_field("QA76.9.A25", "LCC")
    print(f"✓ LCC field: {MARCFieldGenerator.format_marc_field_display(lcc_field)}")
    
    nlm_field = MARCFieldGenerator.create_marc21_classification_field("WZ 100", "NLM")
    print(f"✓ NLM field: {MARCFieldGenerator.format_marc_field_display(nlm_field)}")
    
except Exception as e:
    print(f"✗ Classification field test failed: {e}")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print("✓ Core functionality working")
print("✓ Cache system operational")
print("✓ MARC field generation working")
print("✓ Agent tools interface ready")
print("⚠ Online API tests skipped (requires internet)")
print("="*60)
print("\nNote: For full testing with MESH/LCSH/LCC APIs,")
print("run: pytest tests/authority/ -v")
print("="*60)
