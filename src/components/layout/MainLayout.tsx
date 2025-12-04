import React from 'react';
import { Header } from '../Header';
import { Dropzone } from '../Dropzone';
import { MARCViewer } from '../MARCViewer';
import { OCRTextViewer } from '../OCRTextViewer';
import type { FilePreviewItem, OCRResult } from '../../types';

interface MainLayoutProps {
  files: FilePreviewItem[];
  marcData: string | null;
  ocrResults: Map<string, OCRResult>;
  isProcessing?: boolean;
  statusText?: string;
  tip?: string;
  onDrop: (files: File[]) => void;
  onRemove: (id: string) => void;
  onProcess?: () => void;
  onReset?: () => void;
  onImageClick?: (id: string) => void;
  onClearAll?: () => void;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  files,
  marcData,
  ocrResults,
  isProcessing = false,
  statusText,
  tip,
  onDrop,
  onRemove,
  onProcess,
  onReset,
  onImageClick,
  onClearAll,
}) => {
  // Get the first OCR result to display
  const firstOcrResult = files.length > 0 && ocrResults.size > 0 
    ? ocrResults.get(files[0].id)
    : null;

  const hasOcrResults = ocrResults.size > 0;

  return (
    <>
      <Header onClearAll={files.length > 0 ? onClearAll : undefined} />

      <div className="flex-1 overflow-hidden">
        {hasOcrResults ? (
          <div className="h-full flex flex-col sm:flex-row gap-4 p-4 animate-in fade-in duration-500">
            <div className="w-full sm:w-1/2 flex-shrink-0 overflow-y-auto animate-in slide-in-from-left duration-500">
              <Dropzone
                files={files}
                onDrop={onDrop}
                onRemove={onRemove}
                onProcess={onProcess}
                onReset={onReset}
                disabled={true}
                hasMarcData={hasOcrResults}
                onImageClick={onImageClick}
                isProcessing={isProcessing}
                statusText={statusText}
                tip={tip}
              />
            </div>
            <div className="w-full sm:w-1/2 flex-shrink-0 h-full animate-in slide-in-from-right fade-in duration-500 delay-150">
              {marcData ? (
                <MARCViewer marcData={marcData} />
              ) : firstOcrResult ? (
                <OCRTextViewer ocrResult={firstOcrResult} />
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500">
                  <p>No OCR results available</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto animate-in fade-in duration-300">
            <Dropzone
              files={files}
              onDrop={onDrop}
              onRemove={onRemove}
              onProcess={onProcess}
              disabled={false}
              onImageClick={onImageClick}
              isProcessing={isProcessing}
              statusText={statusText}
              tip={tip}
            />
          </div>
        )}
      </div>
    </>
  );
};

