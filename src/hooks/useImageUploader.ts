import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';

export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

export const useImageUploader = () => {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadStatus('uploading');
    setProgress(0);

    // Simulate file upload
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 100);

    setTimeout(() => {
      clearInterval(interval);
      setProgress(100);
      setUploadStatus('success');
      toast.success('File uploaded successfully!');
    }, 1000);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': [],
      'image/png': [],
      'image/webp': [],
    },
    disabled: uploadStatus === 'uploading',
  });

  return {
    uploadStatus,
    progress,
    getRootProps,
    getInputProps,
    isDragActive,
  };
};