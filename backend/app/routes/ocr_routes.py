import os
import uuid
import logging
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from app.config import Config
from app.services.ocr_service import OCRService
from app.ultis.validators import allowed_file, validate_file_size, sanitize_filename
from app.ultis.request_queue import queue_manager

logger = logging.getLogger(__name__)
ocr_bp = Blueprint('ocr', __name__, url_prefix='/api/ocr')

# OCR service sẽ được khởi tạo lazy khi cần dùng
ocr_service = None
ocr_service_error = None

def get_ocr_service():
    """Lấy hoặc khởi tạo OCR service (lazy initialization)"""
    global ocr_service, ocr_service_error
    
    if ocr_service_error is not None:
        raise RuntimeError(f"OCR Service không khả dụng: {ocr_service_error}")
    
    if ocr_service is None:
        try:
            logger.info("Khởi tạo OCR service...")
            ocr_service = OCRService()
            logger.info("OCR service đã sẵn sàng")
        except Exception as e:
            error_msg = str(e)
            ocr_service_error = error_msg
            logger.error("Không thể khởi tạo OCR service: %s", error_msg)
            
            # Thông báo lỗi cụ thể về version conflict
            if "set_optimization_level" in error_msg:
                ocr_service_error = (
                    "Version conflict giữa PaddlePaddle và PaddleOCR-VL. "
                    "Vui lòng chạy: pip install paddlepaddle-gpu==2.5.2 hoặc "
                    "pip install paddlepaddle==2.5.2 (cho CPU)"
                )
            raise RuntimeError(f"OCR Service không khả dụng: {ocr_service_error}")
    
    return ocr_service

@ocr_bp.route('', methods=['POST'])
@ocr_bp.route('/', methods=['POST'])
@ocr_bp.route('/process', methods=['POST'])
def process_file():
    """
    Xử lý ảnh hoặc PDF đơn lẻ để OCR
    
    Request: multipart/form-data với 'file' 
    Response: JSON chứa kết quả OCR bao gồm markdown
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "error_code": "NO_FILE",
                "message": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "status": "error",
                "error_code": "EMPTY_FILENAME",
                "message": "Empty filename"
            }), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({
                "status": "error",
                "error_code": "INVALID_FORMAT",
                "message": f"File format not supported. Allowed: {Config.ALLOWED_EXTENSIONS}"
            }), 400
        
        if not validate_file_size(file):
            return jsonify({
                "status": "error",
                "error_code": "FILE_TOO_LARGE",
                "message": f"File size exceeds {Config.MAX_FILE_SIZE / (1024*1024)}MB limit"
            }), 400
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        filename = sanitize_filename(file.filename)
        file_path = Config.UPLOAD_FOLDER / f"{file_id}_{filename}"
        
        file.save(str(file_path))
        logger.info(f"File saved: {file_path}")
        
        # Check if PDF or image
        is_pdf = filename.lower().endswith('.pdf')
        
        # Process OCR with queue management
        def process_func():
            try:
                service = get_ocr_service()
                if is_pdf:
                    return service.process_pdf(str(file_path), file_id)
                else:
                    return service.process_image(str(file_path), file_id)
            except RuntimeError as e:
                return {
                    "status": "error",
                    "error_code": "OCR_SERVICE_ERROR",
                    "message": str(e)
                }
        
        queue_result = queue_manager.submit_request(
            request_id=file_id,
            func=process_func
        )
        
        # Cleanup temp file if not queued
        if not queue_result.get('queued', False):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {file_path}: {e}")
        
        # Return result based on queue status
        if queue_result['status'] == 'queued':
            return jsonify({
                "status": "queued",
                "request_id": file_id,
                "queue_position": queue_result['queue_position'],
                "estimated_wait_time": queue_result['estimated_wait_time'],
                "message": "Request queued. Check status with /api/ocr/status/<request_id>"
            }), 202
        
        elif queue_result['status'] == 'rejected':
            return jsonify({
                "status": "error",
                "error_code": "QUEUE_FULL",
                "message": queue_result['error'],
                "queue_size": queue_result['queue_size']
            }), 503
        
        elif queue_result['status'] == 'completed':
            result = queue_result['result']
            status_code = 200 if result["status"] == "success" else 500
            return jsonify(result), status_code
        
        else:  # failed
            return jsonify({
                "status": "error",
                "error_code": "PROCESSING_ERROR",
                "message": queue_result.get('error', 'Unknown error')
            }), 500
        
    except Exception as e:
        logger.error(f"Error in process_file: {e}")
        return jsonify({
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        }), 500

@ocr_bp.route('/batch', methods=['POST'])
def process_batch_files():
    """
    Xử lý nhiều file cùng lúc
    
    Request: multipart/form-data với nhiều 'files'
    Response: JSON chứa danh sách kết quả OCR
    """
    try:
        if 'files' not in request.files:
            return jsonify({
                "status": "error",
                "error_code": "NO_FILES",
                "message": "No files provided"
            }), 400
        
        files = request.files.getlist('files')
        
        if len(files) == 0:
            return jsonify({
                "status": "error",
                "error_code": "EMPTY_FILES",
                "message": "No files selected"
            }), 400
        
        if len(files) > Config.MAX_BATCH_SIZE:
            return jsonify({
                "status": "error",
                "error_code": "BATCH_TOO_LARGE",
                "message": f"Maximum {Config.MAX_BATCH_SIZE} files allowed per batch"
            }), 400
        
        # Validate and save files
        saved_files = []
        file_ids = []
        
        for file in files:
            if file.filename == '':
                continue
            
            if not allowed_file(file.filename):
                logger.warning(f"Skipping invalid file: {file.filename}")
                continue
            
            if not validate_file_size(file):
                logger.warning(f"Skipping large file: {file.filename}")
                continue
            
            # Save file
            file_id = str(uuid.uuid4())
            filename = sanitize_filename(file.filename)
            file_path = Config.UPLOAD_FOLDER / f"{file_id}_{filename}"
            
            file.save(str(file_path))
            saved_files.append(str(file_path))
            file_ids.append(file_id)
            logger.info(f"Batch file saved: {file_path}")
        
        if not saved_files:
            return jsonify({
                "status": "error",
                "error_code": "NO_VALID_FILES",
                "message": "No valid files to process"
            }), 400
        
        # Process batch OCR
        try:
            service = get_ocr_service()
            results = service.process_batch(saved_files, file_ids)
        except RuntimeError as e:
            # Cleanup temp files
            for file_path in saved_files:
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            
            return jsonify({
                "status": "error",
                "error_code": "OCR_SERVICE_ERROR",
                "message": str(e)
            }), 503
        
        # Cleanup temp files
        for file_path in saved_files:
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {file_path}: {e}")
        
        # Return results
        response = {
            "status": "success",
            "total_files": len(results),
            "results": results
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in process_batch_files: {e}")
        return jsonify({
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        }), 500

@ocr_bp.route('/download/<file_id>/<file_type>', methods=['GET'])
def download_output(file_id, file_type):
    """
    Tải file kết quả đã xử lý (JSON hoặc Markdown)
    
    Args:
        file_id: Mã định danh file
        file_type: 'json' hoặc 'markdown'
    """
    try:
        output_dir = Config.OUTPUT_FOLDER / file_id
        
        if file_type == 'json':
            file_path = output_dir / 'result.json'
        elif file_type == 'markdown':
            file_path = output_dir / 'result.md'
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid file type. Use 'json' or 'markdown'"
            }), 400
        
        if not file_path.exists():
            return jsonify({
                "status": "error",
                "message": "File not found"
            }), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ocr_bp.route('/status', methods=['GET'])
@ocr_bp.route('/status/<request_id>', methods=['GET'])
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

@ocr_bp.route('/metrics', methods=['GET'])
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