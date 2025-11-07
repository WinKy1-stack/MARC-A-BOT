import React from 'react';
import { Play, Loader2 } from 'lucide-react';

interface ProcessButtonProps {
  isProcessing: boolean;
  hasMarcData: boolean;
  onClick: () => void;
}

export const ProcessButton: React.FC<ProcessButtonProps> = ({
  isProcessing,
  hasMarcData,
  onClick,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={isProcessing}
      className="px-6 py-3 sm:px-8 sm:py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 disabled:cursor-not-allowed text-white rounded-lg shadow-lg transition-all duration-300 flex items-center gap-2 text-sm sm:text-base font-semibold active:scale-95 hover:scale-105 hover:shadow-xl animate-in fade-in slide-in-from-bottom duration-500"
    >
      {isProcessing ? (
        <>
          <Loader2 className="h-5 w-5 sm:h-6 sm:w-6 animate-spin" />
          <span>Đang xử lý...</span>
        </>
      ) : hasMarcData ? (
        <>
          <Play className="h-5 w-5 sm:h-6 sm:w-6 transition-transform duration-200" />
          <span>Tạo lại</span>
        </>
      ) : (
        <>
          <Play className="h-5 w-5 sm:h-6 sm:w-6 transition-transform duration-200 group-hover:translate-x-1" />
          <span>Bắt đầu xử lý</span>
        </>
      )}
    </button>
  );
};

