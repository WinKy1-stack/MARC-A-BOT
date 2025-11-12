"""
Performance test cho OCR Service

Module này chứa các test về hiệu năng và throughput của OCR service.
"""

import unittest
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.ocr_service import OCRService
from app.services.batch_processor import BatchProcessor
from app.config import Config


class TestOCRPerformance(unittest.TestCase):
    """Test case cho hiệu năng OCR"""
    
    @classmethod
    def setUpClass(cls):
        """Thiết lập một lần cho tất cả test"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.sample_images = []
        
        # Tạo nhiều ảnh mẫu
        for i in range(10):
            image_path = cls.test_dir / f"sample_{i}.jpg"
            cls._create_sample_image(image_path, i)
            cls.sample_images.append(str(image_path))
    
    @staticmethod
    def _create_sample_image(path, color_index=0):
        """Tạo ảnh mẫu với màu sắc khác nhau"""
        try:
            from PIL import Image
            color_value = (color_index * 25) % 255
            img = Image.new('RGB', (200, 200), color=(color_value, color_value, color_value))
            img.save(path)
        except ImportError:
            with open(path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')
    
    @classmethod
    def tearDownClass(cls):
        """Dọn dẹp sau tất cả test"""
        import shutil
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_single_image_processing_time(self, mock_paddle):
        """Test thời gian xử lý ảnh đơn"""
        mock_result = MagicMock()
        mock_result.text = "Performance test text"
        mock_result.confidence = 0.90
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        start_time = time.time()
        result = service.process_image(self.sample_images[0])
        elapsed_time = (time.time() - start_time) * 1000
        
        self.assertEqual(result['status'], 'success')
        self.assertLess(elapsed_time, 5000, "Xử lý ảnh đơn nên < 5s")
        print(f"Thời gian xử lý ảnh đơn: {elapsed_time:.2f}ms")
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_batch_processing_throughput(self, mock_paddle):
        """Test throughput của batch processing"""
        mock_result = MagicMock()
        mock_result.text = "Batch test text"
        mock_result.confidence = 0.85
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        # Test với 10 ảnh
        batch_size = 10
        start_time = time.time()
        
        results = service.process_batch(self.sample_images[:batch_size])
        
        elapsed_time = (time.time() - start_time) * 1000
        avg_time_per_image = elapsed_time / batch_size
        
        self.assertEqual(len(results), batch_size)
        print(f"Batch {batch_size} ảnh: Tổng {elapsed_time:.2f}ms, "
              f"Trung bình {avg_time_per_image:.2f}ms/ảnh")
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_concurrent_vs_sequential_processing(self, mock_paddle):
        """Test so sánh xử lý đồng thời vs tuần tự"""
        mock_result = MagicMock()
        mock_result.text = "Concurrent test"
        mock_result.confidence = 0.87
        
        mock_paddle_instance = MagicMock()
        
        # Simulate processing delay
        def slow_predict(*_args, **_kwargs):
            time.sleep(0.1)  # Simulate 100ms processing
            return [mock_result]
        
        mock_paddle_instance.predict.side_effect = slow_predict
        mock_paddle.return_value = mock_paddle_instance
        
        processor = BatchProcessor()
        processor._ocr_pipeline = mock_paddle_instance
        
        batch_size = 5
        
        # Test với max_workers=1 (tuần tự)
        start_time = time.time()
        processor.process_batch(self.sample_images[:batch_size], max_workers=1)
        sequential_time = (time.time() - start_time) * 1000
        
        # Test với max_workers=3 (đồng thời)
        start_time = time.time()
        processor.process_batch(self.sample_images[:batch_size], max_workers=3)
        concurrent_time = (time.time() - start_time) * 1000
        
        print(f"Tuần tự: {sequential_time:.2f}ms")
        print(f"Đồng thời (3 workers): {concurrent_time:.2f}ms")
        print(f"Cải thiện: {((sequential_time - concurrent_time) / sequential_time * 100):.1f}%")
        
        # Xử lý đồng thời nên nhanh hơn
        self.assertLess(concurrent_time, sequential_time)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_memory_usage_batch(self, mock_paddle):
        """Test sử dụng bộ nhớ trong batch processing"""
        import psutil
        import os
        
        mock_result = MagicMock()
        mock_result.text = "Memory test"
        mock_result.confidence = 0.88
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        # Đo memory trước khi xử lý
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Xử lý batch
        service.process_batch(self.sample_images)
        
        # Đo memory sau khi xử lý
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before
        
        print(f"Memory trước: {mem_before:.2f}MB")
        print(f"Memory sau: {mem_after:.2f}MB")
        print(f"Tăng: {mem_increase:.2f}MB")
        
        # Memory tăng không nên quá 500MB cho 10 ảnh
        self.assertLess(mem_increase, 500)
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_batch_stats_accuracy(self, mock_paddle):
        """Test độ chính xác của batch statistics"""
        mock_result = MagicMock()
        mock_result.text = "Stats test"
        mock_result.confidence = 0.90
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        processor = BatchProcessor()
        processor._ocr_pipeline = mock_paddle_instance
        processor.reset_stats()
        
        # Xử lý 2 batch
        batch1_size = 3
        batch2_size = 5
        
        processor.process_batch(self.sample_images[:batch1_size])
        processor.process_batch(self.sample_images[:batch2_size])
        
        stats = processor.get_batch_stats()
        
        expected_total = batch1_size + batch2_size
        self.assertEqual(stats['total_processed'], expected_total)
        self.assertEqual(stats['total_success'], expected_total)
        self.assertEqual(stats['total_failed'], 0)
        self.assertEqual(stats['success_rate'], 100.0)
        
        print(f"Stats: {stats}")


class TestOCRStressTest(unittest.TestCase):
    """Stress test cho OCR service"""
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_high_load_processing(self, mock_paddle):
        """Test xử lý với tải cao"""
        mock_result = MagicMock()
        mock_result.text = "Stress test"
        mock_result.confidence = 0.85
        
        mock_paddle_instance = MagicMock()
        mock_paddle_instance.predict.return_value = [mock_result]
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        # Simulate xử lý nhiều request liên tiếp
        num_requests = 50
        success_count = 0
        total_time = 0
        
        for i in range(num_requests):
            start_time = time.time()
            try:
                result = service.process_image(f"test_{i}.jpg")
                if result['status'] == 'success':
                    success_count += 1
                total_time += (time.time() - start_time) * 1000
            except (RuntimeError, ValueError) as e:
                print(f"Request {i} failed: {e}")
        
        avg_time = total_time / num_requests
        success_rate = (success_count / num_requests) * 100
        
        print(f"Processed {num_requests} requests")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Average time: {avg_time:.2f}ms")
        
        # Success rate nên >= 95%
        self.assertGreaterEqual(success_rate, 95.0)


class TestOCRTimeout(unittest.TestCase):
    """Test timeout và error handling"""
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_timeout_handling(self, mock_paddle):
        """Test xử lý timeout"""
        mock_paddle_instance = MagicMock()
        
        # Simulate timeout
        def timeout_predict(*_args, **_kwargs):
            time.sleep(Config.REQUEST_TIMEOUT + 1)
            return []
        
        mock_paddle_instance.predict.side_effect = timeout_predict
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        # Test với timeout ngắn
        with self.assertRaises(Exception):
            service.process_image("test.jpg")
    
    @patch('app.services.base_ocr_service.PaddleOCRVL')
    def test_error_recovery(self, mock_paddle):
        """Test khả năng phục hồi sau lỗi"""
        mock_paddle_instance = MagicMock()
        
        # Lần đầu fail, lần sau success
        call_count = 0
        
        def intermittent_predict(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                raise RuntimeError("Temporary failure")
            
            mock_result = MagicMock()
            mock_result.text = "Recovered"
            mock_result.confidence = 0.85
            return [mock_result]
        
        mock_paddle_instance.predict.side_effect = intermittent_predict
        mock_paddle.return_value = mock_paddle_instance
        
        service = OCRService()
        service._ocr_pipeline = mock_paddle_instance
        
        # Lần đầu fail
        result1 = service.process_image("test1.jpg")
        self.assertEqual(result1['status'], 'error')
        
        # Lần sau success
        result2 = service.process_image("test2.jpg")
        self.assertEqual(result2['status'], 'success')


if __name__ == '__main__':
    # Chạy test với verbose output
    unittest.main(verbosity=2)
