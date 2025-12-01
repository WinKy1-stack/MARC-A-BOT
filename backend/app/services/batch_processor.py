import time
import logging
import uuid
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.base_ocr_service import BaseOCRService
from app.services.image_processor import ImageProcessor
from app.services.pdf_processor import PDFProcessor
from app.config import Config

logger = logging.getLogger(__name__)


class BatchProcessor(BaseOCRService):
    """
    Xử lý nhiều file cùng lúc với theo dõi hiệu năng
    
    Tính năng:
    - Xử lý đồng thời với thread pool
    - Theo dõi metrics hiệu năng
    - Xử lý lỗi cho từng file
    - Ghi log tiến trình
    """
    
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.pdf_processor = PDFProcessor()
        self.stats = {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'avg_time_ms': 0,
            'total_time_ms': 0
        }
    
    def process_batch(
        self, 
        file_paths: List[str], 
        file_ids: Optional[List[str]] = None,
        max_workers: int = 2  # Giảm từ 3 xuống 2 để tránh PaddlePaddle tensor conflicts
    ) -> List[Dict]:
        """
        Xử lý nhiều ảnh/PDF cùng lúc với xử lý đồng thời
        
        Args:
            file_paths: Danh sách đường dẫn file
            file_ids: Danh sách mã định danh (tùy chọn)
            max_workers: Số lượng worker tối đa chạy đồng thời (mặc định: 3)
            
        Returns:
            Danh sách kết quả OCR kèm metrics hiệu năng
        """
        if file_ids is None:
            file_ids = [str(uuid.uuid4()) for _ in file_paths]
        
        if len(file_paths) != len(file_ids):
            logger.error("file_paths and file_ids length mismatch")
            raise ValueError("file_paths and file_ids must have the same length")
        
        results = []
        start_time = time.time()
        success_count = 0
        failed_count = 0
        
        logger.info(f"Starting batch OCR-VL for {len(file_paths)} files with {max_workers} workers")
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_single_file, file_path, file_id): (file_path, file_id, idx)
                for idx, (file_path, file_id) in enumerate(zip(file_paths, file_ids))
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_file):
                file_path, file_id, idx = future_to_file[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'success':
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    logger.info(
                        f"Progress: {completed}/{len(file_paths)} - "
                        f"File {idx + 1}: {file_id} - "
                        f"Status: {result['status']} - "
                        f"Time: {result.get('processing_time_ms', 0)}ms"
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_id}: {e}")
                    failed_count += 1
                    results.append({
                        'status': 'error',
                        'image_id': file_id,
                        'error': str(e),
                        'processing_time_ms': 0
                    })
        
        # Sort results by original order
        results_dict = {r.get('image_id') or r.get('pdf_id'): r for r in results}
        sorted_results = [results_dict[file_id] for file_id in file_ids if file_id in results_dict]
        
        # Calculate statistics
        total_time = int((time.time() - start_time) * 1000)
        avg_time = total_time // len(file_paths) if file_paths else 0
        
        # Update global stats
        self.stats['total_processed'] += len(file_paths)
        self.stats['total_success'] += success_count
        self.stats['total_failed'] += failed_count
        self.stats['total_time_ms'] += total_time
        self.stats['avg_time_ms'] = (
            self.stats['total_time_ms'] // self.stats['total_processed']
            if self.stats['total_processed'] > 0 else 0
        )
        
        logger.info(
            f"Batch OCR-VL completed: {len(sorted_results)} files in {total_time}ms "
            f"(avg: {avg_time}ms/file) - Success: {success_count}, Failed: {failed_count}"
        )
        
        return sorted_results
    
    def _process_single_file(self, file_path: str, file_id: str) -> Dict:
        """
        Xử lý một file đơn lẻ (phương thức nội bộ cho thread pool)
        
        Args:
            file_path: Đường dẫn đến file
            file_id: Mã định danh file
            
        Returns:
            Dictionary chứa kết quả OCR
        """
        try:
            # Check if PDF or image
            if file_path.lower().endswith('.pdf'):
                return self.pdf_processor.process_pdf(file_path, file_id)
            else:
                return self.image_processor.process_image(file_path, file_id)
                
        except Exception as e:
            logger.error(f"Error processing file {file_id}: {e}")
            return {
                'status': 'error',
                'image_id': file_id,
                'error': str(e),
                'processing_time_ms': 0
            }
    
    def get_batch_stats(self) -> Dict:
        """
        Lấy thống kê xử lý batch
        
        Returns:
            Dictionary chứa thống kê xử lý
        """
        return {
            'total_processed': self.stats['total_processed'],
            'total_success': self.stats['total_success'],
            'total_failed': self.stats['total_failed'],
            'success_rate': (
                round(self.stats['total_success'] / self.stats['total_processed'] * 100, 2)
                if self.stats['total_processed'] > 0 else 0
            ),
            'avg_time_ms': self.stats['avg_time_ms'],
            'total_time_ms': self.stats['total_time_ms']
        }
    
    def reset_stats(self):
        """Reset thống kê xử lý batch"""
        self.stats = {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'avg_time_ms': 0,
            'total_time_ms': 0
        }
        logger.info("Batch statistics reset")
