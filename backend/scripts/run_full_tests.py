"""
Script chạy toàn bộ tests cho Authority Control Service
Bao gồm: Unit tests, Integration tests, Quick tests

Usage:
    python scripts/run_full_tests.py
"""

import subprocess
import sys
import os
from pathlib import Path

def print_section(title):
    """In section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def run_command(cmd, description):
    """Chạy command và trả về kết quả"""
    print(f"▶️  {description}")
    print(f"   Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - THÀNH CÔNG\n")
            return True
        else:
            print(f"❌ {description} - THẤT BẠI (exit code: {result.returncode})\n")
            return False
    except Exception as e:
        print(f"❌ Lỗi khi chạy: {e}\n")
        return False

def main():
    """Chạy toàn bộ test suite"""
    print_section("AUTHORITY CONTROL SERVICE - FULL TEST SUITE")
    
    # Kiểm tra backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    print(f"📁 Working directory: {backend_dir}\n")
    
    results = {}
    
    # Test 1: Quick functionality test
    print_section("1. QUICK FUNCTIONALITY TEST")
    results['quick_test'] = run_command(
        [sys.executable, "test_authority_quick.py"],
        "Quick Test - Core Functionality"
    )
    
    # Test 2: Unit tests cho authority mapper
    print_section("2. UNIT TESTS - Authority Mapper")
    results['mapper_tests'] = run_command(
        [sys.executable, "-m", "pytest", "tests/authority/test_authority_mapper.py", "-v", "--tb=short"],
        "Unit Tests - Authority Mapper"
    )
    
    # Test 3: Unit tests cho MARC generator
    print_section("3. UNIT TESTS - MARC Generator")
    results['marc_tests'] = run_command(
        [sys.executable, "-m", "pytest", "tests/authority/test_marc_generator.py", "-v", "--tb=short"],
        "Unit Tests - MARC Generator"
    )
    
    # Test 4: Integration tests
    print_section("4. INTEGRATION TESTS")
    results['integration_tests'] = run_command(
        [sys.executable, "-m", "pytest", "tests/authority/test_integration.py", "-v", "--tb=short"],
        "Integration Tests"
    )
    
    # Test 5: Coverage report (nếu muốn)
    print_section("5. TEST COVERAGE (Optional)")
    coverage_result = run_command(
        [sys.executable, "-m", "pytest", "tests/authority/", "--cov=services.authority", 
         "--cov-report=term-missing", "--tb=short"],
        "Full Test Suite with Coverage"
    )
    results['coverage'] = coverage_result
    
    # Tổng kết
    print_section("KẾT QUẢ TỔNG HỢP")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print("Chi tiết:")
    test_names = {
        'quick_test': 'Quick Functionality Test',
        'mapper_tests': 'Authority Mapper Tests',
        'marc_tests': 'MARC Generator Tests',
        'integration_tests': 'Integration Tests',
        'coverage': 'Coverage Report'
    }
    
    for key, value in results.items():
        status = "✅ PASS" if value else "❌ FAIL"
        print(f"  {status}  {test_names.get(key, key)}")
    
    print(f"\n{'='*70}")
    print(f"Tổng kết: {passed}/{total} test suites passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}\n")
    
    # Hướng dẫn tiếp theo
    if passed == total:
        print("🎉 TẤT CẢ TESTS ĐỀU PASS!")
        print("\n📌 Bước tiếp theo:")
        print("   1. Test API endpoints với: python scripts/test_endpoints.py")
        print("   2. (Cần mở Flask server trước: python app.py)")
    else:
        print("⚠️  Một số tests thất bại. Kiểm tra output ở trên để debug.")
    
    print()
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
