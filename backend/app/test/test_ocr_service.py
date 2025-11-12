"""
Test suite cho OCR Service

Module này chứa các unit test và integration test cho OCR service,
bao gồm xử lý ảnh đơn, PDF, và batch processing.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.ocr_service import OCRService
from app.services.image_processor import ImageProcessor
from app.services.pdf_processor import PDFProcessor
from app.services.batch_processor import BatchProcessor
from app.config import Config


class TestOCRService(unittest.TestCase):
    """Test case cho OCRService chính"""
    
    @classmethod
    def setUpClass(cls):
        """Thiết lập một lần cho tất cả test"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.sample_image_path = cls.test_dir / "sample.jpg"
        cls.sample_pdf_path = cls.test_dir / "sample.pdf"
        
        # Tạo file ảnh giả
        cls._create_sample_image(cls.sample_image_path)
        cls._create_sample_pdf(cls.sample_pdf_path)
    
    @staticmethod
    def _create_sample_image(path):
        """Tạo file ảnh mẫu cho testing"""
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='white')
            img.save(path)
        except ImportError:
            # Fallback: tạo file giả nếu không có PIL
            with open(path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')
    
    @staticmethod
    def _create_sample_pdf(path):
        """Tạo file PDF mẫu cho testing"""
        # Tạo file PDF đơn giản
        with open(path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        self.ocr_service = OCRService()
    
    def tearDown(self):
        """Dọn dẹp sau mỗi test"""
        # Cleanup được thực hiện trong tearDownClass
    
    @classmethod
    def tearDownClass(cls):
        """Dọn dẹp sau tất cả test"""
        import shutil
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_service_initialization(self, _mock_paddle):
        """Test khởi tạo OCR service"""
        service = OCRService()
        self.assertIsNotNone(service)
        self.assertIsInstance(service.image_processor, ImageProcessor)
        self.assertIsInstance(service.pdf_processor, PDFProcessor)
        self.assertIsInstance(service.batch_processor, BatchProcessor)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_process_image_success(self, mock_paddle):
        """Test xử lý ảnh thành công"""
        # Mock OCR result
        mock_result = MagicMock()
        mock_result.text = "Sample OCR text"
        mock_result.markdown = "# Sample OCR text"
        mock_result.confidence = 0.95
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        # Reinitialize service với mock
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        result = service.process_image(str(self.sample_image_path), "test-id-1")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['image_id'], 'test-id-1')
        self.assertIn('ocr_text', result)
        self.assertIn('confidence', result)
        self.assertGreater(result['confidence'], 0)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_process_image_no_content(self, mock_paddle):
        """Test xử lý ảnh không có nội dung"""
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = []
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        result = service.process_image(str(self.sample_image_path))
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['ocr_text'], '')
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_process_image_error(self, mock_paddle):
        """Test xử lý ảnh bị lỗi"""
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.side_effect = Exception("OCR processing failed")
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        result = service.process_image(str(self.sample_image_path))
        
        self.assertEqual(result['status'], 'error')
        self.assertIsNotNone(result['error'])
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_process_pdf_success(self, mock_paddle):
        """Test xử lý PDF thành công"""
        # Mock OCR results cho nhiều trang
        mock_page1 = MagicMock()
        mock_page1.text = "Page 1 text"
        mock_page1.markdown = "# Page 1"
        mock_page1.confidence = 0.90
        
        mock_page2 = MagicMock()
        mock_page2.text = "Page 2 text"
        mock_page2.markdown = "# Page 2"
        mock_page2.confidence = 0.85
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_page1, mock_page2]
        mock_paddle_instance.concatenate_markdown_pages.return_value = "# Page 1\n# Page 2"
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        result = service.process_pdf(str(self.sample_pdf_path), "test-pdf-1")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['pdf_id'], 'test-pdf-1')
        self.assertEqual(result['total_pages'], 2)
        self.assertIn('combined_text', result)
        self.assertIn('combined_markdown', result)
        self.assertEqual(len(result['pages']), 2)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_process_batch_success(self, mock_paddle):
        """Test xử lý batch file thành công"""
        mock_result = MagicMock()
        mock_result.text = "Batch text"
        mock_result.markdown = "# Batch"
        mock_result.confidence = 0.88
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        file_paths = [str(self.sample_image_path), str(self.sample_image_path)]
        file_ids = ["batch-1", "batch-2"]
        
        results = service.process_batch(file_paths, file_ids)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['image_id'], 'batch-1')
        self.assertEqual(results[1]['image_id'], 'batch-2')
    
    def test_get_model_status(self):
        """Test lấy trạng thái model"""
        status = self.ocr_service.get_model_status()
        
        self.assertIn('pipeline_loaded', status)
        self.assertIn('features', status)
        self.assertIn('layout_detection', status['features'])
        self.assertIn('doc_orientation', status['features'])


class TestImageProcessor(unittest.TestCase):
    """Test case cho ImageProcessor"""
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        self.processor = ImageProcessor()
        self.test_dir = Path(tempfile.mkdtemp())
        self.sample_image = self.test_dir / "test.jpg"
        self._create_sample_image()
    
    def _create_sample_image(self):
        """Tạo ảnh mẫu"""
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(self.sample_image)
        except ImportError:
            with open(self.sample_image, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')
    
    def tearDown(self):
        """Dọn dẹp"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_process_image_with_high_confidence(self, mock_paddle):
        """Test xử lý ảnh với confidence cao"""
        mock_result = MagicMock()
        mock_result.text = "High confidence text"
        mock_result.confidence = 0.98
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        processor = ImageProcessor()
        processor._ocr_pipeline = mock_paddle_instance
        
        result = processor.process_image(str(self.sample_image))
        
        self.assertEqual(result['status'], 'success')
        self.assertGreaterEqual(result['confidence'], Config.MIN_CONFIDENCE)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_process_image_timing(self, mock_paddle):
        """Test đo thời gian xử lý ảnh"""
        mock_result = MagicMock()
        mock_result.text = "Timing test"
        mock_result.confidence = 0.85
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        processor = ImageProcessor()
        processor._ocr_pipeline = mock_paddle_instance
        
        result = processor.process_image(str(self.sample_image))
        
        self.assertIn('processing_time_ms', result)
        self.assertGreater(result['processing_time_ms'], 0)


class TestBatchProcessor(unittest.TestCase):
    """Test case cho BatchProcessor"""
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        self.processor = BatchProcessor()
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_batch_stats_tracking(self, mock_paddle):
        """Test theo dõi thống kê batch"""
        mock_result = MagicMock()
        mock_result.text = "Stats test"
        mock_result.confidence = 0.90
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        processor = BatchProcessor()
        processor._ocr_pipeline = mock_paddle_instance
        
        # Reset stats trước khi test
        processor.reset_stats()
        
        # Process batch
        file_paths = ["file1.jpg", "file2.jpg"]
        processor.process_batch(file_paths, max_workers=2)
        
        stats = processor.get_batch_stats()
        
        self.assertEqual(stats['total_processed'], 2)
        self.assertGreater(stats['total_time_ms'], 0)
    
    def test_reset_stats(self):
        """Test reset thống kê"""
        self.processor.reset_stats()
        stats = self.processor.get_batch_stats()
        
        self.assertEqual(stats['total_processed'], 0)
        self.assertEqual(stats['total_success'], 0)
        self.assertEqual(stats['total_failed'], 0)


class TestOCRUtils(unittest.TestCase):
    """Test case cho OCR utility functions"""
    
    def test_clean_text(self):
        """Test làm sạch text"""
        from app.services.ocr_utils import clean_text
        
        dirty_text = "  Hello   World  \n  "
        clean = clean_text(dirty_text)
        
        self.assertEqual(clean, "Hello World")
    
    def test_extract_sections(self):
        """Test trích xuất sections từ text"""
        from app.services.ocr_utils import extract_sections
        
        text = """
        Introduction to Python Programming
        by John Doe
        Published by Tech Press 2023
        ISBN: 978-1234567890
        """
        
        sections = extract_sections(text)
        
        self.assertIn('title', sections)
        self.assertIn('author', sections)
        self.assertIn('isbn', sections)
        self.assertIn('year', sections)
    
    def test_calculate_confidence(self):
        """Test tính toán confidence"""
        from app.services.ocr_utils import calculate_confidence
        
        mock_result = MagicMock()
        mock_result.confidence = 0.92
        
        confidence = calculate_confidence(mock_result)
        
        self.assertEqual(confidence, 0.92)
    
    def test_format_for_marc21(self):
        """Test format cho MARC21"""
        from app.services.ocr_utils import format_for_marc21
        
        ocr_result = {
            'ocr_text': 'Sample book text',
            'confidence': 0.90,
            'image_id': 'test-123',
            'processing_time_ms': 1500,
            'layout_detected': True
        }
        
        formatted = format_for_marc21(ocr_result)
        
        self.assertTrue(formatted['ready_for_marc21'])
        self.assertIn('raw_text', formatted)
        self.assertIn('cleaned_text', formatted)
        self.assertIn('sections', formatted)
        self.assertIn('metadata', formatted)


if __name__ == '__main__':
    unittest.main()
