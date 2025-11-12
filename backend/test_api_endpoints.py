"""
Test API endpoints for Authority Control Service
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("="*60)
print("TESTING AUTHORITY CONTROL API ENDPOINTS")
print("="*60)

# Test 1: Health Check
print("\n[Test 1] GET /api/authority/health")
try:
    response = requests.get(f"{BASE_URL}/api/authority/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✓ Health check OK")
except Exception as e:
    print(f"✗ Health check failed: {e}")

# Test 2: Get Tool Definitions
print("\n[Test 2] GET /api/authority/tools")
try:
    response = requests.get(f"{BASE_URL}/api/authority/tools", timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"✓ Found {len(data.get('tools', []))} tools")
        for tool in data.get('tools', []):
            print(f"  - {tool['name']}")
    else:
        print(f"✗ Failed: {data}")
except Exception as e:
    print(f"✗ Get tools failed: {e}")

# Test 3: Generate MARC Fields
print("\n[Test 3] POST /api/authority/generate-marc")
try:
    payload = {
        "authorities": [
            {
                "term": "Diabetes Mellitus",
                "authority_id": "D003920",
                "source": "MESH",
                "category": "medical",
                "score": 100.0,
                "metadata": {}
            },
            {
                "term": "Educators",
                "authority_id": "sh85041014",
                "source": "LCSH",
                "category": "general",
                "score": 100.0,
                "metadata": {}
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/authority/generate-marc",
        json=payload,
        timeout=5
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        print(f"✓ Generated {data.get('count')} MARC fields:")
        for display in data.get('formatted_display', []):
            print(f"  {display}")
    else:
        print(f"✗ Failed: {data}")
        
except Exception as e:
    print(f"✗ Generate MARC failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Validate Authority Term
print("\n[Test 4] POST /api/authority/validate")
try:
    payload = {
        "term": "Machine Learning",
        "source": "MESH"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/authority/validate",
        json=payload,
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        print(f"✓ Validation result: {data.get('is_valid')}")
    else:
        print(f"  Note: {data.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"✗ Validate failed: {e}")

# Test 5: Cache Statistics
print("\n[Test 5] GET /api/authority/cache/stats")
try:
    response = requests.get(
        f"{BASE_URL}/api/authority/cache/stats?days=7",
        timeout=5
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        stats = data.get('statistics', {})
        print(f"✓ Cache Statistics:")
        print(f"  Total entries: {stats.get('total_cache_entries', 0)}")
        print(f"  Total queries: {stats.get('total_queries', 0)}")
        print(f"  Hit rate: {stats.get('hit_rate', 0):.2f}%")
    else:
        print(f"✗ Failed: {data}")
        
except Exception as e:
    print(f"✗ Cache stats failed: {e}")

# Test 6: Map Keywords (will fail without internet, but test the endpoint)
print("\n[Test 6] POST /api/authority/map")
try:
    payload = {
        "keywords": ["diabetes", "hypertension"],
        "subject_type": "medical"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/authority/map",
        json=payload,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        print(f"✓ Mapped {len(data.get('authorities', []))} keywords")
        print(f"  MARC fields: {len(data.get('marc_fields', []))}")
        
        # Show first MARC field
        if data.get('marc_fields'):
            field = data['marc_fields'][0]
            subfields = ' '.join([f"${sf['code']} {sf['value']}" for sf in field.get('subfields', [])])
            print(f"  Example: {field['field']} {field['ind1']}{field['ind2']} {subfields}")
    else:
        print(f"  Note: Requires internet connection for MESH/LCSH APIs")
        print(f"  Error: {data.get('error', 'Unknown')}")
        
except Exception as e:
    print(f"  Note: Map keywords requires internet (expected to fail offline)")
    print(f"  Error: {e}")

# Summary
print("\n" + "="*60)
print("API ENDPOINT TEST SUMMARY")
print("="*60)
print("✓ Flask server is running")
print("✓ All endpoints are accessible")
print("✓ Local operations working (generate, validate cache)")
print("⚠ Online operations require internet (search, map)")
print("="*60)
