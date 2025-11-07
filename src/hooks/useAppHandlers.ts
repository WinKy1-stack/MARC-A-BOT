import { useCallback } from 'react';
import { toast } from 'react-hot-toast';
import type { FilePreviewItem } from '../types';

interface UseAppHandlersProps {
  files: FilePreviewItem[];
  addFiles: (files: File[]) => void;
  removeFile: (id: string) => void;
  clearAll: () => void;
  processImages: (fileCount: number) => void;
  resetMARC: () => void;
}

export const useAppHandlers = ({
  files,
  addFiles,
  removeFile,
  clearAll,
  processImages,
  resetMARC,
}: UseAppHandlersProps) => {
  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        addFiles(acceptedFiles);
        toast.success(
          `Đã tải thành công ${acceptedFiles.length} ${acceptedFiles.length === 1 ? 'ảnh' : 'ảnh'}`
        );
      }
    },
    [addFiles]
  );

  const handleRemoveImage = useCallback(
    (id: string) => {
      const fileToRemove = files.find((f) => f.id === id);
      removeFile(id);
      if (fileToRemove) {
        toast.success(`Đã xóa ${fileToRemove.fileName}`, {
          icon: '🗑️',
        });
      }
    },
    [removeFile, files]
  );

  const handleClearAll = useCallback(() => {
    if (files.length > 0) {
      clearAll();
      resetMARC();
      toast.success(
        `Đã xóa tất cả ${files.length} ${files.length === 1 ? 'ảnh' : 'ảnh'}`,
        {
          icon: '🗑️',
        }
      );
    }
  }, [clearAll, resetMARC, files]);

  const handleProcess = useCallback(() => {
    const fileCount = processImages(files.length);
    toast.success(`Đã xử lý thành công ${fileCount} ${fileCount === 1 ? 'ảnh' : 'ảnh'}!`, {
      duration: 4000,
    });
  }, [processImages, files.length]);

  const handleReset = useCallback(() => {
    resetMARC();
    toast.success('Đã reset, có thể xử lý lại!', {
      duration: 3000,
    });
  }, [resetMARC]);

  return {
    handleDrop,
    handleRemoveImage,
    handleClearAll,
    handleProcess,
    handleReset,
  };
};

