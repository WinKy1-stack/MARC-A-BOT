import time
import logging
import uuid
from typing import Dict, Optional
from app.config import Config
from app.services.base_ocr_service import BaseOCRService
from app.services.ocr_utils import (
    extract_text_from_result,
    save_result_outputs,
    calculate_confidence
)

logger = logging.getLogger(__name__)


class ImageProcessor(BaseOCRService):
    """Xử lý ảnh đơn lẻ với OCR-VL"""
    
    def process_image(self, file_path: str, image_id: Optional[str] = None) -> Dict:
        """
        Xử lý ảnh/PDF đơn lẻ với OCR-VL
        
        Args:
            file_path: Đường dẫn đến file ảnh hoặc PDF
            image_id: Mã định danh ảnh (tùy chọn)
            
        Returns:
            Dictionary chứa kết quả OCR bao gồm đường dẫn markdown và JSON
        """
        start_time = time.time()
        
        if image_id is None:
            image_id = str(uuid.uuid4())
        
        result = {
            "status": "error",
            "image_id": image_id,
            "ocr_text": "",
            "markdown": "",
            "confidence": 0.0,
            "processing_time_ms": 0,
            "output_files": {},
            "layout_detected": False,
            "error": None
        }
        
        try:
            # Check if pipeline needs reinitialization
            self._ensure_pipeline_ready()
            
            # Run OCR-VL prediction
            logger.info(f"Processing {file_path} with OCR-VL...")
            ocr_results = self._ocr_pipeline.predict(input=file_path)
            
            if not ocr_results or len(ocr_results) == 0:
                result["error"] = "No content detected in file"
                result["status"] = "success"
                return result
            
            # Process first page/result (for single image)
            ocr_result = ocr_results[0]
            
            # Extract text
            extracted_text = extract_text_from_result(ocr_result)
            
            # Get markdown if available
            markdown_text = ""
            if hasattr(ocr_result, 'markdown'):
                markdown_text = ocr_result.markdown
            
            # Calculate confidence
            confidence = calculate_confidence(ocr_result)
            
            # Save outputs (JSON, Markdown)
            output_paths = save_result_outputs(ocr_result, image_id)
            
            # Update result
            result.update({
                "status": "success",
                "ocr_text": extracted_text,
                "markdown": markdown_text,
                "confidence": round(confidence, 4),
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "output_files": output_paths,
                "layout_detected": Config.USE_LAYOUT_DETECTION
            })
            
            # Update last used time
            self._update_last_used()
            
            logger.info(f"OCR-VL completed for {image_id}: "
                       f"confidence={confidence:.2f}, time={result['processing_time_ms']}ms")
            
        except Exception as e:
            logger.error(f"OCR-VL processing error for {image_id}: {e}")
            result["error"] = str(e)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        
        return result
