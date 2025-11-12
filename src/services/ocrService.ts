/**
 * OCR Service - Kết nối với Backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api/ocr';

export interface OCRResult {
  status: 'success' | 'error' | 'queued';
  file_id?: string;
  extracted_text?: string;
  markdown?: string;
  sections?: {
    title?: string;
    author?: string;
    publisher?: string;
    isbn?: string;
    year?: string;
  };
  confidence?: number;
  processing_time?: number;
  timestamp?: string;
  error_code?: string;
  message?: string;
  queue_position?: number;
  estimated_wait_time?: number;
  request_id?: string;
}

export interface BatchOCRResult {
  status: 'success' | 'error';
  total_files: number;
  results: OCRResult[];
}

export interface ServiceStatus {
  status: 'ok' | 'error';
  pipeline?: {
    initialized: boolean;
    model_loaded: boolean;
    last_used: string;
    auto_unload_enabled: boolean;
    will_unload_in_seconds?: number;
  };
  gpu?: {
    available: boolean;
    device_count: number;
    current_device: number;
    memory_used_mb: number;
    memory_total_mb: number;
  };
  queue?: {
    queue_size: number;
    active_requests: number;
    max_concurrent: number;
    max_queue_size: number;
    total_queued: number;
    total_processed: number;
    total_failed: number;
    total_timeout: number;
  };
  config?: {
    use_gpu: boolean;
    max_batch_size: number;
    max_file_size_mb: number;
    supported_formats: string[];
  };
}

class OCRService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Xử lý một file ảnh để OCR
   */
  async processFile(file: File): Promise<OCRResult> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${this.baseUrl}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'OCR processing failed');
      }

      const result: OCRResult = await response.json();
      return result;
    } catch (error) {
      console.error('Error processing file:', error);
      throw error;
    }
  }

  /**
   * Xử lý nhiều file cùng lúc (batch)
   */
  async processBatch(files: File[]): Promise<BatchOCRResult> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(`${this.baseUrl}/batch`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Batch OCR processing failed');
      }

      const result: BatchOCRResult = await response.json();
      return result;
    } catch (error) {
      console.error('Error processing batch:', error);
      throw error;
    }
  }

  /**
   * Lấy trạng thái service hoặc request cụ thể
   */
  async getStatus(requestId?: string): Promise<ServiceStatus | OCRResult> {
    try {
      const url = requestId
        ? `${this.baseUrl}/status/${requestId}`
        : `${this.baseUrl}/status`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Failed to get status');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting status:', error);
      throw error;
    }
  }

  /**
   * Lấy metrics và thống kê
   */
  async getMetrics(hours: number = 24) {
    try {
      const response = await fetch(`${this.baseUrl}/metrics?hours=${hours}`);

      if (!response.ok) {
        throw new Error('Failed to get metrics');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting metrics:', error);
      throw error;
    }
  }

  /**
   * Download kết quả đã xử lý
   */
  async downloadResult(fileId: string, format: 'json' | 'markdown'): Promise<Blob> {
    try {
      const response = await fetch(`${this.baseUrl}/download/${fileId}/${format}`);

      if (!response.ok) {
        throw new Error('Failed to download result');
      }

      return await response.blob();
    } catch (error) {
      console.error('Error downloading result:', error);
      throw error;
    }
  }

  /**
   * Polling status cho queued request
   */
  async pollRequestStatus(
    requestId: string,
    onUpdate?: (status: OCRResult) => void,
    interval: number = 2000,
    maxAttempts: number = 30
  ): Promise<OCRResult> {
    let attempts = 0;

    return new Promise((resolve, reject) => {
      const poll = setInterval(async () => {
        attempts++;

        try {
          const status = (await this.getStatus(requestId)) as OCRResult;

          if (onUpdate) {
            onUpdate(status);
          }

          // Đã hoàn thành
          if (status.status === 'success' || status.status === 'error') {
            clearInterval(poll);
            resolve(status);
          }

          // Timeout
          if (attempts >= maxAttempts) {
            clearInterval(poll);
            reject(new Error('Polling timeout'));
          }
        } catch (error) {
          clearInterval(poll);
          reject(error);
        }
      }, interval);
    });
  }
}

// Export singleton instance
export const ocrService = new OCRService();
