import logging
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.routes.ocr_routes import ocr_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize directories
Config.init_app()

# Register blueprints
app.register_blueprint(ocr_bp)

@app.route('/')
def home():
    """Endpoint gốc của API"""
    return jsonify({
        'message': 'Welcome to MARC-A-BOT Backend API',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'ocr_single': '/api/ocr/process',
            'ocr_batch': '/api/ocr/batch',
            'ocr_status': '/api/ocr/status',
            'ocr_download': '/api/ocr/download/<file_id>/<file_type>'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint kiểm tra sức khỏe hệ thống"""
    try:
        from app.ultis.gpu_utils import get_gpu_info, get_system_info
        
        return jsonify({
            'status': 'healthy',
            'service': 'MARC-A-BOT Backend',
            'gpu': get_gpu_info(),
            'system': get_system_info()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'degraded',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Xử lý lỗi 404"""
    return jsonify({
        'status': 'error',
        'error_code': 'NOT_FOUND',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Xử lý lỗi 500"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'status': 'error',
        'error_code': 'INTERNAL_ERROR',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting MARC-A-BOT Backend Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
