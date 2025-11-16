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
    """Xử lý ảnh đơn lẻ với PaddleOCR"""
    
    def process_image(self, file_path: str, image_id: Optional[str] = None) -> Dict:
        """
        Xử lý ảnh đơn lẻ với PaddleOCR
        
        Args:
            file_path: Đường dẫn đến file ảnh
            image_id: Mã định danh ảnh (tùy chọn)
            
        Returns:
            Dictionary chứa kết quả OCR
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
            
            # Run OCR prediction (PaddleOCR 3.x không dùng cls parameter)
            logger.info("Processing %s with PaddleOCR...", file_path)
            ocr_results = self._ocr_pipeline.ocr(file_path)  # Bỏ cls=True
            
            if not ocr_results or len(ocr_results) == 0 or not ocr_results[0]:
                result["error"] = "No content detected in file"
                result["status"] = "success"
                return result
            
            # Extract text from OCR results với validation đầy đủ
            extracted_text = ""
            confidence_scores = []
            
            # Kiểm tra kỹ structure của results trước khi truy cập
            if ocr_results and ocr_results[0]:
                for line in ocr_results[0]:
                    # Validate từng line trước khi extract
                    if line and isinstance(line, (list, tuple)) and len(line) >= 2:
                        # line format: [box_coordinates, (text, confidence)]
                        text_info = line[1]
                        if text_info and isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                            try:
                                text = str(text_info[0]) if text_info[0] else ""
                                conf = float(text_info[1]) if text_info[1] is not None else 0.0
                                if text:  # Chỉ thêm nếu có text
                                    extracted_text += text + "\n"
                                    confidence_scores.append(conf)
                            except (ValueError, TypeError, IndexError) as e:
                                logger.warning("Error parsing OCR line: %s", e)
                                continue
            
            # Calculate average confidence
            confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Validate extracted text
            if not extracted_text.strip():
                logger.warning("No text extracted from image %s", image_id)
                result["error"] = "No text content found in image"
                result["status"] = "success"
                return result
            
            # Save outputs (JSON only, no markdown for standard OCR)
            output_paths = {}
            if Config.ENABLE_JSON_OUTPUT:
                import json
                output_dir = Config.OUTPUT_FOLDER / image_id
                output_dir.mkdir(exist_ok=True, parents=True)
                json_path = output_dir / "result.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'text': extracted_text.strip(),
                        'confidence': confidence,
                        'lines': len(ocr_results[0])
                    }, f, ensure_ascii=False, indent=2)
                output_paths['json'] = str(json_path)
            
            # Update result
            result.update({
                "status": "success",
                "ocr_text": extracted_text.strip(),
                "markdown": "",  # Standard OCR không có markdown
                "confidence": round(confidence, 4),
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "output_files": output_paths,
                "layout_detected": False
            })
            
            # Update last used time
            self._update_last_used()
            
            logger.info(f"OCR completed for {image_id}: "
                       f"confidence={confidence:.2f}, time={result['processing_time_ms']}ms")
            
        except Exception as e:
            logger.error(f"OCR processing error for {image_id}: {e}")
            result["error"] = str(e)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        
        return result
