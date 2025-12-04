/**
 * OCR Service - Kết nối với Backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api/ocr';
const SSE_BASE_URL = API_BASE_URL; // SSE chung prefix /stream

export interface OCRResult {
  status: 'success' | 'error' | 'queued';
  image_id?: string;
  ocr_text?: string;  // Text extracted by OCR
  markdown?: string;
  confidence?: number;
  processing_time_ms?: number;
  output_files?: {
    json?: string;
    markdown?: string;
  };
  layout_detected?: boolean;
  error?: string;
  
  // Queue-related fields
  request_id?: string;
  queue_position?: number;
  estimated_wait_time?: number;
  message?: string;
  error_code?: string;
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
    // Validate file
    if (!file) {
      console.error('OCR Service: No file provided');
      throw new Error('No file provided');
    }

    if (!(file instanceof File)) {
      console.error('OCR Service: Invalid file type', typeof file, file);
      throw new Error('Invalid file type');
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${this.baseUrl}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('OCR Service: Error response', errorData);
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
   * Lang nghe SSE trang thai request. Tra ve ham close.
   */
  subscribeRequestStatus(
    requestId: string,
    onMessage: (event: MessageEvent) => void,
    onError?: (event: Event) => void
  ): () => void {
    const source = new EventSource(`${SSE_BASE_URL}/stream/${requestId}`);
    source.onmessage = onMessage;
    source.onerror = (e) => {
      onError?.(e);
      source.close();
    };
    return () => source.close();
  }

  /**
   * Cho den khi request queued hoan tat bang SSE.
   */
  async waitForQueuedResult(
    requestId: string,
    onUpdate?: (info: { statusText?: string; progress?: number; tip?: string }) => void
  ): Promise<OCRResult> {
    return new Promise((resolve, reject) => {
      const source = new EventSource(`${SSE_BASE_URL}/stream/${requestId}`);

      const cleanup = () => source.close();

      const parsePayload = (event: MessageEvent) => {
        try {
          const payload = JSON.parse(event.data);
          const result = payload?.result ?? payload;
          return result as OCRResult;
        } catch (err) {
          reject(err);
          return null;
        }
      };

      source.addEventListener('update', (event) => {
        try {
          const payload = JSON.parse((event as MessageEvent).data);

          // Priority 1: Detailed progress info from OCR processing
          if (payload?.progress_info && onUpdate) {
            const { message, progress, current_page, total_pages } = payload.progress_info;

            let statusMessage = message || 'Đang xử lý...';

            // Add page info for PDF processing
            if (current_page && total_pages) {
              statusMessage = `${message} (${current_page}/${total_pages})`;
            }

            onUpdate({
              statusText: statusMessage,
              progress: progress || undefined,
            });
          }
          // Priority 2: Queue info (fallback)
          else if (payload?.queue && onUpdate) {
            const { queue_size, active_requests } = payload.queue;
            onUpdate({
              statusText: `Hàng chờ: ${queue_size} | Đang xử lý: ${active_requests}`,
            });
          }
        } catch (err) {
          console.error('SSE update parse error', err);
        }
      });

      source.addEventListener('tip', (event) => {
        if (onUpdate) {
          try {
            const payload = JSON.parse((event as MessageEvent).data);
            if (payload?.message) {
              onUpdate({ tip: payload.message });
            }
          } catch {
            // ignore
          }
        }
      });

      source.addEventListener('completed', (event) => {
        cleanup();
        const parsed = parsePayload(event as MessageEvent);
        if (parsed) resolve(parsed);
      });

      source.addEventListener('error', (event) => {
        cleanup();
        const msgEvent = event as MessageEvent;
        if (msgEvent.data) {
          try {
            const payload = JSON.parse(msgEvent.data);
            if (onUpdate && payload?.message) {
              onUpdate({ statusText: payload.message });
            }
            reject(new Error(payload?.message || 'SSE error'));
          } catch (err) {
            reject(err);
          }
        } else {
          reject(new Error('SSE connection error'));
        }
      });
    });
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
