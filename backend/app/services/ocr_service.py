"""
OCR Service - Service chính tích hợp tất cả các processor OCR

Module này là điểm truy cập chính cho các thao tác OCR,
ủy quyền công việc cho các processor chuyên biệt:
- ImageProcessor: Xử lý ảnh đơn lẻ
- PDFProcessor: Xử lý tài liệu PDF
- BatchProcessor: Xử lý batch file
"""

from typing import Dict, List, Optional
from app.services.base_ocr_service import BaseOCRService
from app.services.image_processor import ImageProcessor
from app.services.pdf_processor import PDFProcessor
from app.services.batch_processor import BatchProcessor


class OCRService(BaseOCRService):
    """
    Service OCR chính - Facade pattern cho tất cả thao tác OCR
    
    Service này ủy quyền xử lý cho các processor chuyên biệt
    đồng thời duy trì khả năng tương thích ngược với code hiện tại.
    """
    
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.pdf_processor = PDFProcessor()
        self.batch_processor = BatchProcessor()
    
    def process_image(self, file_path: str, image_id: Optional[str] = None) -> Dict:
        """
        Xử lý ảnh đơn lẻ với OCR-VL
        
        Args:
            file_path: Đường dẫn đến file ảnh
            image_id: Mã định danh ảnh (tùy chọn)
            
        Returns:
            Dictionary chứa kết quả OCR bao gồm đường dẫn markdown và JSON
        """
        return self.image_processor.process_image(file_path, image_id)
    
    def process_pdf(self, pdf_path: str, image_id: Optional[str] = None) -> Dict:
        """
        Xử lý PDF nhiều trang với OCR-VL
        
        Args:
            pdf_path: Đường dẫn đến file PDF
            image_id: Mã định danh (tùy chọn)
            
        Returns:
            Dictionary chứa kết quả OCR tổng hợp cho tất cả các trang
        """
        return self.pdf_processor.process_pdf(pdf_path, image_id)
    
    def process_batch(self, file_paths: List[str], file_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Xử lý nhiều ảnh/PDF cùng lúc
        
        Args:
            file_paths: Danh sách đường dẫn file
            file_ids: Danh sách mã định danh (tùy chọn)
            
        Returns:
            Danh sách kết quả OCR
        """
        return self.batch_processor.process_batch(file_paths, file_ids)