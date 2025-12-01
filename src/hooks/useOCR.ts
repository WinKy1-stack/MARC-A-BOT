import { useState, useCallback } from 'react';
import { ocrService } from '../services/ocrService';
import type { OCRResult, BatchOCRResult } from '../services/ocrService';
import { toast } from 'react-hot-toast';

interface UseOCRState {
  isProcessing: boolean;
  progress: number;
  results: OCRResult[];
  error: string | null;
  statusText?: string;
  tip?: string;
}

export const useOCR = () => {
  const [state, setState] = useState<UseOCRState>({
    isProcessing: false,
    progress: 0,
    results: [],
    error: null,
    statusText: '',
    tip: '',
  });

  /**
   * Xử lý một file
   */
  const processFile = useCallback(async (file: File): Promise<OCRResult | null> => {
    setState((prev) => ({ ...prev, isProcessing: true, error: null, statusText: '' }));

    try {
      const result = await ocrService.processFile(file);

      // Nếu bị queue -> nghe SSE để cập nhật tiến trình
      if (result.status === 'queued' && result.request_id) {
        setState((prev) => ({
          ...prev,
          statusText: `Đang chờ xử lý... Vị trí: ${result.queue_position}`,
        }));
        toast.loading(`Đang chờ xử lý... Vị trí: ${result.queue_position}`, {
          id: result.request_id,
        });

        const finalResult = await ocrService.waitForQueuedResult(result.request_id, (info) => {
          if (info.statusText || info.tip || info.progress !== undefined) {
            setState((prev) => ({
              ...prev,
              statusText: info.statusText ?? prev.statusText,
              tip: info.tip ?? prev.tip,
              progress: info.progress ?? prev.progress,
            }));
          }
        });

        toast.dismiss(result.request_id);

        if (finalResult.status === 'success' || finalResult.status === 'completed') {
          const normalized =
            (finalResult as any).result && (finalResult as any).result.status
              ? ((finalResult as any).result as OCRResult)
              : finalResult;

          toast.success('Xử lý thành công!');
          setState((prev) => ({
            ...prev,
            isProcessing: false,
            statusText: '',
            tip: '',
            results: [...prev.results, normalized],
          }));
          return normalized;
        } else {
          throw new Error((finalResult as any).message || 'OCR failed');
        }
      }

      // Xử lý ngay
      if (result.status === 'success') {
        toast.success('Xử lý thành công!');
        setState((prev) => ({
          ...prev,
          isProcessing: false,
          statusText: '',
          tip: '',
          results: [...prev.results, result],
        }));
        return result;
      } else {
        throw new Error(result.message || 'OCR failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast.error(`Lỗi: ${errorMessage}`);
      setState((prev) => ({
        ...prev,
        isProcessing: false,
        error: errorMessage,
        statusText: '',
        tip: '',
      }));
      return null;
    }
  }, []);

  /**
   * Xử lý batch files
   */
  const processBatch = useCallback(async (files: File[]): Promise<OCRResult[]> => {
    setState((prev) => ({
      ...prev,
      isProcessing: true,
      error: null,
      progress: 0,
      statusText: 'Đang xử lý batch...',
    }));

    try {
      const toastId = toast.loading(`Đang xử lý ${files.length} ảnh...`);

      const batchResult: BatchOCRResult = await ocrService.processBatch(files);

      toast.dismiss(toastId);

      if (batchResult.status === 'success') {
        const successCount = batchResult.results.filter((r) => r.status === 'success').length;

        toast.success(`Xử lý thành công ${successCount}/${batchResult.total_files} ảnh!`, {
          duration: 4000,
        });

        setState((prev) => ({
          ...prev,
          isProcessing: false,
          progress: 100,
          statusText: '',
          tip: '',
          results: batchResult.results,
        }));

        return batchResult.results;
      } else {
        throw new Error('Batch processing failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast.error(`Lỗi xử lý batch: ${errorMessage}`);
      setState((prev) => ({
        ...prev,
        isProcessing: false,
        error: errorMessage,
        statusText: '',
        tip: '',
      }));
      return [];
    }
  }, []);

  /**
   * Check service status
   */
  const checkStatus = useCallback(async () => {
    try {
      const status = await ocrService.getStatus();
      return status;
    } catch (error) {
      console.error('Error checking status:', error);
      return null;
    }
  }, []);

  /**
   * Reset results
   */
  const resetResults = useCallback(() => {
    setState({
      isProcessing: false,
      progress: 0,
      results: [],
      error: null,
      statusText: '',
      tip: '',
    });
  }, []);

  return {
    ...state,
    processFile,
    processBatch,
    checkStatus,
    resetResults,
  };
};
