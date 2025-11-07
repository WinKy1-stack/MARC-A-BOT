import React from 'react';
import { Header } from '../Header';
import { Dropzone } from '../Dropzone';
import { MARCViewer } from '../MARCViewer';
import type { FilePreviewItem } from '../../types';

interface MainLayoutProps {
  files: FilePreviewItem[];
  marcData: string | null;
  onDrop: (files: File[]) => void;
  onRemove: (id: string) => void;
  onProcess?: () => void;
  onReset?: () => void;
  onImageClick?: (id: string) => void;
  onClearAll?: () => void;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  files,
  marcData,
  onDrop,
  onRemove,
  onProcess,
  onReset,
  onImageClick,
  onClearAll,
}) => {
  return (
    <>
      <Header onClearAll={files.length > 0 ? onClearAll : undefined} />

      <div className="flex-1 overflow-hidden">
        {marcData ? (
          <div className="h-full flex flex-col sm:flex-row gap-4 p-4 animate-in fade-in duration-500">
            <div className="w-full sm:w-1/2 flex-shrink-0 overflow-y-auto animate-in slide-in-from-left duration-500">
              <Dropzone
                files={files}
                onDrop={onDrop}
                onRemove={onRemove}
                onProcess={onProcess}
                onReset={onReset}
                disabled={true}
                hasMarcData={true}
                onImageClick={onImageClick}
              />
            </div>
            <div className="w-full sm:w-1/2 flex-shrink-0 h-full animate-in slide-in-from-right fade-in duration-500 delay-150">
              <MARCViewer marcData={marcData} />
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto animate-in fade-in duration-300">
            <Dropzone
              files={files}
              onDrop={onDrop}
              onRemove={onRemove}
              onProcess={onProcess}
              disabled={false}
              onImageClick={onImageClick}
            />
          </div>
        )}
      </div>
    </>
  );
};

