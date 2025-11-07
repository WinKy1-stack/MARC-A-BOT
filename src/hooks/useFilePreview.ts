import { useState, useEffect, useCallback } from 'react';
import type { FilePreviewItem } from '../types';

export const useFilePreview = () => {
  const [files, setFiles] = useState<FilePreviewItem[]>([]);

  const addFiles = useCallback((newFiles: File[]) => {
    const newItems: FilePreviewItem[] = newFiles.map((file) => ({
      id: `${Date.now()}-${Math.random()}`,
      preview: URL.createObjectURL(file),
      fileName: file.name,
      file,
    }));

    setFiles((prev) => [...prev, ...newItems]);
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => {
      const fileToRemove = prev.find((f) => f.id === id);
      if (fileToRemove) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return prev.filter((f) => f.id !== id);
    });
  }, []);

  const clearAll = useCallback(() => {
    files.forEach((file) => {
      URL.revokeObjectURL(file.preview);
    });
    setFiles([]);
  }, [files]);

  // Cleanup effect: Xóa URL object khi component unmount
  useEffect(() => {
    return () => {
      files.forEach((file) => {
        URL.revokeObjectURL(file.preview);
      });
    };
  }, [files]);

  return {
    files,
    addFiles,
    removeFile,
    clearAll,
  };
};

