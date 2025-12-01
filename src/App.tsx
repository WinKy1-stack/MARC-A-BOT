import React from 'react';
import { useFilePreview } from './hooks/useFilePreview';
import { useMARC } from './hooks/useMARC';
import { useImagePreview } from './hooks/useImagePreview';
import { useAppHandlers } from './hooks/useAppHandlers';
import { ToastProvider } from './components/ToastProvider';
import { MainLayout } from './components/layout/MainLayout';
import { ImagePreview } from './components/ImagePreview';

const App: React.FC = () => {
  const { files, addFiles, removeFile, clearAll } = useFilePreview();
  const { marcData, ocrResults, processImages, resetMARC } = useMARC();
  const { previewIndex, openPreview, closePreview, nextImage, previousImage } =
    useImagePreview();

  const {
    handleDrop,
    handleRemoveImage,
    handleClearAll,
    handleProcess,
    handleReset,
  } = useAppHandlers({
    files,
    addFiles,
    removeFile,
    clearAll,
    processImages,
    resetMARC,
  });

  const handleImageClick = (id: string) => {
    openPreview(id, files);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-100 font-sans overflow-hidden">
      <ToastProvider />
      <MainLayout
        files={files}
        marcData={marcData}
        ocrResults={ocrResults}
        onDrop={handleDrop}
        onRemove={handleRemoveImage}
        onProcess={handleProcess}
        onReset={handleReset}
        onImageClick={handleImageClick}
        onClearAll={handleClearAll}
      />

      {previewIndex !== null && (
        <ImagePreview
          images={files}
          currentIndex={previewIndex}
          onClose={closePreview}
          onNext={() => nextImage(files.length)}
          onPrevious={previousImage}
        />
      )}
    </div>
  );
};

export default App;
