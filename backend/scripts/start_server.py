"""
Script khởi động Flask server với các tùy chọn
Usage:
    python scripts/start_server.py [--port PORT] [--debug]
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    """Khởi động Flask server"""
    parser = argparse.ArgumentParser(description='Khởi động Authority Control Service API')
    parser.add_argument('--port', type=int, default=5000, help='Port để chạy server (mặc định: 5000)')
    parser.add_argument('--debug', action='store_true', help='Bật debug mode')
    parser.add_argument('--host', default='0.0.0.0', help='Host address (mặc định: 0.0.0.0)')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'app.py'
    if args.debug:
        os.environ['FLASK_DEBUG'] = '1'
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print("\n" + "="*70)
    print("  AUTHORITY CONTROL SERVICE - FLASK API SERVER")
    print("="*70)
    print(f"\n📁 Working directory: {backend_dir}")
    print(f"🌐 Server URL: http://{args.host}:{args.port}")
    print(f"🔧 Debug mode: {'ON' if args.debug else 'OFF'}")
    print(f"\n📚 API Endpoints:")
    print(f"   - Health Check:    http://localhost:{args.port}/api/authority/health")
    print(f"   - Tools:           http://localhost:{args.port}/api/authority/tools")
    print(f"   - Search:          http://localhost:{args.port}/api/authority/search")
    print(f"   - Map Keywords:    http://localhost:{args.port}/api/authority/map")
    print(f"   - Generate MARC:   http://localhost:{args.port}/api/authority/generate-marc")
    print(f"   - Validate:        http://localhost:{args.port}/api/authority/validate")
    print(f"   - Cache Stats:     http://localhost:{args.port}/api/authority/cache/stats")
    print(f"\n⚠️  Press CTRL+C to stop the server")
    print("="*70 + "\n")
    
    # Import and run Flask app
    try:
        from app import app
        app.run(host=args.host, port=args.port, debug=args.debug)
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        print("\n📌 Đảm bảo bạn đã cài đặt dependencies:")
        print("   pip install -r requirements.txt\n")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi khởi động server: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
