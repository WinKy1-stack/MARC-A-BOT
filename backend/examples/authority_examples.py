"""
Example: Using Authority Control Service
Ví dụ sử dụng Authority Control Service
"""
from services.authority.authority_service import AuthorityService
from services.authority.tools import AuthorityTools
import json


def example_1_search_single_keyword():
    """Ví dụ 1: Tìm authority term cho một keyword"""
    print("\n=== Example 1: Search Single Keyword ===")
    
    service = AuthorityService()
    
    # Search for MESH term
    results = service.search_authority("diabetes", source="MESH")
    
    print(f"Found {len(results)} results for 'diabetes':")
    for result in results:
        print(f"  - {result['term']} ({result['source']}) - ID: {result['authority_id']}")


def example_2_map_multiple_keywords():
    """Ví dụ 2: Map nhiều keywords thành authority terms"""
    print("\n=== Example 2: Map Multiple Keywords ===")
    
    service = AuthorityService()
    
    keywords = ["diabetes", "hypertension", "insulin resistance"]
    result = service.process_keywords(keywords, subject_type="medical")
    
    print(f"Input: {keywords}")
    print(f"\nAuthorities found:")
    for auth in result['authorities']:
        print(f"  - {auth['term']} ({auth['source']}) - Score: {auth.get('final_score', auth['score'])}")
        
    print(f"\nMARC21 650 Fields:")
    for field in result['marc_fields']:
        subfield_str = ' '.join([f"${sf['code']} {sf['value']}" for sf in field['subfields']])
        print(f"  {field['field']} {field['ind1']}{field['ind2']} {subfield_str}")


def example_3_generate_marc_fields():
    """Ví dụ 3: Tạo MARC21 fields từ authority terms"""
    print("\n=== Example 3: Generate MARC21 Fields ===")
    
    from services.authority.marc_generator import MARCFieldGenerator
    
    authorities = [
        {
            'term': 'Machine Learning',
            'authority_id': 'D015996',
            'source': 'MESH',
            'category': 'medical',
            'score': 100.0,
            'metadata': {}
        },
        {
            'term': 'Artificial Intelligence',
            'authority_id': 'D001185',
            'source': 'MESH',
            'category': 'medical',
            'score': 95.0,
            'metadata': {}
        }
    ]
    
    marc_fields = MARCFieldGenerator.create_marc21_650_field(authorities)
    
    print("Generated MARC21 650 Fields:")
    for field in marc_fields:
        display = MARCFieldGenerator.format_marc_field_display(field)
        print(f"  {display}")
        
        # Validate
        is_valid = MARCFieldGenerator.validate_marc_field(field)
        print(f"    Valid: {is_valid}")


def example_4_validate_authority_term():
    """Ví dụ 4: Validate authority term"""
    print("\n=== Example 4: Validate Authority Term ===")
    
    service = AuthorityService()
    
    terms_to_validate = [
        ("Machine Learning", "MESH"),
        ("Python Programming", "LCSH"),
        ("Fake Term XYZ", "MESH")
    ]
    
    for term, source in terms_to_validate:
        is_valid = service.validate_term(term, source)
        print(f"  {term} ({source}): {'✓ Valid' if is_valid else '✗ Invalid'}")


def example_5_cache_statistics():
    """Ví dụ 5: Xem cache statistics"""
    print("\n=== Example 5: Cache Statistics ===")
    
    service = AuthorityService()
    stats = service.get_cache_statistics(days=7)
    
    print("Cache Performance (Last 7 days):")
    print(f"  Total Cache Entries: {stats.get('total_cache_entries', 0)}")
    print(f"  Total Queries: {stats.get('total_queries', 0)}")
    print(f"  Cache Hit Rate: {stats.get('hit_rate', 0):.2f}%")
    print(f"  Exact Matches: {stats.get('exact_matches', 0)}")
    print(f"  Fuzzy Matches: {stats.get('fuzzy_matches', 0)}")


def example_6_agent_tools():
    """Ví dụ 6: Sử dụng tools cho AI Agent"""
    print("\n=== Example 6: Agent Tools ===")
    
    tools = AuthorityTools()
    
    # Get tool definitions
    tool_defs = tools.get_tool_definitions()
    print(f"Available Tools: {len(tool_defs)}")
    for tool in tool_defs:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Use a tool
    print("\nUsing 'search_authority_terms' tool:")
    result = tools.search_authority_terms("diabetes", "MESH")
    
    if result['success']:
        print(f"  Found {result['count']} results")
        for res in result['results'][:3]:  # Show first 3
            print(f"    - {res['term']} (ID: {res['authority_id']})")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")


def example_7_real_world_medical_book():
    """Ví dụ 7: Xử lý keywords từ sách y khoa thực tế"""
    print("\n=== Example 7: Real-World Medical Book ===")
    
    service = AuthorityService()
    
    # Keywords từ một cuốn sách y khoa
    book_info = {
        'title': 'Diabetes Management and Care',
        'keywords': [
            'diabetes mellitus',
            'blood glucose',
            'insulin therapy',
            'diabetic complications',
            'metabolic syndrome'
        ]
    }
    
    print(f"Book: {book_info['title']}")
    print(f"Keywords: {', '.join(book_info['keywords'])}")
    
    result = service.process_keywords(
        book_info['keywords'],
        subject_type='medical'
    )
    
    print(f"\nProcessing Results:")
    print(f"  Total Authorities Found: {result['stats']['total_authorities']}")
    print(f"  MARC Fields Generated: {result['stats']['total_marc_fields']}")
    print(f"  Sources Used: {', '.join(result['stats']['sources_used'])}")
    
    print(f"\nMARC21 Record Fragment:")
    for field in result['marc_fields']:
        display = service.marc_generator.format_marc_field_display(field)
        print(f"  {display}")


def example_8_vietnamese_education_book():
    """Ví dụ 8: Xử lý keywords từ sách giáo dục Việt Nam"""
    print("\n=== Example 8: Vietnamese Education Book ===")
    
    service = AuthorityService()
    
    # Từ MARC record mẫu
    book_info = {
        'title': 'GS. Trần Hồng Quân với sự nghiệp giáo dục đào tạo Việt Nam',
        'keywords': ['Educators', 'Teachers'],
        'classification': 'LA2383.V52'
    }
    
    print(f"Book: {book_info['title']}")
    print(f"Classification (LCC): {book_info['classification']}")
    
    result = service.process_keywords(
        book_info['keywords'],
        subject_type='general'
    )
    
    print(f"\nSubject Headings (650 fields):")
    for field in result['marc_fields']:
        display = service.marc_generator.format_marc_field_display(field)
        print(f"  {display}")
    
    # Generate classification field
    from services.authority.marc_generator import MARCFieldGenerator
    class_field = MARCFieldGenerator.create_marc21_classification_field(
        book_info['classification'],
        'LCC'
    )
    
    print(f"\nClassification (050 field):")
    display = MARCFieldGenerator.format_marc_field_display(class_field)
    print(f"  {display}")


def example_9_batch_processing():
    """Ví dụ 9: Batch processing nhiều bộ keywords"""
    print("\n=== Example 9: Batch Processing ===")
    
    service = AuthorityService()
    
    batches = [
        ['diabetes', 'hypertension'],
        ['machine learning', 'artificial intelligence'],
        ['education', 'teaching']
    ]
    
    print(f"Processing {len(batches)} batches...")
    results = service.batch_process(batches, subject_type='general')
    
    for i, result in enumerate(results):
        print(f"\nBatch {i+1}:")
        print(f"  Keywords: {', '.join(batches[i])}")
        print(f"  Authorities: {result['stats']['total_authorities']}")
        print(f"  MARC Fields: {result['stats']['total_marc_fields']}")


def example_10_export_to_json():
    """Ví dụ 10: Export kết quả ra JSON"""
    print("\n=== Example 10: Export to JSON ===")
    
    service = AuthorityService()
    
    keywords = ['diabetes', 'hypertension']
    result = service.process_keywords(keywords, subject_type='medical')
    
    # Export to JSON
    output = {
        'input': {
            'keywords': keywords,
            'subject_type': 'medical'
        },
        'output': {
            'authorities': result['authorities'],
            'marc_fields': result['marc_fields'],
            'statistics': result['stats']
        }
    }
    
    json_output = json.dumps(output, indent=2, ensure_ascii=False)
    
    print("JSON Output:")
    print(json_output)
    
    # Save to file (optional)
    # with open('authority_output.json', 'w', encoding='utf-8') as f:
    #     f.write(json_output)


if __name__ == '__main__':
    print("=" * 60)
    print("Authority Control Service - Examples")
    print("=" * 60)
    
    # Run all examples
    examples = [
        example_1_search_single_keyword,
        example_2_map_multiple_keywords,
        example_3_generate_marc_fields,
        example_4_validate_authority_term,
        example_5_cache_statistics,
        example_6_agent_tools,
        example_7_real_world_medical_book,
        example_8_vietnamese_education_book,
        example_9_batch_processing,
        example_10_export_to_json
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
