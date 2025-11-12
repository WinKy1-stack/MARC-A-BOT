"""
Script test riêng biệt cho API endpoints
Chạy Flask server trước khi test script này

Usage:
    Terminal 1: python app.py
    Terminal 2: python scripts/test_endpoints.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/authority"

def print_header(title):
    """In header cho mỗi test"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_health():
    """Test 1: Health check endpoint"""
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_get_tools():
    """Test 2: Lấy danh sách tools"""
    print_header("TEST 2: Get Tools List")
    try:
        response = requests.get(f"{BASE_URL}/tools", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Số lượng tools: {len(data.get('tools', []))}")
        print(f"Tools:")
        for tool in data.get('tools', []):
            print(f"  - {tool['name']}: {tool['description'][:50]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_generate_marc():
    """Test 3: Generate MARC fields"""
    print_header("TEST 3: Generate MARC Fields")
    try:
        payload = {
            "authorities": [
                {
                    "term": "Machine Learning",
                    "source": "MESH",
                    "id": "D015996",
                    "subject_type": "medical"
                },
                {
                    "term": "Python (Computer program language)",
                    "source": "LCSH",
                    "id": "sh95008857",
                    "subject_type": "general"
                }
            ]
        }
        response = requests.post(
            f"{BASE_URL}/generate-marc",
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"MARC Fields Generated:")
        for field in data.get('marc_fields', []):
            print(f"  {field}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_validate_term():
    """Test 4: Validate authority term"""
    print_header("TEST 4: Validate Authority Term")
    try:
        # Test valid field
        payload = {
            "marc_field": "650  2 $a Machine Learning $2 mesh $0 (DNLM)D015996"
        }
        response = requests.post(
            f"{BASE_URL}/validate",
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Valid field test:")
        print(f"  Is Valid: {data.get('is_valid')}")
        print(f"  Errors: {data.get('errors', [])}")
        
        # Test invalid field
        payload = {
            "marc_field": "650 INVALID FIELD"
        }
        response = requests.post(
            f"{BASE_URL}/validate",
            json=payload,
            timeout=5
        )
        data = response.json()
        print(f"\nInvalid field test:")
        print(f"  Is Valid: {data.get('is_valid')}")
        print(f"  Errors: {data.get('errors', [])}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_cache_stats():
    """Test 5: Cache statistics"""
    print_header("TEST 5: Cache Statistics")
    try:
        response = requests.get(
            f"{BASE_URL}/cache/stats",
            params={"days": 7},
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        stats = data.get('statistics', {})
        print(f"Cache Statistics:")
        print(f"  Total Entries: {stats.get('total_entries', 0)}")
        print(f"  Hit Rate: {stats.get('hit_rate', 0):.2f}%")
        print(f"  Total Hits: {stats.get('total_hits', 0)}")
        print(f"  Total Misses: {stats.get('total_misses', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_search_authority():
    """Test 6: Search authority (cần internet)"""
    print_header("TEST 6: Search Authority (Online)")
    try:
        payload = {
            "keyword": "diabetes",
            "source": "MESH"
        }
        response = requests.post(
            f"{BASE_URL}/search",
            json=payload,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        results = data.get('results', [])
        print(f"Kết quả tìm kiếm: {len(results)} terms")
        if results:
            print(f"Top 3 results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.get('term')} (score: {result.get('score', 0):.2f})")
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Cần internet connection: {e}")
        return False

def test_map_keywords():
    """Test 7: Map keywords (cần internet)"""
    print_header("TEST 7: Map Keywords (Online)")
    try:
        payload = {
            "keywords": ["python programming", "machine learning"],
            "subject_type": "general"
        }
        response = requests.post(
            f"{BASE_URL}/map",
            json=payload,
            timeout=15
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        mappings = data.get('mappings', [])
        print(f"Mapped {len(mappings)} keywords:")
        for mapping in mappings:
            keyword = mapping.get('keyword')
            authorities = mapping.get('authorities', [])
            print(f"\n  '{keyword}' →")
            for auth in authorities:
                print(f"    - {auth.get('term')} ({auth.get('source')}, score: {auth.get('score', 0):.2f})")
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Cần internet connection: {e}")
        return False

def wait_for_server():
    """Đợi server khởi động"""
    print("⏳ Đang kiểm tra kết nối với Flask server...")
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server đã sẵn sàng!\n")
                return True
        except:
            if attempt < max_attempts - 1:
                print(f"   Attempt {attempt + 1}/{max_attempts}... waiting 2s")
                time.sleep(2)
    
    print("\n❌ Không thể kết nối với server!")
    print("\n📌 Hướng dẫn:")
    print("   1. Mở terminal mới")
    print("   2. cd c:\\Workspace\\Bien_muc\\MARC-A-BOT\\backend")
    print("   3. python app.py")
    print("   4. Chạy lại script này\n")
    return False

def main():
    """Chạy tất cả tests"""
    print("\n" + "="*60)
    print("  AUTHORITY CONTROL SERVICE - API ENDPOINT TESTS")
    print("="*60)
    
    if not wait_for_server():
        return
    
    # Danh sách tests
    tests = [
        ("Health Check", test_health),
        ("Get Tools", test_get_tools),
        ("Generate MARC", test_generate_marc),
        ("Validate Term", test_validate_term),
        ("Cache Stats", test_cache_stats),
        ("Search Authority (Online)", test_search_authority),
        ("Map Keywords (Online)", test_map_keywords),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
            time.sleep(0.5)  # Delay nhỏ giữa các tests
        except Exception as e:
            print(f"\n❌ Test '{name}' failed: {e}")
            results.append((name, False))
    
    # Tổng kết
    print_header("KẾT QUẢ TEST")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {name}")
    
    print(f"\n{'='*60}")
    print(f"Tổng kết: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}%)")
    print(f"{'='*60}\n")
    
    # Ghi chú
    if passed_count < total_count:
        print("📝 Lưu ý:")
        print("   - Tests 6-7 cần internet connection")
        print("   - Nếu offline, kết quả 5/7 pass là bình thường")
        print("   - Core functionality (tests 1-5) hoạt động độc lập\n")

if __name__ == "__main__":
    main()
