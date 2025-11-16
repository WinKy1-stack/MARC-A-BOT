"""
Quick Start Script - Authority Control Service
Khởi động và test hệ thống nhanh chóng
"""
import subprocess
import time
import requests
import sys
from pathlib import Path


class QuickStarter:
    """Quick start helper for Authority Control Service"""
    
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.base_url = "http://localhost:5000"
        self.flask_process = None
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")
    
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        self.print_header("Step 1: Checking Dependencies")
        
        required = ["Flask", "requests", "rapidfuzz", "pymarc"]
        missing = []
        
        for package in required:
            try:
                __import__(package.lower())
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package} - NOT INSTALLED")
                missing.append(package)
        
        if missing:
            print(f"\n⚠️  Missing packages: {', '.join(missing)}")
            print("   Run: pip install -r requirements.txt")
            return False
        
        print("\n✅ All dependencies installed!")
        return True
    
    def check_service_structure(self):
        """Check if authority service files exist"""
        self.print_header("Step 2: Checking Service Files")
        
        required_files = [
            "services/authority/config.py",
            "services/authority/authority_service.py",
            "services/authority/tools.py",
            "services/authority/marc_generator.py",
            "services/authority/cache/cache_manager.py",
            "services/authority/clients/mesh_client.py",
            "services/authority/clients/loc_client.py",
            "api/authority_routes.py"
        ]
        
        missing = []
        for file_path in required_files:
            full_path = self.backend_path / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - MISSING")
                missing.append(file_path)
        
        if missing:
            print(f"\n⚠️  Missing files. Authority service may not be complete.")
            return False
        
        print("\n✅ All service files found!")
        return True
    
    def wait_for_service(self, max_wait=30):
        """Wait for Flask service to be ready"""
        print("   Waiting for service to start", end="")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/api/authority/health", timeout=2)
                if response.status_code == 200:
                    print(" ✅")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(".", end="", flush=True)
            time.sleep(1)
        
        print(" ❌")
        return False
    
    def quick_test(self):
        """Run quick functionality test"""
        self.print_header("Step 4: Quick Functionality Test")
        
        tests = [
            ("Health Check", "GET", "/api/authority/health", None),
            ("Search MESH", "POST", "/api/authority/search", 
             {"keyword": "diabetes", "source": "MESH"}),
            ("Map Keywords", "POST", "/api/authority/map",
             {"keywords": ["diabetes", "insulin"], "subject_type": "medical"})
        ]
        
        passed = 0
        for name, method, endpoint, data in tests:
            try:
                url = f"{self.base_url}{endpoint}"
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)
                
                if response.status_code == 200:
                    print(f"   ✅ {name}")
                    passed += 1
                else:
                    print(f"   ❌ {name} (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ {name} (Error: {e})")
        
        print(f"\n   Results: {passed}/{len(tests)} tests passed")
        return passed == len(tests)
    
    def show_quick_examples(self):
        """Show quick usage examples"""
        self.print_header("Quick Usage Examples")
        
        print("🔍 1. Search Authority Terms:")
        print("   curl -X POST http://localhost:5000/api/authority/search \\")
        print("     -H 'Content-Type: application/json' \\")
        print('     -d \'{"keyword": "machine learning", "source": "ALL"}\'')
        
        print("\n📝 2. Map Keywords:")
        print("   curl -X POST http://localhost:5000/api/authority/map \\")
        print("     -H 'Content-Type: application/json' \\")
        print('     -d \'{"keywords": ["diabetes", "insulin"], "subject_type": "medical"}\'')
        
        print("\n📚 3. Generate MARC21:")
        print("   curl -X POST http://localhost:5000/api/authority/generate-marc \\")
        print("     -H 'Content-Type: application/json' \\")
        print('     -d \'{"keywords": ["artificial intelligence"]}\'')
        
        print("\n🤖 4. Get Agent Tools:")
        print("   curl http://localhost:5000/api/authority/tools")
        
        print("\n📊 5. Cache Statistics:")
        print("   curl http://localhost:5000/api/authority/cache/stats")
    
    def show_next_steps(self):
        """Show next steps"""
        self.print_header("Next Steps")
        
        print("📖 Documentation:")
        print("   - DEPLOYMENT_GUIDE.md - Complete deployment guide")
        print("   - backend/docs/API_REFERENCE.md - API documentation")
        print("   - backend/docs/QUICKSTART.md - Quick start guide")
        
        print("\n🧪 Testing:")
        print("   - python backend/test_complete_workflow.py - Full test suite")
        print("   - python backend/examples/agent_4_integration.py - Agent examples")
        print("   - pytest backend/tests/authority/ -v - Run all tests")
        
        print("\n🔧 Configuration:")
        print("   - Edit backend/services/authority/config.py")
        print("   - Adjust API timeouts, cache settings")
        print("   - Enable/disable Z39.50 (NLM)")
        
        print("\n📈 Monitoring:")
        print("   - Check cache hit rate: /api/authority/cache/stats")
        print("   - View logs in console")
        print("   - Monitor response times")
    
    def run(self):
        """Main quick start workflow"""
        print("\n" + "="*80)
        print("  🚀 AUTHORITY CONTROL SERVICE - QUICK START")
        print("="*80)
        
        # Step 1: Check dependencies
        if not self.check_dependencies():
            print("\n⚠️  Please install dependencies first:")
            print("   pip install -r requirements.txt")
            return False
        
        # Step 2: Check service files
        if not self.check_service_structure():
            print("\n⚠️  Service files are incomplete.")
            return False
        
        # Step 3: Check if service is already running
        self.print_header("Step 3: Checking Service Status")
        try:
            response = requests.get(f"{self.base_url}/api/authority/health", timeout=2)
            if response.status_code == 200:
                print("   ✅ Service is already running!")
                service_running = True
            else:
                service_running = False
        except requests.exceptions.RequestException:
            print("   ℹ️  Service is not running")
            service_running = False
        
        if not service_running:
            print("\n   To start the service manually:")
            print("   cd backend")
            print("   python app.py")
            print("\n   Or run this script with --start flag")
            return False
        
        # Step 4: Quick test
        if not self.quick_test():
            print("\n⚠️  Some tests failed. Check service logs.")
            return False
        
        # Success!
        self.print_header("✅ Quick Start Complete!")
        print("   Authority Control Service is ready to use!")
        print("   Base URL: http://localhost:5000")
        print("   API Docs: http://localhost:5000/api/authority/health")
        
        # Show examples
        self.show_quick_examples()
        
        # Show next steps
        self.show_next_steps()
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick Start - Authority Control Service")
    parser.add_argument("--start", action="store_true", help="Start Flask service")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    args = parser.parse_args()
    
    starter = QuickStarter()
    
    if args.start:
        print("Starting Flask service...")
        print("Run: python backend/app.py")
        print("\nOr in another terminal:")
        print("  cd backend")
        print("  python app.py")
        return
    
    if args.test:
        print("Running complete test suite...")
        subprocess.run([sys.executable, "backend/test_complete_workflow.py"])
        return
    
    # Default: Run quick start
    success = starter.run()
    
    if success:
        print("\n🎉 Ready to go!")
    else:
        print("\n⚠️  Quick start incomplete. Check messages above.")


if __name__ == "__main__":
    main()
