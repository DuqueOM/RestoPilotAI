import { Button } from '@/components/ui/button';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Checkpoint } from '@/types/marathon-agent';
import { ChevronDown, ChevronUp, Save } from 'lucide-react';
import { useState } from 'react';

interface CheckpointViewerProps {
  checkpoints: Checkpoint[];
  onRestore?: (checkpointId: string) => void;
}

export function CheckpointViewer({ checkpoints, onRestore }: CheckpointViewerProps) {
  const [expandedCheckpoint, setExpandedCheckpoint] = useState<string | null>(null);

  if (!checkpoints || checkpoints.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Checkpoints</CardTitle>
          <CardDescription>No checkpoints saved yet</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-sm flex items-center gap-2">
              <Save className="h-4 w-4" />
              Checkpoints ({checkpoints.length})
            </CardTitle>
            <CardDescription>Automatic save points for recovery</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {checkpoints.map((checkpoint, index) => (
          <Collapsible
            key={checkpoint.checkpoint_id}
            open={expandedCheckpoint === checkpoint.checkpoint_id}
            onOpenChange={(isOpen) =>
              setExpandedCheckpoint(isOpen ? checkpoint.checkpoint_id : null)
            }
          >
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <CollapsibleTrigger className="w-full">
                <div className="flex items-center justify-between p-3 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">Step {checkpoint.step_index}</Badge>
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900">
                        Checkpoint #{checkpoints.length - index}
                      </p>
                      <p className="text-xs text-gray-600">
                        {new Date(checkpoint.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  {expandedCheckpoint === checkpoint.checkpoint_id ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </div>
              </CollapsibleTrigger>

              <CollapsibleContent>
                <div className="p-3 bg-gray-50 border-t border-gray-200 space-y-3">
                  {/* Results Summary */}
                  <div>
                    <p className="text-xs font-medium text-gray-700 mb-2">Accumulated Results:</p>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(checkpoint.accumulated_results).map(([key, value]) => (
                        <div key={key} className="p-2 bg-white rounded border border-gray-200">
                          <p className="text-xs text-gray-600">{key}</p>
                          <p className="text-xs font-medium text-gray-900 truncate">
                            {typeof value === 'object' ? 'Object' : String(value)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Restore Button */}
                  {onRestore && (
                    <Button
                      onClick={() => onRestore(checkpoint.checkpoint_id)}
                      variant="outline"
                      size="sm"
                      className="w-full"
                    >
                      Restore from this checkpoint
                    </Button>
                  )}
                </div>
              </CollapsibleContent>
            </div>
          </Collapsible>
        ))}
      </CardContent>
    </Card>
  );
}
