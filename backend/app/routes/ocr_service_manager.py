"""
Quản lý khởi tạo OCR Service (Singleton)
"""
import logging
from app.services.ocr_service import OCRService

logger = logging.getLogger(__name__)

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
