import { useState, useCallback } from 'react';
import type { FilePreviewItem } from '../types';

export const useImagePreview = () => {
  const [previewIndex, setPreviewIndex] = useState<number | null>(null);

  const openPreview = useCallback((id: string, files: FilePreviewItem[]) => {
    const index = files.findIndex((f) => f.id === id);
    if (index !== -1) {
      setPreviewIndex(index);
    }
  }, []);

  const closePreview = useCallback(() => {
    setPreviewIndex(null);
  }, []);

  const nextImage = useCallback((filesLength: number) => {
    setPreviewIndex((prev) => {
      if (prev !== null && prev < filesLength - 1) {
        return prev + 1;
      }
      return prev;
    });
  }, []);

  const previousImage = useCallback(() => {
    setPreviewIndex((prev) => {
      if (prev !== null && prev > 0) {
        return prev - 1;
      }
      return prev;
    });
  }, []);

  return {
    previewIndex,
    openPreview,
    closePreview,
    nextImage,
    previousImage,
  };
};

