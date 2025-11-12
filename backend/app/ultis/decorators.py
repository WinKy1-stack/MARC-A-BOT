"""
Logging Decorators

Module này chứa các decorator để tự động log execution time và API requests.
"""

import logging
import time
from functools import wraps

from app.ultis.metrics_logger import OCRMetricsLogger


def log_execution_time(func):
    """
    Decorator để log thời gian thực thi của function
    
    Args:
        func: Function cần đo thời gian
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('ocr_service')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(
                "Function %s executed in %.2f ms",
                func.__name__,
                execution_time
            )
            
            return result
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(
                "Function %s failed after %.2f ms: %s",
                func.__name__,
                execution_time,
                str(e)
            )
            raise
    
    return wrapper


def log_api_request(func):
    """
    Decorator để log API request và response
    
    Args:
        func: API endpoint function
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        
        logger = logging.getLogger('ocr_service')
        metrics_logger = OCRMetricsLogger()
        
        start_time = time.time()
        
        # Log request
        request_data = {
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr
        }
        
        logger.info("API Request: %s %s", request.method, request.path)
        
        try:
            response = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            # Log response
            status_code = getattr(response, 'status_code', 200)
            logger.info(
                "API Response: %s %s - Status: %d - Time: %.2f ms",
                request.method,
                request.path,
                status_code,
                execution_time
            )
            
            # Log metrics
            request_data.update({
                'status_code': status_code,
                'execution_time_ms': round(execution_time, 2)
            })
            metrics_logger.log_ocr_request(request_data)
            
            return response
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(
                "API Error: %s %s - Error: %s - Time: %.2f ms",
                request.method,
                request.path,
                str(e),
                execution_time
            )
            
            # Log error metrics
            metrics_logger.log_error({
                'endpoint': request.endpoint,
                'method': request.method,
                'error': str(e),
                'execution_time_ms': round(execution_time, 2)
            })
            
            raise
    
    return wrapper


def log_ocr_operation(operation_type: str = 'ocr'):
    """
    Decorator để log các thao tác OCR
    
    Args:
        operation_type: Loại thao tác (ocr, batch, pdf)
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('ocr_service')
            metrics_logger = OCRMetricsLogger()
            
            start_time = time.time()
            
            logger.info("Starting %s operation: %s", operation_type, func.__name__)
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Log kết quả
                if isinstance(result, dict):
                    metrics_logger.log_ocr_result({
                        'operation': operation_type,
                        'function': func.__name__,
                        'status': result.get('status', 'unknown'),
                        'processing_time_ms': execution_time,
                        'confidence': result.get('confidence', 0)
                    })
                
                logger.info(
                    "Completed %s operation: %s in %.2f ms",
                    operation_type,
                    func.__name__,
                    execution_time
                )
                
                return result
            
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                metrics_logger.log_error({
                    'operation': operation_type,
                    'function': func.__name__,
                    'error': str(e),
                    'processing_time_ms': execution_time
                })
                
                logger.error(
                    "Failed %s operation: %s after %.2f ms - %s",
                    operation_type,
                    func.__name__,
                    execution_time,
                    str(e)
                )
                
                raise
        
        return wrapper
    return decorator
