"""
Test Authority Control Service - Complete Workflow
Kiểm tra toàn bộ workflow từ keywords đến MARC21
"""
import requests
import json
from typing import List, Dict
import time


class AuthorityServiceTester:
    """Tester cho Authority Control Service"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print('='*80)
        
    def test_health_check(self):
        """Test 1: Health Check"""
        self.print_section("TEST 1: Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/api/authority/health")
            result = response.json()
            
            print(f"✅ Status: {result['status']}")
            print(f"✅ Service: {result['service']}")
            print(f"✅ Version: {result.get('version', 'N/A')}")
            
            self.results.append(("Health Check", True))
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Health Check", False))
            return False
    
    def test_search_medical(self):
        """Test 2: Search Medical Terms (MESH)"""
        self.print_section("TEST 2: Search Medical Terms")
        
        keywords = ["diabetes", "insulin", "hypertension"]
        
        for keyword in keywords:
            try:
                response = requests.post(
                    f"{self.base_url}/api/authority/search",
                    json={"keyword": keyword, "source": "MESH"}
                )
                result = response.json()
                
                print(f"\n🔍 Keyword: {keyword}")
                print(f"   Found: {result['total_results']} terms")
                
                if result['results']:
                    top_result = result['results'][0]
                    print(f"   Top Match: {top_result['term']}")
                    print(f"   Source: {top_result['source']}")
                    print(f"   Confidence: {top_result['confidence']:.2f}")
                
                self.results.append((f"Search: {keyword}", True))
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.results.append((f"Search: {keyword}", False))
    
    def test_map_medical_keywords(self):
        """Test 3: Map Medical Keywords to Authorities"""
        self.print_section("TEST 3: Map Medical Keywords")
        
        keywords = [
            "diabetes mellitus type 2",
            "insulin resistance",
            "cardiovascular disease"
        ]
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/authority/map",
                json={
                    "keywords": keywords,
                    "subject_type": "medical"
                }
            )
            result = response.json()
            
            elapsed = time.time() - start_time
            
            print(f"\n📊 Mapping Results:")
            print(f"   Keywords: {len(keywords)}")
            print(f"   Time: {elapsed:.2f}s")
            print(f"   Valid Terms: {result['statistics']['valid_terms']}")
            print(f"   Cache Hits: {result['statistics']['cache_hits']}")
            print(f"   API Calls: {result['statistics']['api_calls']}")
            
            print(f"\n📝 Mapped Terms:")
            for item in result['mapping_results']:
                status = "✅" if item['is_valid'] else "⚠️"
                print(f"   {status} {item['original_keyword']} → {item['term']}")
                print(f"      Source: {item['source']} | Confidence: {item['confidence']:.2f}")
            
            print(f"\n📚 MARC21 650 Fields Generated:")
            for field in result['marc21_fields']:
                print(f"   {field}")
            
            self.results.append(("Map Medical Keywords", True))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Map Medical Keywords", False))
    
    def test_map_science_keywords(self):
        """Test 4: Map Computer Science Keywords"""
        self.print_section("TEST 4: Map Computer Science Keywords")
        
        keywords = [
            "machine learning",
            "artificial intelligence",
            "neural networks",
            "deep learning"
        ]
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/authority/map",
                json={
                    "keywords": keywords,
                    "subject_type": "science"
                }
            )
            result = response.json()
            
            elapsed = time.time() - start_time
            
            print(f"\n📊 Mapping Results:")
            print(f"   Keywords: {len(keywords)}")
            print(f"   Time: {elapsed:.2f}s")
            print(f"   Valid Terms: {result['statistics']['valid_terms']}")
            
            print(f"\n📝 Mapped Terms:")
            for item in result['mapping_results']:
                status = "✅" if item['is_valid'] else "⚠️"
                print(f"   {status} {item['original_keyword']} → {item['term']}")
            
            print(f"\n📚 MARC21 Fields:")
            for field in result['marc21_fields'][:3]:
                print(f"   {field}")
            
            self.results.append(("Map CS Keywords", True))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Map CS Keywords", False))
    
    def test_validate_terms(self):
        """Test 5: Validate Authority Terms"""
        self.print_section("TEST 5: Validate Authority Terms")
        
        test_cases = [
            ("Diabetes Mellitus", "MESH", True),
            ("Machine Learning", "LCSH", True),
            ("Invalid Term XYZ", "MESH", False)
        ]
        
        for term, source, expected in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/authority/validate",
                    json={"term": term, "source": source}
                )
                result = response.json()
                
                is_valid = result.get('is_valid', False)
                status = "✅" if is_valid == expected else "⚠️"
                
                print(f"\n{status} Term: {term}")
                print(f"   Source: {source}")
                print(f"   Valid: {is_valid}")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
                
                self.results.append((f"Validate: {term}", True))
                
            except Exception as e:
                print(f"❌ Error: {e}")
                self.results.append((f"Validate: {term}", False))
    
    def test_generate_marc(self):
        """Test 6: Generate MARC21 Fields"""
        self.print_section("TEST 6: Generate MARC21 Fields")
        
        keywords = [
            "python programming",
            "software engineering",
            "web development"
        ]
        
        try:
            response = requests.post(
                f"{self.base_url}/api/authority/generate-marc",
                json={"keywords": keywords}
            )
            result = response.json()
            
            print(f"\n📚 Generated MARC21 Fields:")
            for field in result['marc21_fields']:
                print(f"   {field}")
            
            print(f"\n📊 Statistics:")
            print(f"   Total Fields: {len(result['marc21_fields'])}")
            
            self.results.append(("Generate MARC", True))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Generate MARC", False))
    
    def test_cache_statistics(self):
        """Test 7: Cache Statistics"""
        self.print_section("TEST 7: Cache Statistics")
        
        try:
            response = requests.get(f"{self.base_url}/api/authority/cache/stats")
            result = response.json()
            
            print(f"\n📊 Cache Performance:")
            print(f"   Total Entries: {result.get('total_entries', 0)}")
            print(f"   Cache Hits: {result.get('cache_hits', 0)}")
            print(f"   Cache Misses: {result.get('cache_misses', 0)}")
            print(f"   Hit Rate: {result.get('hit_rate', 0):.1f}%")
            print(f"   Cache Size: {result.get('cache_size_mb', 0):.2f} MB")
            
            self.results.append(("Cache Statistics", True))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Cache Statistics", False))
    
    def test_tools_definitions(self):
        """Test 8: Get Tools for Agent"""
        self.print_section("TEST 8: Agent Tools Definitions")
        
        try:
            response = requests.get(f"{self.base_url}/api/authority/tools")
            result = response.json()
            
            print(f"\n🤖 Available Tools: {len(result['tools'])}")
            
            for tool in result['tools']:
                print(f"\n   📌 {tool['name']}")
                print(f"      {tool['description']}")
                print(f"      Required: {tool['parameters'].get('required', [])}")
            
            self.results.append(("Tools Definitions", True))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Tools Definitions", False))
    
    def test_complete_workflow(self):
        """Test 9: Complete Agent 4 Workflow"""
        self.print_section("TEST 9: Complete Agent 4 Workflow")
        
        print("\n🤖 Simulating Agent 4 Workflow:")
        print("   OCR Text → Keywords → Authorities → MARC21")
        
        # Step 1: Agent extracts keywords (simulated)
        print("\n   Step 1: Extract Keywords from OCR")
        extracted_keywords = [
            "diabetes",
            "treatment",
            "clinical guidelines",
            "patient care"
        ]
        print(f"   ✅ Extracted: {extracted_keywords}")
        
        # Step 2: Standardize with Authority Control
        print("\n   Step 2: Standardize with Authority Control")
        try:
            response = requests.post(
                f"{self.base_url}/api/authority/map",
                json={
                    "keywords": extracted_keywords,
                    "subject_type": "medical"
                }
            )
            result = response.json()
            
            authority_terms = [
                item['term'] for item in result['mapping_results'] 
                if item['is_valid']
            ]
            print(f"   ✅ Authority Terms: {authority_terms}")
            
            # Step 3: Generate MARC21
            print("\n   Step 3: Generate MARC21 Output")
            marc_fields = result['marc21_fields']
            
            print(f"\n   📚 Final MARC21 Record:")
            for field in marc_fields:
                print(f"      {field}")
            
            print(f"\n   📊 Workflow Statistics:")
            print(f"      Original Keywords: {len(extracted_keywords)}")
            print(f"      Valid Authorities: {len(authority_terms)}")
            print(f"      MARC Fields: {len(marc_fields)}")
            print(f"      Cache Hit Rate: {result['statistics'].get('cache_hit_rate', 0):.1f}%")
            
            self.results.append(("Complete Workflow", True))
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("Complete Workflow", False))
    
    def print_summary(self):
        """Print test summary"""
        self.print_section("TEST SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for _, status in self.results if status)
        failed = total - passed
        
        print(f"\n📊 Results:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n⚠️ Failed Tests:")
            for name, status in self.results:
                if not status:
                    print(f"   - {name}")
        else:
            print(f"\n🎉 All tests passed!")
        
        print("\n" + "="*80 + "\n")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("  🧪 AUTHORITY CONTROL SERVICE - COMPLETE TEST SUITE")
        print("="*80)
        
        print("\n⏳ Starting tests...")
        
        # Run tests in sequence
        self.test_health_check()
        self.test_search_medical()
        self.test_map_medical_keywords()
        self.test_map_science_keywords()
        self.test_validate_terms()
        self.test_generate_marc()
        self.test_cache_statistics()
        self.test_tools_definitions()
        self.test_complete_workflow()
        
        # Print summary
        self.print_summary()


def main():
    """Main test runner"""
    print("\n🚀 Khởi động test suite...")
    print("   Đảm bảo Flask server đang chạy tại http://localhost:5000")
    print("   (python backend/app.py)")
    
    input("\n   Press Enter để bắt đầu tests...")
    
    tester = AuthorityServiceTester()
    tester.run_all_tests()
    
    print("\n💡 Tips:")
    print("   - Kiểm tra cache statistics để xem performance")
    print("   - Chạy lại để test cache hit rate")
    print("   - Xem backend/DEPLOYMENT_GUIDE.md để biết thêm examples")


if __name__ == "__main__":
    main()
