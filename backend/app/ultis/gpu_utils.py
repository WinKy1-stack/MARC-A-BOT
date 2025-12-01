import logging
import platform
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def check_gpu_available() -> bool:
    """
    Kiểm tra xem GPU có khả dụng cho tính toán không
    
    Returns:
        True nếu GPU khả dụng, False nếu không
    """
    try:
        import paddle
        return paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
    except ImportError:
        logger.warning("PaddlePaddle not installed, GPU check skipped")
        return False
    except Exception as e:
        logger.error(f"Error checking GPU availability: {e}")
        return False


def get_gpu_info() -> Dict:
    """
    Lấy thông tin GPU
    
    Returns:
        Dictionary chứa thông tin GPU
    """
    info = {
        "available": False,
        "count": 0,
        "devices": [],
        "cuda_version": None,
        "driver_version": None
    }
    
    try:
        import paddle
        
        if paddle.device.is_compiled_with_cuda():
            info["available"] = True
            info["count"] = paddle.device.cuda.device_count()
            info["cuda_version"] = paddle.version.cuda()
            
            # Get device names
            for i in range(info["count"]):
                try:
                    device_name = paddle.device.cuda.get_device_name(i)
                    device_capability = paddle.device.cuda.get_device_capability(i)
                    info["devices"].append({
                        "id": i,
                        "name": device_name,
                        "capability": f"{device_capability[0]}.{device_capability[1]}"
                    })
                except Exception as e:
                    logger.warning(f"Could not get info for GPU {i}: {e}")
        
    except ImportError:
        logger.info("PaddlePaddle not installed")
    except Exception as e:
        logger.error(f"Error getting GPU info: {e}")
    
    return info


def select_device(use_gpu: bool = True) -> str:
    """
    Chọn thiết bị tính toán (GPU hoặc CPU)
    
    Args:
        use_gpu: Có ưu tiên GPU nếu khả dụng không
        
    Returns:
        Chuỗi device: 'gpu' hoặc 'cpu'
    """
    if use_gpu and check_gpu_available():
        logger.info("GPU is available and will be used")
        return 'gpu'
    else:
        logger.info("Using CPU for computation")
        return 'cpu'


def get_system_info() -> Dict:
    """
    Lấy thông tin hệ thống
    
    Returns:
        Dictionary chứa thông tin hệ thống
    """
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }
