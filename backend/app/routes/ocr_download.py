"""
Route xử lý download file kết quả
"""
import logging
from flask import Blueprint, request, jsonify, send_file

from app.config import Config

logger = logging.getLogger(__name__)


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
