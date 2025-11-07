import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface MARCViewerProps {
  marcData: string;
}

export const MARCViewer: React.FC<MARCViewerProps> = ({ marcData }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(marcData);
      setCopied(true);
      toast.success('Đã sao chép MARC record!');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('Không thể sao chép');
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-lg border border-gray-200 transform transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-800 animate-in fade-in slide-in-from-top duration-300">MARC Record</h2>
        <button
          onClick={handleCopy}
          className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all duration-200 flex items-center gap-2 text-sm font-medium active:scale-95 hover:scale-105 hover:shadow-md"
          aria-label="Sao chép MARC record"
        >
          {copied ? (
            <>
              <Check className="h-4 w-4 animate-in zoom-in duration-200" />
              <span className="hidden sm:inline">Đã sao chép</span>
            </>
          ) : (
            <>
              <Copy className="h-4 w-4 transition-transform duration-200 group-hover:rotate-12" />
              <span className="hidden sm:inline">Sao chép</span>
            </>
          )}
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <pre className="text-xs sm:text-sm font-mono text-gray-700 whitespace-pre-wrap break-words bg-gray-50 p-4 rounded border border-gray-200 animate-in fade-in duration-500 delay-300">
          {marcData}
        </pre>
      </div>
    </div>
  );
};

