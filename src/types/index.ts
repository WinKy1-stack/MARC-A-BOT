export interface FilePreviewItem {
  id: string;
  preview: string;
  fileName: string;
  file: File;
  ocrResult?: OCRResult;  // Store OCR result for each file
}

export interface OCRResult {
  status: 'success' | 'error' | 'queued';
  image_id?: string;
  ocr_text?: string;
  markdown?: string;
  confidence?: number;
  processing_time_ms?: number;
  output_files?: {
    json?: string;
    markdown?: string;
  };
  layout_detected?: boolean;
  error?: string;
  request_id?: string;
  queue_position?: number;
  estimated_wait_time?: number;
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

