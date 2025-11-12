"""
Metrics Logger cho OCR Service

Module này chứa logger chuyên dụng để theo dõi metrics và performance.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from app.config import Config


class OCRMetricsLogger:
    """
    Logger chuyên dụng cho OCR metrics và performance tracking
    
    Ghi log các metrics như thời gian xử lý, confidence, success rate
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Khởi tạo metrics logger
        
        Args:
            log_dir: Thư mục chứa log files
        """
        self.log_dir = log_dir or Config.LOG_DIR
        self.metrics_file = self.log_dir / 'ocr_metrics.jsonl'
        
        # Đảm bảo thư mục tồn tại
        self.log_dir.mkdir(exist_ok=True, parents=True)
    
    def log_ocr_request(self, request_data: Dict[str, Any]):
        """
        Ghi log OCR request
        
        Args:
            request_data: Dictionary chứa thông tin request
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'ocr_request',
            **request_data
        }
        
        self._write_metrics(log_entry)
    
    def log_ocr_result(self, result_data: Dict[str, Any]):
        """
        Ghi log kết quả OCR
        
        Args:
            result_data: Dictionary chứa kết quả OCR
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'ocr_result',
            **result_data
        }
        
        self._write_metrics(log_entry)
    
    def log_batch_stats(self, batch_stats: Dict[str, Any]):
        """
        Ghi log thống kê batch processing
        
        Args:
            batch_stats: Dictionary chứa thống kê batch
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'batch_stats',
            **batch_stats
        }
        
        self._write_metrics(log_entry)
    
    def log_error(self, error_data: Dict[str, Any]):
        """
        Ghi log lỗi OCR
        
        Args:
            error_data: Dictionary chứa thông tin lỗi
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            **error_data
        }
        
        self._write_metrics(log_entry)
    
    def _write_metrics(self, log_entry: Dict[str, Any]):
        """
        Ghi metrics vào file
        
        Args:
            log_entry: Dictionary chứa log entry
        """
        try:
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error("Failed to write metrics: %s", e)
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Lấy tóm tắt metrics trong khoảng thời gian
        
        Args:
            hours: Số giờ để lấy metrics (mặc định: 24)
            
        Returns:
            Dictionary chứa tóm tắt metrics
        """
        try:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            total_requests = 0
            total_success = 0
            total_failed = 0
            total_time = 0
            confidence_scores = []
            
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
                        
                        if entry_time < cutoff_time:
                            continue
                        
                        if entry['type'] == 'ocr_result':
                            total_requests += 1
                            
                            if entry.get('status') == 'success':
                                total_success += 1
                                total_time += entry.get('processing_time_ms', 0)
                                
                                if 'confidence' in entry:
                                    confidence_scores.append(entry['confidence'])
                            else:
                                total_failed += 1
                    
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            avg_time = total_time / total_success if total_success > 0 else 0
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'period_hours': hours,
                'total_requests': total_requests,
                'total_success': total_success,
                'total_failed': total_failed,
                'success_rate': round(success_rate, 2),
                'avg_processing_time_ms': round(avg_time, 2),
                'avg_confidence': round(avg_confidence, 4),
                'timestamp': datetime.now().isoformat()
            }
        
        except FileNotFoundError:
            return {
                'period_hours': hours,
                'total_requests': 0,
                'total_success': 0,
                'total_failed': 0,
                'success_rate': 0,
                'avg_processing_time_ms': 0,
                'avg_confidence': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def clear_old_metrics(self, days: int = 30):
        """
        Xóa metrics cũ hơn số ngày chỉ định
        
        Args:
            days: Số ngày để giữ lại metrics
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            temp_file = self.metrics_file.with_suffix('.tmp')
            
            with open(self.metrics_file, 'r', encoding='utf-8') as f_in:
                with open(temp_file, 'w', encoding='utf-8') as f_out:
                    for line in f_in:
                        try:
                            entry = json.loads(line)
                            entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
                            
                            # Giữ lại entry mới hơn cutoff
                            if entry_time >= cutoff_time:
                                f_out.write(line)
                        
                        except (json.JSONDecodeError, KeyError):
                            continue
            
            # Replace file gốc
            temp_file.replace(self.metrics_file)
            logging.info("Cleared metrics older than %d days", days)
        
        except FileNotFoundError:
            logging.warning("Metrics file not found for cleanup")
        except Exception as e:
            logging.error("Failed to clear old metrics: %s", e)


# Khởi tạo global metrics logger
metrics_logger = OCRMetricsLogger()
