"""
Integration test cho OCR API routes

Module này chứa các integration test cho các endpoint API OCR,
bao gồm upload file, xử lý batch, và download kết quả.
"""

import unittest
import json
import io
from unittest.mock import patch

from app.config import Config
# Import app factory function
from app import create_app


class TestOCRRoutes(unittest.TestCase):
    """Test case cho OCR API routes"""
    
    @classmethod
    def setUpClass(cls):
        """Thiết lập một lần cho tất cả test"""
        Config.init_app()
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """Test endpoint health check"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
    
    def test_home_endpoint(self):
        """Test endpoint home"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'running')
        self.assertIn('endpoints', data)
    
    def test_ocr_status(self):
        """Test endpoint OCR status"""
        response = self.client.get('/api/ocr/status')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('config', data)
    
    @patch('app.services.ocr_service.OCRService.process_image')
    def test_process_single_image_success(self, mock_process):
        """Test xử lý ảnh đơn lẻ thành công"""
        # Mock return value
        mock_process.return_value = {
            'status': 'success',
            'image_id': 'test-123',
            'ocr_text': 'Sample OCR text',
            'confidence': 0.95,
            'processing_time_ms': 1200,
            'error': None
        }
        
        # Tạo file giả
        data = {
            'file': (io.BytesIO(b'fake image data'), 'test.jpg')
        }
        
        response = self.client.post(
            '/api/ocr/process',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['status'], 'success')
        self.assertIn('ocr_text', result)
    
    def test_process_no_file(self):
        """Test xử lý khi không có file"""
        response = self.client.post('/api/ocr/process')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error_code'], 'NO_FILE')
    
    def test_process_empty_filename(self):
        """Test xử lý với tên file rỗng"""
        data = {
            'file': (io.BytesIO(b'data'), '')
        }
        
        response = self.client.post(
            '/api/ocr/process',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertEqual(result['error_code'], 'EMPTY_FILENAME')
    
    def test_process_invalid_format(self):
        """Test xử lý với định dạng file không hợp lệ"""
        data = {
            'file': (io.BytesIO(b'data'), 'test.xyz')
        }
        
        response = self.client.post(
            '/api/ocr/process',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertEqual(result['error_code'], 'INVALID_FORMAT')
    
    @patch('app.services.ocr_service.OCRService.process_batch')
    def test_process_batch_success(self, mock_batch):
        """Test xử lý batch file thành công"""
        # Mock return value
        mock_batch.return_value = [
            {
                'status': 'success',
                'image_id': 'batch-1',
                'ocr_text': 'Text 1',
                'confidence': 0.90,
                'processing_time_ms': 1000
            },
            {
                'status': 'success',
                'image_id': 'batch-2',
                'ocr_text': 'Text 2',
                'confidence': 0.88,
                'processing_time_ms': 1100
            }
        ]
        
        # Tạo nhiều file giả
        data = {
            'files': [
                (io.BytesIO(b'image 1'), 'test1.jpg'),
                (io.BytesIO(b'image 2'), 'test2.jpg')
            ]
        }
        
        response = self.client.post(
            '/api/ocr/batch',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['total_files'], 2)
    
    def test_batch_no_files(self):
        """Test batch khi không có file"""
        response = self.client.post('/api/ocr/batch')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error_code'], 'NO_FILES')
    
    def test_batch_exceeds_limit(self):
        """Test batch vượt quá giới hạn"""
        # Tạo quá nhiều file
        files = [(io.BytesIO(b'data'), f'test{i}.jpg') 
                 for i in range(Config.MAX_BATCH_SIZE + 1)]
        
        data = {'files': files}
        
        response = self.client.post(
            '/api/ocr/batch',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertEqual(result['error_code'], 'BATCH_TOO_LARGE')
    
    def test_download_invalid_file_type(self):
        """Test download với loại file không hợp lệ"""
        response = self.client.get('/api/ocr/download/test-123/invalid')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Invalid file type', data['message'])
    
    def test_download_file_not_found(self):
        """Test download file không tồn tại"""
        response = self.client.get('/api/ocr/download/nonexistent-id/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_404_error(self):
        """Test xử lý lỗi 404"""
        response = self.client.get('/api/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error_code'], 'NOT_FOUND')


class TestValidators(unittest.TestCase):
    """Test case cho validator functions"""
    
    def test_allowed_file_valid(self):
        """Test kiểm tra file hợp lệ"""
        from app.ultis.validators import allowed_file
        
        self.assertTrue(allowed_file('test.jpg'))
        self.assertTrue(allowed_file('test.png'))
        self.assertTrue(allowed_file('test.pdf'))
        self.assertTrue(allowed_file('document.jpeg'))
    
    def test_allowed_file_invalid(self):
        """Test kiểm tra file không hợp lệ"""
        from app.ultis.validators import allowed_file
        
        self.assertFalse(allowed_file('test.exe'))
        self.assertFalse(allowed_file('test.txt'))
        self.assertFalse(allowed_file('test'))
        self.assertFalse(allowed_file(''))
    
    def test_sanitize_filename(self):
        """Test làm sạch tên file"""
        from app.ultis.validators import sanitize_filename
        
        # Test với ký tự đặc biệt
        clean = sanitize_filename('file with spaces.jpg')
        self.assertEqual(clean, 'file_with_spaces.jpg')
        
        # Test với ký tự không hợp lệ
        clean = sanitize_filename('file@#$%.jpg')
        self.assertNotIn('@', clean)
        self.assertNotIn('#', clean)
    
    def test_validate_file_size(self):
        """Test kiểm tra kích thước file"""
        from app.ultis.validators import validate_file_size
        
        # Tạo file giả nhỏ
        small_file = io.BytesIO(b'x' * 1000)  # 1KB
        self.assertTrue(validate_file_size(small_file))
        
        # Tạo file giả lớn (vượt quá MAX_FILE_SIZE)
        large_file = io.BytesIO(b'x' * (Config.MAX_FILE_SIZE + 1000))
        self.assertFalse(validate_file_size(large_file))


class TestGPUUtils(unittest.TestCase):
    """Test case cho GPU utility functions"""
    
    def test_check_gpu_available(self):
        """Test kiểm tra GPU khả dụng"""
        from app.ultis.gpu_utils import check_gpu_available
        
        # Hàm này sẽ trả về bool
        result = check_gpu_available()
        self.assertIsInstance(result, bool)
    
    def test_get_gpu_info(self):
        """Test lấy thông tin GPU"""
        from app.ultis.gpu_utils import get_gpu_info
        
        info = get_gpu_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('available', info)
        self.assertIn('count', info)
    
    def test_select_device(self):
        """Test chọn thiết bị"""
        from app.ultis.gpu_utils import select_device
        
        # Test với GPU preference
        device = select_device(use_gpu=True)
        self.assertIn(device, ['gpu', 'cpu'])
        
        # Test với CPU only
        device = select_device(use_gpu=False)
        self.assertEqual(device, 'cpu')
    
    def test_get_system_info(self):
        """Test lấy thông tin hệ thống"""
        from app.ultis.gpu_utils import get_system_info
        
        info = get_system_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('platform', info)
        self.assertIn('python_version', info)


if __name__ == '__main__':
    unittest.main()
