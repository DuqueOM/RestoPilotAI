import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  progress: number;
  className?: string;
  showLabel?: boolean;
}

export function ProgressBar({ progress, className, showLabel = true }: ProgressBarProps) {
  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div className={cn("w-full", className)}>
      <div className="flex justify-between mb-1">
        {showLabel && (
          <span className="text-base font-medium text-blue-700 dark:text-white">Progress</span>
        )}
        <span className="text-sm font-medium text-blue-700 dark:text-white">{Math.round(clampedProgress)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div 
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out" 
          style={{ width: `${clampedProgress}%` }}
        ></div>
      </div>
    </div>
  );
}
