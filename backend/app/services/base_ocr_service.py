import time
import logging
import threading
from typing import Dict
from paddleocr import PaddleOCR
from app.config import Config
from app.ultis.gpu_utils import select_device

logger = logging.getLogger(__name__)


class BaseOCRService:
    """Service cơ sở cho OCR với khởi tạo và quản lý pipeline"""
    
    _instance = None
    _ocr_pipeline = None
    _last_used = None
    _cleanup_timer = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BaseOCRService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._ocr_pipeline is None:
            self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Khởi tạo pipeline PaddleOCR"""
        try:
            # PaddleOCR 3.x sử dụng device thay vì use_gpu
            device = 'gpu:0' if Config.USE_GPU else 'cpu'
            
            logger.info("Initializing PaddleOCR pipeline on %s...", device)
            
            # Khởi tạo PaddleOCR với device parameter (PaddleOCR 3.x)
            self._ocr_pipeline = PaddleOCR(
                device=device,  # 'gpu:0' hoặc 'cpu'
                use_angle_cls=True,  # Nhận diện góc xoay
                lang='en',  # English OCR
                det_db_thresh=0.3,  # Detection threshold
                det_db_box_thresh=0.5,  # Box threshold
                rec_batch_num=6  # Batch size cho recognition
            )
            
            self._last_used = time.time()
            logger.info("PaddleOCR pipeline initialized successfully on %s", device)
            
            # Bắt đầu cleanup timer nếu được bật
            if Config.ENABLE_MODEL_AUTO_UNLOAD:
                self._start_cleanup_timer()
            
        except Exception as e:
            logger.error("Failed to initialize OCR pipeline: %s", e)
            raise RuntimeError(f"OCR pipeline initialization failed: {e}") from e
    
    def _ensure_pipeline_ready(self):
        """Đảm bảo pipeline đã được khởi tạo trước khi sử dụng"""
        with self._lock:
            if self._ocr_pipeline is None:
                self._initialize_pipeline()
    
    def _update_last_used(self):
        """Cập nhật timestamp lần sử dụng cuối"""
        self._last_used = time.time()
        
        # Reset cleanup timer
        if Config.ENABLE_MODEL_AUTO_UNLOAD:
            self._start_cleanup_timer()
    
    def _start_cleanup_timer(self):
        """Bắt đầu timer để tự động dọn dẹp model"""
        # Hủy timer cũ nếu có
        if self._cleanup_timer is not None:
            self._cleanup_timer.cancel()
        
        # Tạo timer mới
        self._cleanup_timer = threading.Timer(
            Config.MODEL_IDLE_TIMEOUT,
            self._cleanup_idle_model
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _cleanup_idle_model(self):
        """Giải phóng model nếu idle quá lâu"""
        with self._lock:
            if self._ocr_pipeline is None:
                return
            
            idle_time = time.time() - self._last_used if self._last_used else 0
            
            if idle_time >= Config.MODEL_IDLE_TIMEOUT:
                logger.info(
                    "Unloading OCR model after %.1f seconds of inactivity",
                    idle_time
                )
                
                try:
                    # Giải phóng model
                    del self._ocr_pipeline
                    self._ocr_pipeline = None
                    
                    # Force garbage collection
                    import gc
                    gc.collect()
                    
                    logger.info("OCR model unloaded successfully")
                
                except Exception as e:
                    logger.error("Error unloading OCR model: %s", e)
    
    def force_unload_model(self):
        """Giải phóng model ngay lập tức (manual)"""
        with self._lock:
            if self._cleanup_timer is not None:
                self._cleanup_timer.cancel()
                self._cleanup_timer = None
            
            if self._ocr_pipeline is not None:
                logger.info("Manually unloading OCR model")
                del self._ocr_pipeline
                self._ocr_pipeline = None
                
                import gc
                gc.collect()
                
                logger.info("OCR model unloaded")
    
    def get_model_status(self) -> Dict:
        """Lấy trạng thái hiện tại của pipeline"""
        idle_time = int(time.time() - self._last_used) if self._last_used else None
        
        return {
            "pipeline_loaded": self._ocr_pipeline is not None,
            "last_used": self._last_used,
            "idle_time_seconds": idle_time,
            "auto_unload_enabled": Config.ENABLE_MODEL_AUTO_UNLOAD,
            "idle_timeout_seconds": Config.MODEL_IDLE_TIMEOUT,
            "will_unload_in_seconds": (
                max(0, Config.MODEL_IDLE_TIMEOUT - idle_time)
                if self._ocr_pipeline is not None and idle_time is not None
                else None
            ),
            "features": {
                "layout_detection": Config.USE_LAYOUT_DETECTION,
                "doc_orientation": Config.USE_DOC_ORIENTATION,
                "doc_unwarping": Config.USE_DOC_UNWARPING
            }
        }
