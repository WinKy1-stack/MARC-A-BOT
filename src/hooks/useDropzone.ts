import { useRef } from 'react';
import type { DropzoneRootProps, DropzoneInputProps } from '../types';

interface UseDropzoneOptions {
  onDrop: (files: File[]) => void;
  accept: Record<string, string[]>;
  multiple?: boolean;
  disabled?: boolean;
}

export const useDropzone = ({
  onDrop,
  accept,
  multiple = false,
  disabled = false,
}: UseDropzoneOptions) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const getRootProps = (): DropzoneRootProps => ({
    onClick: () => {
      if (!disabled) {
        inputRef.current?.click();
      }
    },
    onDrop: (e) => {
      if (disabled) return;
      e.preventDefault();
      const files = Array.from(e.dataTransfer?.files || []);
      if (files.length > 0) {
        onDrop(files as File[]);
      }
    },
    onDragOver: (e) => {
      if (!disabled) {
        e.preventDefault();
      }
    },
    onDragEnter: () => {
      if (!disabled) {
        console.log('Drag Enter');
      }
    },
    onDragLeave: () => {
      if (!disabled) {
        console.log('Drag Leave');
      }
    },
    style: {
      cursor: disabled ? 'not-allowed' : 'pointer',
    },
  });

  const getInputProps = (): DropzoneInputProps => ({
    type: 'file',
    accept: Object.keys(accept).join(','),
    multiple: multiple,
    onChange: (e) => {
      const files = Array.from(e.target.files || []);
      if (files.length > 0) {
        onDrop(files as File[]);
        e.target.value = '';
      }
    },
  });

  return {
    getRootProps,
    getInputProps,
    inputRef,
    isDragActive: false,
  };
};

