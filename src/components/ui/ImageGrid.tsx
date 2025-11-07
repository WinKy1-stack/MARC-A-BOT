import React from 'react';
import { X } from 'lucide-react';
import type { FilePreviewItem } from '../../types';

interface ImageGridProps {
  files: FilePreviewItem[];
  disabled?: boolean;
  onRemove?: (id: string) => void;
  onImageClick?: (id: string) => void;
}

export const ImageGrid: React.FC<ImageGridProps> = ({
  files,
  disabled = false,
  onRemove,
  onImageClick,
}) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 sm:gap-3 md:gap-4 max-h-[calc(100vh-200px)] sm:max-h-[60vh] overflow-y-auto p-1 sm:p-2">
      {files.map((file, index) => (
        <div
          key={file.id}
          className="relative group animate-in fade-in zoom-in duration-300"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <div
            className={`relative aspect-square rounded-md sm:rounded-lg overflow-hidden shadow-sm sm:shadow-md bg-gray-100 transform transition-all duration-300 ${
              onImageClick ? 'group-hover:scale-105 group-hover:shadow-lg cursor-pointer' : ''
            }`}
            onClick={(e) => {
              e.stopPropagation();
              onImageClick?.(file.id);
            }}
          >
            <img
              src={file.preview}
              alt={file.fileName}
              className={`w-full h-full object-cover transition-transform duration-300 ${
                onImageClick ? 'group-hover:scale-110' : ''
              }`}
            />
            {!disabled && onRemove && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onRemove(file.id);
                }}
                className="absolute top-1 right-1 p-1 sm:p-1.5 bg-red-500 text-white rounded-full shadow-lg opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-all duration-200 hover:bg-red-600 active:scale-95 hover:scale-110"
                aria-label="Xóa ảnh"
              >
                <X className="h-3 w-3 sm:h-4 sm:w-4" />
              </button>
            )}
          </div>
          <p
            className="text-[10px] sm:text-xs text-gray-600 mt-0.5 sm:mt-1 truncate px-0.5 transition-colors duration-200 group-hover:text-gray-800"
            title={file.fileName}
          >
            {file.fileName}
          </p>
        </div>
      ))}
    </div>
  );
};

