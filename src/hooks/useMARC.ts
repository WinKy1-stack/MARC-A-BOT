import { useState, useCallback } from 'react';
import { MARC_DATA } from '../constants/marc';

export const useMARC = () => {
  const [marcData, setMarcData] = useState<string | null>(null);

  const processImages = useCallback((fileCount: number) => {
    setMarcData(MARC_DATA);
    return fileCount;
  }, []);

  const resetMARC = useCallback(() => {
    setMarcData(null);
  }, []);

  return {
    marcData,
    processImages,
    resetMARC,
  };
};

