"""
Example: Sử dụng Tool "get_classification_and_keywords"
Output: KHUNG PHÂN LOẠI và TỪ KHÓA CHUẨN
"""
import requests
import json


def example_medical_document():
    """
    Example 1: Tài liệu y học
    Output: NLM Classification + MESH Keywords
    """
    print("="*80)
    print("EXAMPLE 1: Tài liệu Y Học - NLM + MESH")
    print("="*80)
    
    # Input keywords từ OCR/Agent 4
    keywords = [
        "diabetes mellitus",
        "insulin therapy",
        "glucose monitoring",
        "cardiovascular complications"
    ]
    
    print(f"\n📥 INPUT Keywords:")
    for kw in keywords:
        print(f"   - {kw}")
    
    # Gọi API
    response = requests.post(
        'http://localhost:5000/api/authority/classification-keywords',
        json={
            'keywords': keywords,
            'subject_type': 'medical'
        }
    )
    
    result = response.json()
    
    if result['success']:
        output = result['output']
        
        # 1. KHUNG PHÂN LOẠI (Classification Framework)
        print(f"\n📊 KHUNG PHÂN LOẠI (Classification Framework):")
        classifications = output['classification_framework']
        
        if classifications:
            for cls in classifications:
                print(f"\n   Framework: {cls['framework']}")
                print(f"   Number: {cls['classification_number']}")
                print(f"   Description: {cls['description']}")
                print(f"   MARC Field: {cls['marc_field']}")
        else:
            print("   (Không tìm thấy classification numbers)")
        
        # 2. TỪ KHÓA CHUẨN (Controlled Keywords)
        print(f"\n🏷️  TỪ KHÓA CHUẨN (Controlled Keywords):")
        keywords_list = output['controlled_keywords']
        
        for kw in keywords_list:
            status = "✅" if kw['vocabulary'] != 'UNCONTROLLED' else "⚠️"
            print(f"\n   {status} Keyword: {kw['keyword']}")
            print(f"      Vocabulary: {kw['vocabulary']}")
            print(f"      Term ID: {kw['term_id']}")
            print(f"      Confidence: {kw['confidence']:.1f}%")
        
        # 3. MARC21 FIELDS
        print(f"\n📚 MARC21 FIELDS:")
        marc = result['marc_fields']
        
        print(f"\n   Classification Fields (050/060):")
        for field in marc['classification']:
            print(f"      {field}")
        
        print(f"\n   Subject Heading Fields (650):")
        for field in marc['subjects'][:5]:  # Show first 5
            print(f"      {field}")
        
        # 4. Summary
        print(f"\n📈 SUMMARY:")
        summary = result['summary']
        print(f"   Total Keywords: {summary['total_keywords']}")
        print(f"   Classifications Found: {summary['classifications_found']}")
        print(f"   Controlled Terms: {summary['controlled_terms_found']}")
        print(f"   Uncontrolled Terms: {summary['uncontrolled_terms']}")
        
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")


def example_computer_science_document():
    """
    Example 2: Tài liệu khoa học máy tính
    Output: LCC Classification + LCSH Keywords
    """
    print("\n\n" + "="*80)
    print("EXAMPLE 2: Tài liệu Khoa học - LCC + LCSH")
    print("="*80)
    
    keywords = [
        "machine learning",
        "artificial intelligence",
        "neural networks",
        "deep learning"
    ]
    
    print(f"\n📥 INPUT Keywords:")
    for kw in keywords:
        print(f"   - {kw}")
    
    response = requests.post(
        'http://localhost:5000/api/authority/classification-keywords',
        json={
            'keywords': keywords,
            'subject_type': 'science'
        }
    )
    
    result = response.json()
    
    if result['success']:
        output = result['output']
        
        print(f"\n📊 KHUNG PHÂN LOẠI (LCC):")
        for cls in output['classification_framework']:
            print(f"   {cls['classification_number']} - {cls['description']}")
        
        print(f"\n🏷️  TỪ KHÓA CHUẨN (LCSH):")
        for kw in output['controlled_keywords']:
            print(f"   • {kw['keyword']} ({kw['vocabulary']})")
        
        print(f"\n📚 MARC21:")
        print(f"   Classification: {result['marc_fields']['classification']}")
        print(f"   Subjects: {result['marc_fields']['subjects'][:3]}")


def example_integration_with_agent():
    """
    Example 3: Integration với Agent Pipeline
    """
    print("\n\n" + "="*80)
    print("EXAMPLE 3: Integration với Agent 4 Pipeline")
    print("="*80)
    
    # Giả lập Agent 4 extract keywords
    print("\n🤖 Agent 4: Extract Keywords from OCR")
    ocr_text = """
    Clinical Guidelines for Type 2 Diabetes Mellitus Management
    Including insulin therapy protocols and glucose monitoring strategies
    """
    
    # Simulated extraction (trong thực tế dùng AI)
    extracted_keywords = ["diabetes mellitus", "insulin", "glucose", "clinical guidelines"]
    print(f"   Extracted: {extracted_keywords}")
    
    # Gọi Authority Control Service
    print("\n🔄 Authority Control Service: Standardize Keywords")
    response = requests.post(
        'http://localhost:5000/api/authority/classification-keywords',
        json={
            'keywords': extracted_keywords,
            'subject_type': 'medical'
        }
    )
    
    result = response.json()
    
    if result['success']:
        # Output cho MARC Record
        print("\n📝 OUTPUT cho MARC Record:")
        
        output = result['output']
        marc = result['marc_fields']
        
        print("\n   1️⃣ KHUNG PHÂN LOẠI để xếp sách:")
        for cls in output['classification_framework']:
            print(f"      {cls['framework']} {cls['classification_number']}")
        
        print("\n   2️⃣ TỪ KHÓA để tìm kiếm:")
        for kw in output['controlled_keywords']:
            if kw['vocabulary'] != 'UNCONTROLLED':
                print(f"      • {kw['keyword']} ({kw['vocabulary']})")
        
        print("\n   3️⃣ MARC21 Fields sẵn sàng:")
        print(f"      Classification: {len(marc['classification'])} fields")
        print(f"      Subjects: {len(marc['subjects'])} fields")


def example_batch_processing():
    """
    Example 4: Batch Processing nhiều tài liệu
    """
    print("\n\n" + "="*80)
    print("EXAMPLE 4: Batch Processing Multiple Documents")
    print("="*80)
    
    documents = [
        {
            'title': 'Diabetes Treatment Guide',
            'keywords': ['diabetes', 'treatment', 'insulin'],
            'type': 'medical'
        },
        {
            'title': 'Machine Learning Handbook',
            'keywords': ['machine learning', 'algorithms', 'AI'],
            'type': 'science'
        },
        {
            'title': 'Ancient Roman History',
            'keywords': ['rome', 'history', 'archaeology'],
            'type': 'general'
        }
    ]
    
    for doc in documents:
        print(f"\n📄 Document: {doc['title']}")
        
        response = requests.post(
            'http://localhost:5000/api/authority/classification-keywords',
            json={
                'keywords': doc['keywords'],
                'subject_type': doc['type']
            }
        )
        
        result = response.json()
        
        if result['success']:
            summary = result['summary']
            print(f"   ✅ Processed: {summary['controlled_terms_found']}/{summary['total_keywords']} terms")
            print(f"   📊 Classifications: {summary['classifications_found']}")
        else:
            print(f"   ❌ Error: {result.get('error')}")


def example_compare_output_formats():
    """
    Example 5: So sánh output format của các tools
    """
    print("\n\n" + "="*80)
    print("EXAMPLE 5: So sánh Output của Tools khác nhau")
    print("="*80)
    
    keywords = ["diabetes", "insulin"]
    
    # Tool 1: map_keywords_to_authorities (old)
    print("\n🔧 Tool 1: map_keywords_to_authorities")
    response1 = requests.post(
        'http://localhost:5000/api/authority/map',
        json={'keywords': keywords, 'subject_type': 'medical'}
    )
    result1 = response1.json()
    print(f"   Output: authorities + marc_fields")
    print(f"   MARC Fields: {result1['marc21_fields']}")
    
    # Tool 2: get_classification_and_keywords (new)
    print("\n🔧 Tool 2: get_classification_and_keywords")
    response2 = requests.post(
        'http://localhost:5000/api/authority/classification-keywords',
        json={'keywords': keywords, 'subject_type': 'medical'}
    )
    result2 = response2.json()
    
    if result2['success']:
        output = result2['output']
        print(f"   Output: classification_framework + controlled_keywords")
        print(f"\n   KHUNG PHÂN LOẠI:")
        for cls in output['classification_framework']:
            print(f"      {cls['framework']} {cls['classification_number']}")
        print(f"\n   TỪ KHÓA:")
        for kw in output['controlled_keywords']:
            print(f"      {kw['keyword']} ({kw['vocabulary']})")
        print(f"\n   MARC Fields:")
        print(f"      Classification: {result2['marc_fields']['classification']}")
        print(f"      Subjects: {result2['marc_fields']['subjects']}")


def print_tool_info():
    """Print tool information"""
    print("\n" + "="*80)
    print("🤖 TOOL: get_classification_and_keywords")
    print("="*80)
    
    print("\n📖 Mô tả:")
    print("   Tool này trả về 2 thứ chính:")
    print("   1. KHUNG PHÂN LOẠI (Classification Framework)")
    print("      - LCC numbers (050 field) cho tài liệu general/science")
    print("      - NLM numbers (060 field) cho tài liệu medical")
    print("   2. TỪ KHÓA CHUẨN (Controlled Keywords)")
    print("      - MESH terms cho medical")
    print("      - LCSH terms cho general/science")
    
    print("\n📥 Input:")
    print("   - keywords: List of raw keywords")
    print("   - subject_type: 'medical' | 'general' | 'science'")
    
    print("\n📤 Output:")
    print("   - classification_framework: List[{framework, number, description}]")
    print("   - controlled_keywords: List[{keyword, vocabulary, term_id, confidence}]")
    print("   - marc_fields: {classification: [], subjects: []}")
    
    print("\n🔗 API Endpoint:")
    print("   POST /api/authority/classification-keywords")
    
    print("\n💡 Use Case:")
    print("   - Agent 4 extract keywords từ OCR")
    print("   - Call tool để standardize")
    print("   - Output: Khung phân loại + từ khóa chuẩn")
    print("   - Use trong MARC record generation")


def main():
    """Main runner"""
    print("\n" + "="*80)
    print("🎯 EXAMPLES: Tool get_classification_and_keywords")
    print("   Output: KHUNG PHÂN LOẠI + TỪ KHÓA CHUẨN")
    print("="*80)
    
    print("\nNote: Đảm bảo Authority Service đang chạy tại http://localhost:5000")
    input("\nPress Enter để bắt đầu examples...")
    
    # Print tool info
    print_tool_info()
    
    # Run examples
    try:
        example_medical_document()
        example_computer_science_document()
        example_integration_with_agent()
        example_batch_processing()
        example_compare_output_formats()
        
        print("\n\n" + "="*80)
        print("✅ All examples completed!")
        print("="*80)
        
        print("\n💡 Key Takeaways:")
        print("   1. Tool mới trả về output RÕ RÀNG:")
        print("      - KHUNG PHÂN LOẠI (LCC/NLM numbers)")
        print("      - TỪ KHÓA CHUẨN (MESH/LCSH terms)")
        print("   2. Output structured cho agent dễ sử dụng")
        print("   3. MARC fields ready cho integration")
        print("   4. Support batch processing")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Authority Service")
        print("   Please start the service first:")
        print("   cd backend")
        print("   python app.py")


if __name__ == "__main__":
    main()
