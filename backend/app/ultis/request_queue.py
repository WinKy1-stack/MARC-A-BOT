"""
Request Queue Management

Module này quản lý queue cho OCR requests khi hệ thống quá tải.
"""

import time
import logging
import threading
from queue import Queue, Full, Empty
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum

from app.config import Config

logger = logging.getLogger(__name__)


class RequestStatus(Enum):
    """Trạng thái của request trong queue"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class QueuedRequest:
    """Đại diện cho một request trong queue"""
    request_id: str
    func: Callable
    args: tuple
    kwargs: dict
    created_at: float
    status: RequestStatus = RequestStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    progress_info: Optional[Dict[str, Any]] = None  # Detailed progress information


class RequestQueueManager:
    """
    Quản lý queue cho OCR requests
    
    Giới hạn số lượng request xử lý đồng thời,
    các request vượt quá sẽ được đưa vào queue chờ.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.queue = Queue(maxsize=Config.QUEUE_MAX_SIZE)
            self.active_requests = 0
            self.active_lock = threading.Lock()
            self.requests_dict = {}
            self.requests_lock = threading.Lock()
            
            # Statistics
            self.total_queued = 0
            self.total_processed = 0
            self.total_failed = 0
            self.total_timeout = 0
            
            self._initialized = True
            logger.info("Request Queue Manager initialized")
    
    def submit_request(
        self,
        request_id: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Submit request vào queue hoặc xử lý ngay
        
        Args:
            request_id: ID của request
            func: Function cần thực thi
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Dictionary chứa kết quả hoặc thông tin queue
        """
        if not Config.ENABLE_REQUEST_QUEUE:
            # Queue disabled, xử lý trực tiếp
            try:
                result = func(*args, **kwargs)
                return {
                    'status': 'completed',
                    'result': result,
                    'queued': False
                }
            except Exception as e:
                logger.error("Error processing request %s: %s", request_id, e)
                return {
                    'status': 'failed',
                    'error': str(e),
                    'queued': False
                }
        
        # LUÔN queue request để có thể track progress qua SSE
        # Ngay cả khi có slot trống, vẫn đưa vào queue và xử lý background
        try:
            queued_request = QueuedRequest(
                request_id=request_id,
                func=func,
                args=args,
                kwargs=kwargs,
                created_at=time.time()
            )

            self.queue.put(queued_request, block=False)

            with self.requests_lock:
                self.requests_dict[request_id] = queued_request

            self.total_queued += 1

            logger.info(
                "Request %s queued. Queue size: %d",
                request_id,
                self.queue.qsize()
            )

            # Trigger processing ngay nếu có slot trống
            self._process_next_in_queue()

            return {
                'status': 'queued',
                'request_id': request_id,
                'queue_position': self.queue.qsize(),
                'estimated_wait_time': self._estimate_wait_time(),
                'queued': True
            }

        except Full:
            logger.error("Queue is full, rejecting request %s", request_id)
            return {
                'status': 'rejected',
                'error': 'Queue is full',
                'queue_size': Config.QUEUE_MAX_SIZE,
                'queued': False
            }
    
    def _process_next_in_queue(self):
        """Xử lý request tiếp theo trong queue"""
        try:
            # Lấy request từ queue
            queued_request = self.queue.get(block=False)
            
            # Kiểm tra timeout
            wait_time = time.time() - queued_request.created_at
            if wait_time > Config.QUEUE_TIMEOUT:
                logger.warning(
                    "Request %s timeout after %.1f seconds",
                    queued_request.request_id,
                    wait_time
                )
                queued_request.status = RequestStatus.TIMEOUT
                queued_request.error = "Request timeout in queue"
                self.total_timeout += 1
                return
            
            # Xử lý trong thread riêng
            thread = threading.Thread(
                target=self._execute_queued_request,
                args=(queued_request,)
            )
            thread.daemon = True
            thread.start()
        
        except Empty:
            # Queue trống
            pass
    
    def _execute_queued_request(self, queued_request: QueuedRequest):
        """Thực thi request từ queue"""
        with self.active_lock:
            self.active_requests += 1
        
        try:
            queued_request.status = RequestStatus.PROCESSING
            
            result = queued_request.func(
                *queued_request.args,
                **queued_request.kwargs
            )
            
            queued_request.result = result
            queued_request.status = RequestStatus.COMPLETED
            self.total_processed += 1
            
            logger.info("Request %s completed", queued_request.request_id)
        
        except Exception as e:
            logger.error(
                "Error executing queued request %s: %s",
                queued_request.request_id,
                e
            )
            queued_request.status = RequestStatus.FAILED
            queued_request.error = str(e)
            self.total_failed += 1
        
        finally:
            with self.active_lock:
                self.active_requests -= 1
            
            # Xử lý request tiếp theo
            self._process_next_in_queue()
    
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy trạng thái của request

        Args:
            request_id: ID của request

        Returns:
            Dictionary chứa trạng thái hoặc None
        """
        with self.requests_lock:
            queued_request = self.requests_dict.get(request_id)

        if queued_request is None:
            return None

        status_dict = {
            'request_id': request_id,
            'status': queued_request.status.value,
            'created_at': queued_request.created_at,
            'wait_time': time.time() - queued_request.created_at,
            'result': queued_request.result,
            'error': queued_request.error
        }

        # Include progress info if available
        if queued_request.progress_info:
            status_dict['progress_info'] = queued_request.progress_info

        return status_dict

    def update_request_progress(self, request_id: str, progress_info: Dict[str, Any]):
        """
        Cập nhật progress information cho request

        Args:
            request_id: ID của request
            progress_info: Dictionary chứa thông tin tiến trình
                          VD: {'step': 'loading_model', 'message': 'Đang load model...', 'progress': 10}
        """
        with self.requests_lock:
            queued_request = self.requests_dict.get(request_id)
            if queued_request:
                queued_request.progress_info = progress_info
                logger.debug("Progress updated for request %s: %s", request_id, progress_info)
    
    def _estimate_wait_time(self) -> int:
        """
        Ước tính thời gian chờ (giây)
        
        Returns:
            Số giây ước tính
        """
        # Giả định mỗi request mất ~2 giây
        avg_processing_time = 2
        queue_size = self.queue.qsize()
        concurrent = Config.MAX_CONCURRENT_REQUESTS
        
        estimated = (queue_size * avg_processing_time) // concurrent
        return max(1, estimated)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê queue
        
        Returns:
            Dictionary chứa thống kê
        """
        return {
            'queue_size': self.queue.qsize(),
            'active_requests': self.active_requests,
            'max_concurrent': Config.MAX_CONCURRENT_REQUESTS,
            'max_queue_size': Config.QUEUE_MAX_SIZE,
            'total_queued': self.total_queued,
            'total_processed': self.total_processed,
            'total_failed': self.total_failed,
            'total_timeout': self.total_timeout,
            'queue_enabled': Config.ENABLE_REQUEST_QUEUE
        }
    
    def clear_queue(self):
        """Xóa tất cả request trong queue"""
        cleared = 0
        try:
            while True:
                self.queue.get(block=False)
                cleared += 1
        except Empty:
            pass
        
        logger.info("Cleared %d requests from queue", cleared)
        return cleared


# Khởi tạo global queue manager
queue_manager = RequestQueueManager()
