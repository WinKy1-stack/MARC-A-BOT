import React, { useState } from 'react';
import { Copy, Check, FileText, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import type { OCRResult } from '../types';

interface OCRTextViewerProps {
  ocrResult: OCRResult;
}

export const OCRTextViewer: React.FC<OCRTextViewerProps> = ({ ocrResult }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!ocrResult.ocr_text) return;
    
    try {
      await navigator.clipboard.writeText(ocrResult.ocr_text);
      setCopied(true);
      toast.success('Đã sao chép text!');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('Không thể sao chép');
    }
  };

  // Show error state
  if (ocrResult.status === 'error') {
    return (
      <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-lg border border-red-200">
        <div className="flex items-center justify-between px-4 py-3 border-b border-red-200 bg-red-50 rounded-t-lg">
          <h2 className="text-lg font-semibold text-red-800 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            OCR Error
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <div className="text-sm text-red-600 bg-red-50 p-4 rounded border border-red-200">
            {ocrResult.error || 'Unknown error occurred'}
          </div>
        </div>
      </div>
    );
  }

  // Show empty state
  if (!ocrResult.ocr_text || ocrResult.ocr_text.trim() === '') {
    return (
      <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-lg border border-gray-200">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-lg">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            OCR Text
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No text detected in image</p>
          </div>
        </div>
      </div>
    );
  }

  // Show OCR text
  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-lg border border-gray-200 transform transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-indigo-600" />
          <h2 className="text-lg sm:text-xl font-semibold text-gray-800">
            OCR Text
          </h2>
          {ocrResult.confidence && (
            <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-medium">
              {(ocrResult.confidence * 100).toFixed(1)}% confidence
            </span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all duration-200 flex items-center gap-2 text-sm font-medium active:scale-95 hover:scale-105 hover:shadow-md"
          aria-label="Sao chép OCR text"
        >
          {copied ? (
            <>
              <Check className="h-4 w-4 animate-in zoom-in duration-200" />
              <span className="hidden sm:inline">Đã sao chép</span>
            </>
          ) : (
            <>
              <Copy className="h-4 w-4" />
              <span className="hidden sm:inline">Sao chép</span>
            </>
          )}
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
          <pre className="text-sm font-mono text-gray-700 whitespace-pre-wrap break-words">
            {ocrResult.ocr_text}
          </pre>
        </div>
        
        {ocrResult.processing_time_ms && (
          <div className="mt-3 text-xs text-gray-500 text-right">
            Processing time: {ocrResult.processing_time_ms}ms
          </div>
        )}
      </div>
    </div>
  );
};
