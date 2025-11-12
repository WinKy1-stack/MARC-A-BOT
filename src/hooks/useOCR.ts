import { useState, useCallback } from 'react';
import { ocrService } from '../services/ocrService';
import type { OCRResult, BatchOCRResult } from '../services/ocrService';
import { toast } from 'react-hot-toast';

interface UseOCRState {
  isProcessing: boolean;
  progress: number;
  results: OCRResult[];
  error: string | null;
}

export const useOCR = () => {
  const [state, setState] = useState<UseOCRState>({
    isProcessing: false,
    progress: 0,
    results: [],
    error: null,
  });

  /**
   * Xử lý một file
   */
  const processFile = useCallback(async (file: File): Promise<OCRResult | null> => {
    setState((prev) => ({ ...prev, isProcessing: true, error: null }));

    try {
      const result = await ocrService.processFile(file);

      // Nếu bị queue
      if (result.status === 'queued' && result.request_id) {
        toast.loading(
          `Đang chờ xử lý... Vị trí: ${result.queue_position}`,
          { id: result.request_id }
        );

        // Poll status
        const finalResult = await ocrService.pollRequestStatus(
          result.request_id,
          () => {
            toast.loading('Đang xử lý...', { id: result.request_id });
          }
        );

        toast.dismiss(result.request_id);

        if (finalResult.status === 'success') {
          toast.success('Xử lý thành công!');
          setState((prev) => ({
            ...prev,
            isProcessing: false,
            results: [...prev.results, finalResult],
          }));
          return finalResult;
        } else {
          throw new Error(finalResult.message || 'OCR failed');
        }
      }

      // Xử lý ngay
      if (result.status === 'success') {
        toast.success('Xử lý thành công!');
        setState((prev) => ({
          ...prev,
          isProcessing: false,
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
    }));

    try {
      const toastId = toast.loading(`Đang xử lý ${files.length} ảnh...`);

      const batchResult: BatchOCRResult = await ocrService.processBatch(files);

      toast.dismiss(toastId);

      if (batchResult.status === 'success') {
        const successCount = batchResult.results.filter(
          (r) => r.status === 'success'
        ).length;

        toast.success(
          `Xử lý thành công ${successCount}/${batchResult.total_files} ảnh!`,
          { duration: 4000 }
        );

        setState((prev) => ({
          ...prev,
          isProcessing: false,
          progress: 100,
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
