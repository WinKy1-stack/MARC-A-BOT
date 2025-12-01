"""
Routes package
"""

from flask import Blueprint, jsonify
import logging

from .ocr_routes import ocr_bp
from .sse_routes import sse_bp

logger = logging.getLogger(__name__)

# Health check blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
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
    except (ImportError, AttributeError, RuntimeError) as e:
        logger.error("Health check error: %s", e)
        return jsonify({
            'status': 'degraded',
            'error': str(e)
        }), 500

@health_bp.route('/', methods=['GET'])
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
            'ocr_metrics': '/api/ocr/metrics'
        }
    })

__all__ = ['health_bp', 'ocr_bp']
__all__.append('sse_bp')
