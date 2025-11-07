import React from 'react';
import { Trash2 } from 'lucide-react';

interface HeaderProps {
  onClearAll?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onClearAll }) => {
  return (
    <div className="flex-shrink-0 bg-white shadow-sm px-4 py-3 sm:px-6 sm:py-4">
      <div className="relative">
        <div className="flex items-center justify-center">
          <div className="flex-1 text-center">
            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-800">
              <span className="text-indigo-600">Tải Lên Ảnh</span> Bằng Kéo Thả
            </h1>
            <p className="text-gray-500 text-xs sm:text-sm md:text-base mt-1 sm:mt-2 px-2">
              Kéo thả nhiều file ảnh (JPG, PNG, GIF, WEBP) vào khung bên dưới, hoặc bấm để chọn file
            </p>
          </div>
        </div>
        {onClearAll && (
          <button
            onClick={onClearAll}
            className="absolute top-0 right-0 px-3 py-2 sm:px-4 sm:py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg shadow-md transition-colors flex items-center gap-2 text-xs sm:text-sm font-medium active:scale-95 z-50"
            aria-label="Xóa tất cả ảnh"
          >
            <Trash2 className="h-4 w-4 sm:h-5 sm:w-5" />
            <span className="hidden sm:inline">Xóa tất cả</span>
          </button>
        )}
      </div>
    </div>
  );
};

