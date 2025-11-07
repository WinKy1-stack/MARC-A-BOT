export interface FilePreviewItem {
  id: string;
  preview: string;
  fileName: string;
  file: File;
}

export interface DropzoneRootProps {
  onClick: (event: React.MouseEvent<HTMLElement>) => void;
  onDrop: (event: React.DragEvent<HTMLElement>) => void;
  onDragOver: (event: React.DragEvent<HTMLElement>) => void;
  onDragEnter: (event: React.DragEvent<HTMLElement>) => void;
  onDragLeave: (event: React.DragEvent<HTMLElement>) => void;
  style: React.CSSProperties;
}

export interface DropzoneInputProps {
  type: 'file';
  accept: string;
  multiple: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

