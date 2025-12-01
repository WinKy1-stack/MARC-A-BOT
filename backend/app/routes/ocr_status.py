"""
Route xử lý status và metrics
"""
import logging
from flask import Blueprint, request, jsonify

from app.config import Config
from app.ultis.request_queue import queue_manager
from .ocr_service_manager import get_ocr_service

logger = logging.getLogger(__name__)


def get_status(request_id=None):
    """
    Lấy trạng thái service OCR-VL hoặc trạng thái request cụ thể
    
    Args:
        request_id: ID của request (optional)
    """
    try:
        # Nếu có request_id, trả về trạng thái của request đó
        if request_id:
            request_status = queue_manager.get_request_status(request_id)
            
            if request_status is None:
                return jsonify({
                    "status": "error",
                    "message": "Request not found"
                }), 404
            
            return jsonify(request_status), 200
        
        # Nếu không có request_id, trả về trạng thái service
        from app.ultis.gpu_utils import get_gpu_info
        
        # Kiểm tra OCR service status
        try:
            service = get_ocr_service()
            model_status = service.get_model_status()
            ocr_available = True
            ocr_error = None
        except RuntimeError as e:
            model_status = {
                "initialized": False,
                "error": str(e)
            }
            ocr_available = False
            ocr_error = str(e)
        
        gpu_info = get_gpu_info()
        queue_stats = queue_manager.get_queue_stats()
        
        return jsonify({
            "status": "ok" if ocr_available else "degraded",
            "ocr_available": ocr_available,
            "ocr_error": ocr_error,
            "pipeline": model_status,
            "gpu": gpu_info,
            "queue": queue_stats,
            "config": {
                "use_gpu": Config.USE_GPU,
                "max_batch_size": Config.MAX_BATCH_SIZE,
                "max_file_size_mb": Config.MAX_FILE_SIZE / (1024*1024),
                "supported_formats": list(Config.ALLOWED_EXTENSIONS)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_status: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def get_metrics():
    """Lấy metrics và thống kê OCR"""
    try:
        from app.ultis.metrics_logger import metrics_logger
        from app.services.batch_processor import BatchProcessor
        
        # Lấy tham số hours từ query string (mặc định 24h)
        hours = request.args.get('hours', 24, type=int)
        
        # Lấy metrics summary
        metrics_summary = metrics_logger.get_metrics_summary(hours=hours)
        
        # Lấy batch stats nếu có
        batch_processor = BatchProcessor()
        batch_stats = batch_processor.get_batch_stats()
        
        return jsonify({
            "status": "success",
            "metrics": metrics_summary,
            "batch_stats": batch_stats,
            "timestamp": metrics_summary.get('timestamp')
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_metrics: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
