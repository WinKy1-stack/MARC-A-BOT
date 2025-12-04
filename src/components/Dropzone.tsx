import React from 'react';
import { useDropzone } from '../hooks/useDropzone';
import { FILE_ACCEPT_CONFIG } from '../constants/fileConfig';
import { ImageGrid } from './ui/ImageGrid';
import { DropzoneEmpty } from './ui/DropzoneEmpty';
import { ProcessButton } from './ui/ProcessButton';
import type { FilePreviewItem } from '../types';

interface DropzoneProps {
  files: FilePreviewItem[];
  onDrop: (files: File[]) => void;
  onRemove: (id: string) => void;
  onProcess?: () => void;
  onReset?: () => void;
  disabled?: boolean;
  hasMarcData?: boolean;
  onImageClick?: (id: string) => void;
  isProcessing?: boolean;
  statusText?: string;
  tip?: string;
}

export const Dropzone: React.FC<DropzoneProps> = ({
  files,
  onDrop,
  onRemove,
  onProcess,
  onReset,
  disabled = false,
  hasMarcData = false,
  onImageClick,
  isProcessing = false,
  statusText,
  tip,
}) => {
  const { getRootProps, getInputProps, inputRef, isDragActive } = useDropzone({
    onDrop,
    accept: FILE_ACCEPT_CONFIG,
    multiple: true,
    disabled,
  });

  const handleProcess = async () => {
    if (!onProcess || isProcessing) return;
    onProcess();
  };

  const handleButtonClick = () => {
    if (hasMarcData && onReset) {
      onReset();
    } else {
      handleProcess();
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-2 sm:p-4 md:p-8">
      <div
        {...getRootProps()}
        className={`
          w-full max-w-2xl transition-all duration-300 ease-in-out
          flex flex-col items-center justify-center text-center relative
          rounded-lg sm:rounded-xl p-4 sm:p-6 md:p-8 lg:p-12 mb-4
          ${
            disabled
              ? 'bg-gray-100 border-2 sm:border-4 border-gray-200 border-dashed cursor-not-allowed opacity-60'
              : isDragActive
              ? 'bg-indigo-50 border-2 sm:border-4 border-indigo-400 border-solid'
              : 'bg-white border-2 sm:border-4 border-gray-300 border-dashed hover:border-indigo-400 hover:bg-indigo-50 shadow-md sm:shadow-lg'
          }
        `}
      >
        <input {...getInputProps()} ref={inputRef} className="hidden" />

        {files.length > 0 ? (
          <div className="w-full">
            <ImageGrid
              files={files}
              disabled={disabled}
              onRemove={onRemove}
              onImageClick={onImageClick}
            />
          </div>
        ) : (
          <DropzoneEmpty isDragActive={isDragActive} />
        )}
      </div>

      {files.length > 0 && (onProcess || onReset) && (
        <div className="flex flex-col items-center gap-2">
          <ProcessButton
            isProcessing={isProcessing}
            hasMarcData={hasMarcData}
            onClick={handleButtonClick}
          />
          {(statusText || tip) && (
            <div className="text-xs text-gray-600 text-center">
              {statusText && <div>{statusText}</div>}
              {tip && <div className="text-gray-500">💡 {tip}</div>}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
