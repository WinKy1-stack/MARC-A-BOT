import { useState, useCallback } from 'react';
import { useOCR } from './useOCR';
import type { OCRResult } from '../services/ocrService';
import type { FilePreviewItem } from '../types';

export const useMARC = () => {
  const [marcData, setMarcData] = useState<string | null>(null);
  const [ocrResults, setOcrResults] = useState<Map<string, OCRResult>>(new Map());
  const { processFile, isProcessing } = useOCR();

  const processImages = useCallback(
    async (files: FilePreviewItem[]) => {
      if (files.length === 0) return 0;

      try {
        let successCount = 0;
        const newResults = new Map<string, OCRResult>();

        // Process each file
        for (const fileItem of files) {
          const result = await processFile(fileItem.file);
          if (result && result.status === 'success') {
            newResults.set(fileItem.id, result);
            successCount++;
          } else if (result && result.status === 'error') {
            newResults.set(fileItem.id, result);
          }
        }

        setOcrResults(newResults);
        return successCount;
      } catch (error) {
        console.error('Error processing images:', error);
        return 0;
      }
    },
    [processFile]
  );

  const resetMARC = useCallback(() => {
    setMarcData(null);
    setOcrResults(new Map());
  }, []);

  return {
    marcData,
    ocrResults,
    processImages,
    resetMARC,
    isProcessing,
  };
};

