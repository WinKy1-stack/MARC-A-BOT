"""
MARC-A-BOT Backend - Điểm khởi chạy chính

Script để chạy Flask server với các tùy chọn cấu hình
"""

import sys
import logging
import argparse
from pathlib import Path

# Thêm thư mục backend vào Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.config import Config

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Phân tích các tham số dòng lệnh"""
    parser = argparse.ArgumentParser(
        description='MARC-A-BOT Backend OCR Service'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Địa chỉ host (mặc định: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Số port (mặc định: 5001)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Bật chế độ debug'
    )
    
    parser.add_argument(
        '--no-gpu',
        action='store_true',
        help='Tắt GPU (chỉ dùng CPU)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Số worker processes (cho production)'
    )
    
    parser.add_argument(
        '--production',
        action='store_true',
        help='Chạy ở chế độ production với Gunicorn'
    )
    
    return parser.parse_args()


def check_system_requirements():
    """Kiểm tra yêu cầu hệ thống"""
    logger.info("Đang kiểm tra yêu cầu hệ thống...")
    
    # Kiểm tra phiên bản Python
    if sys.version_info < (3, 11):
        logger.warning(
            "Phát hiện Python %d.%d. Khuyến nghị Python 3.11+",
            sys.version_info.major, sys.version_info.minor
        )
    
    # Kiểm tra GPU
    if Config.USE_GPU:
        try:
            import paddle
            gpu_count = paddle.device.cuda.device_count()
            if gpu_count > 0:
                logger.info("✓ Phát hiện GPU: %d thiết bị", gpu_count)
            else:
                logger.warning("⚠ Không tìm thấy GPU. Chạy ở chế độ CPU.")
                Config.USE_GPU = False
        except ImportError as e:
            logger.warning("⚠ Kiểm tra GPU thất bại: %s. Chạy ở chế độ CPU.", str(e))
            Config.USE_GPU = False
    else:
        logger.info("Chạy ở chế độ CPU (GPU đã tắt)")
    
    # Kiểm tra các thư mục cần thiết
    for directory in [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER, Config.LOG_DIR]:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info("✓ Đã tạo thư mục: %s", directory)
        else:
            logger.info("✓ Thư mục đã tồn tại: %s", directory)
    
    logger.info("Kiểm tra hệ thống hoàn tất!")


def run_development_server(host, port, debug):
    """Chạy development server với Flask"""
    logger.info("=" * 60)
    logger.info("MARC-A-BOT Backend - Development Server")
    logger.info("=" * 60)
    logger.info("Host: %s", host)
    logger.info("Port: %d", port)
    logger.info("Debug: %s", debug)
    logger.info("GPU: %s", 'Bật' if Config.USE_GPU else 'Tắt')
    logger.info("Kích thước Batch tối đa: %d", Config.MAX_BATCH_SIZE)
    logger.info("Request đồng thời tối đa: %d", Config.MAX_CONCURRENT_REQUESTS)
    logger.info("Queue: %s", 'Bật' if Config.ENABLE_REQUEST_QUEUE else 'Tắt')
    logger.info("=" * 60)
    logger.info("\n🚀 Server đang khởi động tại http://%s:%d\n", host, port)
    
    flask_app = create_app()
    flask_app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        threaded=True
    )


def run_production_server(host, port, workers):
    """Chạy production server với Gunicorn"""
    try:
        import gunicorn.app.base
    except ImportError:
        logger.error("Gunicorn chưa được cài đặt. Cài đặt với: pip install gunicorn")
        logger.info("Sử dụng development server thay thế...")
        run_development_server(host, port, False)
        return
    
    logger.info("=" * 60)
    logger.info("MARC-A-BOT Backend - Production Server (Gunicorn)")
    logger.info("=" * 60)
    logger.info("Host: %s", host)
    logger.info("Port: %d", port)
    logger.info("Workers: %d", workers)
    logger.info("GPU: %s", 'Bật' if Config.USE_GPU else 'Tắt')
    logger.info("=" * 60)
    
    # Cấu hình Gunicorn
    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, flask_app, options=None):
            self.options = options or {}
            self.application = flask_app
            super().__init__()
        
        def init(self, parser, opts, args):
            """Khởi tạo gunicorn application"""
            pass

        def load_config(self):
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '%s:%d' % (host, port),
        'workers': workers,
        'worker_class': 'sync',
        'timeout': 120,
        'keepalive': 5,
        'max_requests': 1000,
        'max_requests_jitter': 50,
        'loglevel': 'info',
        'accesslog': '-',
        'errorlog': '-',
    }
    
    flask_app = create_app()
    StandaloneApplication(flask_app, options).run()


def main():
    """Điểm khởi chạy chính"""
    args = parse_arguments()
    
    # Ghi đè cấu hình GPU nếu có flag --no-gpu
    if args.no_gpu:
        Config.USE_GPU = False
        logger.info("GPU đã bị tắt qua tham số dòng lệnh")
    
    # Kiểm tra yêu cầu hệ thống
    try:
        check_system_requirements()
    except (ImportError, OSError, RuntimeError) as e:
        logger.error("Kiểm tra hệ thống thất bại: %s", e)
        sys.exit(1)
    
    # Chạy server
    try:
        if args.production:
            run_production_server(args.host, args.port, args.workers)
        else:
            run_development_server(args.host, args.port, args.debug)
    except KeyboardInterrupt:
        logger.info("\n\n👋 Server đã dừng bởi người dùng")
    except (ImportError, OSError, RuntimeError) as e:
        logger.error("Lỗi server: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
