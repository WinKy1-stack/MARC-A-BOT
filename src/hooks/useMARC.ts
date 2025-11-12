import { useState, useCallback } from 'react';
import { useOCR } from './useOCR';
import type { OCRResult } from '../services/ocrService';

export const useMARC = () => {
  const [marcData, setMarcData] = useState<string | null>(null);
  const [ocrResults, setOcrResults] = useState<OCRResult[]>([]);
  const { processBatch, isProcessing, results } = useOCR();

  const processImages = useCallback(
    async (files: File[]) => {
      if (files.length === 0) return 0;

      try {
        const results = await processBatch(files);
        setOcrResults(results);

        // Convert OCR results to MARC format
        const marcText = convertToMARC(results);
        setMarcData(marcText);

        return results.filter((r) => r.status === 'success').length;
      } catch (error) {
        console.error('Error processing images:', error);
        return 0;
      }
    },
    [processBatch]
  );

  const resetMARC = useCallback(() => {
    setMarcData(null);
    setOcrResults([]);
  }, []);

  return {
    marcData,
    ocrResults,
    processImages,
    resetMARC,
    isProcessing,
    results,
  };
};

/**
 * Convert OCR results to MARC21 format
 */
function convertToMARC(results: OCRResult[]): string {
  const marcLines: string[] = [];

  marcLines.push('=LDR  00000nam a2200000 a 4500');
  marcLines.push('');

  results.forEach((result, index) => {
    if (result.status === 'success' && result.sections) {
      const { sections } = result;

      // Control fields
      marcLines.push(`=008  ${new Date().toISOString().slice(0, 10).replace(/-/g, '')}s${sections.year || '    '}    vn a          000 0 vie d`);
      marcLines.push('');

      // ISBN
      if (sections.isbn) {
        marcLines.push(`=020  \\\\$a${sections.isbn}`);
      }

      // Title
      if (sections.title) {
        marcLines.push(`=245  00$a${sections.title}`);
      }

      // Author
      if (sections.author) {
        marcLines.push(`=100  1\\$a${sections.author}`);
      }

      // Publisher
      if (sections.publisher) {
        marcLines.push(`=260  \\\\$a[Place]$b${sections.publisher}$c${sections.year || ''}`);
      }

      // Note về OCR
      marcLines.push(`=500  \\\\$aExtracted via OCR (confidence: ${((result.confidence || 0) * 100).toFixed(1)}%)`);
      
      if (index < results.length - 1) {
        marcLines.push('');
        marcLines.push('---');
        marcLines.push('');
      }
    }
  });

  return marcLines.join('\n');
}


