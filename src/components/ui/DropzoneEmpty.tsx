import React from 'react';
import { UploadCloud, Image as ImageIcon } from 'lucide-react';

interface DropzoneEmptyProps {
  isDragActive: boolean;
}

export const DropzoneEmpty: React.FC<DropzoneEmptyProps> = ({ isDragActive }) => {
  return (
    <div className="text-gray-500 px-2 sm:px-4">
      <div className="flex justify-center mb-4 sm:mb-6">
        {isDragActive ? (
          <UploadCloud className="h-16 w-16 sm:h-20 sm:w-20 md:h-24 md:w-24 text-indigo-400" />
        ) : (
          <ImageIcon className="h-16 w-16 sm:h-20 sm:w-20 md:h-24 md:w-24 text-indigo-400" />
        )}
      </div>
      {isDragActive ? (
        <p className="text-base sm:text-xl md:text-2xl font-semibold text-indigo-700 px-2">
          Thả file ảnh vào đây...
        </p>
      ) : (
        <>
          <p className="text-sm sm:text-base md:text-lg lg:text-xl font-medium mb-1 sm:mb-2 px-2">
            Kéo thả ảnh vào đây, hoặc{' '}
            <span className="text-indigo-600 font-bold underline">bấm để chọn file</span>
          </p>
          <p className="text-xs sm:text-sm md:text-base text-gray-400">(Có thể chọn nhiều file)</p>
        </>
      )}
    </div>
  );
};

