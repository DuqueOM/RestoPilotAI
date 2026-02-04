'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { MarathonTaskState, TaskStatus } from '@/types/marathon-agent';
import {
    AlertTriangle,
    CheckCircle2,
    Loader2,
    PauseCircle,
    PlayCircle,
    RotateCcw,
    XCircle
} from 'lucide-react';

interface PipelineProgressProps {
  taskState: MarathonTaskState;
  onCancel: () => void;
  onRecover?: () => void;
}

export function PipelineProgress({ taskState, onCancel, onRecover }: PipelineProgressProps) {
  const getStatusConfig = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.RUNNING:
        return {
          icon: Loader2,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          label: 'Running',
          variant: 'default' as const,
        };
      case TaskStatus.COMPLETED:
        return {
          icon: CheckCircle2,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          label: 'Completed',
          variant: 'outline' as const,
        };
      case TaskStatus.FAILED:
        return {
          icon: XCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          label: 'Failed',
          variant: 'destructive' as const,
        };
      case TaskStatus.RECOVERING:
        return {
          icon: RotateCcw,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          label: 'Recovering',
          variant: 'default' as const,
        };
      case TaskStatus.CANCELLED:
        return {
          icon: PauseCircle,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          label: 'Cancelled',
          variant: 'secondary' as const,
        };
      default:
        return {
          icon: PlayCircle,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          label: 'Pending',
          variant: 'secondary' as const,
        };
    }
  };

  const statusConfig = getStatusConfig(taskState.status);
  const StatusIcon = statusConfig.icon;

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start).getTime();
    const endTime = end ? new Date(end).getTime() : Date.now();
    const durationMs = endTime - startTime;
    const seconds = Math.floor(durationMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  return (
    <div className={`p-6 rounded-lg border ${statusConfig.borderColor} ${statusConfig.bgColor}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <StatusIcon 
            className={`h-6 w-6 ${statusConfig.color} ${
              taskState.status === TaskStatus.RUNNING || taskState.status === TaskStatus.RECOVERING
                ? 'animate-spin'
                : ''
            }`}
          />
          <div>
            <h3 className="font-semibold text-gray-900">Marathon Agent Pipeline</h3>
            <p className="text-sm text-gray-600">
              Task ID: <code className="text-xs bg-gray-200 px-1 rounded">{taskState.task_id}</code>
            </p>
          </div>
        </div>
        <Badge variant={statusConfig.variant}>{statusConfig.label}</Badge>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Overall Progress</span>
          <span className="font-medium text-gray-900">
            {(taskState.progress * 100).toFixed(1)}%
          </span>
        </div>
        <Progress value={taskState.progress * 100} className="h-3" />
        <div className="flex items-center justify-between text-xs text-gray-600">
          <span>
            Step {taskState.current_step} of {taskState.total_steps}
          </span>
          <span>
            {taskState.checkpoints.length} checkpoint{taskState.checkpoints.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Current Step Info */}
      <div className="p-3 bg-white rounded border border-gray-200 mb-4">
        <p className="text-xs text-gray-600 mb-1">Current Step</p>
        <p className="font-medium text-gray-900">{taskState.current_step_name}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-2 bg-white rounded border border-gray-200">
          <p className="text-xs text-gray-600">Started</p>
          <p className="text-sm font-medium text-gray-900">
            {new Date(taskState.started_at).toLocaleTimeString()}
          </p>
        </div>
        <div className="text-center p-2 bg-white rounded border border-gray-200">
          <p className="text-xs text-gray-600">Duration</p>
          <p className="text-sm font-medium text-gray-900">
            {formatDuration(taskState.started_at, taskState.completed_at)}
          </p>
        </div>
        <div className="text-center p-2 bg-white rounded border border-gray-200">
          <p className="text-xs text-gray-600">ETA</p>
          <p className="text-sm font-medium text-gray-900">
            {taskState.estimated_completion
              ? new Date(taskState.estimated_completion).toLocaleTimeString()
              : 'Calculating...'}
          </p>
        </div>
      </div>

      {/* Error Message */}
      {taskState.error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded mb-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="text-sm text-red-700">{taskState.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        {taskState.status === TaskStatus.RUNNING && (
          <Button
            onClick={onCancel}
            variant="destructive"
            size="sm"
            className="flex-1"
          >
            <XCircle className="h-4 w-4 mr-2" />
            Cancel Task
          </Button>
        )}
        {taskState.status === TaskStatus.FAILED && taskState.can_recover && onRecover && (
          <Button
            onClick={onRecover}
            variant="default"
            size="sm"
            className="flex-1"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Recover from Checkpoint
          </Button>
        )}
      </div>
    </div>
  );
}
