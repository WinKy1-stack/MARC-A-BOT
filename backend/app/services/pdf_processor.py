import time
import logging
import uuid
import json
from typing import Dict, Optional
from pathlib import Path
from app.config import Config
from app.services.base_ocr_service import BaseOCRService
from app.services.ocr_utils import (
    extract_text_from_result,
    calculate_confidence
)
from app.ultis.request_queue import queue_manager

logger = logging.getLogger(__name__)


class PDFProcessor(BaseOCRService):
    """Xử lý file PDF với PaddleOCR"""
    
    def process_pdf(self, pdf_path: str, image_id: Optional[str] = None) -> Dict:
        """
        Xử lý file PDF nhiều trang với PaddleOCR
        
        Args:
            pdf_path: Đường dẫn đến file PDF
            image_id: Mã định danh (tùy chọn)
            
        Returns:
            Dictionary chứa kết quả OCR tổng hợp cho tất cả các trang
        """
        start_time = time.time()
        
        if image_id is None:
            image_id = str(uuid.uuid4())
        
        result = {
            "status": "error",
            "pdf_id": image_id,
            "total_pages": 0,
            "combined_text": "",
            "combined_markdown": "",
            "pages": [],
            "processing_time_ms": 0,
            "output_files": {},
            "error": None
        }
        
        try:
            # Report progress: Bắt đầu xử lý PDF
            queue_manager.update_request_progress(image_id, {
                "step": "starting",
                "message": "Bắt đầu xử lý PDF...",
                "progress": 5
            })

            # Check if pipeline needs reinitialization
            queue_manager.update_request_progress(image_id, {
                "step": "loading_model",
                "message": "Đang tải mô hình OCR...",
                "progress": 10
            })
            self._ensure_pipeline_ready()

            logger.info("Processing PDF %s with PaddleOCR...", pdf_path)

            # Convert PDF to images first (PaddleOCR doesn't directly support PDF)
            from pdf2image import convert_from_path
            import tempfile
            import os
            import shutil

            temp_dir = tempfile.mkdtemp()
            text_list = []
            pages_data = []

            try:
                # Convert PDF to images
                queue_manager.update_request_progress(image_id, {
                    "step": "converting_pdf",
                    "message": "Đang chuyển đổi PDF sang hình ảnh...",
                    "progress": 15
                })
                logger.info("Converting PDF to images...")
                images = convert_from_path(pdf_path, dpi=200)
                logger.info("Converted %d pages", len(images))

                queue_manager.update_request_progress(image_id, {
                    "step": "converted",
                    "message": f"Đã chuyển đổi {len(images)} trang",
                    "progress": 20,
                    "total_pages": len(images)
                })
                
                # Process each page
                for idx, image in enumerate(images):
                    try:
                        # Report progress for each page
                        # Progress từ 20% -> 80% cho việc xử lý các trang
                        page_progress = 20 + int((idx / len(images)) * 60)
                        queue_manager.update_request_progress(image_id, {
                            "step": "processing_page",
                            "message": f"Đang xử lý trang {idx+1}/{len(images)}...",
                            "progress": page_progress,
                            "current_page": idx + 1,
                            "total_pages": len(images)
                        })

                        # Save temp image
                        temp_image_path = os.path.join(temp_dir, f"page_{idx+1}.jpg")
                        image.save(temp_image_path, 'JPEG', quality=95)

                        logger.info("Processing page %d/%d", idx+1, len(images))
                        
                        # OCR với thread-safe inference
                        page_results = self.ocr_inference(temp_image_path)  # Dùng method từ BaseOCRService
                        
                        page_text = ""
                        confidence_scores = []
                        
                        # Validate OCR results structure trước khi parse
                        if page_results and page_results[0]:
                            for line in page_results[0]:
                                # Kiểm tra kỹ structure của line
                                if line and isinstance(line, (list, tuple)) and len(line) >= 2:
                                    # line format: [box_coordinates, (text, confidence)]
                                    text_info = line[1]
                                    if text_info and isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                        try:
                                            text = str(text_info[0]) if text_info[0] else ""
                                            conf = float(text_info[1]) if text_info[1] is not None else 0.0
                                            if text:  # Chỉ thêm nếu có text
                                                page_text += text + "\n"
                                                confidence_scores.append(conf)
                                        except (ValueError, TypeError, IndexError) as parse_error:
                                            logger.warning("Error parsing OCR line on page %d: %s", idx+1, parse_error)
                                            continue
                        
                        page_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
                        
                        text_list.append(page_text)
                        pages_data.append({
                            "page_number": idx + 1,
                            "text": page_text.strip(),
                            "confidence": round(page_confidence, 4),
                            "lines_detected": len(confidence_scores)
                        })
                        
                        logger.info("Page %d completed: %d lines, confidence=%.2f", 
                                   idx+1, len(confidence_scores), page_confidence)
                        
                    except Exception as page_error:
                        logger.error("Error processing page %d: %s", idx+1, page_error)
                        text_list.append("")
                        pages_data.append({
                            "page_number": idx + 1,
                            "text": "",
                            "confidence": 0.0,
                            "lines_detected": 0,
                            "error": str(page_error)
                        })
            
            finally:
                # Cleanup temp files
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temporary files")
                except Exception as cleanup_error:
                    logger.warning("Failed to cleanup temp dir: %s", cleanup_error)
            
            combined_text = "\n\n".join(text_list)

            # Save combined result
            queue_manager.update_request_progress(image_id, {
                "step": "saving_results",
                "message": "Đang lưu kết quả...",
                "progress": 85
            })

            output_dir = Config.OUTPUT_FOLDER / image_id
            output_dir.mkdir(exist_ok=True, parents=True)
            
            json_path = output_dir / f"{Path(pdf_path).stem}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(pages_data, f, ensure_ascii=False, indent=2)
            
            # Calculate overall stats
            total_lines = sum(page.get('lines_detected', 0) for page in pages_data)
            avg_confidence = sum(page.get('confidence', 0) for page in pages_data) / len(pages_data) if pages_data else 0.0
            
            # Update result
            result.update({
                "status": "success",
                "total_pages": len(pages_data),
                "combined_text": combined_text.strip(),
                "pages": pages_data,
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "output_files": {
                    "json": str(json_path)
                },
                "stats": {
                    "total_lines": total_lines,
                    "avg_confidence": round(avg_confidence, 4)
                }
            })
            
            self._update_last_used()

            queue_manager.update_request_progress(image_id, {
                "step": "completed",
                "message": f"Hoàn thành! Đã xử lý {len(pages_data)} trang",
                "progress": 100
            })

            logger.info("OCR PDF completed for %s: %d pages, %d lines, avg_conf=%.2f, time=%dms",
                       image_id, len(pages_data), total_lines, avg_confidence, result['processing_time_ms'])
            
        except Exception as e:
            logger.error("OCR PDF processing error for %s: %s", image_id, e, exc_info=True)
            result["error"] = str(e)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        
        return result
