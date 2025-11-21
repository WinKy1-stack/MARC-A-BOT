"""
Route xử lý OCR cho file đơn lẻ
"""
import os
import uuid
import logging
from flask import Blueprint, request, jsonify

from app.config import Config
from app.ultis.validators import allowed_file, validate_file_size, sanitize_filename
from app.ultis.request_queue import queue_manager
from .ocr_service_manager import get_ocr_service

logger = logging.getLogger(__name__)


def process_file():
    """
    Xử lý ảnh hoặc PDF đơn lẻ để OCR
    
    Request: multipart/form-data với 'file' 
    Response: JSON chứa kết quả OCR bao gồm markdown
    """
    try:
        # Log request info for debugging
        logger.info(f"Received OCR request - Method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Files in request: {list(request.files.keys())}")
        logger.info(f"Form in request: {list(request.form.keys())}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Check if file is in request
        if 'file' not in request.files:
            logger.error(f"No 'file' field in request. Available fields: {list(request.files.keys())}")
            return jsonify({
                "status": "error",
                "error_code": "NO_FILE",
                "message": "No file provided. Expected 'file' field in multipart/form-data"
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
