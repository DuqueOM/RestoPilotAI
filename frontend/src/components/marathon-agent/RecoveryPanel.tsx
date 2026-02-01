import React from 'react';
import { RecoveryOption } from '@/types/marathon-agent';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCcw, History } from 'lucide-react';
import { formatCheckpointTime } from '@/lib/utils/checkpoint-manager';
import { cn } from '@/lib/utils';

interface RecoveryPanelProps {
  options: RecoveryOption[];
  onRecover: (checkpointId: string) => void;
  isRecovering?: boolean;
  className?: string;
}

export function RecoveryPanel({ options, onRecover, isRecovering, className }: RecoveryPanelProps) {
  if (!options || options.length === 0) return null;

  return (
    <div className={cn("bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900 rounded-lg p-4", className)}>
      <div className="flex items-start space-x-3 mb-4">
        <div className="bg-red-100 dark:bg-red-800 p-2 rounded-full mt-1">
          <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-300" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-red-900 dark:text-red-200">Task Execution Failed</h3>
          <p className="text-sm text-red-700 dark:text-red-300 mt-1">
            The process encountered an error. You can recover from a previous stable checkpoint.
          </p>
        </div>
      </div>

      <div className="space-y-3 pl-11">
        <h4 className="text-xs font-semibold uppercase text-red-800 dark:text-red-400 flex items-center">
          <History className="w-3 h-3 mr-1" />
          Available Recovery Points
        </h4>
        <div className="grid gap-2">
          {options.map((option) => (
            <div 
              key={option.checkpoint_id}
              className="bg-white dark:bg-gray-800 p-3 rounded border border-red-100 dark:border-red-900/50 flex items-center justify-between shadow-sm"
            >
              <div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {option.description}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {formatCheckpointTime(option.timestamp)}
                </div>
              </div>
              <Button 
                size="sm" 
                onClick={() => onRecover(option.checkpoint_id)}
                disabled={isRecovering}
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                {isRecovering ? (
                  <RefreshCcw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <RefreshCcw className="w-4 h-4 mr-2" />
                )}
                Recover
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
