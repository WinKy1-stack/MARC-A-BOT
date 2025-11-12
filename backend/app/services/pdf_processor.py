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

logger = logging.getLogger(__name__)


class PDFProcessor(BaseOCRService):
    """Xử lý file PDF với OCR-VL"""
    
    def process_pdf(self, pdf_path: str, image_id: Optional[str] = None) -> Dict:
        """
        Xử lý file PDF nhiều trang với OCR-VL
        
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
            # Check if pipeline needs reinitialization
            self._ensure_pipeline_ready()
            
            logger.info(f"Processing PDF {pdf_path} with OCR-VL...")
            ocr_results = self._ocr_pipeline.predict(input=pdf_path)
            
            if not ocr_results or len(ocr_results) == 0:
                result["error"] = "No content detected in PDF"
                result["status"] = "success"
                return result
            
            # Process each page
            markdown_list = []
            text_list = []
            pages_data = []
            
            for idx, page_result in enumerate(ocr_results):
                page_text = extract_text_from_result(page_result)
                page_markdown = page_result.markdown if hasattr(page_result, 'markdown') else ""
                page_confidence = calculate_confidence(page_result)
                
                markdown_list.append(page_markdown)
                text_list.append(page_text)
                
                pages_data.append({
                    "page_number": idx + 1,
                    "text": page_text,
                    "markdown": page_markdown,
                    "confidence": round(page_confidence, 4)
                })
            
            # Concatenate all pages markdown
            combined_markdown = self._ocr_pipeline.concatenate_markdown_pages(markdown_list)
            combined_text = "\n\n".join(text_list)
            
            # Save combined markdown
            output_dir = Config.OUTPUT_FOLDER / image_id
            output_dir.mkdir(exist_ok=True, parents=True)
            
            md_path = output_dir / f"{Path(pdf_path).stem}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(combined_markdown)
            
            json_path = output_dir / f"{Path(pdf_path).stem}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(pages_data, f, ensure_ascii=False, indent=2)
            
            # Update result
            result.update({
                "status": "success",
                "total_pages": len(ocr_results),
                "combined_text": combined_text,
                "combined_markdown": combined_markdown,
                "pages": pages_data,
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "output_files": {
                    "markdown": str(md_path),
                    "json": str(json_path)
                }
            })
            
            self._update_last_used()
            
            logger.info(f"OCR-VL PDF completed for {image_id}: "
                       f"{len(ocr_results)} pages, time={result['processing_time_ms']}ms")
            
        except Exception as e:
            logger.error(f"OCR-VL PDF processing error for {image_id}: {e}")
            result["error"] = str(e)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        
        return result
