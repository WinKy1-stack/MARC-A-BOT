import React, { useEffect } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

interface ImagePreviewProps {
  images: Array<{ id: string; preview: string; fileName: string }>;
  currentIndex: number;
  onClose: () => void;
  onNext: () => void;
  onPrevious: () => void;
}

export const ImagePreview: React.FC<ImagePreviewProps> = ({
  images,
  currentIndex,
  onClose,
  onNext,
  onPrevious,
}) => {
  const currentImage = images[currentIndex];

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowLeft') {
        onPrevious();
      } else if (e.key === 'ArrowRight') {
        onNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, onNext, onPrevious]);

  if (!currentImage) return null;

  return (
    <div 
      className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center animate-in fade-in duration-300"
      onClick={onClose}
    >
      <div 
        className="relative max-w-7xl max-h-[90vh] w-full h-full flex items-center justify-center p-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Nút đóng */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-full transition-all duration-200 hover:scale-110"
          aria-label="Đóng"
        >
          <X className="h-6 w-6" />
        </button>

        {/* Nút Previous */}
        {images.length > 1 && (
          <button
            onClick={onPrevious}
            className="absolute left-4 top-1/2 -translate-y-1/2 z-10 p-3 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-full transition-all duration-200 hover:scale-110"
            aria-label="Ảnh trước"
          >
            <ChevronLeft className="h-6 w-6" />
          </button>
        )}

        {/* Ảnh */}
        <div className="relative max-w-full max-h-full flex flex-col items-center">
          <img
            src={currentImage.preview}
            alt={currentImage.fileName}
            className="max-w-full max-h-[85vh] object-contain rounded-lg shadow-2xl"
          />
          <div className="mt-4 text-white text-center">
            <p className="text-sm sm:text-base font-medium">{currentImage.fileName}</p>
            {images.length > 1 && (
              <p className="text-xs sm:text-sm text-gray-300 mt-1">
                {currentIndex + 1} / {images.length}
              </p>
            )}
          </div>
        </div>

        {/* Nút Next */}
        {images.length > 1 && (
          <button
            onClick={onNext}
            className="absolute right-4 top-1/2 -translate-y-1/2 z-10 p-3 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-full transition-all duration-200 hover:scale-110"
            aria-label="Ảnh tiếp theo"
          >
            <ChevronRight className="h-6 w-6" />
          </button>
        )}
      </div>
    </div>
  );
};

