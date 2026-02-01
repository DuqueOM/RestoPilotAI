import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { formatCheckpointTime } from '@/lib/utils/checkpoint-manager';
import { Checkpoint } from '@/types/marathon-agent';
import { ChevronDown, ChevronRight, Database } from 'lucide-react';
import { useState } from 'react';

interface CheckpointViewerProps {
  checkpoints: Checkpoint[];
  className?: string;
  onRecover?: (checkpointId: string) => void;
}

export function CheckpointViewer({ checkpoints, className, onRecover }: CheckpointViewerProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (!checkpoints || checkpoints.length === 0) {
    return (
      <div className={cn("text-center p-4 text-gray-500 text-sm border rounded-lg border-dashed", className)}>
        No checkpoints available
      </div>
    );
  }

  // Sort by timestamp desc
  const sortedCheckpoints = [...checkpoints].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <div className={cn("space-y-4", className)}>
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center">
        <Database className="w-4 h-4 mr-2" />
        Checkpoints & State Snapshots
      </h3>
      <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
        {sortedCheckpoints.map((cp) => (
          <div 
            key={cp.checkpoint_id} 
            className="border rounded-md bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-200"
          >
            <div 
              className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50"
              onClick={() => setExpandedId(expandedId === cp.checkpoint_id ? null : cp.checkpoint_id)}
            >
              <div className="flex items-center space-x-3">
                {expandedId === cp.checkpoint_id ? (
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                )}
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    Step Index: {cp.step_index + 1}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {formatCheckpointTime(cp.timestamp)}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700"
                )}>
                  Checkpoint
                </span>
              </div>
            </div>

            {expandedId === cp.checkpoint_id && (
              <div className="p-3 border-t bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700">
                <div className="mb-3">
                  <h4 className="text-xs font-semibold uppercase text-gray-500 mb-1">State Snapshot</h4>
                  <pre className="text-xs font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto text-gray-700 dark:text-gray-300">
                    {JSON.stringify(cp.state_snapshot, null, 2)}
                  </pre>
                </div>
                {onRecover && (
                  <div className="flex justify-end">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="text-xs"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRecover(cp.checkpoint_id);
                      }}
                    >
                      Recover to this state
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
