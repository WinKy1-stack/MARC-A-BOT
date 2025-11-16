"""
OCR Routes - Main Blueprint
Tổng hợp tất cả các routes OCR
"""
import logging
from flask import Blueprint

from .ocr_single import process_file
from .ocr_batch import process_batch_files
from .ocr_status import get_status, get_metrics
from .ocr_download import download_output

logger = logging.getLogger(__name__)

# Tạo blueprint chính
ocr_bp = Blueprint('ocr', __name__, url_prefix='/api/ocr')

# Register routes cho single file processing
ocr_bp.route('', methods=['POST'])(process_file)
ocr_bp.route('/', methods=['POST'])(process_file)
ocr_bp.route('/process', methods=['POST'])(process_file)

# Register route cho batch processing
ocr_bp.route('/batch', methods=['POST'])(process_batch_files)

# Register routes cho status và metrics
ocr_bp.route('/status', methods=['GET'])(lambda: get_status(None))
ocr_bp.route('/status/<request_id>', methods=['GET'])(get_status)
ocr_bp.route('/metrics', methods=['GET'])(get_metrics)

# Register route cho download
ocr_bp.route('/download/<file_id>/<file_type>', methods=['GET'])(download_output)