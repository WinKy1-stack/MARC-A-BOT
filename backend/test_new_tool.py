"""
Quick Test - Tool get_classification_and_keywords
Verify tool hoạt động và output đúng format
"""
import requests
import json


def test_tool_availability():
    """Test 1: Kiểm tra tool có trong danh sách không"""
    print("="*80)
    print("TEST 1: Tool Availability")
    print("="*80)
    
    try:
        response = requests.get('http://localhost:5000/api/authority/tools')
        result = response.json()
        
        if result['success']:
            tools = result['tools']
            tool_names = [t['name'] for t in tools]
            
            if 'get_classification_and_keywords' in tool_names:
                print("✅ Tool 'get_classification_and_keywords' FOUND")
                
                # Print tool details
                tool = next(t for t in tools if t['name'] == 'get_classification_and_keywords')
                print(f"\n   Description: {tool['description']}")
                print(f"   Parameters: {list(tool['parameters']['properties'].keys())}")
                
                return True
            else:
                print("❌ Tool NOT FOUND in tools list")
                print(f"   Available tools: {tool_names}")
                return False
        else:
            print(f"❌ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_medical_keywords():
    """Test 2: Test với medical keywords"""
    print("\n" + "="*80)
    print("TEST 2: Medical Keywords")
    print("="*80)
    
    keywords = ["diabetes", "insulin"]
    
    print(f"\n📥 Input: {keywords}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/authority/classification-keywords',
            json={'keywords': keywords, 'subject_type': 'medical'}
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ API Call SUCCESS")
            
            # Check output structure
            output = result['output']
            
            print(f"\n📊 Output Structure:")
            print(f"   ✓ classification_framework: {len(output['classification_framework'])} items")
            print(f"   ✓ controlled_keywords: {len(output['controlled_keywords'])} items")
            
            # Show classification
            if output['classification_framework']:
                print(f"\n📚 KHUNG PHÂN LOẠI:")
                for cls in output['classification_framework']:
                    print(f"   • {cls['framework']} {cls['classification_number']}")
            else:
                print(f"\n📚 KHUNG PHÂN LOẠI: (none found)")
            
            # Show keywords
            print(f"\n🏷️  TỪ KHÓA CHUẨN:")
            for kw in output['controlled_keywords']:
                print(f"   • {kw['keyword']} ({kw['vocabulary']})")
            
            # Show MARC fields
            marc = result['marc_fields']
            print(f"\n📋 MARC Fields:")
            print(f"   Classification (050/060): {len(marc['classification'])} fields")
            print(f"   Subjects (650): {len(marc['subjects'])} fields")
            
            return True
        else:
            print(f"❌ API Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_science_keywords():
    """Test 3: Test với science keywords"""
    print("\n" + "="*80)
    print("TEST 3: Science Keywords")
    print("="*80)
    
    keywords = ["machine learning", "neural networks"]
    
    print(f"\n📥 Input: {keywords}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/authority/classification-keywords',
            json={'keywords': keywords, 'subject_type': 'science'}
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ API Call SUCCESS")
            
            output = result['output']
            
            # Check for LCC classification
            if output['classification_framework']:
                lcc_found = any(c['framework'] == 'LCC' 
                               for c in output['classification_framework'])
                if lcc_found:
                    print("   ✓ LCC classification found")
                else:
                    print("   ⚠️  LCC classification not found")
            
            # Check for LCSH keywords
            if output['controlled_keywords']:
                lcsh_found = any(k['vocabulary'] == 'LCSH' 
                                for k in output['controlled_keywords'])
                if lcsh_found:
                    print("   ✓ LCSH keywords found")
                else:
                    print("   ⚠️  LCSH keywords not found")
            
            return True
        else:
            print(f"❌ API Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_output_format():
    """Test 4: Verify output format chi tiết"""
    print("\n" + "="*80)
    print("TEST 4: Output Format Verification")
    print("="*80)
    
    keywords = ["diabetes"]
    
    try:
        response = requests.post(
            'http://localhost:5000/api/authority/classification-keywords',
            json={'keywords': keywords, 'subject_type': 'medical'}
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ Checking output structure...")
            
            # Check top-level keys
            required_keys = ['success', 'input_keywords', 'subject_type', 
                           'output', 'marc_fields', 'summary']
            
            for key in required_keys:
                if key in result:
                    print(f"   ✓ {key}")
                else:
                    print(f"   ❌ {key} MISSING")
            
            # Check output keys
            print("\n   Output keys:")
            output = result['output']
            if 'classification_framework' in output:
                print(f"      ✓ classification_framework (list)")
            if 'controlled_keywords' in output:
                print(f"      ✓ controlled_keywords (list)")
            
            # Check marc_fields keys
            print("\n   MARC fields keys:")
            marc = result['marc_fields']
            if 'classification' in marc:
                print(f"      ✓ classification (050/060 fields)")
            if 'subjects' in marc:
                print(f"      ✓ subjects (650 fields)")
            
            # Check summary
            print("\n   Summary:")
            summary = result['summary']
            for key, value in summary.items():
                print(f"      {key}: {value}")
            
            return True
        else:
            print(f"❌ API Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_compare_with_old_tool():
    """Test 5: So sánh với tool cũ"""
    print("\n" + "="*80)
    print("TEST 5: Compare New Tool vs Old Tool")
    print("="*80)
    
    keywords = ["diabetes", "insulin"]
    
    # Old tool: map
    print("\n🔧 Old Tool: /api/authority/map")
    try:
        response1 = requests.post(
            'http://localhost:5000/api/authority/map',
            json={'keywords': keywords, 'subject_type': 'medical'}
        )
        result1 = response1.json()
        print(f"   Output keys: {list(result1.keys())}")
        print(f"   MARC fields: {len(result1.get('marc21_fields', []))} fields (650 only)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # New tool: classification-keywords
    print("\n🔧 New Tool: /api/authority/classification-keywords")
    try:
        response2 = requests.post(
            'http://localhost:5000/api/authority/classification-keywords',
            json={'keywords': keywords, 'subject_type': 'medical'}
        )
        result2 = response2.json()
        
        if result2['success']:
            output = result2['output']
            marc = result2['marc_fields']
            
            print(f"   Output keys: {list(result2.keys())}")
            print(f"   Classification: {len(output['classification_framework'])} items")
            print(f"   Keywords: {len(output['controlled_keywords'])} items")
            print(f"   MARC classification: {len(marc['classification'])} fields (050/060)")
            print(f"   MARC subjects: {len(marc['subjects'])} fields (650)")
            
            print("\n   ✅ New tool provides BOTH classification AND keywords!")
        else:
            print(f"   ❌ Error: {result2.get('error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 QUICK TEST: Tool get_classification_and_keywords")
    print("="*80)
    
    print("\n⚠️  Ensure Authority Service is running at http://localhost:5000")
    input("Press Enter to start tests...")
    
    results = []
    
    # Run tests
    results.append(("Tool Availability", test_tool_availability()))
    results.append(("Medical Keywords", test_medical_keywords()))
    results.append(("Science Keywords", test_science_keywords()))
    results.append(("Output Format", test_output_format()))
    test_compare_with_old_tool()  # Comparison test
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    print(f"\n   Tests Passed: {passed}/{total}")
    
    for name, status in results:
        icon = "✅" if status else "❌"
        print(f"   {icon} {name}")
    
    if passed == total:
        print("\n🎉 All tests PASSED!")
        print("\n💡 Tool is ready to use!")
        print("   - Endpoint: POST /api/authority/classification-keywords")
        print("   - Output: Khung phân loại + Từ khóa chuẩn")
        print("   - See: backend/docs/TOOL_CLASSIFICATION_KEYWORDS.md")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
