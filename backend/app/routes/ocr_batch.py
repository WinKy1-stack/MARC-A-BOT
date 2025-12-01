"""
Route xử lý OCR cho batch files
"""
import os
import uuid
import logging
from flask import Blueprint, request, jsonify

from app.config import Config
from app.ultis.validators import allowed_file, validate_file_size, sanitize_filename
from .ocr_service_manager import get_ocr_service

logger = logging.getLogger(__name__)


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
