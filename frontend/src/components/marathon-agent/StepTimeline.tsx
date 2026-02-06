'use client';

import { StatusBadge, StatusType } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';
import { PipelineStep, StepStatus } from '@/types/marathon-agent';
import { CheckCircle2, Circle, Loader2, SkipForward, Sparkles, XCircle } from 'lucide-react';

interface StepTimelineProps {
  steps: PipelineStep[];
}

export function StepTimeline({ steps }: StepTimelineProps) {
  const getStepIcon = (status: StepStatus) => {
    switch (status) {
      case StepStatus.COMPLETED:
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case StepStatus.RUNNING:
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
      case StepStatus.FAILED:
        return <XCircle className="h-5 w-5 text-red-600" />;
      case StepStatus.SKIPPED:
        return <SkipForward className="h-5 w-5 text-gray-400" />;
      default:
        return <Circle className="h-5 w-5 text-gray-300" />;
    }
  };

  const stepStatusMap: Record<StepStatus, StatusType> = {
    [StepStatus.COMPLETED]: 'completed',
    [StepStatus.RUNNING]: 'running',
    [StepStatus.FAILED]: 'error',
    [StepStatus.SKIPPED]: 'idle',
    [StepStatus.PENDING]: 'pending',
  };

  return (
    <div className="space-y-4">
      {steps.map((step, index) => (
        <div key={step.step_id} className="flex gap-4">
          {/* Timeline Line */}
          <div className="flex flex-col items-center">
            <div className="flex-shrink-0">{getStepIcon(step.status)}</div>
            {index < steps.length - 1 && (
              <div
                className={`w-0.5 h-full mt-2 ${
                  step.status === StepStatus.COMPLETED
                    ? 'bg-green-200'
                    : step.status === StepStatus.RUNNING
                    ? 'bg-blue-200'
                    : 'bg-gray-200'
                }`}
              />
            )}
          </div>

          {/* Step Content */}
          <div className="flex-1 pb-8">
            <div className={cn(
              'flex items-start justify-between mb-2 p-3 rounded-lg border transition-all',
              step.status === StepStatus.RUNNING ? 'bg-blue-50/50 border-blue-200' :
              step.status === StepStatus.COMPLETED ? 'bg-white border-green-100' :
              step.status === StepStatus.FAILED ? 'bg-red-50/30 border-red-200' :
              'bg-gray-50/50 border-gray-100'
            )}>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-gray-900 text-sm">{step.name}
                    {step.status === StepStatus.RUNNING && <Sparkles className="h-3 w-3 text-purple-500 inline ml-1" />}
                  </h4>
                  <StatusBadge
                    status={stepStatusMap[step.status] || 'pending'}
                    label={step.status === StepStatus.RUNNING ? 'Running...' : step.status}
                    size="sm"
                  />
                </div>
                <p className="text-sm text-gray-600">{step.description}</p>
              </div>
              {step.duration_ms && (
                <span className="text-xs text-gray-500 ml-4">
                  {(step.duration_ms / 1000).toFixed(1)}s
                </span>
              )}
            </div>

            {/* Retry Info */}
            {step.retry_count > 0 && (
              <div className="text-xs text-yellow-600 mb-2">
                Retried {step.retry_count}/{step.max_retries} times
              </div>
            )}

            {/* Error Message */}
            {step.error_message && (
              <div className="p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                {step.error_message}
              </div>
            )}

            {/* Timestamps */}
            <div className="flex gap-4 text-xs text-gray-500 mt-2">
              {step.started_at && (
                <span>Started: {new Date(step.started_at).toLocaleTimeString()}</span>
              )}
              {step.completed_at && (
                <span>Completed: {new Date(step.completed_at).toLocaleTimeString()}</span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
